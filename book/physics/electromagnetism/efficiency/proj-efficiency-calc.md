# ⚙️ Обчислення та оптимізація ККД силових систем

У цій вставці наведено практичну програмну реалізацію алгоритмів для обчислення ККД, аналізу джоулевих втрат та пошуку точок оптимального навантаження електромагнітних пристроїв і силових ліній. Поданий код дозволяє виконувати розрахунок параметрів режиму Якобі, будувати характеристики ефективності трансформаторів та моделювати зниження втрат при підвищенні напруги.

Для забезпечення сумісності з розробкою в галузі системного програмування, вбудованих систем (embedded) та високоефективних обчислень приклад реалізовано мовами C та C++.

## Фізико-математична модель симулятора

Програма моделює два ключові прикладні сценарії:
1. **Аналіз кола постійного струму при дискретному підвищенні опору навантаження `R_L`**: симулятор розраховує струм у колі `I = E / (R_L + r)`, корисну потужність `P_L = I² · R_L`, внутрішні втрати джерела `P_loss = I² · r` та поточний ККД `η = P_L / (P_L + P_loss)`. Це дозволяє наочно надати таблицю даних, яка демонструє точний 50% ККД у точці узгодження `R_L = r` та поступове підвищення ККД до 90% і вище при зростанні `R_L`.
2. **Оптимізація режиму роботи силового трансформатора**: програма приймає паспортні дані трансформатора (номінальну потужність `S_n`, постійні втрати в сталі `P_0`, змінні втрати короткого замикання в міді `P_sc` та коефіцієнт потужності `cos φ`). На основі формули `k_opt = √(P_0 / P_sc)` алгоритм обчислює оптимальний коефіцієнт навантаження `k_opt` і порівнює ККД при оптимальному та номінальному навантаженнях.

## Архітектурний опис структури даних та алгоритму

Симулятор побудовано на трьох фундаментальних модулях:
- **Модуль джерела електричного живлення**: зберігає величину електрорушійної сили (ЕРС) та внутрішнього опору `r`. Він слугує базою для розрахунку параметрів за законом Ома та теоремою Якобі.
- **Модуль сканування опору навантаження**: виконує дискретну ітерацію по заданому діапазону опорів навантаження від `R_start` до `R_end` з обраним кроком. На кожному кроці розраховуються корисна потужність, теплові втрати всередині джерела та миттєвий ККД.
- **Модуль оптимізації трансформатора**: аналізує співвідношення між постійними магнітними втратами в осерді та квадратичними джоулевими втратами в обмотках. Він знаходить точку перетину двох кривих втрат, яка відповідає максимуму характеристики ККД.

Обчислення виконуються з використанням математичної арифметики подвійної точності (`double`). Усі вхідні та вихідні величини узгоджені в єдину систему одиниць SI (Вольти, Ампери, Вати, Оми). Для перетворення кВт у Вт вираз автоматично здійснює множення на scaling фактор.

## Алгоритми обробки сигналів для вбудованих систем (DSP/ADC)

У реальних цифрових ваттметрах та смарт-лічильниках вимірювання активної потужності виконується шляхом дискретного оцифрування миттєвих значень напруги `V[k]` та струму `I[k]` за допомогою аналогово-цифрового перетворювача (АЦП/ADC):

```
P_active = (1 / N) · ∑ (V[k] · I[k])
```

для `k` від `0` до `N - 1`, де `N` — кількість відліків за період фундаментальної частоти мережі (наприклад, 128 відліків на один період 20 мс при 50 Гц). Обчислення ККД виконується шляхом одночасного вимірювання вхідного `P_in` та вихідного `P_out` потоків потужності з синхронізацією фазових кутів та фільтрацією високочастотних завад через цифрові КІХ/БІХ фільтри.

## Економічна оптимізація провідника за законом Кельвіна

