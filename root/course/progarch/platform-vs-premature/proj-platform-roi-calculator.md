# ⚙️ Калькулятор ROI та аудит меж платформи

Припущення про необхідність побудови внутрішньої платформи розробки (англ. *Internal Developer Platform, IDP*) без попереднього об'єктивного аналізу економічних показників та когнітивного навантаження часто призводить до передчасної абстракції та марнотратства інженерних ресурсів. Ця вставка містить практичний інструмент аудиту — калькулятор оцінки ROI платформи, алгоритм визначення меж її доцільності та модуль імітаційного моделювання часової дискаунтованої вартості (англ. *Net Present Value, NPV*) інвестицій у платформу на горизонті 3 років. Скрипт розраховує точку рівноваги (англ. *break-even point*), чистий фінансовий ефект, коефіцієнт ризику передчасного тертя та дає автоматизовані архітектурні рекомендації щодо готовності організації до впровадження IDP.

## Модель даних та вхідні параметри аудиту

Інструмент оцінює поточний та перспективний стан інженерної організації на основі кількісних метрик, які збираються під час технічного аудиту:
- `num_stream_teams` — кількість автономних продуктових (stream-aligned) команд у компанії.
- `team_size` — середня кількість інженерів розробки у кожній продуктовій команді.
- `engineer_hourly_rate` — середня вартість години продуктового інженера (включаючи пряму заробітну плату, податки, ліцензії та оверхед робочого місця, $/год).
- `infra_time_ratio` — частка часу продуктових розробників, яка витрачається на рутинний інфраструктурний оверхед за відсутності платформи (значення у діапазоні 0.0…1.0).
- `platform_engineers` — кількість виділених платформних інженерів у компанії.
- `platform_hourly_rate` — вартість години платформного інженера ($/год).
- `friction_delay_ratio` — частка часу продуктових розробників, втрачена через тертя незрілої платформи (затримки у тікетах, зламані CRD, обхідні рішення).
- `platform_efficiency` — коефіцієнт усунення рутинного інфраструктурного часу платформою за умови її якісної розробки.
- `discount_rate` — ставка дисконтування для фінансового моделювання NPV (типово 0.10 або 10% річних).

## Практичні аспекти вимірювання та збору даних

Під час проведення реального інженерного аудиту в організації вимірювання зазначених параметрів має проводитися на основі об'єктивних джерел даних та інструментальних замірів:

1. **Вимірювання `infra_time_ratio`:** Аналіз розподілу робочих задач розробників у системі відстеження задач (Jira/Linear) та проведення опитувань за методологією DevEx (Developer Experience Assessment Framework). Час, витрачений на редагування маніфестів Kubernetes, Dockerfile, конфігурацій Terraform, CI-пайплайнів та розбір мережевих доступів у AWS IAM, вважається інфраструктурним оверхедом.
2. **Вимірювання `friction_delay_ratio`:** Визначення середнього часу очікування виконання тікетів у платформній команді (Lead Time of Platform Requests) та опитування інженерів щодо кількості годин, витрачених на боротьбу з помилками у внутрішніх CLI-обгортках та надупликованих маніфестах.
3. **Оцінка `platform_efficiency`:** Зріла платформа на базі асфальтованих шляхів (Golden Paths) здатна усунути до 75–85% рутинного інфраструктурного навантаження. Якщо ж розробники все одно змушені вручну редагувати конфігураційні файли або писати власні скрипти розгортання, коефіцієнт ефективності падає до 20–30%.

## Реалізація алгоритму аудиту та розрахунку NPV

Нижче наведено ідіоматичну реалізацію алгоритму двома мовами розробки — Python (для швидкого запуску, автоматизації та інтеграції в скрипти аудиту DevEx) та C++ (для інтеграції у внутрішні високопродуктивні CLI-інструменти аналітики та корпоративні дашборди організації).

