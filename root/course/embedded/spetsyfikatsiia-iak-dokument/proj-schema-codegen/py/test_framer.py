"""Рамкування: як кадр знаходять у потоці, де є шум і немає меж.

Схема розбирає готовий кадр — межі йому дає цей автомат. Тому кожен тест
тут про те, що робить приймач вузла, коли в паузі між пакетами прилетіло
сміття, коли пакет розірвало на шматки або коли байт 0xAA трапився
всередині шуму.
"""

from __future__ import annotations

import io

import golden_vectors as gv
from telemetry import FrameReader, read_frames

NOISE = b"\x00\x11\x22\x33"

# Кадр із навмисно битою сумою й БЕЗ жодного 0xAA поза стартовим маркером:
# так поведінка ресинхронізації однозначна, а не «як пощастить із CRC».
BAD_CRC_FRAME = gv.build_frame(
    gv.MSG_TELEMETRY,
    gv.telemetry_payload(2450, 10132, 3300, flags=gv.FLAG_ALERT),
    seq_id=0x4A,
    crc=0x1234,
)
BAD_EOF_FRAME = gv.build_frame(
    gv.MSG_TELEMETRY,
    gv.telemetry_payload(2450, 10132, 3300),
    seq_id=0x4A,
    crc=0x1234,
    eof=0x00,
)


def test_clean_frame_passes_through():
    reader = FrameReader()
    assert reader.feed(gv.GOLDEN_TELEMETRY) == [gv.GOLDEN_TELEMETRY]
    assert reader.stats.frames == 1
    assert reader.stats.dropped == 0
    assert reader.pending == 0


def test_noise_around_frame_is_discarded():
    reader = FrameReader()
    frames = reader.feed(NOISE + gv.GOLDEN_TELEMETRY)

    assert frames == [gv.GOLDEN_TELEMETRY]
    assert reader.stats.dropped == len(NOISE)


def test_byte_at_a_time_delivery():
    # UART віддає по байту; кадр не має розсипатися від цього.
    reader = FrameReader()
    collected = []
    for byte in NOISE + gv.GOLDEN_TELEMETRY:
        collected += reader.feed(bytes([byte]))

    assert collected == [gv.GOLDEN_TELEMETRY]
    assert reader.stats.bytes_in == len(NOISE) + len(gv.GOLDEN_TELEMETRY)


def test_two_frames_in_one_chunk():
    reader = FrameReader()
    frames = reader.feed(gv.GOLDEN_TELEMETRY + gv.GOLDEN_PING)

    assert frames == [gv.GOLDEN_TELEMETRY, gv.GOLDEN_PING]
    assert reader.stats.frames == 2


def test_partial_frame_waits_for_the_rest():
    reader = FrameReader()
    assert reader.feed(gv.GOLDEN_TELEMETRY[:10]) == []
    assert reader.pending == 10

    assert reader.feed(gv.GOLDEN_TELEMETRY[10:]) == [gv.GOLDEN_TELEMETRY]
    assert reader.pending == 0


def test_bad_crc_frame_does_not_swallow_the_next_one():
    # Головна пастка наївного рамкувальника: викинути весь буфер і разом
    # із битим кадром проґавити цілий наступний.
    reader = FrameReader()
    frames = reader.feed(BAD_CRC_FRAME + gv.GOLDEN_TELEMETRY)

    assert frames == [gv.GOLDEN_TELEMETRY]
    assert reader.stats.bad_crc == 1
    assert reader.stats.frames == 1
    assert reader.stats.dropped == len(BAD_CRC_FRAME)


def test_bad_eof_frame_is_dropped():
    reader = FrameReader()
    frames = reader.feed(BAD_EOF_FRAME + gv.GOLDEN_PING)

    assert frames == [gv.GOLDEN_PING]
    assert reader.stats.bad_eof == 1


def test_false_start_marker_inside_noise():
    # 0xAA у шумі дає заявлену довжину 0x4A20 — понад стелю вузла, отже
    # це не заголовок, а збіг.
    reader = FrameReader()
    frames = reader.feed(b"\xaa\xff" + gv.GOLDEN_TELEMETRY)

    assert frames == [gv.GOLDEN_TELEMETRY]
    assert reader.stats.bad_len == 1
    assert reader.stats.resyncs == 1


def test_pure_noise_never_accumulates():
    reader = FrameReader()
    for _ in range(100):
        assert reader.feed(NOISE) == []
    assert reader.pending == 0  # буфер не росте без меж
    assert reader.stats.dropped == 400


def test_reset_forgets_the_tail():
    reader = FrameReader()
    reader.feed(gv.GOLDEN_TELEMETRY[:10])
    reader.reset()

    assert reader.pending == 0
    assert reader.feed(gv.GOLDEN_TELEMETRY) == [gv.GOLDEN_TELEMETRY]


def test_read_frames_over_a_stream():
    dump = NOISE + gv.GOLDEN_TELEMETRY + NOISE + gv.GOLDEN_SET_CONFIG + gv.GOLDEN_ACK
    reader = FrameReader()

    # Шматок навмисно не кратний довжині кадру: межі мусять знаходитися самі.
    frames = list(read_frames(reader, io.BytesIO(dump), chunk_size=7))

    assert frames == [gv.GOLDEN_TELEMETRY, gv.GOLDEN_SET_CONFIG, gv.GOLDEN_ACK]
    assert reader.stats.frames == 3
    assert reader.stats.dropped == 2 * len(NOISE)
