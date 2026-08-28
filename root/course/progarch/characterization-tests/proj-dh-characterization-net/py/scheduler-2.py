# scheduler.py — після рефакторингу. ПОВЕДІНКА та сама (баг теж на місці).
import random
from datetime import datetime


def _threshold(rules, h):
    thr = rules.get("threshold", 20.0)
    if rules.get("night") and (h >= 23 or h < 6):
        thr -= 2.0
    if rules.get("vacation"):
        thr = 12.0                                # антизамерзання
    if 6 <= h < 9:
        thr = rules.get("morning", 21.0)          # ← той самий баг переїхав сюди БЕЗ змін
    return thr


def _climate(t, thr):
    if t is None or t != t:
        return "IDLE"
    if t < thr:
        return "HEAT+" if random.random() < 0.25 else "HEAT"
    if t > thr + 3.0:
        return "COOL"
    return "IDLE"


def plan(sensors, rules):
    out = []
    h = datetime.now().hour                        # ім'я модуля лишилось — шов цілий
    for room, s in sensors.items():
        thr = _threshold(rules, h)
        t = s.get("temp")
        if t is None or t != t:                    # німий давач — і світло не чіпаємо
            out.append(room + ":IDLE")
            continue
        out.append(room + ":" + _climate(t, thr))
        if s.get("motion") and s.get("lux", 999) < 20:
            out.append(room + ":LIGHT")
    return out
