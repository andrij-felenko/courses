# ⚙️ Програма розрахунку параметрів спіральної антени

Проектування спіральної антени осьового режиму вимагає точного математичного узгодження фізичних розмірів геометрії спіралі, розмірів екрана-рефлектора та параметрів високочастотного узгоджувача вхідного імпедансу. Найменша відхилення в кроці намотування або діаметрі спіралі зміщує робочу частоту та викликає деградацію кругової поляризації.

Для автоматизації обчислень розроблено програмний калькулятор у двох варіантах — мовою C (стандарт C99) та сучасній ідіоматичній мові C++ (стандарт C++20 / C++23).

---

### Принцип роботи калькулятора та математичні співвідношення

Програма приймає на вхід два ключові інженерні параметри:
1. **Цільову робочу частоту (`f_MHz`):** значення центральної частоти діапазону у мегагерцах (наприклад, 2437 МГц для Wi-Fi/Bluetooth, 1575.42 МГц для GPS L1, 5800 МГц для FPV-відеозв'язку).
2. **Кількість витків спіралі (`N`):** ціле число від 3 до 30, що визначає необхідний коефіцієнт підсилення антени та ширину її діаграми спрямованості.

#### Математичний алгоритм обчислень:
1. **Довжина хвилі у вакуумі:** за вхідною робочою частотою `f` (у мегагерцах, МГц) обчислюється довжина хвилі `λ` (у міліметрах):
   ```
   λ = c / f = 299 792.458 / f_MHz
   ```
2. **Геометрія витка:** для центральної частоти робочого діапазону обирається канонічна довжина кола `C = λ`. Діаметр намотування провідника `D`:
   ```
   D = C / π = λ / π
   ```
3. **Крок намотування спіралі:** при оптимальному куті нахилу `α = 12.8°` (0.2234 радіана) крок `S` становить:
   ```
   S = C · tan(α) = λ · tan(12.8°) ≈ 0.2272 · λ
   ```
4. **Довжина провідника одного витка:** обчислюється як гіпотенуза розгортки:
   ```
   L₀ = √(C² + S²) = √(λ² + S²)
   ```
5. **Загальні габарити:** для спіралі з `N` витків осьова довжина `L = N · S`, а сумарна довжина дроту `L_wire = N · L₀`.
6. **Мінімальний розмір екрана (Ground Plane):** для забезпечення належного відбиття хвилі сторона чи діаметр рефлектора повинен задовольняти умову `D_gp ≥ 0.75 · λ`.
7. **Вхідний імпеданс спіралі:** обчислюється як активний опір `R_in = 140 · (C / λ)`. При `C = λ` опір становить `140 Ом`.
8. **Параметри узгоджувального трансформатора:** для переходу від вхідного опору спіралі `140 Ом` до стандартного 50-омного кабелю обчислюється хвильовий опір чвертьхвильового трансформатора `Z_match = √(50 · 140) ≈ 83.67 Ом` та довжина трансформаторної лінії `L_match = λ / 4`.
9. **Коефіцієнт підсилення (Gain) та ширина променя (HPBW):**
   ```
   G_dBi = 10 · log₁₀ [ 12 · N · (C / λ)² · (S / λ) ]
   HPBW = 52° / [ (C / λ) · √( N · S / λ ) ]
   ```

---

### Структура та архітектура вихідного коду

Розробка програми у двох мовних вкладинках демонструє перехід від процедурного підходу мови C до ідіоматичного безпечного проєктування мовою C++:

- **Версія мовою C (стандарт C99):** використовує просту структуру `HelixAntennaParams` для збереження проміжних та кінцевих результатів обчислення, чисті процедурні функції та стандартний вивід `printf`. Відсутні динамічні виділення пам'яті (`malloc`), що гарантує відсутність витоків пам'яті та високу швидкість виконання на вбудованих мікроконтролерах.
- **Версія мовою C++ (стандарт C++20 / C++23):** реалізує суворе оброблення помилок через мономорфний тип повернення `std::expected<HelixAntennaDesign, CalculationError>`, математичні константи зі стандарту `<numbers>` (`std::numbers::pi`), безпечні числові функції `<cmath>` (`std::hypot`), обчислення у `constexpr`-контексті та стабільне форматування через `<iostream>` та `<iomanip>`.

---

### Вихідний код калькулятора (C та C++)

:::tabs
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для збереження повного набору параметрів антени */
typedef struct {
    double freq_mhz;        /* Робоча частота (МГц) */
    double lambda_mm;       /* Довжина хвилі у вакуумі (мм) */
    double diameter_mm;     /* Діаметр намотування спіралі D (мм) */
    double circumference_mm;/* Довжина кола витка C (мм) */
    double spacing_mm;      /* Крок витка S (мм) */
    double turn_length_mm;  /* Довжина провідника одного витка L0 (мм) */
    double total_length_mm; /* Загальна осьова довжина антени L (мм) */
    double wire_length_mm;  /* Загальна довжина дроту для N витків (мм) */
    double reflector_dim_mm;/* Мінімальний розмір екрана (мм) */
    double r_in_ohm;        /* Вхідний хвильовий опір антени (Ом) */
    double gain_dbi;        /* Коефіцієнт підсилення (дБі) */
    double hpbw_deg;        /* Ширина ДН за рівнем -3 дБ (градуси) */
    double z_match_ohm;     /* Опір 1/4-хвильового трансформатора до 50 Ом */
} HelixAntennaParams;

HelixAntennaParams calculate_helix(double freq_mhz, int num_turns) {
    HelixAntennaParams p;
    p.freq_mhz = freq_mhz;

    /* Швидкість світла c = 299 792.458 км/с */
    p.lambda_mm = 299792.458 / freq_mhz;

    /* Для центральної частоти обираємо довжину кола C = lambda */
    p.circumference_mm = p.lambda_mm;
    p.diameter_mm = p.circumference_mm / M_PI;

    /* Оптимальний кут нахилу alpha = 12.8 градусів (0.2234 радіана) */
    double alpha_rad = 12.8 * M_PI / 180.0;
    p.spacing_mm = p.circumference_mm * tan(alpha_rad);

    /* Довжина дроту одного витка L0 = sqrt(C^2 + S^2) */
    p.turn_length_mm = sqrt(p.circumference_mm * p.circumference_mm + 
                           p.spacing_mm * p.spacing_mm);

    p.total_length_mm = num_turns * p.spacing_mm;
    p.wire_length_mm = num_turns * p.turn_length_mm;

    /* Мінімальний діаметр/сторона рефлектора D_gp >= 0.75 * lambda */
    p.reflector_dim_mm = 0.75 * p.lambda_mm;

    /* Вхідний опір за формулою Крауса: R_in = 140 * (C / lambda) */
    double c_lambda = p.circumference_mm / p.lambda_mm;
    double s_lambda = p.spacing_mm / p.lambda_mm;
    p.r_in_ohm = 140.0 * c_lambda;

    /* Коефіцієнт підсилення: G = 12 * N * (C/lambda)^2 * (S/lambda) */
    double g_linear = 12.0 * num_turns * (c_lambda * c_lambda) * s_lambda;
    p.gain_dbi = 10.0 * log10(g_linear);

    /* Ширина діаграми спрямованості HPBW = 52 / ( (C/lambda) * sqrt(N * S/lambda) ) */
    p.hpbw_deg = 52.0 / (c_lambda * sqrt(num_turns * s_lambda));

    /* Опір чвертьхвильового трансформатора Z_t = sqrt(Z_in * Z_out) */
    p.z_match_ohm = sqrt(50.0 * p.r_in_ohm);

    return p;
}

int main(void) {
    double freq = 2437.0; /* Частота Wi-Fi / Bluetooth (МГц) */
    int turns = 8;        /* 8 витків */

    HelixAntennaParams h = calculate_helix(freq, turns);

    printf("=== Розрахунок спіральної антени (Краус) ===\n");
    printf("Частота:                  %.1f МГц (lambda = %.1f мм)\n", h.freq_mhz, h.lambda_mm);
    printf("Кількість витків N:        %d\n", turns);
    printf("Діаметр спіралі D:        %.2f мм\n", h.diameter_mm);
    printf("Крок витка S:             %.2f мм\n", h.spacing_mm);
    printf("Осьова довжина L:         %.1f мм\n", h.total_length_mm);
    printf("Загальна довжина дроту:   %.1f мм\n", h.wire_length_mm);
    printf("Розмір рефлектора D_gp:   >= %.1f мм\n", h.reflector_dim_mm);
    printf("-------------------------------------------\n");
    printf("Вхідний опір R_in:        %.1f Ом\n", h.r_in_ohm);
    printf("Трансформатор до 50 Ом:   Z0 = %.1f Ом (L = %.1f мм)\n", 
           h.z_match_ohm, h.lambda_mm / 4.0);
    printf("Коефіцієнт підсилення:     %.2f дБі\n", h.gain_dbi);
    printf("Ширина променя (HPBW):    %.1f градусів\n", h.hpbw_deg);

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <string_view>

struct HelixAntennaDesign {
    double freq_mhz;
    double lambda_mm;
    double diameter_mm;
    double spacing_mm;
    double total_length_mm;
    double wire_length_mm;
    double reflector_min_mm;
    double input_impedance_ohm;
    double gain_dbi;
    double hpbw_deg;
    double match_line_impedance_ohm;
};

enum class CalculationError {
    InvalidFrequency,
    InvalidTurnCount
};

constexpr std::string_view error_to_string(CalculationError err) noexcept {
    switch (err) {
        case CalculationError::InvalidFrequency: return "Частота повинна бути більшою за нуль";
        case CalculationError::InvalidTurnCount:  return "Кількість витків повинна бути від 3 до 30";
    }
    return "Невідома помилка";
}

[[nodiscard]] constexpr std::expected<HelixAntennaDesign, CalculationError>
design_helical_antenna(double freq_mhz, int num_turns) noexcept {
    if (freq_mhz <= 0.0) {
        return std::unexpected(CalculationError::InvalidFrequency);
    }
    if (num_turns < 3 || num_turns > 30) {
        return std::unexpected(CalculationError::InvalidTurnCount);
    }

    constexpr double speed_of_light_mm_s = 299792.458;
    const double lambda = speed_of_light_mm_s / freq_mhz;
    const double circumference = lambda; // C = lambda
    const double diameter = circumference / std::numbers::pi;

    // Pitch angle alpha = 12.8 degrees
    constexpr double pitch_angle_rad = 12.8 * std::numbers::pi / 180.0;
    const double spacing = circumference * std::tan(pitch_angle_rad);

    const double turn_length = std::hypot(circumference, spacing);
    const double total_length = num_turns * spacing;
    const double wire_length = num_turns * turn_length;
    const double reflector_dim = 0.75 * lambda;

    const double c_rel = circumference / lambda;
    const double s_rel = spacing / lambda;

    const double r_in = 140.0 * c_rel;
    const double g_lin = 12.0 * num_turns * (c_rel * c_rel) * s_rel;
    const double gain = 10.0 * std::log10(g_lin);

    const double hpbw = 52.0 / (c_rel * std::sqrt(num_turns * s_rel));
    const double z_match = std::sqrt(50.0 * r_in);

    return HelixAntennaDesign{
        .freq_mhz = freq_mhz,
        .lambda_mm = lambda,
        .diameter_mm = diameter,
        .spacing_mm = spacing,
        .total_length_mm = total_length,
        .wire_length_mm = wire_length,
        .reflector_min_mm = reflector_dim,
        .input_impedance_ohm = r_in,
        .gain_dbi = gain,
        .hpbw_deg = hpbw,
        .match_line_impedance_ohm = z_match
    };
}

int main() {
    constexpr double target_freq = 2437.0; // Wi-Fi / Bluetooth
    constexpr int turns_count = 8;

    const auto result = design_helical_antenna(target_freq, turns_count);

    if (!result) {
        std::cerr << "Помилка розрахунку: " << error_to_string(result.error()) << '\n';
        return 1;
    }

    const auto& h = *result;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Розрахунок спіральної антени (C++17/23) ===\n"
              << "Частота:                  " << h.freq_mhz << " МГц (λ = " << h.lambda_mm << " мм)\n"
              << "Кількість витків N:        " << turns_count << "\n"
              << "Діаметр спіралі D:        " << h.diameter_mm << " мм\n"
              << "Крок витка S:             " << h.spacing_mm << " мм\n"
              << "Осьова довжина L:         " << h.total_length_mm << " мм\n"
              << "Загальна довжина дроту:   " << h.wire_length_mm << " мм\n"
              << "Розмір рефлектора D_gp:   >= " << h.reflector_min_mm << " мм\n"
              << "-------------------------------------------\n"
              << "Вхідний опір R_in:        " << h.input_impedance_ohm << " Ом\n"
              << "Трансформатор до 50 Ом:   Z0 = " << h.match_line_impedance_ohm 
              << " Ом (L = " << (h.lambda_mm / 4.0) << " мм)\n"
              << "Коефіцієнт підсилення:     " << h.gain_dbi << " дБі\n"
              << "Ширина променя (HPBW):    " << h.hpbw_deg << " градусів\n";

    return 0;
}
```
:::

---

### Інструкція з компіляції та перевірка результатів

Для практичної компіляції та перевірки роботи програми в операційних системах Linux, macOS або Windows використовують такі стандартні команди:

1. **Компіляція версії мовою C:**
   Для компіляції використовується будь-який стандартний компілятор C99 (GCC, Clang або MSVC):
   ```bash
   gcc -O2 -std=c99 proj-helix-calc.c -o helix_calc -lm
   ```
   Прапорець `-lm` є обов'язковим у компіляторах GCC/Clang під Linux/Unix для підключення системної математичної бібліотеки `libm` (яка містить функції `sqrt`, `log10`, `tan`).

2. **Компіляція версії мовою C++:**
   Версія C++ використовує новітні стандарти C++20 / C++23 (зокрема `std::numbers::pi`, `std::expected` та `std::hypot`):
   ```bash
   g++ -O3 -std=c++23 proj-helix-calc.cpp -o helix_calc_cpp
   ```

3. **Аналіз результатів обчислення (для частоти 2437 МГц та N = 8 витків):**
   - Довжина хвилі у вакуумі становить `λ = 123.0 мм`.
   - Діаметр намотування спіралі `D = 39.15 мм`.
   - Крок намотування `S = 27.95 мм`.
   - Розрахунковий вхідний опір `R_in = 140 Ом`.
   - Необхідний хвильовий опір чвертьхвильового смужкового трансформатора для узгодження з 50-омною лінією дорівнює `Z0 = 83.67 Ом` при довжині смужки `L = 30.75 мм`.
   - Очікуваний коефіцієнт підсилення становить `13.38 дБі` при ширині головного променя `HPBW = 38.6°`.

---

### Інженерні крайові випадки та обмеження застосування

Розроблена програма базується на аналітичних моделях Крауса, які мають чітко визначені межі інженерної застосовності:

- **Найменша кількість витків (`N < 3`):** при `num_turns < 3` режим біжучої хвилі не встигає повністю сформуватися. Відбита хвиля від вільного кінця викликає значні стоячі хвилі, внаслідок чого вхідний опір набуває високої реактивної складової (`X_in ≠ 0`), а поляризація з кругової перетворюється на еліптичну. Калькулятор повертає помилку `CalculationError::InvalidTurnCount`.
- **Верхня межа витків (`N > 30`):** при збільшенні кількості витків понад 30 омічні втрати в дроті та розсіювання хвилі призводять до того, що підсилення антени перестає зростати, виходячи на плато (насичення за підсиленням на рівні `~18.5...19 дБі`). Крім того, різко звужується ширина променя, що ускладнює точне наведення антени на об'єкт.
- **Широкосмуговість узгодження:** при відхиленні частоти від розрахункової центральної частоти `f_0` в межах `±20%` антена зберігає осьовий режим, але для збереження оптимуму КХС на краях діапазону рекомендовано використовувати клиноподібний трансформатор імпедансу замість чвертьхвильового смужкового трансформатора.
