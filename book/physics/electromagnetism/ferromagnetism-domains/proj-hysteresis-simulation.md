# 💻 Симуляція кривої намагнічування та петлі гістерезису

Цей практичний проект присвячено чисельному моделюванню початкової кривої намагнічування та необоротної петлі гістерезису у феромагнетиках на основі феноменологічної фізичної моделі Джайлса — Атертона (Jiles — Atherton hysteresis model). У статті наведено детальний фізичний аналіз усіх параметрів моделі, рівняння термодинамічної дисипації, алгоритм чисельного інтегрування Рунге — Кутти 4-го порядку та компілятивний програмний код мовами C та C++.

## Фізичні основи моделі Джайлса — Атертона

Модель Джайлса — Атертона є однією з найпоширеніших у сучасній комп'ютерній інженерії та моделюванні електромагнітних пристроїв (SPICE, ANSYS, COMSOL). Вона базується на термодинамічному описі руху доменних стінок у неідеальному кристалі з дефектами. Загальна макроскопічна намагніченість феромагнетика `M` розділяється на дві фізично різні компоненти: оборотну намагніченість `M_rev` (пружне вигинання доменних стінок під дією слабких полів) та необоротну намагніченість `M_irr` (стрибкоподібне подолання дефектів, дислокацій та сторонніх включень):

```
M = M_irr + M_rev                                 [сумарна намагніченість]
```

### 1. Безгістерезисна (безтертєва) намагніченість `M_an`
Увага приділяється ідеальній безгістерезисній кривій `M_an(H_e)`, яка відповідала б стану матеріалу за повної відсутності дефектів кристалічної ґратки. Вона описується класичною модифікованою функцією Ланжевена від ефективного магнітного поля `H_e = H + α · M`:

```
M_an(H_e) = M_s · [ coth( H_e / a ) - ( a / H_e ) ]  [функція Ланжевена]
```

де `M_s` — намагніченість насичення матеріалу (А/м), `a` — параметр термічного поля (А/м), який виражає ефективну температуру спінової системи, а `α` — безрозмірний параметр внутрішньодоменного молекулярного поля Вейса, який описує позитивний зворотний зв'язок між сусідніми доменами.

### 2. Необоротна компонента `M_irr` та процес пиннингу
Зміна необоротної намагніченості під дією зміни зовнішнього магнітного поля `dH` підпорядковується диференціальному рівнянню пиннингу (закріплення) доменних стінок на дефектах кристалічної ґратки:

```
dM_irr / dH = ( M_an - M_irr ) / ( δ · k - α · ( M_an - M_irr ) )  [необоротний зсув стінок]
```

де `k` — параметр пиннингу, який прямо пропорційний середній густині дефектів у кристалі та визначає коерцитивну силу `H_c`. Змінна `δ = sgn(dH)` виражає напрямок зміни зовнішнього поля (`+1` при зростанні поля, `-1` при зменшенні). Це гарантує, що робота, затрачена на подолання пиннингу дефектів, завжди є додатною величинами, перетворюючись на тепловий рух атомів.

### 3. Оборотна компонента `M_rev` та підсумкове диференціальне рівняння
Оборотна частина вигинання стінок пропорційна різниці між безгістерезисною та необоротною намагніченістю з коефіцієнтом пружності `c` (`0 < c < 1`):

```
M_rev = c · ( M_an - M_irr )                      [пружне вигинання стінок]
```

Повне диференціальне рівняння зв'язку `dM/dH` для чисельного розрахунку записується у формі, зручній для інтегрування:

```
dM / dH = ( 1 / (1 + c) ) · ( dM_irr / dH ) + ( c / (1 + c) ) · ( dM_an / dH )
```

Обчислення площі замкненої петлі гістерезису `Q = ∮ H dB` дає густину втрат енергії на перемагнічування за один цикл (вимірюється в Дж/м³).

## Фізичні параметри моделі та їхній вплив на петлю

Для практичного використання моделі Джайлса — Атертона необхідно розуміти фізичний зміст кожного з п'яти основних параметрів матеріалу:

