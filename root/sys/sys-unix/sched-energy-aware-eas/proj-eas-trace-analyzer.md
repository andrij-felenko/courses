# ⚙️ Аналізатор та симулятор рішень EAS

Ця вставка містить повністю робочий приклад консольної утиліти-аналізатора, яка реалізує алгоритм моделювання рішень Energy-Aware Scheduling (EAS). Програма зчитує спрощену таблицю станів Energy Model (OPP) двох процесорних кластерів (LITTLE та big) і розраховує підсумкову енергетичну дельту `ΔE = E_with - E_without` при пробудженні задачі для двох конкуруючих варіантів її призначення.

## 1. Опис алгоритму та математичної моделі симулятора

Утиліта приймає з аргументів командного рядка три числові параметри:
- `util_little`: поточне сумарне навантаження PELT на енергоефективному кластері LITTLE;
- `util_big`: поточне сумарне навантаження PELT на продуктивному кластері big;
- `task_util`: навантаження `util_avg` нової задачі, яка пробуджується і вимагає призначення на ядро.

Програма моделює два сценарії розміщення задачі:

1. **Варіант А (Placement on LITTLE):** задача додається до черги виконання ядра LITTLE. Сумарне навантаження кластера становитиме `util_little + task_util`.
2. **Варіант Б (Placement on big):** задача додається до черги виконання ядра big. Сумарне навантаження кластера становитиме `util_big + task_util`.

Для кожного варіанта симулятор виконує такі математичні кроки:
- Обчислює необхідну частоту кластера з урахуванням 25-відсоткового запасу продуктивності (headroom `1.25`), який вимагає регулятор `schedutil`.
- Обмежує отриманий запит стелею вихідної ємності кластера `capacity_orig`.
- Виконує бінарний пошук відповідного стану OPP в таблиці Energy Model.
- Визначає споживану потужність кластера в міліватах (мВт).
- Розраховує сумарне енергоспоживання системи `E_candidate` та визначає енергетичну дельту `ΔE = E_candidate - E_current`.
- Порівнює `ΔE_A` та `ΔE_B` і виводить підсумкове рішення планувальника про вибір ядра.

Симулятор навмисно не моделює стану Over-Utilized: якщо запит перевищує місткість кластера, він просто обмежує його стелею `capacity_orig` і бере найвищий OPP. У реальному ядрі перевищення 80% ємності будь-якого ядра скасовує енергетичні обчислення й повертає планувальник до симетричного балансування навантаження CFS — цю різницю добре видно у Сценарії 2.

## 2. Порівняльний розбір системних архітектур реалізації

Представлений кодовий приклад виконано у двох діалектах: стандартному ANSI C (C99) та сучасному ідіоматичному C++20. Обидві версії демонструють розбіжність підходів до проектування системного софту під Linux.

У C-реалізації використовується пряме управління пам'яттю, статично розміщені структури даних `perf_domain_t` та процедурний підхід. Функція `get_domain_power()` приймає вказівник на константну структуру й ітерується по масиву станів `opps`. Такий підхід є типовим для системних модулів ядра Linux, де відсутня стандартна бібліотека C++ і вимагається мінімальний розмір двійкового коду.

У C++20-реалізації застосовано принципи RAII (Resource Acquisition Is Initialization), строгу типізацію `std::uint32_t`, концепцію незмінних рядкових представлень `std::string_view`, а також алгоритми стандартної бібліотеки `std::find_if`. Клас `PerfDomain` інкапсулює внутрішній стан домену і надає константний метод `calculate_power()`, що унеможливлює випадкову деструктивну модифікацію даних OPP під час виконання розрахунків.

Крім того, C++20-версія використовує кваліфікатор `[[nodiscard]]` для запобігання ігноруванню результатів обчислення потужності та забезпечує гарантію відсутності винятків `noexcept` для простіших методів-доступу, що є стандартом проектування високопродуктивних системних бібліотек.

У практичних задачах бенчмаркінгу C++20-код дозволяє розширювати симулятор новими апаратними доменами (наприклад, додавати Prime-ядра або GPU-кластери) без зміни сигнатур функцій, лише шляхом додавання нових екземплярів `PerfDomain` до вектора доменів.

