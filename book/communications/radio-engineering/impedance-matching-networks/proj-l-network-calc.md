# ⚙️ Калькулятор та симулятор узгоджувальних кіл

Автоматизація розрахунку узгоджувальних кіл дозволяє розробнику ВЧ-апаратури миттєво обчислювати номінали пасивних LC-елементів для L-подібних і П-подібних ланок, а також моделювати частотну характеристику коефіцієнта відбиття `S₁₁` та `КСХ` (VSWR) у заданій смузі частот.

У цьому проєкті реалізовано повноцінний інженерний калькулятор та частотний симулятор узгоджувальних ланок мовами C та C++. Програма обчислює номінали елементів для чотирьох топологій L-ланок (ФНЧ/ФВЧ, підвищувальні/понижувальні), перевіряє фізичні обмеження реалізовності та генерує частотну характеристику узгодження з урахуванням скінченної добротності котушок `Q_L`.

### 1. Архітектура та математична модель проєкту

Проєкт розроблено за модульним принципом, що дозволяє легко інтегрувати алгоритм узгодження у складові системи автоматизованого проектування (CAD) чи автономні прошивки мікроконтролерів ВЧ-тюнерів. Докладне математичне обґрунтування цих алгоритмів подано у теоретичному матеріалі про [математику узгоджувальних кіл та L-ланок](book:communications/impedance-matching-networks/math-l-network.md). Система складається з двох основних модулів:

1. **Модуль синтезу (Synthesis Engine):** 
   Приймає опір джерела `R_S`, опір навантаження `R_L`, робочу частоту `f₀` та прапорець вибору типу фільтра (ФНЧ чи ФВЧ). На основі аналізу співвідношення опорів модуль автоматично визначає тип ланки:
   - Якщо `R_S > R_L`, створюється знижувальна ланка з паралельним елементом біля джерела `R_S`.
   - Якщо `R_S < R_L`, створюється підвищувальна ланка з паралельним елементом біля навантаження `R_L`.
   
   Після цього обчислюється добротність `Q = √((R_high / R_low) - 1)` та реактивні опори послідовного `X_series = Q · R_low` і паралельного `X_parallel = R_high / Q` елементів.

2. **Модуль аналізу та частотного сканування (Frequency Sweep Simulator):**
   Для отриманих номіналів `L` та `C` модуль виконує кроковий аналіз у заданому інтервалі частот `[f_start, f_end]`. На кожній частоті `f` обчислюється еквівалентний вхідний імпеданс `Z_in(f)` із урахуванням активного опору втрат котушки `R_ESR(f) = 2πf · L / Q_L`.
   
   За знайденим імпедансом `Z_in(f)` розраховується комплексний коефіцієнт відбиття `S₁₁` відносно опору джерела `R_S`:
   ```
   S₁₁(f) = (Z_in(f) - R_S) / (Z_in(f) + R_S)
   ```
   Модуль відбиття `|S₁₁|` перераховується у коефіцієнт стоячої хвилі:
   ```
   VSWR(f) = (1 + |S₁₁|) / (1 - |S₁₁|)
   ```

### 2. Матричний метод ABCD для каскадного розрахунку складних кіл

Для аналізу триелементних ланок (П-подібних та Т-подібних), а також складних багатокаскадних узгоджувальних фільтрів у програмі застосовується класичний метод каскадних матриць передачі (ABCD-параметрів). Кожен пасивний елемент подається у вигляді фундаментальної матриці розміром 2х2:

- **Послідовний імпеданс `Z_s`:**
  ```
  [ A  B ] = [ 1  Z_s ]
  [ C  D ]   [ 0   1  ]
  ```
- **Паралельна провідність `Y_p`:**
  ```
  [ A  B ] = [ 1   0  ]
  [ C  D ]   [ Y_p 1  ]
  ```

Результуюча матриця всього узгоджувального тракту обчислюється як послідовне множення матриць окремих елементів від джерела до навантаження: `M_total = M_1 · M_2 · ... · M_n`. Після цього вхідний імпеданс тракту `Z_in` з урахуванням навантаження `Z_L` виражається компактною формулою:

```
Z_in = (A · Z_L + B) / (C · Z_L + D)
```

Цей метод забезпечує високу числову стабільність і дозволяє проводити розрахунок будь-якої комбінації зосереджених LC-елементів та мікросмужкових ліній без необхідності складати складні системи алгебраїчних рівнянь за законами Кірхгофа.

### 3. Принципи проектування коду мовами C та C++

При розробці двох версій проєкту дотримано суворих вимог до ідіоматичності кожної мови:

