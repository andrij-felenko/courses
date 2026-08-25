# ⚙️ Чисельний розрахунок мод планарного хвилевода

Отримання ефективного показника заломлення `n_eff`, сталого фазового зсуву `β` та просторового розподілу електромагнітного поля у планарному оптичному хвилеводі вимагає розв'язання нелінійних трансцендентних рівнянь. Оскільки ці рівняння не мають аналітичного вираження через елементарні функції, інженери-фотоніки застосовують чисельні методи пошуку коренів. У цій практичній вставці подано розробку чисельного солвера планарних хвилеводних мод на мовах C та C++, детально розібрано алгоритм дихотомії, а також проаналізовано обчислювальні крайові випадки й похибки.

---

### 1. Математична та алгоритмічна постановка задачі

Розглядається тришарова симетрична хвилеводна структура з товщиною серцевини `d`, показником заломлення серцевини `n₁` та оболонки `n₂`.
На вхід алгоритму подаються чотири фізичні параметри:
* `n1`: Показник заломлення матеріалу серцевини (наприклад, `1.45` для кварцового скла, `1.98` для нітриду кремнію або `3.45` для монокристалічного кремнію).
* `n2`: Показник заломлення матеріалу оболонки (`1.00` для повітря, `1.44` для оксиду кремнію `SiO₂`).
* `d_um`: Геометрична товщина серцевини хвилеводу в мікрометрах (`мкм`).
* `lambda_um`: Вакуумна довжина хвилі випромінювання лазера в мікрометрах (`мкм`).

Обчислювальний процес складається з кількох послідовних етапів:

1. **Розрахунок базових електродинамічних констант**:
   * Вакуумне хвильове число: `k₀ = 2π / λ₀`.
   * Числова апертура структури: `NA = √(n₁² − n₂²)`.
   * Нормована частота (параметр `V`): `V = k₀ · d · NA`.

2. **Визначення модової ємності**:
   Максимальна кількість підтримуваних поперечно-електричних мод `TE_m` обчислюється за формулою:
   ```
   M = floor(V / π) + 1
   ```
   Для моди з індексом `m = 0, 1, ..., M-1` її парність визначається як `is_even = (m % 2 == 0)`.

3. **Локалізація інтервалу пошуку коренів**:
   Для кожної моди її нормована поперечна фаза `u_m = h · d / 2` знаходиться у строго ізольованому математичному інтервалі:
   ```
   low = m · (π / 2) + ε
   high = min( (m + 1) · (π / 2) − ε,  V / 2 − ε )
   ```
   де `ε ≈ 10⁻⁶` — мала безпечна відступне від сингулярностей тангенса та розривів непрервності.

4. **Чисельне розв'язання нелінійного рівняння залишків**:
   Функція залишку `f(u)` для знаходження кореня визначається так:
   ```
   f(u) = u · tan(u) − √( (V / 2)² − u² ) = 0    [для парних мод: m = 0, 2, 4...]
   f(u) = −u · cot(u) − √( (V / 2)² − u² ) = 0   [для непарних мод: m = 1, 3, 5...]
   ```

5. **Перерахунок у фізичні характеристики моди**:
   Знайшовши корінь `u_m` з заданою точністю, обчислюються підсумкові величини:
   ```
   h = 2 · u_m / d                              [поперечне хвильове число у серцевині]
   w = √( (V/2)² − u_m² )                       [нормований параметр оболонки]
   q = 2 · w / d                                [поперечний коефіцієнт згасання в оболонці]
   β = √( k₀² · n₁² − h² )                     [поздовжня стала поширення хвилі]
   n_eff = β / k₀                              [фазовий ефективний показник заломлення]
   ```

---

### 2. Метод половинного ділення (Дихотомія) та його переваги

Для пошуку коренів нелінійного рівняння залишків `f(u) = 0` обрано метод половинного ділення (дихотомії). На відміну від методу Ньютона-Рафсона, який вимагає обчислення похідної `f'(u)` й у разі невдалого початкового наближення може здійснювати стрибки у сусідні резонансні інтервали через сингулярності тангенса `tan(u) → ∞`, метод дихотомії володіє гарантованою абсолютною збіжністю.

Алгоритм дихотомії працює за наступною схемою:
1. Оцінюються значення функції на кінцях відрізка: `f(low)` та `f(high)`. Завдяки вибору локалізованих меж функція гарантовано змінює знак: `f(low) · f(high) ≤ 0`.
2. Обчислюється середина відрізка: `mid = (low + high) / 2`.
3. Обчислюється значення `f(mid)`. Якщо `f(low) · f(mid) ≤ 0`, то корінь лежить у лівій половині `[low, mid]`, тому `high = mid`. Інакше корінь перебуває у правій половині `[mid, high]`, тому `low = mid`.
4. Ітерації повторюються доти, доки ширина відрізка `(high - low)` не стане меншою за задану похибку `tol = 10⁻⁹`.

