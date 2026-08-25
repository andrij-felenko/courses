# ⚙️ Чисельне моделювання еволюції та розпливання квантового хвильового пакета

Нерівність Гайзенберга запевняє, що будь-який квантовий стан із обмеженою просторовою шириною `σ_x` неминуче містить спектральний розкид імпульсів `σ_p ≥ ℏ / (2 σ_x)`. У разі вільного руху частинки (коли зовнішній потенціал відсутній, `V(x) = 0`) складові хвильового пакета з вищими імпульсами (вищими фазовими швидкостями) випереджають повільніші складові. Як наслідок, просторовий розмах хвильового пакета монотонно зростає у часі — явище, відоме у фізиці як **дисперсійне розпливання хвильового пакета**.

Еволюція Гаусового хвильового пакета описується аналітичними формулами зміни його ширини `σ(t)`, виявляє різницю між фазовою та груповою швидкостями, підпорядковується теоремі Еренфеста для руху в зовнішніх полях і обчислюється чисельними алгоритмами розв'язання часового рівняння Шредінгера.

![Розпливання хвильового пакета](img/fig4-wavepacket-spreading.svg)
*Еволюція та розпливання огинаючої густини ймовірності |ψ(x, t)|² вільного Гаусового хвильового пакета з часом.*

## Фізична модель та розклад за плоскими хвилями

Розглянемо одновимірне часове рівняння Шредінгера для вільної мікрочастинки маси `m` у відсутність зовнішніх полів:

```
i ℏ (∂ψ / ∂t) = - (ℏ² / 2m) (∂²ψ / ∂x²) [вільне рівняння Шредінгера]
```

У початковий момент часу `t = 0` стан частинки задано нормованим Гаусовим хвильовим пакетом із середньою координатою `x₀ = 0`, середнім хвильовим вектором `k₀ = p₀ / ℏ` та початковою просторовою шириною `σ₀`:

```
ψ(x, 0) = (1 / (2 π σ₀²)^(1/4)) · exp( - x² / (4 σ₀²) + i k₀ x ) [початковий стан]
```

Густина ймовірності у початковий момент має симетричний Гаусів розподіл `|ψ(x, 0)|² = (1 / √(2 π σ₀²)) exp(- x² / (2 σ₀²))`, для якого початкові дисперсії складають `σ_x(0) = σ₀` та `σ_p(0) = ℏ / (2 σ₀)`, досягаючи точного теоретичного мінімуму невизначеності `σ_x(0) · σ_p(0) = ℏ / 2`.

Щоб знайти еволюцію стану `ψ(x, t)`, розкладемо початкову хвильову функцію в інтеграл Фур'є за власними функціями оператора імпульсу — плоскими хвилями `exp(i k x)`:

```
ϕ(k) = (1 / √(2 π)) ∫ ψ(x, 0) exp(-i k x) dx
= (2 σ₀² / π)^(1/4) · exp( - σ₀² (k - k₀)² ) [амплітуда Фур'є в імпульсному просторі]
```

Кожна плоска хвиля `exp(i k x)` еволюціонує у часі з власною частотою `ω(k) = ℏ k² / (2m)` відповідно до закону `exp(-i ω(k) t)`. Зворотне перетворення Фур'є дає точний аналітичний вираз для хвильової функції у довільний момент часу `t > 0`:

```
ψ(x, t) = (1 / √(2 π)) ∫ ϕ(k) exp(i (k x - ω(k) t)) dk
= (1 / (2 π σ₀²)^(1/4)) · (1 / √(1 + i ℏ t / (2 m σ₀²)))
  · exp( - (x - v₀ t)² / (4 σ₀² (1 + i ℏ t / (2 m σ₀²))) + i k₀ (x - v₀ t / 2) )
```

де `v₀ = ℏ k₀ / m` — групова швидкість руху центру пакета.

## Аналіз розпливання та кінематика хвильового пакета

Обчисливши квадрат модуля хвильової функції `|ψ(x, t)|²`, отримуємо густину ймовірності знаходження частинки у точці `x` у момент часу `t`:

```
|ψ(x, t)|² = (1 / √(2 π σ(t)²)) · exp( - (x - v₀ t)² / (2 σ(t)²) ) [густина ймовірності]
```

де часова залежність просторової ширини (стандартного відхилення) задається співвідношенням:

```
σ(t) = σ₀ · √( 1 + ( ℏ t / (2 m σ₀²) )² ) [закон розпливання пакета]
```

