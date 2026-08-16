# ⚙️ Обчислення термічних меж та ефективності теплової трубки мовами C та C++

Практична програмна реалізація інженерного алгоритму охоплює розрахунок термічних меж, капілярного та кипійного лімітів передачі тепла, а також еквівалентного теплового опору теплової трубки. Два зіставимі ідіоматичні кодові модулі мовами C (C99/C11) та C++ (C++20) містять вичерпний аналіз архітектурних рішень, обчислювальної стійкості, обробки помилок та крайових фізичних випадків.

### 1. Постановка інженерно-обчислювальної задачі

Під час розробки систем охолодження для силової електроніки, серверних процесорів чи космічних апаратів інженер постає перед задачею автоматизованої перевірки працездатності обраної теплової трубки за заданого теплового навантаження `Q` (у ватах) та робочої температури `T` (у градусах Цельсія).

Обчислювальний модуль мусить розрахувати наступні ключеві показники:
1. **Ефективну довжину переносу маси** `L_eff` та площу перерізу пористого фітиля `A_w`.
2. **Число Мерита** робочої рідини `N_M` для оцінки її термодинамічної якості.
3. **Максимальний капілярний тиск** `ΔP_cap,max` за рівнянням Лапласа-Янга.
4. **Гравітаційний протитиск** `ΔP_g` за заданого кута нахилу пристрою до горизонту.
5. **Граничну теплову потужність за капілярним лімітом** `Q_max,cap`, виходячи з гідродинамічного балансу тисків у рідкій фазі за законом Дарсі.
6. **Ефективну теплопровідність фітиля** `λ_eff,wick`, просоченого рідиною, за двокомпонентною формулою Максвелла.
7. **Граничну потужність за кипійним лімітом** `Q_max,boil`, яка викликає критичне зародження парових бульбашок на стінці випаровувача.
8. **Послідовний сумарний еквівалентний тепловий опір** `R_th,total` (у °C/Вт).

### 2. Покроковий математичний алгоритм обчислювального ядра

Обчислювальне ядро реалізує строгий алгоритм розрахунку фізичних параметрів за такою послідовністю кроків:

- **Крок 1. Розрахунок геометрії контуру:**
  Ефективна довжина переносу маси враховує розподілене підведення та відведення тепла у випаровувачі та конденсаторі:
  ```
  L_eff = 0.5 · L_evap + L_adiab + 0.5 · L_cond
  A_w = π · (r_inner² - r_vapor²)
  ```

- **Крок 2. Розрахунок капілярного та гравітаційного тисків:**
  Максимальний тиск всмоктування визначається формулою Лапласа-Янга при змочуванні `cos θ = 1`:
  ```
  ΔP_cap,max = (2 · γ · cos θ) / r_eff_pore
  ΔP_g = ρ_l · g · L_total · sin(φ)
  ΔP_available = ΔP_cap,max - ΔP_g
  ```

- **Крок 3. Розрахунок капілярного ліміту:**
  Якщо гравітаційний протитиск перевищує капілярний помп (`ΔP_available ≤ 0`), приплив рідини припиняється і капілярний ліміт дорівнює нулю (`Q_max,cap = 0`). Якщо ж запасу тиску вистачає:
  ```
  Q_max,cap = ΔP_available · (ρ_l · K · A_w · h_fg) / (μ_l · L_eff)
  ```

- **Крок 4. Розрахунок ефективної теплопровідності просоченого фітиля (Модель Максвелла):**
  Теплопровідність двокомпонентного середовища (металева матриця + просочувальна рідина) розраховується за формулою:
  ```
  λ_eff,wick = λ_metal · [ (λ_metal + λ_fluid) - (1 - ε)·(λ_metal - λ_fluid) ] / [ (λ_metal + λ_fluid) + (1 - ε)·(λ_metal - λ_fluid) ]
  ```

