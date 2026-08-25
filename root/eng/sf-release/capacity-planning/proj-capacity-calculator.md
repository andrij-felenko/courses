# ⚙️ Моделювання потреби в ресурсах та аналізатор Headroom

Планування обчислювальної місткості на основі статичних електронних таблиць не враховує нелінійну динаміку черг, багаторівневе резервування зон доступності та раптові спалахи попиту. Інженерний симулятор навантаження дозволяє наперед промоделювати поведінку кластера: обчислити необхідну кількість вузлів, перевірити стійкість до відмови дата-центру (Multi-AZ Failover), розрахувати динамічний Headroom та спрогнозувати 99-й перцентиль затримки в черзі при екстремальних навантаженнях.

## Архітектура моделі розрахунку та вхідна телеметрія

При проєктуванні системи планування потужностей інженер має справу з двома взаємопов'язаними площинами: динамікою бізнес-попиту (скільки користувачів створюють замовлення) та фізичними обмеженнями серверного вузла (скільки запитів на секунду здатне обробити одне ядро CPU до переповнення сокетних черг).

Аналізатор місткості спирається на метрики часових рядів, які збираються з агентів моніторингу (Prometheus, CloudWatch, Datadog), і виконує три послідовні розрахункові фази:

1. **Фаза профілювання та екстраполяції навантаження:** розрахунок сумарного пікового потоку запитів `Λ_peak`. Вона враховує середній денний трафік у стані спокою (`base_rps`), добову циклічність активності користувачів (`diurnal_factor`, наприклад, пік між 19:00 та 21:00), коефіцієнт короткочасних стохастичних спалахів (`burst_factor`, спричинений пуш-сповіщеннями чи маркетинговими розсилками) та темп бізнес-росту сервісу на обраному горизонті планування (`months_ahead`).
2. **Фаза просторового розміщення та резервування відмов:** визначення мінімальної кількості робочих вузлів на основі гранично безпечної утилізації `U_target` (зазвичай 60–75%), рівномірний розподіл вузлів між `M` незалежними зонами доступності (Availability Zones, AZ) та додавання локального резерву `N+k` у кожній зоні для безперервного виведення машин у режим оновлення без порушення загального бюджету місткості.
3. **Фаза стрес-симуляції та аналізу черг:** моделювання катастрофічного сценарію повної втрати однієї зони доступності (AZ Outage), розрахунок післяаварійної завантаженості `U_disaster`, перевірка наближення до критичного коліна насичення та аналітична оцінка 99-го перцентиля затримки черги `p99` за формулою розподілу черг `M/M/1`.

```
ВХІДНІ ТЕЛЕМЕТРИЧНІ ДАНІ:
- Базовий RPS, Добовий коефіцієнт піку, Фактор випадкових сплесків
- Продуктивність 1 вузла (RPS), Чистий час обробки на ядрі S (мс)
- Кількість зон AZ, Локальний резерв відмов на зону (N+1)
        │
        ▼
   [ АНАЛІЗАТОР HEADROOM ТА МІСТКОСТІ ]
        │
        ├── 1. Прогнозування складного відсотка росту (Compound Growth)
        ├── 2. Розрахунок мінімального робочого пулу (N_work)
        ├── 3. Балансування по зонах доступності (Bin Packing)
        ├── 4. Оцінка штатного Headroom = 1 - U_steady
        ├── 5. Моделювання відмови дата-центру (AZ Outage)
        └── 6. Розрахунок p99 затримки черги (штатний стан проти аварії)
        │
        ▼
ЗВІТ: Рекомендована топологія, розподіл по зонах, запас міцності та SLO
```

### Чому затримка оцінюється саме на 99-му перцентилі

Середнє арифметичне значення затримки (Mean Latency) є оманливим показником для оцінки достатності потужностей: якщо 95% запитів повертаються за 15 мс, а 5% зависають у черзі на 4 000 мс через брак вільних обчислювальних потоків, середнє значення покаже прийнятні 214 мс, тоді як кожен двадцятий клієнт зазнає збою операції.

Математична модель калькулятора використовує квантильну функцію очікування `M/M/1`:

```
t_99 = S · ( ln[ U / 0.01 ] / (1 - U) )
```

