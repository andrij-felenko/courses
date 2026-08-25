# ⚙️ Обчислення оптичної дисперсії та розширення імпульсів у середовищі

Практичний розрахунок заломлення світла у скляних призмах, розрахунок хроматичних аберацій складних лінзових систем та оцінка часового розширення лазерних імпульсів у оптичних світловодах вимагають систематичного обчислення показника заломлення `n(λ)`, його першої похідної `dn / dλ` та другої похідної `d²n / dλ²`. Для цього у сучасних обчислювальних алгоритмах геометрооптичного та хвильового моделювання застосовують формулу Зельмейєра з 6 каталожними коефіцієнтами конкретного скла або кристала.

У цьому практичному проекті розбирається алгоритмічна база розрахунку дисперсійних характеристик матеріалів, аналізуються чисельні методи диференціювання, розглядаються пастки точності плаваючої крапки та наводиться робоча реалізація мовами C, C++ та Python.

### 1. Математичні та алгоритмічні основи обчислення

#### Оцінка показника заломлення та чисельне диференціювання

Формула Зельмейєра виражає квадрат показника заломлення `n²(λ)` через суму трьох резонансних членів:

```
n²(λ) = 1 + (B₁ · λ²) / (λ² - C₁) + (B₂ · λ²) / (λ² - C₂) + (B₃ · λ²) / (λ² - C₃)
```

значення довжини хвилі `λ` передається у мікронах (`мкм`). Обчислення самого значення `n(λ)` зводиться до трьох операцій ділення та добування квадратного кореня `n = √(n²)`.

Для знаходження групового показника заломлення `n_g = n - λ · (dn / dλ)` необхідно обчислити першу похідну `dn / dλ`. Існує два шляхи знаходження похідної:

1. **Аналітичне диференціювання**: Шляхом взяття похідної від обох частин рівняння Зельмейєра:

```
2 · n · (dn / dλ) = ∑ [ 2 · B_i · λ · (λ² - C_i) - 2 · B_i · λ³ ] / (λ² - C_i)²
= ∑ [ -2 · B_i · C_i · λ ] / (λ² - C_i)²
```

Звідси аналітична похідна дорівнює:

```
dn / dλ = -(λ / n) · ∑ [ (B_i · C_i) / (λ² - C_i)² ]
```

2. **Чисельне диференціювання методом центральних різниць**:
Аналітична формула вимагає додаткових обчислювальних циклів. У чисельних розрахунках частіше застосовують метод центральних різниць із симетричним кроком `h`:

```
dn / dλ ≈ [ n(λ + h) - n(λ - h) ] / (2 · h)
```

Похибка схеми центральних різниць має другий порядок точності `O(h²)`. Оптимальний вибір кроку `h = 10⁻⁴ мкм` (тобто `0.1 нм`) забезпечує найвищу точність, збалансовану між похибкою округлення плаваючої крапки та похибкою апроксимації Тейлора.

#### Обчислення матеріальної дисперсії та розширення імпульсу

Параметр матеріальної хроматичної дисперсії `D` (вимірюється у `пс / (нм · км)`) виражається через другу похідну `d²n / dλ²`:

```
D = -(λ / c) · (d²n / dλ²)
```

Другу похідну чисельно обчислюють за 3-точковою центральною схемою:

```
d²n / dλ² ≈ [ n(λ + h) - 2 · n(λ) + n(λ - h) ] / h²
```

Часове розширення імпульсу `Δτ` на трасі довжиною `L` при спектральній ширині лазерного випромінювання `Δλ` становить `Δτ = |D| · Δλ · L`.

### 2. Архітектура оптичного обчислювального модуля

Програмний модуль оптичної дисперсії будується за принципом розділення зберігання каталогів матеріалів та математичних обчислювачів. Основний потік обчислення складається з п'яти послідовних етапів:

