#!/usr/bin/env python3
"""
Nightly Regression Runner with CUSUM Analysis and Automated Git Bisect.
"""
import sys
import json
import subprocess
import dataclasses
from typing import List, Optional, Tuple


@dataclasses.dataclass
class BaselineProfile:
    mean_power_mw: float
    std_power_mw: float
    max_frag_index: float
    p99_latency_us: float


class CusumDetector:
    def __init__(self, target_mean: float, std_dev: float, slack_delta: float = 1.0, threshold_h: float = 4.5):
        self.mu0 = target_mean
        self.sigma = max(std_dev, 1e-6)
        self.k = (slack_delta * self.sigma) / 2.0
        self.h = threshold_h * self.sigma
        self.c_plus = 0.0
        self.c_minus = 0.0

    def update(self, value: float) -> Tuple[bool, float]:
        """Оновлення статистики CUSUM. Повертає (is_alert, c_plus)."""
        self.c_plus = max(0.0, self.c_plus + (value - self.mu0) - self.k)
        self.c_minus = max(0.0, self.c_minus - (value - self.mu0) - self.k)
        is_alert = self.c_plus > self.h
        return is_alert, self.c_plus


def integrate_power_energy(current_samples_ma: List[float], voltage_v: float = 3.3, sample_rate_hz: float = 1000.0) -> Tuple[float, float]:
    """Чисельне інтегрування енергії за методом трапецій."""
    if len(current_samples_ma) < 2:
        return 0.0, 0.0

    dt = 1.0 / sample_rate_hz
    # Переведення струму з мА в А: I_A = I_mA / 1000.0
    # Потужність P = V * I (Вт)
    power_w = [(voltage_v * i_ma / 1000.0) for i_ma in current_samples_ma]
    
    # Інтеграл трапецій: E = dt * ( (P[0] + P[-1])/2 + sum(P[1:-1]) )
    energy_joules = dt * ((power_w[0] + power_w[-1]) / 2.0 + sum(power_w[1:-1]))
    total_time_s = len(current_samples_ma) * dt
    avg_power_mw = (energy_joules / total_time_s) * 1000.0

    return energy_joules, avg_power_mw


def run_automated_bisect(good_commit: str, bad_commit: str, test_command: str) -> Optional[str]:
    """Автоматичний запуск git bisect для виявлення коміту, що вніс регресію."""
    print(f"[*] Starting git bisect between GOOD={good_commit} and BAD={bad_commit}")
    try:
        subprocess.run(["git", "bisect", "reset"], check=False)
        subprocess.run(["git", "bisect", "start", bad_commit, good_commit], check=True)
        
        # Запуск бінарного пошуку за скриптом тестування
        result = subprocess.run(
            ["git", "bisect", "run", "bash", "-c", test_command],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "is the first bad commit" in line:
                bad_hash = line.split()[0]
                print(f"[!] Regression culprit isolated: {bad_hash}")
                return bad_hash
    except subprocess.CalledProcessError as e:
        print(f"[-] Bisect failed with error: {e}")
    finally:
        subprocess.run(["git", "bisect", "reset"], check=False)
    return None


def main():
    baseline = BaselineProfile(
        mean_power_mw=12.5,
        std_power_mw=0.8,
        max_frag_index=0.35,
        p99_latency_us=450.0
    )

    detector = CusumDetector(target_mean=baseline.mean_power_mw, std_dev=baseline.std_power_mw)

    # Імітація серії вимірів нічного прогону
    simulated_current_ma = [3.8] * 500 + [18.2] * 20 + [3.8] * 480
    energy_j, avg_power_mw = integrate_power_energy(simulated_current_ma, voltage_v=3.3, sample_rate_hz=100.0)

    print(f"[+] Total Energy: {energy_j:.4f} Joules, Average Power: {avg_power_mw:.2f} mW")
    is_alert, cusum_stat = detector.update(avg_power_mw)

    if is_alert:
        print(f"[ALERT] Power Regression Detected! CUSUM statistic: {cusum_stat:.2f} > Threshold")
        culprit = run_automated_bisect(
            good_commit="HEAD~10",
            bad_commit="HEAD",
            test_command="python scripts/single_run_benchmark.py --max-power-mw 14.0"
        )
        sys.exit(1 if culprit else 2)
    else:
        print(f"[OK] Nightly run within baseline. CUSUM: {cusum_stat:.2f}")
        sys.exit(0)


if __name__ == "__main__":
    main()