Ця формула безпосередньо показує ціну утилізації: при зростанні `U` знаменник `1 - U` стрімко стискається, перетворюючи навіть мікросекундний чистий час обробки `S` на відчутну затримку в десятки або сотні мілісекунд. Калькулятор автоматично перевіряє, чи не призведе аварійне перерозподілення трафіку до виходу `t_99` за межі допустимого інженерного бюджету.

## Реалізація аналізатора

Нижче наведено робочу реалізацію симулятора навантаження та аналізатора Headroom двома мовами: Python для швидкого аналізу телеметрії та сучасний C++20 для вбудовування в контролери оркестрації та інфраструктурні демони.

:::tabs
```py
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
```
```cpp
#include <cmath>
#include <format>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

struct WorkloadProfile {
    double base_rps;          // Середній денний трафік (RPS)
    double diurnal_factor;    // Коефіцієнт вечірнього піку
    double burst_factor;      // Коефіцієнт непередбачених сплесків
    double growth_rate_pct;   // Очікуваний ріст на місяць у %
    int months_ahead;         // Горизонт планування в місяцях
};

struct NodeProfile {
    double capacity_rps;      // Максимальна продуктивність одного вузла (RPS)
    double service_time_ms;   // Чистий час виконання запиту на CPU (мс)
    double max_safe_util;     // Гранично допустима безпечна утилізація
};

struct ResilienceConfig {
    int availability_zones;   // Кількість зон доступності (AZ)
    int extra_nodes_per_az;   // Локальний резерв на зону (N+1)
};

struct CapacityPlan {
    double forecast_peak_rps;
    int total_nodes;
    int nodes_per_az;
    double steady_state_util;
    double steady_state_headroom;
    double disaster_util;
    double disaster_headroom;
    double steady_p99_latency_ms;
    double disaster_p99_latency_ms;
    bool is_slo_safe;
};

// Обчислює 99-й перцентиль затримки очікування в черзі за моделлю M/M/1
[[nodiscard]] double calculate_p99_queue_delay(double service_time_ms, double util) noexcept {
    if (util >= 0.999) {
        return std::numeric_limits<double>::infinity();
    }
    if (util <= 0.001) {
        return 0.0;
    }
    // t_99 = S * ln(util / (1 - 0.99)) / (1 - util)
    return service_time_ms * (std::log(util / 0.01) / (1.0 - util));
}

[[nodiscard]] CapacityPlan plan_capacity(
    const WorkloadProfile& workload,
    const NodeProfile& node,
    const ResilienceConfig& resilience
) {
    if (resilience.availability_zones < 2) {
        throw std::invalid_argument("Для Multi-AZ планування потрібно щонайменше 2 зони.");
    }

    // 1. Прогноз пікового навантаження з урахуванням складного відсотка росту
    const double growth_multiplier = std::pow(1.0 + workload.growth_rate_pct / 100.0, workload.months_ahead);
    const double peak_rps = workload.base_rps * workload.diurnal_factor * workload.burst_factor * growth_multiplier;

    // 2. Розрахунок штатної потреби для Multi-AZ схеми
    const int m = resilience.availability_zones;
    const double disaster_usable_node_rps = node.capacity_rps * node.max_safe_util;
    const int min_working_nodes_disaster = static_cast<int>(std::ceil(peak_rps / disaster_usable_node_rps));
    const int nodes_per_az_work = static_cast<int>(std::ceil(static_cast<double>(min_working_nodes_disaster) / (m - 1)));

    // Повний розмір зони з локальним резервом (N+k)
    const int nodes_per_az_total = nodes_per_az_work + resilience.extra_nodes_per_az;
    const int total_nodes = nodes_per_az_total * m;

    // 3. Аналіз штатного стану (Normal State)
    const double total_cluster_capacity_rps = total_nodes * node.capacity_rps;
    const double steady_util = peak_rps / total_cluster_capacity_rps;
    const double steady_headroom = 1.0 - steady_util;

    // 4. Аналіз катастрофічного стану (1 AZ Outage)
    const int surviving_nodes = nodes_per_az_total * (m - 1);
    const double disaster_capacity_rps = surviving_nodes * node.capacity_rps;
    const double disaster_util = peak_rps / disaster_capacity_rps;
    const double disaster_headroom = 1.0 - disaster_util;

    // 5. Розрахунок затримок черг
    const double steady_p99 = calculate_p99_queue_delay(node.service_time_ms, steady_util);
    const double disaster_p99 = calculate_p99_queue_delay(node.service_time_ms, disaster_util);
    const bool is_safe = disaster_util <= node.max_safe_util;

    return CapacityPlan{
        .forecast_peak_rps = peak_rps,
        .total_nodes = total_nodes,
        .nodes_per_az = nodes_per_az_total,
        .steady_state_util = steady_util,
        .steady_state_headroom = steady_headroom,
        .disaster_util = disaster_util,
        .disaster_headroom = disaster_headroom,
        .steady_p99_latency_ms = steady_p99,
        .disaster_p99_latency_ms = disaster_p99,
        .is_slo_safe = is_safe
    };
}

void print_report(const CapacityPlan& plan) {
    std::cout << "====================================================================\n";
    std::cout << "           ЗВІТ ПЛАНУВАННЯ ПОТУЖНОСТЕЙ ТА HEADROOM (C++20)\n";
    std::cout << "====================================================================\n";
    std::cout << "Прогнозований піковий трафік : " << plan.forecast_peak_rps << " RPS\n";
    std::cout << "Загальна кількість вузлів     : " << plan.total_nodes 
              << " (по " << plan.nodes_per_az << " у кожній з зон)\n";
    std::cout << "--------------------------------------------------------------------\n";
    std::cout << "ШТАТНИЙ РЕЖИМ (УСІ ЗОНИ ПРАЦЮЮТЬ):\n";
    std::cout << "  • Утилізація кластера       : " << (plan.steady_state_util * 100.0) << "%\n";
    std::cout << "  • Запас міцності (Headroom) : " << (plan.steady_state_headroom * 100.0) << "%\n";
    std::cout << "  • Оцінка p99 затримки черги : " << plan.steady_p99_latency_ms << " мс\n";
    std::cout << "--------------------------------------------------------------------\n";
    std::cout << "СТРЕС-СЦЕНАРІЙ (АВАРІЯ 1 ЗОНИ ДОСТУПНОСТІ):\n";
    std::cout << "  • Утилізація вцілілих зон   : " << (plan.disaster_util * 100.0) << "%\n";
    std::cout << "  • Залишковий Headroom       : " << (plan.disaster_headroom * 100.0) << "%\n";
    std::cout << "  • Оцінка p99 затримки черги : " << plan.disaster_p99_latency_ms << " мс\n";
    std::cout << "--------------------------------------------------------------------\n";
    const std::string_view status_str = plan.is_slo_safe ? "✓ БЕЗПЕЧНО (SLO ДОТРИМАНО)" : "✖ НЕБЕЗПЕКА (РИЗИК КОЛАПСУ)";
    std::cout << "ПІДСУМКОВИЙ СТАТУС НАДІЙНОСТІ : " << status_str << "\n";
    std::cout << "====================================================================\n";
}

int main() {
    const WorkloadProfile workload{
        .base_rps = 5000.0,
        .diurnal_factor = 1.6,
        .burst_factor = 1.2,
        .growth_rate_pct = 8.0,
        .months_ahead = 3
    };

    const NodeProfile node{
        .capacity_rps = 350.0,
        .service_time_ms = 2.8,
        .max_safe_util = 0.75
    };

    const ResilienceConfig resilience{
        .availability_zones = 3,
        .extra_nodes_per_az = 1
    };

    const CapacityPlan plan = plan_capacity(workload, node, resilience);
    print_report(plan);

    return 0;
}
```
:::

