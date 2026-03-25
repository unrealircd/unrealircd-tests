# Extended ban tests

Tests for extended bans (extbans) in UnrealIRCd.

## Covered in this directory (9/18)

| Extban | Char | Test file |
|---|---|---|
| `channel` | c | `inchannel` |
| `forward` | f | `forward` |
| `join` | j | `join` |
| `msgbypass` | m | `msgbypass` |
| `nickchange` | n | `nickchange` |
| `quiet` | q | `quiet` |
| `realname` | r | `realname` |
| `security-group` | G | `securitygroup` |
| `text` | T | `text` |

## Tested elsewhere (2)

- `account` (a) — tested in `tests/services/account_extban`
- `time` (t) — tested in `tests/serial/time_extban_expiry`, also used as
  wrapper in `forward` and `text` tests

## Not covered (7)

### GeoIP-dependent (2)

- `asn` (A) — matches AS number
- `country` (C) — matches country code

### TLS-dependent (1)

- `certfp` (S) — matches client certificate fingerprint

### Other (4)

- `flood` (F) — per-user channel flood control
- `inherit` (i) — inherits bans from another channel
- `operclass` (O) — matches oper class
- `partmsg` (p) — restricts part/quit messages