1. **Ініціалізація та валідація даних**: Завантаження паспорта матеріалу (наприклад, `N-BK7` або `Fused Silica`) та перевірка, що запрошувана довжина хвилі `λ` лежить у діапазоні прозорості `[λ_min, λ_max]`.
2. **Прямий розрахунок Зельмейєра**: Обчислення фазового показника заломлення `n(λ)` за формулою 6 коефіцієнтів.
3. **Чисельне диференціювання**: Обчислення похідних `dn / dλ` та `d²n / dλ²` за симетричною триточковою схемою центральних різниць.
4. **Розрахунок похідних фізичних величин**: Обчислення фазової швидкості `v_p = c / n`, групової швидкості `v_g = c / n_g`, числа Аббе `V_d` та параметра матеріальної дисперсії `D`.
5. **Моделювання хвильоводної траси**: Оцінка міжсимвольної інтерференції (ISI) та розширення пікосекундних світлових імпульсів у волоконній лінії зв'язку.

### 3. Алгоритм пошуку довжини хвилі нульової дисперсії (Метод Ньютона-Рафсона)

Важливим практичним завданням у проектуванні волоконно-оптичних ліній зв'язку є визначення точної довжини хвилі `λ₀`, на якій матеріальна дисперсія дорівнює нулю (`D(λ₀) = 0`). Оскільки параметр дисперсії proportional до другої похідної `d²n / dλ² = 0`, завдання зводиться до пошуку кореня нелінійного рівняння `f(λ) = d²n / dλ² = 0`.

Для цього застосовують ітераційний **метод Ньютона-Рафсона**:

```
λ_{k+1} = λ_k - f(λ_k) / f'(λ_k)
```

де похідна `f'(λ) = d³n / dλ³` обчислюється чисельно за 4-точковою схемою. Початкове наближення обирають у діапазоні `λ₀ = 1.30 мкм`. Ітераційний процес сходиться за 3–4 кроки з точністю до `10⁻⁶ мкм`, визначаючи довжину хвилі нульової дисперсії кварцового скла `λ₀ ≈ 1.273 мкм` (у чистому середовищі без урахування хвилеводного профілю).

### 4. Моделювання компенсації дисперсії у WDM-мережах

У сучасних магістральних мережах спектрального ущільнення (WDM) для компенсації накопиченого розширення імпульсів застосовують модулі компенсації дисперсії (Dispersion Compensation Modules, DCM). Алгоритм розрахунку компенсаційної лінії базується на умові нульової сумарної дисперсії траси:

```
D_total = D_1 · L_1 + D_DCF · L_DCF = 0
```

де `D_1` та `L_1` — параметр дисперсії та довжина основного волокна (наприклад, `SMF-28` із `D_1 = +17 пс / (нм · км)` на `1.55 мкм`), а `D_DCF` та `L_DCF` — параметри компенсаційного волокна з від'ємною дисперсією (`D_DCF = -100 пс / (нм · км)`).

Програма обчислює необхідну довжину компенсаційного світловода `L_DCF = -(D_1 · L_1) / D_DCF`, відновлюючи початкову тривалість імпульсу та усуваючи міжсимвольні спотворення.

### 5. Реалізація розрахунку дисперсії мовами C, C++ та Python

Усі наведені нижче приклади є незалежними, ідіоматичними реалізаціями одного алгоритму для відповідної мови та платформи.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define C_VACUUM 299792458.0 /* Швидкість світла у вакуумі (м/с) */

/* Структура каталожного скла за Зельмейєром */
typedef struct {
    const char* name;
    double B1, B2, B3; /* Коефіцієнти B_i */
    double C1, C2, C3; /* Резонансні квадрати C_i (мкм²) */
} SellmeierGlassC;

/* Обчислення показника заломлення n(lambda) */
double glass_n(const SellmeierGlassC* g, double lambda_um) {
    double l2 = lambda_um * lambda_um;
    double n2 = 1.0 + (g->B1 * l2) / (l2 - g->C1)
                    + (g->B2 * l2) / (l2 - g->C2)
                    + (g->B3 * l2) / (l2 - g->C3);
    return sqrt(n2);
}