## Аналіз виводу програми та покрокова перевірка розрахунку

Виконаємо детальний математичний розрахунок для вказаних у коді параметрів і простежимо кожну ланку обчислювального ланцюга:

1. **Прогноз піку навантаження з урахуванням зростання бізнесу:**
   ```
   Множник росту за 3 місяці при 8% на місяць = (1 + 0.08)³ = 1.08³ = 1.259712
   Базовий пік = 5 000 · 1.6 (добовий) · 1.2 (сплеск) = 9 600 RPS
   Прогнозований пік з урахуванням росту = 9 600 · 1.259712 ≈ 12 093.2 RPS
   ```

2. **Розрахунок потреби для 3 зон (`M = 3` AZ):**
   ```
   Корисна місткість одного вузла при аварії = 350 · 0.75 = 262.5 RPS
   Потрібно робочих вузлів на 2 вцілілі зони = ceil[ 12 093.2 / 262.5 ] = ceil[ 46.069 ] = 47 вузлів
   Вузлів на одну зону (робочих) = ceil[ 47 / 2 ] = 24 вузли
   Вузлів на одну зону (з локальним резервом N+1) = 24 + 1 = 25 вузлів
   Сумарний пул кластера = 25 · 3 = 75 вузлів
   ```

3. **Оцінка показників у штатному режимі:**
   ```
   Сумарна пікова потужність кластера = 75 · 350 = 26 250 RPS
   Штатна утилізація = 12 093.2 / 26 250 ≈ 0.4607 (46.1%)
   Штатний Headroom = 100% - 46.1% = 53.9%
   p99 затримка черги:
   t_99 = 2.8 мс · ( ln(0.4607 / 0.01) / (1 - 0.4607) ) = 2.8 · ( ln(46.07) / 0.5393 ) = 2.8 · ( 3.830 / 0.5393 ) ≈ 19.88 мс
   ```

