# ⚙️ Автоматизований аналізатор виробничої генеалогії та польових відмов

Коли в сервісні центри надходять десятки несправних друкованих плат із масиву в 20 000 виготовлених пристроїв, ручне зіставлення серійних номерів за таблицями Excel перетворюється на багатотижневий кошмар. Автоматизований аналізатор генеалогії завантажує журнал виробництва (зв'язок серійного номера плати з кодами партій кожного встановленого чіпа, лінією монтажу та датою паяння), зіставляє його зі списком рекламацій і за мілісекунди обчислює статистичні метрики для кожної позиції специфікації матеріалів (BOM), виявляючи справжнє джерело браку.

## Призначення та архітектура аналізатора

У серійному виробництві вбудованої електроніки дані про кожну виготовлену одиницю розпорошені між кількома незалежними інформаційними контурами фабрики:
1. **Система керування виробництвом (MES / ERP):** фіксує рух мультипанелей конвеєром, містить логи сканування 2D DataMatrix на вході кожного автомата, ідентифікатор SMT-лінії, номер виробничої зміни, температуру і відносну вологість у приміщенні, а також унікальний ID термопрофілю печі оплавлення.
2. **Логи живильників монтажних автоматів (Pick & Place Feeder Logs):** реєструють кожну заміну котушки та пов'язують позиційний десігнатор на платі (`C12`, `U4`, `R28`) з унікальним штрихкодом котушки (`Reel UID`), номером партії постачальника (`Lot Code`) та кодом дати виготовлення чіпа (`Date Code`).
3. **Система реєстрації рекламацій та повернень (CRM / RMA Database):** формує потік звернень від кінцевих користувачів, де фіксується серійний номер виробу, дата звернення, напрацювання в годинах (*Time to Failure — TTF*), умови навколишнього середовища та детальний звіт технічного спеціаліста про характер відмови.

Аналізатор вирішує задачу зворотного інженерного простежування: він зводить ці розрізнені потоки даних в єдину аналітичну матрицю, послідовно висуває статистичні гіпотези щодо кожного виробничого фактора та ізолює мінімальний діапазон серійних номерів, що потребує гарантійного відклику.

```
+-----------------------------------+      +---------------------------------+
|  MES & SMT Feeder Logs            |      |  RMA Customer Return Database   |
|  (Serial ↔ DateCodes ↔ SMT Line)  |      |  (Failed Serials + Symptoms)    |
+-----------------+-----------------+      +----------------+----------------+
                  |                                         |
                  +--------------------+--------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  Парсер та агрегатор генеалогії   |
                     |  (Memory-mapped Record Index)     |
                     +-----------------+-----------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  Генератор 2x2 матриць            |
                     |  для кожної позиції BOM & процесу |
                     +-----------------+-----------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  Статистичний рушій:              |
                     |  • Odds Ratio + 95% CI            |
                     |  • Log-Gamma точний тест Фішера   |
                     |  • Поправка на множинність тестів |
                     +-----------------+-----------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  Звіт карантину та ізоляції:      |
                     |  • Винний компонент / Reel UID    |
                     |  • Точний список серійних номерів |
                     +-----------------+-----------------+
```

## Алгоритм роботи та чисельна стабільність

Аналізатор реалізує чотири послідовні фази обробки:

1. **Фаза індексації та парсингу:** Завантаження записів виробничих плат у пам'ять. Для кожної плати формується компактна бінарна структура, що містить серійний номер, текстові атрибути вузлів та бітовий прапорець факту польової відмови (`is_failed`).
2. **Фаза підрахунку матриць спряженості:** Для кожного унікального фактора (наприклад, `MCU_DateCode = DC2134` або `MLCC_Lot = L-8921`) сканується весь масив пристроїв та обчислюються чотири базові частоти:
   - `a` — фактор присутній і пристрій відмовив (істинно позитивні);
   - `b` — фактор присутній, але пристрій працює справно (хибно позитивні);
   - `c` — фактор відсутній, але пристрій відмовив (фоновий брак або альтернативна причина);
   - `d` — фактор відсутній і пристрій працює справно (істинно негативні).
3. **Фаза статистичної фільтрації:** Обчислення відношення шансів (`OR`) та логарифмічного точного тесту Фішера. Пряме обчислення факторіалів через рекурсію або цикл призводить до переповнення на числах понад `170!`, тому алгоритм використовує функцію `lgamma()`. Для знаходження двостороннього `p-value` алгоритм підсумовує гіпергеометричні ймовірності всіх конфігурацій таблиці, ймовірність яких не перевищує ймовірність спостережуваного результату.
4. **Фаза формування карантинного списку:** Якщо для певного фактора виконується умова `p < 1e-5` та `OR > 10.0`, програма автоматично генерує перелік усіх серійних номерів пристроїв, що містять цей фактор, і експортує його для складського карантину.

## Реалізація аналізатора мовами C та C++

Нижче наведено повні та готові до компіляції реалізації аналізатора двома системними мовами програмування.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define MAX_RECORDS 25000
#define MAX_STR_LEN 64

typedef struct {
    char serial[MAX_STR_LEN];
    char smt_line[MAX_STR_LEN];
    char mcu_datecode[MAX_STR_LEN];
    char ldo_reel[MAX_STR_LEN];
    char mlcc_lot[MAX_STR_LEN];
    bool is_failed;
} BoardRecord;

typedef struct {
    char attr_name[MAX_STR_LEN];
    char attr_value[MAX_STR_LEN];
    int a; // фактор є + відмова
    int b; // фактор є + справний
    int c; // фактора нема + відмова
    int d; // фактора нема + справний
    double odds_ratio;
    double ci_low;
    double ci_high;
    double p_value;
} ContingencyResult;

static double log_factorial(int n) {
    return lgamma((double)(n + 1));
}

static double fisher_exact_2x2(int a, int b, int c, int d) {
    int n1 = a + b;
    int n0 = c + d;
    int m1 = a + c;
    int m0 = b + d;
    int total = n1 + n0;

    double log_hyper_denom = log_factorial(n1) + log_factorial(n0) +
                             log_factorial(m1) + log_factorial(m0) -
                             log_factorial(total);

    double log_p_observed = log_hyper_denom - (log_factorial(a) + log_factorial(b) +
                                              log_factorial(c) + log_factorial(d));
    double p_observed = exp(log_p_observed);

    int min_a = (m1 - n0 > 0) ? m1 - n0 : 0;
    int max_a = (n1 < m1) ? n1 : m1;

    double p_total = 0.0;
    for (int x = min_a; x <= max_a; ++x) {
        int cur_b = n1 - x;
        int cur_c = m1 - x;
        int cur_d = n0 - cur_c;

        double log_p_cur = log_hyper_denom - (log_factorial(x) + log_factorial(cur_b) +
                                              log_factorial(cur_c) + log_factorial(cur_d));
        double p_cur = exp(log_p_cur);

        if (p_cur <= p_observed * (1.0 + 1e-9)) {
            p_total += p_cur;
        }
    }
    return (p_total > 1.0) ? 1.0 : p_total;
}

static void calculate_metrics(ContingencyResult *res) {
    double a = res->a;
    double b = res->b;
    double c = res->c;
    double d = res->d;

    // Корекція Холдейна-Енскомба при нульових клітинках
    if (a == 0 || b == 0 || c == 0 || d == 0) {
        a += 0.5; b += 0.5; c += 0.5; d += 0.5;
    }

    res->odds_ratio = (a * d) / (b * c);
    double se_ln_or = sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d);
    double ln_or = log(res->odds_ratio);

    res->ci_low = exp(ln_or - 1.96 * se_ln_or);
    res->ci_high = exp(ln_or + 1.96 * se_ln_or);
    res->p_value = fisher_exact_2x2(res->a, res->b, res->c, res->d);
}