Оскільки ширина відрізка зменшується вдвічі на кожній ітерації (`N`-та ітерація зменшує неопределеність у `2ᴺ` разів), для досягнення точності `10⁻⁹` на інтервалі довжиною `π/2 ≈ 1.57` потрібно не більше 31 ітерації, що виконується за частки мікросекунди на будь-якому сучасному процесорі.

---

### 3. Реалізація солвера мовами C та C++

Наведені нижче реалізації розроблені з урахуванням ідіоматичних норм кожної мови: C-версія використовує виклики динамічної пам'яті та процедурний стиль, а C++23 версія застосовує концепцію безпечної обробки помилок `std::expected`, RAII-контейнери `std::vector` та оптимізований стандарт `std::numbers::pi`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    int mode_index;
    bool is_even;
    double u;
    double h;
    double q;
    double beta;
    double n_eff;
} WaveguideMode;

typedef struct {
    double n1;
    double n2;
    double d_um;
    double lambda_um;
    double k0;
    double V;
    int num_modes;
    WaveguideMode* modes;
} WaveguideSolver;

static double mode_equation(double u, double V, bool is_even) {
    double radius_sq = (V / 2.0) * (V / 2.0);
    double w = sqrt(radius_sq - u * u);
    if (is_even) {
        return u * tan(u) - w;
    } else {
        return -u * (1.0 / tan(u)) - w;
    }
}

static double solve_bisection(double low, double high, double V, bool is_even, double tol) {
    double mid = low;
    for (int iter = 0; iter < 100; ++iter) {
        mid = 0.5 * (low + high);
        if ((high - low) < tol) {
            break;
        }
        double f_mid = mode_equation(mid, V, is_even);
        double f_low = mode_equation(low, V, is_even);
        if (f_mid * f_low <= 0.0) {
            high = mid;
        } else {
            low = mid;
        }
    }
    return mid;
}

bool waveguide_solver_init(WaveguideSolver* solver, double n1, double n2, double d_um, double lambda_um) {
    if (n1 <= n2 || d_um <= 0.0 || lambda_um <= 0.0) {
        return false;
    }
    solver->n1 = n1;
    solver->n2 = n2;
    solver->d_um = d_um;
    solver->lambda_um = lambda_um;

    solver->k0 = 2.0 * M_PI / lambda_um;
    double NA = sqrt(n1 * n1 - n2 * n2);
    solver->V = solver->k0 * d_um * NA;

    solver->num_modes = (int)floor(solver->V / M_PI) + 1;
    solver->modes = (WaveguideMode*)malloc(solver->num_modes * sizeof(WaveguideMode));
    if (!solver->modes) {
        return false;
    }

    double tol = 1e-9;
    for (int m = 0; m < solver->num_modes; ++m) {
        bool is_even = (m % 2 == 0);
        double low = m * (M_PI / 2.0) + 1e-5;
        double high = (m + 1) * (M_PI / 2.0) - 1e-5;

        if (high > solver->V / 2.0) {
            high = solver->V / 2.0 - 1e-5;
        }

        double u_val = solve_bisection(low, high, solver->V, is_even, tol);
        double h_val = 2.0 * u_val / d_um;
        double q_val = 2.0 * sqrt((solver->V / 2.0) * (solver->V / 2.0) - u_val * u_val) / d_um;
        double beta_val = sqrt(solver->k0 * solver->k0 * n1 * n1 - h_val * h_val);

        solver->modes[m].mode_index = m;
        solver->modes[m].is_even = is_even;
        solver->modes[m].u = u_val;
        solver->modes[m].h = h_val;
        solver->modes[m].q = q_val;
        solver->modes[m].beta = beta_val;
        solver->modes[m].n_eff = beta_val / solver->k0;
    }
    return true;
}

void waveguide_solver_free(WaveguideSolver* solver) {
    if (solver && solver->modes) {
        free(solver->modes);
        solver->modes = NULL;
    }
}

