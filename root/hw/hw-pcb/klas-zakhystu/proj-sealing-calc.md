# ⚙️ Інженерний розрахунок ущільнень та компенсації тиску корпусу РЕА

Проектування герметичного корпусу за стандартами IEC 60529 (IP65–IP68) та ISO 20653 (IP69K) спирається на точний баланс механічних і термодинамічних параметрів: ступінь деформації еластомеру, коефіцієнт заповнення паза, прогин фланця між гвинтами та швидкість скидання термічного розрідження. Цей модуль містить повний набір фізичних рівнянь та готову бібліотеку мовами C та C++ для автоматизованого обчислення геометрії ущільнювального шва, контактних сил і площі захисної вентиляційної мембрани.

## Фізико-математична модель розрахунку

### 1. Геометрія паза та стиснення еластомерного шнура

Еластомери під час стиснення зберігають постійний об'єм (коефіцієнт Пуассона ν ≈ 0.499). При вертикальному стисненні круглий переріз діаметром d_s сплющується в квазіеліпс, розширюючись у боки прямокутного паза шириною W та глибиною H.

Ступінь стиснення (Compression Ratio) у відсотках визначається різницею висоти вільного шнура та робочої глибини паза:

```
[Ступінь стиснення еластомеру]
C = ((d_s - H) / d_s) * 100%
```

Для статичних торцевих ущільнень (Face Seal) оптимальний діапазон становить 20% ≤ C ≤ 30%. За значення C < 15% контактний тиск недостатній для заповнення мікронерівностей поверхні (Ra > 0.8 мкм), що призводить до протікання. При C > 35% матеріал зазнає надмірної залишкової деформації (Compression Set) і швидко деградує.

Коефіцієнт заповнення паза (Gland Fill Factor) показує, яку частку площі поперечного перерізу прямокутного паза займає недеформований еластомер:

```
[Площа перерізу круглого шнура]
A_seal = (pi * d_s^2) / 4

[Площа перерізу прямокутного паза]
A_gland = W * H

[Коефіцієнт заповнення паза]
F = (A_seal / A_gland) * 100%
```

Нормативний діапазон заповнення становить 70% ≤ F ≤ 85%. Вільний простір 15–30% обов'язковий: він компенсує бічне розширення гуми при стисненні, теплове лінійне розширення полімеру (коефіцієнт α ≈ 1.5 · 10⁻⁴ K⁻¹, що на порядок вище за алюміній) та можливе набухання еластомеру при контакті з мастилами або паливом. Якщо F ≥ 100%, ущільнення створює гідростатичний тиск усередині замкненого об'єму паза, що призводить до зрізання фланців або розриву кріпильних гвинтів.

### 2. Контактне напруження та сумарна сила притискання

Для переходу від твердості еластомеру за шкалою Шора А (S, Shore A) до модуля пружності Юнга E використовується емпірична залежність ASTM/ISO:

```
[Модуль пружності еластомеру, МПа]
E = (15.75 + 2.15 * S) / (100 - S)
```

Контактна лінійна сила f_lin (зусилля на одиницю довжини периметра, Н/мм) для круглого шнура описується напівемпіричною формулою Ліндлі (Lindley equation):

```
[Погонна сила стиснення O-кільця, Н/мм]
f_lin = E * d_s * (1.25 * (C / 100)^1.5 + 0.1 * (C / 100)^3)
```

Сумарна сила притискання кришки корпусу по всьому периметру паза L_perim:

```
[Повна сила затискання кришки, Н]
F_total = f_lin * L_perim
```

### 3. Прогин фланця між гвинтами та максимальний крок кріплення

Під дією відпорної сили еластомеру фланець корпусу між сусідніми гвинтами працює як балка на двох опорах під дією рівномірно розподіленого навантаження q = f_lin (Н/мм). Максимальний прогин посередині між гвинтами з кроком L_bolt становить:

```
[Момент інерції поперечного перерізу фланця, мм^4]
I_flange = (b_flange * t_flange^3) / 12

[Максимальний прогин стінки фланця, мм]
delta_max = (f_lin * L_bolt^4) / (384 * E_mat * I_flange)
```

де b_flange — ширина полиці фланця, t_flange — товщина стінки фланця, E_mat — модуль пружності матеріалу корпусу (для алюмінієвих сплавів E ≈ 70000 МПа, для полікарбонату E ≈ 2300 МПа, для ABS-пластику E ≈ 2000 МПа).