Ця формула ілюструє фундаментальну квантову рису: **чим тісніше ми локалізуємо частинку у початковий момент `t = 0` (тобто чим меншим є `σ₀`), тим вищою є невизначеність імпульсу `σ_p = ℏ / (2 σ₀)`, і тим швидше хвильовий пакет розпливається у просторі!**

Звернемо увагу на важливу відмінність між двома швидкостями:
1. **Фазова швидкість окремої монохроматичної хвилі:** `v_фаз = ω / k = ℏ k / (2m) = v / 2`.
2. **Групова швидкість огинаючої пакета:** `v_груп = dω / dk = ℏ k / m = v`.

Оскільки фазова швидкість удвічі менша за групову, горби окремих осциляцій всередині пакета рухаються повільніше за саму огинаючу оболонку: вони зароджуються на задньому хвості пакета, пробігають крізь центр і зникають на передньому фронті.

Для мікрочастинок (наприклад, електрона з масою `m = 9.1 · 10⁻³¹ кг` та початковим розміром `σ₀ = 0.1 нм`) характерний час розпливання `τ = 2 m σ₀² / ℏ` становить близько `1.7 · 10⁻¹⁶ с` (фемтосекунди). Натомість для макроскопічного об'єкта масою 1 грам із розміром 1 мікрон час розпливання перевищує вік Всесвіту, що пояснює, чому макроскопічні тіла рухаються за класичними траєкторіями без видимого розпливання.

## Рух у постійному силовому полі та теорема Еренфеста

Розглянемо випадок, коли на квантову частинку діє однорідна постійна сила `F` (наприклад, однорідне електричне або гравітаційне поле `V(x) = -F x`).

Рівняння Шредінгера для даної системи має вигляд:

```
i ℏ (∂ψ / ∂t) = - (ℏ² / 2m) (∂²ψ / ∂x²) - F x ψ [рівняння Шредінгера в однорідному полі]
```

Застосовуючи перетворення координат до рухомої системи відліку, що прискорюється за класичним законом `x_cl(t) = x₀ + v₀ t + (F / 2m) t²`, можна отримати точний розв'язок для хвильової функції:

```
|ψ(x, t)|² = (1 / √(2 π σ(t)²)) · exp( - (x - x_cl(t))² / (2 σ(t)²) )
```

Цей результат є глибокою ілюстрацією **теореми Еренфеста** (нід. *Paul Ehrenfest*):
1. **Центр ваги хвильового пакета `⟨x⟩(t)` рухається суворо за класичною траєкторією Ньютона:** `m (d²⟨x⟩ / dt²) = ⟨F⟩ = F`.
2. **Просторова ширина пакета `σ(t)` розпливається абсолютно так само, як і для вільної частинки:** `σ(t) = σ₀ √(1 + (ℏ t / 2 m σ₀²)²)`.

Наявність зовнішнього однорідного поля прискорює пакет як ціле, але ніяк не зупиняє і не прискорює його квантове розпливання.

## Дискретизація простору та сіткові дисперсійні похибки

Під час переходу від неперервного диференціального рівняння Шредінгера до різницевої сітки з кроком `dx` друга похідна апроксимується триточковим шаблоном:

```
∂²ψ / ∂x² ≈ (ψ_{i+1} - 2 ψ_i + ψ_{i-1}) / dx² [триточковий шаблон різниці]
```

Якщо підставити плоску хвилю `ψ_i = exp(i k x_i)` у дискретний оператор кінетичної енергії, дискретне дисперсійне співвідношення набуває вигляду:

```
ω_сітка(k) = (2 ℏ / (m dx²)) · sin²(k dx / 2) [дискретний закон дисперсії]
```

Для довгих хвиль (`k dx << 1`) расклад у ряд Тейлора дає `sin(k dx / 2) ≈ k dx / 2 - (k dx)³ / 48`, звідки:

```
ω_сітка(k) ≈ (ℏ k² / 2m) · (1 - (k dx)² / 12) [похилка просторової дискретизації]
```

Цей результат показує, що просторова дискретизація вносить штучну цифрову дисперсію. Щоб зменшити сіткову похибку до рівня менше 1%, крок сітки повинен задовольняти умову `dx ≤ λ_мін / 8 = π / (4 k_макс)`.

## Алгоритм Кранка — Ніколсон для часового рівняння Шредінгера

Для чисельного інтегрування часового рівняння Шредінгера дискретизуємо просторову область `[x_min, x_max]` на `N` вузлів з кроком `dx = (x_max - x_min) / (N - 1)` та часовий крок `dt`.