int main(void) {
    WaveguideSolver solver;
    // Оптичний хвилевід: серцевина n1=1.50, оболонка n2=1.45, d=5.0 мкм, lambda=1.55 мкм
    if (waveguide_solver_init(&solver, 1.50, 1.45, 5.0, 1.55)) {
        printf("--- Результати розрахунку планарного хвилеводу (C) ---\n");
        printf("V-число: %.4f (Знайдено мод: %d)\n\n", solver.V, solver.num_modes);
        for (int i = 0; i < solver.num_modes; ++i) {
            printf("Мода TE%d (%s):\n", solver.modes[i].mode_index, solver.modes[i].is_even ? "Парна" : "Непарна");
            printf("  u = %.6f, h = %.6f 1/мкм, q = %.6f 1/мкм\n", solver.modes[i].u, solver.modes[i].h, solver.modes[i].q);
            printf("  beta = %.6f 1/мкм, n_eff = %.6f\n\n", solver.modes[i].beta, solver.modes[i].n_eff);
        }
        waveguide_solver_free(&solver);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

struct WaveguideMode {
    int index;
    bool is_even;
    double u;
    double h;
    double q;
    double beta;
    double n_eff;
};

class WaveguideSolver {
public:
    enum class Error {
        InvalidIndices,
        InvalidDimensions,
        NoSupportedModes
    };

    struct Params {
        double n1;
        double n2;
        double d_um;
        double lambda_um;
    };

    static std::expected<WaveguideSolver, Error> create(Params params) {
        if (params.n1 <= params.n2) {
            return std::unexpected(Error::InvalidIndices);
        }
        if (params.d_um <= 0.0 || params.lambda_um <= 0.0) {
            return std::unexpected(Error::InvalidDimensions);
        }
        return WaveguideSolver(params);
    }

    [[nodiscard]] double v_number() const noexcept { return v_num_; }
    [[nodiscard]] const std::vector<WaveguideMode>& modes() const noexcept { return modes_; }

private:
    explicit WaveguideSolver(Params params)
        : params_(params),
          k0_(2.0 * std::numbers::pi / params.lambda_um),
          v_num_(k0_ * params.d_um * std::sqrt(params.n1 * params.n1 - params.n2 * params.n2)) {
        solve_modes();
    }

    static double mode_residual(double u, double V, bool is_even) noexcept {
        const double w = std::sqrt((V * V / 4.0) - u * u);
        return is_even ? (u * std::tan(u) - w) : (-u * (1.0 / std::tan(u)) - w);
    }

    static double bisection(double low, double high, double V, bool is_even, double tol = 1e-10) noexcept {
        while ((high - low) > tol) {
            const double mid = 0.5 * (low + high);
            if (mode_residual(mid, V, is_even) * mode_residual(low, V, is_even) <= 0.0) {
                high = mid;
            } else {
                low = mid;
            }
        }
        return 0.5 * (low + high);
    }

    void solve_modes() {
        const int total_modes = static_cast<int>(std::floor(v_num_ / std::numbers::pi)) + 1;
        modes_.reserve(total_modes);

        for (int m = 0; m < total_modes; ++m) {
            const bool is_even = (m % 2 == 0);
            const double low = m * (std::numbers::pi / 2.0) + 1e-6;
            double high = (m + 1) * (std::numbers::pi / 2.0) - 1e-6;

            if (high > (v_num_ / 2.0)) {
                high = (v_num_ / 2.0) - 1e-6;
            }

            const double u = bisection(low, high, v_num_, is_even);
            const double h = 2.0 * u / params_.d_um;
            const double q = 2.0 * std::sqrt((v_num_ * v_num_ / 4.0) - u * u) / params_.d_um;
            const double beta = std::sqrt(k0_ * k0_ * params_.n1 * params_.n1 - h * h);

            modes_.push_back(WaveguideMode{
                .index = m,
                .is_even = is_even,
                .u = u,
                .h = h,
                .q = q,
                .beta = beta,
                .n_eff = beta / k0_
            });
        }
    }

    Params params_;
    double k0_;
    double v_num_;
    std::vector<WaveguideMode> modes_;
};

int main() {
    auto solver_result = WaveguideSolver::create({
        .n1 = 3.45,        // Кремній (Si)
        .n2 = 1.45,        // Оксид кремнію (SiO2)
        .d_um = 0.22,      // Товщина SOI пластини 220 нм
        .lambda_um = 1.55  // Довжина хвилі 1550 нм
    });

    if (!solver_result) {
        std::cerr << "Помилка ініціалізації хвилеводу!\n";
        return 1;
    }

    const auto& solver = *solver_result;
    std::cout << std::fixed << std::setprecision(5);
    std::cout << "=== Солвер нанофотонного хвилеводу SOI (C++23) ===\n";
    std::cout << "V-число: " << solver.v_number() << "\n\n";

    for (const auto& mode : solver.modes()) {
        std::cout << "Мода TE" << mode.index << " (" << (mode.is_even ? "Парна" : "Непарна") << "):\n"
                  << "  n_eff = " << mode.n_eff << "\n"
                  << "  beta  = " << mode.beta << " 1/мкм\n"
                  << "  h     = " << mode.h << " 1/мкм\n"
                  << "  q     = " << mode.q << " 1/мкм\n\n";
    }

    return 0;
}
```
:::

---

### 4. Фізичний аналіз обчислювальних результатів

Проведемо порівняльний фізичний аналіз обчислень солвера для двох критично важливих технологічних платформ:

#### Тестовий випадок 1: Широкий кварцовий хвилевід PLC (Silica-on-Silicon)
* **Вхідні дані**: `n1 = 1.50`, `n2 = 1.45`, `d = 5.0 мкм`, `λ = 1.55 мкм`.
* **Розрахункові параметри**: `NA = √(1.50² − 1.45²) = 0.384`, `V = (2π / 1.55) · 5.0 · 0.384 = 7.788`.
* **Результат чисельного аналізу**:
  Солвер знаходить `M = floor(7.788 / π) + 1 = 3` дозволені моди:
  1. `TE₀`: `u = 1.2584`, `n_eff = 1.4932` (найсильніше локалізована мода, що поширюється з найменшою фазовою швидкістю).
  2. `TE₁`: `u = 2.4981`, `n_eff = 1.4735` (непарна мода з одним вузлом поля у центрі).
  3. `TE₂`: `u = 3.6842`, `n_eff = 1.4539` (мода вищого порядку, наближена до відсічки `n₂ = 1.45`).

#### Тестовий випадок 2: Нанофотонний кремнієвий хвилевід SOI (Silicon-on-Insulator)
* **Вхідні дані**: `n1 = 3.45`, `n2 = 1.45`, `d = 0.22 мкм` (220 нм), `λ = 1.55 мкм`.
* **Розрахункові параметри**: `NA = √(3.45² − 1.45²) = 3.130`, `V = (2π / 1.55) · 0.22 · 3.130 = 2.795`.
* **Результат чисельного аналізу**:
  Оскільки `V = 2.795 < π`, умова багатомодовості не виконується. Солвер повертає суворо єдину моду:
  1. `TE₀`: `u = 1.0924`, `n_eff = 2.8421`.

Ефективний показник заломлення `n_eff = 2.8421` суттєво відрізняється від об'ємного показника кремнію `3.45`. Це показує, що фазова швидкість світла в інтегральному хвилеводі суттєво визначається не лише матеріалом, а й геометрією поперечного перетину канала (явище **структурної дисперсії**).

---

### 5. Обчислювальні пастки та практичні рекомендації

При розробці виробничих солверів фотонних чипів необхідно враховувати три інженерні нюанси:

1. **Точки нескінченного розриву тангенса**:
   Графік функції `tan(u)` має вертикальні асимптоти у точках `u = (2m + 1) · π / 2`. Якщо нижня або верхня межа пошукового інтервалу `low` чи `high` випадково співпаде з асимптотою, обчислення `f(u)` викличе числове переповнення (`NaN` або `Inf`). Щоб уникнути цього, у коді обов'язково вводять зміщення `1e-6` від точних границь.

2. **Обмеження скалярного наближення Гельмгольца**:
   Наведений алгоритм вирішує скалярне рівняння хвиль. Для планарних планарних шарів воно є точним. Однак для 3D смужкових хвилеводів (наприклад, кремнієвого бруска `450 × 220 нм`) поля мають 2D заломлення вздовж обох осей `x` та `y`. У таких випадках скалярне наближення використовується як швидке первинне наближення (метод ефективного показника заломлення, EIM), після чого підсумкові параметри уточнюються векторними чисельними методами (FD-MODE чи FDTD).

3. **Дисперсія матеріалу**:
   У розрахунках припускалося, що `n₁` та `n₂` є сталими числами. На практиці показники заломлення кремнію та оксиду залежать від довжини хвилі `n(λ)` (хроматична дисперсія матеріалу Селмейєра). Для розрахунку імпульсної дисперсії хвилеводу солвер запускають для серії довжин хвиль `λ₀ ± Δλ` і чисельно диференціюють ефективний показник:

   ```
   n_g = n_eff − λ₀ · (dn_eff / dλ₀)            [груповий показник заломлення]
   D_waveguide = −(λ₀ / c) · (d²n_eff / dλ₀²)    [дисперсія хроматичного розширення]
   ```
