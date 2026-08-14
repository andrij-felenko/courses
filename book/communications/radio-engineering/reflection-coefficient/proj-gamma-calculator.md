# ⚙️ Програмний розрахунок комплексного коефіцієнта відбиття та лінійних параметрів ВЧ-тракту

Цей практичний інструментарій містить повнофункціональний програмний модуль для обчислення комплексного коефіцієнта відбиття `Γ`, коефіцієнта стоячої хвилі (КСХ/VSWR), втрат на відбиття (Return Loss), втрат на неузгодженні (Mismatch Loss) та автоматичної трансформації комплексного імпедансу вздовж лінії передачі з урахуванням її згасання та коефіцієнта укорочення.

### Фізико-математична методологія та архітектура модуля

У сучасній високочастотній інженерії та вимірювальних комплексах векторних аналізаторів кіл (VNA) програмний перерахунок параметрів неузгодження виконується на кожному кроці сканування частоти. Завдання даного модуля полягає в забезпеченні високої обчислювальної точності, стійкості до крайніх фізичних режимів (коротке замикання, розрив, нульове згасання) та гарантованої відсутності невизначених станів (таких як ділення на нуль або взяття логарифма від нуля).

Алгоритм приймає на вхід комплексний імпеданс навантаження `Z_L = R_L + j X_L` (Ом) та фізичні характеристики лінії передачі, після чого послідовно виконує п'ять обчислювальних етапів.

#### 1. Розрахунок хвильової довжини та фазової сталої
Швидкість поширення електромагнітної хвилі `v_p` у будь-якому діелектрику є меншою за швидкість світла у вакуумі `c₀ ≈ 299792458 м/с` і визначається коефіцієнтом укорочення `v_f` (`velocity factor`): 

```
v_p = c₀ · v_f
```

Наприклад, для стандартного коаксіального кабелю RG-58 із суцільним поліетиленовим діелектриком `v_f ≈ 0.66`; для тефлонового кабелю (PTFE) `v_f ≈ 0.70`; а для мікросмугової лінії на друкованій платі зі склотекстоліту FR4 `v_f ≈ 0.55–0.62` залежно від товщини та покриття.

Фазова стала `β` визначає просторову швидкість наростання фази хвилі в радіанах на метр вздовж лінії передачі:

```
β = 2π / λ = 2π · f / (c₀ · v_f)
```

#### 2. Переведення згасання з дБ/м у Непери/м
У датушитах високочастотних кабелів згасання вказують у логарифмічних одиницях `дБ/м`. Проте в комплексних показниках експоненти `exp(−γ l)` згасання має вимірюватися у натуральних одиницях — Неперах на метр (Нп/м). 

Зв'язок між логарифмами з основою 10 та основою `e` визначається фундаментальним співвідношенням:

```
1 Нп = 20 / ln(10) дБ ≈ 8.685889638 дБ
```

Тому коефіцієнт згасання `α` у Неперах на метр обчислюється як:

```
α_Np = α_dB / 8.685889638
```

#### 3. Обчислення первинного коефіцієнта відбиття на навантаженні `Γ_L`
Комплексне значення обчислюється за базовою білінійною формулою:

```
Γ_L = (Z_L − Z₀) / (Z_L + Z₀)
```

Модуль `|Γ_L| = √(Re(Γ_L)² + Im(Γ_L)²)` описує амплітудне відношення відбитої хвилі до падаючої, а фазовий кут `φ = arctan2(Im(Γ_L), Re(Γ_L))` — фазовий зсув у радіанах (із подальшим переведенням у градуси).

