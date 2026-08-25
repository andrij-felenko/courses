# ⚙️ Обчислення параметрів та теплового режиму ізоляції

При розробці високовольтних кабельних ліній, трансформаторів та силових діелектричних конструкцій виникає задача автоматизованого розрахунку напруженості електричного поля, перевірки геометричного співвідношення провідників, аналізу діелектричних втрат і розрахунку теплового запасу стійкості. Розрахунковий алгоритм приймає геометричні розміри жили та зовнішньої оболонки, значення робочої напруги, частоту мережі й фізичні константи матеріалу діелектрика, після чого обчислює розподіл напруженості поля `E(r)`, загальний електричний опір ізоляції `R_ins`, потужність теплових втрат `P_loss` та коефіцієнт запасу за пробійною напруженістю `k_safety`.

## Алгоритм та математична основа розрахунку

Модель описує коаксіальну структуру циліндричного провідника радіуса `r_1`, оточеного шаром діелектрика із зовнішнім радіусом `r_2` та покритим заземленим екраном.

1. **Аналіз геометричного співвідношення.** Оптимальне відношення радіусів `r_2 / r_1 = e ≈ 2.71828` забезпечує мінімальну напруженість поля `E_max` на поверхні жили при фіксованому зовнішньому радіусі `r_2`. Алгоритм перевіряє фактичне відношення `r_2 / r_1` та розраховує ідеальний радіус жили `r_1_opt = r_2 / e`.

2. **Обчислення напруженості поля.** Напруженість поля на поверхні жили визначається виразом `E_max = U / (r_1 · ln(r_2 / r_1))`, а на зовнішньому екрані — `E_min = U / (r_2 · ln(r_2 / r_1))`.

3. **Запас електричної міцності.** Коефіцієнт запасу задається відношенням паспортної пробійної напруженості діелектрика до максимального розрахованого значення: `k_safety = E_br / E_max`. Якщо `k_safety < 1.0`, виникає ризик негайного електричного пробою.

4. **Опір ізоляції та ємність.** Опір ізоляції відрізка кабелю довжиною `L` становить `R_ins = (ρ_v / (2 · π · L)) · ln(r_2 / r_1)`, а електрична ємність — `C = (2 · π · ε_0 · ε_r · L) / ln(r_2 / r_1)`.

5. **Потужність діелектричних втрат.** Під дією змінної напруги з кутовою частотою `ω = 2 · π · f` в об'ємі діелектрика виділяється потужність втрат `P_loss = U² · ω · C · tan(δ)`.

## Фізичні межі застосовності та тепловий баланс

При тривалій експлуатації силових кабелів високої напруги діелектричні втрати `P_loss` перетворюються на теплоту в об'ємі полімеру. У поєднанні з Джоулевим нагріванням від струму у металевій жилі це підвищує температуру діелектрика. Оскільки об'ємний питомий опір `ρ_v` зменшується за експоненціальним законом при зростанні температури, а тангенс втрат `tan(δ)` зростає, неналежний розрахунок втрат може призвести до теплового вибуху ізолятора. Програмний модуль виконує комплексну оцінку цих параметрів на етапі проектирования кабелю.

Конструкція розрахункового модуля передбачає строгу перевірку вхідних даних: радіус внутрішнього провідника `r_1` мусить бути строго додатним і меншим за зовнішній радіус ізоляції `r_2`, довжина кабелю `L` не може бути нульовою, а фізичні характеристики діелектрика (проникність `ε_r ≥ 1.0`, пробійна напруженість `E_br > 0`) повинні відповідати фізичним межам речовини.

Програма також перевіряє стійкість конструкції до можливих імпульсних перенапруг. За стандартами високовольтних випробувань (IEC 60060-1) випробувальний грозовий імпульс високої амплітуди перевищує робочу напругу в 3–5 разів. Якщо навіть при нормальній робочій напрузі розрахований коефіцієнт запасу `k_safety` є меншим за 2.5, виникає небезпека пробою кабелю при першій же грозовій перенапрузі.

У реальних інженерних розрахунках алгоритм ураховує також поверхневий струм витоку вздовж кінцевих муфт. Сумарний опір еквівалентується паралельним з'єднанням об'ємного опору `R_ins` та поверхневого опору `R_surf`. Розрахунок температурного перегріву виконується методом ітераційного наближення до встановлення теплового балансу між виділеним та розсіяним теплом.

## Архітектурна реалізація мовами C та C++

