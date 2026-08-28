from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class PreArmCheck:
    name: str
    check: Callable[[], str | None]   # None = ОК; інакше рядок причини
    mandatory: bool                   # чи можна вимкнути

def chk_gps():
    if gps_fix_type() < GPS_FIX_3D or gps_num_sats() < 6:
        return "GPS: 3D fix required"
    return None

def chk_battery():
    if battery_voltage() < arm_min_voltage():
        return "Battery below arming voltage"
    return None
# ... chk_gyro_calibrated, chk_ekf_ready, chk_rc_alive, chk_safety_switch ...

CHECKS = [
    PreArmCheck("GYRO",   chk_gyro_calibrated, True),
    PreArmCheck("EKF",    chk_ekf_ready,       True),
    PreArmCheck("GPS",    chk_gps,             False),   # можна вимкнути для польоту без GPS
    PreArmCheck("RC",     chk_rc_alive,        True),
    PreArmCheck("BATT",   chk_battery,         True),
    PreArmCheck("SAFETY", chk_safety_switch,   True),
]
