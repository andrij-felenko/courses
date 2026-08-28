# ⚙️ Метрологічний рушій оцінювання невизначеності на C та C++

У вбудованих системах точного вимірювання — від промислових вагових терміналів і систем обліку газу до давачів тиску в авіоніці та медичних моніторах — недостатньо видавати сире усереднене число з АЦП. Автоматика та оператор мають знати гарантовані межі довіри: який внесок дає випадковий шум вибірки, скільки додає крок квантування перетворювача та як на результат впливає паспортна похибка дільника, термодрейф чи опорне джерело напруги. Цей модуль реалізує повний цикл обчислення стандартної та розширеної невизначеності за стандартом ISO/IEC Guide 98-3 (GUM) прямо на мікроконтролері або промисловому шлюзі без динамічного виділення пам'яті.

### Чому наївна статистика ламається на мікроконтролерах

Більшість програмістів вбудованих систем для оцінки розкиду вибірки використовують класичну формулу дисперсії зі шкільного підручника: `s² = (∑ x² − (∑ x)² / N) / (N − 1)`. У математиці на папері цей вираз тотожний сумі квадратів відхилень `∑ (x_i − x̄)²`. Проте в арифметиці з рухомою комою (особливо при використанні 32-розрядних чисел `float`, характерних для апаратних блоків FPU мікроконтролерів Cortex-M4F або ESP32) він призводить до фатального явища — **катастрофічного скасування розрядів** (*catastrophic cancellation*).

Уявімо вимірювання напруги прецизійного сенсора з постійним зміщенням 10.000 В і випадковим шумом близько 1 мВ. Числа `x_i` мають вигляд `10.001, 9.999, 10.002...`. Сума їхніх квадратів `∑ x²` для вибірки з 1000 відліків становить близько `100 000.0`, а квадрат суми `(∑ x)² / N` — також `100 000.0`. Формат `float` (IEEE 754) має лише 24 біти двійкової мантиси, що забезпечує приблизно 7.2 десяткових знаків точності. Віднімаючи два гігантські числа `100 000.0`, різниця між якими криється у восьмому чи дев'ятому знаку, програма повністю втрачає корисну інформацію і замість справжньої дисперсії отримує нуль або навіть від'ємне число.

Щоб усунути цю проблему без збереження всього масиву вибірок у пам'яті (яка в мікроконтролерах дуже обмежена), у модулі застосовано **алгоритм Велфорда** (B. P. Welford, 1962). Він обчислює середнє та суму квадратів різниць рекурентно у потоковому режимі `O(1)` за часом та пам'яттю, оперуючи виключно малим приростом `delta = x_k − mean_{k-1}`.

### Архітектура метрологічного обробника

Розрахунок складається з чотирьох узгоджених етапів:

1. **Однопрохідний статистичний аналіз (Тип A)**: накопичення потоку відліків АЦП за алгоритмом Велфорда, обчислення вибіркового середнього, незміщеної дисперсії з поправкою Бесселя та стандартної невизначеності середнього `u_A = s / √N`.
2. **Перетворення апріорних допусків (Тип B)**: уніфікований розрахунок стандартної невизначеності для кроку квантування АЦП, паспортного класу точності приладу, допуску резисторів та температурного дрейфу за прямокутним, трикутним, нормальним або U-подібним розподілами ймовірностей.
3. **Зведення в спільний бюджет та закон поширення**: обчислення сумарної стандартної невизначеності `u_c` за методом кореня із суми зважених квадратів `u_c = √( ∑ (c_i · u_i)² )`, де `c_i` — коефіцієнти чутливості (частинні похідні моделі вимірювання).
4. **Оцінка ефективних ступенів вільності за Велчем-Саттерзвейтом**: визначення сумарного числа ступенів вільності `ν_eff` комбінованого бюджету для вибору коректного коефіцієнта охоплення Стьюдента або нормального розподілу `k = 2.0` (для рівня довіри `P = 95.45%`).

Нижче наведено модулі на мовах C та C++, оптимізовані для роботи в середовищі мікроконтролерів (без використання `malloc` чи винятків у C, з повною підтримкою стандартних типів даних та детермінованим часом виконання).

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define METROLOGY_MAX_COMPONENTS 8