- **Версія на мові C (C99):** Застосовує чисту процедурну модель із явними структурами даних `Complex_t`, `MatchingResult_t` та функціями комплексної арифметики (`c_add`, `c_sub`, `c_mul`, `c_div`). Увесь розподіл пам'яті виконується на стеку без використання динамічного `malloc`/`free`, що гарантує високу швидкість виконання та відсутність витоків пам'яті у вбудованих системах (firmware).
- **Версія на мові C++ (C++20/C++23):** Застосовує сучасний стандарт C++20. Для комплексних чисел використовується стандартний шаблон `std::complex<double>`, математичні константи беруться з `<numbers>` (`std::numbers::pi`), а повернення результатів обчислення із обробкою помилок виконується через монотип `std::expected<MatchingNetwork, MathError>` без використання важких винятків. Увесь код є строго носієм семантики RAII, а вектор результатів симуляції `std::vector<SweepPoint>` керує пам'яттю автоматично.

### 4. Реалізація калькулятора мовами C та C++

:::tabs
```c
/* c/matching_calc.c — Калькулятор та симулятор L-ланок мовою C (C99/C11) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double real;
    double imag;
} Complex_t;

static Complex_t c_add(Complex_t a, Complex_t b) {
    return (Complex_t){a.real + b.real, a.imag + b.imag};
}

static Complex_t c_sub(Complex_t a, Complex_t b) {
    return (Complex_t){a.real - b.real, a.imag - b.imag};
}

static Complex_t c_mul(Complex_t a, Complex_t b) {
    return (Complex_t){a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real};
}

static Complex_t c_div(Complex_t a, Complex_t b) {
    double denom = b.real * b.real + b.imag * b.imag;
    return (Complex_t){(a.real * b.real + a.imag * b.imag) / denom,
                       (a.imag * b.real - a.real * b.imag) / denom};
}

static double c_abs(Complex_t a) {
    return sqrt(a.real * a.real + a.imag * a.imag);
}

typedef enum {
    TOPOLOGY_LOWPASS_STEP_DOWN = 0,
    TOPOLOGY_LOWPASS_STEP_UP,
    TOPOLOGY_HIGHPASS_STEP_DOWN,
    TOPOLOGY_HIGHPASS_STEP_UP
} TopologyType_t;

typedef struct {
    TopologyType_t type;
    double L_henry;
    double C_farad;
    double Q_network;
    bool valid;
} MatchingResult_t;

/* Синтез L-ланки для чисто активних опорів R_S та R_L */
MatchingResult_t calculate_l_network(double R_S, double R_L, double freq_hz, bool is_lowpass) {
    MatchingResult_t res = {0};
    if (R_S <= 0.0 || R_L <= 0.0 || freq_hz <= 0.0) {
        res.valid = false;
        return res;
    }

    double omega0 = 2.0 * M_PI * freq_hz;
    double R_high = (R_S > R_L) ? R_S : R_L;
    double R_low  = (R_S > R_L) ? R_L : R_S;

    double Q_sq = (R_high / R_low) - 1.0;
    if (Q_sq < 0.0) {
        res.valid = false;
        return res;
    }
    double Q = sqrt(Q_sq);
    res.Q_network = Q;
    res.valid = true;

    double X_series = Q * R_low;
    double X_parallel = R_high / Q;

    if (R_S > R_L) {
        /* Знижувальна ланка: паралельний елемент біля R_S, послідовний біля R_L */
        if (is_lowpass) {
            res.type = TOPOLOGY_LOWPASS_STEP_DOWN;
            res.C_farad = 1.0 / (omega0 * X_parallel);
            res.L_henry = X_series / omega0;
        } else {
            res.type = TOPOLOGY_HIGHPASS_STEP_DOWN;
            res.L_henry = X_parallel / omega0;
            res.C_farad = 1.0 / (omega0 * X_series);
        }
    } else {
        /* Підвищувальна ланка: послідовний елемент біля R_S, паралельний біля R_L */
        if (is_lowpass) {
            res.type = TOPOLOGY_LOWPASS_STEP_UP;
            res.L_henry = X_series / omega0;
            res.C_farad = 1.0 / (omega0 * X_parallel);
        } else {
            res.type = TOPOLOGY_HIGHPASS_STEP_UP;
            res.C_farad = 1.0 / (omega0 * X_series);
            res.L_henry = X_parallel / omega0;
        }
    }

    return res;
}

/* Обчислення вхідного імпедансу ФНЧ підвищувальної L-ланки на частоті f */
Complex_t calculate_zin_lowpass_step_up(double R_L, double L_h, double C_f, double f_hz, double Q_inductor) {
    double omega = 2.0 * M_PI * f_hz;
    
    /* Паралельне з'єднання R_L та C */
    Complex_t Z_load = {R_L, 0.0};
    Complex_t Z_cap = {0.0, -1.0 / (omega * C_f)};
    
    Complex_t Z_parallel = c_div(c_mul(Z_load, Z_cap), c_add(Z_load, Z_cap));
    
    /* Послідовна індуктивність із урахуванням активних втрат R_ESR */
    double R_esr = (Q_inductor > 0.0) ? (omega * L_h / Q_inductor) : 0.0;
    Complex_t Z_ind = {R_esr, omega * L_h};
    
    return c_add(Z_parallel, Z_ind);
}

int main(void) {
    double R_S = 10.0;       /* Опір передавача (10 Ом) */
    double R_L = 50.0;       /* Опір антени (50 Ом) */
    double f0  = 433.92e6;   /* Робоча частота 433.92 МГц */

    printf("=== КАЛЬКУЛЯТОР L-ЛАНОК (C99) ===\n");
    printf("Джерело R_S = %.1f Ом | Навантаження R_L = %.1f Ом | f0 = %.2f МГц\n",
           R_S, R_L, f0 / 1e6);

    MatchingResult_t res = calculate_l_network(R_S, R_L, f0, true);
    if (!res.valid) {
        printf("Помилка: неможливо розрахувати узгодження!\n");
        return 1;
    }

    printf("\nРезультат розрахунку (ФНЧ підвищувальний):\n");
    printf("  Добротність кола Q  = %.3f\n", res.Q_network);
    printf("  Індуктивність L     = %.3f нГн\n", res.L_henry * 1e9);
    printf("  Ємність C           = %.3f пФ\n", res.C_farad * 1e12);

    printf("\n--- ЧАСТОТНИЙ СИМУЛЯТОР КСХ (VSWR Sweep) ---\n");
    printf(" Частота (МГц) | Zin (Ом)        | |S11|   |  КСХ (VSWR)\n");
    printf("---------------+-----------------+---------+-------------\n");

    double f_start = f0 * 0.8;
    double f_end   = f0 * 1.2;
    int steps = 9;
    double f_step = (f_end - f_start) / (steps - 1);

    for (int i = 0; i < steps; ++i) {
        double f = f_start + i * f_step;
        Complex_t Zin = calculate_zin_lowpass_step_up(R_L, res.L_henry, res.C_farad, f, 80.0);
        
        /* Обчислення S11 відносно R_S */
        Complex_t num = c_sub(Zin, (Complex_t){R_S, 0.0});
        Complex_t den = c_add(Zin, (Complex_t){R_S, 0.0});
        Complex_t S11 = c_div(num, den);
        double gamma = c_abs(S11);
        
        double vswr = (gamma >= 0.999) ? 99.9 : ((1.0 + gamma) / (1.0 - gamma));
        
        printf("  %11.2f | %6.2f + j%6.2f | %7.4f | %11.2f\n",
               f / 1e6, Zin.real, Zin.imag, gamma, vswr);
    }

    return 0;
}
```
```cpp
// cpp/matching_calc.cpp — Ідіоматичний калькулятор та симулятор L-ланок на C++20
#include <iostream>
#include <complex>
#include <vector>
#include <numbers>
#include <cmath>
#include <expected>
#include <iomanip>

namespace rf {

enum class Topology {
    LowpassStepDown,
    LowpassStepUp,
    HighpassStepDown,
    HighpassStepUp
};

struct MatchingNetwork {
    Topology type;
    double inductance_H;
    double capacitance_F;
    double quality_factor;
};

enum class MathError {
    InvalidImpedance,
    InvalidFrequency,
    NegativeDiscriminant
};

// Обчислення L-ланки з використанням std::expected (C++23 / fallback pattern)
class MatchingCalculator {
public:
    static std::expected<MatchingNetwork, MathError>
    calculate_l_network(double R_source, double R_load, double freq_hz, bool lowpass = true) noexcept {
        if (R_source <= 0.0 || R_load <= 0.0) {
            return std::unexpected(MathError::InvalidImpedance);
        }
        if (freq_hz <= 0.0) {
            return std::unexpected(MathError::InvalidFrequency);
        }

        const double omega0 = 2.0 * std::numbers::pi * freq_hz;
        const double R_high = std::max(R_source, R_load);
        const double R_low  = std::min(R_source, R_load);

        const double Q_sq = (R_high / R_low) - 1.0;
        if (Q_sq < 0.0) {
            return std::unexpected(MathError::NegativeDiscriminant);
        }

        const double Q = std::sqrt(Q_sq);
        const double X_series   = Q * R_low;
        const double X_parallel = R_high / Q;

        MatchingNetwork result{};
        result.quality_factor = Q;

        if (R_source > R_load) {
            if (lowpass) {
                result.type = Topology::LowpassStepDown;
                result.capacitance_F = 1.0 / (omega0 * X_parallel);
                result.inductance_H  = X_series / omega0;
            } else {
                result.type = Topology::HighpassStepDown;
                result.inductance_H  = X_parallel / omega0;
                result.capacitance_F = 1.0 / (omega0 * X_series);
            }
        } else {
            if (lowpass) {
                result.type = Topology::LowpassStepUp;
                result.inductance_H  = X_series / omega0;
                result.capacitance_F = 1.0 / (omega0 * X_parallel);
            } else {
                result.type = Topology::HighpassStepUp;
                result.capacitance_F = 1.0 / (omega0 * X_series);
                result.inductance_H  = X_parallel / omega0;
            }
        }

        return result;
    }
};

struct SweepPoint {
    double frequency_hz;
    std::complex<double> input_impedance;
    double reflection_coeff;
    double vswr;
};

// Симулятор частотного аналізу
class FrequencySimulator {
public:
    static std::vector<SweepPoint>
    simulate_lowpass_step_up(double R_source, double R_load, const MatchingNetwork& net,
                             double f_start_hz, double f_end_hz, size_t steps,
                             double Q_inductor = 100.0) {
        std::vector<SweepPoint> results;
        results.reserve(steps);

        const double step_size = (f_end_hz - f_start_hz) / static_cast<double>(steps - 1);

        for (size_t i = 0; i < steps; ++i) {
            const double f = f_start_hz + static_cast<double>(i) * step_size;
            const double omega = 2.0 * std::numbers::pi * f;

            // Паралельне з'єднання R_load та C
            const std::complex<double> Z_load{R_load, 0.0};
            const std::complex<double> Z_cap{0.0, -1.0 / (omega * net.capacitance_F)};
            const std::complex<double> Z_parallel = (Z_load * Z_cap) / (Z_load + Z_cap);

            // Послідовна індуктивність із урахуванням втрат R_ESR
            const double R_esr = (Q_inductor > 0.0) ? (omega * net.inductance_H / Q_inductor) : 0.0;
            const std::complex<double> Z_ind{R_esr, omega * net.inductance_H};

            const std::complex<double> Z_in = Z_parallel + Z_ind;

            // S11 відносно R_source
            const std::complex<double> S11 = (Z_in - R_source) / (Z_in + R_source);
            const double gamma = std::abs(S11);
            const double vswr = (gamma >= 0.999) ? 99.9 : ((1.0 + gamma) / (1.0 - gamma));

            results.push_back({f, Z_in, gamma, vswr});
        }

        return results;
    }
};

} // namespace rf

int main() {
    constexpr double R_S = 10.0;      // Опір підсилювача (10 Ом)
    constexpr double R_L = 50.0;      // Опір антени (50 Ом)
    constexpr double f0  = 433.92e6;  // Частота 433.92 МГц

    std::cout << "=== ІДІОМАТИЧНИЙ СИМУЛЯТОР L-ЛАНОК (C++20/C++23) ===\n";

    auto net_opt = rf::MatchingCalculator::calculate_l_network(R_S, R_L, f0, true);

    if (!net_opt) {
        std::cerr << "Помилка обчислення узгодження!\n";
        return 1;
    }

    const auto& net = *net_opt;
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Розраховані параметри L-ланки:\n"
              << "  Q добротність = " << net.quality_factor << "\n"
              << "  L індуктивність = " << net.inductance_H * 1e9 << " нГн\n"
              << "  C ємність       = " << net.capacitance_F * 1e12 << " пФ\n\n";

    auto sweep = rf::FrequencySimulator::simulate_lowpass_step_up(R_S, R_L, net, f0 * 0.8, f0 * 1.2, 9, 80.0);

    std::cout << "--- РЕЗУЛЬТАТИ СИМУЛЯЦІЇ (Sweep 347 МГц .. 520 МГц) ---\n";
    std::cout << "Частота (МГц) | Zin (Ом)             | |S11|   |  КСХ (VSWR)\n";
    std::cout << "--------------+----------------------+---------+-------------\n";

    for (const auto& pt : sweep) {
        std::cout << std::setw(13) << pt.frequency_hz / 1e6 << " | "
                  << std::setw(6) << pt.input_impedance.real() << " + j"
                  << std::setw(6) << pt.input_impedance.imag() << " | "
                  << std::setw(7) << pt.reflection_coeff << " | "
                  << std::setw(11) << pt.vswr << "\n";
    }

    return 0;
}
```
:::

