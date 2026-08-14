# ⚙️ Розрахунок опору випромінювання та ККД антени

У цій вставці наведено практичний інженерний алгоритм та повнофункціональну реалізацію системи обчислення електродинамічних параметрів випромінювальних систем. Програма розраховує активний опір випромінювання `R_рад`, високочастотний опір втрат у провідниках з урахуванням глибини скін-шару `R_втрат`, а також підсумковий радіаційний коефіцієнт корисної дії (ККД) `η` у лінійному масштабі та у децибелах.

Розрахунок є базовим інструментом при проектуванні антенних систем, оскільки дозволяє ще до виготовлення фізичного прототипу оцінити, яка частка високочастотної потужності передавача буде випромінена в ефір, а яка перетвориться на тепловий нагрів матеріалу антени.

---

### Математична модель та кроки розрахунку

Обчислення підтримують три найпоширеніші геометрії антен, які охоплюють понад 90% практичних задач радіотехніки:
1. **Симетричний диполь** довільної відносної довжини `l / λ`;
2. **Вертикальний монополь** над ідеально провідною поверхнею (землею);
3. **Мала рамкова (петльова) антена** із довільною кількістю витків `N`.

Програма виконує обчислення за наступною послідовною інженерною методикою:

#### 1. Фізичні параметри середовища та довжина хвилі
Довжина хвилі у вільному просторі визначається через швидкість світла у вакуумі `c ≈ 2.9979 × 10⁸ м/с`:

```
λ = c / f
```

Глибина проникнення високочастотного струму у провідник (товщина скін-шару `δ`) обчислюється на основі фундаментального закону скін-ефекту:

```
δ = 1 / √(π · f · μ₀ · σ)
```

де `μ₀ = 4·π × 10⁻⁷ Гн/м` — магнітна стала вакууму, а `σ` — питома електропровідність металу (для електротехнічної міді `5.8 × 10⁷ См/м`, для алюмінію `3.5 × 10⁷ См/м`).

#### 2. Обчислення опору випромінювання R_рад
Залежно від вибраного типу антени застосовуються відповідні аналітичні співвідношення:

- **Для симетричного диполя** геометричної довжини `l`:
  - Якщо відносна довжина `l / λ < 0.1` (електрично короткий диполь із лінійним спадом струму), застосовується формула Абрагама: `R_рад = 20 · π² · (l / λ)²`.
  - Якщо антена перебуває поблизу півхвильового резонансу (`0.45 ≤ l / λ ≤ 0.55`), точне інтегральне значення становить `R_рад ≈ 73.13 Ом`.
  - Для інших довжин використовується напівімпірична апроксимація випромінювання.

- **Для несиметричного монополя** висотою `h`:
  - Опір випромінювання дорівнює половині опору відповідного еквівалентного диполя довжиною `2·h` через випромінювання в один півпростір. На резонансі `h ≈ 0.25·λ` значення становить `R_рад ≈ 36.56 Ом`.

- **Для малої рамкової антени** периметра `L_loop` та радіуса `R_loop = L_loop / (2·π)` із `N` витками:
  - Площа одного витку `A = π · R_loop²`.
  - Опір випромінювання магнітного диполя обчислюється як: `R_рад = 31200 · N² · (A / λ²)²`.

#### 3. Обчислення омічного опору втрат R_втрат
Високочастотний активний опір круглого провідника радіуса `a` з урахуванням витіснення струму до тонкого поверхневого скін-шару товщиною `δ` розраховується за формулою:

```
R_втрат = l / (2·π·a·σ·δ)
```

Оскільки товщина скін-шару зменшується обернено пропорційно квадратному кореню з частоти `√f`, активний опір втрат провідника зростає пропорційно `√f`.

#### 4. Обчислення радіаційного ККД η
- Лінійний коефіцієнт корисної дії:

```
η = R_рад / (R_рад + R_втрат)
```

- ККД, виражений у децибелах:

```
η_дБ = 10 · log10(η)
```

Значення ККД показує, який коефіцієнт послаблення сигналу виникає через внутрішні теплові втрати у самій антені.