/* Типи апріорних розподілів ймовірностей для оцінювання за Типом B */
typedef enum {
    DISTRIBUTION_RECTANGULAR, /* Прямокутний: u = a / sqrt(3) */
    DISTRIBUTION_TRIANGULAR,  /* Трикутний:   u = a / sqrt(6) */
    DISTRIBUTION_NORMAL_K2,   /* Нормальний 95.45%: u = U / 2.0 */
    DISTRIBUTION_NORMAL_K3,   /* Нормальний 99.73%: u = U / 3.0 */
    DISTRIBUTION_U_SHAPED     /* U-подібний (гармонічний): u = a / sqrt(2) */
} pdf_type_t;

/* Окреме джерело невизначеності в бюджеті */
typedef struct {
    const char *name;
    double std_uncertainty;    /* Стандартна невизначеність u(x_i) */
    double sensitivity;        /* Коефіцієнт чутливості c_i = df/dx_i */
    double degrees_of_freedom; /* Ступені вільності (для типу B часто INFINITY) */
} uncertainty_item_t;

/* Бюджет невизначеності вимірювального каналу */
typedef struct {
    uncertainty_item_t items[METROLOGY_MAX_COMPONENTS];
    size_t count;
} uncertainty_budget_t;

/* Однопрохідний накопичувач Велфорда для оцінки за Типом A */
typedef struct {
    uint32_t count;
    double mean;
    double m2; /* Сума квадратів відхилень від поточного середнього */
} welford_acc_t;

/* Результат метрологічного звіту */
typedef struct {
    double value;           /* Оцінка вимірюваної величини */
    double u_type_a;        /* Стандартна невизначеність типу A (s / sqrt(N)) */
    double u_combined;      /* Сумарна стандартна невизначеність u_c */
    double expanded_u;      /* Розширена невизначеність U = k * u_c */
    double eff_dof;         /* Ефективні ступені вільності (Велч-Саттерзвейт) */
    double coverage_factor; /* Застосований коефіцієнт охоплення k */
} metrology_report_t;

/* Ініціалізація накопичувача вибірки */
void welford_init(welford_acc_t *acc) {
    acc->count = 0;
    acc->mean = 0.0;
    acc->m2 = 0.0;
}

/* Додавання нового відліку за алгоритмом Велфорда */
void welford_update(welford_acc_t *acc, double x) {
    acc->count++;
    double delta = x - acc->mean;
    acc->mean += delta / (double)acc->count;
    double delta2 = x - acc->mean;
    acc->m2 += delta * delta2;
}

/* Обчислення статистичної невизначеності типу A: s / sqrt(N) */
bool welford_get_type_a(const welford_acc_t *acc, double *mean_out, double *u_a_out) {
    if (acc->count < 2) {
        return false;
    }
    *mean_out = acc->mean;
    double variance = acc->m2 / (double)(acc->count - 1);
    double s = sqrt(variance);
    *u_a_out = s / sqrt((double)acc->count);
    return true;
}

/* Розрахунок стандартної невизначеності за Типом B з напівширини a */
double eval_type_b(double half_width, pdf_type_t dist) {
    switch (dist) {
        case DISTRIBUTION_RECTANGULAR:
            return half_width / sqrt(3.0);
        case DISTRIBUTION_TRIANGULAR:
            return half_width / sqrt(6.0);
        case DISTRIBUTION_NORMAL_K2:
            return half_width / 2.0;
        case DISTRIBUTION_NORMAL_K3:
            return half_width / 3.0;
        case DISTRIBUTION_U_SHAPED:
            return half_width / sqrt(2.0);
        default:
            return half_width / sqrt(3.0);
    }
}

/* Розрахунок невизначеності квантування АЦП для кроку LSB = Vref / 2^bits */
double eval_adc_quantization_unc(double v_ref, uint8_t bits) {
    double lsb = v_ref / (double)(1ULL << bits);
    return lsb / sqrt(12.0); /* Рівномірний розподіл на інтервалі [-LSB/2, +LSB/2] */
}

/* Ініціалізація бюджету */
void budget_init(uncertainty_budget_t *b) {
    b->count = 0;
}

/* Додавання джерела до бюджету */
bool budget_add(uncertainty_budget_t *b, const char *name, double u, double c, double dof) {
    if (b->count >= METROLOGY_MAX_COMPONENTS) {
        return false;
    }
    b->items[b->count].name = name;
    b->items[b->count].std_uncertainty = u;
    b->items[b->count].sensitivity = c;
    b->items[b->count].degrees_of_freedom = dof;
    b->count++;
    return true;
}

