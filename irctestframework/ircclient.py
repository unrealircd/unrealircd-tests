import asynchat
import asyncore
import socket
import string
import random
import re
import time

class IrcClient(asynchat.async_chat):
    def bgcolor(self, name):
        if name[2:3] == 'a':
            c = '80'
        else:
            c = '120'
        if name[:2] == 'c1':
            # red
            return '\033[48;2;'+c+';0;0m'
        if name[:2] == 'c2':
            # yellow
            return '\033[48;2;'+c+';'+c+';0m'
        if name[:2] == 'c3':
            # green
            return '\033[48;2;00;'+c+';0m'
        return '\033[48;2;210;105;180m' # error
    def fgcolor(self, name):
        if name[2:3] == 'a':
            c = '192'
            suffix = ''
        else:
            c = '255'
            suffix = '\033[51m'
        if name[:2] == 'c1':
            # red
            return '\033[38;2;'+c+';00;00m' + suffix
        if name[:2] == 'c2':
            # yellow
            return '\033[38;2;'+c+';'+c+';00m' + suffix
        if name[:2] == 'c3':
            # green
            return '\033[38;2;00;'+c+';00m' + suffix
        return '\033[38;2;210;105;180m' # error
    def log(self, message):
        standard = self.bgcolor(self.name) + "\033[38;2;210;210;210m"
        m = standard + message + "\033[0m"
        m = re.sub("(c1a_[a-z]{8})", self.fgcolor('c1a')+r'\1' + standard, m)
        m = re.sub("(c2a_[a-z]{8})", self.fgcolor('c2a')+r'\1' + standard, m)
        m = re.sub("(c3a_[a-z]{8})", self.fgcolor('c3a')+r'\1' + standard, m)
        m = re.sub("(c1b_[a-z]{8})", self.fgcolor('c1b')+r'\1' + standard, m)
        m = re.sub("(c2b_[a-z]{8})", self.fgcolor('c2b')+r'\1' + standard, m)
        m = re.sub("(c3b_[a-z]{8})", self.fgcolor('c3b')+r'\1' + standard, m)
        print m
