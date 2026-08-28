#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Чисельний розрахунок спектра пропускання та заборонених зон 1D магнонного кристала.
Метод: Матриці переходу (Transfer Matrix Method).
"""

import math
import cmath

def solve_magnonic_crystal():
    # Фізичні константи
    gamma = 1.76e11        # Гіромагнітне відношення (рад / (с · Тл))
    mu0 = 4.0 * math.pi * 1e-7 # Магнітна стала (Гн / м)
    A_ex = 3.7e-12         # Обмінна константа YIG (Дж / м)

    # Параметри підмагнічування та геометрія кристала
    H0 = 1000.0 * (1000.0 / (4.0 * math.pi)) # Поле підмагнічування (А/м, ~1000 Естед)
    
    # Шари періоду A та B
    Ms_A = 140.0 * 1e3    # Намагніченість шару A (А/м, чистий YIG)
    Ms_B = 100.0 * 1e3    # Намагніченість шару B (А/м, імплантований YIG)
    
    dA = 150e-9           # Товщина шару A (150 нм)
    dB = 150e-9           # Товщина шару B (150 нм)
    num_periods = 10      # Кількість періодів кристала

    # Частотний діапазон для сканування (від 3 до 10 ГГц)
    f_start = 3.0e9
    f_stop = 10.0e9
    num_steps = 350
    df = (f_stop - f_start) / num_steps

    print("=== Розрахунок магнонного кристала (TMM) ===")
    print(f"Періодів: {num_periods}, d_A = {dA*1e9:.0f} нм, d_B = {dB*1e9:.0f} нм")
    print("---------------------------------------------------------")
    print("Частота (ГГц) | Пропускання T(w) | Стан зони")
    print("---------------------------------------------------------")

    band_gaps = []
    in_gap = False
    gap_start = 0.0

    for i in range(num_steps + 1):
        f = f_start + i * df
        omega = 2.0 * math.pi * f

        # Обчислення хвильових чисел у шарах A та B
        val_A = (omega / gamma - mu0 * H0) * (mu0 * Ms_A / (2.0 * A_ex))
        val_B = (omega / gamma - mu0 * H0) * (mu0 * Ms_B / (2.0 * A_ex))

        k_A = cmath.sqrt(complex(val_A, 0.0))
        k_B = cmath.sqrt(complex(val_B, 0.0))

        # Матриця переходу для шару A
        m11_A = cmath.cos(k_A * dA)
        m12_A = cmath.sin(k_A * dA) / k_A if abs(k_A) > 1e-12 else complex(dA, 0)
        m21_A = -k_A * cmath.sin(k_A * dA)
        m22_A = cmath.cos(k_A * dA)

        # Матриця переходу для шару B
        m11_B = cmath.cos(k_B * dB)
        m12_B = cmath.sin(k_B * dB) / k_B if abs(k_B) > 1e-12 else complex(dB, 0)
        m21_B = -k_B * cmath.sin(k_B * dB)
        m22_B = cmath.cos(k_B * dB)

        # Перемноження матриць одного періоду M_cell = M_B * M_A
        c11 = m11_B * m11_A + m12_B * m21_A
        c12 = m11_B * m12_A + m12_B * m22_A
        c21 = m21_B * m11_A + m22_B * m21_A
        c22 = m21_B * m12_A + m22_B * m22_A

        # Зведення в ступінь N (кількість періодів)
        res11, res12 = complex(1, 0), complex(0, 0)
        res21, res22 = complex(0, 0), complex(1, 0)

        for _ in range(num_periods):
            n11 = res11 * c11 + res12 * c21
            n12 = res11 * c12 + res12 * c22
            n21 = res21 * c11 + res22 * c21
            n22 = res21 * c12 + res22 * c22
            res11, res12, res21, res22 = n11, n12, n21, n22

        # Коефіцієнт пропускання
        k_in = k_A
        denom = res11 + res22 - 1j * (k_in * res12 + res21 / k_in if abs(k_in) > 1e-12 else complex(0, 0))
        t_amp = 2.0 / denom if abs(denom) > 1e-12 else complex(0, 0)
        T_power = abs(t_amp) ** 2

        # Обмеження значення для коректного відображення
        T_power = min(1.0, max(0.0, T_power))

        is_gap = (T_power < 0.05)
        status = "ЗАБОРОНЕНА ЗОНА (GAP)" if is_gap else "Дозволена смуга"

        if i % 35 == 0:
            print(f"   {f/1e9:6.2f}    |     {T_power:6.4f}     | {status}")

        if is_gap and not in_gap:
            in_gap = True
            gap_start = f / 1e9
        elif not is_gap and in_gap:
            in_gap = False
            band_gaps.append((gap_start, f / 1e9))

    print("---------------------------------------------------------")
    print("Виявлені магнонні заборонені зони:")
    for idx, (g_s, g_e) in enumerate(band_gaps, 1):
        print(f"  Зона {idx}: від {g_s:.2f} ГГц до {g_e:.2f} ГГц (ширина: {(g_e - g_s)*1e3:.1f} МГц)")

if __name__ == "__main__":
    solve_magnonic_crystal()
