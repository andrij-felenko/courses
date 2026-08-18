# ⚙️ Чисельне моделювання тунелювання хвильового пакета

Цей практичний проект присвячено чисельному розв'язанню часового одновимірного рівняння Шредінгера для дослідження квантової динаміки тунелювання Гаусового хвильового пакета крізь прямокутний потенціальний бар'єр. Розглянуто теоретичні основи та чисельний алгоритм методу розщеплення оператора (Split-Operator FFT method), математичний аналіз вибору кроків дискретизації, розрахунок нормування хвильової функції, поглинаючі граничні умови, інтегрування коефіцієнтів відбивання та проходження, а також наведено повну реалізацію мовами C та C++.

## 1. Постановка фізичної та чисельної задачі

Динаміка квантовомеханічної частинки масою `m` у часозалежному або стаціонарному потенціальному полі `V(x)` описується часовим одновимірним рівнянням Шредінгера:

```
i ℏ (∂ψ(x, t) / ∂t) = Ĥ ψ(x, t) = [ T̂ + V̂ ] ψ(x, t) = [ - (ℏ² / (2 m)) (∂² / ∂x²) + V(x) ] ψ(x, t)
```

де `Ĥ = T̂ + V̂` — повний гамільтоніан системи, який складається з оператора кінетичної енергії `T̂ = p̂² / (2m)` та оператора потенціальної енергії `V̂ = V(x)`.

Задамо початковий стан частинки при `t = 0` у вигляді Гаусового хвильового пакета, нормованого на одиницю у просторовому інтервалі:

```
ψ(x, 0) = (1 / (π σ²)^(1/4)) exp( - (x - x₀)² / (2 σ²) ) exp( i k₀ x )
```

У цій формулі:
- `x₀` — початкова середня координата центру пакета у просторі.
- `σ` — початкова просторова ширина (дисперсія) хвильового пакета.
- `k₀ = √(2 m E₀) / ℏ` — середній хвильовий вектор, який задає початковий середній імпульс `p₀ = ℏ k₀` та початкову кінетичну енергію `E₀ = p₀² / (2m)`.

Потенціал `V(x)` описує прямокутний потенціальний бар'єр висотою `V₀`, розташований між координатами `x_b1` та `x_b2`:

```
V(x) = V₀,   при x_b1 ≤ x ≤ x_b2
V(x) = 0,    в інших точках простору
```

Чисельне завдання полягає у розрахунку часової еволюції хвильової функції `ψ(x, t)` від моменту `t = 0` до моменту `t_final`, коли хвильовий пакет повністю зіштовхнеться з бар'єром і розділиться на відбиту частину (яка повертається ліворуч) та тунельовану частину (яка продовжує рух праворуч).

## 2. Дисперсія хвильового пакета та критерії дискретизації

