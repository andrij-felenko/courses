# psychrometrics.py — Чиста Python 3 реалізація
import math
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class PsychroResult:
    air_temp_c: float
    rel_humidity_pct: float
    dew_point_c: float
    frost_point_c: float
    sat_vapor_press_kpa: float
    vapor_press_kpa: float

class Psychrometrics:
    MAGNUS_A = 0.61078
    MAGNUS_B = 17.27
    MAGNUS_C = 237.3

    ICE_B = 21.875
    ICE_C = 265.5

    @classmethod
    def compute(cls, temp_c: float, rh_pct: float) -> Optional[PsychroResult]:
        if not (-50.0 <= temp_c <= 80.0 and 0.0 <= rh_pct <= 100.0):
            return None

        p_sat = cls.MAGNUS_A * math.exp((cls.MAGNUS_B * temp_c) / (cls.MAGNUS_C + temp_c))
        p_v = (rh_pct / 100.0) * p_sat

        if rh_pct < 0.001:
            t_d = -50.0
            t_f = -50.0
        else:
            alpha = ((cls.MAGNUS_B * temp_c) / (cls.MAGNUS_C + temp_c)) + math.log(rh_pct / 100.0)
            t_d = (cls.MAGNUS_C * alpha) / (cls.MAGNUS_B - alpha)

            alpha_ice = ((cls.ICE_B * temp_c) / (cls.ICE_C + temp_c)) + math.log(rh_pct / 100.0)
            t_f = (cls.ICE_C * alpha_ice) / (cls.ICE_B - alpha_ice)

        return PsychroResult(
            air_temp_c=temp_c,
            rel_humidity_pct=rh_pct,
            dew_point_c=t_d,
            frost_point_c=t_f,
            sat_vapor_press_kpa=p_sat,
            vapor_press_kpa=p_v
        )
