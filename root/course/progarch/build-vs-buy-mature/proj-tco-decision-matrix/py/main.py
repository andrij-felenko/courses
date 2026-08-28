# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TCOOption:
    name: str
    initial_cost: float           # Початкові витрати R&D / інтеграції ($)
    quarterly_base_infra: float   # Базова хмара / залізо на квартал ($)
    sre_fte_count: float          # Кількість інженерів для Day-2 підтримки
    sre_quarterly_salary: float   # Повна вартість 1 SRE на квартал ($)
    saas_cost_per_unit: float     # Ціна SaaS за одиницю на квартал ($)
    vendor_annual_growth: float   # Щорічна інфляція вендора (0.15 = 15%)
    egress_cost_per_gb: float     # Вартість трафіку ($/GB)

def simulate_3year_tco(
    option: TCOOption,
    quarterly_units: List[int],
    quarterly_egress_gb: List[float],
    annual_discount_rate: float = 0.08
) -> Tuple[float, List[float]]:
    """Розраховує сукупний дисконтований TCO (NPV) та повертає квартальну деталізацію."""
    if len(quarterly_units) != 12 or len(quarterly_egress_gb) != 12:
        raise ValueError("Симуляція вимагає даних рівно за 12 кварталів.")

    quarterly_r = (1.0 + annual_discount_rate) ** 0.25 - 1.0
    total_npv = option.initial_cost
    quarterly_costs: List[float] = []

    for q in range(12):
        year = q // 4
        units = quarterly_units[q]
        egress = quarterly_egress_gb[q]

        # Вартість підписки з урахуванням щорічної ескалації ціни вендором
        vendor_markup = (1.0 + option.vendor_annual_growth) ** year
        license_cost = units * option.saas_cost_per_unit * vendor_markup

        # Операційні витрати та інфраструктура
        ops_cost = option.sre_fte_count * option.sre_quarterly_salary
        infra_cost = option.quarterly_base_infra
        egress_cost = egress * option.egress_cost_per_gb

        raw_cost = license_cost + ops_cost + infra_cost + egress_cost
        discount_factor = (1.0 + quarterly_r) ** (q + 1)
        discounted_cost = raw_cost / discount_factor

        total_npv += discounted_cost
        quarterly_costs.append(discounted_cost)

    return total_npv, quarterly_costs

def find_crossover_point(
    saas_opt: TCOOption,
    self_opt: TCOOption,
    max_units: int = 200000
) -> int:
    """Знаходить точку перелому N*, де квартальні витрати SaaS перевищують Self-Hosted."""
    for units in range(1000, max_units, 1000):
        # Оцінка операційного квартального витрату на 2-му році (year=1)
        saas_q = units * saas_opt.saas_cost_per_unit * (1.0 + saas_opt.vendor_annual_growth) + \
                 (saas_opt.sre_fte_count * saas_opt.sre_quarterly_salary)
        self_q = self_opt.quarterly_base_infra + \
                 (self_opt.sre_fte_count * self_opt.sre_quarterly_salary)
        if saas_q > self_q:
            return units
    return max_units

if __name__ == "__main__":
    # Прогноз зростання навантаження на 12 кварталів
    units_forecast = [10000 + i * 8000 for i in range(12)]
    egress_forecast = [5000.0 + i * 2000.0 for i in range(12)]

    saas = TCOOption(
        name="Managed SaaS",
        initial_cost=15000.0,
        quarterly_base_infra=0.0,
        sre_fte_count=0.25,
        sre_quarterly_salary=25000.0,
        saas_cost_per_unit=1.50,
        vendor_annual_growth=0.15,
        egress_cost_per_gb=0.09
    )

    self_hosted = TCOOption(
        name="Self-Hosted Open Source",
        initial_cost=80000.0,
        quarterly_base_infra=6000.0,
        sre_fte_count=1.50,
        sre_quarterly_salary=25000.0,
        saas_cost_per_unit=0.0,
        vendor_annual_growth=0.0,
        egress_cost_per_gb=0.02
    )

    tco_saas, _ = simulate_3year_tco(saas, units_forecast, egress_forecast)
    tco_self, _ = simulate_3year_tco(self_hosted, units_forecast, egress_forecast)
    n_star = find_crossover_point(saas, self_hosted)

    print(f"3-Річний TCO SaaS: ${tco_saas:,.2f}")
    print(f"3-Річний TCO Self-Hosted: ${tco_self:,.2f}")
    print(f"Точка перелому N*: {n_star:,} одиниць")
