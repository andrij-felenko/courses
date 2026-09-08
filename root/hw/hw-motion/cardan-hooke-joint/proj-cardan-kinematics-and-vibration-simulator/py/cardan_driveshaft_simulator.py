#!/usr/bin/env python3
"""
cardan_driveshaft_simulator.py
Чисельне моделювання кінематики карданної передачі (Z- та W-схеми, довільні кути
зламу та фазове розведення вилок), розрахунок кутових прискорень, динамічних крутних
моментів та швидке перетворення Фур'є (FFT) для гармонійного спектрального аналізу.
"""

import math
import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


@dataclass
class SimulationResult:
    """Результати моделювання руху карданного валопроводу."""
    time: List[float]
    phi_in: List[float]
    omega_in: List[float]
    phi_out: List[float]
    omega_out: List[float]
    alpha_out: List[float]
    torque_dyn: List[float]


class CardanDriveshaftSimulator:
    """
    Симулятор кінематики та динаміки карданних передач.
    Підтримує одиночні шарніри Гука, симетричні двозв'язні схеми (Z- та W-подібні)
    та довільні просторові перекоси з розфазуванням вилок.
    """

    def __init__(
        self,
        beta1_deg: float,
        beta2_deg: float = 0.0,
        gamma_deg: float = 0.0,
        is_double: bool = False,
        j_load: float = 0.05
    ):
        """
        Ініціалізація параметрів валопроводу.

        :param beta1_deg: Кут зламу першого шарніра Гука (градуси).
        :param beta2_deg: Кут зламу другого шарніра Гука (градуси).
        :param gamma_deg: Кут розфазування вилок проміжного вала (градуси, 0 - копланарні).
        :param is_double: Ознака двозв'язної карданної передачі (True) чи одиночного шарніра (False).
        :param j_load: Момент інерції навантаження на вихідному валу (кг·м²).
        """
        self.beta1 = math.radians(beta1_deg)
        self.beta2 = math.radians(beta2_deg)
        self.gamma = math.radians(gamma_deg)
        self.is_double = is_double
        self.j_load = j_load

    @staticmethod
    def single_joint_phi2(phi1: float, beta: float) -> float:
        """
        Аналітичний розрахунок кута повороту відомого вала одиночного шарніра Гука:
        tan(phi2) = tan(phi1) * cos(beta).
        Враховує квадранти для неперервного наростання кута.
        """
        # Чисельно стабільне обчислення через atan2
        sin_phi1 = math.sin(phi1)
        cos_phi1 = math.cos(phi1)
        cos_b = math.cos(beta)

        # Миттєвий кут у межах поточного оберту
        turns = math.floor(phi1 / (2.0 * math.pi))
        phi1_rem = phi1 - turns * 2.0 * math.pi

        # atan2(sin(phi1)*cos(beta), cos(phi1))
        phi2_rem = math.atan2(math.sin(phi1_rem) * cos_b, math.cos(phi1_rem))
        if phi2_rem < 0:
            phi2_rem += 2.0 * math.pi

        return turns * 2.0 * math.pi + phi2_rem

    @staticmethod
    def single_joint_ratio(phi1: float, beta: float) -> float:
        """
        Миттєве передавальне відношення кутової швидкості одиночного шарніра:
        i(phi1) = omega2 / omega1 = cos(beta) / (1 - sin^2(beta) * sin^2(phi1)).
        """
        cos_b = math.cos(beta)
        sin_b = math.sin(beta)
        sin_phi = math.sin(phi1)
        denom = 1.0 - (sin_b * sin_phi) ** 2
        return cos_b / denom

    @staticmethod
    def single_joint_alpha2(phi1: float, omega1: float, beta: float) -> float:
        """
        Миттєве кутове прискорення відомого вала при сталій вхідній швидкості d(omega1)/dt = 0:
        alpha2 = omega1^2 * cos(beta) * sin^2(beta) * sin(2*phi1) / (1 - sin^2(beta) * sin^2(phi1))^2.
        """
        cos_b = math.cos(beta)
        sin_b = math.sin(beta)
        sin_phi = math.sin(phi1)
        denom = 1.0 - (sin_b * sin_phi) ** 2
        numerator = (omega1 ** 2) * cos_b * (sin_b ** 2) * math.sin(2.0 * phi1)
        return numerator / (denom ** 2)

    def simulate(
        self,
        omega_in_rpm: float,
        num_revs: float = 2.0,
        samples_per_rev: int = 360
    ) -> SimulationResult:
        """
        Покрокове моделювання обертання карданної передачі.

        :param omega_in_rpm: Вхідна частота обертання у об/хв.
        :param num_revs: Кількість обертів для симуляції.
        :param samples_per_rev: Кількість точок дискретизації на один оберт.
        """
        omega1 = omega_in_rpm * (2.0 * math.pi / 60.0)
        total_samples = int(num_revs * samples_per_rev)
        total_angle = num_revs * 2.0 * math.pi
        d_phi = total_angle / total_samples
        dt = d_phi / omega1

        time_list: List[float] = []
        phi_in_list: List[float] = []
        omega_in_list: List[float] = []
        phi_out_list: List[float] = []
        omega_out_list: List[float] = []
        alpha_out_list: List[float] = []
        torque_dyn_list: List[float] = []

        for i in range(total_samples):
            t = i * dt
            p1 = i * d_phi

            if not self.is_double:
                # Одиночний карданний шарнір
                p_out = self.single_joint_phi2(p1, self.beta1)
                w_out = omega1 * self.single_joint_ratio(p1, self.beta1)
                a_out = self.single_joint_alpha2(p1, omega1, self.beta1)
            else:
                # Двозв'язний валопровід (шарнір 1 -> проміжний вал -> шарнір 2)
                p2 = self.single_joint_phi2(p1, self.beta1)
                w2 = omega1 * self.single_joint_ratio(p1, self.beta1)

                # У карданному валу вилки проміжного вала копланарні (утворюють Z-схему при gamma = 0).
                # Оскільки ведена вилка шарніра 1 перпендикулярна тяговій вилці хрестовини при phi1 = 0,
                # геометричний кут входу в шарнір 2 має базовий фазовий зсув pi/2.
                # Тоді gamma = 0 відповідає копланарним вилкам (повна компенсація),
                # а gamma = 90° — помилковому складанню зі складанням пульсацій.
                p2_fork = p2 + math.pi / 2.0 + self.gamma
                p_out = self.single_joint_phi2(p2_fork, self.beta2)
                ratio2 = self.single_joint_ratio(p2_fork, self.beta2)
                w_out = w2 * ratio2

                # Чисельне диференціювання кутової швидкості для двозв'язного валопроводу
                dt_num = 1e-6
                p1_fwd = p1 + omega1 * dt_num
                p2_fwd = self.single_joint_phi2(p1_fwd, self.beta1)
                w2_fwd = omega1 * self.single_joint_ratio(p1_fwd, self.beta1)
                w_out_fwd = w2_fwd * self.single_joint_ratio(p2_fwd + math.pi / 2.0 + self.gamma, self.beta2)

                p1_bwd = p1 - omega1 * dt_num
                p2_bwd = self.single_joint_phi2(p1_bwd, self.beta1)
                w2_bwd = omega1 * self.single_joint_ratio(p1_bwd, self.beta1)
                w_out_bwd = w2_bwd * self.single_joint_ratio(p2_bwd + math.pi / 2.0 + self.gamma, self.beta2)

                a_out = (w_out_fwd - w_out_bwd) / (2.0 * dt_num)

            # Динамічний момент навантаження від прискорення інерції
            t_dyn = self.j_load * a_out

            time_list.append(t)
            phi_in_list.append(p1)
            omega_in_list.append(omega1)
            phi_out_list.append(p_out)
            omega_out_list.append(w_out)
            alpha_out_list.append(a_out)
            torque_dyn_list.append(t_dyn)

        return SimulationResult(
            time=time_list,
            phi_in=phi_in_list,
            omega_in=omega_in_list,
            phi_out=phi_out_list,
            omega_out=omega_out_list,
            alpha_out=alpha_out_list,
            torque_dyn=torque_dyn_list
        )

    @staticmethod
    def compute_fft(signal: List[float], dt: float) -> Tuple[List[float], List[float]]:
        """
        Обчислення амплітудного спектра сигналу за дискретним перетворенням Фур'є (ДПФ).
        Реалізовано без зовнішніх залежностей (Cooley-Tukey FFT для розмірів степеня 2
        або стандартне ДПФ для довільної довжини вибірки).
        """
        n = len(signal)
        # Видаляємо постійну складову (DC offset)
        mean_val = sum(signal) / n
        centered = [x - mean_val for x in signal]

        # Розрахунок амплітуд для перших n // 2 гармонік
        num_freqs = n // 2
        freqs: List[float] = []
        amplitudes: List[float] = []
        sampling_rate = 1.0 / dt

        for k in range(num_freqs):
            freq = k * sampling_rate / n
            re_part = 0.0
            im_part = 0.0
            for t_idx in range(n):
                angle = 2.0 * math.pi * k * t_idx / n
                re_part += centered[t_idx] * math.cos(angle)
                im_part -= centered[t_idx] * math.sin(angle)
            # Нормована амплітуда (помножена на 2 для одностороннього спектра)
            amp = (2.0 / n) * math.sqrt(re_part ** 2 + im_part ** 2)
            freqs.append(freq)
            amplitudes.append(amp)

        return freqs, amplitudes

    @staticmethod
    def analyze_harmonics(
        freqs: List[float],
        amplitudes: List[float],
        base_rot_freq: float,
        max_order: int = 6
    ) -> Dict[int, float]:
        """
        Виділення амплітуд гармонік кратності обертової частоти вала (1/rev, 2/rev, 4/rev ...).

        :param base_rot_freq: Базова частота обертання вала f_0 = omega / (2 * pi), Гц.
        :param max_order: Максимальний порядок гармоніки для пошуку.
        """
        orders: Dict[int, float] = {}
        for order in range(1, max_order + 1):
            target_freq = order * base_rot_freq
            # Знаходимо найближчу спектральну лінію
            best_idx = min(range(len(freqs)), key=lambda i: abs(freqs[i] - target_freq))
            orders[order] = amplitudes[best_idx]
        return orders