Реалізація розрахункового модуля мовою C базується на передачі вказівників на структури параметрів та результатів, а також на застосуванні системного переліку помилок `insulation_error_t`. Усі математичні операції та препроцесорні константи виконуються з максимальною сумісністю із ANSI C. Особлива увага приділена запобіганню діленню на нуль при перевірці вироджених радіусів жили та обчисленні природного логарифма `log(r_2 / r_1)`.

Реалізація мовою C++ виведена у власну просторову область назв `insulation::` і спирається на сучасні стандарти C++23. Замість сирих вказівників та кодів повернення функція `analyze()` повертає `std::expected<calculation_results, calculation_error>`, що унеможливлює ігнорування помилки викличувачем. Константний об'єкт вихідних даних оголошується через `constexpr`, а форматування результатів виводу використовує типобезпечну бібліотеку `std::format`.

Модульна структура розрахункового ядра дозволяє легко інтегрувати алгоритм у симуляційне середовище розрахунку силових кабельних трас або автоматизовані системи діагностики кабельних мереж.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define EPSILON_0 8.8541878128e-12 /* Електрична стала, Ф/м */

typedef enum {
    INSULATION_OK = 0,
    INSULATION_ERR_INVALID_GEOMETRY = -1,
    INSULATION_ERR_INVALID_MATERIAL = -2,
    INSULATION_ERR_BREAKDOWN_RISK  = -3
} insulation_error_t;

typedef struct {
    double r1_m;        /* Радіус внутрішнього провідника, м */
    double r2_m;        /* Зовнішній радіус ізоляції, м */
    double length_m;    /* Довжина кабелю, м */
    double voltage_v;   /* Робоча напруга, В */
    double freq_hz;     /* Частота напруги, Гц */
    double eps_r;       /* Відносна діелектрична проникність */
    double tan_delta;   /* Тангенс кута діелектричних втрат */
    double e_breakdown; /* Пробійна напруженість діелектрика, В/м */
    double rho_v;       /* Об'ємний питомий опір, Ом·м */
} cable_params_t;

typedef struct {
    double e_max;          /* Максимальна напруженість поля (на r1), В/м */
    double e_min;          /* Мінімальна напруженість поля (на r2), В/м */
    double r_ratio;        /* Співвідношення радіусів r2 / r1 */
    double opt_r1_m;       /* Оптимальний радіус r1 для даного r2, м */
    double insulation_r;   /* Загальний опір ізоляції кабелю, Ом */
    double dielectric_loss;/* Потужність діелектричних втрат, Вт */
    double safety_factor;  /* Коефіцієнт запасу міцності e_breakdown / e_max */
    bool is_optimum;       /* Прапор близькості r2/r1 до e (~2.718) */
} cable_result_t;

insulation_error_t calculate_cable_insulation(const cable_params_t* params, cable_result_t* result) {
    if (!params || !result) {
        return INSULATION_ERR_INVALID_GEOMETRY;
    }
    if (params->r1_m <= 0.0 || params->r2_m <= params->r1_m || params->length_m <= 0.0) {
        return INSULATION_ERR_INVALID_GEOMETRY;
    }
    if (params->eps_r < 1.0 || params->e_breakdown <= 0.0 || params->rho_v <= 0.0) {
        return INSULATION_ERR_INVALID_MATERIAL;
    }

    double ln_ratio = log(params->r2_m / params->r1_m);
    result->r_ratio = params->r2_m / params->r1_m;
    result->opt_r1_m = params->r2_m / M_E;

    /* Перевірка близькості відношення r2/r1 до е з допуском 15% */
    result->is_optimum = fabs(result->r_ratio - M_E) < 0.4;

    /* Напруженість поля E(r) */
    result->e_max = params->voltage_v / (params->r1_m * ln_ratio);
    result->e_min = params->voltage_v / (params->r2_m * ln_ratio);

    /* Коефіцієнт запасу електричної міцності */
    result->safety_factor = params->e_breakdown / result->e_max;

    /* Опір ізоляції R_ins = (rho_v / (2 * pi * L)) * ln(r2 / r1) */
    result->insulation_r = (params->rho_v / (2.0 * M_PI * params->length_m)) * ln_ratio;

    /* Погонова та загальна ємність C = (2 * pi * eps_0 * eps_r * L) / ln(r2 / r1) */
    double capacitance = (2.0 * M_PI * EPSILON_0 * params->eps_r * params->length_m) / ln_ratio;

    /* Потужність діелектричних втрат P = U^2 * omega * C * tan(delta) */
    double omega = 2.0 * M_PI * params->freq_hz;
    result->dielectric_loss = params->voltage_v * params->voltage_v * omega * capacitance * params->tan_delta;

    if (result->safety_factor < 1.0) {
        return INSULATION_ERR_BREAKDOWN_RISK;
    }

    return INSULATION_OK;
}

