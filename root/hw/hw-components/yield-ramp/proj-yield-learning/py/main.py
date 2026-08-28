#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
semiconductor_yield_tool.py — Модуль моделювання дефектів, діагностики бітових карт SRAM
та оцінки швидкості дозрівання напівпровідникового техпроцесу.
"""

import math
import random
from typing import List, Tuple, Dict, Set, Any


class PhysicalDefect:
    """Опис фізичного дефекту на поверхні кремнієвої пластини."""
    def __init__(self, x_mm: float, y_mm: float, size_nm: float, origin: str = "particle"):
        self.x = x_mm
        self.y = y_mm
        self.size = size_nm
        self.origin = origin


class WaferDefectSimulator:
    """Генератор просторових карт дефектів пластини з регульованою кластеризацією."""
    def __init__(self, diameter_mm: float = 300.0, edge_exclusion_mm: float = 3.0):
        self.diameter = diameter_mm
        self.radius = diameter_mm / 2.0
        self.active_radius = self.radius - edge_exclusion_mm
        self.area_cm2 = math.pi * (self.active_radius / 10.0) ** 2

    def generate_wafer_defects(
        self,
        base_density_cm2: float,
        cluster_factor_alpha: float = 1.2,
        radial_coeff: float = 3.0,
        radial_power: int = 6
    ) -> List[PhysicalDefect]:
        """
        Генерує масив дефектів із поєднанням випадкового фону,
        радіального градієнта та просторових кластерів.
        """
        defects: List[PhysicalDefect] = []
        target_defect_count = int(base_density_cm2 * self.area_cm2)
        if target_defect_count <= 0:
            return defects

        # Частка дефектів у гніздах обернено пропорційна параметру кластеризації alpha
        cluster_ratio = 1.0 / (1.0 + cluster_factor_alpha)
        num_clustered = int(target_defect_count * cluster_ratio)
        num_random = target_defect_count - num_clustered

        # 1. Генерація фонових дефектів із радіальним крайовим ефектом
        while len(defects) < num_random:
            r = self.active_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            norm_r = r / self.active_radius

            # Ймовірність прийняття за степеневим крайовим градієнтом
            p_radial = 1.0 + radial_coeff * (norm_r ** radial_power)
            p_acceptance = p_radial / (1.0 + radial_coeff)

            if random.random() <= p_acceptance:
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                # Розмір дефекту за законом f(x) ~ 1/x^3
                size_nm = 15.0 / math.sqrt(random.uniform(0.01, 1.0))
                defects.append(PhysicalDefect(x, y, size_nm, "random_background"))

        # 2. Генерація кластерних гнізд
        num_clusters = max(1, int(num_clustered / 15))
        for _ in range(num_clusters):
            r_center = self.active_radius * math.sqrt(random.random()) * 0.88
            th_center = random.uniform(0, 2 * math.pi)
            cx = r_center * math.cos(th_center)
            cy = r_center * math.sin(th_center)
            cluster_spread_mm = random.uniform(4.0, 18.0)

            points_in_this_cluster = int(num_clustered / num_clusters)
            for _ in range(points_in_this_cluster):
                dr = random.gauss(0, cluster_spread_mm / 2.5)
                dth = random.uniform(0, 2 * math.pi)
                px = cx + dr * math.cos(dth)
                py = cy + dr * math.sin(dth)

                # Перевірка перебування точки в межах активної зони
                if px * px + py * py <= self.active_radius * self.active_radius:
                    size_nm = random.uniform(25.0, 300.0)
                    defects.append(PhysicalDefect(px, py, size_nm, "cluster_agglomerate"))

        return defects


class SRAMBitmapAnalyzer:
    """Локалізатор відмов та класифікатор топологічних сигнатур SRAM."""
    def __init__(self, rows: int = 2048, cols: int = 2048, cell_pitch_um: float = 0.35):
        self.rows = rows
        self.cols = cols
        self.pitch_um = cell_pitch_um
        self.die_width_mm = (cols * cell_pitch_um) / 1000.0
        self.die_height_mm = (rows * cell_pitch_um) / 1000.0
        self.die_area_cm2 = (self.die_width_mm / 10.0) * (self.die_height_mm / 10.0)

    def analyze_die(self, die_defects: List[PhysicalDefect]) -> Dict[str, Any]:
        """
        Проектує фізичні координати на дискретну матрицю комірок пам'яті
        і виявляє сигнатури відмов.
        """
        failed_cells: Set[Tuple[int, int]] = set()

        for d in die_defects:
            if 0.0 <= d.x <= self.die_width_mm and 0.0 <= d.y <= self.die_height_mm:
                col = int((d.x / self.die_width_mm) * self.cols)
                row = int((d.y / self.die_height_mm) * self.rows)
                col = max(0, min(self.cols - 1, col))
                row = max(0, min(self.rows - 1, row))

                # Врахування радіуса фізичного пошкодження
                impact_radius_cells = max(1, int((d.size / 1000.0) / self.pitch_um))
                for dr in range(-impact_radius_cells, impact_radius_cells + 1):
                    for dc in range(-impact_radius_cells, impact_radius_cells + 1):
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if dr * dr + dc * dc <= impact_radius_cells * impact_radius_cells:
                                failed_cells.add((nr, nc))

        # Аналіз просторового розподілу відмов за рядками та стовпчиками
        row_hist: Dict[int, int] = {}
        col_hist: Dict[int, int] = {}
        for r, c in failed_cells:
            row_hist[r] = row_hist.get(r, 0) + 1
            col_hist[c] = col_hist.get(c, 0) + 1

        results = {
            "single_bit_fails": 0,
            "row_wordline_fails": 0,
            "col_bitline_fails": 0,
            "cluster_area_fails": 0,
            "total_bad_bits": len(failed_cells),
            "is_functional": len(failed_cells) == 0
        }

        # Сигнатура обриву/замикання Wordline (понад 60% бітів рядка пошкоджено)
        row_thresh = int(self.cols * 0.6)
        for r, count in row_hist.items():
            if count >= row_thresh:
                results["row_wordline_fails"] += 1

        # Сигнатура обриву/замикання Bitline (понад 60% бітів стовпчика пошкоджено)
        col_thresh = int(self.rows * 0.6)
        for c, count in col_hist.items():
            if count >= col_thresh:
                results["col_bitline_fails"] += 1

        if len(failed_cells) > 80 and results["row_wordline_fails"] == 0 and results["col_bitline_fails"] == 0:
            results["cluster_area_fails"] += 1
        elif 0 < len(failed_cells) <= 15:
            results["single_bit_fails"] += len(failed_cells)

        return results


class YieldLearningFitter:
    """Математичний блок підбору параметрів нарощування виходу."""
    @staticmethod
    def stapper_yield(density_d: float, area_a: float, alpha: float) -> float:
        """Обчислення виходу за формулою від'ємного біноміального розподілу Стаппера."""
        arg = (density_d * area_a) / alpha
        return (1.0 + arg) ** (-alpha)

    @staticmethod
    def fit_curve(
        time_points: List[float],
        defect_data: List[float]
    ) -> Tuple[float, float, float]:
        """
        Нелінійна апроксимація кривої D(t) = D_inf + (D_0 - D_inf) * exp(-k * t).
        Повертає кортеж: (D_0, D_inf, k).
        """
        d0_init = max(defect_data)
        dinf_init = min(defect_data) * 0.75
        best_k = 0.1
        best_sse = float('inf')

        # Оптимізація коефіцієнта навчання методом сіткового пошуку
        for k_cand in [i * 0.005 for i in range(2, 400)]:
            sse = 0.0
            for t, d_obs in zip(time_points, defect_data):
                d_model = dinf_init + (d0_init - dinf_init) * math.exp(-k_cand * t)
                sse += (d_obs - d_model) ** 2
            if sse < best_sse:
                best_sse = sse
                best_k = k_cand

        return d0_init, dinf_init, best_k