/* Зведення бюджету та розрахунок сумарної й розширеної невизначеності */
bool budget_evaluate(const uncertainty_budget_t *b, double meas_val, double k, metrology_report_t *rep) {
    if (b->count == 0) {
        return false;
    }

    double sum_sq = 0.0;
    double ws_denom = 0.0;

    for (size_t i = 0; i < b->count; ++i) {
        double c_u = b->items[i].sensitivity * b->items[i].std_uncertainty;
        double contribution_sq = c_u * c_u;
        sum_sq += contribution_sq;

        if (isfinite(b->items[i].degrees_of_freedom) && b->items[i].degrees_of_freedom > 0.0) {
            double c_u_quad = contribution_sq * contribution_sq;
            ws_denom += c_u_quad / b->items[i].degrees_of_freedom;
        }
    }

    rep->value = meas_val;
    rep->u_combined = sqrt(sum_sq);
    rep->coverage_factor = k;
    rep->expanded_u = k * rep->u_combined;

    /* Формула Велча-Саттерзвейта для ефективних ступенів вільності */
    if (ws_denom > 1e-15) {
        double u_c_quad = sum_sq * sum_sq;
        rep->eff_dof = u_c_quad / ws_denom;
    } else {
        rep->eff_dof = INFINITY;
    }

    return true;
}