#        print "\033[" + str(self.color) + "m" + message + "\033[0m"
#        for name,obj in self.clients.iteritems():
#            str = str.replace("$" + name, obj.nick)

    def __init__(self, (host, port), name, color, syncchan):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\r\n')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.data_in = ''
        self.name = name
        self.nick = name + '_' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        self.synced = 0
        self.ready = -10
        self.synctext = ''
        self.color = color
        self.hide_sync = 1
        self.hide_handshake = 1
        self.syncchan = syncchan
        self.recvd_syncers = {}
        self.all_lines = []
        self.log("[Client " + self.nick + " on " + host + ":" + str(port) + "]")

    def handle_connect(self):
        # Generalize this later...
        self.out("USER username x x :Test framework")
        self.out("NICK " + self.nick)

    def out(self, data):
        if not self.hide_sync or not "__SYNC__" in data:
            if not self.hide_handshake or self.ready == 1:
                self.log("" + self.name + ">> " + data)
        self.push(data + '\r\n')

    def collect_incoming_data(self, data):
        self.data_in += data

    def found_terminator(self):
        # Log
        if not self.hide_sync or not "__SYNC__" in self.data_in:
            if not self.hide_handshake or self.ready == 1:
                self.log("<<" + self.name + " " + self.data_in)

        # ..
        if not "__SYNC__" in self.data_in and self.ready == 1:
            self.all_lines.append(self.data_in)

        # Parser
        line = self.data_in
        input_data = self.data_in
        source = ''
        prefix = ''

        # Lazy
        if input_data == '':
            input_data = ' '

        # Message with a source? Save it.
        if input_data[0] == ':':
            (source, input_data) = input_data.split(" ", 1)

        # Parse the string, taking into account special handling of last :xxxx argument
        if " :" in input_data:
            (input_data, remainder) = input_data.split(" :", 1)
            e = input_data.split(" ")
            e += [remainder]
        else:
            e = input_data.split(" ")

        cmd = e[0]

        if source[:1] == ':':
            source = source[1:]

        #command = handlers.handler.Command(source, prefix, cmd, e)
        #handler = handlers.handler.HandlerFactory.handler_for_command(command)
        #if handler is not None:
        #    handler.handle(self.context, command)
        
        if cmd == 'PING':
            self.out("PONG :" + e[1])

        if cmd == '001':
            # We got the 001 welcome, now join the syncchannel
            # (we are NOT ready yet)
            self.ready = -9
            self.out("JOIN " + self.syncchan)

        if '366' in line and self.syncchan in line:
            # We joined the syncchan and are now fully ready.
            self.ready = 1

        if cmd == 'PRIVMSG' and '__SYNC' in e[2]:
            # For multisync:
            self.recvd_syncers[e[2]] = 1
            # For singlesync:
            if self.synctext != '' and self.synctext in e[2]:
                self.synced = 1

        if cmd == 'JOIN' and '__SYNC' in e[1]:
            # For multisync, add the nick seen in JOIN for the syncchan:
            nick = source.split("!")[0]
            self.recvd_syncers[nick] = 1

        if cmd == '353' and '__SYNC' in e[3]:
            # for multisync, add each nick seen in NAMES of the syncchan:
            for entry in e[4].split(" "):
                if entry != '':
                    # remove !user@host in case of CAP userhost-in-names
                    nick = entry.split("!")[0]
                    # remove @ (chanops) prefix
                    if nick[:1] == '@':
                        nick = nick[1:]
                    self.recvd_syncers[nick] = 1

        if cmd == 'NICK':
            sourcenick = source.split("!")[0]
            if sourcenick == self.nick:
                # Nick change (self)
                self.nick = e[1]

        # Clear
        self.data_in = ''

    def start_sync(self):
        if self.ready != 1:
            raise Exception("start_sync() requested but not connected yet -- BAD!!!")

        self.synced = -1
        self.synctext = '!__SYNC__' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        self.out("PRIVMSG " + self.syncchan + "," + self.nick + " :" + self.synctext)

    def is_synced(self):
        if self.synced != 1:
            return 0
        return 1

    def is_ready(self):
        if self.ready != 1:
            return 0
        return 1

    def expect(self, failmsg, regex, nofail = 0):
        for line in self.all_lines:
            if re.search(regex, line, re.DOTALL) != None:
                #print 'Regex: ' + regex
                #print 'Matched line: ' + line
                print '\033[1m' + u'\u2714' + ' Test passed: ' + failmsg + '\033[0m'
                return 1
        if nofail == 1:
            return 0
        print '\033[1m' + u'\u274e' + ' Test failed: ' + failmsg + '\033[0m'
        print '******************* EXPECT FAILED ************************'
        self.log('Client: ' + self.nick)
        print 'Fail message: ' + failmsg
        print 'Regex that SHOULD MATCH (but didn\'t): ' + regex
        print 'Lines:'
        for line in self.all_lines:
            print line
        print '************************************************************'
        raise Exception("An expected response was not found in the result: " + failmsg)

    def not_expect(self, failmsg, regex):
        for line in self.all_lines:
            if re.search(regex, line, re.DOTALL) != None:
                print '\033[1m' + u'\u274e' + ' Test failed: ' + failmsg + '\033[0m'
                print
                print '******************* EXPECT FAILED ************************'
                print 'Fail message: ' + failmsg
                print 'Regex that SHOULD NOT MATCH (but did): ' + regex
                print 'Matched line:'
                print line
                print '************************************************************'
                raise Exception("An unexpected response was found in the result: " + failmsg)
        print '\033[1m' + u'\u2714' + ' Test passed: ' + failmsg + '\033[0m'

    def clearlog(self):
        self.all_lines = []
