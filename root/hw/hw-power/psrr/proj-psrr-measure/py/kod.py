# -*- coding: utf-8 -*-
"""Розгортка PSRR: генератор жене синусоїду по частотах, осцилограф ловить
вхід і вихід, когерентний детектор дістає амплітуди з-під шуму."""
import math
import time

import numpy as np
import pyvisa

VIN_TARGET_PP = 0.200        # цільова пульсація НА ВХОДІ LDO, Vpp
GEN_VPP_MAX = 10.0           # стеля генератора
F_START, F_STOP, PER_DEC = 10.0, 2e6, 10
MARGIN_MIN = 12.0            # менший запас над шумом → числу не віримо


def amp_at(v, dt, f0, window=True):
    """Комплексна амплітуда синусоїди частоти f0 у записі v із кроком dt.
    |Â| — амплітуда (не розмах), arg Â — фаза."""
    n = len(v)
    t = np.arange(n) * dt
    w = np.hanning(n) if window else np.ones(n)
    return 2.0 * np.sum(v * w * np.exp(-2j * math.pi * f0 * t)) / np.sum(w)


def floor_at(v, dt, f0):
    """Шумова підлога: та сама оцінка на сусідніх частотах, де сигналу нема."""
    offs = (0.15, 0.21, 0.29, 0.37, 0.43)
    e = [abs(amp_at(v, dt, f0 * (1 + s * k))) for k in offs for s in (-1, 1)]
    return float(np.median(e))
