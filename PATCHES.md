# Patches in this fork

**This fork is retired.** Every fix it carried has landed in
[frinsen/claude-video](https://github.com/frinsen/claude-video), which also
fixes the three problems this fork left open. Install that one instead:

```bash
claude plugin marketplace add frinsen/claude-video
claude plugin install watch@claude-video
```

Upstream [bradautomates/claude-video](https://github.com/bradautomates/claude-video)
is still dormant — no commits since 2026-06-30, still zero merged pull
requests — so the fixes reached users through that fork rather than through
upstream.

This repository stays up because the four pull requests below are still open
against upstream and point at its branches. Nothing installs from it any more.

## Where each fix went

| Fix | Upstream PR | Disposition in frinsen/claude-video |
|---|---|---|
| Flag hallucinated transcripts | [#223](https://github.com/bradautomates/claude-video/pull/223) | **merged as authored** — `assess_speech()` and the retained `no_speech_prob` / `avg_logprob` |
| Prefer manual captions | [#221](https://github.com/bradautomates/claude-video/pull/221) | **adapted** — human-over-auto is the top rule of its caption picker |
| `-vsync` → `-fps_mode` | [#216](https://github.com/bradautomates/claude-video/pull/216) | **duplicate** — same fix taken from #219, and improved: it probes ffmpeg and falls back to `-vsync` on older builds |
| Console encoding | [#217](https://github.com/bradautomates/claude-video/pull/217) | **duplicate** — same fix taken from #192 |

Dispositions are that fork's own, recorded in its
[UPSTREAM.md](https://github.com/frinsen/claude-video/blob/main/UPSTREAM.md)
ledger; authorship is credited in
[AUTHORS.md](https://github.com/frinsen/claude-video/blob/main/AUTHORS.md).

One commit here was never filed upstream: `c5836df` ranks `en-orig` above `en`
among auto caption tracks, after [@robinjose911 pointed out the
ordering](https://github.com/bradautomates/claude-video/pull/221#issuecomment-5749725319).
It turned out to fix nothing reachable — `-orig` marks the *source* language,
so `en-orig` exists only on English-source videos, where the two tracks are
byte-identical. The other fork reaches the same outcome by ranking the target
language's `-orig` track ahead of everything else.

## What this fork never fixed

All three are fixed in frinsen/claude-video.

- **Non-English videos got machine-translated captions.** `--sub-langs` was
  hardcoded to `en.*`, so a Korean video returned YouTube's English
  translation and never its own track. The upstream complaint is #123, #144
  and #153. That fork detects the video's language and fetches
  `<lang>,<lang>-orig,<lang>-[A-Za-z][A-Za-z]`.
- **NTFS ACL permission warning** ([#107](https://github.com/bradautomates/claude-video/issues/107)).
  `st_mode` does not reflect NTFS ACLs, so the check warned on every session
  even with a correctly locked-down file. That fork skips the check on Windows.
- **Two static-clip dedup tests failed on ffmpeg 9**
  (`test_dedup_collapses_static_by_default`, `test_no_dedup_preserves_static_frames`).
  Fixed there via #175.

Measured 2026-09-22 on Windows 11 with ffmpeg 9: frinsen/claude-video runs 206
tests with no failures; this fork's suite had 3 failures on the same machine.