4. **Оцінка показників під час аварії 1 зони:**
   ```
   Вціліло вузлів у 2 зонах = 25 · 2 = 50 вузлів
   Потужність вцілілих зон = 50 · 350 = 17 500 RPS
   Пікова утилізація при катастрофі = 12 093.2 / 17 500 ≈ 0.6910 (69.1%)
   Залишковий Headroom при катастрофі = 100% - 69.1% = 30.9%
   p99 затримка черги при катастрофі:
   t_99 = 2.8 мс · ( ln(0.6910 / 0.01) / (1 - 0.6910) ) = 2.8 · ( ln(69.10) / 0.3090 ) = 2.8 · ( 4.235 / 0.3090 ) ≈ 38.38 мс
   ```

Оскільки аварійна утилізація `69.1%` не перевищує граничний ліміт безпеки `75%`, система успішно пройде випробування втратою дата-центру: 99-й перцентиль затримки черги зросте з 19.88 мс до 38.38 мс, не перетинаючи критичну межу таймаутів користувацьких клієнтів.

## Глибокий аналіз інженерних пасток та системних крайових випадків

При практичній експлуатації кластерів, розрахованих за моделлю Headroom, інженери регулярно стикаються з нелінійними вторинними ефектами, які здатні зламати систему навіть за наявності достатньої кількості процесорних ядер.

### 1. Вичерпання пулів з'єднань баз даних (Connection Pool Saturation)
При масштабуванні бекенду з 20 до 75 вузлів кожен новий процес ініціалізує власні пули постійних з'єднань до сховищ даних (PostgreSQL, MySQL, Redis, Cassandra):
- Якщо кожен бекенд-вузол виділяє пул із 20 з'єднань до PostgreSQL, загальна кількість відкритих сокетів до бази даних підскакує з 400 до `75 · 20 = 1 500` з'єднань;
- Сервер бази даних витрачає гігабайти оперативної пам'яті лише на підтримку системних буферів підключень (кожен процес бекенду в PostgreSQL вимагає окремого форку процесу ОС із власною пам'яттю `work_mem` та дескрипторами);
- База даних входить у стан жорсткої конкуренції за блокування пам'яті (Latch Contention), і час виконання найпростіших SQL-запитів зростає в 10 разів;
- **Архітектурне вирішення:** встановлення проміжного шару пулінгу транзакцій (PgBouncer, ProxySQL або Envoy Database Proxy), який тримає пул з'єднань до самої бази постійно обмеженим (наприклад, строго 100 з'єднань), незалежно від того, скільки сотень реплік бекенду розгорнув оркестратор.

### 2. Асиметрія маршрутизації в L4/L7 Ingress-контролерах
У сучасних мікросервісних архітектурах клієнти використовують протоколи HTTP/2 або gRPC, які підтримують постійні мультиплексовані TCP-з'єднання (Long-lived TCP connections):
- Балансувальник транспортного рівня (L4 Load Balancer) відкриває TCP-сесію один раз і спрямовує всі наступні тисячі RPC-викликів у той самий бекенд-вузол;
- Коли калькулятор потужності виділяє додаткові 25 вузлів під час ранкового піку, нові машини з'являються в мережі, але старі клієнти продовжують штурмувати попередні 50 вузлів через вже відкриті сокети;
- Старі вузли зазнають перевантаження й відмовляють, тоді як нові вузли простоюють із 5% утилізації;
- **Архітектурне вирішення:** конфігурація параметрів ротації з'єднань: налаштування `max_connection_age` (наприклад, примусове плавне закриття TCP-сесії кожні 5 хвилин для перепідключення) та перехід на балансування рівня додатків (L7 Load Balancing), де балансувальник розподіляє окремі HTTP/2-стріми, а не «сирі» TCP-сокети.