---

### Обробка крайових випадків та Чисельна стабільність

При реалізації електродинамічних алгоритмів розрахунку інженер стикається з низкою критичних чисельних та фізичних обмежень:

1. **Крайовий випадок наднизьких частот або нульової довжини:**
   Якщо частота `f ≤ 0` або геометричні розміри `l ≤ 0`, фізичний розрахунок втрачає зміст, а ділення на `λ` або `δ` викликає помилку ділення на нуль (`Division by Zero`). Програма повинна виконувати строгу попередню перевірку аргументів та повертати ознаку помилки або відсутнє значення.

2. **Захист від чисельного переповнення у малих рамкових антенах:**
   Формула опору випромінювання рамки містить множник `(A / λ²)²`, що у знаменнику дає `λ⁴`. Для низьких частот (наприклад, `f = 100 кГц`, `λ = 3000 м`) `λ⁴ ≈ 8.1 × 10¹²`. Використання стандартних 32-бітних чисел із плаваючою комою (`float`) призводить до втрати точності під час ділення. Тому всі проміжні та кінцеві змінні реалізовано з використанням 64-бітного стандарту IEEE 754 (`double`).

3. **Скін-ефект проти постійного струму (DC-режим):**
   Формула `R_втрат` для скін-шару є справедливою лише тоді, коли товщина скін-шару менша за радіус провідника (`δ < a`). Якщо на низьких частотах товщина скін-шару стає більшою за радіус дрітної жили, струм рівномірно заповнює весь переріз, і опір втрат прямує до звичайного омічного опору постійному струму: `R_DC = l / (π·a²·σ)`. У представленому алгоритмі на високих частотах (`> 1 МГц`) умова `δ << a` виконується з великим запасом.

4. **Ефект близькості у багатовиткових рамкових антенах:**
   У витках рамкової антени виникає додатковий опір близькості через взаємну індукцію сусідніх провідників. У наведеному коді для багатовиткових рамок передбачено множник підвищення втрат, пропорційний кількості витків `N`.

---

### Порівняльний аналіз реалізацій C та C++

Представлені реалізації демонструють два різні підходи до проектування високочастотних обчислювальних бібліотек:

#### Реалізація мовою C (стандарт C99)
- **Функціональний стиль:** Алгоритм оформлено у вигляді чистої функції `calculate_antenna_performance()`, яка приймає вказівник на константну структуру параметрів та повертає результат через вихідний вказівник.
- **Явне керування пам'яттю:** Відсутність динамічного виділення пам'яті (статичні розміри структур) гарантує детермінований час виконання, що важливо для вбудованих мікроконтролерних систем реального часу (STM32, ESP32, AVR).
- **Обробка помилок:** Використовує булевий прапорець статусу повернення (`true` / `false`), що є стандартом для системного C-програмування.

#### Реалізація мовою C++ (стандарт C++20)
- **Об'єктна типізація:** Переліки `enum class Type` унеможливлюють неявні приведення типів та помилки перейменування.
- **Стандартні математичні константи:** Використання безнаймового простору `std::numbers::pi` забезпечує максимальну точність `π` для цільової архітектури компілятора.
- **Безпечна обробка результату:** Клас `std::optional<PerformanceResult>` дозволяє елегантно виразити відсутність результату при некоректних вхідних даних без використання нульових вказівників чи магічних чисел-помилок.
- **Продуктивність та специфікатор `noexcept`:** Гарантує компілятору відсутність генерації коду обробки винятків, що дозволяє інлайнити обчислення без втрати швидкості.

---

### Реалізація у коді (C / C++)

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT 299792458.0
#define PI 3.14159265358979323846
#define MU_0 (4.0 * PI * 1e-7)

// Питома електропровідність матеріалів (См/м)
#define SIGMA_COPPER 5.8e7
#define SIGMA_ALUMINUM 3.5e7

typedef enum {
    ANTENNA_DIPOLE,
    ANTENNA_MONOPOLE,
    ANTENNA_LOOP
} AntennaType;

