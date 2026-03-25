# Oper command tests

Tests for commands that require IRC operator privileges.

## Covered commands

| Command | Test file | Notes |
|---|---|---|
| `CHGHOST` | `chghost` | |
| `CHGIDENT` | `chgident` | |
| `CHGNAME` | `chgname` | |
| `DCCDENY` | `dccdeny` | Also tests `UNDCCDENY` |
| `DNS` | `dns` | Core command |
| `GLOBOPS` | `globops` | |
| `KILL` | `kill` | |
| `LOCOPS` | `locops` | |
| `MKPASSWD` | `mkpasswd` | |
| `MODULE` | `module` | Core command |
| `OPER` | `oper` | |
| `OPERMOTD` | `opermotd` | |
| `SAJOIN` | `sajoin` | |
| `SAMODE` | `samode` | |
| `SAPART` | `sapart` | |
| `SETHOST` | `sethost` | |
| `SETIDENT` | `setident` | |
| `TEMPSHUN` | `tempshun` | |
| `TSCTL` | `tsctl` | |
| `WALLOPS` | `wallops` | |

The `tkl` test covers: `KLINE`, `ZLINE`, `GLINE`, `GZLINE`, `SPAMFILTER`.

## Not covered

### TKL subcommands not in `tkl` test

- `ELINE` — exception lines (TKL exemptions)
- `SHUN` — prevents user from executing commands

### Other oper commands

- `ADDMOTD` — appends to MOTD file
- `ADDOMOTD` — appends to oper MOTD file
- `CLOSE` — closes unregistered connections
- `CONNECT` — connects to another server
- `JUMPSERVER` — redirects users to another server
- `RMTKL` — removes TKL entries by pattern
- `SDESC` — changes server description
- `SPAMINFO` — shows spamfilter match details
- `SQUIT` — disconnects a server
- `TLINE` — tests how many users match a host/IP mask