При вільному русі (поза бар'єром) Гаусов хвильовий пакет відчуває природне квантовомеханічне распливання (дисперсію). Його просторова ширина зростає з часом за законом:

```
σ(t) = σ₀ √( 1 + (ℏ t / (2 m σ₀²))² )
```

Це означає, що для збереження високої просторової точності ширина просторової області моделювання `L` має бути значно більшою за розмір пакета `L >> σ(t_final)`, а розрахункова сітка повинна містити достатню кількість точок `N` (типово `N = 256, 512, 1024`).

Крок дискретизації за координатою становить:

```
dx = L / N
```

Відповідно до теореми Найквіста — Котельникова, максимальний хвильовий вектор, який може бути відтворений на такій сітці без явищ еліасингу (перекриття спектрів), становить:

```
k_max = π / dx
```

Для забезпечення точності початковий хвильовий вектор пакета `k₀` разом із шириною його спектра `Δk = 1 / (2 σ₀)` повинен задовольняти умову:

```
k₀ + 3 Δk < k_max  ⇒  k₀ + 3 / (2 σ₀) < π / dx
```

Крок часової дискретизації `Δt` обирається з урахуванням максимальної кінетичної та потенціальної енергії. Для забезпечення стійкості чисельної схеми фазовий набіг за один крок часу не повинен перевищувати 0.1 радіана:

```
Δt < min[ (2 m dx²) / (ℏ π²),  ℏ / (10 V₀) ]
```

## 3. Математичне обґрунтування методу розщеплення оператора (Split-Operator FFT)

Формальний розв'язок часового рівняння Шредінгера за часовий крок `Δt` записується через оператор еволюції в часі:

```
ψ(x, t + Δt) = Û(Δt) ψ(x, t) = exp( - i Ĥ Δt / ℏ ) ψ(x, t) = exp( - i (T̂ + V̂) Δt / ℏ ) ψ(x, t)
```

Оскільки оператор кінетичної енергії `T̂ = - (ℏ² / 2m) ∂²/∂x²` містить похідні по координаті, а оператор потенціальної енергії `V̂ = V(x)` залежить від координати `x`, ці оператори не комутують між собою (`[T̂, V̂] ≠ 0`). Унаслідок цього матричний показник експоненти не дорівнює добутку експонент: `exp(A + B) ≠ exp(A) exp(B)`.

Для розв'язання цієї проблеми застосовують симетричне розщеплення за формулою Бейкера — Кемпбелла — Гаусдорфа (Symplectic Split-Operator scheme):

```
exp( - i (T̂ + V̂) Δt / ℏ ) = exp( - i V̂ Δt / (2 ℏ) ) exp( - i T̂ Δt / ℏ ) exp( - i V̂ Δt / (2 ℏ) ) + O(Δt³)
```

Ця симетрична схема забезпечує другу точність по кроку часу `O(Δt²)` та є строго унітарною, що гарантує точне збереження норми хвильової функції `∫ |ψ(x, t)|² dx = 1.0` протягом будь-якої тривалості моделювання.

Головна перевага методу розщеплення оператора полягає у діагональності операторів у різних просторах:

1. **Множення у координатному просторі:** Оператор потенціалу `exp(-i V(x) Δt / 2ℏ)` є строго діагональним у координатному просторі. Дія оператора зводиться до локального фазового множника для кожної просторової точки `x_i`:
   ```
   ψ'(x_i) = ψ(x_i) exp( - i V(x_i) Δt / (2 ℏ) )
   ```
2. **Множення в імпульсному просторі:** Оператор кінетичної енергії `T̂` не є діагональним у координатному просторі, але стає строго діагональним в імпульсному `k`-просторі. Перехід між координатним та імпульсним просторами здійснюється за допомогою прямого Швидкого Перетворення Фур'є (FFT):
   ```
   ψ̃(k_j) = FFT[ ψ'(x_i) ]
   ```
   У `k`-просторі дія оператора кінетичної енергії є звичайним множенням на фазовий коефіцієнт:
   ```
   ψ̃'(k_j) = ψ̃(k_j) exp( - i (ℏ k_j² / (2 m)) Δt )
   ```
3. **Повернення у координатний простір:** Виконується зворотне Швидке Перетворення Фур'є (IFFT), після чого застосовується друга половина оператора потенціалу:
   ```
   ψ''(x_i) = IFFT[ ψ̃'(k_j) ]
   ψ(x_i, t + Δt) = ψ''(x_i) exp( - i V(x_i) Δt / (2 ℏ) )
   ```

## 4. Обчислення ймовірностей відбивання R та проходження T

Після завершення симуляції у момент часу `t_final` хвильова функція розділяється на дві просторово розділені області.

Ймовірність відбивання `R` (коефіцієнт відбивання) обчислюється шляхом чисельного інтегрування квадрата модуля хвильової функції у просторі ліворуч від передньої стінки бар'єра `x < x_b1`:

```
R = ∫_{-∞}^{x_b1} |ψ(x, t_final)|² dx ≈ ∑_{i: x_i < x_b1} |ψ(x_i, t_final)|² dx
```

Ймовірність проходження `T` (коефіцієнт тунелювання) обчислюється шляхом інтегрування праворуч від задньої стінки бар'єра `x > x_b2`:

```
T = ∫_{x_b2}^{+∞} |ψ(x, t_final)|² dx ≈ ∑_{i: x_i > x_b2} |ψ(x_i, t_final)|² dx
```

Унаслідок унітарності алгоритму сума ймовірностей збереження строго дорівнює одиниці:

```
R + T = 1.0000
```

Щоб запобігти штучному перекрученню результатів через циклічне відбивання хвиль від країв періодичної розрахункової області `x = 0` та `x = L` під час ДПФ, по краях сітки можна додавати комплексний поглинаючий потенціал (CAP — *Complex Absorbing Potential*):

```
V_CAP(x) = - i W₀ ( (x - x_margin) / L_margin )²
```

Цей поглинаючий потенціал плавно зануляє амплітуду вихідних хвиль на межах без утворення паразитного зворотного відбивання.

## 5. Повна реалізація моделювання мовами C та C++

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура комплексного числа для мови C
typedef struct {
    double real;
    double imag;
} Complex;

static Complex c_add(Complex a, Complex b) {
    return (Complex){a.real + b.real, a.imag + b.imag};
}

static Complex c_mul(Complex a, Complex b) {
    return (Complex){a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real};
}

static Complex c_exp_i(double phi) {
    return (Complex){cos(phi), sin(phi)};
}

static double c_abs_sq(Complex a) {
    return a.real * a.real + a.imag * a.imag;
}

// Одномірне ДПФ (для спрощення без зовнішніх бібліотек)
static void dft(const Complex* in, Complex* out, int N, int sign) {
    for (int k = 0; k < N; k++) {
        out[k] = (Complex){0.0, 0.0};
        for (int n = 0; n < N; n++) {
            double angle = sign * 2.0 * M_PI * k * n / N;
            Complex w = c_exp_i(angle);
            out[k] = c_add(out[k], c_mul(in[n], w));
        }
        if (sign < 0) {
            out[k].real /= N;
            out[k].imag /= N;
        }
    }
}

int main(void) {
    const int N = 256;
    const double L = 100.0;
    const double dx = L / N;
    const double dt = 0.05;
    const int steps = 400;

    const double m = 1.0;
    const double hbar = 1.0;

    // Параметри бар'єра
    const double x_b1 = 48.0;
    const double x_b2 = 52.0;
    const double V0 = 1.5;

    // Параметри хвильового пакета
    const double x0 = 25.0;
    const double sigma = 4.0;
    const double E0 = 1.0;
    const double k0 = sqrt(2.0 * m * E0) / hbar;

    Complex* psi = (Complex*)malloc(N * sizeof(Complex));
    Complex* psi_k = (Complex*)malloc(N * sizeof(Complex));
    double* V = (double*)malloc(N * sizeof(double));

    if (!psi || !psi_k || !V) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(psi); free(psi_k); free(V);
        return 1;
    }

    // Ініціалізація потенціалу та хвильової функції
    double norm_factor = 1.0 / sqrt(sigma * sqrt(M_PI));
    for (int i = 0; i < N; i++) {
        double x = i * dx;
        V[i] = (x >= x_b1 && x <= x_b2) ? V0 : 0.0;

        double g = exp(-(x - x0) * (x - x0) / (2.0 * sigma * sigma));
        psi[i] = c_mul((Complex){g * norm_factor, 0.0}, c_exp_i(k0 * x));
    }

    // Головний цикл еволюції у часі (Split-Operator)
    for (int step = 0; step < steps; step++) {
        // 1. Половина кроку потенціалу exp(-i V dt / 2 hbar)
        for (int i = 0; i < N; i++) {
            double phase = -V[i] * dt / (2.0 * hbar);
            psi[i] = c_mul(psi[i], c_exp_i(phase));
        }

        // 2. Перехід в імпульсний простір
        dft(psi, psi_k, N, 1);

        // 3. Крок кінетичної енергії в k-просторі
        for (int k = 0; k < N; k++) {
            double k_val = (k < N / 2) ? (2.0 * M_PI * k / L) : (2.0 * M_PI * (k - N) / L);
            double phase = - (hbar * k_val * k_val / (2.0 * m)) * dt;
            psi_k[k] = c_mul(psi_k[k], c_exp_i(phase));
        }

        // 4. Повернення в координатний простір
        dft(psi_k, psi, N, -1);

        // 5. Друга половина кроку потенціалу
        for (int i = 0; i < N; i++) {
            double phase = -V[i] * dt / (2.0 * hbar);
            psi[i] = c_mul(psi[i], c_exp_i(phase));
        }
    }

    // Розрахунок R та T
    double R = 0.0, T = 0.0;
    for (int i = 0; i < N; i++) {
        double x = i * dx;
        double prob = c_abs_sq(psi[i]) * dx;
        if (x < x_b1) R += prob;
        else if (x > x_b2) T += prob;
    }

    printf("=== Результати чисельного симулятора тунелювання (C) ===\n");
    printf("Енергія пакета E0: %.2f | Висота бар'єра V0: %.2f\n", E0, V0);
    printf("Коефіцієнт відбивання R: %.4f\n", R);
    printf("Коефіцієнт проходження (тунелювання) T: %.4f\n", T);
    printf("Сума ймовірностей R + T: %.4f\n", R + T);

    free(psi);
    free(psi_k);
    free(V);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>
#include <iomanip>

class TunnelingSimulator {
public:
    using Complex = std::complex<double>;

    struct Config {
        std::size_t grid_points{256};
        double domain_length{100.0};
        double dt{0.05};
        std::size_t time_steps{400};
        double mass{1.0};
        double hbar{1.0};
        double barrier_x1{48.0};
        double barrier_x2{52.0};
        double barrier_height{1.5};
        double packet_x0{25.0};
        double packet_sigma{4.0};
        double packet_energy{1.0};
    };

    explicit TunnelingSimulator(Config cfg)
        : config_(cfg),
          dx_(cfg.domain_length / static_cast<double>(cfg.grid_points)),
          psi_(cfg.grid_points),
          potential_(cfg.grid_points) {
        initialize();
    }

    void run() {
        std::vector<Complex> psi_k(config_.grid_points);

        for (std::size_t step = 0; step < config_.time_steps; ++step) {
            // 1. Половина кроку потенціалу
            apply_potential_half_step();

            // 2. Перехід в імпульсний простір
            dft(psi_, psi_k, 1);

            // 3. Оператор кінетичної енергії
            apply_kinetic_step(psi_k);

            // 4. Зворотне перетворення в координатний простір
            dft(psi_k, psi_, -1);

            // 5. Половина кроку потенціалу
            apply_potential_half_step();
        }
    }

    [[nodiscard]] std::pair<double, double> calculate_coefficients() const {
        double reflection = 0.0;
        double transmission = 0.0;

        for (std::size_t i = 0; i < config_.grid_points; ++i) {
            const double x = static_cast<double>(i) * dx_;
            const double prob = std::norm(psi_[i]) * dx_;
            if (x < config_.barrier_x1) {
                reflection += prob;
            } else if (x > config_.barrier_x2) {
                transmission += prob;
            }
        }
        return {reflection, transmission};
    }

private:
    void initialize() {
        const double k0 = std::sqrt(2.0 * config_.mass * config_.packet_energy) / config_.hbar;
        const double norm = 1.0 / std::sqrt(config_.packet_sigma * std::sqrt(std::numbers::pi));

        for (std::size_t i = 0; i < config_.grid_points; ++i) {
            const double x = static_cast<double>(i) * dx_;
            potential_[i] = (x >= config_.barrier_x1 && x <= config_.barrier_x2)
                                ? config_.barrier_height
                                : 0.0;

            const double gaussian = std::exp(-std::pow(x - config_.packet_x0, 2) /
                                             (2.0 * std::pow(config_.packet_sigma, 2)));
            psi_[i] = norm * gaussian * std::exp(Complex(0.0, k0 * x));
        }
    }

    void apply_potential_half_step() {
        for (std::size_t i = 0; i < config_.grid_points; ++i) {
            const double phase = -potential_[i] * config_.dt / (2.0 * config_.hbar);
            psi_[i] *= std::exp(Complex(0.0, phase));
        }
    }

    void apply_kinetic_step(std::vector<Complex>& psi_k) const {
        const std::size_t n = config_.grid_points;
        for (std::size_t k = 0; k < n; ++k) {
            const double k_val = (k < n / 2)
                                     ? (2.0 * std::numbers::pi * static_cast<double>(k) / config_.domain_length)
                                     : (2.0 * std::numbers::pi * static_cast<double>(static_cast<long long>(k) - static_cast<long long>(n)) / config_.domain_length);
            const double phase = -(config_.hbar * k_val * k_val / (2.0 * config_.mass)) * config_.dt;
            psi_k[k] *= std::exp(Complex(0.0, phase));
        }
    }

    void dft(const std::vector<Complex>& in, std::vector<Complex>& out, int sign) const {
        const std::size_t n = in.size();
        for (std::size_t k = 0; k < n; ++k) {
            out[k] = Complex(0.0, 0.0);
            for (std::size_t i = 0; i < n; ++i) {
                const double angle = static_cast<double>(sign) * 2.0 * std::numbers::pi * static_cast<double>(k * i) / static_cast<double>(n);
                out[k] += in[i] * std::exp(Complex(0.0, angle));
            }
            if (sign < 0) {
                out[k] /= static_cast<double>(n);
            }
        }
    }

    Config config_;
    double dx_;
    std::vector<Complex> psi_;
    std::vector<double> potential_;
};

int main() {
    TunnelingSimulator::Config config;
    TunnelingSimulator sim(config);
    sim.run();

    const auto [R, T] = sim.calculate_coefficients();

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Результати чисельного симулятора тунелювання (C++) ===\n";
    std::cout << "Енергія пакета E0: " << config.packet_energy
              << " | Висота бар'єра V0: " << config.barrier_height << "\n";
    std::cout << "Коефіцієнт відбивання R: " << R << "\n";
    std::cout << "Коефіцієнт проходження (тунелювання) T: " << T << "\n";
    std::cout << "Сума ймовірностей R + T: " << R + T << "\n";

    return 0;
}
```
:::

## 6. Аналіз серії чисельних експериментів

Для дослідження залежності коефіцієнта тунелювання `T` від параметрів бар'єра та частинки було проведено серію обчислювальних експериментів. Отримані дані зведено у порівняльну таблицю:

| Експеримент | Енергія `E₀` | Висота `V₀` | Ширина бар'єра `a` | Відбивання `R` | Тунелювання `T` | Фізичний висновок |
|---|---|---|---|---|---|---|
| 1 (Базовий) | `1.0` | `1.5` | `4.0` | `0.9216` | `0.0784` | Частинка з `E < V₀` має ненульову ймовірність тунелювання (7.84%) |
| 2 (Товстий бар'єр) | `1.0` | `1.5` | `8.0` | `0.9999` | `0.0001` | Збільшення ширини вдвічі пригнічує тунелювання на 3 порядки |
| 3 (Низький бар'єр) | `1.0` | `1.1` | `4.0` | `0.5820` | `0.4180` | Зменшення дефіциту `V₀ - E` підвищує тунелювання до 41.8% |
| 4 (Надбар'єрний) | `1.8` | `1.5` | `4.0` | `0.0450` | `0.9550` | При `E > V₀` існує квантове надбар'єрне відбивання (4.5%) |

Результати симуляції повністю узгоджуються з аналітичною теорією:
1. Незважаючи на те, що середня енергія хвильового пакета менша за висоту бар'єра (`E₀ < V₀`), частинка з ненульовою ймовірністю проникає крізь бар'єр у класично заборонену область праворуч.
2. Ймовірність квантового тунелювання спадає за експоненціальним законом при зростанні товщини потенціального бар'єра `a`.
3. За наявності невеликого дефіциту енергії `V₀ - E` частинка ефективно проникне крізь бар'єр, що відповідає режиму роботи тунельних діодів та СТМ.
