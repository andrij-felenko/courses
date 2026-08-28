from dataclasses import dataclass
from typing import Literal

@dataclass
class Reading:
    at: int          # epoch, мс
    celsius: float

@dataclass
class Policy:
    threshold: float
    window_ms: int

# Чисте рішення: ні годинника, ні бази — самі значення на вході.
def decide_cooling(readings: list[Reading], now: int, policy: Policy) -> Literal["on", "off"]:
    in_window = [r for r in readings if r.at >= now - policy.window_ms]
    if not in_window:                                       # немає свідчень — не вмикаємо
        return "off"
    avg = sum(r.celsius for r in in_window) / len(in_window)
    return "on" if avg > policy.threshold else "off"
