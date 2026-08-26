# ⚙️ Розрахунок річної генерації вітроустановки за розподілом Вейбулла

Оцінка енергетичного потенціалу вітрової електроустановки на основі лише середньої арифметичної швидкості вітру призводить до грубих інженерних прорахунків: через кубічну залежність потужності від швидкості (`P ~ v³`) вітер, що дме зі швидкістю 8 м/с половину часу, приносить у чотири рази більше енергії, ніж постійний вітер 4 м/с за той самий період, хоча їхня середня арифметична швидкість однакова. Для точного інженерного прогнозу річного виробітку енергії (AEP, *Annual Energy Production*) застосовують статистичний розподіл Вейбулла, який чисельно згортають із паспортною кривою потужності конкретної вітроустановки.

### Фізико-математична модель та статистика вітру

Ймовірність появи швидкості вітру `v` (у нескінченно малому діапазоні від `v` до `v + dv`) описується функцією густини ймовірності двопараметричного розподілу Вейбулла:

```
f(v; k, c) = (k / c) · (v / c)^(k - 1) · exp[ −(v / c)^k ]
```

Фізичний зміст параметрів:
- **Параметр форми `k`** (*shape parameter*, безрозмірний): характеризує ступінь мінливості та ширину спектра швидкостей вітру. Для більшості сухопутних рівнинних регіонів помірного клімату значення лежить у межах `k ≈ 1.8–2.2`. При `k = 2.0` розподіл Вейбулла перетворюється на класичний розподіл Релея. Низькі значення `k ≈ 1.3–1.6` свідчать про високу турбулентність та різку поривчастість вітру з частими періодами повного штилю, тоді як високі значення `k ≈ 2.5–3.2` притаманні морським узбережжям та пасатним зонам зі стабільним вітровим напором.
- **Параметр масштабу `c`** (*scale parameter*, м/с): пропорційний середньорічній швидкості вітру. Зв'язок між параметром масштабу `c` та середньою швидкістю `v_mean` виражається через значення гамма-функції Ейлера:

```
v_mean = c · Γ(1 + 1/k)
```

При типовому значенні `k = 2.0` маємо `Γ(1.5) = ½ · √π ≈ 0.8862`, тобто `v_mean ≈ 0.886 · c`.

- **Густина повітря `ρ`**: кінетична енергія прямо пропорційна масі повітря. Стандартна густина `ρ₀ = 1.225 кг/м³` задається на рівні моря при температурі +15 °C і тиску 101.3 кПа. При підвищенні висоти установки над рівнем моря або в спекотний літній період густина повітря знижується за барометричною формулою, що пропорційно зменшує вихідну потужність вітроротора:

```
ρ(h, T) = [p₀ · exp(−g·M·h / (R_gas·T))] / [R_spec · T]
```

### Кусково-неперервна модель кривої потужності P(v)

Крива електричної потужності `P(v)` реальної вітроустановки не є гладкою аналітичною функцією на всьому інтервалі швидкостей. Вона ділиться на чотири характерні зони з розривами похідної на межах:

```
1. Зона спокою (v < v_ci):
   P(v) = 0

2. Зона кубічного зростання MPPT (v_ci ≤ v < v_rated):
   P(v) = ½ · ρ · A · v³ · Cp,max · η_мех · η_ген

3. Зона номінальної потужності (v_rated ≤ v ≤ v_cut_out):
   P(v) = P_rated  (потужність стабілізується системою обмеження)

4. Зона аварійного відключення (v > v_cut_out):
   P(v) = 0        (ротор заблокований гальмом)
```

Повний річний виробіток електричної енергії `AEP` (у ват-годинах або кіловат-годинах) є інтегралом добутку електричної потужності `P(v)` на ймовірність появи відповідної швидкості `f(v)` за всі 8760 годин календарного року:

```
AEP = 8760 · ∫₀^∞ P(v) · f(v; k, c) dv
```

Коефіцієнт використання встановленої потужності (КВВП / *Capacity Factor*, `CF`) визначає експлуатаційну ефективність установки відносно теоретичної цілорічної роботи на номіналі:

```
CF = AEP / (P_rated · 8760) = P_avg / P_rated
```

Для малих вітряків (потужністю до 5 кВт) у приземному шарі забудови реалістичний коефіцієнт `CF` становить `14–25%`, тоді як великі промислові турбіни на щоглах понад 100 м досягають `38–52%`.

### Чисельний метод інтегрування та обробка стрибків

