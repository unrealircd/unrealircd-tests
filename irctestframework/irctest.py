#!/usr/bin/python3
import asynchat
import asyncore
import socket
import string
import random
import re
import time

import irctestframework.ircclient

getmsec = lambda: int(round(time.time() * 1000))

class IrcTest(asynchat.async_chat):
    def __init__(self):
        self.clients = {}
        self.syncchan = "#__SYNC__" + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
#        self.syncchan = "#sync_" + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        self.sync = 1
        self.disable_message_tags_check = 0
        self.disable_logging = 0
    
    def new(self, name):
        if name in self.clients:
            raise Exception("IrcTest.new(): client with this nick already exists: " +name)
        # TODO: move to config ;)
        if name[:2] == 'c1':
            color = 31
            host = '127.0.0.1'
            port = 5661
        elif name[:2] == 'c2':
            color = 32
            host = '127.0.0.1'
            port = 5662
        elif name[:2] == 'c3':
            color = 33
            host = '127.0.0.1'
            port = 5663
        else:
            raise Exception("IrcTest.new() expects argument with c1/c2/c3 to indicate server, got: " + name)
        obj = irctestframework.ircclient.IrcClient((host, port), name, color, self.syncchan)
        obj.disable_logging = self.disable_logging
        self.clients[name] = obj
        return obj

    # Are all connections synced?
    def synced(self):
        for name,obj in self.clients.items():
            if not obj.is_synced():
                return 0
        return 1

    def is_ready(self):
        ready_count = 0
        notready_count = 0
        for name,obj in self.clients.items():
            if obj.is_ready():
                ready_count += 1
            else:
                notready_count += 1
        #print 'DEBUG: Client status: ' + str(ready_count) + ' OK, ' + str(notready_count) + ' NOT ready'
        if notready_count > 0:
            return 0
        return 1

    def multisynced(self):
        for name,obj in self.clients.items():
            for name2,obj2 in self.clients.items():
                if not obj.synctext in obj2.recvd_syncers:
                    #print 'Waiting for sync ' + obj.synctext + ' to be received by ' + name2
                    #print 'Have only: '
                    #print obj2.recvd_syncers
                    return 0
        return 1

    def is_multi_ready(self):
        for name,obj in self.clients.items():
            for name2,obj2 in self.clients.items():
                if not obj.nick in obj2.recvd_syncers:
                    return 0
        return 1

    def start_sync(self):
        for name,obj in self.clients.items():
            obj.start_sync()

    def socketloop(self, t):
        on_start = time.time()
        delta = 0
        while time.time() - on_start < t:
            asyncore.loop(count=1, timeout=0.1)

    def connect(self):
        while(not self.is_ready()):
            asyncore.loop(count=1, timeout=0.1)
        cnt=0
        if self.sync == 1:
            current_time = getmsec()
            while(not self.is_multi_ready()):
                asyncore.loop(count=1, timeout=0.1)
                if getmsec() - current_time > 10000:
                    print('Multisync@connect failed after 10 seconds')
                    print('This only happens if not all servers are linked')
                    raise Exception('sync failed - servers not linked?')
            self.multisync()

    def sync(self):
        if self.sync == 0:
            return
        self.start_sync()
        # Then run this:
        while(not self.synced()):
            asyncore.loop(count=1, timeout=0.1)

    def verify_mtags_consistency(self):
        # Based on heuristics, could be wrong, especially with .clearlog()

        # Ignore, if requested:
        if self.disable_message_tags_check:
            return

        # First build a list with all messages from everyone, so we can see which ones are identical
        all_msgs = {}
        for name,obj in self.clients.items():
            for full_line in obj.all_lines:
                # Should we filter purely on channel events? Let's see how long
                # we can get away with it by not doing it for now ;D
                if 1:
                    if full_line[0] == '@':
                        (mtags, line) = full_line.split(" ", 1)
                    else:
                        line = full_line
                    if not line in all_msgs:
                        all_msgs[line] = {}
                    all_msgs[line][name] = full_line
        # Now count all lines that are >1
        for commonline, o in all_msgs.items():
            if len(o) > 1:
                first = None
                for name,full_line in o.items():
                    if not first:
                        first = full_line
                    else:
                        if self.inconsistent_lines(first, full_line):
                            print()
                            print('\033[1mInconsistent message-tag use accross server links:\033[0m')
                            print(('Line (bare): ' + commonline))
                            for name,full_line in o.items():
                                #print('Client ' + name + ': '  + full_line)
                                self.clients[name].log('Client ' + name + ': '  + full_line)

                            raise Exception('mtags: possible mismatch (by verify_mtags_consistency)')

    def inconsistent_lines(self, firstline, secondline):
        # It is no longer this easy...
        # if firstline != secondline:
        #     return 1
        # ..as, for example on msg playback, a batch may be started.
        # So we filter out batch=xyz; here:
        firstline = re.sub("batch=[^; ]+;*", "", firstline)
        secondline = re.sub("batch=[^; ]+;*", "", secondline)
        if firstline != secondline:
            return 1
        return 0

    def multisync(self):
        if self.sync == 0:
            return
        self.start_sync()
        current_time = getmsec()
        while(not self.multisynced()):
            asyncore.loop(count=1, timeout=0.1)
            if getmsec() - current_time > 45000:
                print('Multisync failed after 45 seconds')
                print('This can happen if not all servers are linked')
                raise Exception('multisync failed - servers not linked?')
        self.verify_mtags_consistency()

    def send(self, client, message):
        message = self.replacestr(client, message)
        client.out(message)
        self.multisync()

    def send_all(self, message, skip = None):
        for name,obj in self.clients.items():
            if obj != skip:
                message = self.replacestr(obj, message)
                obj.out(message)
        self.multisync()

    def join_all(self, chan, skip = None, creator = None):
        if creator != None:
            # Ensure this user joins first and has ops
            creator.out("JOIN " + chan)
            self.multisync()
        for name,obj in self.clients.items():
            if obj != skip:
                obj.out("JOIN " + chan)
        self.multisync()

    def random(self, num):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(num))

    def randchan(self, prefix = "#"):
        if prefix == '#':
            return "#" + self.random(16)
        else:
            return prefix + "_" + self.random(16)

    def expect(self, client, failmsg, regex, timeout = 0):
        regex = self.replacestr(client, regex)
        if timeout > 0:
            t = timeout * 1000
            current_time = getmsec()
            while getmsec() - current_time < t:
                if client.expect(failmsg, regex, nofail=1):
                    return 1
                asyncore.loop(count=1, timeout=0.1)
        # Without a timeout it's simply one client.expect() call.
        # ..and also the fallthrough from above (necessary!)
        return client.expect(failmsg, regex)

    def expect_all(self, failmsg_orig, regex, timeout = 0, skip = None):
        cnt = 0
        total = len(self.clients)
        if skip != None:
            total = total - 1 # could be wrong, don't care
        for name,obj in self.clients.items():
            if obj == skip:
                continue
            cnt = cnt + 1
            failmsg = failmsg_orig + ' ('+str(cnt)+' of '+str(total)+')'
            self.expect(obj, failmsg, regex, timeout)

    def not_expect(self, client, failmsg, regex):
        regex = self.replacestr(client, regex)
        return client.not_expect(failmsg, regex)

    def not_expect_all(self, failmsg_orig, regex, skip = None):
        cnt = 0
        total = len(self.clients)
        if skip != None:
            total = total - 1 # could be wrong, don't care
        for name,obj in self.clients.items():
            if obj == skip:
                continue
            cnt = cnt + 1
            failmsg = failmsg_orig + ' ('+str(cnt)+' of '+str(total)+')'
            self.not_expect(obj, failmsg, regex)

    def expect_tag(self, client, failmsg, regex, msgtag, timeout = 0):
        regex = self.replacestr(client, regex)
        if timeout > 0:
            t = timeout * 1000
            current_time = getmsec()
            while getmsec() - current_time < t:
                line = client.expect(failmsg, regex, nofail=1, msgtag=msgtag)
                if line:
                    return line
                asyncore.loop(count=1, timeout=0.1)
        # Without a timeout it's simply one client.expect() call.
        # ..and also the fallthrough from above (necessary!)
        return client.expect(failmsg, regex, msgtag=msgtag)

    def replacestr(self, client, str):
        for name,obj in self.clients.items():
            str = str.replace("$" + name, obj.nick)
        str = str.replace("$me", client.nick)
        return str

    def wait(self, t):
        t = t * 1000
        current_time = getmsec()
        while getmsec() - current_time < t:
            asyncore.loop(count=1, timeout=0.1)

    def clearlog(self, obj = None):
        if obj:
            obj.clearlog()
        else:
            for name,obj in self.clients.items():
                obj.clearlog()