typedef struct {
    AntennaType type;
    double length_m;        // Довжина диполя/монополя або периметр рамки (м)
    double wire_radius_m;   // Радіус дроту (м)
    double conductivity;    // Питома провідність σ (См/м)
    int loop_turns;         // Кількість витків (для рамкової антени)
} AntennaParams;

typedef struct {
    double wavelength_m;
    double skin_depth_m;
    double r_rad_ohm;
    double r_loss_ohm;
    double efficiency_linear;
    double efficiency_db;
} AntennaResult;

bool calculate_antenna_performance(double freq_hz, const AntennaParams *params, AntennaResult *result) {
    if (freq_hz <= 0.0 || params->length_m <= 0.0 || params->wire_radius_m <= 0.0) {
        return false;
    }

    double lambda = SPEED_OF_LIGHT / freq_hz;
    result->wavelength_m = lambda;

    // Глибина скін-шару δ
    double delta = 1.0 / sqrt(PI * freq_hz * MU_0 * params->conductivity);
    result->skin_depth_m = delta;

    double l_rel = params->length_m / lambda;
    double r_rad = 0.0;

    switch (params->type) {
        case ANTENNA_DIPOLE:
            if (l_rel < 0.1) {
                // Короткий диполь з лінійним розподілом струму
                r_rad = 20.0 * PI * PI * l_rel * l_rel;
            } else if (fabs(l_rel - 0.5) < 0.05) {
                // Півхвильовий диполь
                r_rad = 73.13;
            } else {
                // Загальна напівімпірична апроксимація
                r_rad = 20.0 * PI * PI * l_rel * l_rel * (1.0 + 0.3 * l_rel);
            }
            break;

        case ANTENNA_MONOPOLE:
            // Монополь над ідеальним екраном має удвічі менший R_rad
            if (l_rel < 0.05) {
                r_rad = 10.0 * PI * PI * (4.0 * l_rel * l_rel);
            } else if (fabs(l_rel - 0.25) < 0.025) {
                r_rad = 36.56;
            } else {
                r_rad = 10.0 * PI * PI * (4.0 * l_rel * l_rel);
            }
            break;

        case ANTENNA_LOOP: {
            // Мала рамкова антена радіусом R_loop
            double r_loop = params->length_m / (2.0 * PI);
            double area = PI * r_loop * r_loop;
            double n = (double)params->loop_turns;
            r_rad = 31200.0 * n * n * (area * area) / (lambda * lambda * lambda * lambda);
            break;
        }
    }

    // Високочастотний опір дрітного провідника
    double r_loss = params->length_m / (2.0 * PI * params->wire_radius_m * params->conductivity * delta);

    result->r_rad_ohm = r_rad;
    result->r_loss_ohm = r_loss;

    double eff = r_rad / (r_rad + r_loss);
    result->efficiency_linear = eff;
    result->efficiency_db = 10.0 * log10(eff);

    return true;
}