### 3. Накладні витрати системних демонів (Allocatable vs Capacity)
При фізичному плануванні кластерів Kubernetes важливо не плутати загальну апаратну місткість вузла (`node.capacity`) з реально доступною місткістю під бізнес-контейнери (`node.allocatable`):
- На кожному фізичному або віртуальному вузлі працюють обов'язкові системні компоненти: `kubelet`, `containerd`, агент збору логів (Fluentbit/Vector), агент метрик (Prometheus Node Exporter) та мережевий плагін CNI (Cilium/Calico);
- Якщо сервіс розгортається в сервісній сітці (Service Mesh, наприклад Istio або Linkerd), до кожного пода додається проксі-контейнер Sidecar (Envoy), який споживає додаткові 0.25–0.50 vCPU та 128–256 МБ RAM;
- Якщо вузол має номінальні 8 vCPU, реальна корисна місткість становить лише 6.0–6.5 vCPU;
- **Архітектурне вирішення:** калькулятор потужностей зобов'язаний спиратися на значення `allocatable` ресурсів, віднімаючи фіксований системний оверхед перед розрахунком розміру кластера.

### 4. Автоматизація перевірки місткості у CI/CD пайплайнах
Планування потужностей не може бути одноразовою подією під час запуску проекту. Кожен новий реліз програмного забезпечення може містити алгоритмічні регресії (наприклад, випадкову появу проблеми вибірок `N+1` у базі даних або неефективну серіалізацію JSON), яка подвоює собівартість одного запиту:
- У пайплайні CI/CD розгортається автоматизований крок навантажувального тестування (Canary Performance Test);
- Калькулятор зчитує метрику чистого процесорного часу на операцію `service_time_ms` нової версії коду;
- Якщо собівартість транзакції зросла на 15%, калькулятор перераховує необхідний розмір кластера і автоматично блокує реліз (Pipeline Gate), якщо виділеного інфраструктурного бюджету або закладеного Headroom недостатньо для збереження вимог SLO.

### 5. Інтеграція з FinOps: оптимізація структури хмарних витрат
Утримання 75 вузлів, які більшу частину доби завантажені лише на 46%, створює ризик фінансової неефективності, якщо всі сервери оплачуються за найдорожчим тарифом On-Demand.

Інженерна практика поєднує математику Headroom з фінансовою оптимізацією:
1. **Базовий пул (40–45% місткості):** покривається 1–3-річними зарезервованими зобов'язаннями (Reserved Instances / Savings Plans), що знижує витрати на постійне ядро системи на 50–70%;
2. **Добовий робочий пік (до 70% місткості):** динамічно піднімається за допомогою горизонтального автоскейлу стандартних On-Demand інстансів;
3. **Аварійний резерв та Headroom під відмову зон (верхні 30% місткості):** може частково забезпечуватися спотовими віртуальними машинами (Spot Instances) з підтримкою автоматичного дренажу або низькопріоритетними фоновими воркерами, які миттєво звільняють місце під час напливу критичного трафіку.

## Інтеграція з Prometheus: видобування вхідних параметрів із телеметрії

Щоб аналізатор автоматично отримував свіжі параметри навантаження з виробничого середовища, використовують PromQL-запити до сервера моніторингу Prometheus:

1. **Вимірювання базового потоку запитів (`base_rps`):**
   ```promql
   sum(rate(http_requests_total{job="api-backend"}[1h]))
   ```
   Запит обчислює середню швидкість надходження HTTP-запитів за останню годину по всьому кластеру.

2. **Обчислення коефіцієнта добового піку (`diurnal_factor`):**
   ```promql
   max_over_time(sum(rate(http_requests_total{job="api-backend"}[5m]))[24h:5m])
   /
   avg_over_time(sum(rate(http_requests_total{job="api-backend"}[5m]))[24h:5m])
   ```
   Ділення 5-хвилинного максимуму за останню добу на середньодобовий показник дає точний емпіричний коефіцієнт добової нерівномірності.

