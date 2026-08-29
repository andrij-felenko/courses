"""Кодек 16-байтового кадру польового каналу.

Той самий контракт, що й у прошивці вузла, лише описаний форматами `struct`.
Префікс `<` у кожному форматі — не косметика: без нього Python візьме порядок
байтів хоста разом із вирівнюванням, і поля роз'їдуться з кадром від Cortex-M.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

FRAME_SIZE = 16
MAGIC = 0xAA

TYPE_TELEMETRY = 0x01
TYPE_COMMAND = 0x02
TYPE_ACK = 0x03

CMD_SET_RELAY = 0x10

ACK_OK = 0x00
ACK_UNKNOWN_CMD = 0x01
ACK_BAD_VALUE = 0x02

FLAG_RELAY_ON = 0x01
FLAG_SENSOR_FAULT = 0x02

# Тіло кадру — 14 байтів, які накриває CRC; два останні байти самої суми
# дописуються окремо, тому у форматах їх немає.
_TELEMETRY_BODY = "<BBHIhHBB"
_COMMAND_BODY = "<BBHIBB4x"
_ACK_BODY = "<BBHIBBB3x"

for _fmt in (_TELEMETRY_BODY, _COMMAND_BODY, _ACK_BODY):
    assert struct.calcsize(_fmt) == FRAME_SIZE - 2, _fmt


class FrameError(ValueError):
    """Кадр не пройшов перевірку контракту."""


@dataclass(frozen=True)
class Telemetry:
    node_id: int
    seq: int
    temp_c: float
    battery_mv: int
    relay_on: bool
    sensor_fault: bool


@dataclass(frozen=True)
class Command:
    node_id: int
    seq: int
    cmd_id: int
    value: int


@dataclass(frozen=True)
class Ack:
    node_id: int
    seq: int
    cmd_id: int
    status: int
    relay_on: bool
    sensor_fault: bool


def crc16_ccitt(data: bytes) -> int:
    """CRC-16-CCITT: поліном 0x1021, початкове значення 0xFFFF."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def _seal(body: bytes) -> bytes:
    return body + struct.pack("<H", crc16_ccitt(body))


def encode_telemetry(
    node_id: int,
    seq: int,
    temp_c: float,
    battery_mv: int,
    relay_on: bool = False,
    sensor_fault: bool = False,
) -> bytes:
    flags = (FLAG_RELAY_ON if relay_on else 0) | (FLAG_SENSOR_FAULT if sensor_fault else 0)
    body = struct.pack(
        _TELEMETRY_BODY,
        MAGIC,
        TYPE_TELEMETRY,
        node_id,
        seq,
        round(temp_c * 100),
        battery_mv,
        flags,
        0,
    )
    return _seal(body)


def encode_command(node_id: int, seq: int, cmd_id: int, value: int) -> bytes:
    body = struct.pack(_COMMAND_BODY, MAGIC, TYPE_COMMAND, node_id, seq, cmd_id, value)
    return _seal(body)


def encode_ack(node_id: int, seq: int, cmd_id: int, status: int, flags: int = 0) -> bytes:
    body = struct.pack(_ACK_BODY, MAGIC, TYPE_ACK, node_id, seq, cmd_id, status, flags)
    return _seal(body)


def frame_ok(frame: bytes) -> bool:
    """Магія на місці й CRC зійшлася — критерій межі кадру для кадрувальника."""
    if len(frame) != FRAME_SIZE or frame[0] != MAGIC:
        return False
    (rx_crc,) = struct.unpack("<H", frame[-2:])
    return rx_crc == crc16_ccitt(frame[:-2])


def decode(frame: bytes) -> Telemetry | Command | Ack:
    """Розбирає перевірений кадр. Невідомий тип — це FrameError, не мовчання."""
    if not frame_ok(frame):
        raise FrameError("кадр не пройшов перевірку магії або CRC")

    ftype = frame[1]
    if ftype == TYPE_TELEMETRY:
        _, _, node_id, seq, temp_raw, battery_mv, flags, _ = struct.unpack(
            _TELEMETRY_BODY, frame[:-2]
        )
        return Telemetry(
            node_id=node_id,
            seq=seq,
            temp_c=temp_raw / 100.0,
            battery_mv=battery_mv,
            relay_on=bool(flags & FLAG_RELAY_ON),
            sensor_fault=bool(flags & FLAG_SENSOR_FAULT),
        )
    if ftype == TYPE_COMMAND:
        _, _, node_id, seq, cmd_id, value = struct.unpack(_COMMAND_BODY, frame[:-2])
        return Command(node_id=node_id, seq=seq, cmd_id=cmd_id, value=value)
    if ftype == TYPE_ACK:
        _, _, node_id, seq, cmd_id, status, flags = struct.unpack(_ACK_BODY, frame[:-2])
        return Ack(
            node_id=node_id,
            seq=seq,
            cmd_id=cmd_id,
            status=status,
            relay_on=bool(flags & FLAG_RELAY_ON),
            sensor_fault=bool(flags & FLAG_SENSOR_FAULT),
        )

    raise FrameError(f"невідомий тип кадру 0x{ftype:02X}")
