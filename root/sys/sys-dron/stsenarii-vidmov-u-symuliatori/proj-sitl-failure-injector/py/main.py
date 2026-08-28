import sys
from pyulog import ULog
import numpy as np

def analyze_test_run(ulog_path: str, fault_injection_time_s: float) -> bool:
    try:
        log = ULog(ulog_path)
    except Exception as e:
        print(f"Error reading ULog file: {e}")
        return False

    # 1. Витягуємо дані стану апарата
    status_data = log.get_dataset('vehicle_status').data
    timestamp_s = status_data['timestamp'] * 1e-6
    nav_state = status_data['nav_state']
    failsafe = status_data['failsafe']

    # 2. Знаходимо індекси після моменту інжекції
    post_fault_idx = np.where(timestamp_s >= fault_injection_time_s)[0]
    if len(post_fault_idx) == 0:
        print("FAIL: No telemetry data after fault injection time")
        return False

    # 3. Перевіряємо спрацьовування Failsafe
    failsafe_active = failsafe[post_fault_idx]
    if not np.any(failsafe_active == 1):
        print("FAIL: Failsafe was not triggered after fault injection")
        return False

    first_failsafe_time = timestamp_s[post_fault_idx[np.where(failsafe_active == 1)[0][0]]]
    reaction_time = first_failsafe_time - fault_injection_time_s
    print(f"PASS: Failsafe triggered in {reaction_time:.2f} seconds (Limit: 2.0s)")

    # 4. Перевірка брами інновацій EKF
    try:
        innov_data = log.get_dataset('estimator_innovations').data
        gps_gate = innov_data['gps_hpos_gate_exceeded']
        if np.any(gps_gate[post_fault_idx]):
            print("PASS: EKF innovation gate successfully rejected bad GNSS data")
    except Exception:
        pass

    # 5. Перевірка кутів крену та тангажу (не більше 70 градусів)
    att_data = log.get_dataset('vehicle_attitude').data
    q0, q1, q2, q3 = att_data['q[0]'], att_data['q[1]'], att_data['q[2]'], att_data['q[3]']
    roll = np.arctan2(2.0 * (q0*q1 + q2*q3), 1.0 - 2.0 * (q1*q1 + q2*q2)) * 57.2957795
    pitch = np.arcsin(np.clip(2.0 * (q0*q2 - q3*q1), -1.0, 1.0)) * 57.2957795

    max_roll = np.max(np.abs(roll[post_fault_idx]))
    max_pitch = np.max(np.abs(pitch[post_fault_idx]))
    if max_roll > 70.0 or max_pitch > 70.0:
        print(f"FAIL: Vehicle flipped over! Max Roll={max_roll:.1f}°, Max Pitch={max_pitch:.1f}°")
        return False

    print("PASS: All flight envelope invariants satisfied")
    return reaction_time <= 2.0

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python analyze_log.py <path_to_ulog> <fault_time_s>")
        sys.exit(1)
    success = analyze_test_run(sys.argv[1], float(sys.argv[2]))
    sys.exit(0 if success else 1)
