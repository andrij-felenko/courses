"""CRC-16/CCITT-FALSE — те, чого декларативна схема не вміє в принципі.

Поліном 0x1021, init 0xFFFF, без відображення бітів на вході й на виході,
без фінального XOR. Контрольне значення для рядка "123456789" — 0x29B1;
воно ж стоїть статичним твердженням у C++ і assert-ом у C.
"""

from __future__ import annotations

from collections.abc import Iterable

POLY = 0x1021
INIT = 0xFFFF

CRC16_CHECK_VECTOR = b"123456789"
CRC16_CHECK_VALUE = 0x29B1


def _build_table() -> tuple[int, ...]:
    """Побайтова таблиця: 256 записів замість восьми зсувів на байт."""
    table = []
    for byte in range(256):
        crc = byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
        table.append(crc)
    return tuple(table)


_TABLE = _build_table()


def crc16_ccitt(data: Iterable[int] | bytes | bytearray | memoryview) -> int:
    """Сума за таблицею. Приймає будь-що байтоподібне, зокрема зріз memoryview."""
    crc = INIT
    for byte in data:
        crc = ((crc << 8) & 0xFFFF) ^ _TABLE[((crc >> 8) ^ byte) & 0xFF]
    return crc


def crc_input(frame: bytes | bytearray | memoryview, payload_len: int) -> memoryview:
    """Проміжок кадру, на якому рахується сума: version .. останній байт payload.

    Дзеркало інстансу crc_input зі схеми — тільки тут воно потрібне ще до
    того, як кадр узагалі віддали парсерові.
    """
    from .wire import HEADER_LEN

    view = memoryview(frame)
    return view[1 : HEADER_LEN + payload_len]


def verify(frame: bytes | bytearray | memoryview, payload_len: int) -> tuple[int, int]:
    """(записана в кадрі сума, порахована по вмісту)."""
    from .wire import HEADER_LEN

    view = memoryview(frame)
    at = HEADER_LEN + payload_len
    written = int.from_bytes(view[at : at + 2], "little")
    return written, crc16_ccitt(crc_input(view, payload_len))
