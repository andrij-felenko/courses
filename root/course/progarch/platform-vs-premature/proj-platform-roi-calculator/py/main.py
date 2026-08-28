from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any
import math
import json

class PlatformStatus(Enum):
    PREMATURE_DEFICIT = auto()   # Передчасна платформа: чисті збитки та оверхед
    NO_PLATFORM_NEEDED = auto()  # Занадто малий масштаб для виділеної команди
    TRANSITION_SCAFFOLD = auto() # Зона переходу: потрібні шаблони (TVP) без виділеної команди
    MATURE_PROFITABLE = auto()   # Зріла платформа: високий позитивний ROI

@dataclass
class AuditInput:
    num_stream_teams: int
    team_size: int
    engineer_hourly_rate: float
    infra_time_ratio: float
    platform_engineers: int
    platform_hourly_rate: float
    friction_delay_ratio: float = 0.02
    platform_efficiency: float = 0.75
    annual_hours: int = 1920
    discount_rate: float = 0.10
    team_growth_rate_annual: float = 0.20  # Очікуваний приріст команд на рік

@dataclass
class NpvProjection:
    year: int
    num_teams: int
    gross_benefit: float
    platform_cost: float
    net_cash_flow: float
    discounted_cash_flow: float

@dataclass
class AuditReport:
    status: PlatformStatus
    annual_base_infra_cost: float
    annual_platform_team_cost: float
    annual_net_roi: float
    break_even_teams: float
    npv_3year: float
    projections: List[NpvProjection]
    recommendations: List[str]

    def to_json(self) -> str:
        return json.dumps({
            "status": self.status.name,
            "annual_base_infra_cost": round(self.annual_base_infra_cost, 2),
            "annual_platform_team_cost": round(self.annual_platform_team_cost, 2),
            "annual_net_roi": round(self.annual_net_roi, 2),
            "break_even_teams": round(self.break_even_teams, 2) if not math.isinf(self.break_even_teams) else -1,
            "npv_3year": round(self.npv_3year, 2),
            "projections": [
                {
                    "year": p.year,
                    "num_teams": p.num_teams,
                    "gross_benefit": round(p.gross_benefit, 2),
                    "platform_cost": round(p.platform_cost, 2),
                    "net_cash_flow": round(p.net_cash_flow, 2),
                    "discounted_cash_flow": round(p.discounted_cash_flow, 2)
                } for p in self.projections
            ],
            "recommendations": self.recommendations
        }, indent=2, ensure_ascii=False)

