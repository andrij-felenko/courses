#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Стенд верифікації та статистичного аналізу оцінювача стану."""

import math
import struct
from typing import List, Dict, Tuple, Optional


class EstimatorBenchmark:
    """Аналітичний конвеєр для верифікації та тюнінгу фільтра стану."""

    def __init__(self, dt: float = 0.005):
        self.dt = dt  # Базовий крок дискретизації за замовчуванням (200 Гц)
        self.timestamps: List[float] = []
        self.ground_truth: List[float] = []
        self.estimates: List[float] = []
        self.covariances_p: List[float] = []
        self.innovations_y: List[float] = []
        self.covariances_s: List[float] = []

    def parse_binary_log(self, raw_bytes: bytes) -> int:
        """Декодує бінарні пакети структури логу:
        struct LogPacket {
            uint32_t timestamp_us;  // 4 байти
            float raw_sensor;       // 4 байти
            float estimate_x;       // 4 байти
            float cov_p;            // 4 байти
            float innovation_y;     // 4 байти
            float cov_s;            // 4 байти
            float ground_truth;     // 4 байти
        } __attribute__((packed));  // Разом 28 байтів
        """
        packet_size = 28
        fmt = "<I6f"
        count = len(raw_bytes) // packet_size

        self.timestamps.clear()
        self.ground_truth.clear()
        self.estimates.clear()
        self.covariances_p.clear()
        self.innovations_y.clear()
        self.covariances_s.clear()

        for i in range(count):
            chunk = raw_bytes[i * packet_size : (i + 1) * packet_size]
            t_us, raw_z, est_x, cov_p, innov_y, cov_s, gt = struct.unpack(fmt, chunk)
            self.timestamps.append(t_us * 1e-6)
            self.estimates.append(est_x)
            self.covariances_p.append(cov_p)
            self.innovations_y.append(innov_y)
            self.covariances_s.append(cov_s)
            self.ground_truth.append(gt)

        return count

    def compute_rmse(self) -> float:
        """Обчислює Root Mean Square Error (середньоквадратичну похибку)."""
        n = len(self.estimates)
        if n == 0:
            return 0.0
        sum_sq = sum((e - g) ** 2 for e, g in zip(self.estimates, self.ground_truth))
        return math.sqrt(sum_sq / n)

    def compute_max_error(self) -> float:
        """Повертає максимальну абсолютну помилку оцінки."""
        if not self.estimates:
            return 0.0
        return max(abs(e - g) for e, g in zip(self.estimates, self.ground_truth))

    def compute_phase_lag(self, max_lag_steps: int = 40) -> Tuple[float, float]:
        """Знаходить фазовий лаг у секундах через пік кроскореляції між x_est та x_gt."""
        n = len(self.estimates)
        if n <= max_lag_steps:
            return 0.0, 0.0

        mean_est = sum(self.estimates) / n
        mean_gt = sum(self.ground_truth) / n
        x = [v - mean_est for v in self.estimates]
        y = [v - mean_gt for v in self.ground_truth]

        norm_x = math.sqrt(sum(v ** 2 for v in x))
        norm_y = math.sqrt(sum(v ** 2 for v in y))
        if norm_x == 0.0 or norm_y == 0.0:
            return 0.0, 0.0

        best_lag = 0
        best_corr = -1.0

        for lag in range(-max_lag_steps, max_lag_steps + 1):
            s = 0.0
            overlap = 0
            for i in range(n):
                j = i + lag
                if 0 <= j < n:
                    s += x[i] * y[j]
                    overlap += 1
            if overlap > 0:
                corr = s / (norm_x * norm_y)
                if corr > best_corr:
                    best_corr = corr
                    best_lag = lag

        lag_seconds = best_lag * self.dt
        return lag_seconds, best_corr

    def analyze_innovations(self) -> Dict[str, float]:
        """Статистичний аналіз нев'язок (E[y], відсоток виходу за 2σ коридор)."""
        n = len(self.innovations_y)
        if n == 0:
            return {"mean": 0.0, "std": 0.0, "violations_pct": 0.0}

        mean_y = sum(self.innovations_y) / n
        variance_y = sum((y - mean_y) ** 2 for y in self.innovations_y) / (n - 1)
        std_y = math.sqrt(variance_y)

        violations = 0
        for y, s in zip(self.innovations_y, self.covariances_s):
            sigma_bound = 2.0 * math.sqrt(max(1e-12, s))
            if abs(y) > sigma_bound:
                violations += 1

        violations_pct = (violations / n) * 100.0
        return {
            "mean": mean_y,
            "std": std_y,
            "violations_pct": violations_pct,  # Теоретична норма: ~4.55%
        }

    def compute_autocorrelation(self, max_lag: int = 15) -> List[float]:
        """Обчислює вибіркову автокореляцію інновацій r_yy[m] для m = 0..max_lag."""
        n = len(self.innovations_y)
        if n <= max_lag:
            return []

        mean_y = sum(self.innovations_y) / n
        y_centered = [v - mean_y for v in self.innovations_y]
        denom = sum(v ** 2 for v in y_centered)
        if denom == 0.0:
            return [1.0] + [0.0] * max_lag

        r_yy = []
        for m in range(max_lag + 1):
            num = sum(y_centered[k] * y_centered[k + m] for k in range(n - m))
            r_yy.append(num / denom)

        return r_yy

    def compute_nees_and_nis(self) -> Tuple[float, float]:
        """Обчислює середні значення NEES (квадрат помилки/P) та NIS (квадрат інновації/S)."""
        n = len(self.estimates)
        if n == 0:
            return 0.0, 0.0

        nees_sum = 0.0
        nis_sum = 0.0
        for est, gt, p, y, s in zip(
            self.estimates, self.ground_truth, self.covariances_p,
            self.innovations_y, self.covariances_s
        ):
            err = est - gt
            nees_sum += (err ** 2) / max(1e-12, p)
            nis_sum += (y ** 2) / max(1e-12, s)

        avg_nees = nees_sum / n
        avg_nis = nis_sum / n
        return avg_nees, avg_nis


