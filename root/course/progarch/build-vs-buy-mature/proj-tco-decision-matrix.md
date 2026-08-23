# ⚙️ Моделювання 3-річного TCO та розрахунок точки беззбитковості

Алгоритмічна модель трирічної наскрізної вартості володіння (англ. *Total Cost of Ownership*, TCO) надає архітектору строгий математичний апарат для зважування економічних наслідків вибору між орендою SaaS, власним розгортанням відкритого ПЗ (Self-Hosted) та написанням проприєтарної системи з нуля (Build In-House). На відміну від поверхневого порівняння «ціна підписки проти зарплати одного розробника», зріла математична модель враховує часову вартість грошей (англ. *Time Value of Money*), нелінійну інфляцію цін вендора, операційний накладний тягар інфраструктурної команди та витрати на мережевий трафік.

Ця вставка розкриває повне математичне виведення 3-річної моделі TCO, надає робочий алгоритм симуляції трьома мовами програмування (Python, C++ та TypeScript) і описує метод аналізу чутливості (англ. *sensitivity analysis*) для визначення стійкості архітектурного рішення до ризиків.

---

## 1. Математична структура моделі TCO

Сукупна чиста теперішня вартість (англ. *Net Present Value*, NPV) TCO розраховується як сума початкових авансових інвестицій та послідовності дисконтованих квартальних операційних витрат за 12 кварталів (3 роки):

```
TCO_total = C_initial + ∑ [ C_quarterly(t) / (1 + r_q)^t ]   (для t від 1 до 12)
```

де `C_quarterly(t)` — сума чотирьох операційних компонентів у кварталі `t`:

```
C_quarterly(t) = C_license(t) + C_infra(t) + C_ops(t) + C_egress(t)
```

### Деталізація складових формули

1. **Початкові капітальні витрати (`C_initial`):**
   Сума одноразових витрат на старті проєкту. Для власної розробки (Build) вона включає зарплатний фонд команди на період R&D, витрати на проектування архітектури, створення POC та написання автотестів. Для SaaS чи Self-Hosted вона охоплює витрати на налаштування інтеграційного шва (Port-Adapter), інтеграцію з корпоративною системою ідентичності та аудит безпеки.
2. **Плата за підписку та ліцензії (`C_license(t)`):**
   Поточні витрати на використання комерційного ПЗ або SaaS. Ураховує щорічне інфляційне підняття цін вендором на коефіцієнт `g_vendor` (наприклад, `g_vendor = 0.15` для 15% річного зростання):
   ```
   C_license(t) = N_units(t) × Price_per_unit × (1 + g_vendor)^(floor((t-1)/4))
   ```
3. **Витрати на обчислювальну інфраструктуру (`C_infra(t)`):**
   Прямі витрати на хмарні екземпляри (vCPU, RAM), дисковий простір (SSD/NVMe), резервовані бази даних чи оренду фізичних серверів у дата-центрі (Bare-metal).
4. **Витрати на операційний супровід та команду (`C_ops(t)`):**
   Реальна вартість інженерного часу, необхідного для підтримки системи у продакшні. Обчислюється як частка залученості інженерів з урахуванням повних витрат на співробітника (англ. *Fully Loaded Cost* — зарплата, податки, обладнання, ліцензії):
   ```
   C_ops(t) = FTE_count × Quarterly_Fully_Loaded_Salary
   ```
5. **Витрати на вихідний мережевий трафік (`C_egress(t)`):**
   Витрати на передачу даних між хмарою застосунку та зовнішнім SaaS або між зонами доступності (Cross-AZ):
   ```
   C_egress(t) = Volume_GB(t) × Price_per_GB
   ```
6. **Квартальна ставка дисконтування (`r_q`):**
   Приводиться від річної ставки дисконтування `r_annual` (ціни капіталу компанії, зазвичай 8–12%):
   ```
   r_q = (1 + r_annual)^(1/4) - 1
   ```

Дисконтування є критичним фактором: воно карає рішення власної розробки (Build), оскільки ті вимагають великих витрат `C_initial` на початку (у теперішніх, найдорожчих грошах), тоді як SaaS платить малими частками протягом усього періоду.

---

## 2. Структура операційного навантаження Day-2 (`C_ops`)

Для об'єктивного розрахунку `C_ops` важливо враховувати розбивку робочого часу інфраструктурної команди (SRE / DevOps) при утриманні Self-Hosted рішення проти Managed SaaS.

