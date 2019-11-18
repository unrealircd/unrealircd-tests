# About
This is the automated test system for UnrealIRCd 5, written in Python.

Currently only a subset of features are tested. In particular user modes and
channel modes. The ultimate goal is to have a test for each and every feature.
In particular, the testing of commands needs a lot more work.

# A word of caution before you start
When you run the test framework, it will do things like killing all
IRC Servers under the account, overwrite configuration files of both
UnrealIRCd and Anope and Atheme. This is all done without prompting!

# How to run
You run all the test with the `./run -services [anope|atheme]` command.
This script assumes that UnrealIRCd is installed in ~/unrealircd/,
atheme in ~/atheme and anope in ~/anope.
It will kill all UnrealIRCd and services instances on the account,
boot up 3 IRC servers (irc1, irc2 and irc3), link them together
and run the tests.

You can run a specific test via `./run -services xx tests/sometest`.
If you use this syntax then UnrealIRCd is assumed to be already up and
running and linked. If this isn't the case then use
`./run -services xx -boot tests/sometest`.

# Main features
## Tests
Tests are self-contained programs and can be ran individually or (almost)
all in parallel. Parallel execution speeds things up considerably.

## Log output
Raw server traffic has a background color that depends on the client.
Traffic from clones on server 1 will have a red background, on server 2
will have a yellow background and server 3 will be green. This order
is the same is in a traffic light, to make it easy to remember.

In addition to that, any nicks have their foreground color highlighted
in the same colors to make them stand out.

Once you get used to it, it makes it really simple to quickly read
raw server traffic generated by a (failed) test.

Note that raw server traffic is mostly hidden. It is only visible for
the initial linking and will otherwise only be shown for failed tests.

## Automatic synchronization
Tests often do one action and then expect a response. But when can you
expect such a response? And how long do you have to wait to ensure a
lack of response? Sure you can wait a little but this leads to failed
tests under heavy load. And when commands are executed on multiple
servers things become even more tricky if you want certain ordering.
This is why the test framework does all the synchronization automatically.
You can execute a command and immediately test for output (or lack of
output). Similarly, it will guarantee the order of things, even on a
multi-server network. So if you do A) a join of 1 client on 1 server,
and then B) another join on another server later, then the test framework
will always ensure that A happened and has been processed on all servers
before next command (B) will be executed.
In short: you don't need to worry about sequences or synchronization.

In case you wonder: the test framework does this by joining all clones
to a special channel (hidden in raw server output by default). Then,
for each executed command, it sends traffic to this channel and expects
to receive it back on all clones. Technically it is a barrier and
works similar to memory barriers.

# Writing tests

Tests go in the `tests/` directory and are standalone python scripts.
You can use `tests/basic` as a template and look at other existing tests.
Below is a more thorough explanation:

## Connecting users

First a word on nick names: the naming of each client is a fixed scheme.
Typically you connect at least one client to each server and then they
will be named: `c1a`, `c2a`, `c3a`. The digit indicates the server number
and the letter is for clones so there can be a `c1b` etc.

A test typically starts with this code:
```
#!/usr/bin/python
import irctestframework.irctest

m = irctestframework.irctest.IrcTest()
c1a = m.new('c1a')
c2a = m.new('c2a')
c3a = m.new('c3a')
m.connect()
```

Note that behind-the-scenes, the nicks are not actually named just "c1a"
but are named "c1a-halehe" or some other random suffix. This is so tests
can be run in parallel, speeding up testing everything considerably.

## Joining a channel

A typical action after all clones are online is joining a channel.
Naturally, you can skip this part if your test does not require a channel.

```
chan = m.randchan()
m.join_all(chan, creator = c1a)
m.expect(c1a, "user in channel", "JOIN")
print
```

The first line will create a random channel name.
The m.join_all() command is used to join all clones to the channel.
Often you will need one specific clone to have ops, this is why you
can specify the creator of the channel (that will have ops) by
passing `creator=c1a`. Similarly, you can have all clones except
one join the channel by specifying `skip=c3a`.

The m.expect() line will check that clone c1a has received a "JOIN"
message. For displaying purposes it uses the comment "user in channel"
which will be displayed in the test output.

## Actions and responses
Once all clones are connected and things are set up, tests will
perform actions and then expect a certain response (or lack thereof).

For example, this will test the TOPIC command:
```
m.send(c1a, "TOPIC " + chan + " :this is a nice new topic")
m.expect_all("Everyone should see TOPIC change", ":$c1a.* TOPIC " + chan + " :this is a nice new topic")
m.clearlog()
print
```

The first line sends a command through clone c1a to set the topic.
The m.expect_all() will check that every clone (so c1a, c2a and c3a)
have all received the regex `:$c1a.* TOPIC " + chan + " :this is a nice new topic`.
Note that the `$c1a` variable will be expanded to clone c1a's
real nick, which is actually c1a-randomstuff, as explained earlier
under "Connecting users".
If the regex matches, then the test will print a checkmark like:
[v] Everyone should see TOPIC change

Finally, the m.clearlog() action ensures that all server traffic
received up to that point is cleared and we start out fresh.
This is usually necessary for any tests that may run after.

# Function list
Assuming you do a `m = irctestframework.irctest.IrcTest()`, then
the following actions are available in m:
* `m.new('c1a')` - Prepare a new clone
* `m.connect()` - Connect all the previously specified clones
* `m.send(c1a, "SOME COMMAND")` - Send this command to the specified clone
* `m.send_all("SOME COMMAND")` - Send this command to ALL clones.
* `m.expect(c1a, "some comment", ":$c1a.* TOPIC")` - Expect the regex to match, otherwise fail the test.
* `m.not_expect(c1a, "some comment", "this.*should.*not.*happen")` - Expect the regex NOT to match, fail the test if it does.
* `m.expect_all("some comment", "":$c1a.* TOPIC")` - Expect the regex to match on ALL clones, otherwise fail the test
* `m.not_expect_all("some comment", "":$c1a.* TOPIC")` - Expect the regex NOT to match on ALL clones, if it matches on any then fail the test.
* There are more..

# Directory layout:
* `serverconfig/` - Configuration files used by the servers (unrealircd and services)
* `irctestframework/` - The actual test framework. You don't need to touch this if you are just writing tests.
* `logs/` - Log files produced by the tests
* `tests/chanmodes/` - Channel modes
* `tests/usermodes/` - User modes
* `tests/extbans/` - Extended bans
* `tests/extensions` - IRCv3 extensions like CAP stuff etc.
* `tests/usercommands/` - User commands, such as JOIN PART TOPIC etc.
* `tests/opercommands/` - IRCOp-only commands, such as SAJOIN SAPART KILL etc.
* `tests/services/` - Services tests