- **Крок 5. Розрахунок кипійного ліміту (Криза ядерного кипіння):**
  Гранична потужність до зародження паровій плівки на стінці випаровувача становить:
  ```
  Q_max,boil = (4 · π · L_evap · λ_eff,wick · γ · T_sat_K) / [ ρ_v · h_fg · r_bubble · ln(r_inner / r_vapor) ]
  ```

- **Крок 6. Розрахунок послідовного ланцюжка теплових опорів:**
  ```
  R_wall,evap = ln(r_outer / r_inner) / (2 · π · L_evap · λ_metal)
  R_wick,evap = ln(r_inner / r_vapor) / (2 · π · L_evap · λ_eff,wick)
  R_wick,cond = ln(r_inner / r_vapor) / (2 · π · L_cond · λ_eff,wick)
  R_wall,cond = ln(r_outer / r_inner) / (2 · π · L_cond · λ_metal)
  R_th,total = R_wall,evap + R_wick,evap + R_wick,cond + R_wall,cond
  ```

### 3. Порівняння ідіоматичних реалізацій: C vs C++

При розробці інженерного ПЗ постає вибір між мовами програмування C та C++:
- **У реалізації мовою C (C99/C11):** застосовується передача параметрів через покажчики на структури `const HeatPipeParams*`, явна перевірка покажчиків на `NULL`, виклики функцій з `math.h` (`sin`, `log`) та повернення структури результату із прапором валідності `is_valid`. Цей підхід ідеально підходить для вбудованих мікроконтролерів (MCU без C++-стандартної бібліотеки).
- **У реалізації мовою C++ (C++20):** застосовано сучасні ідіоми: класи простору імен `namespace thermal`, семантику `constexpr`, методи `[[nodiscard]]`, математичні константи з `std::numbers::pi` та тип `std::expected<AnalysisResult, CalculationError>` для створення високобезпечного коду без використання винятків.

Нижче подано обидві ідіоматичні реалізації у форматі `:::tabs`.

