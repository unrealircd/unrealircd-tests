# Serial tests

All tests in this directory are run in series, not in parallel.

Please only put tests here that really need it (e.g. netsplit tests or
tests with long sleeps), as it hurts performance.

## Test files

| Test file | What it tests |
|---|---|
| `netsplit_simple` | SQUIT/CONNECT cycle: splits the hub, verifies servers disappear from MAP, reconnects, and checks all users reappear in the channel via NAMES |
| `netsplit_merge` | Full netsplit+merge with state: same SQUIT/CONNECT cycle but also verifies QUIT messages on split, JOIN messages on merge, ban list synchronization across servers (40 bans per server), and correct "set by" fields after merge |
| `crule_directop` | `directop()` crule function: checks if any oper is directly connected to the local server. Must run in serial because parallel tests OPERing up on irc1 cause false positives. |
| `time_extban_expiry` | `~time:` extban expiry: sets a 1-minute and a 5-minute timed text ban, waits for the short one to expire (~90s), verifies it is automatically removed while the longer one stays, and confirms the previously banned text is allowed again. Skipped with `-fast`. |