int main(void) {
    printf("=== Аналізатор виробничої генеалогії PCBA (C99) ===\n");

    int total_records = 20000;
    BoardRecord *records = calloc((size_t)total_records, sizeof(BoardRecord));
    if (!records) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    // Генерація виробничого випуску 20 000 плат
    for (int i = 0; i < total_records; ++i) {
        snprintf(records[i].serial, MAX_STR_LEN, "SN%05d", i + 1);
        snprintf(records[i].smt_line, MAX_STR_LEN, (i % 2 == 0) ? "Line-1" : "Line-2");
        snprintf(records[i].mcu_datecode, MAX_STR_LEN, (i < 10000) ? "DC2130" : "DC2134");
        snprintf(records[i].ldo_reel, MAX_STR_LEN, (i < 15000) ? "R-101" : "R-102");

        // Дефектний лот конденсаторів встановлений на платах SN14000..SN14999 (1000 шт)
        if (i >= 14000 && i < 15000) {
            strncpy(records[i].mlcc_lot, "L-8921", MAX_STR_LEN);
            // 1.8% відмов у дефектному лоті (18 штук)
            records[i].is_failed = (i % 55 == 0 && i < 14990);
        } else {
            strncpy(records[i].mlcc_lot, "L-4410", MAX_STR_LEN);
            // Фоновий брак у решті партій: 2 штуки на 19 000 плат (0.01%)
            records[i].is_failed = (i == 2500 || i == 8700);
        }
    }

    // Перевірка підозрілого атрибута MLCC Lot = L-8921
    ContingencyResult test_mlcc = {0};
    strncpy(test_mlcc.attr_name, "MLCC_Lot", MAX_STR_LEN);
    strncpy(test_mlcc.attr_value, "L-8921", MAX_STR_LEN);

    for (int i = 0; i < total_records; ++i) {
        bool match = (strcmp(records[i].mlcc_lot, "L-8921") == 0);
        if (match && records[i].is_failed) test_mlcc.a++;
        else if (match && !records[i].is_failed) test_mlcc.b++;
        else if (!match && records[i].is_failed) test_mlcc.c++;
        else if (!match && !records[i].is_failed) test_mlcc.d++;
    }

    calculate_metrics(&test_mlcc);

    printf("\nРезультати аналізу для [%s = %s]:\n", test_mlcc.attr_name, test_mlcc.attr_value);
    printf("  Клітинки матриці 2x2: a=%d, b=%d, c=%d, d=%d\n",
           test_mlcc.a, test_mlcc.b, test_mlcc.c, test_mlcc.d);
    printf("  Частота браку в групі:   %.3f%%\n", (double)test_mlcc.a / (test_mlcc.a + test_mlcc.b) * 100.0);
    printf("  Частота браку в контролі: %.4f%%\n", (double)test_mlcc.c / (test_mlcc.c + test_mlcc.d) * 100.0);
    printf("  Відношення шансів (OR):   %.2f (95%% CI: [%.2f .. %.2f])\n",
           test_mlcc.odds_ratio, test_mlcc.ci_low, test_mlcc.ci_high);
    printf("  Точний тест Фішера (p):   %.4e\n", test_mlcc.p_value);

    if (test_mlcc.p_value < 1e-5 && test_mlcc.odds_ratio > 10.0) {
        printf("\n[УВАГА] Виявлено статистично достовірне джерело браку!\n");
        printf("Ізоляція партії: вилучити зі складів плати з атрибутом %s=%s\n",
               test_mlcc.attr_name, test_mlcc.attr_value);
        printf("Діапазон серійних номерів для карантину: SN14001 .. SN15000\n");
    }

    free(records);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <cmath>
#include <iomanip>
#include <format>
#include <optional>
#include <span>

struct BoardRecord {
    std::string serial;
    std::string smt_line;
    std::string mcu_datecode;
    std::string ldo_reel;
    std::string mlcc_lot;
    bool is_failed{false};
};

struct ContingencyStats {
    int a{0}; // фактор є + відмова
    int b{0}; // фактор є + справний
    int c{0}; // фактора нема + відмова
    int d{0}; // фактора нема + справний
    double odds_ratio{0.0};
    double ci_low{0.0};
    double ci_high{0.0};
    double p_value{1.0};
};

class TraceabilityAnalyzer {
public:
    static double log_factorial(int n) noexcept {
        return std::lgamma(static_cast<double>(n + 1));
    }

    static double calculate_fisher_p_value(int a, int b, int c, int d) noexcept {
        const int n1 = a + b;
        const int n0 = c + d;
        const int m1 = a + c;
        const int m0 = b + d;
        const int total = n1 + n0;

        const double log_hyper_denom = log_factorial(n1) + log_factorial(n0) +
                                      log_factorial(m1) + log_factorial(m0) -
                                      log_factorial(total);

        const double log_p_obs = log_hyper_denom - (log_factorial(a) + log_factorial(b) +
                                                   log_factorial(c) + log_factorial(d));
        const double p_obs = std::exp(log_p_obs);

        const int min_a = std::max(0, m1 - n0);
        const int max_a = std::min(n1, m1);

        double p_total = 0.0;
        for (int x = min_a; x <= max_a; ++x) {
            const int cur_b = n1 - x;
            const int cur_c = m1 - x;
            const int cur_d = n0 - cur_c;

            const double log_p_cur = log_hyper_denom - (log_factorial(x) + log_factorial(cur_b) +
                                                       log_factorial(cur_c) + log_factorial(cur_d));
            const double p_cur = std::exp(log_p_cur);

            if (p_cur <= p_obs * (1.0 + 1e-9)) {
                p_total += p_cur;
            }
        }
        return std::min(1.0, p_total);
    }

    static ContingencyStats analyze_attribute(std::span<const BoardRecord> dataset,
                                             auto attribute_selector,
                                             std::string_view target_value) {
        ContingencyStats stats;

        for (const auto& record : dataset) {
            const bool match = (attribute_selector(record) == target_value);
            if (match && record.is_failed) ++stats.a;
            else if (match && !record.is_failed) ++stats.b;
            else if (!match && record.is_failed) ++stats.c;
            else if (!match && !record.is_failed) ++stats.d;
        }

        double a = stats.a, b = stats.b, c = stats.c, d = stats.d;
        if (a == 0 || b == 0 || c == 0 || d == 0) {
            a += 0.5; b += 0.5; c += 0.5; d += 0.5;
        }

        stats.odds_ratio = (a * d) / (b * c);
        const double se_ln_or = std::sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d);
        const double ln_or = std::log(stats.odds_ratio);

        stats.ci_low = std::exp(ln_or - 1.96 * se_ln_or);
        stats.ci_high = std::exp(ln_or + 1.96 * se_ln_or);
        stats.p_value = calculate_fisher_p_value(stats.a, stats.b, stats.c, stats.d);

        return stats;
    }
};

