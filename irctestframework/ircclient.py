#!/usr/bin/python3
import asynchat
import asyncore
import socket
import string
import random
import re
import time

class IrcClient(asynchat.async_chat):
    def __init__(self, xxx_todo_changeme, name, color, syncchan):
        (host, port) = xxx_todo_changeme
        asynchat.async_chat.__init__(self)
        self.set_terminator(b'\r\n')
        self.data_in = ''
        self.name = name
        self.nick = name + '_' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        self.synced = 0
        self.ready = -10
        self.synctext = ''
        self.color = color
        self.hide_sync = 1
        self.hide_handshake = 1
        self.disable_logging = 0
        self.disable_registration = 0
        self.disable_message_tags_check = 0
        self.syncchan = syncchan
        self.recvd_syncers = {}
        self.all_lines = []
        self.log("[Client " + self.nick + " on " + host + ":" + str(port) + "]")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

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
        if self.disable_logging:
            return
        standard = self.bgcolor(self.name) + "\033[38;2;210;210;210m"
        m = standard + message + "\033[0m"
        m = re.sub("(c1a_[a-z]{8})", self.fgcolor('c1a')+r'\1' + standard, m)
        m = re.sub("(c2a_[a-z]{8})", self.fgcolor('c2a')+r'\1' + standard, m)
        m = re.sub("(c3a_[a-z]{8})", self.fgcolor('c3a')+r'\1' + standard, m)
        m = re.sub("(c1b_[a-z]{8})", self.fgcolor('c1b')+r'\1' + standard, m)
        m = re.sub("(c2b_[a-z]{8})", self.fgcolor('c2b')+r'\1' + standard, m)
        m = re.sub("(c3b_[a-z]{8})", self.fgcolor('c3b')+r'\1' + standard, m)
        print(m)
