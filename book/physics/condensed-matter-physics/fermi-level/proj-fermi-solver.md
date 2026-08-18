# ⚙️ Чисельний розрахунок рівноважного рівня Фермі в напівпровідниках

У чисельному моделюванні напівпровідникових приладів, розрахунку зонних діаграм діодів, транзисторів та сонячних елементів, а також при аналізі температурних характеристик датчиків постає фундаментальна обчислювальна задача: розрахувати точне значення рівня Фермі `E_F` для напівпровідникового кристала з довільною концентрацією донорних `N_d` та акцепторних `N_a` домішок при заданій температурі `T`.

Оскільки рівняння електронейтральності кристала є нелінійним і трансцендентним, його розв'язання не виражається у замкненій аналітичній формі й вимагає застосування чисельних методів знаходження кореня.

---

## 1. Фізична постановка задачі та умови електронейтральності

У рівноважному об'ємі напівпровідника сумарний об'ємний електричний заряд дорівнює нулю. Це означає, що щільність позитивних зарядів (вільних дірок `p` та іонізованих донорів `N_d^+`) повинна строго дорівнювати щільності негативних зарядів (вільних електронів `n` та іонізованих акцепторів `N_a^-`):

```
p(E_F) + N_d^+(E_F) - n(E_F) - N_a^-(E_F) = 0
```

Концентрації вільних носіїв у зоні провідності `n` та валентній зоні `p` у параболічному наближенні описуються виразами:

```
n(E_F) = N_c(T) · exp(-(E_c - E_F) / (k_B · T))
p(E_F) = N_v(T) · exp(-(E_F - E_v) / (k_B · T))
```

де `N_c(T)` та `N_v(T)` — ефективні густини станів у зоні провідності та валентній зоні, які залежать від температури як `T³ᐟ²`:

```
N_c(T) = 2 · ((2 · π · m_e* · k_B · T) / h²)³ᐟ²
N_v(T) = 2 · ((2 · π · m_h* · k_B · T) / h²)³ᐟ²
```

Для кремнію (Si) при кімнатній температурі `T = 300 K` стандартні значення ефективних густин станів становлять `N_c ≈ 2.86 × 10¹⁹ см⁻³` та `N_v ≈ 3.10 × 10¹⁹ см⁻³`.

### Часткова іонізація домішок та фактори виродження

У реальних напівпровідниках при зниженні температури не всі домішкові атоми є іонізованими (явище "виморожування" носіїв). Імовірність заповнення домішкового рівня описується статистикою Фермі з урахуванням фактора спинового виродження `g_d` та `g_a`:

```
N_d^+(E_F) = N_d / (1 + g_d · exp((E_F - E_d) / (k_B · T)))
N_a^-(E_F) = N_a / (1 + g_a · exp((E_a - E_F) / (k_B · T)))
```

Для кремнію (Si) донорний фактор виродження `g_d = 2` (через дві можливі орієнтації спіну електрона на донорному рівні), а акцепторний фактор `g_a = 4` (через виродження валентної зони у точці Гейзенберга).

### Залежність ширини забороненої зони від температури (Формула Варшні)

Ширина забороненої зони напівпровідника `E_g` зменшується при нагріванні через розширення кристалічної ґратки та електрон-фононну взаємодію. Емпіричний закон Варшні описує цю залежність:

```
E_g(T) = E_g(0) - (α · T²) / (T + β)
```

Для кремнію (Si): `E_g(0) = 1.166 еВ`, `α = 4.73 × 10⁻⁴ еВ/К`, `β = 636 K`, що при `T = 300 K` дає значення `E_g ≈ 1.12 еВ`.

---

## 2. Фізичний перебіг температурних режимів напівпровідника

Залежно від температури `T` та концентрації домішок напівпровідник проходить три основні фізичні режими, які солвер повинен коректно обчислювати:

