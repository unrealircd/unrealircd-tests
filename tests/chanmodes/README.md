# Channel mode tests

Tests for channel modes in UnrealIRCd.

## Covered (24 test files)

| Mode | Letter | Test file | Notes |
|---|---|---|---|
| Ban list | b | `ban` | Core list mode |
| Ban exempt list | e | `exempt` | Core list mode |
| Censor (word filter) | G | `censor` | |
| Delayed join | D | `delayjoin` | |
| Flood protection | f/F | `flood` | +f and +F (flood profile) |
| History | H | `history` | |
| Invite only | i | `inviteonly` | |
| Link (redirect) | L | `link` | |
| No color | c | `nocolor` | |
| No CTCPs | C | `noctcp` | |
| No external messages | n | `noexternal` | |
| No invite | V | `noinvite` | |
| No kick | Q | `nokick` | |
| No knock | K | `noknock` | |
| No nick change | N | `nonickchange` | |
| No notice | T | `nonotice` | |
| Oper only | O | `operonly` | |
| Permanent | P | `permanent` | |
| Private | p | `private` | Hides channel from LIST |
| Registered only join | R | `regonlyjoin` | |
| Registered only speak | M | `regonlyspeak` | |
| Strip color | S | `stripcolor` | |
| Topic limit | t | `topiclimit` | Only ops/halfops can change topic |
| Voice/Halfop/Op/Admin/Owner | v/h/o/a/q | `vhoaq` | Prefix modes |

## Tested elsewhere

These modes have no dedicated test file in this directory but are exercised
in other tests:

- Key (+k) — tested in `chanmodes/link` (redirect on wrong key),
  `usercommands/mode`, `opercommands/samode`
- Limit (+l) — tested in `chanmodes/link` (redirect when limit reached)
- Moderated (+m) — tested in `crules/has_channel_mode`,
  `extbans/msgbypass` (bypass moderation), `chanmodes/flood` (auto-set on
  message flood)
- Secret (+s) — tested in `usercommands/mode` and `opercommands/samode`
  (MODE parameter parsing)
- Post delayed (+d) — tested in `chanmodes/delayjoin` (internal server flag)
- Is registered (+r) — tested in `services/sasl_pre-registration_*`
  (server sets +r after auth)

## Not covered

- Secure only (+z) — requires TLS
- Is secure (+Z) — requires TLS, set when all members are on TLS