Трудомісткість супроводу Self-Hosted кластера описується чотирма категоріями завдань:
- **Плановий супровід та оновлення (30% часу):** установлення патчів безпеки OS, оновлення версій Kubernetes / Helm-чартів, ротація TLS-сертифікатів, тестування сумісності нових релізів.
- **Моніторинг та оптимізація продуктивності (25% часу):** аналіз метрик Prometheus, оптимізація розмірів індексів баз даних, регулювання конфігурацій GC / RAM, настройка правил алертінгу.
- **Реагування на інциденти та чергування (25% часу):** нічні виклики PagerDuty, усунення наслідків збоїв дисків, ребалансування розділів, розслідування причин аварій (RCA / Post-mortem).
- **Регулярне тестування катастрофічного відновлення (20% часу):** розгортання резервних копій, перевірка сценаріїв failover між регіонами, проведення хаос-тестування (Chaos Engineering).

```
Оцінка FTE залежно від класу виконання:
- Managed SaaS:      0.1 - 0.25 FTE (лише нагляд за API-ключами та моніторинг квот)
- Self-Hosted OS:    1.0 - 2.50 FTE (повноцінний супровід кластера й чергування 24/7)
- In-House Build:    2.0 - 4.00 FTE (супровід плюс постійне виправлення багів у власній базі коду)
```

Спроба оцінити Self-Hosted рішення як «безкоштовне, бо код відкритий» систематично ігнорує той факт, що 1.5 FTE досвідченого SRE-інженера коштує компанії $150,000–$250,000 на рік у сукупних витратах.

---

## 3. Імплементація алгоритму симуляції TCO

Ніжче наведено ідентичні, ідіоматичні реалізації симулятора трирічного TCO та розрахунку точки перелому ($N^*$) трьома мовами програмування.

:::tabs
```py
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
```

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <string_view>
#include <numeric>
#include <iomanip>

struct TCOOption {
    std::string_view name;
    double initial_cost;
    double quarterly_base_infra;
    double sre_fte_count;
    double sre_quarterly_salary;
    double saas_cost_per_unit;
    double vendor_annual_growth;
    double egress_cost_per_gb;
};

struct TCOResult {
    double total_npv;
    std::vector<double> quarterly_discounted;
};

TCOResult calculate_3year_tco(
    const TCOOption& opt,
    const std::vector<int>& quarterly_units,
    const std::vector<double>& quarterly_egress_gb,
    double annual_discount_rate = 0.08)
{
    double quarterly_r = std::pow(1.0 + annual_discount_rate, 0.25) - 1.0;
    double total_npv = opt.initial_cost;
    std::vector<double> q_costs(12, 0.0);

    for (size_t q = 0; q < 12; ++q) {
        size_t year = q / 4;
        double units = static_cast<double>(quarterly_units[q]);
        double egress = quarterly_egress_gb[q];

        double vendor_markup = std::pow(1.0 + opt.vendor_annual_growth, static_cast<double>(year));
        double license_cost = units * opt.saas_cost_per_unit * vendor_markup;
        double ops_cost = opt.sre_fte_count * opt.sre_quarterly_salary;
        double egress_cost = egress * opt.egress_cost_per_gb;

        double raw_cost = license_cost + ops_cost + opt.quarterly_base_infra + egress_cost;
        double discount_factor = std::pow(1.0 + quarterly_r, static_cast<double>(q + 1));
        double discounted = raw_cost / discount_factor;

        total_npv += discounted;
        q_costs[q] = discounted;
    }

    return {total_npv, std::move(q_costs)};
}

int find_crossover_units(const TCOOption& saas, const TCOOption& self_h) {
    for (int units = 1000; units < 200000; units += 1000) {
        double saas_q = units * saas.saas_cost_per_unit * (1.0 + saas.vendor_annual_growth) +
                        (saas.sre_fte_count * saas.sre_quarterly_salary);
        double self_q = self_h.quarterly_base_infra +
                        (self_h.sre_fte_count * self_h.sre_quarterly_salary);
        if (saas_q > self_q) {
            return units;
        }
    }
    return 200000;
}

int main() {
    std::vector<int> units(12);
    std::vector<double> egress(12);
    for (int i = 0; i < 12; ++i) {
        units[i] = 10000 + i * 8000;
        egress[i] = 5000.0 + i * 2000.0;
    }

    TCOOption saas{"Managed SaaS", 15000.0, 0.0, 0.25, 25000.0, 1.50, 0.15, 0.09};
    TCOOption self_hosted{"Self-Hosted OS", 80000.0, 6000.0, 1.50, 25000.0, 0.0, 0.0, 0.02};

    auto res_saas = calculate_3year_tco(saas, units, egress);
    auto res_self = calculate_3year_tco(self_hosted, units, egress);
    int n_star = find_crossover_units(saas, self_hosted);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "3-Year TCO SaaS: $" << res_saas.total_npv << "\n";
    std::cout << "3-Year TCO Self-Hosted: $" << res_self.total_npv << "\n";
    std::cout << "Crossover N*: " << n_star << " units\n";
    return 0;
}
```

```ts
interface TCOInputOption {
  name: string;
  initialCost: number;
  quarterlyBaseInfra: number;
  sreFteCount: number;
  sreQuarterlySalary: number;
  saasCostPerUnit: number;
  vendorAnnualGrowth: number;
  egressCostPerGb: number;
}