#### 4. Обчислення похідних параметрів неузгодження (КСХ, RL, ML)
- **КСХ (VSWR):** обчислюється за формулою `(1 + |Γ|) / (1 − |Γ|)`. Якщо `|Γ| → 1` (ідеальне коротке замикання або розрив), знаменник прямує до нуля. Алгоритм містить захисну перевірку: при `|Γ| ≥ 0.99999` значення КСХ обмежується верхньою планкою `999.99`, що запобігає виникненню винятку `Infinity`.
- **Return Loss (дБ):** обчислюється як `−20 log₁₀(|Γ|)`. При ідеальному узгодженні `|Γ| → 0` значення логарифма прямує до мінус нескінченності. Програма захищає обчислення: при `|Γ| < 1e-12` значення `Return Loss` прирівнюється до максимального практичного порогу `240.0 дБ`.
- **Mismatch Loss (дБ):** обчислюється як `−10 log₁₀(1 − |Γ|²)`. Описує втрату активної потужності суто через відбиття.

#### 5. Трансформація `Γ` та імпедансу `Z_in` вздовж лінії
Комплексний коефіцієнт відбиття на початку лінії довжиною `l` обчислюється шляхом множення на комплексний показник поширення:

```
Γ_in = Γ_L · exp(−2 α l) · exp(−j 2 β l)
```

Після знаходження `Γ_in` зворотним перетворенням обчислюється вхідний комплексний імпеданс лінії:

```
Z_in = Z₀ · (1 + Γ_in) / (1 − Γ_in)
```

### Особливості проектування коду трьома мовами

Розроблений інструментарій подано у трьох ідіоматичних варіантах:

- **C++ (стандарт C++23):** використовує сучасний шаблон `std::expected<ReflectionResult, RfError>` замість винятків `try/catch` або застарілих кодів помилок. Специфікатори `[[nodiscard]]` та `constexpr` гарантують контроль результату на етапі компіляції. Математичні операції спираються на стандартний клас `std::complex<double>` та константи з шапки `<numbers>`.
- **C (стандарт C99/C11):** написаний без зовнішніх залежностей із власною явною структурою `Complex` та швидкими `inline`-функціями для комплексного додавання, віднімання, множення, ділення та експоненти. Код повністю сумісний із вбудованими системами (MCU, bare-metal).
- **Python (версії 3.10+):** використовує нативний тип `complex`, модуль `cmath` для роботи з полярними координатами та фазами і повертає структурований словник із результатами.

### Реалізація модуля

