#!/usr/bin/env python3
"""
Аналізатор планування потужностей та запасу міцності (Headroom).
Моделює розрахунок розміру кластера, Multi-AZ стійкість та затримку черг.
"""

import math
from dataclasses import dataclass
from typing import NamedTuple


@dataclass(frozen=True)
class WorkloadProfile:
    base_rps: float          # Середній денний трафік (RPS)
    diurnal_factor: float    # Коефіцієнт вечірнього піку (наприклад, 1.5)
    burst_factor: float      # Коефіцієнт непередбачених сплесків (наприклад, 1.25)
    growth_rate_pct: float   # Очікуваний ріст на місяць у відсотках (наприклад, 10%)
    months_ahead: int        # Горизонт планування в місяцях (наприклад, 3)


@dataclass(frozen=True)
class NodeProfile:
    capacity_rps: float      # Максимальна продуктивність одного вузла (RPS)
    service_time_ms: float   # Чистий час виконання запиту на CPU (мс)
    max_safe_util: float     # Гранично допустима безпечна утилізація (наприклад, 0.70)


@dataclass(frozen=True)
class ResilienceConfig:
    availability_zones: int  # Кількість зон доступності (AZ, наприклад 3)
    extra_nodes_per_az: int  # Локальний резерв на зону (наприклад, 1 для N+1)


class CapacityPlan(NamedTuple):
    forecast_peak_rps: float
    total_nodes: int
    nodes_per_az: int
    steady_state_util: float
    steady_state_headroom: float
    disaster_util: float
    disaster_headroom: float
    steady_p99_latency_ms: float
    disaster_p99_latency_ms: float
    is_slo_safe: bool


def calculate_p99_queue_delay(service_time_ms: float, util: float) -> float:
    """Обчислює 99-й перцентиль затримки очікування в черзі за моделлю M/M/1."""
    if util >= 0.999:
        return float("inf")
    if util <= 0.001:
        return 0.0
    # t_99 = S * ln(util / (1 - 0.99)) / (1 - util)
    return service_time_ms * (math.log(util / 0.01) / (1.0 - util))


def plan_capacity(
    workload: WorkloadProfile,
    node: NodeProfile,
    resilience: ResilienceConfig,
) -> CapacityPlan:
    # 1. Прогноз пікового навантаження з урахуванням росту
    growth_multiplier = (1.0 + workload.growth_rate_pct / 100.0) ** workload.months_ahead
    peak_rps = workload.base_rps * workload.diurnal_factor * workload.burst_factor * growth_multiplier

    # 2. Розрахунок штатної потреби для Multi-AZ схеми
    # Вцілілі (M - 1) зон повинні тримати пік при утилізації <= node.max_safe_util
    m = resilience.availability_zones
    if m < 2:
        raise ValueError("Для Multi-AZ планування потрібно щонайменше 2 зони.")

    # Корисна потужність одного вузла під час аварії
    disaster_usable_node_rps = node.capacity_rps * node.max_safe_util
    # Потреба у вузлах на вцілілі (m - 1) зон
    min_working_nodes_disaster = math.ceil(peak_rps / disaster_usable_node_rps)
    # Вузлів на одну зону (без відмов)
    nodes_per_az_work = math.ceil(min_working_nodes_disaster / (m - 1))
    
    # Повний розмір зони з локальним резервом (N+k)
    nodes_per_az_total = nodes_per_az_work + resilience.extra_nodes_per_az
    total_nodes = nodes_per_az_total * m

    # 3. Аналіз штатного стану (Normal State)
    total_cluster_capacity_rps = total_nodes * node.capacity_rps
    steady_util = peak_rps / total_cluster_capacity_rps
    steady_headroom = 1.0 - steady_util

    # 4. Аналіз катастрофічного стану (1 AZ Outage)
    surviving_nodes = nodes_per_az_total * (m - 1)
    disaster_capacity_rps = surviving_nodes * node.capacity_rps
    disaster_util = peak_rps / disaster_capacity_rps
    disaster_headroom = 1.0 - disaster_util

    # 5. Розрахунок затримок черг
    steady_p99 = calculate_p99_queue_delay(node.service_time_ms, steady_util)
    disaster_p99 = calculate_p99_queue_delay(node.service_time_ms, disaster_util)

    # Критерій безпеки: утилізація при аварії не перевищує ліміт
    is_safe = disaster_util <= node.max_safe_util

    return CapacityPlan(
        forecast_peak_rps=peak_rps,
        total_nodes=total_nodes,
        nodes_per_az=nodes_per_az_total,
        steady_state_util=steady_util,
        steady_state_headroom=steady_headroom,
        disaster_util=disaster_util,
        disaster_headroom=disaster_headroom,
        steady_p99_latency_ms=steady_p99,
        disaster_p99_latency_ms=disaster_p99,
        is_slo_safe=is_safe,
    )


def print_report(plan: CapacityPlan) -> None:
    print("=" * 68)
    print("           ЗВІТ ПЛАНУВАННЯ ПОТУЖНОСТЕЙ ТА HEADROOM")
    print("=" * 68)
    print(f"Прогнозований піковий трафік : {plan.forecast_peak_rps:,.1f} RPS")
    print(f"Загальна кількість вузлів     : {plan.total_nodes} (по {plan.nodes_per_az} у кожній з зон)")
    print("-" * 68)
    print("ШТАТНИЙ РЕЖИМ (УСІ ЗОНИ ПРАЦЮЮТЬ):")
    print(f"  • Утилізація кластера       : {plan.steady_state_util * 100.0:.1f}%")
    print(f"  • Запас міцності (Headroom) : {plan.steady_state_headroom * 100.0:.1f}%")
    print(f"  • Оцінка p99 затримки черги : {plan.steady_p99_latency_ms:.2f} мс")
    print("-" * 68)
    print("СТРЕС-СЦЕНАРІЙ (АВАРІЯ 1 ЗОНИ ДОСТУПНОСТІ):")
    print(f"  • Утилізація вцілілих зон   : {plan.disaster_util * 100.0:.1f}%")
    print(f"  • Залишковий Headroom       : {plan.disaster_headroom * 100.0:.1f}%")
    print(f"  • Оцінка p99 затримки черги : {plan.disaster_p99_latency_ms:.2f} мс")
    print("-" * 68)
    status_str = "✓ БЕЗПЕЧНО (SLO ДОТРИМАНО)" if plan.is_slo_safe else "✖ НЕБЕЗПЕКА (РИЗИК КОЛАПСУ)"
    print(f"ПІДСУМКОВИЙ СТАТУС НАДІЙНОСТІ : {status_str}")
    print("=" * 68)


if __name__ == "__main__":
    workload = WorkloadProfile(
        base_rps=5000.0,
        diurnal_factor=1.6,
        burst_factor=1.2,
        growth_rate_pct=8.0,
        months_ahead=3,
    )
    node = NodeProfile(
        capacity_rps=350.0,
        service_time_ms=2.8,
        max_safe_util=0.75,
    )
    resilience = ResilienceConfig(
        availability_zones=3,
        extra_nodes_per_az=1,
    )

    plan = plan_capacity(workload, node, resilience)
    print_report(plan)