int main() {
    std::cout << "=== Аналізатор виробничої генеалогії PCBA (C++20) ===\n\n";

    constexpr int kTotalBoards = 20000;
    std::vector<BoardRecord> records;
    records.reserve(kTotalBoards);

    for (int i = 0; i < kTotalBoards; ++i) {
        BoardRecord rec{
            .serial = std::format("SN{:05d}", i + 1),
            .smt_line = (i % 2 == 0) ? "Line-1" : "Line-2",
            .mcu_datecode = (i < 10000) ? "DC2130" : "DC2134",
            .ldo_reel = (i < 15000) ? "R-101" : "R-102",
            .mlcc_lot = (i >= 14000 && i < 15000) ? "L-8921" : "L-4410",
            .is_failed = false
        };

        if (i >= 14000 && i < 15000) {
            rec.is_failed = (i % 55 == 0 && i < 14990); // 18 відмов
        } else {
            rec.is_failed = (i == 2500 || i == 8700);    // 2 відмови
        }
        records.push_back(std::move(rec));
    }

    const auto stats = TraceabilityAnalyzer::analyze_attribute(
        records,
        [](const BoardRecord& r) noexcept -> std::string_view { return r.mlcc_lot; },
        "L-8921"
    );

    std::cout << std::format("Результати аналізу для [MLCC Lot = L-8921]:\n");
    std::cout << std::format("  Клітинки таблиці 2x2: a={}, b={}, c={}, d={}\n",
                             stats.a, stats.b, stats.c, stats.d);
    std::cout << std::format("  Частота відмов у партії:   {:.3f}%\n",
                             (static_cast<double>(stats.a) / (stats.a + stats.b)) * 100.0);
    std::cout << std::format("  Частота відмов у контролі: {:.4f}%\n",
                             (static_cast<double>(stats.c) / (stats.c + stats.d)) * 100.0);
    std::cout << std::format("  Відношення шансів (OR):   {:.2f} (95% CI: [{:.2f} .. {:.2f}])\n",
                             stats.odds_ratio, stats.ci_low, stats.ci_high);
    std::cout << std::format("  Критерій Фішера (p-value): {:.4e}\n\n", stats.p_value);

    if (stats.p_value < 1e-5 && stats.odds_ratio > 10.0) {
        std::cout << "[УВАГА] Виявлено статистично значущий виробничий дефект!\n";
        std::cout << "Діапазон серійних номерів для карантину: SN14001 .. SN15000 (1000 плат)\n";
    }

    return 0;
}
```
:::

## Інженерні пастки розробки аналізаторів генеалогії

Під час впровадження автоматизованої обробки виробничих даних інженери стикаються з чотирма критичними підводними каменями:

1. **Колізія часткових замін котушок посеред зміни:** Якщо монтажний автомат витратив котушку `Reel #1` о 14:30 і оператор зарядив `Reel #2`, плати, виготовлені на стику, можуть містити компоненти з обох котушок. Програма повинна підтримувати діапазонні мітки часу (*Timestamp Slicing*) з точністю до секунди сканування плати, а не лише номер зміни.
2. **Пастка штучного обнулення знаменника:** При рідкісних дефектах клітинка `c` (відмови в контрольній групі) може дорівнювати нулю. Просте ділення на нуль призведе до нескінченного значення `OR = +inf`. Застосування корекції Холдейна — Енскомба (додавання `0.5` до кожної клітинки) стабілізує розрахунок дисперсії без спотворення висновку.
3. **Хибна кореляція через спарені фактори (Confounding):** Якщо на лінії SMT-1 завжди монтували процесори `DC2130`, а на лінії SMT-2 — `DC2134`, чистий однофакторний аналіз покаже високу кореляцію як для лінії, так і для чіпа. Для розділення факторів алгоритм повинен виконувати стратифікований аналіз за критерієм Мантеля — Гензеля (*Cochran-Mantel-Haenszel test*).
4. **Склейка стрічок (Reel Splicing):** Коли оператор з'єднує кінець старої котушки з новою спеціальною клейкою стрічкою зі штифтами (*Splice Tape*), у зоні переходу 10–20 компонентів можуть бути не зафіксовані сканером живильника. Без урахування довжини тракту подавача похибка локалізації серійних номерів складатиме кілька десятків пристроїв.
5. **Інтеграція в конвеєр CI/CD надійності:** У зрілих виробничих процесах аналізатор запускається як щонічний сервіс (*Scheduled Job*) у середовищі з базою даних часових рядів (наприклад, ClickHouse або PostgreSQL). При перевищенні порогу ризику `p < 1e-4` сервіс автоматично створює аварійний тікет у системі інцидентів та блокує відвантаження відповідних піддонів на складі готової продукції.