:::tabs
```cpp
#include <iostream>
#include <complex>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

namespace rf {

// Структура фізичних параметрів лінії передачі
struct LineParams {
    double z0 = 50.0;              // Хвильовий опір лінії (Ом)
    double frequency_hz = 1e9;     // Частота сигналу (Гц)
    double length_m = 0.0;         // Фізична довжина лінії (м)
    double velocity_factor = 0.66; // Коефіцієнт укорочення хвилі
    double attenuation_db_m = 0.0; // Згасання лінії (дБ/м)
};

// Повний підсумок розрахунку ВЧ-тракту
struct ReflectionResult {
    std::complex<double> gamma_load; // Комплексний Γ на навантаженні
    double gamma_mag;                // Модуль |Γ|
    double gamma_phase_deg;         // Фаза Γ (градуси)
    double vswr;                     // КСХ (VSWR)
    double return_loss_db;           // Втрати на відбиття (дБ)
    double mismatch_loss_db;         // Втрати на неузгодженні (дБ)
    double power_transmitted_pct;    // Передана потужність (%)
    double power_reflected_pct;      // Відбита потужність (%)
    std::complex<double> gamma_input;// Комплексний Γ на вході лінії
    std::complex<double> z_input;    // Вхідний імпеданс Z_in (Ом)
};

// Типізована перелічувана помилка розрахунку
enum class RfError {
    InvalidZ0,
    InvalidFrequency,
    InvalidVelocityFactor,
    InvalidLength
};

[[nodiscard]] constexpr std::string_view to_string(RfError err) noexcept {
    switch (err) {
        case RfError::InvalidZ0: 
            return "Хвильовий опір Z0 має бути суворо додатним";
        case RfError::InvalidFrequency: 
            return "Частота сигналу має бути додатною";
        case RfError::InvalidVelocityFactor: 
            return "Коефіцієнт укорочення має бути в межах (0.0, 1.0]";
        case RfError::InvalidLength: 
            return "Довжина лінії не може бути від'ємною";
    }
    return "Невідома помилка розрахунку";
}

// Головна функція обчислення параметрів неузгодження (C++23 std::expected)
[[nodiscard]] std::expected<ReflectionResult, RfError> calculate_reflection(
    std::complex<double> z_load,
    const LineParams& line) noexcept 
{
    if (line.z0 <= 0.0) return std::unexpected(RfError::InvalidZ0);
    if (line.frequency_hz <= 0.0) return std::unexpected(RfError::InvalidFrequency);
    if (line.velocity_factor <= 0.0 || line.velocity_factor > 1.0) {
        return std::unexpected(RfError::InvalidVelocityFactor);
    }
    if (line.length_m < 0.0) return std::unexpected(RfError::InvalidLength);

    constexpr double c0 = 299792458.0; // Швидкість світла у вакуумі (м/с)
    const double v_phase = c0 * line.velocity_factor;
    const double wavelength = v_phase / line.frequency_hz;
    const double beta = 2.0 * std::numbers::pi / wavelength; // Фазова стала (рад/м)

    // Переведення згасання з дБ/м у Непери/м (1 Нп ≈ 8.685889638 дБ)
    const double alpha_np_m = line.attenuation_db_m / 8.685889638;

    // 1. Коефіцієнт відбиття на навантаженні: Γ_L = (Z_L - Z0) / (Z_L + Z0)
    const std::complex<double> gamma_l = (z_load - line.z0) / (z_load + line.z0);
    const double mag = std::abs(gamma_l);
    const double phase_deg = std::arg(gamma_l) * 180.0 / std::numbers::pi;

    // 2. КСХ = (1 + |Γ|) / (1 - |Γ|) з захистом від ділення на нуль
    const double vswr = (mag >= 0.99999) ? 999.99 : (1.0 + mag) / (1.0 - mag);

    // 3. Return Loss (дБ) = -20 * log10(|Γ|) з захистом від log(0)
    const double return_loss = (mag < 1e-12) ? 240.0 : -20.0 * std::log10(mag);

    // 4. Енергетичні співвідношення потужностей
    const double p_ref_pct = mag * mag * 100.0;
    const double p_trans_pct = (1.0 - mag * mag) * 100.0;
    const double mismatch_loss = (mag >= 0.99999) ? 99.99 : -10.0 * std::log10(1.0 - mag * mag);

    // 5. Трансформація Γ вздовж лінії: Γ(l) = Γ_L * exp(-2*alpha*l - j*2*beta*l)
    const std::complex<double> gamma_prop{ -2.0 * alpha_np_m * line.length_m,
                                           -2.0 * beta * line.length_m };
    const std::complex<double> gamma_in = gamma_l * std::exp(gamma_prop);

    // 6. Вхідний імпеданс Z_in = Z0 * (1 + Γ_in) / (1 - Γ_in)
    const std::complex<double> z_in = line.z0 * (1.0 + gamma_in) / (1.0 - gamma_in);

    return ReflectionResult{
        .gamma_load = gamma_l,
        .gamma_mag = mag,
        .gamma_phase_deg = phase_deg,
        .vswr = vswr,
        .return_loss_db = return_loss,
        .mismatch_loss_db = mismatch_loss,
        .power_transmitted_pct = p_trans_pct,
        .power_reflected_pct = p_ref_pct,
        .gamma_input = gamma_in,
        .z_input = z_in
    };
}

} // namespace rf

int main() {
    using namespace std::complex_literals;

    // Приклад: навантаження 75 + j25 Ом підключено через 5 см FR4 траси (2.4 ГГц)
    const std::complex<double> z_load = 75.0 + 25.0j;
    const rf::LineParams line{
        .z0 = 50.0,
        .frequency_hz = 2.4e9,       // 2.4 ГГц (Wi-Fi / Bluetooth)
        .length_m = 0.05,            // 5 см лінія
        .velocity_factor = 0.60,     // Склотекстоліт FR4
        .attenuation_db_m = 1.5      // 1.5 дБ/м згасання
    };

    const auto res = rf::calculate_reflection(z_load, line);
    if (!res) {
        std::cerr << "Помилка: " << rf::to_string(res.error()) << '\n';
        return 1;
    }

    std::cout << std::fixed << std::setprecision(4)
              << "=== ДІАГНОСТИКА ВЧ-ТРАКТУ (C++23) ===\n"
              << "Γ навантаження: " << res->gamma_load.real() << " + j(" 
              << res->gamma_load.imag() << ")\n"
              << "Модуль |Γ|:      " << res->gamma_mag << '\n'
              << "Фаза Γ:          " << res->gamma_phase_deg << " deg\n"
              << "КСХ (VSWR):      " << res->vswr << " : 1\n"
              << "Return Loss:     " << res->return_loss_db << " dB\n"
              << "Mismatch Loss:   " << res->mismatch_loss_db << " dB\n"
              << "Передано P:      " << res->power_transmitted_pct << " %\n"
              << "Відбито P:       " << res->power_reflected_pct << " %\n"
              << "Γ на вході:      " << res->gamma_input.real() << " + j(" 
              << res->gamma_input.imag() << ")\n"
              << "Z вхідне:        " << res->z_input.real() << " + j(" 
              << res->z_input.imag() << ") Ohm\n";
    return 0;
}
```
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура комплексного числа для C
typedef struct {
    double real;
    double imag;
} Complex;

