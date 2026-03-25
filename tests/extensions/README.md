# Extension tests

Tests for IRCv3 capabilities, message tags, and related extensions.

## Covered

| Test file | What it tests |
|---|---|
| `away-notify` | `away-notify` capability |
| `bot-tag` | `bot` message tag |
| `cap` | `CAP` command / capability negotiation |
| `cap-chghost` | `chghost` capability |
| `chathistory` | `CHATHISTORY` command / `draft/chathistory` capability |
| `extended-join` | `extended-join` capability |
| `extjwt` | `EXTJWT` command |
| `labeled-response` | `labeled-response` capability + `label` message tag |
| `multi-prefix` | `multi-prefix` capability |
| `userhost-in-names` | `userhost-in-names` capability |

## Message tag coverage

UnrealIRCd registers 16 message tags. Only 2 have dedicated tests:

| Tag | Tested | Notes |
|---|---|---|
| `account` | no | Sent with messages when `account-tag` cap is active |
| `batch` | no | Used internally by `labeled-response` and `chathistory` |
| `bot` | **yes** | `bot-tag` test |
| `label` | **yes** | `labeled-response` test |
| `msgid` | no | Message IDs, sent automatically on every message |
| `time` | no | Server-time timestamps, sent automatically |
| `+draft/channel-context` | no | Channel context for direct messages |
| `+draft/reply` | no | Reply threading |
| `+draft/typing` | no | Typing indicator (draft) |
| `+typing` | no | Typing indicator |
| `unrealircd.org/geoip` | no | GeoIP data in tags — requires GeoIP |
| `unrealircd.org/issued-by` | no | Shows who issued an oper action |
| `unrealircd.org/json-log` | no | JSON structured log data |
| `unrealircd.org/real-quit-reason` | no | Real quit reason (visible to opers) |
| `unrealircd.org/userhost` | no | user@host in message tags |
| `unrealircd.org/userip` | no | user@ip in message tags |

## Capability coverage

UnrealIRCd registers 28 client capabilities.

### Tested in this directory (9)

`away-notify`, `chghost`, `draft/chathistory`, `extended-join`,
`labeled-response`, `multi-prefix`, `userhost-in-names`,
`cap-notify` (via `cap` test), `batch` (via `labeled-response` test).

### Tested elsewhere (6)

- `account-notify` — tested in `tests/services/account-notify`
- `echo-message` — used in `tests/extensions/labeled-response` and `tests/services/account-tag`
- `invite-notify` — tested in `tests/usercommands/invite`
- `sasl` — tested in `tests/services/`
- `server-time` — requested and used in 6 tests (history, chathistory, labeled-response)
- `setname` — tested in `tests/usercommands/setname`

### Used by test framework but not tested directly (2)

- `message-tags` — requested by all test clients
- `account-tag` — requested by all test clients

### Informational-only capabilities (4)

These are advertise-only (`CLICAP_FLAGS_ADVERTISE_ONLY`): they appear in
CAP LS with a value but are not requestable by clients via CAP REQ.
Testing would be limited to verifying the advertised value.

- `sts` — strict transport security parameters — only visible over TLS
- `unrealircd.org/history-storage` — history backend type and limits
- `unrealircd.org/link-security` — link security level (verified advertised in `cap` test)
- `unrealircd.org/plaintext-policy` — plaintext connection policy

### Not covered (6)

- `draft/extended-isupport` — extended ISUPPORT via CAP
- `draft/no-implicit-names` — suppresses automatic NAMES on JOIN
- `extended-monitor` — extended MONITOR notifications
- `standard-replies` — standard reply format (FAIL/WARN/NOTE)
- `tls` — STARTTLS — requires TLS
- `unrealircd.org/json-log` — JSON log subscription