1. **Режим виморожування носіїв (низкотемпературний, T < 100 K):** Теплової енергії `k_B · T` недостатньо для іонізації всіх донорів. Рівень Фермі розташований між донорним рівнем `E_d` та дном зони провідності `E_c`. Концентрація електронів експоненціально зростає з температурою: `n ∝ exp(-ΔE_d / (2 · k_B · T))`. Частка іонізованих донорів `N_d^+ / N_d` прямує до нуля при `T → 0 K`.
2. **Режим домішкової провідності (насичення, 100 K < T < 500 K):** Усі домішки повністю іонізовані (`N_d^+ ≈ N_d`), а власна концентрація носіїв `n_i` мізерно мала. Концентрація основних носіїв є константою (`n ≈ N_d`), а рівень Фермі плавно опускається до середини забороненої зони при нагріванні.
3. **Режим власної провідності (высокотемпературний, T > 600 K):** Власна концентрація носіїв перевищує концентрацію домішок (`n_i >> N_d`). Напівпровідник втрачає переваги допування, а рівень Фермі наближається до середини забороненої зони `E_i`.

---

## 3. Математичний алгоритм розв'язання та аналіз збіжності

Сформулюємо нелінійну функцію некомпенсованого заряду `f(E_F)`:

```
f(E_F) = p(E_F) + N_d^+(E_F) - n(E_F) - N_a^-(E_F)
```

Розглянемо математичні властивості цієї функції на інтервалі `E_F ∈ [E_v - 0.5, E_c + 0.5]`:
* При `E_F → E_v` концентрація дірок `p(E_F)` зростає експоненціально до величезних значень, роблячи `f(E_F) > 0`.
* При `E_F → E_c` концентрація електронів `n(E_F)` зростає експоненціально, роблячи `f(E_F) < 0`.
* Похідна `df / dE_F` є строго негативною на всьому проміжку:

```
df / dE_F = - (1 / (k_B · T)) · [ n(E_F) + p(E_F) + N_d^+(E_F) · (1 - N_d^+ / N_d) + N_a^-(E_F) · (1 - N_a^- / N_a) ] < 0
```

Строга монотонність функції `f(E_F)` гарантує існування **єдиного дійсного кореня** `f(E_F*) = 0`.

### Порівняння чисельних методів: Бісекція проти Ньютона — Рафсона

1. **Метод ділення навпіл (бісекція):** Забезпечує абсолютну стійкість та гарантовану збіжність незалежно від початкового наближення. Кількість ітерацій `N` для досягнення заданої точності `ε` по енергії обчислюється за формулою:

```
N = ⌈ log₂((E_max - E_min) / ε) ⌉
```

Для інтервалу шириною `2.0 еВ` та точності `ε = 10⁻⁸ еВ` необхідно зробити `N = ⌈ log₂(2.0 / 10⁻⁸) ⌉ = 28` ітерацій, що виконується мікропроцесором менше ніж за одну мікросекунду.

2. **Метод Ньютона — Рафсона:** Забезпечує квадратичну швидкість збіжності поблизу кореня (`E_F^{(k+1)} = E_F^{(k)} - f(E_F) / f'(E_F)`), проте вимагає обчислення похідної та може виходити за межі фізичного інтервалу при невдалому початковому кроці через експоненціальний вибух `f(E_F)`.

Тому найстійкішим інженерним вибором є метод бісекції з жорстко зафіксованою кількістю ітерацій (50–60 кроків), що дає точність біля `10⁻¹⁴ еВ` (границя точності подвійної точності `double`).

---

## 4. Програмна реалізація чисельного солвера

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи */
#define KB_EV 8.617333262145e-5      /* Стала Больцмана в еВ/К */
#define HBAR_EV_S 6.582119569e-16    /* Зведена стала Планка в еВ·с */
#define ME_KG 9.1093837015e-31       /* Маса спокою електрона в кг */

typedef struct {
    double temp_k;        /* Температура в Кельвінах */
    double n_d;           /* Концентрація донорів в см⁻³ */
    double e_d_relative;  /* Енергія донора відносно Ec (еВ, наприклад 0.045) */
    double n_a;           /* Концентрація акцепторів в см⁻³ */
    double e_a_relative;  /* Енергія акцептора відносно Ev (еВ, наприклад 0.045) */
    double m_e_eff;       /* Ефективна маса електрона (в одиницях m0) */
    double m_h_eff;       /* Ефективна маса дірки (в одиницях m0) */
} silicon_config_t;

