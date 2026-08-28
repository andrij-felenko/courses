from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Temperature:
    value: float
    unit: Literal["C", "F"]

def build_state(d: Device) -> dict:
    temperature = d.temperature                       # єдина правда
    return {
        "temperature": {"value": temperature.value, "unit": temperature.unit},
        "tempC": to_celsius(temperature),             # старе — ПОХІДНЕ від нового
        "at": d.last_reading_at,
    }