int main(void) {
    /* Демонстрація: Вимірювання тиску тензометричним давачем з 16-бітним АЦП */
    welford_acc_t adc_sampler;
    welford_init(&adc_sampler);

    /* 16 послідовних вибірок тиску в барах */
    const double raw_samples[16] = {
        10.042, 10.038, 10.045, 10.040, 10.048, 10.037, 10.041, 10.044,
        10.039, 10.046, 10.040, 10.043, 10.036, 10.047, 10.041, 10.042
    };

    for (size_t i = 0; i < 16; ++i) {
        welford_update(&adc_sampler, raw_samples[i]);
    }

    double mean_pressure = 0.0;
    double u_a = 0.0;
    welford_get_type_a(&adc_sampler, &mean_pressure, &u_a);

    /* Формування бюджету невизначеності */
    uncertainty_budget_t budget;
    budget_init(&budget);

    /* 1. Статистичний шум вибірки (Тип A) */
    budget_add(&budget, "Випадковий шум вибірки", u_a, 1.0, 16 - 1);

    /* 2. Квантування АЦП: діапазон 20 бар на 16 біт (Тип B) */
    double u_quant = (20.0 / 65536.0) / sqrt(12.0);
    budget_add(&budget, "Шум квантування АЦП", u_quant, 1.0, INFINITY);

    /* 3. Паспортна похибка калібрування давача: +/-0.05 бар (прямокутний) */
    double u_cal = eval_type_b(0.05, DISTRIBUTION_RECTANGULAR);
    budget_add(&budget, "Калібрування давача", u_cal, 1.0, INFINITY);

    /* 4. Температурний дрейф нуля: +/-0.02 бар (трикутний) */
    double u_temp = eval_type_b(0.02, DISTRIBUTION_TRIANGULAR);
    budget_add(&budget, "Температурний дрейф", u_temp, 1.0, INFINITY);

    metrology_report_t report;
    budget_evaluate(&budget, mean_pressure, 2.0, &report);

    printf("=== Метрологічний звіт вимірювання тиску ===\n");
    printf("Оцінка значення (середнє): %.4f бар\n", report.value);
    printf("Статистична невизначеність u_A: %.5f бар\n", u_a);
    printf("Сумарна невизначеність u_c:     %.5f бар\n", report.u_combined);
    printf("Розширена невизначеність U(k=2): %.5f бар (P = 95.45%%)\n", report.expanded_u);
    printf("Ефективні ступені вільності nu:  %.1f\n", report.eff_dof);
    printf("Результат для запису: P = (%.4f +/- %.4f) бар, k=2\n",
           report.value, report.expanded_u);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <cmath>
#include <numbers>
#include <span>
#include <numeric>
#include <optional>
#include <iomanip>

namespace metrology {

enum class Distribution {
    Rectangular, // u = a / sqrt(3)
    Triangular,  // u = a / sqrt(6)
    NormalK2,    // u = U / 2.0
    NormalK3,    // u = U / 3.0
    UShaped      // u = a / sqrt(2)
};

struct UncertaintyItem {
    std::string_view name;
    double std_uncertainty;
    double sensitivity{1.0};
    double degrees_of_freedom{std::numeric_limits<double>::infinity()};

    [[nodiscard]] constexpr double contribution() const noexcept {
        return sensitivity * std_uncertainty;
    }
};

struct MetrologyReport {
    double value;
    double u_combined;
    double expanded_u;
    double eff_dof;
    double coverage_factor;
};

// Чисельно стабільний акумулятор Велфорда для розрахунку типу A
class WelfordAccumulator {
public:
    void update(double x) noexcept {
        ++count_;
        double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        double delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    void update(std::span<const double> samples) noexcept {
        for (double s : samples) {
            update(s);
        }
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }
    [[nodiscard]] double mean() const noexcept { return mean_; }

    [[nodiscard]] std::optional<double> sample_variance() const noexcept {
        if (count_ < 2) return std::nullopt;
        return m2_ / static_cast<double>(count_ - 1);
    }

    [[nodiscard]] std::optional<double> standard_error_of_mean() const noexcept {
        auto var = sample_variance();
        if (!var) return std::nullopt;
        return std::sqrt(*var / static_cast<double>(count_));
    }

private:
    std::size_t count_{0};
    double mean_{0.0};
    double m2_{0.0};
};

// Оцінка стандартної невизначеності за Типом B
[[nodiscard]] constexpr double eval_type_b(double half_width, Distribution dist) noexcept {
    switch (dist) {
        case Distribution::Rectangular:
            return half_width / std::numbers::sqrt3;
        case Distribution::Triangular:
            return half_width / 2.449489742783178; // sqrt(6)
        case Distribution::NormalK2:
            return half_width / 2.0;
        case Distribution::NormalK3:
            return half_width / 3.0;
        case Distribution::UShaped:
            return half_width / std::numbers::sqrt2;
    }
    return half_width / std::numbers::sqrt3;
}

// Розрахунок невизначеності квантування АЦП
[[nodiscard]] constexpr double eval_adc_quantization(double v_ref, uint8_t bits) noexcept {
    double lsb = v_ref / static_cast<double>(1ULL << bits);
    return lsb / 3.4641016151377544; // sqrt(12)
}

// Калькулятор бюджету невизначеності
class UncertaintyBudget {
public:
    void add_item(UncertaintyItem item) {
        items_.push_back(item);
    }

    [[nodiscard]] std::optional<MetrologyReport> evaluate(double meas_val, double k = 2.0) const {
        if (items_.empty()) return std::nullopt;

        double sum_sq = 0.0;
        double ws_denom = 0.0;

        for (const auto& item : items_) {
            double c_u = item.contribution();
            double cont_sq = c_u * c_u;
            sum_sq += cont_sq;

            if (std::isfinite(item.degrees_of_freedom) && item.degrees_of_freedom > 0.0) {
                double cont_quad = cont_sq * cont_sq;
                ws_denom += cont_quad / item.degrees_of_freedom;
            }
        }

        double u_c = std::sqrt(sum_sq);
        double eff_dof = (ws_denom > 1e-15) ? (sum_sq * sum_sq) / ws_denom : std::numeric_limits<double>::infinity();

        return MetrologyReport{
            .value = meas_val,
            .u_combined = u_c,
            .expanded_u = k * u_c,
            .eff_dof = eff_dof,
            .coverage_factor = k
        };
    }

    [[nodiscard]] const std::vector<UncertaintyItem>& items() const noexcept {
        return items_;
    }

private:
    std::vector<UncertaintyItem> items_;
};

} // namespace metrology

int main() {
    using namespace metrology;

    WelfordAccumulator sampler;
    const std::vector<double> samples = {
        10.042, 10.038, 10.045, 10.040, 10.048, 10.037, 10.041, 10.044,
        10.039, 10.046, 10.040, 10.043, 10.036, 10.047, 10.041, 10.042
    };
    sampler.update(samples);

    auto u_a = sampler.standard_error_of_mean().value_or(0.0);
    double mean_pressure = sampler.mean();

    UncertaintyBudget budget;
    budget.add_item({"Випадковий шум вибірки", u_a, 1.0, static_cast<double>(samples.size() - 1)});
    budget.add_item({"Шум квантування АЦП", eval_adc_quantization(20.0, 16), 1.0});
    budget.add_item({"Калібрування давача", eval_type_b(0.05, Distribution::Rectangular), 1.0});
    budget.add_item({"Температурний дрейф", eval_type_b(0.02, Distribution::Triangular), 1.0});

    if (auto rep = budget.evaluate(mean_pressure, 2.0)) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "=== Метрологічний звіт вимірювання тиску (C++) ===\n";
        std::cout << "Оцінка значення (середнє): " << rep->value << " бар\n";
        std::cout << "Статистична невизначеність u_A: " << std::setprecision(5) << u_a << " бар\n";
        std::cout << "Сумарна невизначеність u_c:     " << rep->u_combined << " бар\n";
        std::cout << "Розширена невизначеність U(k=2): " << rep->expanded_u << " бар (P = 95.45%)\n";
        std::cout << "Ефективні ступені вільності nu:  " << std::setprecision(1) << rep->eff_dof << "\n";
        std::cout << "Результат для запису: P = (" << std::setprecision(4) << rep->value
                  << " +/- " << rep->expanded_u << ") бар, k=2\n";
    }

    return 0;
}
```
:::

### Практичні підводні камені та оптимізація під мікроконтролери

Під час інтеграції розрахунку невизначеності у реальне вбудоване ПЗ інженери часто припускаються кількох критичних помилок:

1. **Плутанина між середньоквадратичним відхиленням одиничного виміру `s` та невизначеністю середнього `s / √N`:**
   Перше число описує амплітуду шуму самого сенсора чи АЦП, а друге — точність локалізації центра розподілу. Якщо система публікує результат одного миттєвого зчитування, невизначеність становить `s`; якщо публікується результат усереднення `N` зчитувань, у бюджет записують саме `s / √N`.
2. **Сліпе додавання допусків за модулем:**
   Спроба скласти напівширини `a_1 + a_2 + a_3...` замість кореня із суми квадратів відповідає найгіршому теоретичному випадку, коли всі незалежні випадкові та апаратурні похибки одночасно відхиляються на максимум в один бік. Для некорельованих джерел це штучно завищує невизначеність у 2–3 рази і призводить до відхилення цілком придатних виробів на вихідному контролі.
3. **Ігнорування динамічного діапазону FPU:**
   При роботі з числами з плаваючою комою одинарної точності (`float32`) на мікроконтролерах без блоку double-precision FPU всі змінні накопичувача Велфорда слід тримати в `float`, але за умови, що попередньо виконано грубе віднімання базового зміщення (наприклад, `x_norm = x_raw - V_nominal`). Це гарантує, що значення `delta` не втратять біти мантиси при малих флуктуаціях.
4. **Некоректне застосування формули Велча-Саттерзвейта при малій кількості вибірок:**
   Коли статистична вибірка містить лише 3–5 відліків, `ν_A = 2..4`, а внесок типу A становить значну частку сумарного бюджету, ефективні ступені вільності `ν_eff` падають до 3–6. У такому разі коефіцієнт охоплення `k` не можна брати рівним 2.0: t-коефіцієнт Стьюдента для `P = 95%` при `ν = 3` дорівнює `t = 3.18`, що вимагає розширення довірчого інтервалу майже в 1.6 раза.

### Ресурси пам'яті та швидкодія в реальному часі

Розроблений C-модуль не потребує динамічного розподілу пам'яті в купі (відсутні виклики `malloc` та `free`), що виключає фрагментацію RAM та недетерміновані затримки при роботі під керуванням операційних систем реального часу (FreeRTOS, Zephyr). 

- **Споживання оперативної пам'яті (RAM):**
  - Структура накопичувача `welford_acc_t` займає лише 24 байти (один `uint32_t` лічильник і два 64-розрядні числа `double`).
  - Структура бюджету `uncertainty_budget_t` на 8 компонентів займає близько 264 байтів.
  - Повний метрологічний стан каналу разом зі звітом вільно вміщується у 320 байтів стеку.
- **Обчислювальна складність:**
  - Обробка одного відліку в перериванні АЦП `welford_update()` вимагає лише 2 операцій віднімання, 2 додавання, 1 множення та 1 ділення (близько 15–25 тактів процесора Cortex-M4 з апаратним FPU).
  - Підсумкове зведення бюджету `budget_evaluate()` виконується лише один раз у кінці вимірювального циклу й потребує одного виклику `sqrt()`, займаючи менше 2 мкс на тактовій частоті 80 МГц.