static inline Complex c_add(Complex a, Complex b) {
    return (Complex){ a.real + b.real, a.imag + b.imag };
}

static inline Complex c_sub(Complex a, Complex b) {
    return (Complex){ a.real - b.real, a.imag - b.imag };
}

static inline Complex c_mul(Complex a, Complex b) {
    return (Complex){ a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real };
}

static inline Complex c_div(Complex a, Complex b) {
    double denom = b.real * b.real + b.imag * b.imag;
    return (Complex){ (a.real * b.real + a.imag * b.imag) / denom,
                      (a.imag * b.real - a.real * b.imag) / denom };
}

static inline double c_abs(Complex a) {
    return sqrt(a.real * a.real + a.imag * a.imag);
}

static inline double c_arg(Complex a) {
    return atan2(a.imag, a.real);
}

static inline Complex c_exp(Complex a) {
    double r = exp(a.real);
    return (Complex){ r * cos(a.imag), r * sin(a.imag) };
}

typedef struct {
    double z0;
    double frequency_hz;
    double length_m;
    double velocity_factor;
    double attenuation_db_m;
} LineParams;

typedef struct {
    Complex gamma_load;
    double gamma_mag;
    double gamma_phase_deg;
    double vswr;
    double return_loss_db;
    double power_transmitted_pct;
    double power_reflected_pct;
    Complex gamma_input;
    Complex z_input;
} ReflectionResult;

bool calculate_reflection(Complex z_load, const LineParams* line, ReflectionResult* out) {
    if (!line || !out || line->z0 <= 0.0 || line->frequency_hz <= 0.0 || 
        line->velocity_factor <= 0.0 || line->velocity_factor > 1.0 || line->length_m < 0.0) {
        return false;
    }

    const double c0 = 299792458.0;
    double v_phase = c0 * line->velocity_factor;
    double wavelength = v_phase / line->frequency_hz;
    double beta = 2.0 * M_PI / wavelength;
    double alpha_np_m = line->attenuation_db_m / 8.685889638;

    // Γ_L = (Z_L - Z0) / (Z_L + Z0)
    Complex z0_c = { line->z0, 0.0 };
    Complex num = c_sub(z_load, z0_c);
    Complex den = c_add(z_load, z0_c);
    out->gamma_load = c_div(num, den);

    out->gamma_mag = c_abs(out->gamma_load);
    out->gamma_phase_deg = c_arg(out->gamma_load) * 180.0 / M_PI;

    out->vswr = (out->gamma_mag >= 0.99999) ? 999.99 : (1.0 + out->gamma_mag) / (1.0 - out->gamma_mag);
    out->return_loss_db = (out->gamma_mag < 1e-12) ? 240.0 : -20.0 * log10(out->gamma_mag);
    out->power_reflected_pct = out->gamma_mag * out->gamma_mag * 100.0;
    out->power_transmitted_pct = (1.0 - out->gamma_mag * out->gamma_mag) * 100.0;

    // Γ(l) = Γ_L * exp(-2*alpha*l - j*2*beta*l)
    Complex gamma_prop = { -2.0 * alpha_np_m * line->length_m, -2.0 * beta * line->length_m };
    out->gamma_input = c_mul(out->gamma_load, c_exp(gamma_prop));

    // Z_in = Z0 * (1 + Γ_in) / (1 - Γ_in)
    Complex one = { 1.0, 0.0 };
    Complex z_in_num = c_mul(z0_c, c_add(one, out->gamma_input));
    Complex z_in_den = c_sub(one, out->gamma_input);
    out->z_input = c_div(z_in_num, z_in_den);

    return true;
}