Проста явна схема Ейлера є нестійкою. Неявна схема Кранка — Ніколсон (Crank-Nicolson scheme) бере просторову другу похідну як середнє арифметичне між часовими шарами `n` та `n+1`:

```
(ψ^{n+1}_i - ψ^n_i) / dt = (i ℏ / (4 m dx²)) · [ (ψ^{n+1}_{i+1} - 2 ψ^{n+1}_i + ψ^{n+1}_{i-1})
                                                 + (ψ^n_{i+1} - 2 ψ^n_i + ψ^n_{i-1}) ]
```

Ввівши безрозмірну константу `α = ℏ dt / (4 m dx²)`, отримуємо тридіагональну систему лінійних алгебраїчних рівнянь відносно невідомих значень `ψ^{n+1}`:

```
-i α ψ^{n+1}_{i-1} + (1 + 2i α) ψ^{n+1}_i - i α ψ^{n+1}_{i+1}
= i α ψ^n_{i-1} + (1 - 2i α) ψ^n_i + i α ψ^n_{i+1} [система Кранка — Ніколсон]
```

Ця система є безумовно стійкою і суворо унітарною, зберігаючи норму `∫ |ψ|² dx = 1` з точністю до машинного нуля на кожному кроці за часом.

## Повнофункціональна програмна реалізація

Нижче наведено порівняльні реалізації чисельного розв'язувача еволюції хвильового пакета методом Кранка — Ніколсон мовами C, C++ та Python.

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

/* Структура для зберігання статистичних параметрів хвильового пакета */
typedef struct {
    double norm;
    double mean_x;
    double var_x;
} WavepacketStats;

WavepacketStats compute_stats(const double complex *psi, int n, double dx, double x_min) {
    double norm = 0.0;
    double mean_x = 0.0;
    double var_x = 0.0;

    for (int i = 0; i < n; i++) {
        double prob = cabs(psi[i]) * cabs(psi[i]);
        double x = x_min + i * dx;
        norm += prob * dx;
        mean_x += x * prob * dx;
    }

    if (norm > 0.0) {
        mean_x /= norm;
        for (int i = 0; i < n; i++) {
            double prob = cabs(psi[i]) * cabs(psi[i]);
            double x = x_min + i * dx;
            var_x += (x - mean_x) * (x - mean_x) * prob * dx;
        }
        var_x /= norm;
    }

    WavepacketStats stats = {norm, mean_x, sqrt(var_x)};
    return stats;
}

/* Алгоритм прогонки (метод Томаса) для розв'язання тридіагональної СЛАУ */
void solve_tridiagonal(int n, const double complex *a, const double complex *b,
                       const double complex *c, double complex *d, double complex *x) {
    double complex *c_prime = (double complex *)malloc(n * sizeof(double complex));
    double complex *d_prime = (double complex *)malloc(n * sizeof(double complex));

    c_prime[0] = c[0] / b[0];
    d_prime[0] = d[0] / b[0];

    for (int i = 1; i < n; i++) {
        double complex denom = b[i] - a[i] * c_prime[i - 1];
        c_prime[i] = c[i] / denom;
        d_prime[i] = (d[i] - a[i] * d_prime[i - 1]) / denom;
    }

    x[n - 1] = d_prime[n - 1];
    for (int i = n - 2; i >= 0; i--) {
        x[i] = d_prime[i] - c_prime[i] * x[i + 1];
    }

    free(c_prime);
    free(d_prime);
}

