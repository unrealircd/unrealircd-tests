# User command tests

Tests for commands available to regular (non-oper) users.

## Covered commands

| Command | Test file | Notes |
|---|---|---|
| `ADMIN` | `admin` | |
| `AWAY` | `away` | |
| `CREDITS` | `credits` | Core command |
| `CYCLE` | `cycle` | |
| `DCCALLOW` | `dccallow` | |
| `HISTORY` | `history` | |
| `INFO` | `info` | Core command |
| `INVITE` | `invite` | |
| `ISON` | `ison` | |
| `JOIN` | `join` | |
| `KICK` | `kick` | |
| `KNOCK` | `knock` | |
| `LICENSE` | `license` | Core command |
| `LINKS` | `links` | |
| `LIST` | `list` | |
| `LUSERS` | `lusers` | |
| `MAP` | `map` | |
| `MODE` | `mode` | Channel and user modes |
| `MONITOR` | `monitor` | |
| `MOTD` | `motd` | |
| `NAMES` | `names` | |
| `NICK` | `nick` | |
| `NOTICE` | `notice` | |
| `PART` | `part` | |
| `PRIVMSG` | `privmsg` | |
| `QUIT` | `quit` | |
| `RULES` | `rules` | |
| `SETNAME` | `setname` | |
| `SILENCE` | `silence` | |
| `TAGMSG` | `tagmsg` | |
| `TIME` | `time` | |
| `TOPIC` | `topic` | |
| `USERHOST` | `userhost` | |
| `USERIP` | `userip` | |
| `VERSION` | `version` | Core command |
| `VHOST` | `vhost` | |
| `WATCH` | `watch` | |
| `WHO` | `who` | |
| `WHOIS` | `whois` | |
| `WHOWAS` | `whowas` | |

## Tested in other directories

These commands have tests outside `usercommands/`:

| Command | Test location | Notes |
|---|---|---|
| `CAP` | `tests/extensions/cap` | IRCv3 capability negotiation |
| `CHATHISTORY` | `tests/extensions/chathistory` | IRCv3 CHATHISTORY |
| `EXTJWT` | `tests/extensions/extjwt` | External JWT tokens |

## Not covered

- `BOTMOTD` — shows bot MOTD
- `HELP` / `HELPOP` — shows help text
- `IRCOPS` — lists online IRC operators
- `LAG` — checks lag to servers
- `LINKSECURITY` — shows link security overview
- `PING` — used implicitly by the test framework but not tested directly
- `SPAMREPORT` — reports spam to other servers
- `STAFF` — shows staff file
- `STATS` — shows server statistics
- `TRACE` — traces route to user/server