Оскільки функція `P(v)` має стрибкоподібні зміни поведінки на межах `v_ci` та `v_cut_out`, аналітичне взяття інтеграла в елементарних функціях неможливе. Програма застосовує чисельне інтегрування за складеним правилом трапецій із високою дискретизацією (`dv = 0.025 м/с`, 1400 кроків у діапазоні від 0 до 35 м/с). Дрібний крок гарантує похибку дискретизації менше 0.05%, що повністю нівелює помилки апроксимації кубічного закону.

### Реалізація алгоритму: C та C++

У наведених програмах реалізовано повний математичний апарат оцінки вітрового виробітку малої установки номіналом 1 кВт (діаметр ротора 2.8 м, площа 6.16 м²) для типових кліматичних умов помірного поясу.

:::tabs
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double rated_power_w;   /* Номінальна електрична потужність (Вт) */
    double v_cut_in;        /* Швидкість увімкнення (м/с) */
    double v_rated;         /* Номінальна швидкість виходу на потужність (м/с) */
    double v_cut_out;       /* Швидкість аварійного гальмування (м/с) */
    double rotor_radius_m;  /* Радіус ротора (м) */
    double cp_max;          /* Максимальний аеродинамічний ККД ротора */
    double eta_gen;         /* Сумарний ККД генератора, підшипників та випрямляча */
} WindTurbine;

typedef struct {
    double shape_k;         /* Безрозмірний параметр форми k */
    double scale_c;         /* Масштабний параметр швидкості c (м/с) */
    double air_density;     /* Фактична густина повітря (кг/м3, стандарт 1.225) */
} WindClimate;

typedef struct {
    double aep_kwh;         /* Річний виробіток енергії (кВт·год/рік) */
    double avg_power_w;     /* Середньорічна вихідна потужність (Вт) */
    double capacity_factor; /* Коефіцієнт використання потужності (CF, 0..1) */
    double hours_operating; /* Кількість годин генерації за рік */
} WindYieldResult;

/* Густина ймовірності розподілу Вейбулла f(v; k, c) */
double weibull_pdf(double v, double k, double c) {
    if (v <= 0.0 || c <= 0.0 || k <= 0.0) {
        return 0.0;
    }
    double v_c = v / c;
    return (k / c) * pow(v_c, k - 1.0) * exp(-pow(v_c, k));
}

/* Модель вихідної потужності генератора P(v) з урахуванням аеродинаміки та ККД */
double turbine_electrical_power(const WindTurbine *t, const WindClimate *w, double v) {
    if (v < t->v_cut_in || v > t->v_cut_out) {
        return 0.0;
    }
    if (v >= t->v_rated) {
        return t->rated_power_w;
    }
    /* Розрахунок площі обметання: A = pi * R^2 */
    double area = M_PI * t->rotor_radius_m * t->rotor_radius_m;
    /* Аеродинамічна потужність на валу: P = 0.5 * rho * A * v^3 * Cp * eta */
    double p_aero = 0.5 * w->air_density * area * pow(v, 3.0) * t->cp_max * t->eta_gen;

    if (p_aero > t->rated_power_w) {
        p_aero = t->rated_power_w;
    }
    return p_aero;
}

/* Чисельний розрахунок річної генерації за складеним правилом трапецій */
WindYieldResult calculate_annual_yield(const WindTurbine *t, const WindClimate *w) {
    const double v_max = 35.0;     /* Верхня межа інтегрування за швидкістю (м/с) */
    const int steps = 1400;        /* Кількість інтервалів: dv = 35.0 / 1400 = 0.025 м/с */
    const double dv = v_max / (double)steps;
    const double hours_per_year = 8760.0;

    double sum_power_weighted = 0.0;
    double sum_prob_operating = 0.0;

    for (int i = 0; i <= steps; ++i) {
        double v = i * dv;
        double pdf = weibull_pdf(v, w->shape_k, w->scale_c);
        double p_el = turbine_electrical_power(t, w, v);

        double weight = (i == 0 || i == steps) ? 0.5 : 1.0;
        sum_power_weighted += weight * (p_el * pdf);

        if (v >= t->v_cut_in && v <= t->v_cut_out) {
            sum_prob_operating += weight * pdf;
        }
    }

    double avg_power = sum_power_weighted * dv;
    double aep_wh = avg_power * hours_per_year;
    double prob_oper = sum_prob_operating * dv;

    WindYieldResult res;
    res.avg_power_w = avg_power;
    res.aep_kwh = aep_wh / 1000.0;
    res.capacity_factor = avg_power / t->rated_power_w;
    res.hours_operating = prob_oper * hours_per_year;
    return res;
}