typedef struct {
    double e_v;
    double e_c;
    double e_g;
    double e_f;
    double n_elec;
    double p_hole;
    double n_d_plus;
    double n_a_minus;
} solver_result_t;

/* Обчислення ширини забороненої зони Si за формулою Варшні */
static double calculate_bandgap_varshni(double temp_k) {
    double eg0 = 1.166; /* еВ */
    double alpha = 4.73e-4;
    double beta = 636.0;
    return eg0 - (alpha * temp_k * temp_k) / (temp_k + beta);
}

/* Обчислення ефективної густини станів Nc та Nv */
static void calculate_effective_dos(double temp_k, double me_eff, double mh_eff, double *nc, double *nv) {
    double t_factor = temp_k / 300.0;
    *nc = 2.86e19 * pow(me_eff / 1.08, 1.5) * pow(t_factor, 1.5);
    *nv = 3.10e19 * pow(mh_eff / 0.81, 1.5) * pow(t_factor, 1.5);
}

/* Функція некомпенсованого заряду: f(Ef) = p + Nd+ - n - Na- */
static double charge_residual(double e_f, double e_c, double e_v, double e_d, double e_a, 
                               double nc, double nv, const silicon_config_t *cfg) {
    double kt = KB_EV * cfg->temp_k;

    /* Обмеження аргументу експоненти для запобігання overflow */
    double arg_n = -(e_c - e_f) / kt;
    double arg_p = -(e_f - e_v) / kt;
    if (arg_n > 80.0) arg_n = 80.0;
    if (arg_p > 80.0) arg_p = 80.0;

    double n = nc * exp(arg_n);
    double p = nv * exp(arg_p);

    /* Іонізовані домішки */
    double arg_d = (e_f - e_d) / kt;
    double arg_a = (e_a - e_f) / kt;
    if (arg_d > 80.0) arg_d = 80.0;
    if (arg_a > 80.0) arg_a = 80.0;

    double n_d_plus = cfg->n_d / (1.0 + 2.0 * exp(arg_d));
    double n_a_minus = cfg->n_a / (1.0 + 4.0 * exp(arg_a));

    return (p + n_d_plus) - (n + n_a_minus);
}

/* Чисельний солвер методом бісекції */
int solve_fermi_level_c(const silicon_config_t *cfg, solver_result_t *res) {
    if (cfg->temp_k <= 0.0) return -1;

    res->e_v = 0.0;
    res->e_g = calculate_bandgap_varshni(cfg->temp_k);
    res->e_c = res->e_v + res->e_g;

    double e_d = res->e_c - cfg->e_d_relative;
    double e_a = res->e_v + cfg->e_a_relative;

    double nc = 0.0, nv = 0.0;
    calculate_effective_dos(cfg->temp_k, cfg->m_e_eff, cfg->m_h_eff, &nc, &nv);

    double e_low = res->e_v - 0.5;
    double e_high = res->e_c + 0.5;
    double e_mid = (e_low + e_high) / 2.0;

    /* Метод бісекції (60 ітерацій забезпечують граничну точність типу double) */
    for (int iter = 0; iter < 60; iter++) {
        e_mid = (e_low + e_high) / 2.0;
        double f_mid = charge_residual(e_mid, res->e_c, res->e_v, e_d, e_a, nc, nv, cfg);

        if (f_mid > 0.0) {
            e_low = e_mid;
        } else {
            e_high = e_mid;
        }
    }

    res->e_f = e_mid;
    double kt = KB_EV * cfg->temp_k;

    res->n_elec = nc * exp(-(res->e_c - res->e_f) / kt);
    res->p_hole = nv * exp(-(res->e_f - res->e_v) / kt);
    res->n_d_plus = cfg->n_d / (1.0 + 2.0 * exp((res->e_f - e_d) / kt));
    res->n_a_minus = cfg->n_a / (1.0 + 4.0 * exp((e_a - res->e_f) / kt));

    return 0;
}