#        print "\033[" + str(self.color) + "m" + message + "\033[0m"
#        for name,obj in self.clients.iteritems():
#            str = str.replace("$" + name, obj.nick)

    # Verify if the required message tags are present
    def check_mtags_present(self, line, mtags, source, e):
        if (e[0] in ("JOIN", "KICK", "MODE", "PRIVMSG", "NOTICE", "PART") and e[1][0] == '#') or \
           (e[0] in ("NICK", "QUIT")) or \
           (e[0] in ("PRIVMSG", "NOTICE")):
            # Single channel event OR
            # Common channel event OR
            # Non-channel PRIVMSG/NOTICE

            # Filter out server notices (to non-channels) for now.
            # It is not important that these contain a msgid since
            # these are never replayed anyway.
            if "." in source and e[1][0] != '#':
                return

            if not "msgid=" in mtags and not self.disable_message_tags_check:
                print("\033[1mMissing mandatory message-tag 'msgid' in channel event\033[0m")
                print("Line :" + line)
                print()
                raise Exception("Missing 'msgid' in channel event")
        return

    def handle_connect(self):
        # Return if we don't want to register as a user (rare):
        if self.disable_registration:
            self.ready = 1
            return
        # Generalize this later...
        self.out("CAP LS")
        self.out("CAP REQ :message-tags account-tag")
        self.out("CAP END")
        self.out("USER username x x :Test framework")
        self.out("NICK " + self.nick)

    def out(self, data):
        if not self.hide_sync or not "__SYNC__" in data:
            if not self.hide_handshake or self.ready == 1:
                self.log("" + self.name + ">> " + data)
        if data.startswith("NICK "):
            # Sending a NICK command to change nick?
            # This is problematic as it interfers with the
            # automatic syncer. We update the nick name in
            # response to the :ournick NICK newnick from
            # the server, but by then it is too late,
            # as we have already sent a PRIVMSG ...,ournick ..
            # So we need to update it here, even though
            # it could fail, of course, in which case
            # we're screwed. Well, at least it fixes the
            # more common case when it succeeds, which
            # helps a lot since then we don't need to disable
            # the syncer in tests.
            (zzcmd, newnick) = data.split(" ", 1)
            self.nick = newnick
        data = data + '\r\n'
        self.push(data.encode())

    def collect_incoming_data(self, data):
        self.data_in += data.decode()

    def hide_sync_data_check(self, str):
        if not self.hide_sync:
            return False
        if not "__SYNC__" in str:
            return False
        # So, there's __SYNC__ in it, but only filter certain stuff:
        if any(x in str for x in ('JOIN', 'QUIT', 'PRIVMSG', 'MODE')):
            return True
        return False

    def found_terminator(self):
        # Log
        if not self.hide_sync_data_check(self.data_in):
            if not self.hide_handshake or self.ready == 1:
                self.log("<<" + self.name + " " + self.data_in)

        # ..
        if self.ready == 1 and not self.hide_sync_data_check(self.data_in):
            self.all_lines.append(self.data_in)

        # Parser
        line = self.data_in
        input_data = self.data_in
        source = ''
        prefix = ''
        mtags = ''

        # Lazy
        if input_data == '':
            input_data = ' '

        # Message with message-tags? Save it
        if input_data[0] == '@':
            (mtags, input_data) = input_data.split(" ", 1)

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

        self.check_mtags_present(line, mtags, source, e)

        #command = handlers.handler.Command(source, prefix, cmd, e)
        #handler = handlers.handler.HandlerFactory.handler_for_command(command)
        #if handler is not None:
        #    handler.handle(self.context, command)
        
        if cmd == 'PING':
            self.out("PONG :" + e[1])

        if cmd == '001':
            # We got the 001 welcome, now join the syncchannel
            # (we are NOT ready yet)
            if self.ready < -9:
                self.ready = -9
                self.out("JOIN " + self.syncchan)
                self.out("MODE " + self.syncchan + " +F off")

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

    def extract_message_tags(self, line):
        if len(line) == 0 or line[0] != '@':
            return [] # no message tags
        (xmtags, input_data) = line[1:].split(" ", 1)
        xmtags = xmtags.split(";")
        mtags = {}
        for e in xmtags:
            (name, value) = e.split("=", 1)
            mtags[name] = value
        return mtags

    def expect(self, failmsg, regex, nofail = 0, msgtag = False):
        for line in self.all_lines:
            if re.search(regex, line, re.DOTALL) != None:
                if not msgtag:
                    print('\033[1m' + '\u2714' + ' Test passed: ' + failmsg + '\033[0m')
                    return line
                else:
                    # Need to check presence of msgtag as well..
                    tags = self.extract_message_tags(line)
                    if msgtag in tags:
                        return tags[msgtag]
                    # fallthrough? bit confusing.
        if nofail == 1:
            return False
        print('\033[1m' + '\u274e' + ' Test failed: ' + failmsg + '\033[0m')
        print('******************* EXPECT FAILED ************************')
        self.log('Client: ' + self.nick)
        print('Fail message: ' + failmsg)
        print('Regex that SHOULD MATCH (but didn\'t): ' + regex)
        print('Lines:')
        for line in self.all_lines:
            print(line)
        print('************************************************************')
        raise Exception("An expected response was not found in the result: " + failmsg)

    def not_expect(self, failmsg, regex):
        for line in self.all_lines:
            if re.search(regex, line, re.DOTALL) != None:
                print('\033[1m' + '\u274e' + ' Test failed: ' + failmsg + '\033[0m')
                print()
                print('******************* EXPECT FAILED ************************')
                print('Fail message: ' + failmsg)
                print('Regex that SHOULD NOT MATCH (but did): ' + regex)
                print('Matched line:')
                print(line)
                print('************************************************************')
                raise Exception("An unexpected response was found in the result: " + failmsg)
        print('\033[1m' + '\u2714' + ' Test passed: ' + failmsg + '\033[0m')

    def clearlog(self):
        self.all_lines = []