## 3. Вихідний код симулятора (C та C++)

Нижче наведено обидві ідіоматичні реалізації утиліти.

:::tabs
```c
/* eas_simulator.c — Реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_OPP 4
#define SCHED_CAPACITY_SCALE 1024

typedef struct {
    unsigned long frequency_khz;
    unsigned long power_mw;
    unsigned long performance;
} opp_entry_t;

typedef struct {
    const char *name;
    unsigned long capacity_orig;
    int num_opp;
    opp_entry_t opps[MAX_OPP];
} perf_domain_t;

static perf_domain_t little_domain = {
    .name = "LITTLE Cluster",
    .capacity_orig = 400,
    .num_opp = 3,
    .opps = {
        { 300000,  45, 100 },
        { 600000,  95, 200 },
        { 1200000, 210, 400 }
    }
};

static perf_domain_t big_domain = {
    .name = "big Cluster",
    .capacity_orig = 1024,
    .num_opp = 3,
    .opps = {
        { 800000,  450, 500 },
        { 1500000, 900, 800 },
        { 2000000, 1500, 1024 }
    }
};

static unsigned long get_domain_power(const perf_domain_t *domain, unsigned long util_request) {
    if (util_request == 0) {
        return 0;
    }
    /* Розрахунок вимоги з урахуванням headroom 1.25 */
    unsigned long req = (util_request * 125) / 100;
    if (req > domain->capacity_orig) {
        req = domain->capacity_orig;
    }

    for (int i = 0; i < domain->num_opp; i++) {
        if (domain->opps[i].performance >= req) {
            return domain->opps[i].power_mw;
        }
    }
    return domain->opps[domain->num_opp - 1].power_mw;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <util_little> <util_big> <task_util>\n", argv[0]);
        return 1;
    }

    unsigned long util_little = strtoul(argv[1], NULL, 10);
    unsigned long util_big = strtoul(argv[2], NULL, 10);
    unsigned long task_util = strtoul(argv[3], NULL, 10);

    /* 1. Поточне енергоспоживання системи */
    unsigned long p_little_cur = get_domain_power(&little_domain, util_little);
    unsigned long p_big_cur = get_domain_power(&big_domain, util_big);
    unsigned long e_current = p_little_cur + p_big_cur;

    /* 2. Варіант А: Задача на LITTLE */
    unsigned long p_little_candA = get_domain_power(&little_domain, util_little + task_util);
    unsigned long p_big_candA = p_big_cur;
    unsigned long e_candA = p_little_candA + p_big_candA;
    long delta_A = (long)e_candA - (long)e_current;

    /* 3. Варіант Б: Задача на big */
    unsigned long p_little_candB = p_little_cur;
    unsigned long p_big_candB = get_domain_power(&big_domain, util_big + task_util);
    unsigned long e_candB = p_little_candB + p_big_candB;
    long delta_B = (long)e_candB - (long)e_current;

    printf("=== Симуляція рішень EAS (C) ===\n");
    printf("Поточне споживання системи: %lu мВт\n", e_current);
    printf("Варіант А (на LITTLE): Споживання = %lu мВт, ΔE = %+ld мВт\n", e_candA, delta_A);
    printf("Варіант Б (на big):    Споживання = %lu мВт, ΔE = %+ld мВт\n", e_candB, delta_B);

    if (delta_A < delta_B) {
        printf("Висновок: Призначити задачу на ядро LITTLE (заощадження %ld мВт)\n", delta_B - delta_A);
    } else {
        printf("Висновок: Призначити задачу на ядро big (заощадження %ld мВт)\n", delta_A - delta_B);
    }

    return 0;
}
```
```cpp
// eas_simulator.cpp — Ідіоматична реалізація мовою C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <numeric>
#include <cstdint>

constexpr std::uint32_t SCHED_CAPACITY_SCALE = 1024;

struct OppEntry {
    std::uint32_t frequency_khz;
    std::uint32_t power_mw;
    std::uint32_t performance;
};

class PerfDomain {
public:
    PerfDomain(std::string_view name, std::uint32_t capacity_orig, std::vector<OppEntry> opps)
        : name_(name), capacity_orig_(capacity_orig), opps_(std::move(opps)) {}

    [[nodiscard]] std::uint32_t calculate_power(std::uint32_t util_request) const {
        if (util_request == 0) {
            return 0;
        }
        const std::uint32_t req = std::min((util_request * 125) / 100, capacity_orig_);

        auto it = std::find_if(opps_.begin(), opps_.end(), [req](const OppEntry& opp) {
            return opp.performance >= req;
        });

        if (it != opps_.end()) {
            return it->power_mw;
        }
        return opps_.back().power_mw;
    }

    [[nodiscard]] std::string_view name() const noexcept { return name_; }

private:
    std::string name_;
    std::uint32_t capacity_orig_;
    std::vector<OppEntry> opps_;
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <util_little> <util_big> <task_util>\n";
        return 1;
    }

    const std::uint32_t util_little = std::stoul(argv[1]);
    const std::uint32_t util_big = std::stoul(argv[2]);
    const std::uint32_t task_util = std::stoul(argv[3]);

    const PerfDomain little_domain{"LITTLE Cluster", 400, {
        { 300000,  45, 100 },
        { 600000,  95, 200 },
        { 1200000, 210, 400 }
    }};

    const PerfDomain big_domain{"big Cluster", 1024, {
        { 800000,  450, 500 },
        { 1500000, 900, 800 },
        { 2000000, 1500, 1024 }
    }};

    const std::uint32_t e_current = little_domain.calculate_power(util_little) + 
                                    big_domain.calculate_power(util_big);

    const std::uint32_t e_candA = little_domain.calculate_power(util_little + task_util) + 
                                  big_domain.calculate_power(util_big);
    const std::int64_t delta_A = static_cast<std::int64_t>(e_candA) - static_cast<std::int64_t>(e_current);

    const std::uint32_t e_candB = little_domain.calculate_power(util_little) + 
                                  big_domain.calculate_power(util_big + task_util);
    const std::int64_t delta_B = static_cast<std::int64_t>(e_candB) - static_cast<std::int64_t>(e_current);

    std::cout << "=== Симуляція рішень EAS (C++20) ===\n";
    std::cout << "Поточне споживання системи: " << e_current << " мВт\n";
    std::cout << "Варіант А (на LITTLE): Споживання = " << e_candA << " мВт, ΔE = " << delta_A << " мВт\n";
    std::cout << "Варіант Б (на big):    Споживання = " << e_candB << " мВт, ΔE = " << delta_B << " мВт\n";

    if (delta_A < delta_B) {
        std::cout << "Висновок: Призначити задачу на ядро LITTLE (заощадження " << (delta_B - delta_A) << " мВт)\n";
    } else {
        std::cout << "Висновок: Призначити задачу на ядро big (заощадження " << (delta_A - delta_B) << " мВт)\n";
    }

    return 0;
}
```
:::

