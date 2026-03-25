# User mode tests

Tests for user modes in UnrealIRCd.

## Covered (7 test files)

| Mode | Letter | Test file | Notes |
|---|---|---|---|
| Bot | B | `bot` | BOTMOTD, WHOIS bot flag |
| Censor | G | `censor` | Badword replacement in private messages |
| No CTCPs | T | `noctcp` | Blocks incoming CTCPs |
| No kick | q | `nokick` | Oper-only unkickable mode |
| Privacy | p | `privacy` | Hides channels from WHOIS |
| Registered only msg | R | `regonlymsg` | Blocks messages from unregistered users |
| Show WHOIS | W | `showwhois` | Oper-only, notifies on WHOIS |

## Tested elsewhere

These modes have no dedicated test file in this directory but are exercised
in other tests:

- Oper (+o) — tested in `opercommands/oper` (OPER sets +o),
  `usercommands/mode` (can't self-set)
- Registered nick (+r) — tested in `services/sasl_pre-registration_*`
  (services set +r after SASL auth), `usercommands/mode` (can't self-set)
- Host hiding (+x) — tested in `extensions/cap-chghost` (+x/-x triggers
  CHGHOST notification)
- Sethost marker (+t) — tested in `opercommands/sethost` (SETHOST sets +t),
  `usercommands/mode` (can't self-set)
## Not covered

### TLS-dependent (2)

- Secure (+z) — set by server for TLS users, `umode_allow_none`
- Secure only msg (+Z) — only accept messages from TLS users

### Server/services-set only (1)

- Service bot (+S) — set by services, `umode_allow_none`

### Other (7)

- Wallops (+w) — receives WALLOPS messages
- Invisible (+i) — hides from WHO/NAMES for non-common channels
- Server notices (+s) — receives server notice messages
- Deaf (+d) — deaf to channel messages
- Private deaf (+D) — deaf to private messages
- Hide oper (+H) — oper-only, hides oper status
- Hide idle (+I) — hides idle time in WHOIS