int main(void) {
    Complex z_load = { 75.0, 25.0 };
    LineParams line = {
        .z0 = 50.0,
        .frequency_hz = 2.4e9,
        .length_m = 0.05,
        .velocity_factor = 0.60,
        .attenuation_db_m = 1.5
    };

    ReflectionResult res;
    if (!calculate_reflection(z_load, &line, &res)) {
        printf("Помилка вхідних параметрів\n");
        return 1;
    }

    printf("=== C РЕЗУЛЬТАТИ ===\n");
    printf("Γ_L = %.4f + j(%.4f)\n", res.gamma_load.real, res.gamma_load.imag);
    printf("|Γ| = %.4f, Фаза = %.2f deg\n", res.gamma_mag, res.gamma_phase_deg);
    printf("VSWR = %.2f : 1, Return Loss = %.2f dB\n", res.vswr, res.return_loss_db);
    printf("Передано потужності = %.2f %%\n", res.power_transmitted_pct);
    printf("Z_in = %.2f + j(%.2f) Ом\n", res.z_input.real, res.z_input.imag);

    return 0;
}
```
```py
import cmath
import math

def calculate_reflection(z_load: complex, z0: float = 50.0, freq_hz: float = 2.4e9,
                         length_m: float = 0.05, vf: float = 0.60, atten_db_m: float = 1.5):
    """
    Обчислює комплексний коефіцієнт відбиття та лінійні параметри ВЧ-тракту.
    """
    if z0 <= 0 or freq_hz <= 0 or vf <= 0 or vf > 1.0 or length_m < 0:
        raise ValueError("Некоректні вхідні параметри лінії передачі")

    c0 = 299792458.0
    v_phase = c0 * vf
    wavelength = v_phase / freq_hz
    beta = 2.0 * math.pi / wavelength
    alpha_np_m = atten_db_m / 8.685889638

    # 1. Γ на навантаженні
    gamma_l = (z_load - z0) / (z_load + z0)
    mag = abs(gamma_l)
    phase_deg = math.degrees(cmath.phase(gamma_l))

    # 2. КСХ та Return Loss
    vswr = (1.0 + mag) / (1.0 - mag) if mag < 0.99999 else 999.99
    return_loss = -20.0 * math.log10(mag) if mag > 1e-12 else 240.0
    p_trans_pct = (1.0 - mag**2) * 100.0
    p_ref_pct = mag**2 * 100.0
    mismatch_loss = -10.0 * math.log10(1.0 - mag**2) if mag < 0.99999 else 99.99

    # 3. Трансформація вздовж лінії
    gamma_in = gamma_l * cmath.exp(complex(-2.0 * alpha_np_m * length_m, -2.0 * beta * length_m))
    z_in = z0 * (1.0 + gamma_in) / (1.0 - gamma_in)

    return {
        "gamma_load": gamma_l,
        "gamma_mag": mag,
        "gamma_phase_deg": phase_deg,
        "vswr": vswr,
        "return_loss_db": return_loss,
        "mismatch_loss_db": mismatch_loss,
        "power_trans_pct": p_trans_pct,
        "power_ref_pct": p_ref_pct,
        "gamma_in": gamma_in,
        "z_in": z_in
    }