## 4. Інструкція зі збірки, тестування та інтерпретації результатів

Компіляція утиліти виконується за допомогою стандартних компіляторів `gcc` та `g++`:

```bash
# Збірка C-реалізації
$ gcc -O2 -Wall -Wextra eas_simulator.c -o eas_sim_c

# Збірка C++20-реалізації
$ g++ -O2 -Wall -Wextra -std=c++20 eas_simulator.cpp -o eas_sim_cpp
```

### Сценарій 1: Легка фонова задача (`task_util = 150`)

Розглянемо виклики симулятора для випадку, коли кластер LITTLE завантажено на `100`, кластер big спить (`0`), а нова задача вимагає `150` одиниць навантаження:

```bash
$ ./eas_sim_cpp 100 0 150
=== Симуляція рішень EAS (C++20) ===
Поточне споживання системи: 95 мВт
Варіант А (на LITTLE): Споживання = 210 мВт, ΔE = 115 мВт
Варіант Б (на big):    Споживання = 545 мВт, ΔE = 450 мВт
Висновок: Призначити задачу на ядро LITTLE (заощадження 335 мВт)
```

**Детальний аналіз:** навантаження `100` із запасом 1.25 уже вимагає від LITTLE 600 МГц, тому вихідне споживання системи — 95 мВт. У Варіанті А додавання задачі піднімає кластер LITTLE до 1.2 ГГц (споживання зростає з 95 мВт до 210 мВт, `ΔE = +115 мВт`). У Варіанті Б ядро big мусить ввімкнутися на мінімальній частоті 800 МГц (споживання 450 мВт), що разом із незмінним LITTLE дає 545 мВт (`ΔE = +450 мВт`). Симулятор обирає ядро LITTLE, заощаджуючи 335 мВт.

