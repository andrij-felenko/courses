"""Серіалізація кадрів.

Kaitai Struct лише читає — записувати він не вміє за задумом. А стенд і
бекенд мусять слати вузлові cmd_set_config і cmd_ping, тож бік запису
пишеться руками. Щоб він не розійшовся зі схемою, тест звіряє його вихід
байт-у-байт із еталонними векторами, зібраними незалежно (golden_vectors).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import ClassVar

from .crc import crc16_ccitt
from .wire import (
    EOF,
    FLAG_ALERT,
    FLAG_SENSOR_FAULT,
    MAX_PAYLOAD,
    PRESSURE_SCALE,
    SOF,
    TEMP_SCALE,
    VERSION,
    MsgType,
    StatusCode,
)


def _fits(name: str, value: int, bits: int, *, signed: bool) -> int:
    """Перевіряє, що число справді влізе в поле на дроті.

    struct.pack і сам кинув би struct.error, але з повідомленням про
    формат, а не про поле: «argument out of range» не підказує, що саме
    ти намагався запхати в s2.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name}: очікували ціле, дістали {type(value).__name__}")
    low = -(1 << (bits - 1)) if signed else 0
    high = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1
    if not low <= value <= high:
        raise ValueError(f"{name}={value} не вміщується в діапазон поля [{low}, {high}]")
    return value


@dataclass(frozen=True, slots=True)
class Ping:
    """cmd_ping — кадр без навантаження, але з повноцінною сумою."""

    MSG_ID: ClassVar[MsgType] = MsgType.CMD_PING

    def to_wire(self) -> bytes:
        return b""


@dataclass(frozen=True, slots=True)
class SetConfig:
    """types::msg_set_config."""

    MSG_ID: ClassVar[MsgType] = MsgType.CMD_SET_CONFIG
    FORMAT: ClassVar[str] = "<HhB"

    sample_rate_hz: int
    alert_threshold_raw: int
    flags_enable: int = 0

    def __post_init__(self) -> None:
        _fits("sample_rate_hz", self.sample_rate_hz, 16, signed=False)
        _fits("alert_threshold_raw", self.alert_threshold_raw, 16, signed=True)
        _fits("flags_enable", self.flags_enable, 8, signed=False)

    @classmethod
    def from_physical(
        cls, *, sample_rate_hz: int, alert_threshold_c: float, flags_enable: int = 0
    ) -> SetConfig:
        return cls(
            sample_rate_hz=sample_rate_hz,
            alert_threshold_raw=round(alert_threshold_c / TEMP_SCALE),
            flags_enable=flags_enable,
        )

    @property
    def alert_threshold_c(self) -> float:
        return self.alert_threshold_raw * TEMP_SCALE

    def to_wire(self) -> bytes:
        return struct.pack(self.FORMAT, self.sample_rate_hz, self.alert_threshold_raw,
                           self.flags_enable)


@dataclass(frozen=True, slots=True)
class Telemetry:
    """types::msg_telemetry разом з instances у вигляді властивостей."""

    MSG_ID: ClassVar[MsgType] = MsgType.TELEMETRY_REPORT
    FORMAT: ClassVar[str] = "<hHHBB"

    temp_raw: int
    pressure_raw: int
    voltage_mv: int
    flags: int = 0
    reserved: int = 0

    def __post_init__(self) -> None:
        _fits("temp_raw", self.temp_raw, 16, signed=True)
        _fits("pressure_raw", self.pressure_raw, 16, signed=False)
        _fits("voltage_mv", self.voltage_mv, 16, signed=False)
        _fits("flags", self.flags, 8, signed=False)
        _fits("reserved", self.reserved, 8, signed=False)

    @classmethod
    def from_physical(
        cls,
        *,
        temperature_c: float,
        pressure_hpa: float,
        voltage_mv: int,
        alert: bool = False,
        fault: bool = False,
    ) -> Telemetry:
        """Зворотний бік instances: фізична величина -> сирий код датчика."""
        flags = (FLAG_ALERT if alert else 0) | (FLAG_SENSOR_FAULT if fault else 0)
        return cls(
            temp_raw=round(temperature_c / TEMP_SCALE),
            pressure_raw=round(pressure_hpa / PRESSURE_SCALE),
            voltage_mv=voltage_mv,
            flags=flags,
        )

    @property
    def temperature_c(self) -> float:
        return self.temp_raw * TEMP_SCALE

    @property
    def pressure_hpa(self) -> float:
        return self.pressure_raw * PRESSURE_SCALE

    @property
    def alert_active(self) -> bool:
        return (self.flags & FLAG_ALERT) != 0

    @property
    def sensor_fault(self) -> bool:
        return (self.flags & FLAG_SENSOR_FAULT) != 0

    def to_wire(self) -> bytes:
        return struct.pack(self.FORMAT, self.temp_raw, self.pressure_raw, self.voltage_mv,
                           self.flags, self.reserved)


@dataclass(frozen=True, slots=True)
class Ack:
    """types::msg_ack_response."""

    MSG_ID: ClassVar[MsgType] = MsgType.CMD_RESPONSE
    FORMAT: ClassVar[str] = "<BB"

    target_seq_id: int
    status: StatusCode | int = StatusCode.OK

    def __post_init__(self) -> None:
        _fits("target_seq_id", self.target_seq_id, 8, signed=False)
        _fits("status", int(self.status), 8, signed=False)

    def to_wire(self) -> bytes:
        return struct.pack(self.FORMAT, self.target_seq_id, int(self.status))


WirePayload = Ping | SetConfig | Telemetry | Ack


def build_frame(
    payload: WirePayload, *, seq_id: int = 0x00, version: int = VERSION
) -> bytes:
    """Збирає кадр цілком: заголовок, навантаження, сума, кінцевий маркер."""
    _fits("seq_id", seq_id, 8, signed=False)
    _fits("version", version, 8, signed=False)

    body_payload = payload.to_wire()
    if len(body_payload) > MAX_PAYLOAD:
        raise ValueError(
            f"навантаження {len(body_payload)} байт понад стелю вузла {MAX_PAYLOAD}"
        )

    body = struct.pack(
        "<BBBH", version, int(payload.MSG_ID), seq_id, len(body_payload)
    ) + body_payload
    return bytes([SOF]) + body + struct.pack("<H", crc16_ccitt(body)) + bytes([EOF])
