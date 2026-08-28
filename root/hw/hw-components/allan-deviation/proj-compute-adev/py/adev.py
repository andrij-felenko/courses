#!/usr/bin/env python3
"""adev.py — перекривна девіація Аллана з журналу відносної частоти.

Виклик:  python adev.py y.txt 1.0      # 1.0 — крок вимірювання τ₀, секунди
Рядок журналу: число y (відносне відхилення частоти) або «*» — пропуск."""
import sys
import numpy as np

MIN_SPANS = 10      # менш як стільки незалежних відрізків τ у записі — не рахуємо


def adev_octaves(y, tau0, min_spans=MIN_SPANS):
    """Дає (τ, σy(τ), доданків, відрізків) для m = 1, 2, 4, 8, …"""
    y = np.asarray(y, dtype=np.float64)
    miss = ~np.isfinite(y)

    # зняти середню частоту: девіація Аллана від сталого зсуву не залежить,
    # а великий зсув під час інтегрування з'їдає значущі цифри
    y = np.where(miss, 0.0, y - y[~miss].mean())

    # один прохід: фаза (секунди) і наростальний лічильник пропусків;
    # фазових точок на одну більше, ніж вимірів
    x = np.concatenate(([0.0], np.cumsum(y) * tau0))
    ng = np.concatenate(([0], np.cumsum(miss)))
    n = x.size

    m = 1
    while 2 * m < n and n // m >= min_spans:
        keep = ng[2 * m:] == ng[:n - 2 * m]              # трійка не накрила пропуск
        d = (x[2 * m:] - 2.0 * x[m:n - m] + x[:n - 2 * m])[keep]
        if d.size >= 2:
            tau = m * tau0
            yield tau, np.sqrt(d @ d / (2.0 * tau * tau * d.size)), d.size, n // m
        m *= 2


if __name__ == "__main__":
    path, tau0 = sys.argv[1], float(sys.argv[2])
    y = np.genfromtxt(path)          # усе, що не число, стає NaN — це й є пропуски
    print("#   tau, s      sigma_y(tau)   доданків   відрізків")
    for tau, sigma, k, spans in adev_octaves(y, tau0):
        print("%9.4g  %14.4e  %9d  %9d" % (tau, sigma, k, spans))