def audit_platform_readiness(inp: AuditInput) -> AuditReport:
    # 1. Обчислення базових інфраструктурних витрат без платформи
    total_stream_engineers = inp.num_stream_teams * inp.team_size
    base_infra_cost_per_hour = total_stream_engineers * inp.engineer_hourly_rate * inp.infra_time_ratio
    annual_base_infra_cost = base_infra_cost_per_hour * inp.annual_hours

    # 2. Обчислення витрат на платформну команду
    platform_team_cost_per_hour = inp.platform_engineers * inp.platform_hourly_rate
    annual_platform_team_cost = platform_team_cost_per_hour * inp.annual_hours

    # 3. Обчислення залишкових витрат та чистих вигод
    eff_saved_ratio = (inp.infra_time_ratio * inp.platform_efficiency) - inp.friction_delay_ratio
    single_team_hourly_savings = (
        inp.team_size * inp.engineer_hourly_rate * eff_saved_ratio
    )

    # 4. Обчислення точки рівноваги (break-even point)
    if single_team_hourly_savings > 0:
        break_even_teams = platform_team_cost_per_hour / single_team_hourly_savings
    else:
        break_even_teams = float('inf')

    # 5. Чистий річний фінансовий ефект (ROI)
    net_hourly_benefit = (inp.num_stream_teams * single_team_hourly_savings) - platform_team_cost_per_hour
    annual_net_roi = net_hourly_benefit * inp.annual_hours

    # 6. Трьохрічне проектування грошових потоків та розрахунок NPV
    projections: List[NpvProjection] = []
    npv_total = 0.0
    
    current_teams = float(inp.num_stream_teams)
    for yr in range(1, 4):
        n_teams_int = int(round(current_teams))
        gross_b = n_teams_int * single_team_hourly_savings * inp.annual_hours
        p_cost = annual_platform_team_cost
        
        # Додаємо невелике зростання витрат платформи при зростанні команд
        if n_teams_int > 8 and inp.platform_engineers > 0:
            extra_eng = (n_teams_int - 8) // 4
            p_cost += extra_eng * inp.platform_hourly_rate * inp.annual_hours

        net_cf = gross_b - p_cost
        dcf = net_cf / math.pow(1.0 + inp.discount_rate, yr)
        npv_total += dcf

        projections.append(NpvProjection(
            year=yr,
            num_teams=n_teams_int,
            gross_benefit=gross_b,
            platform_cost=p_cost,
            net_cash_flow=net_cf,
            discounted_cash_flow=dcf
        ))
        current_teams *= (1.0 + inp.team_growth_rate_annual)

    # 7. Класифікація стану та формування розширених рекомендацій
    recs: List[str] = []
    
    if single_team_hourly_savings <= 0:
        status = PlatformStatus.PREMATURE_DEFICIT
        recs.append("КРИТИЧНО: Платформа додає більше тертя, ніж заощаджує часу розробників.")
        recs.append("Спростіть платформу до Thinnest Viable Platform (TVP): приберіть складні CRD та обов'язкові обгортки.")
        recs.append("Надайте розробникам прямий доступ до ванільних модулів Terraform у режимі Off-roading.")
    elif inp.platform_engineers > 0 and inp.num_stream_teams < break_even_teams:
        status = PlatformStatus.PREMATURE_DEFICIT
        recs.append(f"ПОПЕРЕДЖЕННЯ: Витрати на платформну команду перевищують вигоди при N_s={inp.num_stream_teams}.")
        recs.append(f"Точка окупності досягається при N_s >= {break_even_teams:.1f} команд.")
        recs.append("Переформатуйте платформну команду у режим Enabling Team з частковою участю.")
        recs.append("Скасуйте обов'язкове використання внутрішнього порталу розробників до досягнення потрібного масштабу.")
    elif inp.num_stream_teams < 3 and inp.platform_engineers == 0:
        status = PlatformStatus.NO_PLATFORM_NEEDED
        recs.append("Оптимальний стан: використовуйте ванільні IaC-шаблони та стандартизовані CI-пайплайни.")
        recs.append("Не створюйте виділену платформну команду на даному етапі життя організації.")
        recs.append("Вирішуйте складні інфраструктурні задачі через залучення експертів у режимі Facilitating.")
    elif inp.num_stream_teams >= 3 and inp.num_stream_teams < 5 and inp.platform_engineers == 0:
        status = PlatformStatus.TRANSITION_SCAFFOLD
        recs.append("Перехідна зона: високий інфраструктурний оверхед розробників починає обмежувати релізи.")
        recs.append("Рекомендовано створити TVP (1 виділений інженер або ротаційна роль для розробки shared IaC).")
        recs.append("Зосередьтеся виключно на шаблонізації CI/CD та наданні готовності для баз даних.")
    else:
        status = PlatformStatus.MATURE_PROFITABLE
        recs.append("ОПТИМАЛЬНО: Платформа дає високий позитивний економічний ефект.")
        recs.append("Розвивайте платформу як внутрішній продукт: впроваджуйте Platform Product Manager та DevEx-метрики.")
        recs.append("Створіть автоматизований портал розробника (Backstage/Crossplane) для прискорення онбордингу.")

    return AuditReport(
        status=status,
        annual_base_infra_cost=annual_base_infra_cost,
        annual_platform_team_cost=annual_platform_team_cost,
        annual_net_roi=annual_net_roi,
        break_even_teams=break_even_teams,
        npv_3year=npv_total,
        projections=projections,
        recommendations=recs
    )

if __name__ == "__main__":
    # Приклад аудиту для передчасної платформи (Сценарій 1)
    premature_scenario = AuditInput(
        num_stream_teams=2,
        team_size=4,
        engineer_hourly_rate=50.0,
        infra_time_ratio=0.30,
        platform_engineers=3,
        platform_hourly_rate=65.0,
        friction_delay_ratio=0.10,
        platform_efficiency=0.30
    )
    rep1 = audit_platform_readiness(premature_scenario)
    print(f"=== Сценарій 1: Статус={rep1.status.name} ===")
    print(f"Чистий ROI: {rep1.annual_net_roi:,.2f} $/рік | Точка окупності: {rep1.break_even_teams:.1f} команд | 3y NPV: {rep1.npv_3year:,.2f} $")
    print(rep1.to_json())