1. `M_s` **(Намагніченість насичення, А/м):** Визначає верхню горизонтальну асимптоту петлі гістерезису. Залежить строго від хімічного складу матеріалу та температури. Для чистого заліза `M_s ≈ 1.75·10⁶` А/м (`B_s ≈ 2.15` Тл).
2. `a` **(Константа термічного поля, А/м):** Визначає нахил та вигин початкової безгістерезисної кривої. Чим менше `a`, тим стрімкіше вихідне намагнічування у слабких полях.
3. `α` **(Параметр поля Вейса, безрозмірний):** Характеризує кулонівську обмінну взаємодію між сусідніми доменами. Збільшення `α` робить петлю більш вертикальною та прямокутною.
4. `k` **(Параметр пиннингу дефектів, А/м):** Виражає енергію заклинювання доменної стінки на дефектах. Величина `k` прямо пропорційна коерцитивній силі матеріалу `H_c`. У магнітом'яких сталях `k < 100` А/м, а у твердих магнітах `k > 10⁵` А/м.
5. `c` **(Коефіцієнт оборотності, безрозмірний):** Частка оборотного вигинання доменних стінок відносно загального зміщення. Значення `c = 0` відповідає чисто необоротній петлі з гострими кутами, а `c = 1` — повністю оборотній кривій без гістерезису.

## Алгоритм чисельного інтегрування та стабільність

Диференціальне рівняння Джайлса — Атертона `dM/dH` відрізняється високою нелінійністю поблизу коерцитивної сили `H_c`. Прості чисельні методи (наприклад, метод Ейлера) дають значну похибку та накопичують чисельну нестабільність, що спричиняє розриви кривої та нефізичне від'ємне значення дисипації.

У наведеному програмному модулі реалізовано класичний метод Рунге — Кутти 4-го порядку (RK4) з автоматичною перевіркою фізичного знака приросту необоротної намагніченості. Якщо на черговому кроці розрахунку величина `dM_irr/dH` змінює знак проти напрямку поля `dH`, алгоритм примусово обнуляє необоротний приріст, оскільки затягування стінки назад без зміни напрямку поля суперечить другому закону термодинаміки.

Окрім моделювання форми петлі `M(H)` та `B(H)`, програмний модуль автоматично розраховує повні втрати енергії за цикл перемагнічування шляхом чисельного інтегрування методом трапецій: `Q = ∑ [ H_avg · (B_i - B_{i-1}) ]`.

## Програмна реалізація симулятора

У вкладках `:::tabs` нижче наведено повну реалізацію чисельного моделювання гістерезису. Модуль розраховує початкову криву намагнічування, формує повну замкнену петлю `M(H)` при гармонійній зміні зовнішнього поля та обчислює втрати енергії методом трапецій.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Параметри моделі Джайлса - Атертона для трансформаторної сталі */
typedef struct {
    double Ms;   /* Намагніченість насичення (А/м) */
    double a;    /* Константа поля (А/м) */
    double alpha;/* Параметр міждоменного поля */
    double k;    /* Параметр пиннингу (коерцитивна сила) */
    double c;    /* Коефіцієнт оборотного вигинання */
} ja_params_t;

/* Модифікована функція Ланжевена L(x) = coth(x) - 1/x */
static double langevin(double x) {
    if (fabs(x) < 1e-4) {
        return x / 3.0 - (x * x * x) / 45.0; /* Розклад Тейлора при x -> 0 */
    }
    return (1.0 / tanh(x)) - (1.0 / x);
}

/* Похідна функції Ланжевена dL/dx = 1 - coth^2(x) + 1/x^2 */
static double langevin_der(double x) {
    if (fabs(x) < 1e-4) {
        return 1.0 / 3.0 - (x * x) / 15.0;
    }
    double ct = 1.0 / tanh(x);
    return 1.0 - ct * ct + 1.0 / (x * x);
}

/* Обчислення безгістерезисної намагніченості M_an */
static double calc_Man(double H, double M, const ja_params_t* p) {
    double He = H + p->alpha * M;
    if (fabs(He) < 1e-9) return 0.0;
    return p->Ms * langevin(He / p->a);
}

/* Права частина диференціального рівняння dM/dH */
static double dM_dH(double H, double M, double dir, const ja_params_t* p) {
    double Man = calc_Man(H, M, p);
    double He = H + p->alpha * M;
    double dMan_dHe = (fabs(He) < 1e-9) ? (p->Ms / (3.0 * p->a)) 
                                        : (p->Ms / p->a) * langevin_der(He / p->a);

    double delta = (dir >= 0.0) ? 1.0 : -1.0;
    double den = delta * p->k - p->alpha * (Man - M);

    if (fabs(den) < 1e-9) den = 1e-9;

    double dMirr_dH = (Man - M) / den;

    /* Захист від від'ємного нефізичного приросту необоротної намагніченості */
    if ((dir > 0.0 && dMirr_dH < 0.0) || (dir < 0.0 && dMirr_dH > 0.0)) {
        dMirr_dH = 0.0;
    }

    double dM_dH_val = (dMirr_dH + p->c * dMan_dHe) / (1.0 + p->c * (1.0 - p->alpha * dMan_dHe));
    return dM_dH_val;
}

