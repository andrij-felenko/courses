# -*- coding: utf-8 -*-
"""Проєктувальник антивібраційної опори (isolator sizing).

Модель — маса на пружині з в'язким загасанням, один ступінь вільності.
Чистий stdlib, без залежностей: числовий розрахунок, не гарячий шлях.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import pi, sqrt

G = 9.81            # м/с², прискорення вільного падіння
R_THRESH = sqrt(2)  # поріг ізоляції: нижче нього опора підсилює


def transmissibility(r: float, zeta: float) -> float:
    """T(r, ζ): яка частка розмаху проходить крізь опору."""
    num = 1.0 + (2.0 * zeta * r) ** 2
    den = (1.0 - r * r) ** 2 + (2.0 * zeta * r) ** 2
    return sqrt(num / den)


def ratio_for_target(target_T: float, zeta: float) -> float:
    """Найменше r > √2, за якого T(r, ζ) = target_T.

    Точний корінь квадратного рівняння відносно u = r²:
        A·u² + B·u + C = 0,   A = T²,  B = −[2T² + a(1−T²)],  C = T² − 1,
    де a = (2ζ)². Бо C < 0, корені різного знака — беремо додатний.
    """
    if not 0.0 < target_T < 1.0:
        raise ValueError("target_T має бути в межах (0, 1)")
    a = (2.0 * zeta) ** 2
    A = target_T * target_T
    negB = 2.0 * A + a * (1.0 - A)       # = −B, завжди додатне
    C = A - 1.0                          # < 0
    disc = negB * negB - 4.0 * A * C     # −4AC > 0 → disc > 0 завжди
    u = (negB + sqrt(disc)) / (2.0 * A)  # додатний корінь = r²
    return sqrt(u)
