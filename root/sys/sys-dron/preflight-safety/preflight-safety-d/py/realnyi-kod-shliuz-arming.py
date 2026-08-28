from dataclasses import dataclass

@dataclass
class PrearmResult:
    passed: bool               # умова виконана?
    reason: str | None = None  # якщо ні — що саме сказати оператору

# Кожна перевірка звіряє ОДНЕ припущення, яким політ потім довіриться.
def check_compass() -> PrearmResult:
    if not compass_calibrated():  return PrearmResult(False, "компас не скалібровано")
    if not compass_healthy():     return PrearmResult(False, "компас не відповідає")
    if compass_disagree_deg() > 45.0:                   # два компаси — згода?
        return PrearmResult(False, "компаси не згодні між собою")
    return PrearmResult(True)

def check_gps() -> PrearmResult:
    if gps_fix_type() < GPS_FIX_3D:
        return PrearmResult(False, "немає 3D-фіксації GPS")
    if gps_hdop() > 2.0:                                # точність позиції
        return PrearmResult(False, "низька точність GPS")
    return PrearmResult(True)

def check_battery() -> PrearmResult:
    if battery_voltage() < FS_BATT_VOLTAGE:            # поріг failsafe
        return PrearmResult(False, "низька напруга батареї")
    return PrearmResult(True)