interface TCOSimulationResult {
  totalNpv: number;
  quarterlyBreakdown: number[];
}

function simulateTCO(
  option: TCOInputOption,
  quarterlyUnits: number[],
  quarterlyEgressGb: number[],
  annualDiscountRate: number = 0.08
): TCOSimulationResult {
  if (quarterlyUnits.length !== 12 || quarterlyEgressGb.length !== 12) {
    throw new Error("Simulation requires 12 quarters of data.");
  }

  const quarterlyR = Math.pow(1.0 + annualDiscountRate, 0.25) - 1.0;
  let totalNpv = option.initialCost;
  const quarterlyBreakdown: number[] = [];

  for (let q = 0; q < 12; q++) {
    const year = Math.floor(q / 4);
    const units = quarterlyUnits[q];
    const egress = quarterlyEgressGb[q];

    const vendorMarkup = Math.pow(1.0 + option.vendorAnnualGrowth, year);
    const licenseCost = units * option.saasCostPerUnit * vendorMarkup;
    const opsCost = option.sreFteCount * option.sreQuarterlySalary;
    const egressCost = egress * option.egressCostPerGb;

    const rawCost = licenseCost + opsCost + option.quarterlyBaseInfra + egressCost;
    const discountFactor = Math.pow(1.0 + quarterlyR, q + 1);
    const discounted = rawCost / discountFactor;

    totalNpv += discounted;
    quarterlyBreakdown.push(discounted);
  }

  return { totalNpv, quarterlyBreakdown };
}
```
:::

---

## 4. Аналіз чутливості та оцінка крайових випадків

Математична модель TCO дозволяє провести **аналіз чутливості** (англ. *sensitivity analysis*) — визначення того, які саме змінні найбільше впливають на підсумкову точку беззбитковості $N^*$.

### Важелі впливу на рішення:

1. **Чутливість до інфляції вендора (`g_vendor`):**
   Якщо SaaS-вендор піднімає ціну не на 15%, а на 25% на рік (що є типовим при зміні корпоративних тарифів), точка перелому $N^*$ зсувається ліворуч на 3–4 квартали. Рішення на користь Self-Hosted стає вигідним набагато раніше.
2. **Чутливість до вартості SRE-команди (`sre_quarterly_salary`):**
   У регіонах із високою вартістю інженерних кадрів ($120k+ на рік за 1 SRE) фіксований поріг Self-Hosted розгортання піднімається вгору. Якщо для підтримки кластера потрібні 2.0 FTE старших SRE, то SaaS залишається дешевшим до вищих обсягів навантаження.
3. **Вплив ставки дисконтування (`r_annual`):**
   Для стартапів на ранніх стадіях із високою ціною капіталу та ризиком не дожити до 3-го року ставка дисконтування досягає 25–35%. Це робить авансові витрати `C_initial` надзвичайно дорогими, категорично схиляючи вибір убік SaaS. Для зрілих корпорацій зі ставкою 6–8% перевагу отримують довгострокові інвестиції у власну інфраструктуру.
4. **Цінність розривного шва як фінансового опціону (Option Value of Seams):**
   Створення порту й адаптера на початку проєкту коштує приблизно $10,000–15,000 (додатковий тиждень розробки). Проте цей шов дає організаційний опціон здійснити репатріацію у будь-який момент за фіксовану вартість замість повного переписування продукту за $200,000. Фінансова цінність цього опціону обчислюється як:
   ```
   Val_option = P_repatriation × (TCO_saas - TCO_self) - C_seam
   ```
   Якщо ймовірність досягнення точки $N^*$ протягом 3 років становить 40%, а потенційна економія репатріації дорівнює $120,000, то цінність встановлення шва становить:
   ```
   Val_option = 0.40 × $120,000 - $15,000 = $33,000
   ```
   Позитивне значення цінності опціону (+$33,000) доводить, що інвестувати в ізоляційний шов (Port-Adapter) варто завжди, навіть якщо на першому етапі обирається SaaS.