int main(void) {
    silicon_config_t cfg_n = {
        .temp_k = 300.0,
        .n_d = 1.0e16,
        .e_d_relative = 0.045,
        .n_a = 0.0,
        .e_a_relative = 0.045,
        .m_e_eff = 1.08,
        .m_h_eff = 0.81
    };

    solver_result_t res;
    if (solve_fermi_level_c(&cfg_n, &res) == 0) {
        printf("--- Розрахунок Si n-типу (T = %.1f K, Nd = %.1e cm^-3) ---\n", cfg_n.temp_k, cfg_n.n_d);
        printf("Ширина забороненої зони Eg = %.4f еВ\n", res.e_g);
        printf("Рівень Фермі Ef = %.4f еВ (відносно Ev)\n", res.e_f);
        printf("Відстань Ec - Ef = %.4f еВ\n", res.e_c - res.e_f);
        printf("Концентрація електронів n = %.3e см^-3\n", res.n_elec);
        printf("Частка іонізованих донорів Nd+/Nd = %.1f%%\n", (res.n_d_plus / cfg_n.n_d) * 100.0);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string>
#include <algorithm>

namespace physics {

constexpr double kBoltzEv = 8.617333262145e-5; // еВ/К

struct SemiconductorConfig {
    double temp_k{300.0};
    double n_d{1.0e16};          // см⁻³
    double e_d_relative{0.045};  // еВ відносно Ec
    double n_a{0.0};             // см⁻³
    double e_a_relative{0.045};  // еВ відносно Ev
    double m_e_eff{1.08};
    double m_h_eff{0.81};
};

struct CalculationResult {
    double e_v_ev;
    double e_c_ev;
    double e_g_ev;
    double e_f_ev;
    double n_elec_cm3;
    double p_hole_cm3;
    double n_d_plus_cm3;
    double n_a_minus_cm3;
};

enum class SolverErrorCode {
    InvalidTemperature,
    InvalidDoping
};

class FermiLevelSolver {
public:
    [[nodiscard]] static double calculate_varshni_bandgap(double temp_k) noexcept {
        constexpr double eg0 = 1.166;
        constexpr double alpha = 4.73e-4;
        constexpr double beta = 636.0;
        return eg0 - (alpha * temp_k * temp_k) / (temp_k + beta);
    }

    [[nodiscard]] static std::expected<CalculationResult, SolverErrorCode> solve(
        const SemiconductorConfig& cfg, double tolerance_ev = 1.0e-8) noexcept
    {
        if (cfg.temp_k <= 0.0) {
            return std::unexpected(SolverErrorCode::InvalidTemperature);
        }
        if (cfg.n_d < 0.0 || cfg.n_a < 0.0) {
            return std::unexpected(SolverErrorCode::InvalidDoping);
        }

        const double e_v = 0.0;
        const double e_g = calculate_varshni_bandgap(cfg.temp_k);
        const double e_c = e_v + e_g;
        const double e_d = e_c - cfg.e_d_relative;
        const double e_a = e_v + cfg.e_a_relative;

        const double t_factor = cfg.temp_k / 300.0;
        const double nc = 2.86e19 * std::pow(cfg.m_e_eff / 1.08, 1.5) * std::pow(t_factor, 1.5);
        const double nv = 3.10e19 * std::pow(cfg.m_h_eff / 0.81, 1.5) * std::pow(t_factor, 1.5);
        const double kt = kBoltzEv * cfg.temp_k;

        auto residual = [&](double e_f) noexcept -> double {
            const double arg_n = std::clamp(-(e_c - e_f) / kt, -80.0, 80.0);
            const double arg_p = std::clamp(-(e_f - e_v) / kt, -80.0, 80.0);

            const double n = nc * std::exp(arg_n);
            const double p = nv * std::exp(arg_p);

            const double arg_d = std::clamp((e_f - e_d) / kt, -80.0, 80.0);
            const double arg_a = std::clamp((e_a - e_f) / kt, -80.0, 80.0);

            const double n_d_plus = cfg.n_d / (1.0 + 2.0 * std::exp(arg_d));
            const double n_a_minus = cfg.n_a / (1.0 + 4.0 * std::exp(arg_a));

            return (p + n_d_plus) - (n + n_a_minus);
        };

        double e_low = e_v - 0.5;
        double e_high = e_c + 0.5;
        double e_mid = (e_low + e_high) / 2.0;

        while ((e_high - e_low) > tolerance_ev) {
            e_mid = (e_low + e_high) / 2.0;
            if (residual(e_mid) > 0.0) {
                e_low = e_mid;
            } else {
                e_high = e_mid;
            }
        }

        const double n_final = nc * std::exp(-(e_c - e_mid) / kt);
        const double p_final = nv * std::exp(-(e_mid - e_v) / kt);
        const double nd_plus_final = cfg.n_d / (1.0 + 2.0 * std::exp((e_mid - e_d) / kt));
        const double na_minus_final = cfg.n_a / (1.0 + 4.0 * std::exp((e_a - e_mid) / kt));

        return CalculationResult{
            .e_v_ev = e_v,
            .e_c_ev = e_c,
            .e_g_ev = e_g,
            .e_f_ev = e_mid,
            .n_elec_cm3 = n_final,
            .p_hole_cm3 = p_final,
            .n_d_plus_cm3 = nd_plus_final,
            .n_a_minus_cm3 = na_minus_final
        };
    }
};

} // namespace physics

int main() {
    physics::SemiconductorConfig cfg_p{
        .temp_k = 300.0,
        .n_d = 0.0,
        .e_d_relative = 0.045,
        .n_a = 2.0e17, // p-тип Si, Na = 2e17 cm^-3
        .e_a_relative = 0.045
    };

    if (auto res = physics::FermiLevelSolver::solve(cfg_p)) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "--- Розрахунок Si p-типу (T = 300 K, Na = 2e17 cm^-3) ---\n";
        std::cout << "Ширина забороненої зони Eg = " << res->e_g_ev << " еВ\n";
        std::cout << "Рівень Фермі Ef = " << res->e_f_ev << " еВ (відносно Ev)\n";
        std::cout << "Відстань Ef - Ev = " << (res->e_f_ev - res->e_v_ev) << " еВ\n";
        std::cout << "Концентрація дірок p = " << std::scientific << res->p_hole_cm3 << " см^-3\n";
    }

    return 0;
}
```
:::

---

## 5. Обчислювальні пастки та крайові випадки

При чисельному моделюванні рівня Фермі у напівпровідниках виникає кілька критичних практичних пасток, які вимагають спеціальних інженерних запобіжників:

1. **Переповнення типів плаваючої коми (Floating-Point Overflow):**
   При низьких температурах (`T < 50 K`) значення `k_B · T` стає малим (`~ 0.001 еВ`). При обчисленні виразів `exp((E_c - E_F) / (k_B · T))` аргумент експоненти без запобіжника може перевищувати `+700`, що викликає переповнення типів плаваючої коми і генерацію значень `Inf` або `NaN`. Обов'язковим інженерним рішенням є затискання аргументів експоненти у безпечних межах (`[-80.0, +80.0]`), як це реалізовано за допомогою `std::clamp` у C++ коді.

2. **Нехтування неповним виснаженням домішок при низьких температурах:**
   Спрощена інженерна формула `n ≈ N_d` передбачає, що 100% донорів іонізовані. При `T = 77 K` (жидкий азот) у кремнії іонізується менше 10% донорів, а решта електронів заморожується на донорних рівнях. Використання повної статистичної формули `N_d^+ = N_d / (1 + 2 · exp(...))` є абсолютно необхідним для отримання фізично коректних результатів при низьких температурах.

3. **Вироджений напівпровідник та інтеграли Фермі — Дірака:**
   При надвисоких рівнях легування (`N_d > 3 × 10¹⁹ см⁻³`) рівень Фермі перетинає дно зони провідності (`E_F > E_c`). У цьому випадку наближення Максвелла — Больцмана `n = N_c · exp(...)` дає похибку в сотні відсотків. Професійний солвер при виявленні умови `(E_F - E_c) > -2 · k_B · T` повинен автоматично перемикатися з больцманівської експоненти на чисельну апроксимацію інтеграла Фермі — Дірака `F₁ᐟ₂(η)` (наприклад, за поліноміальною формулою Нікіфорова — Уварова чи за наближенням Блейкмора).