### Сценарій 2: Важка інтерактивна задача (`task_util = 350`)

Розглянемо випадок, коли на LITTLE-кластері вже є навантаження `200`, і пробуджується важка задача `350`:

```bash
$ ./eas_sim_cpp 200 0 350
=== Симуляція рішень EAS (C++20) ===
Поточне споживання системи: 210 мВт
Варіант А (на LITTLE): Споживання = 210 мВт, ΔE = 0 мВт
Варіант Б (на big):    Споживання = 660 мВт, ΔE = 450 мВт
Висновок: Призначити задачу на ядро LITTLE (заощадження 450 мВт)
```

Саме тут видно межу спрощеної моделі. Кластер LITTLE уже за навантаження `200` сидить на верхньому OPP 1.2 ГГц, тому задача `350` не піднімає його потужність узагалі: `ΔE_A = 0`, і симулятор беззастережно лишає задачу на LITTLE. Насправді сумарні `550` перевищують місткість кластера `400` — справжнє ядро оголосило б чергу перевантаженою (over-utilized), обійшло б енергетичні розрахунки й перекинуло задачу на big. Симулятор такої перевірки не робить: він лише обмежує запит стелею `capacity_orig` і бере найвищий OPP.

## 5. Розширення симулятора для роботи з реальними даними ftrace

У реальних виробничих умовах системні інженери розширюють подібні симулятори для парсингу бінарних трас `ftrace` або логів `trace-cmd`.

Для цього розбирають рядки події `sched_energy_diff` — вона є у вендорських (Android) ядрах; у мейнлайні відповідні точки `sched_compute_energy_tp` і `sched_overutilized_tp` оголошені як «голі» tracepoints, тож видно їх не через tracefs, а лише з BPF-програми чи модуля ядра:

```bash
# Приклад читання траси в реальному часі через події tracefs
$ cat /sys/kernel/debug/tracing/trace_pipe | grep sched_energy_diff
```

Отримані значення `task_util`, `src_cpu`, `dst_cpu` та `nrg_diff` подаються у симулятор для порівняння математичного прогнозу Energy Model з фактичними рішеннями, прийнятими ядром Linux. Це дозволяє здійснювати калібрування таблиць OPP у прошивках пристроїв.

Крім того, аналізатор може враховувати значення `uclamp.min` та `uclamp.max`, модифікуючи змінну `task_util` перед передачею у функцію обчислення потужності домену, що відтворює реальну поведінку планувальника в операційній системі Android.

При використанні eBPF-інструментів (таких як `bpftrace` чи `BCC`) логіку цього симулятора можна вбудовувати безпосередньо у ядра системи для проведення автономного профайлінгу енергоспоживання у виробничих середовищах.

## 6. Інтеграція з профайлером Linux perf

Для автоматизованого тестування точності моделювання симулятор може викликатися безпосередньо з утиліти `perf`:

```bash
# Запуск симулятора під моніторингом подій планувальника (ядро з цими вендорськими подіями)
$ perf stat -e sched:sched_energy_diff -e sched:sched_overutilized ./eas_sim_cpp 100 0 150
```

Це дозволяє порівнювати віртуальні розрахунки утиліти з реальними апаратними лічильниками енергії (наприклад, ARM Energy Trace або RAPL на x86) і проводити динамічну підгонку коефіцієнтів споживання.