/* Перша похідна dn/dlambda за методом центральних різниць */
double glass_dn_dlambda(const SellmeierGlassC* g, double lambda_um) {
    double h = 0.0001; /* крок 0.1 нм */
    double n_plus  = glass_n(g, lambda_um + h);
    double n_minus = glass_n(g, lambda_um - h);
    return (n_plus - n_minus) / (2.0 * h);
}

/* Друга похідна d^2n / dlambda^2 */
double glass_d2n_dlambda2(const SellmeierGlassC* g, double lambda_um) {
    double h = 0.0001;
    double n_plus  = glass_n(g, lambda_um + h);
    double n_zero  = glass_n(g, lambda_um);
    double n_minus = glass_n(g, lambda_um - h);
    return (n_plus - 2.0 * n_zero + n_minus) / (h * h);
}

/* Обчислення групового показника n_g */
double glass_group_index(const SellmeierGlassC* g, double lambda_um) {
    double n = glass_n(g, lambda_um);
    double dn_dl = glass_dn_dlambda(g, lambda_um);
    return n - lambda_um * dn_dl;
}

/* Обчислення числа Аббе V_d = (n_d - 1) / (n_F - n_C) */
double glass_abbe_number(const SellmeierGlassC* g) {
    double n_d = glass_n(g, 0.587562); /* 587.56 нм (гелій d) */
    double n_F = glass_n(g, 0.486133); /* 486.13 нм (водень F) */
    double n_C = glass_n(g, 0.656273); /* 656.27 нм (водень C) */
    return (n_d - 1.0) / (n_F - n_C);
}

/* Обчислення матеріальної дисперсії D (пс / (нм * км)) */
double glass_material_dispersion(const SellmeierGlassC* g, double lambda_um) {
    double d2n = glass_d2n_dlambda2(g, lambda_um);
    double lambda_m = lambda_um * 1e-6;
    double d2n_m2 = d2n * 1e12;
    double D_s_m2 = -(lambda_m / C_VACUUM) * d2n_m2;
    return D_s_m2 * 1e6;
}