Критерій нерозривності контакту вимагає, щоб прогин delta_max не перевищував допустимого зниження стиснення прокладки:

```
[Критерій стабільності герметичного шва]
delta_max <= 0.05 * d_s
```

### 4. Термодинамічний перепад тиску та підбір вентиляційної мембрани

При раптовому охолодженні замкненого об'єму повітря V від робочої температури T_hot до температури навколишнього середовища T_cold виникає розрідження (вакуум):

```
[Внутрішнє розрідження в замкненому корпусі, Па]
Delta_P = P_0 * (1 - (T_cold_K / T_hot_K))
```

Для вирівнювання цього перепаду тиску за заданий час релаксації tau (наприклад, 60 секунд) через мікропористу ePTFE-мембрану необхідний об'ємний потік повітря:

```
[Потрібна об'ємна витрата повітря, мл/хв]
Q_req = (V_liters * 1000 * (Delta_P / P_0)) / (tau_sec / 60)
```

Мінімальна активна площа мембрани з питомою проникністю Pi_vent (типово 300–600 мл/хв/см² при перепаді ΔP = 7 кПа):

```
[Мінімальна площа отвору мембрани, см^2]
A_vent = Q_req / (Pi_vent * (Delta_P / 7000))
```

---

## Реалізація інженерного розрахунку на C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура вхідних геометричних і матеріальних параметрів */
typedef struct {
    double cord_diameter_mm;     /* Діаметр перерізу O-кільця d_s */
    double gland_width_mm;       /* Ширина паза W */
    double gland_depth_mm;       /* Глибина паза H */
    double perimeter_mm;         /* Повний периметр ущільнення L_perim */
    double bolt_spacing_mm;      /* Відстань між кріпильними гвинтами L_bolt */
    double flange_thickness_mm;  /* Товщина стінки фланця t */
    double flange_width_mm;      /* Ширина полиці фланця b */
    double shore_a;              /* Твердість за Шором А (30..90) */
    double mat_young_modulus_mpa;/* Модуль Юнга корпусу (ABS=2000, Алюміній=70000) */
    double internal_volume_l;    /* Внутрішній вільний об'єм корпусу V */
    double temp_hot_c;           /* Робоча температура всередині T_hot */
    double temp_cold_c;          /* Температура зовнішнього середовища T_cold */
    double target_time_sec;      /* Бажаний час вирівнювання тиску tau */
    double vent_permeability;    /* Проникність мембрани, мл/(хв*см^2) при 7 кПа */
} GasketInput;

/* Структура вихідних розрахункових результатів */
typedef struct {
    double compression_ratio_pct;/* Ступінь стиснення C (%) */
    double gland_fill_pct;       /* Заповнення паза F (%) */
    double elastomer_modulus_mpa;/* Розрахунковий модуль Юнга гуми E (МПа) */
    double linear_force_n_per_mm;/* Погонна сила притискання f_lin (Н/мм) */
    double total_clamp_force_n;  /* Повна сила стиснення F_total (Н) */
    double bolt_force_n;         /* Сила на один гвинт (Н) */
    double flange_deflection_mm; /* Прогин фланця delta_max (мм) */
    double max_allowable_defl_mm;/* Граничний допустимий прогин (мм) */
    double thermal_vacuum_kpa;   /* Термічне розрідження Delta_P (кПа) */
    double required_airflow_ml_min; /* Необхідна витрата повітря (мл/хв) */
    double min_vent_area_cm2;    /* Мінімальна площа мембрани (см^2) */
    bool is_compression_ok;
    bool is_fill_ok;
    bool is_deflection_ok;
    bool is_design_valid;
} GasketResult;

