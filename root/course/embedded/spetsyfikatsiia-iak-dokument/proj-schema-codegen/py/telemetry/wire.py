"""Константи формату — переписані з ksy/telemetry_protocol.ksy один в один.

Дублювання тут свідоме й мінімальне: серіалізатор і рамкувальник мусять
знати межі кадру ДО того, як згенерований парсер узагалі втрутиться, —
а він втручається лише коли кадр уже вирізано з потоку й перевірено.
"""

from __future__ import annotations

from enum import IntEnum

SOF = 0xAA
EOF = 0x55
VERSION = 0x01

HEADER_LEN = 6  # sof, version, msg_id, seq_id, payload_len(2)
FOOTER_LEN = 3  # crc16(2), eof
MIN_FRAME = HEADER_LEN + FOOTER_LEN

# Стеля навантаження вузла: більший кадр приймати нема куди й нема навіщо.
MAX_PAYLOAD = 64
MAX_FRAME = HEADER_LEN + MAX_PAYLOAD + FOOTER_LEN

# Біти поля flags у msg_telemetry (instances alert_active / sensor_fault)
FLAG_ALERT = 0x01
FLAG_SENSOR_FAULT = 0x02

# Масштаби з instances: на дроті лише цілі, множення живе на краях каналу.
TEMP_SCALE = 0.01
PRESSURE_SCALE = 0.1


class MsgType(IntEnum):
    """enums::msg_type."""

    CMD_PING = 0x01
    CMD_SET_CONFIG = 0x02
    TELEMETRY_REPORT = 0x20
    CMD_RESPONSE = 0x80


class StatusCode(IntEnum):
    """enums::status_code — код виконання у полі status повідомлення cmd_response."""

    OK = 0x00
    INVALID_CRC = 0x01
    UNKNOWN_CMD = 0x02
    PAYLOAD_LENGTH_MISMATCH = 0x03
    PARAM_OUT_OF_RANGE = 0x04
    HARDWARE_BUSY = 0x05


# Довжини навантажень за схемою. Саме таблиця, а не struct.calcsize від
# структури мови: розкладка в пам'яті залежить від вирівнювання, формат
# на дроті — ні.
PAYLOAD_SIZE: dict[MsgType, int] = {
    MsgType.CMD_PING: 0,
    MsgType.CMD_SET_CONFIG: 5,
    MsgType.TELEMETRY_REPORT: 8,
    MsgType.CMD_RESPONSE: 2,
}


def payload_size(msg_id: int) -> int | None:
    """Очікувана довжина навантаження або None, якщо тип не наш."""
    try:
        return PAYLOAD_SIZE[MsgType(msg_id)]
    except ValueError:
        return None