# ── Приклад запуску та верифікації синтетичного набору даних ──────────────────
if __name__ == "__main__":
    import random
    rng = random.Random(42)

    bench = EstimatorBenchmark(dt=0.005)
    raw_buffer = bytearray()

    # Генерація тестового логу на 1000 кроків (5 секунд руху)
    for i in range(1000):
        t_us = i * 5000  # 5 мс у мікросекундах
        t = i * 0.005

        # Еталонний гармонічний рух (Ground Truth)
        true_angle = 15.0 * math.sin(2.0 * math.pi * 0.5 * t)

        # Оцінка фільтра (із шумом та невеликим лагом 10 мс)
        est_angle = 15.0 * math.sin(2.0 * math.pi * 0.5 * (t - 0.010)) + rng.gauss(0, 0.15)
        raw_sensor = true_angle + rng.gauss(0, 0.8)

        # Коваріації стану та інновації
        cov_p = 0.04  # sigma_p = 0.2°
        cov_s = 0.68  # sigma_s = 0.82°
        innov_y = raw_sensor - est_angle

        packet = struct.pack(
            "<I6f",
            t_us,
            raw_sensor,
            est_angle,
            cov_p,
            innov_y,
            cov_s,
            true_angle,
        )
        raw_buffer.extend(packet)

    # Декодування та аналіз
    count = bench.parse_binary_log(bytes(raw_buffer))
    rmse = bench.compute_rmse()
    max_err = bench.compute_max_error()
    lag_sec, corr = bench.compute_phase_lag()
    innov_stats = bench.analyze_innovations()
    autocorr = bench.compute_autocorrelation(max_lag=5)
    nees, nis = bench.compute_nees_and_nis()

    print(f"Оброблено кадрів:        {count}")
    print(f"RMSE:                   {rmse:.4f}°")
    print(f"Максимальна похибка:    {max_err:.4f}°")
    print(f"Фазовий лаг:            {lag_sec * 1000:.1f} мс (кореляція: {corr:.3f})")
    print(f"Середнє інновації E[y]: {innov_stats['mean']:.4f}° (норма: 0.0)")
    print(f"Вильоти за 2σ:          {innov_stats['violations_pct']:.2f}% (норма: ~4.55%)")
    print(f"Автокореляція [0..5]:   {[round(x, 3) for x in autocorr]}")
    print(f"Середній NEES (1 стан): {nees:.3f} (теоретичне матсподівання: 1.0)")
    print(f"Середній NIS (1 вимір): {nis:.3f} (теоретичне матсподівання: 1.0)")