:::tabs
```py
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
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <limits>
#include <sstream>

enum class PlatformStatus {
    PrematureDeficit,
    NoPlatformNeeded,
    TransitionScaffold,
    MatureProfitable
};

std::string status_to_string(PlatformStatus st) {
    switch (st) {
        case PlatformStatus::PrematureDeficit: return "PREMATURE_DEFICIT";
        case PlatformStatus::NoPlatformNeeded: return "NO_PLATFORM_NEEDED";
        case PlatformStatus::TransitionScaffold: return "TRANSITION_SCAFFOLD";
        case PlatformStatus::MatureProfitable: return "MATURE_PROFITABLE";
    }
    return "UNKNOWN";
}

struct AuditInput {
    int num_stream_teams{0};
    int team_size{0};
    double engineer_hourly_rate{0.0};
    double infra_time_ratio{0.0};
    int platform_engineers{0};
    double platform_hourly_rate{0.0};
    double friction_delay_ratio{0.02};
    double platform_efficiency{0.75};
    int annual_hours{1920};
    double discount_rate{0.10};
    double team_growth_rate_annual{0.20};
};

struct NpvProjection {
    int year;
    int num_teams;
    double gross_benefit;
    double platform_cost;
    double net_cash_flow;
    double discounted_cash_flow;
};

struct AuditReport {
    PlatformStatus status;
    double annual_base_infra_cost;
    double annual_platform_team_cost;
    double annual_net_roi;
    double break_even_teams;
    double npv_3year;
    std::vector<NpvProjection> projections;
    std::vector<std::string> recommendations;
};

class PlatformAuditor {
public:
    static AuditReport evaluate(const AuditInput& inp) {
        AuditReport rep;
        
        const int total_stream_engineers = inp.num_stream_teams * inp.team_size;
        const double base_infra_cost_per_hour = total_stream_engineers * inp.engineer_hourly_rate * inp.infra_time_ratio;
        rep.annual_base_infra_cost = base_infra_cost_per_hour * inp.annual_hours;
        
        const double platform_team_cost_per_hour = inp.platform_engineers * inp.platform_hourly_rate;
        rep.annual_platform_team_cost = platform_team_cost_per_hour * inp.annual_hours;
        
        const double eff_saved_ratio = (inp.infra_time_ratio * inp.platform_efficiency) - inp.friction_delay_ratio;
        const double single_team_hourly_savings = inp.team_size * inp.engineer_hourly_rate * eff_saved_ratio;
        
        if (single_team_hourly_savings > 0.0) {
            rep.break_even_teams = platform_team_cost_per_hour / single_team_hourly_savings;
        } else {
            rep.break_even_teams = std::numeric_limits<double>::infinity();
        }
        
        const double net_hourly_benefit = (inp.num_stream_teams * single_team_hourly_savings) - platform_team_cost_per_hour;
        rep.annual_net_roi = net_hourly_benefit * inp.annual_hours;
        
        double npv_total = 0.0;
        double current_teams = static_cast<double>(inp.num_stream_teams);
        
        for (int yr = 1; yr <= 3; ++yr) {
            int n_teams_int = static_cast<int>(std::round(current_teams));
            double gross_b = n_teams_int * single_team_hourly_savings * inp.annual_hours;
            double p_cost = rep.annual_platform_team_cost;
            
            if (n_teams_int > 8 && inp.platform_engineers > 0) {
                int extra_eng = (n_teams_int - 8) / 4;
                p_cost += extra_eng * inp.platform_hourly_rate * inp.annual_hours;
            }
            
            double net_cf = gross_b - p_cost;
            double dcf = net_cf / std::pow(1.0 + inp.discount_rate, yr);
            npv_total += dcf;
            
            rep.projections.push_back(NpvProjection{
                .year = yr,
                .num_teams = n_teams_int,
                .gross_benefit = gross_b,
                .platform_cost = p_cost,
                .net_cash_flow = net_cf,
                .discounted_cash_flow = dcf
            });
            
            current_teams *= (1.0 + inp.team_growth_rate_annual);
        }
        rep.npv_3year = npv_total;
        
        if (single_team_hourly_savings <= 0.0) {
            rep.status = PlatformStatus::PrematureDeficit;
            rep.recommendations.push_back("КРИТИЧНО: Платформа додає більше тертя, ніж заощаджує часу розробників.");
            rep.recommendations.push_back("Спростіть платформу до Thinnest Viable Platform (TVP).");
        } else if (inp.platform_engineers > 0 && inp.num_stream_teams < rep.break_even_teams) {
            rep.status = PlatformStatus::PrematureDeficit;
            rep.recommendations.push_back("ПОПЕРЕДЖЕННЯ: Витрати на платформну команду перевищують вигоди.");
            rep.recommendations.push_back("Переформатуйте команду у режим Enabling Team.");
        } else if (inp.num_stream_teams < 3 && inp.platform_engineers == 0) {
            rep.status = PlatformStatus::NoPlatformNeeded;
            rep.recommendations.push_back("Оптимальний стан: використовуйте ванільні IaC-шаблони без виділеної команди.");
        } else if (inp.num_stream_teams >= 3 && inp.num_stream_teams < 5 && inp.platform_engineers == 0) {
            rep.status = PlatformStatus::TransitionScaffold;
            rep.recommendations.push_back("Перехідна зона: рекомендовано підготувати TVP (1 інженер).");
        } else {
            rep.status = PlatformStatus::MatureProfitable;
            rep.recommendations.push_back("ОПТИМАЛЬНО: Платформа дає високий позитивний економічний ефект.");
        }
        
        return rep;
    }
};

int main() {
    AuditInput input{
        .num_stream_teams = 6,
        .team_size = 5,
        .engineer_hourly_rate = 50.0,
        .infra_time_ratio = 0.30,
        .platform_engineers = 2,
        .platform_hourly_rate = 60.0,
        .friction_delay_ratio = 0.02,
        .platform_efficiency = 0.75
    };
    
    AuditReport report = PlatformAuditor::evaluate(input);
    
    std::cout << "=== Сценарій 2 (Зрілий IDP) ===" << std::endl;
    std::cout << "Статус: " << status_to_string(report.status) << std::endl;
    std::cout << "Річний чистий ROI: $" << std::fixed << std::setprecision(2) << report.annual_net_roi << std::endl;
    std::cout << "Точка окупності: " << report.break_even_teams << " команд" << std::endl;
    std::cout << "3-річний NPV: $" << report.npv_3year << std::endl;
    for (const auto& rec : report.recommendations) {
        std::cout << "  * " << rec << std::endl;
    }
    return 0;
}
```
:::

