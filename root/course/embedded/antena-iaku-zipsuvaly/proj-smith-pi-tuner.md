# ⚙️ Інженерний розрахунок Pi-ланки узгодження імпедансу для VNA

Коли векторний аналізатор кіл (VNA) вимірює розладнану антену всередині закритого корпусу пристрою, він повертає комплексний коефіцієнт відбиття `S₁₁` або комплексний імпеданс `Z_L = R_L + j·X_L` на робочій частоті `f₀`. Завдання інженера — не просто порахувати теоретичні ємності та індуктивності ідеальної L- чи Pi-ланки, а підібрати реальні номінали зі стандартного ряду E24/E96 (SMD 0402) і перевірити, який залишковий КСВ та коефіцієнт відбиття забезпечить цей фізичний набір деталей.

Нижче наведено робочий інструмент на C та C++, який автоматизує повний цикл розрахунку: від виміряного імпедансу антени до вибору стандартних компонентів, моделювання паразитичних параметрів та розрахунку підсумкового КСВ.

## Архітектура розрахункового модуля

Модуль виконує три послідовні задачі:
1. **Аналітичний розрахунок ідеальної L-ланки**: знаходить точні значення `C` (у пікофарадах) та `L` (у наногенрі) для компенсації реактивності та трансформації активного опору до 50 Ом;
2. **Квантування до стандартного ряду E24**: знаходить найближчі доступні на ринку номінали керамічних конденсаторів (C0G/NP0) та високодобротних котушок індуктивності;
3. **Пряме моделювання фізичного кола**: розраховує фактичний комплексний імпеданс на вході узгоджувальної ланки з реальними компонентами й обчислює фінальний КСВ, зворотні втрати `S₁₁` (дБ) та частку відбитої потужності.

## Топологія узгодження: Low-Pass проти High-Pass

При синтезі реактивної ланки інженер постає перед вибором між конфігураціями низьких частот (Low-Pass: паралельний C, послідовний L) та високих частот (High-Pass: паралельний L, послідовний C). Для антенних трактів бездротових пристроїв (BLE, Wi-Fi, LoRa, Zigbee) майже завжди обирають топологію **Low-Pass**, оскільки вона забезпечує додаткове придушення другої та третьої гармонік передавача (наприклад, 4.88 ГГц та 7.32 ГГц для діапазону 2.44 ГГц). Це суттєво спрощує проходження сертифікаційних тестів на електромагнітну сумісність (EMC/ETSI/FCC).

Паралельний конденсатор із боку джерела закорочує високочастотний шум на землю, а послідовний індуктор із боку антени ефективно відсікає високочастотні паразитні коливання.

## Реалізація алгоритму на C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846
#define Z0 50.0

typedef struct {
    double r;  // активний опір (Ом)
    double x;  // реактивний опір (Ом, + індуктивний, - ємнісний)
} ComplexZ;

typedef struct {
    double c_shunt_pf;    // паралельна ємність (пФ)
    double l_series_nh;   // послідовна індуктивність (нГн)
    double vswr_ideal;    // КСВ з теоретичними номіналами (1.0)
    double c_real_pf;     // підібраний номінал E24 (пФ)
    double l_real_nh;     // підібраний номінал E24 (нГн)
    double vswr_real;     // фактичний КСВ з компонентами E24
    double s11_db_real;   // фактичні зворотні втрати S11 (дБ)
    double refl_power_pct;// частка відбитої потужності (%)
} MatchingResult;

// Стандартний ряд номіналів E24 (мантиси)
static const double E24_VALUES[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};
#define E24_SIZE (sizeof(E24_VALUES) / sizeof(E24_VALUES[0]))

// Підбір найближчого значення зі стандартного ряду E24
static double quantize_to_e24(double val) {
    if (val <= 0.0) return 0.0;
    double exponent = floor(log10(val));
    double mantissa = val / pow(10.0, exponent);
    
    double best = E24_VALUES[0];
    double min_diff = fabs(mantissa - best);
    for (size_t i = 1; i < E24_SIZE; ++i) {
        double diff = fabs(mantissa - E24_VALUES[i]);
        if (diff < min_diff) {
            min_diff = diff;
            best = E24_VALUES[i];
        }
    }
    return best * pow(10.0, exponent);
}