def execute_pipeline_demo():
    print("=" * 80)
    print("НАПІВПРОВІДНИКОВИЙ АНАЛІТИЧНИЙ КОМПЛЕКС: ДІАГНОСТИКА YIELD RAMP")
    print("=" * 80)

    # Етап 1: Симуляція кремнієвої пластини діаметром 300 мм
    wafer_sim = WaferDefectSimulator(diameter_mm=300.0, edge_exclusion_mm=3.0)
    current_density = 0.38  # дефектів на см²
    alpha_param = 1.15      # коефіцієнт кластеризації Стаппера

    all_defects = wafer_sim.generate_wafer_defects(
        base_density_cm2=current_density,
        cluster_factor_alpha=alpha_param,
        radial_coeff=2.8,
        radial_power=6
    )

    print(f"\n[1] Параметри симуляції пластини:")
    print(f"    Діаметр підкладки:       {wafer_sim.diameter:.0f} мм")
    print(f"    Корисна площа:           {wafer_sim.area_cm2:.1f} см²")
    print(f"    Цільова густина дефектів:{current_density:.2f} деф./см²")
    print(f"    Згенеровано дефектів:    {len(all_defects)} часток")

    # Етап 2: Аналіз бітової карти тестового чипа пам'яті SRAM
    sram_analyzer = SRAMBitmapAnalyzer(rows=2048, cols=2048, cell_pitch_um=0.32)
    print(f"\n[2] Параметри тестового масиву SRAM (Yield Vehicle):")
    print(f"    Конфігурація матриці:    {sram_analyzer.rows} × {sram_analyzer.cols} (4.19 Мбіт)")
    print(f"    Розміри кристала:        {sram_analyzer.die_width_mm:.2f} × {sram_analyzer.die_height_mm:.2f} мм")
    print(f"    Геометрична площа:       {sram_analyzer.die_area_cm2:.4f} см²")

    # Симулюємо тестовий набір дефектів на одиничному кристалі
    synthetic_die_defects = [
        PhysicalDefect(0.15, 0.20, size_nm=28.0, origin="gate_pinhole"),
        PhysicalDefect(0.42, 0.35, size_nm=180.0, origin="slurry_flake"),
    ]
    classification = sram_analyzer.analyze_die(synthetic_die_defects)

    print(f"\n[3] Результати класифікації топологічних сигнатур відмов:")
    print(f"    Загальна кількість битих бітів:  {classification['total_bad_bits']}")
    print(f"    Точкові дефекти (Single Bit):    {classification['single_bit_fails']}")
    print(f"    Обриви/замикання Wordline (Row): {classification['row_wordline_fails']}")
    print(f"    Обриви/замикання Bitline (Col):  {classification['col_bitline_fails']}")
    print(f"    Площинні плями (Cluster Fail):   {classification['cluster_area_fails']}")
    print(f"    Вердикт придатності кристала:    {'ПРИДАТНИЙ' if classification['is_functional'] else 'БРАК'}")

    # Етап 3: Моделювання річної динаміки нарощування виходу (12 місяців)
    prod_months = [1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 11.0, 12.0]
    historical_defect_densities = [1.45, 1.05, 0.72, 0.42, 0.26, 0.17, 0.12, 0.09]

    d0_fit, dinf_fit, k_rate = YieldLearningFitter.fit_curve(prod_months, historical_defect_densities)

    print(f"\n[4] Апроксимація кривої навчання техпроцесу (Gruber-Leachman Model):")
    print(f"    Початковий рівень дефектності D_0: {d0_fit:.3f} деф./см²")
    print(f"    Асимптотична межа процесу D_inf:   {dinf_fit:.3f} деф./см²")
    print(f"    Коефіцієнт темпу навчання k:       {k_rate:.3f} міс⁻¹")

    # Розрахунок проекції виходу для чипів площею 0.4 см², 1.5 см² та 5.5 см²
    print("\n[5] Проекція виходу придатних за моделлю Стаппера (α = 1.25):")
    print("Місяць | Густина D (см⁻²) | Чип 40 мм² (IoT) | Чип 150 мм² (SoC) | Чип 550 мм² (AI/GPU)")
    print("-" * 80)
    for m, d_val in zip(prod_months, historical_defect_densities):
        y_iot = YieldLearningFitter.stapper_yield(d_val, 0.40, 1.25) * 100.0
        y_soc = YieldLearningFitter.stapper_yield(d_val, 1.50, 1.25) * 100.0
        y_gpu = YieldLearningFitter.stapper_yield(d_val, 5.50, 1.25) * 100.0
        print(f"  {m:4.1f} |     {d_val:6.3f}     |      {y_iot:5.1f}%     |      {y_soc:5.1f}%      |       {y_gpu:5.1f}%")

    print("=" * 80)
    print("Розрахунок завершено.")


if __name__ == "__main__":
    random.seed(12345)
    execute_pipeline_demo()