:::tabs
```c
/* heat_pipe_calc.c — Ідіоматична реалізація мовою C (C99/C11) */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Теплофізичні властивості робочої рідини */
typedef struct {
    const char* name;
    double temp_c;          /* Робоча температура, °C */
    double density_l;       /* Густина рідини, кг/м³ */
    double density_v;       /* Густина пари, кг/м³ */
    double h_fg;            /* Прихована теплота випаровування, Дж/кг */
    double surface_tension; /* Поверхневий натяг, Н/м */
    double viscosity_l;     /* Динамічна в'язкість рідини, Па·с */
    double k_fluid;         /* Теплопровідність рідини, Вт/(м·К) */
} FluidProps;

/* Конструктивні параметри теплової трубки */
typedef struct {
    double length_total;    /* Повна довжина, м */
    double length_evap;     /* Довжина випаровувача, м */
    double length_cond;     /* Довжина конденсатора, м */
    double r_outer;         /* Зовнішній радіус трубки, м */
    double r_inner;         /* Внутрішній радіус стінки (зовнішній радіус фітиля), м */
    double r_vapor;         /* Радіус парового ядра, м */
    double r_eff_pore;      /* Ефективний радіус пор фітиля, м */
    double permeability;    /* Проникність фітиля K, м² */
    double porosity;        /* Порозність фітиля (0.0-1.0) */
    double k_metal;         /* Теплопровідність металу стінки, Вт/(м·К) */
} HeatPipeParams;

/* Результати обчислення */
typedef struct {
    double merit_number;    /* Число Мерита рідини, Вт/м² */
    double p_cap_max;       /* Максимальний капілярний тиск, Па */
    double q_cap_limit;     /* Капілярний ліміт потужності, Вт */
    double q_boil_limit;    /* Кипійний ліміт потужності, Вт */
    double r_thermal_total; /* Еквівалентний тепловий опір, °C/Вт */
    bool is_valid;
} HeatPipeResult;

/* Обчислення числа Мерита: N_M = (ρ_l * γ * h_fg) / μ_l */
double calc_merit_number(const FluidProps* f) {
    if (!f || f->viscosity_l <= 0.0) return 0.0;
    return (f->density_l * f->surface_tension * f->h_fg) / f->viscosity_l;
}

/* Розрахунок термічних меж та опору */
HeatPipeResult calc_heat_pipe(const HeatPipeParams* hp, const FluidProps* fluid, double tilt_deg) {
    HeatPipeResult res = {0};
    if (!hp || !fluid) return res;
    if (hp->r_outer <= hp->r_inner || hp->r_inner <= hp->r_vapor) return res;

    /* 1. Ефективна довжина переносу маси */
    double l_eff = 0.5 * hp->length_evap + (hp->length_total - hp->length_evap - hp->length_cond) + 0.5 * hp->length_cond;

    /* 2. Площа перерізу фітиля */
    double a_wick = M_PI * (hp->r_inner * hp->r_inner - hp->r_vapor * hp->r_vapor);

    /* 3. Максимальний капілярний тиск (припущення: кут змочування θ = 0, cos θ = 1) */
    res.p_cap_max = (2.0 * fluid->surface_tension) / hp->r_eff_pore;

    /* 4. Гравітаційний протитиск */
    double tilt_rad = tilt_deg * (M_PI / 180.0);
    double p_grav = fluid->density_l * 9.81 * hp->length_total * sin(tilt_rad);

    /* 5. Число Мерита */
    res.merit_number = calc_merit_number(fluid);

    /* 6. Капілярний ліміт Q_cap_max */
    double available_dp = res.p_cap_max - p_grav;
    if (available_dp > 0.0) {
        res.q_cap_limit = available_dp * (fluid->density_l * hp->permeability * a_wick * fluid->h_fg) / (fluid->viscosity_l * l_eff);
    } else {
        res.q_cap_limit = 0.0; /* Капілярний помп не може подолати гравітацію */
    }

    /* 7. Ефективна теплопровідність просоченого фітиля (формула Максвелла) */
    double km = hp->k_metal;
    double kf = fluid->k_fluid;
    double eps = hp->porosity;
    double k_wick_eff = km * ((km + kf) - (1.0 - eps) * (km - kf)) / ((km + kf) + (1.0 - eps) * (km - kf));

    /* 8. Кипійний ліміт Q_boil_max */
    double t_sat_k = fluid->temp_c + 273.15;
    double r_b = 2.5e-6; /* Типовий радіус зародка бульбашки, 2.5 мкм */
    double numerator = 4.0 * M_PI * hp->length_evap * k_wick_eff * fluid->surface_tension * t_sat_k;
    double denominator = fluid->density_v * fluid->h_fg * r_b * log(hp->r_inner / hp->r_vapor);
    res.q_boil_limit = numerator / denominator;

    /* 9. Еквівалентний тепловий опір */
    double r_wall_evap = log(hp->r_outer / hp->r_inner) / (2.0 * M_PI * hp->length_evap * hp->k_metal);
    double r_wick_evap = log(hp->r_inner / hp->r_vapor) / (2.0 * M_PI * hp->length_evap * k_wick_eff);
    double r_wick_cond = log(hp->r_inner / hp->r_vapor) / (2.0 * M_PI * hp->length_cond * k_wick_eff);
    double r_wall_cond = log(hp->r_outer / hp->r_inner) / (2.0 * M_PI * hp->length_cond * hp->k_metal);

    res.r_thermal_total = r_wall_evap + r_wick_evap + r_wick_cond + r_wall_cond;
    res.is_valid = true;

    return res;
}

int main(void) {
    /* Параметри води за 100 °C */
    FluidProps water = {
        .name = "Water (100 C)",
        .temp_c = 100.0,
        .density_l = 958.4,
        .density_v = 0.598,
        .h_fg = 2257000.0,
        .surface_tension = 0.0589,
        .viscosity_l = 0.000282,
        .k_fluid = 0.679
    };

    /* Типова мідна трубка D=8мм зі спеченим фітилем */
    HeatPipeParams hp = {
        .length_total = 0.200,   /* 200 мм */
        .length_evap = 0.050,    /* 50 мм */
        .length_cond = 0.050,    /* 50 мм */
        .r_outer = 0.0040,       /* Зовнішній радіус 4 мм */
        .r_inner = 0.0033,       /* Стінка 0.7 мм */
        .r_vapor = 0.0025,       /* Товщина фітиля 0.8 мм */
        .r_eff_pore = 15e-6,     /* Пор 15 мкм */
        .permeability = 1.5e-11, /* K = 1.5e-11 м² */
        .porosity = 0.55,        /* Порозність 55% */
        .k_metal = 390.0         /* Мідь */
    };

    HeatPipeResult res = calc_heat_pipe(&hp, &water, 0.0 /* Горизонтально */);

    if (res.is_valid) {
        printf("--- Розрахунок теплової трубки (%s) ---\n", water.name);
        printf("Число Мерита N_M:        %.2e Вт/м²\n", res.merit_number);
        printf("Макс. капілярний тиск:  %.1f Па\n", res.p_cap_max);
        printf("Капілярний ліміт Q_max: %.2f Вт\n", res.q_cap_limit);
        printf("Кипійний ліміт Q_max:   %.2f Вт\n", res.q_boil_limit);
        printf("Тепловий опір R_th:     %.4f °C/Вт\n", res.r_thermal_total);
    }
    return 0;
}
```
```cpp
// heat_pipe_calc.cpp — Ідіоматична реалізація мовою C++ (C++20)
#include <iostream>
#include <cmath>
#include <string_view>
#include <numbers>
#include <expected>
#include <iomanip>

namespace thermal {

struct FluidProps {
    std::string_view name;
    double temp_c;            // °C
    double density_l;         // кг/м³
    double density_v;         // кг/м³
    double h_fg;              // Дж/кг
    double surface_tension;   // Н/м
    double viscosity_l;       // Па·с
    double k_fluid;           // Вт/(м·К)

    [[nodiscard]] constexpr double merit_number() const noexcept {
        return (density_l * surface_tension * h_fg) / viscosity_l;
    }
};

struct HeatPipeGeometry {
    double length_total;      // м
    double length_evap;       // м
    double length_cond;       // м
    double r_outer;           // м
    double r_inner;           // м
    double r_vapor;           // м
    double r_eff_pore;        // м
    double permeability;      // м²
    double porosity;          // 0..1
    double k_metal;           // Вт/(м·К)

    [[nodiscard]] constexpr double effective_length() const noexcept {
        return 0.5 * length_evap + (length_total - length_evap - length_cond) + 0.5 * length_cond;
    }

    [[nodiscard]] constexpr double wick_area() const noexcept {
        return std::numbers::pi * (r_inner * r_inner - r_vapor * r_vapor);
    }
};

struct AnalysisResult {
    double merit_number;
    double p_cap_max;
    double q_cap_limit;
    double q_boil_limit;
    double r_thermal_total;
};

enum class CalculationError {
    InvalidGeometry,
    NegativeAvailablePressure,
    ZeroViscosity
};

class HeatPipeAnalyzer {
public:
    [[nodiscard]] static std::expected<AnalysisResult, CalculationError> 
    analyze(const HeatPipeGeometry& hp, const FluidProps& fluid, double tilt_deg = 0.0) noexcept 
    {
        if (hp.r_outer <= hp.r_inner || hp.r_inner <= hp.r_vapor || fluid.viscosity_l <= 0.0) {
            return std::unexpected(CalculationError::InvalidGeometry);
        }

        AnalysisResult res{};
        res.merit_number = fluid.merit_number();
        res.p_cap_max = (2.0 * fluid.surface_tension) / hp.r_eff_pore;

        const double tilt_rad = tilt_deg * (std::numbers::pi / 180.0);
        const double p_grav = fluid.density_l * 9.81 * hp.length_total * std::sin(tilt_rad);
        const double available_dp = res.p_cap_max - p_grav;

        if (available_dp <= 0.0) {
            return std::unexpected(CalculationError::NegativeAvailablePressure);
        }

        const double l_eff = hp.effective_length();
        const double a_wick = hp.wick_area();

        // Капілярне обмеження
        res.q_cap_limit = available_dp * (fluid.density_l * hp.permeability * a_wick * fluid.h_fg) 
                          / (fluid.viscosity_l * l_eff);

        // Ефективна теплопровідність фітиля за Максвеллом
        const double km = hp.k_metal;
        const double kf = fluid.k_fluid;
        const double eps = hp.porosity;
        const double k_wick_eff = km * ((km + kf) - (1.0 - eps) * (km - kf)) 
                                  / ((km + kf) + (1.0 - eps) * (km - kf));

        // Кипійний ліміт
        const double t_sat_k = fluid.temp_c + 273.15;
        constexpr double r_b = 2.5e-6; // Радіус зародка бульбашки
        const double num = 4.0 * std::numbers::pi * hp.length_evap * k_wick_eff * fluid.surface_tension * t_sat_k;
        const double den = fluid.density_v * fluid.h_fg * r_b * std::log(hp.r_inner / hp.r_vapor);
        res.q_boil_limit = num / den;

        // Послідовний сумарний опір
        const double r_wall_evap = std::log(hp.r_outer / hp.r_inner) / (2.0 * std::numbers::pi * hp.length_evap * hp.k_metal);
        const double r_wick_evap = std::log(hp.r_inner / hp.r_vapor) / (2.0 * std::numbers::pi * hp.length_evap * k_wick_eff);
        const double r_wick_cond = std::log(hp.r_inner / hp.r_vapor) / (2.0 * std::numbers::pi * hp.length_cond * k_wick_eff);
        const double r_wall_cond = std::log(hp.r_outer / hp.r_inner) / (2.0 * std::numbers::pi * hp.length_cond * hp.k_metal);

        res.r_thermal_total = r_wall_evap + r_wick_evap + r_wick_cond + r_wall_cond;

        return res;
    }
};

} // namespace thermal

int main() {
    constexpr thermal::FluidProps water{
        .name = "Water (100 C)",
        .temp_c = 100.0,
        .density_l = 958.4,
        .density_v = 0.598,
        .h_fg = 2257000.0,
        .surface_tension = 0.0589,
        .viscosity_l = 0.000282,
        .k_fluid = 0.679
    };

    constexpr thermal::HeatPipeGeometry pipe{
        .length_total = 0.200,
        .length_evap = 0.050,
        .length_cond = 0.050,
        .r_outer = 0.0040,
        .r_inner = 0.0033,
        .r_vapor = 0.0025,
        .r_eff_pore = 15e-6,
        .permeability = 1.5e-11,
        .porosity = 0.55,
        .k_metal = 390.0
    };

    if (auto res = thermal::HeatPipeAnalyzer::analyze(pipe, water, 0.0); res.has_value()) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Аналіз теплової трубки (C++20) ===\n";
        std::cout << "Число Мерита:           " << std::scientific << res->merit_number << " Вт/м²\n";
        std::cout << std::fixed;
        std::cout << "Капілярний тиск:       " << res->p_cap_max << " Па\n";
        std::cout << "Капілярний ліміт:      " << res->q_cap_limit << " Вт\n";
        std::cout << "Кипійний ліміт:        " << res->q_boil_limit << " Вт\n";
        std::cout << "Сумарний тепловий опір: " << std::setprecision(4) << res->r_thermal_total << " °C/Вт\n";
    } else {
        std::cerr << "Помилка розрахунку теплової трубки!\n";
    }

    return 0;
}
```
:::