int main(void) {
    const int N = 400;
    const double x_min = -20.0;
    const double x_max = 20.0;
    const double dx = (x_max - x_min) / (N - 1);
    const double dt = 0.01;
    const double hbar = 1.0;
    const double m = 1.0;
    const double sigma_0 = 1.0;
    const double k0 = 2.0;
    const int num_steps = 200;

    double complex *psi = (double complex *)malloc(N * sizeof(double complex));
    double complex *rhs = (double complex *)malloc(N * sizeof(double complex));
    double complex *psi_next = (double complex *)malloc(N * sizeof(double complex));

    /* Ініціалізація початкового Гаусового пакета */
    double norm_factor = 1.0 / pow(2.0 * PI * sigma_0 * sigma_0, 0.25);
    for (int i = 0; i < N; i++) {
        double x = x_min + i * dx;
        psi[i] = norm_factor * exp(-x * x / (4.0 * sigma_0 * sigma_0)) * cexp(I * k0 * x);
    }

    /* Формування діагональних елементів Кранка - Ніколсон */
    double alpha = hbar * dt / (4.0 * m * dx * dx);
    double complex diag_main = 1.0 + 2.0 * I * alpha;
    double complex diag_sub = -I * alpha;

    double complex *a = (double complex *)calloc(N, sizeof(double complex));
    double complex *b = (double complex *)malloc(N * sizeof(double complex));
    double complex *c = (double complex *)calloc(N, sizeof(double complex));

    for (int i = 0; i < N; i++) {
        b[i] = diag_main;
        if (i > 0) a[i] = diag_sub;
        if (i < N - 1) c[i] = diag_sub;
    }

    printf("Крок\tЧас t\tНорма\tСереднє X\tШирина sigma(t)\n");
    for (int step = 0; step <= num_steps; step += 40) {
        WavepacketStats stats = compute_stats(psi, N, dx, x_min);
        printf("%d\t%.2f\t%.5f\t%.4f\t\t%.4f\n", step, step * dt, stats.norm, stats.mean_x, stats.var_x);

        if (step == num_steps) break;

        for (int iter = 0; iter < 40; iter++) {
            for (int i = 1; i < N - 1; i++) {
                rhs[i] = (1.0 - 2.0 * I * alpha) * psi[i] + I * alpha * (psi[i - 1] + psi[i + 1]);
            }
            rhs[0] = 0.0;
            rhs[N - 1] = 0.0;

            solve_tridiagonal(N, a, b, c, rhs, psi_next);
            for (int i = 0; i < N; i++) psi[i] = psi_next[i];
        }
    }

    free(psi); free(rhs); free(psi_next);
    free(a); free(b); free(c);
    return 0;
}
```
```cpp
// cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>

class WavepacketSolver {
public:
    using Complex = std::complex<double>;

    struct StateStats {
        double norm{0.0};
        double mean_x{0.0};
        double sigma_x{0.0};
    };

    WavepacketSolver(int grid_size, double x_min, double x_max, double sigma0, double k0)
        : n_(grid_size), x_min_(x_min), x_max_(x_max), dx_((x_max - x_min) / (grid_size - 1)),
          psi_(grid_size) {
        init_gaussian(sigma0, k0);
    }

    StateStats stats() const {
        double norm = 0.0;
        double mean_x = 0.0;
        double var_x = 0.0;

        for (int i = 0; i < n_; ++i) {
            double prob = std::norm(psi_[i]);
            double x = x_min_ + i * dx_;
            norm += prob * dx_;
            mean_x += x * prob * dx_;
        }

        if (norm > 0.0) {
            mean_x /= norm;
            for (int i = 0; i < n_; ++i) {
                double prob = std::norm(psi_[i]);
                double x = x_min_ + i * dx_;
                var_x += (x - mean_x) * (x - mean_x) * prob * dx_;
            }
            var_x /= norm;
        }

        return {norm, mean_x, std::sqrt(var_x)};
    }

    void step_crank_nicolson(double dt, double hbar = 1.0, double mass = 1.0) {
        const double alpha = hbar * dt / (4.0 * mass * dx_ * dx_);
        const Complex diag_main = 1.0 + Complex(0, 2.0 * alpha);
        const Complex diag_off = Complex(0, -alpha);

        std::vector<Complex> rhs(n_, 0.0);
        for (int i = 1; i < n_ - 1; ++i) {
            rhs[i] = (1.0 - Complex(0, 2.0 * alpha)) * psi_[i]
                   + Complex(0, alpha) * (psi_[i - 1] + psi_[i + 1]);
        }

        // Застосування методу прогонки Томаса
        std::vector<Complex> c_prime(n_, 0.0);
        std::vector<Complex> d_prime(n_, 0.0);

        c_prime[0] = diag_off / diag_main;
        d_prime[0] = rhs[0] / diag_main;

        for (int i = 1; i < n_; ++i) {
            Complex denom = diag_main - diag_off * c_prime[i - 1];
            c_prime[i] = diag_off / denom;
            d_prime[i] = (rhs[i] - diag_off * d_prime[i - 1]) / denom;
        }

        psi_[n_ - 1] = d_prime[n_ - 1];
        for (int i = n_ - 2; i >= 0; --i) {
            psi_[i] = d_prime[i] - c_prime[i] * psi_[i + 1];
        }
    }

private:
    void init_gaussian(double sigma0, double k0) {
        const double norm_factor = 1.0 / std::pow(2.0 * std::numbers::pi * sigma0 * sigma0, 0.25);
        for (int i = 0; i < n_; ++i) {
            double x = x_min_ + i * dx_;
            psi_[i] = norm_factor * std::exp(-x * x / (4.0 * sigma0 * sigma0))
                    * std::exp(Complex(0, k0 * x));
        }
    }