3. **Оцінка чистого часу обробки на процесорі (`service_time_ms`):**
   ```promql
   sum(rate(container_cpu_usage_seconds_total{container="api-backend"}[5m]))
   /
   sum(rate(http_requests_total{job="api-backend"}[5m]))
   * 1000
   ```
   Ділення сумарного витраченого процесорного часу (в секундах ядра на секунду) на кількість оброблених запитів за ту саму секунду з множенням на 1000 повертає чистий час виконання одного запиту на CPU в мілісекундах (`S`).

4. **Виявлення системного тротлінгу CFS:**
   ```promql
   sum(rate(container_cpu_cfs_throttled_seconds_total{container="api-backend"}[5m]))
   /
   sum(rate(container_cpu_cfs_periods_total{container="api-backend"}[5m]))
   ```
   Якщо частка періодів із тротлінгом перевищує 5%, ліміти `cpu.limits` є заниженими, і розрахована місткість не захистить від спалахів затримок.

## Валідація моделі за допомогою хаос-інженерії (Chaos Testing)

Теоретична модель вважається верифікованою лише після того, як її прогнози підтверджуються в контрольованому експерименті відмови (Chaos Engineering):

1. **Підготовка стенду:** на стейджинг-середовищі розгортається кластер із 75 вузлів за результатами роботи аналізатора (по 25 вузлів у 3 зонах доступності);
2. **Генерація пікового потоку:** генератор навантаження (k6 або Locust) подає розрахований піковий потік `12 093` RPS;
3. **Ініціація аварії:** за допомогою інструменту хаос-тестування (Chaos Mesh або AWS Fault Injection Simulator) блокується мережевий маршрутизатор або знеструмлюються всі 25 вузлів у зоні `Zone-C`;
4. **Порівняння телеметрії з розрахунком:**
   - Модель спрогнозувала післяаварійне завантаження `U_disaster = 69.1%`. Телеметрія Prometheus повинна зафіксувати утилізацію ядер у вцілілих зонах `Zone-A` та `Zone-B` на рівні 67–71%;
   - Модель спрогнозувала `p99` затримки черги `38.38` мс. Метрика `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[1m]))` повинна показати стрибок затримки до 35–42 мс без появи помилок HTTP 5xx;
5. **Висновки:** якщо реальна затримка злетіла до 500 мс або з'явилися помилки таймаутів, це свідчить про наявність неврахованого вузького місця (наприклад, блокування пулу з'єднань до бази даних або дефіцит мережевих дескрипторів), яке вимагає коригування вхідного профілю сервісу.

## Автоматизація в Kubernetes: від калькулятора до власного контролера (Operator Pattern)

Ручний запуск інженерного аналізатора перед кожним релізом — це перший крок, проте у динамічних хмарних середовищах навантаження змінюється щодня. Наступним еволюційним рівнем є перетворення цієї моделі на **автономний контролер місткості (Capacity Operator)** усередині кластера Kubernetes.

```
+-------------------------------------------------------------------------+
|                  KUBERNETES CAPACITY OPERATOR LOOP                     |
|                                                                         |
|  [ Prometheus API ] ──(PromQL кожні 15 хв)──> [ Контролер місткості ]  |
|                                                         │               |
|                                             (Розрахунок моделі)         |
|                                                         │               |
|                                                         ▼               |
|  [ Karpenter NodePool ] <──(Оновлення minSize)── [ Custom Resource ]    |
|  [ HPA minReplicas    ] <──(Оновлення меж)────── [ CapacitySchedule ]   |
+-------------------------------------------------------------------------+
```

### Структура користувацького ресурсу (Custom Resource Definition)
Контролер керується маніфестом `CapacityPlan`, у якому інженери фіксують вимоги до стійкості та цілі SLO:

```yaml
apiVersion: autoscaling.infrastructure.io/v1alpha1
kind: CapacityPlan
metadata:
  name: payment-backend-capacity
  namespace: production
spec:
  workloadSelector:
    app: payment-api
  targetUtilization: 0.65
  maxSafeUtilization: 0.75
  maxQueueLatencyP99Ms: 25.0
  serviceLevelObjectiveMs: 50.0
  resilience:
    availabilityZones: 3
    minSurvivingZones: 2
    redundancyPerZone: "N+1"
  telemetrySource:
    prometheusUrl: "http://prometheus-k8s.monitoring.svc:9090"
    trafficMetric: "sum(rate(http_requests_total{app='payment-api'}[5m]))"
    cpuTimeMetric: "sum(rate(container_cpu_usage_seconds_total{container='payment-api'}[5m]))"
```

