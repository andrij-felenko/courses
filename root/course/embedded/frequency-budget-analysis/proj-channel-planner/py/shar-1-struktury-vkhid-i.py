from dataclasses import dataclass
import math                    # math.floor()

# ── Опис радіо: усе так, як стоїть у даташиті ────────────────────────────
@dataclass
class RadioSpec:
    carrier_hz:   float        # несна f₀, Гц     (напр. 2.4e9)
    ppm:          float        # допуск кварцу, частин на мільйон (напр. 40)
    signal_bw_hz: float        # смуга сигналу B, Гц  (з потрібної швидкості)
    guard_hz:     float        # захисний проміжок G на канал, Гц
    rel_speed_ms: float        # взаємна швидкість для Доплера, м/с (0 — нерухомі)
    band_hz:      float        # уся доступна смуга діапазону, Гц

# ── Результат розрахунку ─────────────────────────────────────────────────
@dataclass
class ChannelPlan:
    drift_one_hz:  float       # дрейф несної з ОДНОГО боку (кварц + Доплер), Гц
    slot_hz:       float       # повна ширина слота W = B + 2·Δf + G, Гц
    channels:      int         # скільки слотів влазить у смугу (округлення вниз)
    overhead_frac: float       # частка слота, що пішла НЕ на сигнал (0..1)