Крім технічного аналізу ККД, симулятор моделює економічну оптимізацію перерізу провідника за законом Кельвіна (Kelvin's Law). Закон Кельвіна стверджує, що найекономічніший переріз кабелю `A_opt` досягається тоді, коли річна вартість втраченої джоулевої енергії дорівнює річним амортизаційним відрахуванням від капітальних витрат на провідник:

```
A_opt = I_rms · √( (c_energy · τ · ρ) / (c_capital · p_annuity) )
```

де `c_energy` — вартість 1 кВт·год електроенергії, `τ` — число годин максимальних втрат на рік, `ρ` — питомий опір матеріалу, `c_capital` — вартість одиниці об'єму провідника, `p_annuity` — норма амортизаційних відрахувань. Цей розрахунок дозволяє підібрати переріз провідника так, щоб сумарні витрати протягом 30 років експлуатації були мінімальними.

## Оптимізація пам'яті та кеш-дружність структур даних

У версії мовою C++ структура `EfficiencyPoint` вирівняна за межами 64 біт (8 байтів), що відповідає розміру підсистеми плаваючої коми процесів x86_64 та ARM64. Послідовне розміщення елементів у контейнері `std::vector<EfficiencyPoint>` гарантує високу локальність даних у L1/L2 кеші процесора.

Для забезпечення чисельної стійкості при діленні на малі значення опору застосовано перевірки нормалізованих чисел стандарту IEEE 754. Це упереджує утворення денормалізованих чисел (denormals) та запобігає виникненню винятків ділення на нуль при роботі з розімкненим колом.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура параметрів кола постійного струму */
typedef struct {
    double emf_v;         /* ЕРС джерела, Вольти */
    double internal_r;    /* Внутрішній опір джерела r, Оми */
} dc_source_t;

/* Результат розрахунку для точкового опору навантаження */
typedef struct {
    double r_load;        /* Опір навантаження R_L, Оми */
    double ratio_r;       /* Відношення R_L / r */
    double current_a;     /* Струм у колі, Ампери */
    double p_useful_w;    /* Корисна потужність на навантаженні, Вати */
    double p_loss_w;      /* Потужність втрат всередині джерела, Вати */
    double efficiency;    /* Коефіцієнт корисної дії η, відносна величина (0..1) */
} efficiency_point_t;

/* Структура параметрів трансформатора */
typedef struct {
    double nominal_kva;   /* Номінальна повна потужність S_n, кВА */
    double p_core_kw;     /* Постійні втрати в сталі (холостий хід) P_0, кВт */
    double p_copper_kw;   /* Змінні втрати короткого замикання P_sc, кВт */
    double power_factor;  /* Коефіцієнт потужності cos φ */
} transformer_spec_t;

/* Алгоритм скан-аналізу ККД кола постійного струму */
bool analyze_dc_circuit(const dc_source_t* source, double r_start, double r_end, 
                        size_t steps, efficiency_point_t* results) {
    if (!source || !results || steps == 0 || source->internal_r <= 0.0) {
        return false;
    }

    double step_size = (r_end - r_start) / (double)(steps > 1 ? steps - 1 : 1);
    for (size_t i = 0; i < steps; ++i) {
        double r_l = r_start + (double)i * step_size;
        double total_r = r_l + source->internal_r;
        double current = source->emf_v / total_r;

        results[i].r_load = r_l;
        results[i].ratio_r = r_l / source->internal_r;
        results[i].current_a = current;
        results[i].p_useful_w = current * current * r_l;
        results[i].p_loss_w = current * current * source->internal_r;
        results[i].efficiency = results[i].p_useful_w / (results[i].p_useful_w + results[i].p_loss_w);
    }
    return true;
}

/* Обчислення оптимуму ККД трансформатора */
double calculate_transformer_optimal_k(const transformer_spec_t* spec) {
    if (!spec || spec->p_copper_kw <= 0.0 || spec->p_core_kw <= 0.0) {
        return 0.0;
    }
    return sqrt(spec->p_core_kw / spec->p_copper_kw);
}

/* Обчислення ККД трансформатора при заданому коефіцієнті навантаження k */
double calculate_transformer_efficiency(const transformer_spec_t* spec, double k) {
    if (!spec || k < 0.0) {
        return 0.0;
    }
    double p_out = k * spec->nominal_kva * spec->power_factor;
    double p_losses = spec->p_core_kw + (k * k) * spec->p_copper_kw;
    if (p_out + p_losses <= 0.0) {
        return 0.0;
    }
    return p_out / (p_out + p_losses);
}

int main(void) {
    printf("=== СИМУЛЯТОР ТА ОПТИМІЗАТОР ЕЛЕКТРИЧНОГО ККД ===\n\n");

    /* 1. Дослідження режимів кола постійного струму */
    dc_source_t battery = { .emf_v = 12.0, .internal_r = 2.0 };
    const size_t num_points = 5;
    efficiency_point_t points[5];

    if (analyze_dc_circuit(&battery, 0.5, 10.0, num_points, points)) {
        printf("--- Аналіз кола постійного струму (ЕРС = 12В, r = 2 Ом) ---\n");
        printf("R_L (Ом) | R_L/r | Струм (А) | P_кор (Вт) | P_вт (Вт) | ККД (%%)\n");
        printf("----------------------------------------------------------\n");
        for (size_t i = 0; i < num_points; ++i) {
            printf("%7.2f  | %5.2f | %9.2f | %10.2f | %9.2f | %6.2f%%\n",
                   points[i].r_load, points[i].ratio_r, points[i].current_a,
                   points[i].p_useful_w, points[i].p_loss_w, points[i].efficiency * 100.0);
        }
    }

    /* 2. Оптимізація силового трансформатора */
    transformer_spec_t trans = {
        .nominal_kva = 1000.0,
        .p_core_kw = 2.5,
        .p_copper_kw = 10.0,
        .power_factor = 0.90
    };

    double k_opt = calculate_transformer_optimal_k(&trans);
    double max_eta = calculate_transformer_efficiency(&trans, k_opt);
    double nominal_eta = calculate_transformer_efficiency(&trans, 1.0);

    printf("\n--- Аналіз ККД силового трансформатора (1000 кВА) ---\n");
    printf("Постійні втрати P_0: %.2f кВт, Втрати короткого замикання P_sc: %.2f кВт\n",
           trans.p_core_kw, trans.p_copper_kw);
    printf("Оптимальний коефіцієнт навантаження k_opt: %.3f (%.1f%% від номіналу)\n",
           k_opt, k_opt * 100.0);
    printf("Максимальний ККД (при k_opt): %.3f%%\n", max_eta * 100.0);
    printf("Номінальний ККД (при k = 1.0): %.3f%%\n", nominal_eta * 100.0);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>
#include <optional>

namespace PowerEfficiency {

struct DcSource {
    double emf_v{12.0};
    double internal_r{2.0};
};

struct EfficiencyPoint {
    double r_load_ohm{0.0};
    double ratio_r{0.0};
    double current_amp{0.0};
    double p_useful_watt{0.0};
    double p_loss_watt{0.0};
    double efficiency{0.0};
};

struct TransformerSpec {
    double nominal_kva{1000.0};
    double p_core_kw{2.5};
    double p_copper_kw{10.0};
    double power_factor{0.90};
};

class CircuitAnalyzer {
public:
    static std::vector<EfficiencyPoint> sweepLoad(const DcSource& source, 
                                                 double r_start, 
                                                 double r_end, 
                                                 std::size_t steps) {
        if (steps == 0 || source.internal_r <= 0.0) {
            return {};
        }

        std::vector<EfficiencyPoint> results;
        results.reserve(steps);

        const double step_size = (r_end - r_start) / static_cast<double>(steps > 1 ? steps - 1 : 1);

        for (std::size_t i = 0; i < steps; ++i) {
            const double r_l = r_start + static_cast<double>(i) * step_size;
            const double total_r = r_l + source.internal_r;
            const double current = source.emf_v / total_r;
            const double p_useful = current * current * r_l;
            const double p_loss = current * current * source.internal_r;
            const double eta = p_useful / (p_useful + p_loss);

            results.push_back(EfficiencyPoint{
                .r_load_ohm = r_l,
                .ratio_r = r_l / source.internal_r,
                .current_amp = current,
                .p_useful_watt = p_useful,
                .p_loss_watt = p_loss,
                .efficiency = eta
            });
        }
        return results;
    }
};

class TransformerOptimizer {
public:
    explicit TransformerOptimizer(TransformerSpec spec) : spec_(spec) {}

    [[nodiscard]] std::optional<double> calculateOptimalK() const noexcept {
        if (spec_.p_copper_kw <= 0.0 || spec_.p_core_kw <= 0.0) {
            return std::nullopt;
        }
        return std::sqrt(spec_.p_core_kw / spec_.p_copper_kw);
    }

    [[nodiscard]] double calculateEfficiency(double load_factor_k) const noexcept {
        if (load_factor_k < 0.0) return 0.0;
        const double p_out = load_factor_k * spec_.nominal_kva * spec_.power_factor;
        const double p_losses = spec_.p_core_kw + (load_factor_k * load_factor_k) * spec_.p_copper_kw;
        if (p_out + p_losses <= 0.0) return 0.0;
        return p_out / (p_out + p_losses);
    }

private:
    TransformerSpec spec_;
};

} // namespace PowerEfficiency

int main() {
    using namespace PowerEfficiency;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== СИМУЛЯТОР ККД ТА ЕНЕРГЕТИЧНОГО БАЛАНСУ (C++20) ===\n\n";

    const DcSource source{.emf_v = 24.0, .internal_r = 1.5};
    auto analysis = CircuitAnalyzer::sweepLoad(source, 0.5, 7.5, 5);

    std::cout << "--- Аналіз джерела (ЕРС = 24В, r = 1.5 Ом) ---\n";
    std::cout << "R_L (Ом) | R_L/r | Струм (А) | P_кор (Вт) | P_вт (Вт) | ККД (%)\n";
    std::cout << "----------------------------------------------------------\n";
    for (const auto& pt : analysis) {
        std::cout << std::setw(7) << pt.r_load_ohm << "  | "
                  << std::setw(5) << pt.ratio_r << " | "
                  << std::setw(9) << pt.current_amp << " | "
                  << std::setw(10) << pt.p_useful_watt << " | "
                  << std::setw(9) << pt.p_loss_watt << " | "
                  << std::setw(6) << pt.efficiency * 100.0 << "%\n";
    }

    const TransformerSpec trans_spec{
        .nominal_kva = 2500.0,
        .p_core_kw = 4.0,
        .p_copper_kw = 16.0,
        .power_factor = 0.95
    };

    TransformerOptimizer optimizer(trans_spec);
    if (auto opt_k = optimizer.calculateOptimalK()) {
        std::cout << "\n--- Оптимізація трансформатора " << trans_spec.nominal_kva << " кВА ---\n";
        std::cout << "Оптимальний коефіцієнт k_opt: " << *opt_k << " (" << (*opt_k * 100.0) << "% від номіналу)\n";
        std::cout << "Максимальний ККД: " << (optimizer.calculateEfficiency(*opt_k) * 100.0) << "%\n";
        std::cout << "Номінальний ККД (k=1.0): " << (optimizer.calculateEfficiency(1.0) * 100.0) << "%\n";
    }

    return 0;
}
```
:::

## Оцінка складності та архітектурні нюанси

- **Часова складність**: Алгоритм сканування кіл `CircuitAnalyzer` має лінійну складність `O(N)`, де `N` — кількість кроків сканування. Розрахунок точки оптимуму трансформатора `calculateOptimalK` має константну складність `O(1)`.
- **Просторова складність**: `O(N)` у версії з поверненням вектора результатів або `O(1)` при потоковій обробці вбудованою системою без розширення динамічної пам'яті.
- **Особливості C++ реалізації**: Використовується суворе виділення просторів імен `PowerEfficiency`, безпечна робота з пам'яттю за допомогою `std::vector`, концепція об'єктів з незмінним станом (`const noexcept`) та обгортка `std::optional` для захисту від ділення на нуль або від'ємних втрат.
- **Порівняння реалізацій**: Варіант мовою C розрахований на статичну пам'ять і процедурний виклик (типово для AVR чи ARM Cortex-M мікроконтролерів без підтримки C++ STL). Варіант мовою C++ утилізує сучасний стандарт C++20 з RAII, ізоляцією даних та строгим контролем недійсних станів через шаблони вищого порядку.
- **Точність та чисельна стійкість**: Математичні вирази розраховуються без накопичення похибок ітерацій, оскільки кожен крок `R_L` обчислюється незалежно від базової ЕРС та внутрішнього опору `r`.
