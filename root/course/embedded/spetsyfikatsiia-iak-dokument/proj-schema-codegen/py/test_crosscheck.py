"""Розбір виводу нативних самотестів.

Сам крос-контроль живе в CI: там байти з прошивки й шлюзу звіряються з
еталонними векторами Python. Тут перевіряється розбір їхнього виводу —
щоб крос-контроль не «зеленів» через те, що просто не знайшов рядка.
"""

from __future__ import annotations

import pytest

import golden_vectors as gv
from crosscheck import VERDICT_OK, check_log, extract_labelled


def c_style_log(frame: bytes) -> str:
    """Так друкує dump() у c/main.c: мітка на 18 позицій, байти через пробіл."""
    hex_part = "".join(f" {byte:02X}" for byte in frame)
    return (
        f"{'Golden frame:':<18}{hex_part}   ({len(frame)} байт)\n"
        "seq=0x4A  T=24.50 C  p=1013.2 hPa  U=3300 mV  alert=1  fault=0\n"
        f"\n{VERDICT_OK}\n"
    )


def cpp_style_log(frame: bytes) -> str:
    """Так друкує dump() у cpp/main.cpp: мітка на 16 позицій, пробіл після байта."""
    hex_part = "".join(f"{byte:02X} " for byte in frame)
    return (
        f"{'Golden frame:':<16}{hex_part} ({len(frame)} байт)\n"
        "seq=0x4A T=24.50 C p=1013.2 hPa U=3300 mV alert=true fault=false\n"
        f"\n{VERDICT_OK}\n"
    )


@pytest.mark.parametrize("render", [c_style_log, cpp_style_log])
def test_extracts_frame_from_both_dialects(render):
    assert extract_labelled(render(gv.GOLDEN_TELEMETRY), "Golden frame:") == gv.GOLDEN_TELEMETRY


def test_length_suffix_is_not_taken_for_bytes():
    # «(17 байт)» стоїть одразу за байтами — дужка мусить обірвати збіг.
    frame = gv.GOLDEN_PING
    assert extract_labelled(c_style_log(frame), "Golden frame:") == frame


@pytest.mark.parametrize("render", [c_style_log, cpp_style_log])
def test_matching_log_has_no_problems(tmp_path, render):
    log = tmp_path / "self-test.log"
    log.write_text(render(gv.GOLDEN_TELEMETRY), encoding="utf-8")

    assert check_log(log) == []


def test_diverged_frame_is_reported(tmp_path):
    log = tmp_path / "self-test.log"
    # Прошивка порахувала температуру іншим масштабом — байти розійшлися.
    log.write_text(c_style_log(gv.NEGATIVE_TEMPERATURE), encoding="utf-8")

    problems = check_log(log)
    assert problems and "еталонний кадр розійшовся" in problems[0]


def test_missing_verdict_is_reported(tmp_path):
    log = tmp_path / "self-test.log"
    text = c_style_log(gv.GOLDEN_TELEMETRY).replace(VERDICT_OK, "Є РОЗБІЖНОСТІ")
    log.write_text(text, encoding="utf-8")

    assert any("самотест не доповів" in problem for problem in check_log(log))


def test_log_without_frame_line(tmp_path):
    log = tmp_path / "empty.log"
    log.write_text("нічого не сталося\n", encoding="utf-8")

    assert check_log(log) == ["у виводі немає рядка «Golden frame:»"]

    with pytest.raises(LookupError):
        extract_labelled("", "Golden frame:")
