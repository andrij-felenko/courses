# scheduler.py — успадкований планувальник Digital Homes.
# Розрісся накопиченням «ще одного if». Тестів нема, автори пішли.
import random
from datetime import datetime


def plan(sensors, rules):
    out = []
    h = datetime.now().hour                       # ← дикий вхід: стінний годинник
    base = rules.get("threshold", 20.0)
    for room in sensors:
        s = sensors[room]
        t = s.get("temp")
        thr = base
        if rules.get("night") and (h >= 23 or h < 6):
            thr = base - 2.0
        if rules.get("vacation"):
            thr = 12.0                            # відпустка: лише антизамерзання труб
        if 6 <= h < 9:
            thr = rules.get("morning", 21.0)      # ранкове прогрівання (дописане згодом)
        if t is None or t != t:                   # None або NaN — давач мовчить
            out.append(room + ":IDLE")
            continue
        if t < thr:
            if random.random() < 0.25:            # ← дикий вхід: «комфортний» буст
                out.append(room + ":HEAT+")
            else:
                out.append(room + ":HEAT")
        elif t > thr + 3.0:
            out.append(room + ":COOL")
        else:
            out.append(room + ":IDLE")
        if s.get("motion") and s.get("lux", 999) < 20:
            out.append(room + ":LIGHT")
    return out