### 4. Фізичний аналіз чисельних результатів тестового запуску

Проаналізуємо числові значення, отримані в результаті виконання програми для тестової мідної трубки діаметром `D = 8 мм` (зовнішній радіус `4.0 мм`) та довжиною `L = 200 мм`:

1. **Максимальний капілярний тиск (`p_cap_max = 7853.3 Па`).** 
   Спечений фітиль із дрібним ефективним радіусом пор `r_eff_pore = 15 мкм` розвиває тиск всмоктування близько 0.078 атмосфери. Цього капілярного всмоктування з запасом вистачає для долання в'язкісного опору рідини.

2. **Капілярний ліміт потужності (`q_cap_limit = 115.4 Вт`).** 
   У горизонтальному положенні одна 8-міліметрова водяна теплова трубка зі спеченим фітилем здатна надійно передавати до 115 Вт теплової потужності. Для охолодження процесора з TDP 230 Вт знадобиться пара таких трубок.

3. **Кипійний ліміт потужності (`q_boil_limit = 248.6 Вт`).** 
   Кипійний ліміт істотно перевищує капілярний ліміт (248.6 Вт проти 115.4 Вт). Це означає, що при даній товщині фітиля (0.8 мм) ядерне кипіння на стінці не настане доти, доки трубка не висохне від перевищення капілярного ліміту.