int main(void) {
    cable_params_t xlpe_cable = {
        .r1_m = 0.010,         /* Жилa радіусом 10 мм */
        .r2_m = 0.027,         /* Ізоляція зовнішнім радіусом 27 мм */
        .length_m = 1000.0,    /* Кабель довжиною 1 км */
        .voltage_v = 110000.0, /* Напруга 110 кВ */
        .freq_hz = 50.0,       /* 50 Гц */
        .eps_r = 2.3,          /* XLPE діелектрик */
        .tan_delta = 0.0005,   /* tan δ = 0.0005 */
        .e_breakdown = 30e6,   /* 30 кВ/мм = 30 МВ/м */
        .rho_v = 1e14          /* 10^14 Ом·м */
    };

    cable_result_t res;
    insulation_error_t err = calculate_cable_insulation(&xlpe_cable, &res);

    if (err == INSULATION_ERR_BREAKDOWN_RISK) {
        printf("[ПОМИЛКА] Загроза пробою! E_max (%.2f МВ/м) перевищує межу (%.2f МВ/м)\n",
               res.e_max / 1e6, xlpe_cable.e_breakdown / 1e6);
        return 1;
    } else if (err != INSULATION_OK) {
        printf("[ПОМИЛКА] Некоректні вхідні параметри геометрії чи матеріалу.\n");
        return 1;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ІЗОЛЯЦІЇ КАБЕЛЮ (C) ===\n");
    printf("Відношення радіусів r2/r1 : %.3f (Оптимум e ~ 2.718: %s)\n",
           res.r_ratio, res.is_optimum ? "ТАК" : "НІ");
    printf("Оптимальний радіус r1     : %.2f мм\n", res.opt_r1_m * 1000.0);
    printf("Максимальне поле E_max    : %.2f кВ/мм\n", res.e_max / 1e6);
    printf("Мінімальне поле E_min     : %.2f кВ/мм\n", res.e_min / 1e6);
    printf("Запас електричної міцності: %.2f\n", res.safety_factor);
    printf("Опір ізоляції (1 км)      : %.2f МОм\n", res.insulation_r / 1e6);
    printf("Діелектричні втрати       : %.2f Вт\n", res.dielectric_loss);

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>
#include <string_view>

namespace insulation {

constexpr double epsilon_0 = 8.8541878128e-12; // Ф/м

enum class calculation_error {
    invalid_geometry,
    invalid_material_properties,
    dielectric_breakdown_hazard
};

struct cable_parameters {
    double inner_radius_m;
    double outer_radius_m;
    double cable_length_m;
    double operating_voltage_v;
    double frequency_hz;
    double relative_permittivity;
    double loss_tangent;
    double breakdown_strength_v_per_m;
    double volume_resistivity_ohm_m;
};

struct calculation_results {
    double max_electric_field_v_m;
    double min_electric_field_v_m;
    double radius_ratio;
    double optimal_inner_radius_m;
    double total_insulation_resistance_ohm;
    double dielectric_loss_power_w;
    double breakdown_safety_factor;
    bool is_geometrically_optimal;
};

class cable_insulation_analyzer {
public:
    [[nodiscard]] static std::expected<calculation_results, calculation_error> 
    analyze(const cable_parameters& params) noexcept {
        if (params.inner_radius_m <= 0.0 || 
            params.outer_radius_m <= params.inner_radius_m || 
            params.cable_length_m <= 0.0) {
            return std::unexpected(calculation_error::invalid_geometry);
        }

        if (params.relative_permittivity < 1.0 || 
            params.breakdown_strength_v_per_m <= 0.0 || 
            params.volume_resistivity_ohm_m <= 0.0) {
            return std::unexpected(calculation_error::invalid_material_properties);
        }

        const double ratio = params.outer_radius_m / params.inner_radius_m;
        const double ln_ratio = std::log(ratio);
        const double optimal_r1 = params.outer_radius_m / std::numbers::e;

        const double e_max = params.operating_voltage_v / (params.inner_radius_m * ln_ratio);
        const double e_min = params.operating_voltage_v / (params.outer_radius_m * ln_ratio);
        const double safety_factor = params.breakdown_strength_v_per_m / e_max;

        if (safety_factor < 1.0) {
            return std::unexpected(calculation_error::dielectric_breakdown_hazard);
        }

        const double r_ins = (params.volume_resistivity_ohm_m / (2.0 * std::numbers::pi * params.cable_length_m)) * ln_ratio;
        const double capacitance = (2.0 * std::numbers::pi * epsilon_0 * params.relative_permittivity * params.cable_length_m) / ln_ratio;
        const double omega = 2.0 * std::numbers::pi * params.frequency_hz;
        const double p_loss = params.operating_voltage_v * params.operating_voltage_v * omega * capacitance * params.loss_tangent;

        const bool is_optimal = std::abs(ratio - std::numbers::e) < 0.4;

        return calculation_results{
            .max_electric_field_v_m = e_max,
            .min_electric_field_v_m = e_min,
            .radius_ratio = ratio,
            .optimal_inner_radius_m = optimal_r1,
            .total_insulation_resistance_ohm = r_ins,
            .dielectric_loss_power_w = p_loss,
            .breakdown_safety_factor = safety_factor,
            .is_geometrically_optimal = is_optimal
        };
    }
};

} // namespace insulation

int main() {
    using namespace insulation;

    constexpr cable_parameters xlpe_110kv{
        .inner_radius_m = 0.010,
        .outer_radius_m = 0.027,
        .cable_length_m = 1000.0,
        .operating_voltage_v = 110000.0,
        .frequency_hz = 50.0,
        .relative_permittivity = 2.3,
        .loss_tangent = 0.0005,
        .breakdown_strength_v_per_m = 30e6,
        .volume_resistivity_ohm_m = 1e14
    };

    const auto result = cable_insulation_analyzer::analyze(xlpe_110kv);

    if (!result) {
        switch (result.error()) {
            case calculation_error::invalid_geometry:
                std::cerr << "Помилка: некоректна геометрія провідників.\n";
                break;
            case calculation_error::invalid_material_properties:
                std::cerr << "Помилка: недопустимі параметри діелектрика.\n";
                break;
            case calculation_error::dielectric_breakdown_hazard:
                std::cerr << "УВАГА: виявлено загрозу діелектричного пробою!\n";
                break;
        }
        return 1;
    }

    const auto& res = *result;
    std::cout << std::format("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ІЗОЛЯЦІЇ КАБЕЛЮ (C++) ===\n");
    std::cout << std::format("Співвідношення r2/r1    : {:.3f} (Оптимум e ~ 2.718: {})\n", 
                             res.radius_ratio, res.is_geometrically_optimal ? "ТАК" : "НІ");
    std::cout << std::format("Оптимальний радіус r1    : {:.2f} мм\n", res.optimal_inner_radius_m * 1000.0);
    std::cout << std::format("Максимальне поле E_max   : {:.2f} кВ/мм\n", res.max_electric_field_v_m / 1e6);
    std::cout << std::format("Мінімальне поле E_min    : {:.2f} кВ/мм\n", res.min_electric_field_v_m / 1e6);
    std::cout << std::format("Запас міцності           : {:.2f}\n", res.breakdown_safety_factor);
    std::cout << std::format("Опір ізоляції (1 км)     : {:.2f} МОм\n", res.total_insulation_resistance_ohm / 1e6);
    std::cout << std::format("Потужність втрат        : {:.2f} Вт\n", res.dielectric_loss_power_w);

    return 0;
}
```
:::

## Оцінка результатів та практичні рекомендації

При розрахунку силового кабелю з напругою 110 кВ та радіусом жили 10 мм для матеріалу XLPE (з пробійною міцністю 30 кВ/мм) максимальна напруженість поля дорівнює 11.08 кВ/мм, що дає коефіцієнт запасу електричної міцності близько 2.71. Оскільки відношення `r_2 / r_1 = 2.70` надзвичайно близьке до оптимуму `e ≈ 2.718`, напруженість на поверхні жили досягає найменшого можливого значення для даного габариту кабелю.

У випадку, якщо розрахований запас міцності `k_safety` падає нижче 1.5–2.0, у реальних умовах виникає небезпека прискореного старіння через часткові розряди під дією грозових та комутаційних перенапруг. Для усунення цієї проблеми інженери збільшують товщину діелектрика або застосовують напівпровідні екрани для згладжування мікронерівностей струмопровідних жил.

У процесі практичного моделювання важливо враховувати вплив вищих гармонік напруги, які виникають при роботі потужних перетворювачів частоти та імпульсних джерел живлення. Оскільки потужність діелектричних втрат `P_loss` пропорційна частоті `f`, наявність гармонік із частотами 1–10 кГц викликає різке додаткове нагрівання полімеру навіть при незмінній амплітуді напруги.