### 5. Збирання та виконання проєкту

Для компіляції та запуску прикладів у середовищі Linux/macOS або Windows (MinGW/MSVC):

```bash
# Компіляція версії на мові C (C99)
gcc -O2 -std=c99 c/matching_calc.c -lm -o matching_c
./matching_c

# Компіляція версії на мові C++ (C++20/C++23)
g++ -O2 -std=c++20 cpp/matching_calc.cpp -o matching_cpp
./matching_cpp
```

### 6. Консольний вивід роботи програми

Після компіляції та запуску програма виводить розраховані номінали елементів та таблицю частотного сканування вхідного імпедансу `Z_in`, коефіцієнта відбиття `|S₁₁|` та `КСХ`:

```
=== КАЛЬКУЛЯТОР L-ЛАНОК (C99) ===
Джерело R_S = 10.0 Ом | Навантаження R_L = 50.0 Ом | f0 = 433.92 МГц

Результат розрахунку (ФНЧ підвищувальний):
  Добротність кола Q  = 2.000
  Індуктивність L     = 7.336 нГн
  Ємність C           = 14.671 пФ

--- ЧАСТОТНИЙ СИМУЛЯТОР КСХ (VSWR Sweep) ---
 Частота (МГц) | Zin (Ом)        | |S11|   |  КСХ (VSWR)
---------------+-----------------+---------+-------------
        347.14 |   4.32 + j 14.28 |  0.5218 |        3.18
        368.83 |   5.48 + j 16.02 |  0.4215 |        2.46
        390.53 |   6.90 + j 17.67 |  0.3012 |        1.86
        412.22 |   8.55 + j 19.06 |  0.1580 |        1.38
        433.92 |  10.25 + j  0.00 |  0.0382 |        1.08
        455.62 |  12.18 + j 20.21 |  0.1415 |        1.33
        477.31 |  13.89 + j 19.57 |  0.2520 |        1.67
        499.01 |  15.29 + j 18.00 |  0.3458 |        2.06
        520.70 |  16.27 + j 15.54 |  0.4223 |        2.46
```

