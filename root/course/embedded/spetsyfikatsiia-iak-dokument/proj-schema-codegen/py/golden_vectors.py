"""Еталонні кадри (Golden Packets) для схеми telemetry_protocol.ksy.

Кадр: SOF(1) version(1) msg_id(1) seq_id(1) payload_len(2, LE) payload
      crc16(2, LE) EOF(1). CRC-16/CCITT-FALSE рахується від version до
      останнього байта payload — ні SOF, ні саме поле суми в неї не входять.

Вектори будуються тут, а не лежать шматком hex у тесті: так видно, з яких
саме чисел вони склалися, і зіпсувати їх під негативний випадок можна
одним іменованим аргументом.

Файл навмисно не залежить від пакета telemetry й користується самим лише
struct: вектор, зібраний тим самим кодом, який він перевіряє, нічого не
доводить. Збіг цих байтів із виходом telemetry.encoder — окремий тест.
"""

from __future__ import annotations

import struct

SOF = 0xAA
EOF = 0x55
VERSION = 0x01
HEADER_LEN = 6
FOOTER_LEN = 3

MSG_PING = 0x01
MSG_SET_CONFIG = 0x02
MSG_TELEMETRY = 0x20
MSG_RESPONSE = 0x80

STATUS_OK = 0x00

FLAG_ALERT = 0x01
FLAG_SENSOR_FAULT = 0x02


def crc16_ccitt(data: bytes) -> int:
    """CRC-16/CCITT-FALSE: поліном 0x1021, init 0xFFFF, без відображення бітів."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def build_frame(
    msg_id: int,
    payload: bytes,
    *,
    seq_id: int = 0x00,
    version: int = VERSION,
    sof: int = SOF,
    eof: int = EOF,
    declared_len: int | None = None,
    crc: int | None = None,
) -> bytes:
    """Збирає кадр. Іменовані аргументи дозволяють збрехати в будь-якому полі:
    declared_len — заявити не ту довжину, crc — лишити стару суму."""
    if declared_len is None:
        declared_len = len(payload)
    body = bytes([version, msg_id, seq_id]) + struct.pack("<H", declared_len) + payload
    if crc is None:
        crc = crc16_ccitt(body)
    return bytes([sof]) + body + struct.pack("<H", crc) + bytes([eof])


def telemetry_payload(
    temp_raw: int, pressure_raw: int, voltage_mv: int, flags: int = 0x00, reserved: int = 0x00
) -> bytes:
    return struct.pack("<hHHBB", temp_raw, pressure_raw, voltage_mv, flags, reserved)


def set_config_payload(sample_rate_hz: int, alert_threshold_raw: int, flags_enable: int) -> bytes:
    return struct.pack("<HhB", sample_rate_hz, alert_threshold_raw, flags_enable)


def ack_payload(target_seq_id: int, status: int) -> bytes:
    return bytes([target_seq_id, status])


def frame_crc(frame: bytes) -> tuple[int, int]:
    """(записана в кадрі, порахована по вмісту).

    Kaitai читає crc16 як звичайне число й нічого не звіряє — перевірка суми
    лишається за нами, як і за прошивкою.
    """
    written = struct.unpack_from("<H", frame, len(frame) - FOOTER_LEN)[0]
    return written, crc16_ccitt(frame[1:-FOOTER_LEN])


def flip_bit(frame: bytes, index: int, mask: int = 0x01) -> bytes:
    """Псує один біт кадру, не чіпаючи поле суми."""
    corrupted = bytearray(frame)
    corrupted[index] ^= mask
    return bytes(corrupted)


GOLDEN_TELEMETRY = build_frame(
    MSG_TELEMETRY,
    telemetry_payload(temp_raw=2450, pressure_raw=10132, voltage_mv=3300, flags=FLAG_ALERT),
    seq_id=0x4A,
)

# 0xFEC8 у доповняльному коді = -312 -> -3.12 °C
NEGATIVE_TEMPERATURE = build_frame(
    MSG_TELEMETRY,
    telemetry_payload(temp_raw=-312, pressure_raw=10000, voltage_mv=3290, flags=FLAG_SENSOR_FAULT),
    seq_id=0x4B,
)

GOLDEN_SET_CONFIG = build_frame(
    MSG_SET_CONFIG,
    set_config_payload(sample_rate_hz=100, alert_threshold_raw=8500, flags_enable=0x03),
    seq_id=0x10,
)

GOLDEN_ACK = build_frame(MSG_RESPONSE, ack_payload(0x10, STATUS_OK), seq_id=0x11)

GOLDEN_PING = build_frame(MSG_PING, b"", seq_id=0x12)

ALL_GOLDEN = {
    "telemetry": GOLDEN_TELEMETRY,
    "negative temp": NEGATIVE_TEMPERATURE,
    "set_config": GOLDEN_SET_CONFIG,
    "ack": GOLDEN_ACK,
    "ping": GOLDEN_PING,
}