## Детальний розбір чотирьох практичних сценаріїв використання

Для глибшого розуміння інженерної логіки прийняття рішень розглянемо чотири типові сценарії з практики архітектурного аудиту організацій різного масштабу:

### Сценарій 1: Малий стартап із передчасною платформною командою
Організація має лише 2 продуктові команди (по 4 розробники), але заснувала виділену платформну команду з 3 інженерів, які почали будувати власну систему оркестрації та розгортання на базі Kubernetes CRD. 
- **Результат розрахунку:** Штраф за тертя `friction_delay_ratio = 0.10` перевищує виграш від автоматизації `platform_efficiency = 0.30`. Скрипт виставляє статус `PREMATURE_DEFICIT` і показує від'ємний річний ROI у розмірі `-408,960.00 $/рік` та 3-річний від'ємний NPV у розмірі `-1,016,846.00 $`.
- **Архітектурне рішення:** Розформувати виділену платформну команду. Повернути розробникам прямий доступ до ванільних інструментів хмари через стандартні шаблони Terraform. Скасувати використання недосконалого внутрішнього порталу.

### Сценарій 2: Зріла середня компанія (6 продуктів, 2 платформні інженери)
Компанія масштабувалася до 6 продуктових команд і створила компактну платформну команду з 2 інженерів, яка надає готові CI/CD-пайплайни та шаблони розгортання в AWS за принципом Golden Path.
- **Результат розрахунку:** Точка окупності досягається вже при `N_{s,crit} = 2.3` команд. Скрипт видає статус `MATURE_PROFITABLE` із додатним ROI понад `+360,000.00 $/рік` та 3-річним NPV понад `+1,048,000.00 $`.
- **Архітектурне рішення:** Закріпити платформу як внутрішній продукт, призначити Platform Product Manager для вивчення потреб розробників, розпочати впровадження Backstage для візуалізації сервісного каталогу.

### Сценарій 3: Ростучий бізнес у перехідній зоні (4 команди, без платформи)
Організація має 4 продуктові команди, але не має жодного платформного інженера. Розробники починають дублювати IaC-код і скаржаться на зростання часу розгортання.
- **Результат розрахунку:** Скрипт виявляє статус `TRANSITION_SCAFFOLD`. Базові інфраструктурні витрати перевищують 500,000 $/рік.
- **Архітектурне рішення:** Створити Thinnest Viable Platform (TVP), виділивши 1 інженера для розробки спільних модулів Terraform та документації без побудови складного UI-порталу.

### Сценарій 4: Дисбаланс масштабів у корпорації (10 продуктів, 12 платформних інженерів)
Велике підприємство роздуло платформний підрозділ до 12 інженерів, які почали будувати власні мову конфігурації та систему моніторингу замість використання стандартних галузевих інструментів.
- **Результат розрахунку:** Прямі витрати на платформну команду ($1.5M/рік) перевищують економно згенеровану цінність продуктових команд, викликаючи падіння ROI до негативних значень.
- **Архітектурне рішення:** Скоротити обсяг власної розробки платформи, перейти на стандартизовані open-source рішення (Backstage, ArgoCD) та зменшити склад платформної команди до 3–4 інженерів, перевівши решту в продуктивні команди.

## Матриця діагностичних дій та рефакторингу платформи

Залежно від виявленого статусу інженерне керівництво реалізує відповідні кроки матриці оптимізації DevEx:

| Виявлений статус | Показник N_{s} проти N_{crit} | Ризик тертя | Рекомендована інфраструктурна топологія |
| :--- | :--- | :--- | :--- |
| `NO_PLATFORM_NEEDED` | N_s < 3 | Низький | Повна автономія: ванільні шаблони IaC, режим Facilitating. |
| `TRANSITION_SCAFFOLD` | 3 ≤ N_s < 5 | Середній | Thinnest Viable Platform (TVP): 1 інженер, спільні CI/IaC-модулі. |
| `MATURE_PROFITABLE` | N_s ≥ N_{crit} | Задовільний | Platform as a Product: виділений IDP, Backstage, Platform PM. |
| `PREMATURE_DEFICIT` | N_s < N_{crit} або T_{delay} високий | Критичний | Негайна декомпозиція: спрощення абстракцій, надання Off-roading. |

Інтеграція даного скрипту аудиту у щоквартальний процес оцінки інженерних метрик (Architecture Review Board) дозволяє запобігти передчасним інвестиціям та своєчасно запустити створення платформи саме тоді, коли вона принесе максимальний фінансовий та технологічний ефект.
