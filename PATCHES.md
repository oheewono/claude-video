# Patches in this fork

Fork of [bradautomates/claude-video](https://github.com/bradautomates/claude-video)
carrying fixes that are open upstream but not yet merged. Upstream's `main` has
had no commits since 2026-06-30 and has never merged a pull request, so this
fork exists to make the skill usable in the meantime.

Every change here is also filed upstream. If those land, this fork should go
away.

| Fix | Upstream PR | Why |
|---|---|---|
| `-vsync` → `-fps_mode` | [#216](https://github.com/bradautomates/claude-video/pull/216) | `-vsync` was removed in ffmpeg 8. Without this, frame extraction fails outright on ffmpeg 8+ and `/watch` returns nothing. |
| Console encoding | [#217](https://github.com/bradautomates/claude-video/pull/217) | `watch.py` and `setup.py` crash with `UnicodeEncodeError` on Windows consoles whose codepage cannot encode em dashes (cp1252, cp949, ...). |
| Prefer manual captions | [#221](https://github.com/bradautomates/claude-video/pull/221) | The caption picker sorted by filename, so an auto-generated track beat a human-authored one. Auto-captions are ~2.6x the tokens, unpunctuated, and mistranscribe proper nouns. |
| Rank `en-orig` above `en` | [#221](https://github.com/bradautomates/claude-video/pull/221) (follow-up) | Among auto tracks `en-orig` is the source-language ASR output and bare `en` is YouTube's translation target. Reported by [@robinjose911](https://github.com/bradautomates/claude-video/pull/221#issuecomment-5749725319); this fork now diverges from #221 as filed, which ranked `en` first. |
| Flag hallucinated transcripts | [#222](https://github.com/bradautomates/claude-video/issues/222) (issue) | Whisper invents dialogue over music or silence and the report presented it as a normal transcript. Now labelled low-confidence, using the `no_speech_prob` that `verbose_json` already returned and the code discarded. |

Each fix is one commit, so `git log` is the index:

```bash
git log --oneline 83da59f..main
```

## Install

```bash
claude plugin marketplace add oheewono/claude-video
claude plugin install watch@claude-video-patched
```

Uninstall the upstream plugin first if you have it — both provide `/watch`.

## Known issues not fixed here

- The NTFS ACL permission warning on Windows ([#107](https://github.com/bradautomates/claude-video/issues/107)). `st_mode` does not reflect NTFS ACLs, so the check warns even on a correctly locked-down file. Cosmetic.
- Two static-clip dedup tests fail on ffmpeg 9 (`test_dedup_collapses_static_by_default`, `test_no_dedup_preserves_static_frames`). Not attributed to any of the above; flagged in #217.
