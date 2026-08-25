# ⚙️ Калькулятор ефективної апертури та параметрів антени

Практичний модуль для обчислення ефективної апертури `A_e`, геометричного розміру параболічних апертур, коефіцієнта ефективності `η_a` та розрахунку прийнятої потужності за рівнянням Фрііса. Інженерний код розроблено двома мовами — C (C99/C11) та C++ (C++20/C++23) — для застосування у вбудованих системах управління трансіверами (firmware), програмах обробки телеметрії та високопродуктивних НВЧ-симуляторах радіоліній.

## 1. Архітектура та математична основа інструменту

Модуль вирішує завдання автоматизованого перетворення між трьома основними уявленнями антенних характеристик, які використовуються на різних етапах проектування радіосистем:

1. **Просторова апертура:** Обчислення ефективної площі перехоплення `A_e` у квадратних метрах (`м²`) на основі робочої частоти сигналу `f` та паспортного підсилення антени `G_dBi`.
2. **Геометрична площа:** Визначення еквівалентного фізичного діаметра параболічного дзеркала `D` за заданого коефіцієнта ефективності апертури `η_a`.
3. **Енергетика прийому:** Розрахунок кінцевої прийнятої потужності у ватах (`Вт`) та децибел-міліватах (`дБм`) від вхідної густини потоку енергії `S` (`Вт/м²` або `дБВт/м²`).

Математичний алгоритм обчислень спирається на такі фундаментальні співвідношення електродинаміки:

```
λ = c / f                             [довжина електромагнітної хвилі у вакуумі]
G_linear = 10^(G_dBi / 10)            [перетворення підсилення з дБі у лінійний масштаб]
A_e = (λ² / (4π)) · G_linear          [фундаментальна ефективна апертура антени]
A_phys = A_e / η_a                    [фізична площа дзеркала за ефективності η_a]
D = √(4 · A_phys / π)                 [геометричний діаметр круглої параболи]
P_r = S · A_e                         [прийнята потужність від густини потоку S]
```

---

## 2. Реалізація у коді (C та C++)

Нижче наведено подвійну реалізацію модуля:
- **Класичний модуль мовою C:** Застосовує строгий захист від нульових вказівників, явні коди повернення помилок та структуру передачі параметрів за посиланням, що є стандартом для мікроконтролерних систем (STM32, ESP32, Nordic nRF52) та ядерних драйверів.
- **Сучасна реалізація на C++20/C++23:** Використовує монадичні комбінатори помилок `std::expected`, стале обчислення `constexpr` під час компіляції, безпечні зрізи пам'яті `std::span` та форматування `std::format` без виділення динамічної пам'яті у купі (heap).