if __name__ == "__main__":
    res = calculate_reflection(complex(75, 25))
    print("=== PYTHON РЕЗУЛЬТАТИ ===")
    print(f"Γ_L = {res['gamma_load'].real:.4f} + {res['gamma_load'].imag:.4f}j")
    print(f"|Γ| = {res['gamma_mag']:.4f}, Фаза = {res['gamma_phase_deg']:.2f}°")
    print(f"VSWR = {res['vswr']:.2f}:1, Return Loss = {res['return_loss_db']:.2f} dB")
    print(f"Передано потужності = {res['power_trans_pct']:.2f}%")
    print(f"Z_in = {res['z_in'].real:.2f} + {res['z_in'].imag:.2f}j Ом")
```
:::

### Набір тестових сценаріїв та верифікація

Для перевірки коректності функціонування модуля розроблено чотири еталонні верифікаційні тестові кейси:

1. **Тест 1: Точне узгодження (`Z_L = 50 Ом`, `Z₀ = 50 Ом`)**
   - Очікуваний результат: `Γ_L = 0.0 + j0.0`, `|Γ| = 0.0`, `VSWR = 1.00`, `Return Loss = 240.0 dB`, `Передана потужність = 100.0%`.

2. **Тест 2: Ідеальне коротке замикання (`Z_L = 0 Ом`, `Z₀ = 50 Ом`)**
   - Очікуваний результат: `Γ_L = −1.0 + j0.0`, `|Γ| = 1.0`, `Фаза = 180.0°`, `VSWR = 999.99`, `Return Loss = 0.0 dB`, `Передана потужність = 0.0%`.

3. **Тест 3: Ідеальний розрив (`Z_L = 1e8 Ом`, `Z₀ = 50 Ом`)**
   - Очікуваний результат: `Γ_L ≈ +1.0 + j0.0`, `|Γ| ≈ 1.0`, `Фаза = 0.0°`, `VSWR = 999.99`, `Return Loss = 0.0 dB`, `Передана потужність = 0.0%`.

4. **Тест 4: Чвертьхвильовий трансформатор (`Z_L = 100 Ом`, `Z₀ = 50 Ом`, `l = λ / 4`)**
   - Очікуваний результат: на навантаженні `Γ_L = 0.3333` (`Z_L = 100 Ом`), після трансформації на `λ/4` фаза обертається на 180°, `Γ_in = −0.3333`, а вхідний імпеданс стає `Z_in = Z₀² / Z_L = 2500 / 100 = 25 Ом`.

### Потенційні інженерні пастки розробки

Під час практичного використання алгоритму обчислення коефіцієнта відбиття слід пам'ятати про наступні кричущі помилки:

1. **Ігнорування коефіцієнта укорочення (`velocity factor`).** На частотах у декілька гігагерц помилка у коефіцієнті укорочення всього в `0.05` призводить до фазової зсунутості розрахованого `Γ_in` на десятки градусів. Це повністю руйнує точність синтезу узгоджувальних шлейфів.
2. **Нехтування втратами в лінії.** Якщо кабель має помітне згасання (наприклад, 3 дБ), то виміряний на початку кабелю КСХ буде значно кращим за реальний КСХ антени. Автоматизований софт вимірювальних приладів повинен проводити деембедінг (*de-embedding*) — зворотний перерахунок `Γ_L = Γ_in · exp(+2 γ l)`, щоб показати інженеру істинні параметри антени, а не оману, створену згасанням кабелю.
3. **Обчислення розриву лінії у цифрових системах.** При знятті навантаження `Z_L → ∞` програма не повинна передавати у формулу число `Infinity` чи надзвичайно велике значення без захисного обмеження, оскільки ділення двох великих чисел у плаваючій точці може дати невизначеність `NaN`.
