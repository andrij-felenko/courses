from dataclasses import dataclass
from typing import Literal, TypedDict

@dataclass(frozen=True)
class Temperature:
    value: float
    unit: Literal["C", "F"]

@dataclass(frozen=True)
class Device:
    id: str
    temperature: Temperature     # канонічне джерело правди
    last_reading_at_ms: int      # канонічне: epoch у мілісекундах

class DeviceStateDTO(TypedDict):
    temperature: dict
    atMs: int
    tempC: float
    at: int

def to_celsius(t: Temperature) -> float:
    return t.value if t.unit == "C" else (t.value - 32) * 5 / 9

def build_device_state(d: Device) -> DeviceStateDTO:
    return {
        "temperature": {"value": d.temperature.value, "unit": d.temperature.unit},  # нове
        "atMs": d.last_reading_at_ms,                       # нове
        "tempC": round(to_celsius(d.temperature), 1),       # старе — ПОХІДНЕ
        "at": d.last_reading_at_ms // 1000,                 # старе — ПОХІДНЕ (секунди)
    }