:::tabs
```c
/* aperture_calc.h — Професійний калькулятор апертури антени (C99/C11) */
#ifndef APERTURE_CALC_H
#define APERTURE_CALC_H

#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#define SPEED_OF_LIGHT 299792458.0 /* швидкість світла у вакуумі, м/с */
#define M_PI_CONST     3.14159265358979323846

/* Структура вхідних параметрів антени */
typedef struct {
    double frequency_hz;   /* Частота сигналу у Гц (f > 0) */
    double gain_dbi;       /* Підсилення антени у дБі */
    double efficiency;     /* Коефіцієнт ефективності η_a (0.0 ... 1.0) */
} antenna_params_t;

/* Структура розрахованих результатів */
typedef struct {
    double wavelength_m;      /* Довжина хвилі λ, м */
    double effective_area_m2; /* Ефективна апертура A_e, м² */
    double physical_area_m2;  /* Фізична площа A_phys (якщо η_a > 0), м² */
    double dish_diameter_m;   /* Еквівалентний діаметр параболи D, м */
} aperture_result_t;

/* Перелічення кодів помилок */
typedef enum {
    APERTURE_OK = 0,
    APERTURE_ERR_NULL_PTR,
    APERTURE_ERR_INVALID_FREQ,
    APERTURE_ERR_INVALID_EFFICIENCY
} aperture_error_t;

/**
 * @brief Обчислює параметри ефективної та фізичної апертури антени.
 * @param params Вказівник на вхідні параметри антени.
 * @param result Вказівник на структуру для запису результатів.
 * @return Код помилки APERTURE_OK у разі успіху.
 */
aperture_error_t calculate_aperture(const antenna_params_t* params, aperture_result_t* result) {
    if (!params || !result) {
        return APERTURE_ERR_NULL_PTR;
    }
    if (params->frequency_hz <= 0.0) {
        return APERTURE_ERR_INVALID_FREQ;
    }
    if (params->efficiency < 0.0 || params->efficiency > 1.0) {
        return APERTURE_ERR_INVALID_EFFICIENCY;
    }

    /* 1. Обчислюємо довжину хвилі λ = c / f */
    double lambda = SPEED_OF_LIGHT / params->frequency_hz;

    /* 2. Лінеаризуємо підсилення: G_linear = 10^(G_dBi / 10) */
    double g_linear = pow(10.0, params->gain_dbi / 10.0);

    /* 3. Ефективна апертура A_e = (λ² / 4π) · G_linear */
    double a_e = (lambda * lambda / (4.0 * M_PI_CONST)) * g_linear;

    result->wavelength_m = lambda;
    result->effective_area_m2 = a_e;

    /* 4. Фізичні розміри за наявності ефективності η_a > 0 */
    if (params->efficiency > 0.0) {
        result->physical_area_m2 = a_e / params->efficiency;
        result->dish_diameter_m = sqrt(4.0 * result->physical_area_m2 / M_PI_CONST);
    } else {
        result->physical_area_m2 = 0.0;
        result->dish_diameter_m = 0.0;
    }

    return APERTURE_OK;
}

/**
 * @brief Обчислює прийняту потужність від густини потоку S (Вт/м²).
 */
double calculate_received_power_watts(double power_density_w_m2, double effective_area_m2) {
    if (power_density_w_m2 < 0.0 || effective_area_m2 < 0.0) {
        return 0.0;
    }
    return power_density_w_m2 * effective_area_m2;
}

#endif /* APERTURE_CALC_H */
```
```cpp
// aperture_calc.hpp — Сучасний ідіоматичний модуль на C++20 / C++23
#ifndef APERTURE_CALC_HPP
#define APERTURE_CALC_HPP

#include <cmath>
#include <numbers>
#include <expected>
#include <span>
#include <vector>
#include <iostream>
#include <format>

namespace rf {

constexpr double speed_of_light = 299'792'458.0; // швидкість світла, м/с

struct AntennaParams {
    double frequency_hz{0.0};
    double gain_dbi{0.0};
    double efficiency{0.60}; // типова ефективність 60%
};

struct ApertureResult {
    double wavelength_m{0.0};
    double effective_area_m2{0.0};
    double physical_area_m2{0.0};
    double dish_diameter_m{0.0};
};

enum class ApertureError {
    InvalidFrequency,
    InvalidEfficiency
};

// Обчислення апертури з використанням std::expected (C++23)
[[nodiscard]] constexpr std::expected<ApertureResult, ApertureError>
calculate_aperture(const AntennaParams& params) noexcept {
    if (params.frequency_hz <= 0.0) {
        return std::unexpected(ApertureError::InvalidFrequency);
    }
    if (params.efficiency < 0.0 || params.efficiency > 1.0) {
        return std::unexpected(ApertureError::InvalidEfficiency);
    }

    const double lambda = speed_of_light / params.frequency_hz;
    const double g_linear = std::pow(10.0, params.gain_dbi / 10.0);

    const double a_e = (lambda * lambda / (4.0 * std::numbers::pi)) * g_linear;

    ApertureResult res{};
    res.wavelength_m = lambda;
    res.effective_area_m2 = a_e;

    if (params.efficiency > 0.0) {
        res.physical_area_m2 = a_e / params.efficiency;
        res.dish_diameter_m = std::sqrt(4.0 * res.physical_area_m2 / std::numbers::pi);
    }

    return res;
}

// Розрахунок прийнятої потужності у дБм за вхідної густини потоку S (дБВт/м²)
[[nodiscard]] constexpr double power_received_dbm(double S_dbw_m2, double a_e_m2) noexcept {
    const double a_e_db = 10.0 * std::log10(a_e_m2);
    const double p_r_dbw = S_dbw_m2 + a_e_db;
    return p_r_dbw + 30.0; // перетворення з дБВт у дБм
}

// Пакетний аналіз антенного масиву через std::span
inline void print_aperture_report(std::span<const AntennaParams> antennas) {
    size_t idx = 0;
    for (const auto& ant : antennas) {
        auto res = calculate_aperture(ant);
        if (res) {
            std::cout << std::format(
                "Антена #{}: {:.2f} ГГц, {:.1f} дБі\n"
                "  Довжина хвилі λ:   {:.2f} мм\n"
                "  Ефективна площа A_e: {:.6f} м² ({:.2f} см²)\n"
                "  Діаметр тарілки D:   {:.2f} м (при η = {:.0f}%)\n\n",
                ++idx, ant.frequency_hz / 1e9, ant.gain_dbi,
                res->wavelength_m * 1000.0,
                res->effective_area_m2, res->effective_area_m2 * 10000.0,
                res->dish_diameter_m, ant.efficiency * 100.0
            );
        }
    }
}

} // namespace rf

#endif // APERTURE_CALC_HPP
```
:::

---

## 3. Детальний інженерний розбір пасток та крайових випадків у коді