/* Метод Рунге - Кутти 4-го порядку для кроку по H */
static double rk4_step(double H, double M, double dH, const ja_params_t* p) {
    double dir = (dH >= 0.0) ? 1.0 : -1.0;
    double k1 = dM_dH(H, M, dir, p);
    double k2 = dM_dH(H + 0.5 * dH, M + 0.5 * dH * k1, dir, p);
    double k3 = dM_dH(H + 0.5 * dH, M + 0.5 * dH * k2, dir, p);
    double k4 = dM_dH(H + dH, M + dH * k3, dir, p);

    return M + (dH / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
}

int main(void) {
    ja_params_t fe = {
        .Ms = 1.6e6,
        .a = 800.0,
        .alpha = 1.1e-3,
        .k = 500.0,
        .c = 0.15
    };

    int steps = 1000;
    double H_max = 3000.0; /* Максимальне зовнішнє поле (А/м) */
    double M = 0.0;
    double H = 0.0;
    double mu0 = 4.0 * M_PI * 1e-7;

    double loss_Q = 0.0; /* Площа петлі ∮ H dB */
    double M_prev = 0.0;
    double H_prev = 0.0;

    printf("# H(A/m)\tM(A/m)\tB(T)\n");

    /* Повний цикл перемагнічування 0 -> +Hmax -> -Hmax -> +Hmax */
    for (int cycle = 0; cycle < 2; ++cycle) {
        /* Вверх 0 -> Hmax */
        double dH = H_max / steps;
        for (int i = 0; i < steps; ++i) {
            M = rk4_step(H, M, dH, &fe);
            H += dH;
            double B = mu0 * (H + M);
            if (cycle == 1) {
                double dB = B - mu0 * (H_prev + M_prev);
                loss_Q += H * dB;
            }
            H_prev = H; M_prev = M;
        }

        /* Вниз Hmax -> -Hmax */
        dH = -2.0 * H_max / (2 * steps);
        for (int i = 0; i < 2 * steps; ++i) {
            M = rk4_step(H, M, dH, &fe);
            H += dH;
            double B = mu0 * (H + M);
            if (cycle == 1) {
                double dB = B - mu0 * (H_prev + M_prev);
                loss_Q += H * dB;
            }
            H_prev = H; M_prev = M;
        }

        /* Назад -Hmax -> +Hmax */
        dH = 2.0 * H_max / (2 * steps);
        for (int i = 0; i < 2 * steps; ++i) {
            M = rk4_step(H, M, dH, &fe);
            H += dH;
            double B = mu0 * (H + M);
            if (cycle == 1) {
                double dB = B - mu0 * (H_prev + M_prev);
                loss_Q += H * dB;
            }
            H_prev = H; M_prev = M;
            if (cycle == 1 && i % 40 == 0) {
                printf("%.2f\t%.2f\t%.4f\n", H, M, B);
            }
        }
    }

    printf("# Розраховані втрати на гістерезис Q = ∮ H dB: %.2f Дж/м3\n", fabs(loss_Q));
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <expected>
#include <span >

namespace physics {

struct JilesAthertonParams {
    double Ms{1.6e6};    // Намагніченість насичення (А/м)
    double a{800.0};     // Константа термічного поля (А/м)
    double alpha{1.1e-3};// Поле Вейса
    double k{500.0};     // Пиннинг дефектів
    double c{0.15};      // Коефіцієнт оборотності
};

struct HysteresisPoint {
    double H_field;
    double M_magnetization;
    double B_induction;
};

class HysteresisSimulator {
public:
    explicit HysteresisSimulator(JilesAthertonParams params) noexcept 
        : p_(params) {}

    [[nodiscard]] double langevin(double x) const noexcept {
        if (std::abs(x) < 1e-4) {
            return x / 3.0 - (x * x * x) / 45.0;
        }
        return (1.0 / std::tanh(x)) - (1.0 / x);
    }

    [[nodiscard]] double langevinDerivative(double x) const noexcept {
        if (std::abs(x) < 1e-4) {
            return 1.0 / 3.0 - (x * x) / 15.0;
        }
        const double ct = 1.0 / std::tanh(x);
        return 1.0 - ct * ct + 1.0 / (x * x);
    }

    [[nodiscard]] double computeMan(double H, double M) const noexcept {
        const double He = H + p_.alpha * M;
        if (std::abs(He) < 1e-9) return 0.0;
        return p_.Ms * langevin(He / p_.a);
    }

    [[nodiscard]] double computeDerivative(double H, double M, double dir) const noexcept {
        const double Man = computeMan(H, M);
        const double He = H + p_.alpha * M;
        const double dMan_dHe = (std::abs(He) < 1e-9) 
            ? (p_.Ms / (3.0 * p_.a)) 
            : (p_.Ms / p_.a) * langevinDerivative(He / p_.a);

        const double delta = (dir >= 0.0) ? 1.0 : -1.0;
        double den = delta * p_.k - p_.alpha * (Man - M);
        if (std::abs(den) < 1e-9) den = 1e-9;

        double dMirr_dH = (Man - M) / den;
        if ((dir > 0.0 && dMirr_dH < 0.0) || (dir < 0.0 && dMirr_dH > 0.0)) {
            dMirr_dH = 0.0;
        }

        return (dMirr_dH + p_.c * dMan_dHe) / (1.0 + p_.c * (1.0 - p_.alpha * dMan_dHe));
    }

    [[nodiscard]] double rk4Step(double H, double M, double dH) const noexcept {
        const double dir = (dH >= 0.0) ? 1.0 : -1.0;
        const double k1 = computeDerivative(H, M, dir);
        const double k2 = computeDerivative(H + 0.5 * dH, M + 0.5 * dH * k1, dir);
        const double k3 = computeDerivative(H + 0.5 * dH, M + 0.5 * dH * k2, dir);
        const double k4 = computeDerivative(H + dH, M + dH * k3, dir);

        return M + (dH / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    }

    [[nodiscard]] std::vector<HysteresisPoint> generateLoop(double H_max, std::size_t steps) const {
        std::vector<HysteresisPoint> points;
        points.reserve(steps * 4);

        double H = 0.0;
        double M = 0.0;
        constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;

        // Попередній вихід на насичення
        const double dH_init = H_max / static_cast<double>(steps);
        for (std::size_t i = 0; i < steps; ++i) {
            M = rk4Step(H, M, dH_init);
            H += dH_init;
        }

        // Основний замкнений цикл: +Hmax -> -Hmax -> +Hmax
        const double dH_down = -2.0 * H_max / static_cast<double>(steps * 2);
        for (std::size_t i = 0; i < steps * 2; ++i) {
            M = rk4Step(H, M, dH_down);
            H += dH_down;
            points.push_back({.H_field = H, .M_magnetization = M, .B_induction = mu0 * (H + M)});
        }

        const double dH_up = 2.0 * H_max / static_cast<double>(steps * 2);
        for (std::size_t i = 0; i < steps * 2; ++i) {
            M = rk4Step(H, M, dH_up);
            H += dH_up;
            points.push_back({.H_field = H, .M_magnetization = M, .B_induction = mu0 * (H + M)});
        }

        return points;
    }

    [[nodiscard]] static double calculateLosses(std::span<const HysteresisPoint> loop) noexcept {
        double area = 0.0;
        for (std::size_t i = 1; i < loop.size(); ++i) {
            const double dB = loop[i].B_induction - loop[i - 1].B_induction;
            const double H_avg = 0.5 * (loop[i].H_field + loop[i - 1].H_field);
            area += H_avg * dB;
        }
        return std::abs(area);
    }

private:
    JilesAthertonParams p_;
};

} // namespace physics
```
:::

## Аналіз обчислювальних результатів

Симуляція дозволяє точно оцінити вплив кожного параметра матеріалу на його інженерні характеристики:

1. **Контроль коерцитивної сили:** Збільшення параметра пиннингу `k` призводить до розширення петлі по осі `H` та збільшення коерцитивної сили `H_c ≈ k`.
2. **Контроль зашкоджень на перемагнічування:** Втрати енергії за один цикл `Q` обчислюються методом чисельного інтегрування трапецій `∫ H dB`. Для м'якої трансформаторної сталі `Q ≈ 150...300` Дж/м³, тоді як для твердого матеріалу магніту `Q > 50000` Дж/м³.
3. **Чисельна стабільність:** Використання 4-го порядку Рунге — Кутти забезпечує стабільність розв'язку диференціального рівняння Джайлса — Атертона без виникнення чисельної осциляції на ділянках високої крутизни поблизу `H_c`.