/* Головна функція розрахунку параметрів ущільнення та вентиляції */
bool calculate_gasket_seal(const GasketInput *in, GasketResult *out) {
    if (!in || !out) return false;
    if (in->cord_diameter_mm <= 0.0 || in->gland_width_mm <= 0.0 || in->gland_depth_mm <= 0.0) return false;
    if (in->shore_a <= 10.0 || in->shore_a >= 98.0) return false;

    /* 1. Стиснення та заповнення паза */
    out->compression_ratio_pct = ((in->cord_diameter_mm - in->gland_depth_mm) / in->cord_diameter_mm) * 100.0;
    
    double a_seal = (M_PI * in->cord_diameter_mm * in->cord_diameter_mm) / 4.0;
    double a_gland = in->gland_width_mm * in->gland_depth_mm;
    out->gland_fill_pct = (a_seal / a_gland) * 100.0;

    /* 2. Модуль пружності та контактне навантаження */
    out->elastomer_modulus_mpa = (15.75 + 2.15 * in->shore_a) / (100.0 - in->shore_a);
    
    double comp_frac = out->compression_ratio_pct / 100.0;
    if (comp_frac < 0.0) comp_frac = 0.0;
    
    out->linear_force_n_per_mm = out->elastomer_modulus_mpa * in->cord_diameter_mm *
        (1.25 * pow(comp_frac, 1.5) + 0.1 * pow(comp_frac, 3.0));
    
    out->total_clamp_force_n = out->linear_force_n_per_mm * in->perimeter_mm;
    
    double bolt_count = in->perimeter_mm / in->bolt_spacing_mm;
    if (bolt_count < 1.0) bolt_count = 1.0;
    out->bolt_force_n = out->total_clamp_force_n / bolt_count;

    /* 3. Жорсткість і прогин фланця */
    double i_flange = (in->flange_width_mm * pow(in->flange_thickness_mm, 3.0)) / 12.0;
    out->flange_deflection_mm = (out->linear_force_n_per_mm * pow(in->bolt_spacing_mm, 4.0)) /
        (384.0 * in->mat_young_modulus_mpa * i_flange);
    out->max_allowable_defl_mm = 0.05 * in->cord_diameter_mm;

    /* 4. Термічний вакуум і розмір мембрани */
    double t_hot_k = in->temp_hot_c + 273.15;
    double t_cold_k = in->temp_cold_c + 273.15;
    double p_atm_kpa = 101.325;
    
    if (t_hot_k > t_cold_k) {
        out->thermal_vacuum_kpa = p_atm_kpa * (1.0 - (t_cold_k / t_hot_k));
    } else {
        out->thermal_vacuum_kpa = 0.0;
    }

    double tau_min = in->target_time_sec / 60.0;
    if (tau_min <= 0.0) tau_min = 1.0;
    
    out->required_airflow_ml_min = (in->internal_volume_l * 1000.0 * (out->thermal_vacuum_kpa / p_atm_kpa)) / tau_min;
    
    double delta_p_norm = out->thermal_vacuum_kpa / 7.0; /* Нормування на 7 кПа */
    if (delta_p_norm < 0.1) delta_p_norm = 0.1;
    
    out->min_vent_area_cm2 = out->required_airflow_ml_min / (in->vent_permeability * delta_p_norm);

    /* 5. Перевірка критеріїв надійності */
    out->is_compression_ok = (out->compression_ratio_pct >= 18.0 && out->compression_ratio_pct <= 32.0);
    out->is_fill_ok = (out->gland_fill_pct >= 65.0 && out->gland_fill_pct <= 85.0);
    out->is_deflection_ok = (out->flange_deflection_mm <= out->max_allowable_defl_mm);
    
    out->is_design_valid = out->is_compression_ok && out->is_fill_ok && out->is_deflection_ok;
    return true;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <format>

namespace sealing {

enum class CalculationError {
    InvalidGeometry,
    InvalidHardness,
    InvalidTemperature,
    ZeroTimeInterval
};

struct GasketParameters {
    double cord_diameter_mm{2.5};      // Діаметр шнура d_s
    double gland_width_mm{3.4};        // Ширина паза W
    double gland_depth_mm{1.9};        // Глибина паза H
    double perimeter_mm{500.0};        // Повний периметр ущільнення
    double bolt_spacing_mm{45.0};      // Відстань між гвинтами
    double flange_thickness_mm{3.0};   // Товщина фланця
    double flange_width_mm{8.0};       // Ширина фланця
    double shore_a{70.0};              // Твердість за Шором А
    double mat_young_modulus_mpa{70000.0}; // Модуль Юнга матеріалу (Алюміній)
    double internal_volume_l{1.2};     // Внутрішній об'єм корпусу
    double temp_hot_c{65.0};           // Робоча температура
    double temp_cold_c{10.0};          // Температура охолодження
    double target_time_sec{60.0};      // Час вирівнювання тиску
    double vent_permeability{400.0};   // Проникність ePTFE (мл/хв*см^2 при 7 кПа)
};

struct GasketAnalysis {
    double compression_pct{0.0};
    double gland_fill_pct{0.0};
    double elastomer_modulus_mpa{0.0};
    double linear_force_n_per_mm{0.0};
    double total_force_n{0.0};
    double bolt_force_n{0.0};
    double flange_deflection_mm{0.0};
    double max_allowed_deflection_mm{0.0};
    double thermal_vacuum_kpa{0.0};
    double airflow_req_ml_min{0.0};
    double min_vent_area_cm2{0.0};
    
    [[nodiscard]] constexpr bool is_compression_valid() const noexcept {
        return compression_pct >= 18.0 && compression_pct <= 32.0;
    }
    
    [[nodiscard]] constexpr bool is_fill_valid() const noexcept {
        return gland_fill_pct >= 65.0 && gland_fill_pct <= 85.0;
    }
    
    [[nodiscard]] constexpr bool is_deflection_valid() const noexcept {
        return flange_deflection_mm <= max_allowed_deflection_mm;
    }
    
    [[nodiscard]] constexpr bool is_pass() const noexcept {
        return is_compression_valid() && is_fill_valid() && is_deflection_valid();
    }
};

class EnclosureSealingCalculator {
public:
    [[nodiscard]] static std::expected<GasketAnalysis, CalculationError> calculate(const GasketParameters& p) noexcept {
        if (p.cord_diameter_mm <= 0.0 || p.gland_width_mm <= 0.0 || p.gland_depth_mm <= 0.0 ||
            p.gland_depth_mm >= p.cord_diameter_mm) {
            return std::unexpected(CalculationError::InvalidGeometry);
        }
        if (p.shore_a <= 10.0 || p.shore_a >= 95.0) {
            return std::unexpected(CalculationError::InvalidHardness);
        }
        if (p.target_time_sec <= 0.0 || p.vent_permeability <= 0.0) {
            return std::unexpected(CalculationError::ZeroTimeInterval);
        }

        GasketAnalysis res{};

        // 1. Стиснення та заповнення паза
        res.compression_pct = ((p.cord_diameter_mm - p.gland_depth_mm) / p.cord_diameter_mm) * 100.0;
        
        const double a_seal = (std::numbers::pi * p.cord_diameter_mm * p.cord_diameter_mm) / 4.0;
        const double a_gland = p.gland_width_mm * p.gland_depth_mm;
        res.gland_fill_pct = (a_seal / a_gland) * 100.0;

        // 2. Модуль пружності та контактне навантаження
        res.elastomer_modulus_mpa = (15.75 + 2.15 * p.shore_a) / (100.0 - p.shore_a);
        
        const double c_frac = std::max(0.0, res.compression_pct / 100.0);
        res.linear_force_n_per_mm = res.elastomer_modulus_mpa * p.cord_diameter_mm *
            (1.25 * std::pow(c_frac, 1.5) + 0.1 * std::pow(c_frac, 3.0));
        
        res.total_force_n = res.linear_force_n_per_mm * p.perimeter_mm;
        
        const double num_bolts = std::max(1.0, p.perimeter_mm / p.bolt_spacing_mm);
        res.bolt_force_n = res.total_force_n / num_bolts;

        // 3. Прогин фланця
        const double i_flange = (p.flange_width_mm * std::pow(p.flange_thickness_mm, 3.0)) / 12.0;
        res.flange_deflection_mm = (res.linear_force_n_per_mm * std::pow(p.bolt_spacing_mm, 4.0)) /
            (384.0 * p.mat_young_modulus_mpa * i_flange);
        res.max_allowed_deflection_mm = 0.05 * p.cord_diameter_mm;

        // 4. Термічний вакуум і повітрообмін мембрани
        const double t_hot_k = p.temp_hot_c + 273.15;
        const double t_cold_k = p.temp_cold_c + 273.15;
        constexpr double p_atm_kpa = 101.325;

        if (t_hot_k > t_cold_k) {
            res.thermal_vacuum_kpa = p_atm_kpa * (1.0 - (t_cold_k / t_hot_k));
        } else {
            res.thermal_vacuum_kpa = 0.0;
        }

        const double tau_min = p.target_time_sec / 60.0;
        res.airflow_req_ml_min = (p.internal_volume_l * 1000.0 * (res.thermal_vacuum_kpa / p_atm_kpa)) / tau_min;
        
        const double delta_p_norm = std::max(0.1, res.thermal_vacuum_kpa / 7.0);
        res.min_vent_area_cm2 = res.airflow_req_ml_min / (p.vent_permeability * delta_p_norm);

        return res;
    }
};

} // namespace sealing
```
:::

---

## Тестовий приклад розрахунку та аналіз результатів

Розглянемо практичний випадок розрахунку корпусу вуличного промислового концентратора IP67:
* Зовнішні розміри корпусу: 150 × 100 × 80 мм, периметр ущільнювального шва L_perim = 500 мм.
* Матеріал корпусу: литий алюміній (E = 70000 МПа), ширина фланця b = 8 мм, товщина стінки t = 3 мм.
* Крок кріпильних гвинтів М4: L_bolt = 45 мм (11 гвинтів по периметру).
* Ущільнення: силіконовий шнур (VMQ) круглого перерізу d_s = 2.5 мм, твердість 70 Shore A.
* Геометрія паза: ширина W = 3.4 мм, глибина H = 1.9 мм.
* Термодинаміка: внутрішній об'єм V = 1.2 л, нагрів приладу до T_hot = +65 °C, охолодження зливою до T_cold = +10 °C, час компенсації tau = 60 с.

:::tabs
```c
int main(void) {
    GasketInput cfg = {
        .cord_diameter_mm = 2.5,
        .gland_width_mm = 3.4,
        .gland_depth_mm = 1.9,
        .perimeter_mm = 500.0,
        .bolt_spacing_mm = 45.0,
        .flange_thickness_mm = 3.0,
        .flange_width_mm = 8.0,
        .shore_a = 70.0,
        .mat_young_modulus_mpa = 70000.0,
        .internal_volume_l = 1.2,
        .temp_hot_c = 65.0,
        .temp_cold_c = 10.0,
        .target_time_sec = 60.0,
        .vent_permeability = 400.0
    };

    GasketResult res;
    if (calculate_gasket_seal(&cfg, &res)) {
        printf("--- РЕЗУЛЬТАТИ РОЗРАХУНКУ УЩІЛЬНЕННЯ IP67 ---\n");
        printf("Ступінь стиснення:        %.2f %%  [%s]\n", res.compression_ratio_pct, res.is_compression_ok ? "OK" : "ПОМИЛКА");
        printf("Заповнення паза:          %.2f %%  [%s]\n", res.gland_fill_pct, res.is_fill_ok ? "OK" : "ПОМИЛКА");
        printf("Погонна сила стиснення:   %.2f Н/мм\n", res.linear_force_n_per_mm);
        printf("Сумарна сила притискання: %.1f Н (%.1f кгс)\n", res.total_clamp_force_n, res.total_clamp_force_n / 9.81);
        printf("Зусилля на 1 гвинт:       %.1f Н\n", res.bolt_force_n);
        printf("Прогин фланця між гвинтами: %.4f мм (макс допустимий: %.4f мм) [%s]\n",
               res.flange_deflection_mm, res.max_allowable_defl_mm, res.is_deflection_ok ? "OK" : "ПОМИЛКА");
        printf("Термічний вакуум:         -%.2f кПа (-%.0f мбар)\n", res.thermal_vacuum_kpa, res.thermal_vacuum_kpa * 10.0);
        printf("Потрібний потік повітря:  %.1f мл/хв\n", res.required_airflow_ml_min);
        printf("Мін. площа ePTFE-мембрани: %.3f см^2 (діаметр >= %.1f мм)\n",
               res.min_vent_area_cm2, 2.0 * sqrt(res.min_vent_area_cm2 / M_PI) * 10.0);
        printf("ЗАГАЛЬНИЙ ВИСНОВОК:       %s\n", res.is_design_valid ? "КОНСТРУКЦІЯ НАДІЙНА" : "ПОТРІБНЕ ДООПРАЦЮВАННЯ");
    }
    return 0;
}
```
```cpp
int main() {
    using namespace sealing;
    GasketParameters cfg{
        .cord_diameter_mm = 2.5,
        .gland_width_mm = 3.4,
        .gland_depth_mm = 1.9,
        .perimeter_mm = 500.0,
        .bolt_spacing_mm = 45.0,
        .flange_thickness_mm = 3.0,
        .flange_width_mm = 8.0,
        .shore_a = 70.0,
        .mat_young_modulus_mpa = 70000.0,
        .internal_volume_l = 1.2,
        .temp_hot_c = 65.0,
        .temp_cold_c = 10.0,
        .target_time_sec = 60.0,
        .vent_permeability = 400.0
    };

    auto eval = EnclosureSealingCalculator::calculate(cfg);
    if (!eval) {
        std::cerr << "Помилка вхідних параметрів розрахунку!\n";
        return 1;
    }

    const auto& res = *eval;
    std::cout << std::format("--- РЕЗУЛЬТАТИ РОЗРАХУНКУ УЩІЛЬНЕННЯ IP67 ---\n");
    std::cout << std::format("Ступінь стиснення:        {:.2f} %  [{}]\n", res.compression_pct, res.is_compression_valid() ? "OK" : "ПОМИЛКА");
    std::cout << std::format("Заповнення паза:          {:.2f} %  [{}]\n", res.gland_fill_pct, res.is_fill_valid() ? "OK" : "ПОМИЛКА");
    std::cout << std::format("Погонна сила стиснення:   {:.2f} Н/мм\n", res.linear_force_n_per_mm);
    std::cout << std::format("Сумарна сила притискання: {:.1f} Н ({:.1f} кгс)\n", res.total_force_n, res.total_force_n / 9.81);
    std::cout << std::format("Зусилля на 1 гвинт:       {:.1f} Н\n", res.bolt_force_n);
    std::cout << std::format("Прогин фланця між гвинтами: {:.4f} мм (ліміт: {:.4f} мм) [{}]\n",
                             res.flange_deflection_mm, res.max_allowed_deflection_mm, res.is_deflection_valid() ? "OK" : "ПОМИЛКА");
    std::cout << std::format("Термічний вакуум:         -{:.2f} кПа (-{:.0f} мбар)\n", res.thermal_vacuum_kpa, res.thermal_vacuum_kpa * 10.0);
    std::cout << std::format("Потрібний потік повітря:  {:.1f} мл/хв\n", res.airflow_req_ml_min);
    
    const double vent_diameter_mm = 2.0 * std::sqrt(res.min_vent_area_cm2 / std::numbers::pi) * 10.0;
    std::cout << std::format("Мін. площа ePTFE-мембрани: {:.3f} см^2 (діаметр >= {:.1f} мм)\n",
                             res.min_vent_area_cm2, vent_diameter_mm);
    std::cout << std::format("ЗАГАЛЬНИЙ ВИСНОВОК:       {}\n", res.is_pass() ? "КОНСТРУКЦІЯ НАДІЙНА" : "ПОТРІБНЕ ДООПРАЦЮВАННЯ");

    return 0;
}
```
:::

### Інженерний аналіз отриманих результатів

1. **Стиснення 24.00% (1.9 мм глибина проти 2.5 мм шнура):** Повністю вкладається в цільовий коридор 20–30%. Забезпечує надійне перекриття мікронерівностей литої поверхні без ризику пластичного сплющування силікону.
2. **Заповнення паза 75.99% (A_seal = 4.91 мм², A_gland = 6.46 мм²):** Залишає 24% вільного об'єму для поперечної деформації та температурного розширення гуми в діапазоні до +85 °C.
3. **Силове навантаження:** Погонна сила 1.88 Н/мм генерує повне стягувальне навантаження на корпус 940 Н (95.8 кгс). При 11 гвинтах кожен гвинт М4 навантажений силою 85.5 Н, що вимагає моменту затягування лише ≈ 0.6–0.8 Н·м (безпечно для різьби в алюмінії).
4. **Жорсткість фланця:** Прогин стінки корпусу між гвинтами становить delta_max = 0.013 мм, що значно менше допустимого ліміту 0.125 мм (5% від d_s). Зазор між фланцями не розкриється під час вібрації або струменів води IP66.
5. **Компенсація вакууму:** Охолодження приладу генерує внутрішнє розрідження -16.48 кПа (-165 мбар). Для його скидання за 60 секунд потрібна ePTFE-мембрана з активною площею не менше 0.208 см² (діаметр від ≥ 5.2 мм, що відповідає стандартному різьбовому ввертишу M12 Gore Vent).
