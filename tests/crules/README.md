# Crule function tests

Tests for the conditional rule (`rule "..."`) functions in UnrealIRCd.

Most functions are tested via `VHOST`: each vhost block in
`serverconfig/unrealircd/crules.conf` has a `match { rule "..."; }` that is
evaluated when the test sends `VHOST <login> <password>`.
Match = vhost applied, no match = denied.

Functions that need `context->text` or `context->destination` (text analysis
and channel-targeting functions) are tested via spamfilter blocks instead.

## Covered functions (48/59)

### Tested in this directory (45)

| Function | Test file |
|---|---|
| `bytes_received()` | `bytes_received` |
| `bytes_sent()` | `bytes_sent` |
| `cap_set()` | `cap_set` |
| `cap_version()` | `cap_version` |
| `channel_count()` | `channel_count` |
| `channel_member_count()` | `channel_member_count` |
| `connected()` | `connected` |
| `connections_from_ip()` | `connections_from_ip` |
| `destination()` | `destination` |
| `digit_percentage()` | `digit_percentage` |
| `directcon()` | `directcon` |
| `has_channel_mode()` | `has_channel_mode` |
| `has_swhois()` | `has_swhois` |
| `has_user_mode()` | `has_user_mode` |
| `idle_time()` | `idle_time` |
| `in_channel()` | `in_channel` |
| `in_security_group()` | `in_security_group` |
| `is_away()` | `is_away` |
| `is_local()` | `is_local` |
| `is_oper()` | `is_oper` |
| `match_away()` | `match_away` |
| `match_class()` | `match_class` |
| `match_ip()` | `match_ip` |
| `match_mask()` | `match_mask` |
| `match_operclass()` | `match_operclass` |
| `match_operlogin()` | `match_operlogin` |
| `match_realhost()` | `match_realhost` |
| `match_realname()` | `match_realname` |
| `match_server()` | `match_server` |
| `match_vhost()` | `match_vhost` |
| `max_repeat_count()` | `max_repeat_count` |
| `messages_received()` | `messages_received` |
| `messages_sent()` | `messages_sent` |
| `mixed_utf8_score()` | `mixed_utf8_score` |
| `non_ascii_percentage()` | `non_ascii_percentage` |
| `online_time()` | `online_time` |
| `reputation()` | `reputation` |
| `server_port()` | `server_port` |
| `tag()` | `tag` |
| `text_byte_count()` | `text_byte_count` |
| `text_character_count()` | `text_character_count` |
| `unicode_block_count()` | `unicode_block_count` |
| `unicode_count()` | `unicode_count` |
| `uppercase_percentage()` | `uppercase_percentage` |
| `word_count()` | `word_count` |

The `logic` test covers `&&` and `!` operators (not a function).

`inchannel()` is a deprecated alias for `in_channel()` and is not tested
separately.

### Tested in `tests/serial/` (1)

| Function | Test file |
|---|---|
| `directop()` | `crule_directop` |

Runs in serial because `directop()` checks global server state (any locally
connected oper), which is affected by other tests OPERing up in parallel.

### Tested in `tests/services/` (2)

These require a services daemon (Anope or Atheme) and live in
`tests/services/` instead:

| Function | Test file |
|---|---|
| `is_identified()` | `crule_is_identified` |
| `match_account()` | `crule_match_account` |

## Not covered (11)

### TLS-dependent (4)

The test framework connects clients on plain-text ports by default.
Testing these would require connecting clients over TLS (ports 5901-5903).

- `is_tls()` — checks if client is using TLS
- `match_certfp()` — matches client certificate fingerprint
- `match_sni()` — matches TLS SNI hostname
- `match_tls_cipher()` — matches TLS cipher suite

### GeoIP-dependent (3)

Test clients connect from localhost (127.0.0.1), which has no GeoIP data.

- `match_asn()` — matches AS number
- `match_asname()` — matches AS name
- `match_country()` — matches country code

### Special infrastructure (3)

These require specific connection types that the test framework does not
set up.

- `is_webirc()` — requires a WEBIRC gateway
- `is_websocket()` — requires a WebSocket client
- `via()` — requires testing message routing paths (takes 2 arguments:
  server mask and port)

### Negative-only gap (1)

- `is_local()` — positive test exists, but a negative test is not feasible:
  VHOST is always processed on the client's own server, so the client is
  always local during evaluation.