int main(void) {
    WindTurbine turbine = {
        .rated_power_w = 1000.0,   /* 1000 Вт номіналу */
        .v_cut_in = 3.0,          /* 3.0 м/с швидкість старту */
        .v_rated = 11.0,          /* 11.0 м/с вихід на повну потужність */
        .v_cut_out = 24.0,        /* 24.0 м/с штормове гальмування */
        .rotor_radius_m = 1.4,    /* Радіус 1.4 м (діаметр 2.8 м, площа 6.16 м2) */
        .cp_max = 0.42,           /* Трилопатевий ротор із профілем NACA */
        .eta_gen = 0.85           /* Сумарний ККД генератора та випрямляча */
    };

    WindClimate climate = {
        .shape_k = 2.05,          /* Параметр форми Вейбулла (помірний вітер) */
        .scale_c = 6.20,          /* Масштабний параметр (середня швидкість ~5.5 м/с) */
        .air_density = 1.225      /* Густина повітря на рівні моря при 15 °C */
    };

    WindYieldResult res = calculate_annual_yield(&turbine, &climate);

    printf("=== Розрахунок річної генерації малої вітроустановки ===\n");
    printf("Номінальна потужність:      %.0f Вт\n", turbine.rated_power_w);
    printf("Діаметр ротора:             %.2f м (площа: %.2f м2)\n",
           turbine.rotor_radius_m * 2.0, M_PI * turbine.rotor_radius_m * turbine.rotor_radius_m);
    printf("Параметри вітру Вейбулла:   k = %.2f, c = %.2f м/с\n", climate.shape_k, climate.scale_c);
    printf("Густина повітря:            %.3f кг/м3\n", climate.air_density);
    printf("----------------------------------------------------\n");
    printf("Середньорічна потужність:   %.1f Вт\n", res.avg_power_w);
    printf("Річна генерація (AEP):      %.1f кВт·год/рік\n", res.aep_kwh);
    printf("Коефіцієнт потужності (CF): %.2f %% (КВВП)\n", res.capacity_factor * 100.0);
    printf("Час активної генерації:     %.0f годин/рік (%.1f %% часу)\n",
           res.hours_operating, (res.hours_operating / 8760.0) * 100.0);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>

struct WindTurbine {
    double rated_power_w{1000.0};
    double v_cut_in{3.0};
    double v_rated{11.0};
    double v_cut_out{24.0};
    double rotor_radius_m{1.4};
    double cp_max{0.42};
    double eta_gen{0.85};

    [[nodiscard]] constexpr double swept_area() const noexcept {
        return std::numbers::pi * rotor_radius_m * rotor_radius_m;
    }
};

struct WindClimate {
    double shape_k{2.05};
    double scale_c{6.20};
    double air_density{1.225};

    [[nodiscard]] double pdf(double v) const noexcept {
        if (v <= 0.0 || scale_c <= 0.0 || shape_k <= 0.0) {
            return 0.0;
        }
        const double v_c = v / scale_c;
        return (shape_k / scale_c) * std::pow(v_c, shape_k - 1.0) * std::exp(-std::pow(v_c, shape_k));
    }
};

struct YieldResult {
    double aep_kwh{0.0};
    double avg_power_w{0.0};
    double capacity_factor{0.0};
    double hours_operating{0.0};
};

class WindEnergyEstimator {
public:
    static double electrical_power(const WindTurbine& t, const WindClimate& w, double v) noexcept {
        if (v < t.v_cut_in || v > t.v_cut_out) {
            return 0.0;
        }
        if (v >= t.v_rated) {
            return t.rated_power_w;
        }
        const double p_aero = 0.5 * w.air_density * t.swept_area() * std::pow(v, 3.0) * t.cp_max * t.eta_gen;
        return std::min(p_aero, t.rated_power_w);
    }

    static YieldResult evaluate(const WindTurbine& t, const WindClimate& w) noexcept {
        constexpr double v_max = 35.0;
        constexpr int steps = 1400;
        constexpr double dv = v_max / static_cast<double>(steps);
        constexpr double hours_per_year = 8760.0;

        double sum_power_weighted = 0.0;
        double sum_prob_operating = 0.0;

        for (int i = 0; i <= steps; ++i) {
            const double v = static_cast<double>(i) * dv;
            const double pdf = w.pdf(v);
            const double p_el = electrical_power(t, w, v);

            const double weight = (i == 0 || i == steps) ? 0.5 : 1.0;
            sum_power_weighted += weight * (p_el * pdf);

            if (v >= t.v_cut_in && v <= t.v_cut_out) {
                sum_prob_operating += weight * pdf;
            }
        }

        const double avg_power = sum_power_weighted * dv;
        const double aep_wh = avg_power * hours_per_year;
        const double prob_oper = sum_prob_operating * dv;

        return YieldResult{
            .aep_kwh = aep_wh / 1000.0,
            .avg_power_w = avg_power,
            .capacity_factor = avg_power / t.rated_power_w,
            .hours_operating = prob_oper * hours_per_year
        };
    }
};

int main() {
    const WindTurbine turbine;
    const WindClimate climate;

    const YieldResult res = WindEnergyEstimator::evaluate(turbine, climate);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Розрахунок річної генерації малої вітроустановки ===\n";
    std::cout << "Номінальна потужність:      " << turbine.rated_power_w << " Вт\n";
    std::cout << "Діаметр ротора:             " << (turbine.rotor_radius_m * 2.0)
              << " м (площа: " << turbine.swept_area() << " м2)\n";
    std::cout << "Параметри вітру Вейбулла:   k = " << climate.shape_k
              << ", c = " << climate.scale_c << " м/с\n";
    std::cout << "Густина повітря:            " << climate.air_density << " кг/м3\n";
    std::cout << "----------------------------------------------------\n";
    std::cout << "Середньорічна потужність:   " << std::setprecision(1) << res.avg_power_w << " Вт\n";
    std::cout << "Річна генерація (AEP):      " << res.aep_kwh << " кВт·год/рік\n";
    std::cout << "Коефіцієнт потужності (CF): " << std::setprecision(2) << (res.capacity_factor * 100.0) << " % (КВВП)\n";
    std::cout << "Час активної генерації:     " << std::setprecision(0) << res.hours_operating
              << " годин/рік (" << std::setprecision(1) << (res.hours_operating / 8760.0 * 100.0) << " % часу)\n";

    return 0;
}
```
:::

### Інженерні пастки аналізу вітрових даних

1. **Помилка прямого усереднення (нерівність Єнсена)**: Підстановка середньої швидкості вітру `v_avg` безпосередньо у формулу потужності `P(v_avg)` занижує реальну енергію вітру в 1.5–2.5 раза порівняно з інтегралом розподілу. Для опуклої кубічної функції середнє значення куба завжди строго більше за куб середнього значення: `E[v³] > (E[v])³`. Розрахунок «по середній швидкості» підходить для гідроелектростанцій із постійним потоком води, але фатально непридатний для вітроенергетики.
2. **Висотна екстраполяція параметрів Вейбулла**: Дані метеостанцій зазвичай наводяться для стандартної висоти анемометра (грец. *ἄνεμος* — вітер + *μέτροн* — міра) 10 метрів на відкритій місцевості аеропортів. При перенесенні на реальну висоту щогли малої установки `h` масштабний параметр `c` змінюється за логарифмічним або степеневим законом вітрового зсуву `c(h) = c_10 · (h / 10)^α`, а параметр форми `k` дещо зростає з висотою через ламінаризацію потоку. Ігнорування висотної поправки в зоні забудови завищує очікуваний виробіток у 2–3 рази.
3. **Облік нижнього порогу `v_cut_in` та пускового моменту**: Якщо в регіоні більшість вітрових годин припадає на легкий бриз 2.0–2.8 м/с, установка з порогом увімкнення `v_cut_in = 3.2 м/с` простоюватиме без генерації до 70% річного часу. Для слабковітрових локацій вигідніше обирати ротор зі збільшеним радіусом лопатей та зниженою швидкістю старту, навіть якщо це супроводжується дещо нижчим максимальним ККД на штормових режимах.
4. **Нелінійність електромеханічного ККД при слабкому вітрі**: На практиці ККД генератора та випрямляча не є постійною константою `η = 0.85`. При слабкому вітрі струм генератора малий, і постійне падіння напруги на діодах випрямляча (близько 0.7–1.0 В на діодний міст) забирає до 15–25% всієї генерованої напруги. У міру зростання вітру напруга генератора зростає, і відносні втрати на діодах падають до 2–4%.
