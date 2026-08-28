#!/usr/bin/env python3
"""
STTSimulator: RK4 Macrospin LLGS Dynamics Simulator for pMTJ STT-MRAM Cells.
Calculates switching trajectories, critical current thresholds, and dynamic resistance.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, Dict

# Фізичні фундаментальні константи
HBAR = 1.054571817e-34      # Зведена стала Планка (Дж·с)
E_CHARGE = 1.602176634e-19  # Елементарний заряд (Кл)
MU_0 = 4.0 * np.pi * 1e-7   # Магнітна стала (Гн/м)
GAMMA_0 = 2.211e5           # Гіромагнітне відношення (м/(А·с))
KB = 1.380649e-23           # Стала Больцмана (Дж/К)


@dataclass
class STTCellParameters:
    """Фізичні та геометріяні параметри комірки pMTJ."""
    Ms: float = 1.0e6         # Намагніченість насичення CoFeB (А/м)
    Hk_eff: float = 3.0e5     # Ефективне поле анізотропії (А/м)
    alpha: float = 0.01       # Безрозмірний коефіцієнт загасання Ґільберта
    P: float = 0.65           # Спінова поляризація струму
    thickness: float = 1.4e-9 # Товщина вільного шару d (м)
    diameter: float = 45e-9   # Діаметр pMTJ (м)
    R_P: float = 4500.0       # Опір у паралельному стані (Ом)
    TMR: float = 1.80         # Тунельний магнітоопір (180%)

    @property
    def area(self) -> float:
        """Площа поперечного перерізу (м²)."""
        return np.pi * (self.diameter / 2.0)**2

    @property
    def volume(self) -> float:
        """Об'єм вільного шару (м³)."""
        return self.area * self.thickness

    @property
    def critical_current_j0(self) -> float:
        """Критична густина струму J_c0 при T = 0 K (А/м²)."""
        g0 = self.P / (1.0 + self.P**2)
        numerator = 2.0 * E_CHARGE * MU_0 * self.Ms * self.thickness * self.alpha * self.Hk_eff
        denominator = HBAR * self.P * g0
        return numerator / denominator

    @property
    def critical_current_i0(self) -> float:
        """Критичний струм I_c0 (А)."""
        return self.critical_current_j0 * self.area


class LLGSSolver:
    """Обчислювальне ядро інтегрування рівняння ЛЛҐС."""

    def __init__(self, params: STTCellParameters):
        self.p = params
        self.gamma_prime = GAMMA_0 / (1.0 + self.p.alpha**2)
        # Вектор поляризації за замовчуванням вздовж легкої осі +Z
        self.p_vec = np.array([0.0, 0.0, 1.0])

    def slonczewski_efficiency(self, cos_theta: float) -> float:
        """Функція ефективності Слончевського g(θ)."""
        return self.p.P / (1.0 + (self.p.P**2) * cos_theta)

    def compute_a_J(self, J_e: float, cos_theta: float) -> float:
        """Амплітуда інпланарного моменту Слончевського a_J (А/м)."""
        g_theta = self.slonczewski_efficiency(cos_theta)
        coeff = (HBAR * self.p.P * J_e) / (2.0 * E_CHARGE * MU_0 * self.p.Ms * self.p.thickness)
        return coeff * g_theta

    def llg_rhs(self, m: np.ndarray, J_e: float, H_ext: np.ndarray) -> np.ndarray:
        """
        Права частина явного рівняння ЛЛҐС: dm/dt = f(m).
        """
        # 1. Ефективне магнітне поле (анізотропія + зовнішнє поле)
        H_eff = np.array([0.0, 0.0, self.p.Hk_eff * m[2]]) + H_ext

        # 2. Момент Слончевського
        cos_theta = np.dot(m, self.p_vec)
        a_J = self.compute_a_J(J_e, cos_theta)

        # 3. Векторні добутки
        m_cross_H = np.cross(m, H_eff)
        m_cross_m_cross_H = np.cross(m, m_cross_H)

        m_cross_p = np.cross(m, self.p_vec)
        m_cross_m_cross_p = np.cross(m, m_cross_p)

        # 4. Доданки рівняння ЛЛҐС
        term_precession = - self.gamma_prime * m_cross_H
        term_damping = - self.p.alpha * self.gamma_prime * m_cross_m_cross_H
        term_stt_slonczewski = - self.gamma_prime * a_J * m_cross_m_cross_p
        term_stt_fieldlike = self.p.alpha * self.gamma_prime * a_J * m_cross_p

        dm_dt = term_precession + term_damping + term_stt_slonczewski + term_stt_fieldlike
        return dm_dt

    def step_rk4(self, m: np.ndarray, dt: float, J_e: float, H_ext: np.ndarray) -> np.ndarray:
        """Один крок інтегрування за схемою Рунге — Кутти 4-го порядку."""
        k1 = self.llg_rhs(m, J_e, H_ext)
        k2 = self.llg_rhs(m + 0.5 * dt * k1, J_e, H_ext)
        k3 = self.llg_rhs(m + 0.5 * dt * k2, J_e, H_ext)
        k4 = self.llg_rhs(m + dt * k3, J_e, H_ext)

        m_next = m + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        # Нормування вектора до 1.0
        return m_next / np.linalg.norm(m_next)


def run_simulation(
    current_ratio: float = 1.5,
    t_max_ns: float = 5.0,
    dt_ps: float = 0.1
) -> Dict[str, np.ndarray]:
    """
    Запуск симуляції перемикання.
    current_ratio: відношення робочого струму до критичного I / I_c0.
    """
    cell = STTCellParameters()
    solver = LLGSSolver(cell)

    I_c0 = cell.critical_current_i0
    I_write = current_ratio * I_c0
    J_write = I_write / cell.area

    # Часова сітка
    dt = dt_ps * 1e-12
    n_steps = int((t_max_ns * 1e-9) / dt)
    t_array = np.linspace(0, t_max_ns, n_steps)

    # Початковий стан: зсув на 3 градуси від легкої осі
    theta_0 = np.radians(3.0)
    m = np.array([np.sin(theta_0), 0.0, np.cos(theta_0)])

    # Масиви для збереження траєкторії
    m_history = np.zeros((n_steps, 3))
    r_history = np.zeros(n_steps)
    H_ext = np.zeros(3)

    for i in range(n_steps):
        m_history[i] = m
        # Розрахунок поточного опору pMTJ: R(θ) = R_P * (1 + TMR) / (1 + TMR * cos²(θ/2))
        cos_theta = m[2]
        r_history[i] = cell.R_P * (1.0 + cell.TMR) / (1.0 + cell.TMR * (0.5 * (1.0 + cos_theta)))
        m = solver.step_rk4(m, dt, J_write, H_ext)

    return {
        "t_ns": t_array,
        "m_x": m_history[:, 0],
        "m_y": m_history[:, 1],
        "m_z": m_history[:, 2],
        "R_kOhm": r_history / 1000.0,
        "I_write_uA": I_write * 1e6,
        "I_c0_uA": I_c0 * 1e6
    }