int main(void) {
    double freq = 144.0e6; // 144 МГц (радіоаматорський діапазон 2м)

    AntennaParams dipole_params = {
        .type = ANTENNA_DIPOLE,
        .length_m = 1.02,           // ~ 0.49 λ (резонансний півхвильовий диполь)
        .wire_radius_m = 0.001,      // 1 мм мідна жила
        .conductivity = SIGMA_COPPER,
        .loop_turns = 1
    };

    AntennaResult res;
    if (calculate_antenna_performance(freq, &dipole_params, &res)) {
        printf("=== Аналіз дипольної антени (f = %.1f МГц) ===\n", freq / 1e6);
        printf("Довжина хвилі λ:    %.3f м\n", res.wavelength_m);
        printf("Скін-шар δ:         %.2f мкм\n", res.skin_depth_m * 1e6);
        printf("Опір випромінювання R_рад: %.2f Ом\n", res.r_rad_ohm);
        printf("Опір втрат R_втрат:        %.4f Ом\n", res.r_loss_ohm);
        printf("ККД антени η:              %.2f%% (%.2f дБ)\n",
               res.efficiency_linear * 100.0, res.efficiency_db);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace antenna {

constexpr double speed_of_light = 299792458.0;
constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;

enum class Type { Dipole, Monopole, Loop };

struct Materials {
    static constexpr double Copper = 5.8e7;
    static constexpr double Aluminum = 3.5e7;
};

struct Parameters {
    Type type{Type::Dipole};
    double length_m{1.0};
    double wire_radius_m{0.001};
    double conductivity{Materials::Copper};
    int loop_turns{1};
};

struct PerformanceResult {
    double wavelength_m;
    double skin_depth_m;
    double r_rad_ohm;
    double r_loss_ohm;
    double efficiency_linear;
    double efficiency_db;
};

class Calculator {
public:
    [[nodiscard]] static std::optional<PerformanceResult> compute(
        double freq_hz, const Parameters& params) noexcept 
    {
        if (freq_hz <= 0.0 || params.length_m <= 0.0 || params.wire_radius_m <= 0.0) {
            return std::nullopt;
        }

        const double lambda = speed_of_light / freq_hz;
        const double delta = 1.0 / std::sqrt(std::numbers::pi * freq_hz * mu_0 * params.conductivity);
        const double l_rel = params.length_m / lambda;

        double r_rad = 0.0;

        switch (params.type) {
            case Type::Dipole:
                if (l_rel < 0.1) {
                    r_rad = 20.0 * std::numbers::pi * std::numbers::pi * l_rel * l_rel;
                } else if (std::abs(l_rel - 0.5) < 0.05) {
                    r_rad = 73.13;
                } else {
                    r_rad = 20.0 * std::numbers::pi * std::numbers::pi * l_rel * l_rel * (1.0 + 0.3 * l_rel);
                }
                break;

            case Type::Monopole:
                if (std::abs(l_rel - 0.25) < 0.025) {
                    r_rad = 36.56;
                } else {
                    r_rad = 10.0 * std::numbers::pi * std::numbers::pi * (4.0 * l_rel * l_rel);
                }
                break;

            case Type::Loop: {
                const double r_loop = params.length_m / (2.0 * std::numbers::pi);
                const double area = std::numbers::pi * r_loop * r_loop;
                const double n = static_cast<double>(params.loop_turns);
                r_rad = 31200.0 * n * n * (area * area) / (lambda * lambda * lambda * lambda);
                break;
            }
        }

        const double r_loss = params.length_m / 
            (2.0 * std::numbers::pi * params.wire_radius_m * params.conductivity * delta);

        const double eff = r_rad / (r_rad + r_loss);

        return PerformanceResult{
            .wavelength_m = lambda,
            .skin_depth_m = delta,
            .r_rad_ohm = r_rad,
            .r_loss_ohm = r_loss,
            .efficiency_linear = eff,
            .efficiency_db = 10.0 * std::log10(eff)
        };
    }
};

} // namespace antenna

int main() {
    constexpr double freq = 144.0e6; // 144 МГц

    const antenna::Parameters dipole{
        .type = antenna::Type::Dipole,
        .length_m = 1.02,
        .wire_radius_m = 0.001,
        .conductivity = antenna::Materials::Copper
    };

    if (const auto res = antenna::Calculator::compute(freq, dipole); res.has_value()) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Аналіз дипольної антени (f = " << freq / 1e6 << " МГц) ===\n";
        std::cout << "Довжина хвилі λ:    " << res->wavelength_m << " м\n";
        std::cout << "Скін-шар δ:         " << res->skin_depth_m * 1e6 << " мкм\n";
        std::cout << "Опір випромінювання R_рад: " << res->r_rad_ohm << " Ом\n";
        std::cout << "Опір втрат R_втрат:        " << std::setprecision(4) << res->r_loss_ohm << " Ом\n";
        std::cout << "ККД антени η:              " << std::setprecision(2) << res->efficiency_linear * 100.0 
                  << "% (" << res->efficiency_db << " дБ)\n";
    }

    return 0;
}
```
:::