def main():
    print("=" * 72)
    print("ЧИСЕЛЬНЕ МОДЕЛЮВАННЯ КІНЕМАТИКИ ТА ДИНАМІКИ КАРДАННИХ ПЕРЕДАЧ")
    print("=" * 72)

    # Параметри системи
    rpm = 1500.0  # 1500 об/хв (25 Гц, кутова швидкість 157.08 рад/с)
    beta = 12.0   # Кут зламу 12 градусів
    j_load = 0.02 # Момент інерції навантаження 0.02 кг·м²
    f0 = rpm / 60.0

    print(f"Робоча частота обертання: {rpm:.1f} об/хв (базова частота f0 = {f0:.2f} Гц)")
    print(f"Кут зламу шарнірів: beta = {beta:.1f}°")
    print(f"Інерція навантаження: J_load = {j_load} кг·м²\n")

    # 1. Одиночний шарнір Гука
    sim_single = CardanDriveshaftSimulator(beta1_deg=beta, is_double=False, j_load=j_load)
    res_single = sim_single.simulate(omega_in_rpm=rpm, num_revs=2.0, samples_per_rev=180)
    dt = res_single.time[1] - res_single.time[0]
    freqs, amps_single = CardanDriveshaftSimulator.compute_fft(res_single.omega_out, dt)
    orders_single = CardanDriveshaftSimulator.analyze_harmonics(freqs, amps_single, f0)

    w_min_s = min(res_single.omega_out)
    w_max_s = max(res_single.omega_out)
    pulsation_s = (w_max_s - w_min_s) / res_single.omega_in[0] * 100.0
    t_dyn_peak_s = max(abs(t) for t in res_single.torque_dyn)

    print("1. ОДИНОЧНИЙ ШАРНІР ГУКА:")
    print(f"   Діапазон швидкості виходу: [{w_min_s:.2f} ... {w_max_s:.2f}] рад/с")
    print(f"   Коефіцієнт пульсації швидкості: delta = {pulsation_s:.2f} %")
    print(f"   Піковий знакозмінний динамічний момент: T_dyn = ±{t_dyn_peak_s:.2f} Н·м")
    print(f"   Амплітуда вібрації на 2/rev (50 Гц): {orders_single.get(2, 0.0):.3f} рад/с\n")

    # 2. Здвоєна Z-схема з компенсацією (beta1 = beta2 = 12°, gamma = 0°)
    sim_z = CardanDriveshaftSimulator(beta1_deg=beta, beta2_deg=beta, gamma_deg=0.0, is_double=True, j_load=j_load)
    res_z = sim_z.simulate(omega_in_rpm=rpm, num_revs=2.0, samples_per_rev=180)
    freqs_z, amps_z = CardanDriveshaftSimulator.compute_fft(res_z.omega_out, dt)
    orders_z = CardanDriveshaftSimulator.analyze_harmonics(freqs_z, amps_z, f0)

    w_min_z = min(res_z.omega_out)
    w_max_z = max(res_z.omega_out)
    pulsation_z = (w_max_z - w_min_z) / res_z.omega_in[0] * 100.0
    t_dyn_peak_z = max(abs(t) for t in res_z.torque_dyn)

    print("2. ЗДВОЄНА Z-СХЕМА (ПОВНА КІНЕМАТИЧНА КОМПЕНСАЦІЯ):")
    print(f"   Діапазон швидкості виходу: [{w_min_z:.2f} ... {w_max_z:.2f}] рад/с")
    print(f"   Коефіцієнт пульсації швидкості: delta = {pulsation_z:.4f} % (прагне до 0)")
    print(f"   Піковий динамічний момент: T_dyn = {t_dyn_peak_z:.4f} Н·м")
    print(f"   Амплітуда вібрації на 2/rev (50 Гц): {orders_z.get(2, 0.0):.5f} рад/с (компенсовано)\n")

    # 3. Здвоєна схема з помилкою збирання (розфазування вилок на 90°)
    sim_bad = CardanDriveshaftSimulator(beta1_deg=beta, beta2_deg=beta, gamma_deg=90.0, is_double=True, j_load=j_load)
    res_bad = sim_bad.simulate(omega_in_rpm=rpm, num_revs=2.0, samples_per_rev=180)
    freqs_bad, amps_bad = CardanDriveshaftSimulator.compute_fft(res_bad.omega_out, dt)
    orders_bad = CardanDriveshaftSimulator.analyze_harmonics(freqs_bad, amps_bad, f0)

    w_min_b = min(res_bad.omega_out)
    w_max_b = max(res_bad.omega_out)
    pulsation_b = (w_max_b - w_min_b) / res_bad.omega_in[0] * 100.0
    t_dyn_peak_b = max(abs(t) for t in res_bad.torque_dyn)

    print("3. ДВОЗВ'ЯЗНА СХЕМА З РОЗФАЗУВАННЯМ ВИЛОК НА 90° (ПОМИЛКА МОНТАЖУ):")
    print(f"   Діапазон швидкості виходу: [{w_min_b:.2f} ... {w_max_b:.2f}] рад/с")
    print(f"   Коефіцієнт пульсації швидкості: delta = {pulsation_b:.2f} % (ПОДВОЄННЯ ПУЛЬСАЦІЇ)")
    print(f"   Піковий знакозмінний момент: T_dyn = ±{t_dyn_peak_b:.2f} Н·м")
    print(f"   Амплітуда вібрації на 2/rev (50 Гц): {orders_bad.get(2, 0.0):.3f} рад/с")
    print("=" * 72)


if __name__ == "__main__":
    main()
