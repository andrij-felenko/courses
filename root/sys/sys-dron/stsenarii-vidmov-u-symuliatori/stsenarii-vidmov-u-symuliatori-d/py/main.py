# Автоматизована перевірка Failsafe у CI конвеєрі
from pyulog import ULog
import numpy as np

def verify_simulation_log(ulog_path: str) -> bool:
    log = ULog(ulog_path)
    
    # 1. Перевірка прапорця Failsafe
    status = log.get_dataset('vehicle_status').data
    failsafe_indices = np.where(status['failsafe'] == 1)[0]
    if len(failsafe_indices) == 0:
        print("FAIL: Failsafe flag was never triggered")
        return False
        
    # 2. Перевірка брами інновацій EKF
    innov = log.get_dataset('estimator_innovations').data
    gps_gate = innov['gps_hpos_gate_exceeded']
    if not np.any(gps_gate):
        print("FAIL: Innovation gate did not reject corrupted GPS")
        return False
        
    # 3. Перевірка вертикальної швидкості при посадці
    local_pos = log.get_dataset('vehicle_local_position').data
    vz_landing = local_pos['vz'][-100:]  # Останні 100 відліків
    if np.max(np.abs(vz_landing)) > 2.2:
        print(f"FAIL: Hard landing detected, max vz = {np.max(np.abs(vz_landing))} m/s")
        return False
        
    print("PASS: All Failsafe assertions verified successfully")
    return True