int main(void) {
    SellmeierGlassC bk7 = {
        "N-BK7",
        1.03961212, 0.231792344, 1.01046945,
        0.00600069867, 0.0200179144, 103.560653
    };

    double lambda = 0.587562; /* 587.56 нм */
    double n = glass_n(&bk7, lambda);
    double dn_dl = glass_dn_dlambda(&bk7, lambda);
    double n_g = glass_group_index(&bk7, lambda);
    double v_p = C_VACUUM / n;
    double v_g = C_VACUUM / n_g;
    double v_d = glass_abbe_number(&bk7);
    double D_mat = glass_material_dispersion(&bk7, lambda);

    printf("--- Дисперсійний паспорт матеріалу %s ---\n", bk7.name);
    printf("Довжина хвилі: %.6f мкм\n", lambda);
    printf("Показник заломлення n: %.6f\n", n);
    printf("Перша похідна dn/dlambda: %.6f 1/мкм\n", dn_dl);
    printf("Груповий показник n_g: %.6f\n", n_g);
    printf("Фазова швидкість v_p: %.2f км/с\n", v_p / 1000.0);
    printf("Групова швидкість v_g: %.2f км/с\n", v_g / 1000.0);
    printf("Число Аббе V_d: %.2f\n", v_d);
    printf("Матеріальна дисперсія D: %.2f пс/(нм*км)\n", D_mat);

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <array>
#include <vector>

constexpr double C_VACUUM = 299792458.0; // Швидкість світла у вакуумі (м/с)

struct GlassCoefficients {
    std::array<double, 3> B{};
    std::array<double, 3> C{};
};

class SellmeierSolver {
private:
    std::string m_name;
    GlassCoefficients m_coeffs;

public:
    SellmeierSolver(std::string name, GlassCoefficients coeffs)
        : m_name(std::move(name)), m_coeffs(coeffs) {}

    [[nodiscard]] std::string_view name() const noexcept { return m_name; }

    // Показник заломлення n(lambda)
    [[nodiscard]] double n(double lambda_um) const noexcept {
        const double l2 = lambda_um * lambda_um;
        const double n2 = 1.0 + (m_coeffs.B[0] * l2) / (l2 - m_coeffs.C[0])
                              + (m_coeffs.B[1] * l2) / (l2 - m_coeffs.C[1])
                              + (m_coeffs.B[2] * l2) / (l2 - m_coeffs.C[2]);
        return std::sqrt(n2);
    }

    // Перша похідна dn / dlambda
    [[nodiscard]] double dn_dlambda(double lambda_um, double h = 1e-4) const noexcept {
        return (n(lambda_um + h) - n(lambda_um - h)) / (2.0 * h);
    }

    // Друга похідна d^2n / dlambda^2
    [[nodiscard]] double d2n_dlambda2(double lambda_um, double h = 1e-4) const noexcept {
        return (n(lambda_um + h) - 2.0 * n(lambda_um) + n(lambda_um - h)) / (h * h);
    }

    // Груповий показник заломлення n_g = n - lambda * (dn/dlambda)
    [[nodiscard]] double group_index(double lambda_um) const noexcept {
        return n(lambda_um) - lambda_um * dn_dlambda(lambda_um);
    }

    // Число Аббе V_d
    [[nodiscard]] double abbe_number() const noexcept {
        const double n_d = n(0.587562);
        const double n_F = n(0.486133);
        const double n_C = n(0.656273);
        return (n_d - 1.0) / (n_F - n_C);
    }

    // Матеріальна дисперсія D у пс / (нм * км)
    [[nodiscard]] double material_dispersion(double lambda_um) const noexcept {
        const double d2n = d2n_dlambda2(lambda_um);
        const double lambda_m = lambda_um * 1e-6;
        const double d2n_m2 = d2n * 1e12;
        const double D_s_m2 = -(lambda_m / C_VACUUM) * d2n_m2;
        return D_s_m2 * 1e6;
    }

    // Часове розширення імпульсу delta_t (пікосекунди)
    [[nodiscard]] double pulse_broadening_ps(double lambda_um, double delta_lambda_nm, double length_km) const noexcept {
        return std::abs(material_dispersion(lambda_um)) * delta_lambda_nm * length_km;
    }
};

int main() {
    const SellmeierSolver fused_silica(
        "Fused Silica (Кварцеве скло)",
        GlassCoefficients{
            {0.6961663, 0.4079426, 0.8974794},
            {0.004679148, 0.01351206, 97.93400254}
        }
    );

    const std::vector<double> wavelengths_um = {0.85, 1.31, 1.55}; // стандартні телеком-вікна
    const double delta_lambda_nm = 1.5; // ширина лазера 1.5 нм
    const double fiber_length_km = 20.0; // лінія 20 км

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Оптичний аналіз середовища: " << fused_silica.name() << "\n";
    std::cout << "Число Аббе V_d: " << fused_silica.abbe_number() << "\n\n";

    std::cout << "Довжина хвилі |   n(lambda)   |     n_g       | D [пс/(нм*км)] | Розширення (20 км)\n";
    std::cout << "--------------|---------------|---------------|----------------|-------------------\n";

    for (const double wave : wavelengths_um) {
        const double n_val = fused_silica.n(wave);
        const double ng_val = fused_silica.group_index(wave);
        const double D_val = fused_silica.material_dispersion(wave);
        const double dt_ps = fused_silica.pulse_broadening_ps(wave, delta_lambda_nm, fiber_length_km);

        std::cout << std::setw(9) << wave << " мкм | "
                  << std::setw(13) << n_val << " | "
                  << std::setw(13) << ng_val << " | "
                  << std::setw(14) << D_val << " | "
                  << std::setw(12) << dt_ps << " пс\n";
    }

    return 0;
}
```
```py
import math

class SellmeierSolver:
    def __init__(self, name: str, B: list[float], C: list[float]):
        self.name = name
        self.B = B
        self.C = C
        self.c_vacuum = 299792458.0

    def n(self, lambda_um: float) -> float:
        l2 = lambda_um ** 2
        n2 = 1.0 + sum((b * l2) / (l2 - c) for b, c in zip(self.B, self.C))
        return math.sqrt(n2)

    def dn_dlambda(self, lambda_um: float, h: float = 1e-4) -> float:
        return (self.n(lambda_um + h) - self.n(lambda_um - h)) / (2.0 * h)

    def d2n_dlambda2(self, lambda_um: float, h: float = 1e-4) -> float:
        return (self.n(lambda_um + h) - 2.0 * self.n(lambda_um) + self.n(lambda_um - h)) / (h * h)

    def group_index(self, lambda_um: float) -> float:
        return self.n(lambda_um) - lambda_um * self.dn_dlambda(lambda_um)

    def abbe_number(self) -> float:
        n_d = self.n(0.587562)
        n_F = self.n(0.486133)
        n_C = self.n(0.656273)
        return (n_d - 1.0) / (n_F - n_C)

    def material_dispersion(self, lambda_um: float) -> float:
        d2n = self.d2n_dlambda2(lambda_um)
        lambda_m = lambda_um * 1e-6
        d2n_m2 = d2n * 1e12
        D_val = -(lambda_m / self.c_vacuum) * d2n_m2
        return D_val * 1e6

glasses = [
    SellmeierSolver("N-BK7 (Крон)", [1.03961212, 0.231792344, 1.01046945], [0.00600069867, 0.0200179144, 103.560653]),
    SellmeierSolver("N-SF11 (Флінт)", [1.73759695, 0.313747346, 1.89878101], [0.013188707, 0.0623068142, 155.23629]),
    SellmeierSolver("Fused Silica", [0.6961663, 0.4079426, 0.8974794], [0.004679148, 0.01351206, 97.93400254])
]

print(f"{'Скло':<20} | {'n (d-лінія)':<12} | {'n_g (d-лінія)':<12} | {'V_d (Аббе)':<10} | {'D (1.55 мкм)':<15}")
print("-" * 75)
for g in glasses:
    n_d = g.n(0.587562)
    ng_d = g.group_index(0.587562)
    vd = g.abbe_number()
    D_155 = g.material_dispersion(1.55)
    print(f"{g.name:<20} | {n_d:<12.6f} | {ng_d:<12.6f} | {vd:<10.2f} | {D_155:<15.2f}")
```
:::

### 6. Типові пастки реалізації та аналіз похибок

Під час програмування оптичних розрахунків дисперсії розробники часто припускаються трьох типових помилок:

1. **Неузгодженість розмірностей довжини хвилі**: У канонічному рівнянні Зельмейєра коефіцієнти `C_1, C_2, C_3` задано у квадратних мікрометрах (`мкм²`). Якщо у програму передається значення довжини хвилі у нанометрах (`нм`, наприклад `587.56`), знаменник `(λ² - C_i)` стає катастрофічно величезним, і розрахований показник заломлення вироджується в `n = 1.0`. Перед передачею у формулу довжину хвилі необхідно переводити у мікрометри (`λ_um = λ_nm / 1000.0`).
2. **Втрата точності при чисельному диференціюванні**: При обчисленні другої похідної `d²n / dλ²` через чисельні різниці знаменник містить `h² = 10⁻⁸`. При використання змінних типу `float` (32 біти, 7 десяткових знаків точності) відбувається катастрофічна втрата розрядів при відніманні близьких чисел `(n(λ+h) - 2n(λ) + n(λ-h))`. Усі обчислення коефіцієнтів дисперсії обов'язково здійснювати з подвійною точністю `double` (64 біти) або `long double`.
3. **Область сингулярності поблизу УФ-краю**: При моделюванні проходження світла в глибокому ультрафіолеті (`λ < 0.2 мкм`) довжина хвилі може наблизитися до першого коефіцієнта `C₁ ≈ 0.006 мкм²` (що відповідає `λ_резонанс = √C₁ ≈ 0.077 мкм`). У цій точці знаменник прямує до нуля, викликаючи виключення ділення на нуль або генерацію значення `NaN`. Програма повинна містити попередню перевірку діапазону прозорості `[lambda_min, lambda_max]`.