4. **Еквівалентний тепловий опір (`r_thermal_total = 0.0845 °C/Вт`).** 
   Перепад температур між випаровувачем та конденсатором при передачі потужності 100 Вт становитиме всього `ΔT = Q · R_th = 100 · 0.0845 = 8.45 °C`. Це підтверджує близьку до ідеальної ізотермічність пристрою.

### 5. Аналіз крайових обчислювальних випадків

Під час використання чисельного модуля у розрахункових комплексах необхідно враховувати наступні крайові фізико-математичні випадки:

1. **Перевірка геометричної цілісності (Geometric Sanity Checks).** 
   Геометричні радіуси вхідних параметрів повинні задовольняти суворому порядку вкладеності: `r_outer > r_inner > r_vapor > r_eff_pore > 0`. Порушення цього співвідношення призведе до від'ємних площ або спроби логарифмування від'ємного числа під час розрахунку радіального теплового опору `ln(r_inner / r_vapor)`. У реалізації на C++20 це контролюється поверненням помилки `CalculationError::InvalidGeometry`.

2. **Обробка гравітаційного запирання (Gravity Lockout).** 
   Якщо кут нахилу `φ` є позитивним (випаровувач розміщено вище конденсатора — робота проти сил тяжіння) і гідростатичний протитиск `ΔP_g = ρ_l · g · L · sin φ` перевищує максимальний капілярний тиск `ΔP_cap,max`, наявний тиск всмоктування `available_dp` стає від'ємним. Фізично це означає, що капілярний помп не здатний підняти рідину, циркуляція зупиняється і випаровувач пересихає. Код повертає `0.0` Вт або тип `CalculationError::NegativeAvailablePressure`.

3. **Обчислювальна стійкість плаваючої крапки (Double Precision Stability).** 
   Параметри пористих фітилів оперують мікроскопічними числами (`K ≈ 10⁻¹¹ м²`, `r_eff ≈ 10⁻⁵ м`), тоді як прихована теплота є великим числом (`h_fg ≈ 10⁶ Дж/кг`). Щоб запобігти накопиченню помилок округлення під час множення та ділення крайніх порядків величин, усі розрахунки виконуються із подвійною точністю у форматі `double`.

4. **Методика юніт-тестування термодинамічних модулів.**
   Під час автоматизованого тестування коду слід перевіряти інваріант: для вертикального положення трубки (випаровувач внизу, `φ = -90°`) капілярний ліміт `Q_max,cap` повинен бути більшим, ніж для горизонтального положення (`φ = 0°`), за рахунок позитивної допомоги гравітаційного стовпа рідини.
