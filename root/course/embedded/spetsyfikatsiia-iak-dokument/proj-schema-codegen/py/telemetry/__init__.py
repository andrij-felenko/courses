"""Рантайм телеметрійного протоколу для бекенду й стендових скриптів.

Розбір полів робить згенерований Kaitai-парсер — зсуви тут не дублюються.
Пакет додає рівно те, чого декларативна схема принципово не вміє:

* **CRC-16** — у мові виразів Kaitai немає контрольних сум; схема лише
  віддає інстансом ``crc_input`` проміжок байтів, на якому сума рахується;
* **серіалізацію** — Kaitai тільки читає, а стенд мусить іще й слати
  команди вузлові;
* **рамкування потоку** — схема розбирає ГОТОВИЙ кадр, а не шукає його
  початок серед шуму в паузах;
* **таксономію помилок**, однакову з прошивкою: ті самі ERR_INVALID_SOF,
  ERR_INVALID_CRC, ERR_INVALID_LEN, ERR_UNKNOWN_MSG.
"""

from __future__ import annotations

from .crc import CRC16_CHECK_VALUE, CRC16_CHECK_VECTOR, crc16_ccitt, crc_input
from .decoder import (
    DecodedFrame,
    Envelope,
    check_envelope,
    crc_matches_schema,
    decode,
    generated_parser,
)
from .encoder import Ack, Ping, SetConfig, Telemetry, WirePayload, build_frame
from .errors import ParseError, ProtocolError
from .framer import FrameReader, FramerStats, read_frames
from .wire import (
    EOF,
    FLAG_ALERT,
    FLAG_SENSOR_FAULT,
    FOOTER_LEN,
    HEADER_LEN,
    MAX_FRAME,
    MAX_PAYLOAD,
    MIN_FRAME,
    PAYLOAD_SIZE,
    SOF,
    VERSION,
    MsgType,
    StatusCode,
    payload_size,
)

__all__ = [
    "Ack",
    "CRC16_CHECK_VALUE",
    "CRC16_CHECK_VECTOR",
    "DecodedFrame",
    "EOF",
    "Envelope",
    "FLAG_ALERT",
    "FLAG_SENSOR_FAULT",
    "FOOTER_LEN",
    "FrameReader",
    "FramerStats",
    "HEADER_LEN",
    "MAX_FRAME",
    "MAX_PAYLOAD",
    "MIN_FRAME",
    "MsgType",
    "PAYLOAD_SIZE",
    "ParseError",
    "Ping",
    "ProtocolError",
    "SOF",
    "SetConfig",
    "StatusCode",
    "Telemetry",
    "VERSION",
    "WirePayload",
    "build_frame",
    "check_envelope",
    "crc16_ccitt",
    "crc_input",
    "crc_matches_schema",
    "decode",
    "generated_parser",
    "payload_size",
    "read_frames",
]
