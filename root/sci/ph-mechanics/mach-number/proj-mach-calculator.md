# ⚙️ Обчислення параметрів стисливого потоку та класифікація режимів за числом Маха

У цій вставці наведено практичний алгоритм та програмні модулі для обчислення локальної швидкості звуку, числа Маха, класифікації режиму течії та параметрів ізоентропійного гальмування (повна температура, повний тиск, коефіцієнт стисливості).

Обчислення виконуються на основі термодинамічних параметрів набігаючого середовища: статичної температури `T` (Кельвіни), статичного тиску `p` (Паскалі), швидкості потоку `v` (м/с), а також газовмісних констант (показник адіабати `γ` та питома газова стала `R`).

Модуль спроектовано для роботи в системах реального часу (бортові обчислювачі, польотні контролери, аеродинамічні симулятори), тому він не здійснює динамічного виділення пам'яті (пам'ять купи / heap) під час розрахунків і має гарантований складний час виконання `O(1)`.

---

## 1. Фізична модель та покрокова розрахункова схема

Алгоритм базується на термодинаміці адіабатичного гальмування ідеального газу. Для забезпечення числової стійкості алгоритм виконує сувору попередню перевірку вхідних фізичних параметрів на фізичну допустимість: статична температура та тиск повинні бути строго додатними (`T > 0`, `p > 0`), швидкість — невід'ємною (`v ≥ 0`), а показник адіабати — більшим за одиницю (`γ > 1.0`).

Розрахунок складається з п'яти послідовних кроків:

1. **Валідація вхідних даних:** Перевірка меж фізичної коректності аргументів. При виявленні некоректних даних (наприклад, нульової чи від'ємної абсолютної температури або нульового тиску) алгоритм миттєво повертає код помилки або `std::nullopt`, не виконуючи ділення на нуль чи обчислення квадратного кореня з від'ємного числа.
2. **Обчислення локальної швидкості звуку:** За формулою Лапласа `a = √(γ · R · T)`. Для сухого повітря (`γ = 1.4`, `R = 287.058 Дж/(кг·К)`) при `T = 288.15 K` (рівень моря) отримаємо `a ≈ 340.29 м/с`. При політі в стратосфері (`T = 216.65 K`) швидкість звуку падає до `a ≈ 295.07 м/с`.
3. **Обчислення числа Маха:** Безрозмірне відношення `M = v / a`.
4. **Класифікація режиму течії:** Залежно від обчисленого числа Маха потік відноситься до одного з п'яти режимів:
   - `M < 0.3` — нестислий дозвуковий потік (`SUBSONIC_INCOMPRESSIBLE`);
   - `0.3 ≤ M < 0.8` — стислий дозвуковий потік (`SUBSONIC_COMPRESSIBLE`);
   - `0.8 ≤ M ≤ 1.2` — трансзвуковий потік (`TRANSONIC`);
   - `1.2 < M ≤ 5.0` — надзвуковий потік (`SUPERSONIC`);
   - `M > 5.0` — гіперзвуковий потік (`HYPERSONIC`).
5. **Обчислення термодинамічних параметрів гальмування:**
   - Температурний коефіцієнт гальмування: `T₀ / T = 1 + ((γ - 1) / 2) · M²`.
   - Повна температура гальмування: `T₀ = T · (T₀ / T)`.
   - Коефіцієнт тиску гальмування: `p₀ / p = (T₀ / T)^(γ / (γ - 1))`.
   - Повний тиск гальмування: `p₀ = p · (p₀ / p)`.
   - Поправка Прандтля-Ґлауерта для дозвукового стисливого потоку (`M < 0.95`): `F_PG = 1 / √(1 - M²)`.

---

## 2. Покрокове простеження обчислень для реальних польотних режимів

Для детального розуміння роботи алгоритму простежимо числові значення змінних на кожному кроці розрахунку для трьох типових практичних випадків:

### Випадок А: Дозвуковий пасажирський літак (`v = 250 м/с`, `h = 10 000 м`)
- Статичні параметри атмосфери ISA: `T = 223.15 K` (`-50 °C`), `p = 26436 Па`.
- Швидкість звуку: `a = √(1.4 · 287.058 · 223.15) = 299.47 м/с`.
- Число Маха: `M = 250.0 / 299.47 = 0.835`.
- Класифікація: **Трансзвуковий потік** (`TRANSONIC`), оскільки `0.8 ≤ M ≤ 1.2`.
- Коефіцієнт повної температури: `T₀ / T = 1 + 0.2 · (0.835)² = 1.1394`.
- Повна температура: `T₀ = 223.15 · 1.1394 = 254.26 K` (`-18.9 °C`).
- Коефіцієнт повного тиску: `p₀ / p = (1.1394)^3.5 = 1.5833`.
- Повний тиск гальмування: `p₀ = 26436 · 1.5833 = 41857 Па`.

### Випадок Б: Надзвуковий винищувач (`v = 600 м/с`, `h = 11 000 м`)
- Статичні параметри атмосфери ISA: `T = 216.65 K` (`-56.5 °C`), `p = 22632 Па`.
- Швидкість звуку: `a = √(1.4 · 287.058 · 216.65) = 295.07 м/с`.
- Число Маха: `M = 600.0 / 295.07 = 2.033`.
- Класифікація: **Надзвуковий потік** (`SUPERSONIC`), оскільки `1.2 < M ≤ 5.0`.
- Коефіцієнт повної температури: `T₀ / T = 1 + 0.2 · (2.033)² = 1.8267`.
- Повна температура: `T₀ = 216.65 · 1.8267 = 395.79 K` (`+122.6 °C`).
- Коефіцієнт повного тиску: `p₀ / p = (1.8267)^3.5 = 8.214`.
- Повний тиск гальмування: `p₀ = 22632 · 8.214 = 185900 Па`.

---

## 3. Реалізація програмою

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Константи сухого повітря за стандартних умов ISA */
#define DEFAULT_GAMMA 1.4
#define DEFAULT_R_GAS 287.058

typedef enum {
    REGIME_SUBSONIC_INCOMPRESSIBLE,
    REGIME_SUBSONIC_COMPRESSIBLE,
    REGIME_TRANSONIC,
    REGIME_SUPERSONIC,
    REGIME_HYPERSONIC
} FlowRegime;

typedef struct {
    double speed_of_sound;      /* м/с */
    double mach_number;         /* безрозмірне */
    FlowRegime regime;
    double total_temperature;   /* К */
    double total_pressure;      /* Па */
    double prandtl_glauert;     /* фактор стисливості, 0 якщо M >= 1 */
} GasDynamicsResult;

/* Головна функція розрахунку газодинамічних параметрів */
int compute_gas_dynamics(double velocity, double static_temp_k, double static_press_pa,
                         double gamma, double r_gas, GasDynamicsResult *out_res) {
    if (!out_res || static_temp_k <= 0.0 || static_press_pa <= 0.0 || gamma <= 1.0 || r_gas <= 0.0 || velocity < 0.0) {
        return -1; /* Помилка некоректних вхідних даних */
    }

    /* 1. Локальна швидкість звуку */
    double a = sqrt(gamma * r_gas * static_temp_k);
    out_res->speed_of_sound = a;

    /* 2. Число Маха */
    double M = velocity / a;
    out_res->mach_number = M;

    /* 3. Класифікація режиму */
    if (M < 0.3) {
        out_res->regime = REGIME_SUBSONIC_INCOMPRESSIBLE;
    } else if (M < 0.8) {
        out_res->regime = REGIME_SUBSONIC_COMPRESSIBLE;
    } else if (M <= 1.2) {
        out_res->regime = REGIME_TRANSONIC;
    } else if (M <= 5.0) {
        out_res->regime = REGIME_SUPERSONIC;
    } else {
        out_res->regime = REGIME_HYPERSONIC;
    }

    /* 4. Параметри гальмування */
    double temp_ratio = 1.0 + ((gamma - 1.0) / 2.0) * M * M;
    out_res->total_temperature = static_temp_k * temp_ratio;
    
    double press_ratio = pow(temp_ratio, gamma / (gamma - 1.0));
    out_res->total_pressure = static_press_pa * press_ratio;

    /* 5. Поправка Прандтля-Ґлауерта */
    if (M < 0.95) {
        out_res->prandtl_glauert = 1.0 / sqrt(1.0 - M * M);
    } else {
        out_res->prandtl_glauert = 0.0; /* Не застосовується у білязвуковому та надзвуковому режимах */
    }

    return 0;
}

const char* regime_to_string(FlowRegime r) {
    switch (r) {
        case REGIME_SUBSONIC_INCOMPRESSIBLE: return "Дозвуковий (нестислий)";
        case REGIME_SUBSONIC_COMPRESSIBLE:   return "Дозвуковий (стислий)";
        case REGIME_TRANSONIC:               return "Трансзвуковий";
        case REGIME_SUPERSONIC:              return "Надзвуковий";
        case REGIME_HYPERSONIC:              return "Гіперзвуковий";
        default:                             return "Невідомий";
    }
}

int main(void) {
    double v = 550.0;           /* 550 м/с (близько 1980 км/год) */
    double T_static = 216.65;   /* Стратосфера -56.5 °C */
    double p_static = 22632.0;  /* 22.63 кПа на висоті 11 км */

    GasDynamicsResult res;
    if (compute_gas_dynamics(v, T_static, p_static, DEFAULT_GAMMA, DEFAULT_R_GAS, &res) == 0) {
        printf("Швидкість потоку:    %.1f м/с\n", v);
        printf("Швидкість звуку:     %.2f м/с\n", res.speed_of_sound);
        printf("Число Маха:          %.3f\n", res.mach_number);
        printf("Режим течії:         %s\n", regime_to_string(res.regime));
        printf("Повна температура:   %.2f K (Статична: %.2f K)\n", res.total_temperature, T_static);
        printf("Повний тиск:         %.1f Па (Статичний: %.1f Па)\n", res.total_pressure, p_static);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <optional>
#include <string_view>
#include <iomanip>

namespace gas_dynamics {

constexpr double default_gamma = 1.4;
constexpr double default_r_gas = 287.058;

enum class flow_regime {
    subsonic_incompressible,
    subsonic_compressible,
    transonic,
    supersonic,
    hypersonic
};

[[nodiscard]] constexpr std::string_view to_string(flow_regime regime) noexcept {
    switch (regime) {
        case flow_regime::subsonic_incompressible: return "Дозвуковий (нестислий)";
        case flow_regime::subsonic_compressible:   return "Дозвуковий (стислий)";
        case flow_regime::transonic:               return "Трансзвуковий";
        case flow_regime::supersonic:              return "Надзвуковий";
        case flow_regime::hypersonic:              return "Гіперзвуковий";
    }
    return "Невідомий";
}

struct simulation_result {
    double speed_of_sound{};
    double mach_number{};
    flow_regime regime{flow_regime::subsonic_incompressible};
    double total_temperature{};
    double total_pressure{};
    double prandtl_glauert_factor{};
};

[[nodiscard]] std::optional<simulation_result> calculate(
    double velocity_m_s,
    double static_temperature_k,
    double static_pressure_pa,
    double gamma = default_gamma,
    double r_gas = default_r_gas) noexcept 
{
    if (static_temperature_k <= 0.0 || static_pressure_pa <= 0.0 || gamma <= 1.0 || r_gas <= 0.0 || velocity_m_s < 0.0) {
        return std::nullopt;
    }

    const double a = std::sqrt(gamma * r_gas * static_temperature_k);
    const double mach = velocity_m_s / a;

    flow_regime regime = flow_regime::subsonic_incompressible;
    if (mach < 0.3) {
        regime = flow_regime::subsonic_incompressible;
    } else if (mach < 0.8) {
        regime = flow_regime::subsonic_compressible;
    } else if (mach <= 1.2) {
        regime = flow_regime::transonic;
    } else if (mach <= 5.0) {
        regime = flow_regime::supersonic;
    } else {
        regime = flow_regime::hypersonic;
    }

    const double temp_ratio = 1.0 + ((gamma - 1.0) / 2.0) * mach * mach;
    const double press_ratio = std::pow(temp_ratio, gamma / (gamma - 1.0));

    const double pg_factor = (mach < 0.95) ? (1.0 / std::sqrt(1.0 - mach * mach)) : 0.0;

    return simulation_result{
        .speed_of_sound = a,
        .mach_number = mach,
        .regime = regime,
        .total_temperature = static_temperature_k * temp_ratio,
        .total_pressure = static_pressure_pa * press_ratio,
        .prandtl_glauert_factor = pg_factor
    };
}

} // namespace gas_dynamics

int main() {
    constexpr double velocity = 550.0;
    constexpr double static_temp = 216.65;
    constexpr double static_press = 22632.0;

    if (const auto res = gas_dynamics::calculate(velocity, static_temp, static_press)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Швидкість потоку:    " << velocity << " м/с\n";
        std::cout << "Швидкість звуку:     " << res.speed_of_sound << " м/с\n";
        std::cout << "Число Маха:          " << std::setprecision(3) << res.mach_number << "\n";
        std::cout << "Режим течії:         " << gas_dynamics::to_string(res.regime) << "\n";
        std::cout << "Повна температура:   " << std::setprecision(2) << res.total_temperature << " K\n";
        std::cout << "Повний тиск:         " << res.total_pressure << " Па\n";
    }

    return 0;
}
```
:::

---

## 4. Крайові випадки, числова стійкість та оптимізація

При розробці бортового програмного забезпечення необхідно враховувати такі крайові випадки та математичні обмеження:

- **Сингулярність при `M → 1.0`:** Поправка Прандтля-Ґлауерта `1 / √(1 - M²)` прямує до нескінченності при `M = 1.0`. У коді встановлено поріг `M < 0.95`, за яким фактор дорівнює `0.0`. Це захищає програму від переповнення плаваючої коми (FP overflow).
- **Вимірювання статичної температури:** Завжди використовується саме *статична* температура набігаючого потоку `T`, а не температура гальмування `T₀`, виміряна термометром на корпусі літака. Якщо датчик показує температуру гальмування `T_sensor`, статичну температуру обчислити зворотно за допомогою відновлювального коефіцієнта датчика.
- **Оптимізація обчислення степеня:** Вбудована функція `pow()` в C/C++ є відносно повільною. У гарячих циклах контролерів польоту для повітря (`γ = 1.4`) показник степеня `γ / (γ - 1) = 3.5` обчислюють комбінацією квадратного кореня та кубу: `pow(x, 3.5) = x³ · √x`, що прискорює розрахунок у 3–5 разів.
- **Інтеграція з атмосферою ISA:** Для автономних обчислювачів значення статичної температури та тиску беруться з бортового барометричного висотоміра або моделі атмосфери ISA, що дозволяє отримувати точні значення числа Маха незалежно від змінення температури на різних висотах польоту.

---

## 5. Валідаційні тести та автоматична перевірка точності

Для верифікації реалізації програмного модуля газодинамічних розрахунків у складі вбудованого ПЗ застосовують набір автоматизованих юніт-тестів (unit tests), які перевіряють граничні та нормальні значення:

1. **Тест спокою (`v = 0 м/с`):** Число Маха має строго дорівнювати `0.0`, а параметри гальмування `T₀` та `p₀` повинні бути рівними статичним параметрам `T` і `p`.
2. **Тест звукової межі (`M = 1.0`):** При швидкості `v = a` відношення повної температури має дорівнювати `1.2000 ± 1e-4`, а відношення тисків — `1.8929 ± 1e-4`.
3. **Тест надзвукового винищувача (`M = 2.0`):** При політі з `M = 2.0` відношення температур становить `1.8000`, а відношення тисків `7.8240`.
4. **Тест валідації вхідних даних:** При передачі від'ємної температури `T = -10.0 K` або від'ємного тиску функція повинна коректно повертати помилку `-1` або `std::nullopt`, не допускаючи фатального аварійного завершення (crash / segmentation fault) бортової системи.

У високопродуктивних аеродинамічних симуляторах польоту та систем повітряних сигналів функція обчислення газодинаміки викликається у внутрішньому розрахунковому циклі польотного обчислювача з високою частотою (від `100 Гц` до `1000 Гц`). Відсутність побічних ефектів, повної відмови від динамічного виділення пам'яті та системних викликів робить цю реалізацію повністю детермінованою та безпечною для використання в операційних системах реального часу (RTOS, таких як FreeRTOS, VxWorks чи Zephyr).