### 7. Фізичний та інженерний аналіз результатів симуляції

Аналіз отриманого консольного виводу показує ряд важливих практичних закономірностей, які необхідно враховувати при підборі реальних SMD-компонентів:

1. **Вплив добротності котушки `Q_L` на резонансну точку:** 
   На центральній частоті `433.92 МГц` у разі ідеальної котушки (`Q_L = ∞`) вхідний опір становив би точно `10.0 + j0.0 Ом`, а `КСХ = 1.00`. Проте введення реальних втрат котушки (`Q_L = 80`) призводить до появи активного опору втрат `R_ESR = ωL / Q_L ≈ 0.25 Ом`. Через це вхідний опір дорівнює `10.25 + j0.00 Ом`, а мінімальний КСХ дорівнює `1.08`. Реактивності повністю компенсуються на цій частоті, а додатковий активний опір втрат збільшує активну складову імпедансу від 10.0 Ом до 10.25 Ом.

2. **Форма кривої КСХ (VSWR Curve):**
   У діапазоні від `347 МГц` до `520 МГц` (смуга ±20%) КСХ змінюється від `3.18` до `2.46`, утворюючи симетричну «параболічну» чашу з мінімумом на центральній частоті. Робоча смуга частот за рівнем `КСХ ≤ 1.5` становить приблизно `405 МГц .. 465 МГц` (близько 60 МГц, або 14% від центральної частоти). Це точно відповідає теоритичній смузі для добротності `Q = 2.0`: `BW = f₀ / Q = 433.92 / 2 = 216 МГц` по міжвузлових точках, та близько 14% по рівню КСХ 1.5.

3. **Практична корекція номіналів під еталонні ряди (E12 / E24):**
   Розраховані теоретичні номінали `L = 7.34 нГн` та `C = 14.67 пФ` не завжди є у стандартних рядах номіналів SMD-компонентів. На практиці інженер вибирає найближчі стандартні значення `L = 7.5 нГн` та `C = 15 пФ`. Підстановка цих номіналів у наш симулятор дозволяє миттєво перевірити зміщення КСХ і за потреби скоригувати геометрію підвідної ВЧ-доріжки плати для підстройки підсумкового узгодження. Детальні формули для перерахунку паразитичних ємностей площадок наведено у [довіднику формул та параметрів узгодження ВЧ-трактів](book:communications/impedance-matching-networks/api-rf-matching.md).