Під час проектування ПЗ для радіосистем, обробки даних супутникових каналів зв'язку та моделювання радарних профілів розробники стикаються з низкою підступних помилок, які можуть викривити результати обчислень на декілька порядків:

### 1. Пастка логарифмічного підсилення (дБі проти лінійного розмаху)
Паспортне підсилення антени в інженерній документації завжди подається у логарифмічних децибелах відносно ізотропного випромінювача (`дБі`). Найпоширенішою помилкою є безпосереднє підставляння значення `gain_dbi` (наприклад, `24.0`) у формулу `A_e = (λ² / 4π) · G`.

Формула апертури вимагає **чисто лінійного коефіцієнта** `G_linear = 10^(gain_dbi / 10)`. Наприклад:
- Для антени з підсиленням `3 дБі` лінійний коефіцієнт дорівнює `2.0`.
- Для антени з підсиленням `20 дБі` лінійний коефіцієнт дорівнює `100.0`.
- Для супутникової тарілки `40 дБі` лінійний коефіцієнт становить `10 000.0`.

Помилкове використання значення 40 замість 10 000 у коді призводить до заниження розрахованої ефективної площі антени у 250 разів (−24 дБ помилки у бюджеті радіолінії).

### 2. Розмежування апертурної (η_a) та омічної (e_r) ефективності
У реальних антенних розрахунках плутають два абсолютно різні коефіцієнти ефективності:
- **Коефіцієнт ефективності апертури (`η_a`):** Суто геометрична величина, що характеризує нерівномірність освітлення рефлектора, переливання енергії через краї та затінення опромінювачем. Вона використовується **виключно** для обчислення фізичних габаритів параболічного дзеркала: `A_phys = A_e / η_a`.
- **Коефіцієнт омічної ефективності випромінювання (`e_r`):** Характеризує теплові втрати у металі та кабелі. Цей коефіцієнт **уже включений** у паспортне підсилення антени `G = e_r · D`.

Спроба повторно помножити обчислену ефективну апертуру `A_e` на омічну ефективність у коді є критичною помилкою подвійного врахування втрат.

### 3. Чисельна точність при роботі з ЕВЧ-діапазоном (30…300 ГГц)
На надвисоких частотах (міліметрові та субміліметрові хвилі) довжина хвилі падає до кількох міліметрів (`λ = 1 мм` на 300 ГГц, де `λ² = 10⁻⁶ м²`). Для малогабаритних ненапрямлених антен значення ефективної апертури становить порядок `10⁻⁷ … 10⁻⁸ м²`.

Якщо для накопичувальних розрахунків у багатовузлових сітках застосовувати типи із плаваючою крапкою одинарної точності `float` (які мають лише 23 біти мантиси, тобто близько 7 значущих десяткових цифр), каскадне множення малої апертури на великі відстані спричиняє втрату точності під час підсумовування з іншими компонентами бюджету. Модуль гарантує високу точність завдяки використанню стандарту `double` (IEEE 754 float64 з 53 бітами мантиси).

### 4. Оцінка меж фізичного діаметра параболи
Коли функція `calculate_aperture()` обчислює еквівалентний діаметр параболи `D`, параметр `efficiency` перевіряється на входження в інтервал `(0.0, 1.0]`. Якщо передати `efficiency = 0.0` (що характерно для уявної ізотропної антени, яка взагалі не має фізичного дзеркала), код уникає ділення на нуль, повертаючи `physical_area_m2 = 0.0` та `dish_diameter_m = 0.0`.

### 5. Практичний виклик коду в інженерних проектах

Нижче наведено приклад застосування C++ модуля для порівняльного розрахунку трьох антен різних діапазонів (Wi-Fi 2.4 ГГц, супутниковий Ku-діапазон 12 ГГц та радіорелейка E-band 70 ГГц):

```cpp
#include "aperture_calc.hpp"
#include <array>

int main() {
    const std::array<rf::AntennaParams, 3> system_antennas{{
        {.frequency_hz = 2.4e9,  .gain_dbi = 2.15, .efficiency = 1.00}, // Dipole 2.4 GHz
        {.frequency_hz = 12.0e9, .gain_dbi = 36.0, .efficiency = 0.65}, // Ku-band Dish 60cm
        {.frequency_hz = 70.0e9, .gain_dbi = 45.0, .efficiency = 0.55}  // E-band Millimeter Dish
    }};

    std::cout << "=== ЗВІТ ЕФЕКТИВНОЇ АПЕРТУРИ СИСТЕМИ ===\n\n";
    rf::print_aperture_report(system_antennas);

    return 0;
}
```

Цей приклад демонструє, як наочно порівняти ефективні площі антен різних частотних діапазонів та оцінити реальні фізичні габарити обладнання перед виїздом на монтаж радіолінії.