// Розрахунок КСВ за комплексним імпедансом
static double calculate_vswr(ComplexZ z, double *out_s11_db) {
    double num_r = z.r - Z0;
    double num_x = z.x;
    double den_r = z.r + Z0;
    double den_x = z.x;
    
    double num_mag = sqrt(num_r * num_r + num_x * num_x);
    double den_mag = sqrt(den_r * den_r + den_x * den_x);
    if (den_mag == 0.0) return 999.0;
    
    double gamma = num_mag / den_mag;
    if (gamma >= 1.0) gamma = 0.9999;
    
    if (out_s11_db) {
        *out_s11_db = (gamma > 1e-6) ? (20.0 * log10(gamma)) : -120.0;
    }
    return (1.0 + gamma) / (1.0 - gamma);
}

// Розрахунок L-ланки для антени з R_L < 50 Ом
bool calculate_l_match(double freq_hz, ComplexZ z_ant, MatchingResult *res) {
    if (z_ant.r <= 0.0 || z_ant.r >= Z0) {
        return false; // Потрібна інша топологія, якщо R_L >= 50 Ом
    }
    
    double w = 2.0 * PI * freq_hz;
    
    // 1. Теоретичний розрахунок
    double q = sqrt((Z0 / z_ant.r) - 1.0);
    double b_shunt = q / Z0;                  // провідність паралельного конденсатора (См)
    double x_series = (q * z_ant.r) - z_ant.x;// реактивний опір послідовного індуктора (Ом)
    
    res->c_shunt_pf = (b_shunt / w) * 1e12;
    res->l_series_nh = (x_series / w) * 1e9;
    res->vswr_ideal = 1.0;
    
    // 2. Квантування до ряду E24
    res->c_real_pf = quantize_to_e24(res->c_shunt_pf);
    res->l_real_nh = quantize_to_e24(res->l_series_nh);
    
    // 3. Пряме моделювання вхідного імпедансу з компонентами E24
    double c_farads = res->c_real_pf * 1e-12;
    double l_henries = res->l_real_nh * 1e-9;
    
    // Додаємо послідовний індуктор до антени: Z1 = Z_ant + j*w*L
    double z1_r = z_ant.r;
    double z1_x = z_ant.x + (w * l_henries);
    
    // Переходимо до провідності Y1 = 1 / Z1
    double denom1 = z1_r * z1_r + z1_x * z1_x;
    double y1_g = z1_r / denom1;
    double y1_b = -z1_x / denom1;
    
    // Додаємо паралельний конденсатор: Yin = Y1 + j*w*C
    double yin_g = y1_g;
    double yin_b = y1_b + (w * c_farads);
    
    // Повертаємося до імпедансу Zin = 1 / Yin
    double denom_in = yin_g * yin_g + yin_b * yin_b;
    ComplexZ z_in = {
        .r = yin_g / denom_in,
        .x = -yin_b / denom_in
    };
    
    res->vswr_real = calculate_vswr(z_in, &res->s11_db_real);
    double gamma_real = (res->vswr_real - 1.0) / (res->vswr_real + 1.0);
    res->refl_power_pct = gamma_real * gamma_real * 100.0;
    
    return true;
}

