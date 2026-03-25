# Database persistence tests

Tests that verify UnrealIRCd correctly writes state to `.db` files and reads
it back after a restart.

## How it works

The tests are split into two phases:

1. **`writing/`** — creates state (TKLs, reputation scores, permanent channels,
   chat history) and verifies it is active on the running server.
2. **`reading/`** — run after a server reboot with `-keepdbs` so the databases
   are preserved. Verifies the state survived the restart.

These tests are excluded from the normal parallel test run and must be run
explicitly, e.g.:

```
./run -boot tests/db/writing/tkl
./run -keepdbs -boot tests/db/reading/tkl
```

## Test files

| Data | Writing | Reading |
|---|---|---|
| TKLs (KLINE, ZLINE, GLINE, GZLINE, SPAMFILTER) | `writing/tkl` | `reading/tkl` |
| Reputation scores | `writing/reputation` | `reading/reputation` |
| Permanent channels (+P modes and lists) | `writing/permanent` | `reading/permanent` |
| Channel history | `writing/history` | `reading/history` |

The history tests require the encryption config (`-include crypt`) since
history is stored encrypted.
