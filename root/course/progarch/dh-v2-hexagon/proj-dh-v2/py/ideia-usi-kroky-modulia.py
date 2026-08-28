from dataclasses import dataclass, replace
from typing import Protocol

HYSTERESIS = 0.5                     # °C — ширина смуги понад поріг (з кроку про порт)

@dataclass(frozen=True)
class Reading:                       # значення давача з v1: одиниця й статус — у типі
    celsius: float                   # ЗАВЖДИ °C
    ok: bool = True                  # чи це справжнє свіже число

@dataclass(frozen=True)
class Config:
    threshold: float = 20.0          # поріг — вхід рішення, а не його нутрощі

@dataclass(frozen=True)
class Device:                        # доменний пристрій із реєстру
    kind: str                        # "lock", "lamp", "thermostat"…
    room: str
    state: str = "unknown"

def decide(r: Reading, cfg: Config, heating: bool) -> bool:
    if not r.ok:                     # давач мовчить → безпечний спокій (як вирішив v1)
        return False
    if heating:                      # вже гріємо — тримаємо, доки не перескочили верх смуги
        return r.celsius < cfg.threshold + HYSTERESIS
    return r.celsius < cfg.threshold # ще ні — вмикаємо, тільки-но впало під поріг