int main(void) {
    double freq = 2.44e9; // 2.44 ГГц ISM
    ComplexZ z_detuned = { .r = 15.0, .x = -35.0 }; // розладнана антена в корпусі
    
    MatchingResult res;
    if (calculate_l_match(freq, z_detuned, &res)) {
        printf("--- Узгодження антени 2.44 ГГц ---\n");
        printf("Вхідний імпеданс антени: %.1f + j(%.1f) Ом\n", z_detuned.r, z_detuned.x);
        printf("Теоретичні номінали: C_shunt = %.2f пФ, L_series = %.2f нГн\n", 
               res.c_shunt_pf, res.l_series_nh);
        printf("Реальні номінали E24:  C = %.1f пФ, L = %.1f нГн\n", 
               res.c_real_pf, res.l_real_nh);
        printf("Фактичний КСВ з E24:   %.2f (S11 = %.1f дБ, відбито %.2f%% потужності)\n", 
               res.vswr_real, res.s11_db_real, res.refl_power_pct);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <algorithm>
#include <expected>
#include <string_view>
#include <iomanip>

namespace rf {

inline constexpr double Z0 = 50.0;

struct ComplexZ {
    double r{0.0};  // активний опір (Ом)
    double x{0.0};  // реактивний опір (Ом)
};

struct MatchingResult {
    double c_shunt_pf{0.0};
    double l_series_nh{0.0};
    double c_real_pf{0.0};
    double l_real_nh{0.0};
    double vswr_real{1.0};
    double s11_db_real{-100.0};
    double refl_power_pct{0.0};
};

enum class MatchingError {
    InvalidResistance,
    TopologyNotSupported
};

// Стандартний ряд номіналів E24
inline constexpr std::array<double, 24> E24_VALUES = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

constexpr double quantize_to_e24(double val) noexcept {
    if (val <= 0.0) return 0.0;
    const double exponent = std::floor(std::log10(val));
    const double mantissa = val / std::pow(10.0, exponent);
    
    auto it = std::min_element(E24_VALUES.begin(), E24_VALUES.end(),
        [mantissa](double a, double b) {
            return std::abs(mantissa - a) < std::abs(mantissa - b);
        });
    return *it * std::pow(10.0, exponent);
}

double calculate_vswr(const ComplexZ& z, double& out_s11_db) noexcept {
    const double num_mag = std::hypot(z.r - Z0, z.x);
    const double den_mag = std::hypot(z.r + Z0, z.x);
    if (den_mag == 0.0) return 999.0;
    
    double gamma = std::clamp(num_mag / den_mag, 0.0, 0.9999);
    out_s11_db = (gamma > 1e-6) ? (20.0 * std::log10(gamma)) : -120.0;
    return (1.0 + gamma) / (1.0 - gamma);
}

// Розрахунок L-ланки для імпедансу антени R_L < 50 Ом
std::expected<MatchingResult, MatchingError> calculate_l_match(
    double freq_hz, const ComplexZ& z_ant) noexcept 
{
    if (z_ant.r <= 0.0) return std::unexpected(MatchingError::InvalidResistance);
    if (z_ant.r >= Z0) return std::unexpected(MatchingError::TopologyNotSupported);
    
    const double w = 2.0 * std::numbers::pi * freq_hz;
    
    // 1. Теоретичний розрахунок L-ланки
    const double q = std::sqrt((Z0 / z_ant.r) - 1.0);
    const double b_shunt = q / Z0;
    const double x_series = (q * z_ant.r) - z_ant.x;
    
    MatchingResult res{};
    res.c_shunt_pf = (b_shunt / w) * 1e12;
    res.l_series_nh = (x_series / w) * 1e9;
    
    // 2. Квантування до ряду E24
    res.c_real_pf = quantize_to_e24(res.c_shunt_pf);
    res.l_real_nh = quantize_to_e24(res.l_series_nh);
    
    // 3. Пряме моделювання вхідного імпедансу
    const double c_farads = res.c_real_pf * 1e-12;
    const double l_henries = res.l_real_nh * 1e-9;
    
    // Z1 = Z_ant + j*w*L
    const double z1_r = z_ant.r;
    const double z1_x = z_ant.x + (w * l_henries);
    
    // Y1 = 1 / Z1
    const double denom1 = z1_r * z1_r + z1_x * z1_x;
    const double y1_g = z1_r / denom1;
    const double y1_b = -z1_x / denom1;
    
    // Yin = Y1 + j*w*C
    const double yin_g = y1_g;
    const double yin_b = y1_b + (w * c_farads);
    
    // Zin = 1 / Yin
    const double denom_in = yin_g * yin_g + yin_b * yin_b;
    const ComplexZ z_in{
        .r = yin_g / denom_in,
        .x = -yin_b / denom_in
    };
    
    res.vswr_real = calculate_vswr(z_in, res.s11_db_real);
    const double gamma_real = (res.vswr_real - 1.0) / (res.vswr_real + 1.0);
    res.refl_power_pct = gamma_real * gamma_real * 100.0;
    
    return res;
}

} // namespace rf

int main() {
    constexpr double freq = 2.44e9;
    constexpr rf::ComplexZ z_detuned{.r = 15.0, .x = -35.0};
    
    auto match = rf::calculate_l_match(freq, z_detuned);
    if (match.has_value()) {
        const auto& res = match.value();
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- Узгодження антени 2.44 ГГц (C++) ---\n";
        std::cout << "Вхідний імпеданс антени: " << z_detuned.r << " + j(" << z_detuned.x << ") Ом\n";
        std::cout << "Теоретичні номінали: C_shunt = " << res.c_shunt_pf << " пФ, L_series = " << res.l_series_nh << " нГн\n";
        std::cout << "Реальні номінали E24:  C = " << res.c_real_pf << " пФ, L = " << res.l_real_nh << " нГн\n";
        std::cout << "Фактичний КСВ з E24:   " << res.vswr_real << " (S11 = " << res.s11_db_real 
                  << " дБ, відбито " << res.refl_power_pct << "% потужності)\n";
    }
    return 0;
}
```
:::

## Інженерні пастки при виборі компонентів

При перенесенні розрахованих номіналів на друковану плату слід враховувати три критичні паразитичні ефекти:

1. **Власна резонансна частота (SRF / Self-Resonant Frequency)**: котушка індуктивності номіналом 3.8 нГн на частоті 2.44 ГГц повинна мати власну паразитну ємність `C_par < 0.15` пФ, щоб її SRF перевищувала 6–8 ГГц. Якщо вибрати стандартний дросельний індуктор для кіл живлення замість високочастотного керамічного чи дротяного RF-індуктора (наприклад, серій Murata LQG15 / LQW15 або Coilcraft 0402HP), на частоті 2.4 ГГц він перетвориться на конденсатор через домінування власної міжевиткової ємності;
2. **Паразитна ємність контактних майданчиків (Pad Capacitance)**: контактний майданчик під SMD-компонент типорозміру 0402 над суцільним полігоном землі на стандартній платі товщиною 1.0 мм (FR-4) додає приблизно 0.15–0.25 пФ паралельної паразитної ємності. На частотах 2.4–5.8 ГГц два таких майданчики можуть подвоїти еквівалентну ємність ланки, якщо номінал становить 0.5–1.0 пФ. Для компенсації під контактними майданчиками RF-елементів роблять локальний виріз у першому внутрішньому шарі землі (Ground Cutout under Pads);
3. **Добротність конденсаторів (Q-factor)**: для паралельного конденсатора необхідно використовувати діелектрик класу C0G/NP0 (наприклад, Murata GJM або GRM серій). Конденсатори загального застосування з діелектриком X5R/X7R мають високий тангенс кута втрат `tan(δ) > 0.02` на частотах вище 1 ГГц і розсіюють до 30–50% енергії корисного сигналу у вигляді тепла прямо всередині керамічного корпусу компонента;
4. **Паразитна індуктивність перехідних отворів (Via Inductance)**: перехідний отвір (via) діаметром 0.3 мм у платі товщиною 1.0 мм додає приблизно 0.8–1.2 нГн паразитної індуктивності між контактним майданчиком заземленого конденсатора та суцільним полігоном GND. На частоті 2.44 ГГц 1 нГн індуктивності дає додатковий реактивний опір `X_via = 2·π·f·L ≈ +15.3` Ом, що кардинально зміщує точку заземлення паралельного конденсатора й розладнує розрахункову ланку. Для мінімізації паразитної індуктивності заземлювальні майданчики Pi-контуру прошивають двома паралельними отворами, розміщеними впритул до виводу компонента.

## Практична методика налаштування за допомогою NanoVNA

Процес інженерної підгонки узгоджувальної ланки на робочому столі складається з п'яти кроків:

1. **Калібрування площини вимірювання (SOLT Calibration)**: калібрування аналізатора кіл виконується за методикою Short-Open-Load-Through безпосередньо на кінці тонкого вимірювального коаксіального кабелю. Якщо кабель впаюється на плату, площину калібрування зсувають у точку впайки за допомогою функції Port Extension (компенсація затримки кабелю);
2. **Вимірювання "голого" імпедансу антени**: послідовний індуктор замінюють нульовим резистором (SMD jumper), а паралельні конденсатори не встановлюють (Not Fitted / DNP). Плату закривають у корпус, підключають до VNA і записують вхідний імпеданс `Z_ant = R_L + j·X_L` у форматі Touchstone (`.s1p`);
3. **Розрахунок номіналів**: отриманий імпеданс передається на вхід нашої розрахункової утиліти для визначення номіналів `C_sh` та `L_ser`;
4. **Запаювання компонентів**: на плату встановлюються розраховані прецизійні RF-компоненти ряду E24/E96;
5. **Контрольне вимірювання**: корпус повторно збирається, закручуються всі металеві гвинти, і на екрані VNA перевіряється, що коефіцієнт відбиття `S₁₁` опустився нижче позначки `−15` дБ у всій робочій смузі частот.