    int n_;
    double x_min_, x_max_, dx_;
    std::vector<Complex> psi_;
};

int main() {
    WavepacketSolver solver(400, -20.0, 20.0, 1.0, 2.0);

    std::cout << "Крок\tНорма\t\tСереднє X\tШирина sigma(t)\n";
    for (int step = 0; step <= 200; ++step) {
        if (step % 40 == 0) {
            auto [norm, mean_x, sigma_x] = solver.stats();
            std::cout << step << "\t" << norm << "\t" << mean_x << "\t\t" << sigma_x << "\n";
        }
        solver.step_crank_nicolson(0.01);
    }
    return 0;
}
```
```py
# py
import numpy as np

def simulate_wavepacket(N=400, x_min=-20.0, x_max=20.0, dt=0.01, steps=200, sigma0=1.0, k0=2.0):
    x = np.linspace(x_min, x_max, N)
    dx = x[1] - x[0]

    # Початковий Гаусів пакет
    psi = (1.0 / (2.0 * np.pi * sigma0**2)**0.25) * np.exp(-x**2 / (4.0 * sigma0**2) + 1j * k0 * x)

    # Параметри Кранка - Ніколсон
    alpha = dt / (4.0 * dx**2)
    diag_main = (1.0 + 2j * alpha) * np.ones(N, dtype=complex)
    diag_off = (-1j * alpha) * np.ones(N - 1, dtype=complex)

    # Побудова тридіагональної матриці
    A = np.diag(diag_main) + np.diag(diag_off, k=1) + np.diag(diag_off, k=-1)

    print("Крок\tНорма\t\tСереднє X\tШирина sigma(t)")
    for step in range(steps + 1):
        norm = np.sum(np.abs(psi)**2) * dx
        mean_x = np.sum(x * np.abs(psi)**2) * dx / norm
        sigma_x = np.sqrt(np.sum((x - mean_x)**2 * np.abs(psi)**2) * dx / norm)

        if step % 40 == 0:
            print(f"{step}\t{norm:.5f}\t{mean_x:.4f}\t\t{sigma_x:.4f}")

        # Формування правої частини
        rhs = np.zeros_like(psi)
        rhs[1:-1] = (1.0 - 2j * alpha) * psi[1:-1] + 1j * alpha * (psi[:-2] + psi[2:])

        # Розв'язання СЛАУ
        psi = np.linalg.solve(A, rhs)

if __name__ == "__main__":
    simulate_wavepacket()
```
:::

## Аналіз пасток та рекомендації для чисельного розв'язання

1. **Крайові умови та відбиття хвилі (Boundary Reflection):**
   При досягненні поширеним пакетом меж обчислювального доменованого простору `x_min` або `x_max` на нульових граничних умовах виникає штучне відбиття хвилі, що викликає хибну самоінтерференцію. Для моделювання нескінченного середовища біля країв додають комплексний поглинаючий потенціал (англ. *Complex Absorbing Potential, CAP*) `V_abs(x) = -i V₀ ((x - x_bound) / w)⁴`, який невідображувально гасить хвилю.

2. **Критерій числової стійкості та збереження норми:**
   У той час як явна різницева схема (Euler method) є безумовно нестійкою для рівняння Шредінгера, метод Кранка — Ніколсон є унітарним: оператор еволюції `U_CN = (I + i Δt Ĥ / 2)⁻¹ (I - i Δt Ĥ / 2)` є суворо унітарним (`U_CN⁺ U_CN = I`), що гарантує точне збереження норми `∫ |ψ|² dx = 1` при довільному кроці `Δt`.

3. **Співвідношення дискретизації `Δx` та `Δp`:**
   Відповідно до принципу невизначеності, максимальний імпульс, який може бути репрезентований на просторовій сітці з кроком `dx`, обмежений теоремою Найквіста — Котельникова: `p_max = π ℏ / dx`. Якщо початкова ширина `σ₀` занадто мала, високі імпульсні гармоніки `k > k_max` викличуть явище аліасингу (спотворення високих частот). Оптимальний вибір кроку сітки вимагає `dx ≤ σ₀ / 4`.
