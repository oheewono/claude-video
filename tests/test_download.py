"""yt-dlp argv construction for download.py.

Regression guard: ``--sub-langs all`` makes yt-dlp fetch YouTube's hundreds of
auto-translated caption tracks, which can take minutes and stalls before the
video download even starts. We only support English, so the request must stay
bounded to the English-only pattern.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "watch" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import download  # noqa: E402

URL = "https://www.youtube.com/watch?v=rlOpbu3Enkw"


def _capture_argv(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Stub subprocess.run inside download.py and record every argv."""
    calls: list[list[str]] = []

    class _Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        return _Result()

    monkeypatch.setattr(download.subprocess, "run", fake_run)
    return calls


def _sub_langs(argv: list[str]) -> str:
    idx = argv.index("--sub-langs")
    return argv[idx + 1]


def _assert_english_only(langs: str) -> None:
    tokens = langs.split(",")
    assert "all" not in tokens, f"sub-langs must not request all languages, got {langs!r}"
    assert all(t.startswith("en") for t in tokens), f"sub-langs must be English-only, got {langs!r}"


def test_fetch_captions_requests_english_only(monkeypatch, tmp_path):
    calls = _capture_argv(monkeypatch)
    download.fetch_captions(URL, tmp_path / "download")
    _assert_english_only(_sub_langs(calls[0]))


def test_download_url_requests_english_only(monkeypatch, tmp_path):
    calls = _capture_argv(monkeypatch)
    # _pick_video returns None with no real file, which raises SystemExit after
    # the yt-dlp argv is already built — that's all we need to inspect.
    with pytest.raises(SystemExit):
        download.download_url(URL, tmp_path / "download")
    _assert_english_only(_sub_langs(calls[0]))


# --- caption picking -------------------------------------------------------
#
# Both manual and auto-generated tracks land as video.<lang>.vtt, so only
# info.json can tell them apart. _pick_subtitle ranks on (manual?, lang).


def _tracks(out_dir: Path, *langs: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for lang in langs:
        (out_dir / f"video.{lang}.vtt").write_text(f"WEBVTT {lang}\n", encoding="utf-8")


def _info(out_dir: Path, subtitles: dict | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "video.info.json"
    payload: dict = {"title": "t"}
    if subtitles is not None:
        payload["subtitles"] = subtitles
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_manual_track_beats_auto(tmp_path):
    out = tmp_path / "download"
    _tracks(out, "en", "en-orig")
    info = _info(out, {"en-GB": [{"ext": "vtt"}]})
    _tracks(out, "en-GB")
    picked = download._pick_subtitle(out, download._manual_sub_langs(info))
    assert picked is not None and picked.name == "video.en-GB.vtt"


def test_auto_prefers_orig_over_translated(tmp_path):
    """en-orig is the source-language ASR track; bare en is the translation
    target. Ranking en first would hand back a machine translation whenever a
    source-language original sits next to it."""
    out = tmp_path / "download"
    _tracks(out, "en", "en-orig")
    info = _info(out, {})
    picked = download._pick_subtitle(out, download._manual_sub_langs(info))
    assert picked is not None and picked.name == "video.en-orig.vtt"


def test_manual_english_picked_when_only_track(tmp_path):
    out = tmp_path / "download"
    _tracks(out, "en")
    info = _info(out, {"en": [{"ext": "vtt"}]})
    picked = download._pick_subtitle(out, download._manual_sub_langs(info))
    assert picked is not None and picked.name == "video.en.vtt"


def test_no_tracks_returns_none(tmp_path):
    out = tmp_path / "download"
    out.mkdir(parents=True)
    assert download._pick_subtitle(out, set()) is None


def test_missing_info_json_yields_no_manual_langs(tmp_path):
    assert download._manual_sub_langs(tmp_path / "video.info.json") == set()
