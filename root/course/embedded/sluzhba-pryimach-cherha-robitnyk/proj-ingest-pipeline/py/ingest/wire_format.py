"""Двійковий кадр телеметрії: 24 байти, big-endian, CRC-16/CCITT у хвості.

Розкладка (зміщення в байтах):
    0..1  magic 0xAA55      12..13 raw_temp   int16,  крок 0.01 °C
    2     version           14..15 raw_hum    uint16, крок 0.01 %
    3     flags             16..17 raw_vbat   uint16, крок 0.001 В
    4..7  device_id  uint32 18..19 seq        uint16
    8..11 uptime_ms  uint32 20..21 status     uint16
                           22..23 crc16 по байтах 0..21
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import Enum

FRAME_SIZE = 24
MAGIC = 0xAA55
VERSION = 1
_CRC_POLY = 0x1021

# Структури створюємо один раз: struct.Struct компілює формат, а struct.unpack — ні.
_HEADER = struct.Struct(">HBB")
_BODY = struct.Struct(">IIhHHHH")
_CRC = struct.Struct(">H")


class Reason(str, Enum):
    """Причина, з якої кадр не став подією."""

    BAD_SIZE = "bad_size"
    BAD_MAGIC = "bad_magic"
    BAD_VERSION = "bad_version"
    CRC_MISMATCH = "crc_mismatch"


class DecodeError(Exception):
    def __init__(self, reason: Reason) -> None:
        super().__init__(reason.value)
        self.reason = reason


@dataclass(slots=True)
class RawPacket:
    """Сирий пакет: байти з сокета плюс мітка часу прийому."""

    data: bytes
    recv_wall: float   # t_recv за настінним годинником (unix-час)
    recv_mono: float   # монотонна мітка — нею міряємо затримку
    peer_id: int


@dataclass(slots=True)
class TelemetryFrame:
    device_id: int
    uptime_ms: int
    temperature_c: float
    humidity_pct: float
    battery_v: float
    seq: int
    status: int


@dataclass(slots=True)
class NormalizedEvent:
    device_id: str
    event_time: float   # t_event = t_recv - lag
    lag_ms: int
    temperature_c: float
    humidity_pct: float
    battery_v: float
    seq: int


def crc16_ccitt(data: bytes) -> int:
    """Побітовий CRC-16/CCITT: на 24 байтах таблиця не окупається."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ _CRC_POLY) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def decode_frame(data: bytes) -> TelemetryFrame:
    """Розбирає кадр або кидає DecodeError із причиною відмови."""
    if len(data) != FRAME_SIZE:
        raise DecodeError(Reason.BAD_SIZE)

    magic, version, _flags = _HEADER.unpack_from(data, 0)
    if magic != MAGIC:
        raise DecodeError(Reason.BAD_MAGIC)
    if version != VERSION:
        raise DecodeError(Reason.BAD_VERSION)

    (crc_in,) = _CRC.unpack_from(data, 22)
    if crc_in != crc16_ccitt(data[:22]):
        raise DecodeError(Reason.CRC_MISMATCH)

    device_id, uptime_ms, raw_temp, raw_hum, raw_vbat, seq, status = _BODY.unpack_from(data, 4)
    return TelemetryFrame(
        device_id=device_id,
        uptime_ms=uptime_ms,
        temperature_c=raw_temp * 0.01,
        humidity_pct=raw_hum * 0.01,
        battery_v=raw_vbat * 0.001,
        seq=seq,
        status=status,
    )


def in_physical_range(frame: TelemetryFrame) -> bool:
    """Фізичні межі давачів: усе поза ними — не дані, а несправність."""
    return (
        -40.0 <= frame.temperature_c <= 125.0
        and 0.0 <= frame.humidity_pct <= 100.0
        and 2.5 <= frame.battery_v <= 4.6
    )


def format_device_id(raw_id: int) -> str:
    return f"esp32-{raw_id:08x}"


def encode_frame(
    device_id: int,
    uptime_ms: int,
    raw_temp: int,
    raw_humidity: int,
    raw_battery: int,
    seq: int,
    status: int,
) -> bytes:
    """Складання кадру для генератора навантаження — воно ж документує розкладку."""
    head = _HEADER.pack(MAGIC, VERSION, 0)
    body = _BODY.pack(device_id, uptime_ms, raw_temp, raw_humidity, raw_battery, seq, status)
    return head + body + _CRC.pack(crc16_ccitt(head + body))