### Цикл узгодження контролера (Reconciliation Loop)
Кожні 15 хвилин оператор виконує три операції:
1. **Збір метрик:** виконує PromQL-запити до Prometheus, витягує поточний `base_rps`, оцінює добовий тренд та вимірює середній час `service_time_ms`;
2. **Розрахунок моделі:** запускає внутрішній алгоритм (ідентичний наведеній вище реалізації на C++ чи Python) і визначає мінімальну безпечну кількість вузлів у кожній зоні доступності;
3. **Застосування змін до оркестратора:**
   - Оновлює параметр `spec.minReplicas` у маніфесті Horizontal Pod Autoscaler (HPA), щоб автоскейл не міг зменшити кількість подів нижче порога Multi-AZ безпеки під час нічного спаду навантаження;
   - Коригує ліміти вузлів у пулі планувальника Karpenter (`NodePool.spec.limits.cpu`), гарантуючи резервування фізичних інстансів під аварійний Headroom.

## Захист контуру моніторингу: відмовостійкість при збої телеметрії

Якщо система планування автоматизована, виникає новий клас ризику: **що станеться, якщо сервер Prometheus тимчасово вийде з ладу або почне повертати нульові значення метрик?**

Наївний автоскейлер, побачивши нульовий RPS або відсутність даних від Prometheus, вирішить, що навантаження зникло, і почне скорочувати кластер, спричиняючи аварію.

Інженерний контур планування Headroom зобов'язаний реалізовувати три рівні захисту від помилок спостережуваності:

1. **Захисний поріг зниження (Floor Limit):** контролеру заборонено встановлювати розмір пулу нижче статично зафіксованого абсолютного мінімуму (Hard Minimum), який розрахований на річний базовий рівень бізнесу;
2. **Фільтр заморозки стану (Hold on Error):** якщо запит до Prometheus повертає таймаут, мережеву помилку або порожній набір часових рядів, контролер зберігає останній успішно розрахований план місткості та генерує сповіщення черговому інженеру (Alerting);
3. **Обмеження швидкості деградації (Rate of Change Limiting):** зміна розміру кластера вниз (Scale-In) обмежується демпфером (наприклад, зменшення пулу не більше ніж на 10% за одне 30-хвилинне вікно стабілізації), що повністю виключає раптове схлопування потужностей через короткочасний шум телеметрії.

## Налаштування мережевих буферів ядра Linux для пікових навантажень

Навіть якщо обчислювальний пул розраховано правильно, система може зазнавати втрат пакетів на рівні ядра операційної системи, якщо мережеві буфери пам'яті (Socket Buffers) залишаються зі стандартними низькими лімітами дистрибутива.

Для підтримки пікового трафіку в 12 000+ RPS на кожному хості налаштовують параметри ядра через `sysctl`:

```ini
# Максимальний розмір черги очікування виклику accept()
net.core.somaxconn = 65535

# Максимальний розмір черги напіввідкритих TCP-з'єднань (SYN-пакети)
net.ipv4.tcp_max_syn_backlog = 65535

# Буфери прийому (min, default, max) для TCP-сокетів
net.ipv4.tcp_rmem = 4096 87380 16777216

# Буфери надсилання (min, default, max) для TCP-сокетів
net.ipv4.tcp_wmem = 4096 65536 16777216

# Максимальний розмір черги пакетів на мережевому інтерфейсі (NIC Backlog)
net.core.netdev_max_backlog = 10000
```

Ці налаштування гарантують, що під час раптових сплесків трафіку (Burst Factor) мережевий стек ядра Linux буферизує вхідні пакети в оперативній пам'яті без відкидання (No Packet Drops), надаючи застосунку та планувальнику Headroom необхідний час для плавної обробки черги та виділення додаткових вузлів без переривання сервісу. Комплексне поєднання системних параметрів ядра, моделювання черг та автоматизації в оркестраторі усуває ризик непередбачених відмов і забезпечує повний захист цільових вимог SLO під будь-яким піковим навантаженням.
