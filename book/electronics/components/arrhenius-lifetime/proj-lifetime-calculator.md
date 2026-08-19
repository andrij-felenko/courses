# ⚙️ Інженерний розрахунок надійності: калькулятор ресурсу конденсаторів, коефіцієнтів AF та MTBF

Під час розробки сучасних імпульсних джерел живлення, приводних інверторів, телекомунікаційних базових станцій та автомобільних контролерів оцінка терміну служби компонентів є обов'язковим етапом проєктування. Інженер не може покладатися на інтуїтивні оцінки: помилка у визначенні робочої температури серцевини конденсатора чи напівпровідникового кристала всього на 10 °C змінює розрахунковий ресурс виробу вдвічі, що в умовах масового виробництва призводить до мільйонних збитків від передчасних гарантійних відмов.

Нижче представлено завершений інженерний інструмент надійності, реалізований мовами C та C++. Модуль розв'язує комплексні прикладні задачі: від точного розрахунку температурного коефіцієнта прискорення Арреніуса з контролем чисельної точності до багатофакторного прогнозування ресурсу електролітичних конденсаторів з урахуванням внутрішнього саморозігріву та статистичної обробки планів прискорених випробувань HTOL за стандартами JEDEC JESD22-A108 та AEC-Q100.

## Архітектура та фізико-математичні основи калькулятора

Програмний комплекс побудовано на основі чотирьох взаємопов'язаних аналітичних модулів:

### 1. Модуль кінетики Арреніуса та контроль чисельної стабільності
Швидкість термохімічних реакцій та дифузійних процесів описується множником `exp( −E_a / (k_B · T) )`. Коефіцієнт температурного прискорення `AF_T` між робочою температурою `T_use` та підвищеною випробувальною температурою `T_stress` визначається виразом:

```
AF_T = exp[ (E_a / k_B) · ( 1 / (T_use + 273.15) − 1 / (T_stress + 273.15) ) ]
```

Під час програмної реалізації цієї формули виникає проблема віднімання близьких чисел: різниця обернених температур `(1 / T_use) − (1 / T_stress)` для температурного діапазону електроніки (наприклад, між +45 °C та +125 °C) має порядок `10⁻⁴ ... 10⁻³ К⁻¹`. При використанні чисел із плаваючою комою одинарної точності (`float`) накопичення похибок округлення може призвести до спотворення результату на 5–10 %. Тому всі обчислення в ядрі виконуються виключно у форматі подвійної точності `double` (IEEE 754).

### 2. Модуль теплової моделі та ресурсу електролітичних конденсаторів
В алюмінієвих оксидно-електролітичних конденсаторах з рідким електролітом швидкість деградації визначається двома джерелами теплової енергії: температурою навколишнього середовища всередині корпусу виробу `T_ambient` та внутрішнім джоулевим саморозігрівом серцевини `ΔT_core`, викликаним протіканням змінного струму пульсацій `I_ripple` крізь активний опір `ESR` (`P_loss = I_ripple² · ESR`).

Тепловий потік від внутрішнього рулону фольги до алюмінієвого стаканчика та далі у повітря описується еквівалентним тепловим опором:

```
ΔT_core = P_loss · ( θ_core_to_can + θ_can_to_ambient ) = I_ripple² · ESR · θ_thermal
```

Оскільки в технічній документації (даташитах) виробники зазвичай не вказують абсолютне значення `θ_thermal`, вони регламентують максимально допустимий внутрішній перегрів `ΔT_max_ripple` (зазвичай 5 °C для високотемпературних серій 105 °C/125 °C та 10 °C для серій 85 °C) при номінальному паспортному струмі пульсацій `I_ripple_rated`. Тоді внутрішній перегрів за фактичного струму `I_ripple_actual` розраховується через квадратичну пропорцію:

```
ΔT_core = ΔT_max_ripple · ( I_ripple_actual / I_ripple_rated )²
T_core = T_ambient + ΔT_core
```

Очікуваний робочий ресурс конденсатора `L` обчислюється за формулою подвоєння терміну служби на кожні 10 °C зниження температури серцевини нижче паспортного максимуму `T_max` із корекцією на дератинг за напругою:

```
L = L_0 · 2^( (T_max − T_core) / 10 ) · ( V_rated / V_actual )^n_volt
```

де `L_0` — гарантований ресурс при граничній температурі `T_max` (зазвичай 2000, 5000 або 10 000 годин), а `n_volt` — емпіричний показник напругового фактора (приймається рівним `1.0` для напруг від 0.6 до 1.0 номіналу або `0.0` для консервативного розрахунку).

**Критичні інженерні обмеження та крайові випадки:**
- **Стеля 15 років (131 400 годин):** Якщо за низької температури довкілля (+25...+35 °C) математична формула видає теоретичний ресурс у 40–80 років, програма автоматично примусово обмежує результуючий термін служби значенням 15 років. Це зумовлено тим, що гумова ущільнювальна пробка з часом зазнає незворотної механічної деструкції, втрачає пружність та тріскається під впливом озону, перепадів тиску та залишкових механічних напружень незалежно від температурного охолодження.
- **Теплове перевантаження:** Якщо температура серцевини перевищує `T_max`, або якщо фактичний струм пульсацій перевищує `I_ripple_rated` більш ніж у 1.2 раза, програма встановлює прапорець критичного перегріву `is_overheated = true`. Робота в такому режимі призводить до бурхливого виділення водню, закипання електроліту та спрацьовування запобіжного насічного клапана на денці конденсатора.

### 3. Модуль мультифакторного старіння MLCC та плівкових конденсаторів
Для багатошарових керамічних конденсаторів (MLCC класу X7R/X8R на основі `BaTiO3`) та металізованих плівкових конденсаторів деградація ізоляційного шару підпорядковується комбінованій температурно-напруговій моделі Прокоповича-Васкаса:

```
AF_total = ( V_stress / V_use )^n_volt · exp[ (E_a / k_B) · ( 1 / (T_use + 273.15) − 1 / (T_stress + 273.15) ) ]
```

де `n_volt ≈ 3.0 ... 4.0` для MLCC та `n_volt ≈ 5.0 ... 8.0` для плівкових конденсаторів, а енергія активації міграції дефектів становить `E_a ≈ 1.1 ... 1.3 еВ`.

### 4. Модуль статистичної кваліфікації за стандартом HTOL (JEDEC JESD22-A108)
Під час кваліфікації надійності вибірку з `N` мікросхем тестують протягом часу `t_test` (типово 1000 годин) за підвищеної температури `T_stress` (наприклад, +125 °C). Сумарний еквівалентний час польового напрацювання розраховується як:

```
T_total = N · t_test · AF_total  [приладо-годин]
```

За нульової кількості зафіксованих відмов (`r = 0`) верхня довірча межа інтенсивності відмов `λ` для заданого рівня статистичної достовірності (Confidence Level `CL` = 60 % або 90 %) визначається через квантилі розподілу хі-квадрат:

```
λ_upper = ( χ²( 2·r + 2, 1 − CL ) / ( 2 · T_total ) ) × 10⁹  [FIT, відмов / 10⁹ годин]
MTBF = 10⁹ / λ_upper  [годин]
```

Для нульової кількості відмов квантилі мають значення `χ²(2, 0.40) ≈ 1.833` для 60 % довіри та `χ²(2, 0.10) ≈ 4.605` для 90 % довіри.

## Реалізація інженерного модуля

Нижче наведено повний вихідний код модуля мовами C та C++. Обидві версії є повністю самодостатніми, не мають зовнішніх залежностей окрім стандартної бібліотеки та містять вичерпні перевірки крайових умов.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define KB_EV 8.617333262e-5            /* Стала Больцмана в еВ/К */
#define MAX_ELECTROLYTIC_LIFE_HOURS 131400.0 /* 15 років у годинах (15 * 8760) */
#define HOURS_PER_YEAR 8760.0

/* Структура параметрів електролітичного конденсатора */
typedef struct {
    double l0_hours;         /* Паспортний ресурс при Tmax (год, напр. 2000, 5000) */
    double t_max_c;          /* Гранична температура за даташитом (°C, напр. 105.0) */
    double t_ambient_c;      /* Фактична температура повітря навколо компонента (°C) */
    double dt_max_ripple_c;  /* Паспортний перегрів від номінальних пульсацій (зазвичай 5.0 °C) */
    double i_ripple_actual;  /* Фактичний діючий струм пульсацій (А) */
    double i_ripple_rated;   /* Допустимий паспортний струм пульсацій (А) */
    double v_rated;          /* Номінальна напруга конденсатора (В) */
    double v_actual;         /* Фактична прикладена постійна напруга (В) */
    double voltage_exponent; /* Показник дератингу за напругою (0.0 для старих серій, 1.0..2.0 для нових) */
} ElectrolyticCapConfig;

/* Результат розрахунку ресурсу конденсатора */
typedef struct {
    double dt_core_c;
    double t_core_c;
    double raw_life_hours;
    double effective_life_hours;
    double life_years;
    bool is_overheated;
    bool is_clamped_to_15y;
} CapLifeReport;

/* Структура звіту кваліфікації HTOL */
typedef struct {
    double equivalent_field_hours;
    double fit_60;
    double fit_90;
    double mtbf_hours_60;
    double mtbf_years_60;
} HtolReport;

/* 1. Розрахунок температурного коефіцієнта прискорення Арреніуса */
double arrhenius_af(double ea_ev, double t_use_c, double t_stress_c) {
    if (ea_ev <= 0.0) return 1.0;
    double t_use_k = t_use_c + 273.15;
    double t_stress_k = t_stress_c + 273.15;
    if (t_use_k <= 0.0 || t_stress_k <= 0.0) return 1.0;
    double inv_diff = (1.0 / t_use_k) - (1.0 / t_stress_k);
    return exp((ea_ev / KB_EV) * inv_diff);
}

/* 2. Мультифакторна модель Прокоповича-Васкаса для MLCC та плівки */
double prokopowicz_vaskas_af(double ea_ev, double t_use_c, double t_stress_c,
                             double v_use, double v_stress, double n_exponent) {
    double af_temp = arrhenius_af(ea_ev, t_use_c, t_stress_c);
    double af_volt = 1.0;
    if (v_use > 0.0 && v_stress > 0.0 && n_exponent > 0.0) {
        af_volt = pow(v_stress / v_use, n_exponent);
    }
    return af_temp * af_volt;
}

/* 3. Розрахунок ресурсу алюмінієвого електролітичного конденсатора */
CapLifeReport calc_electrolytic_life(const ElectrolyticCapConfig *cfg) {
    CapLifeReport rep;
    double ripple_ratio = 0.0;
    if (cfg->i_ripple_rated > 0.0) {
        ripple_ratio = cfg->i_ripple_actual / cfg->i_ripple_rated;
    }
    if (ripple_ratio < 0.0) ripple_ratio = 0.0;

    /* Джоулів перегрів пропорційний квадрату відношення струмів */
    rep.dt_core_c = cfg->dt_max_ripple_c * (ripple_ratio * ripple_ratio);
    rep.t_core_c = cfg->t_ambient_c + rep.dt_core_c;
    rep.is_overheated = (rep.t_core_c > cfg->t_max_c);

    /* Температурний множник: степінь двійки */
    double temp_factor = pow(2.0, (cfg->t_max_c - rep.t_core_c) / 10.0);

    /* Напруговий дератинг */
    double volt_factor = 1.0;
    if (cfg->voltage_exponent > 0.0 && cfg->v_actual > 0.0 && cfg->v_actual <= cfg->v_rated) {
        volt_factor = pow(cfg->v_rated / cfg->v_actual, cfg->voltage_exponent);
    }

    rep.raw_life_hours = cfg->l0_hours * temp_factor * volt_factor;

    if (rep.raw_life_hours > MAX_ELECTROLYTIC_LIFE_HOURS) {
        rep.effective_life_hours = MAX_ELECTROLYTIC_LIFE_HOURS;
        rep.is_clamped_to_15y = true;
    } else {
        rep.effective_life_hours = rep.raw_life_hours;
        rep.is_clamped_to_15y = false;
    }

    rep.life_years = rep.effective_life_hours / HOURS_PER_YEAR;
    return rep;
}

/* 4. Оцінка надійності за результатами HTOL (r = 0 відмов) */
HtolReport evaluate_htol(int n_samples, double t_test_hours, double af) {
    HtolReport rep;
    rep.equivalent_field_hours = (double)n_samples * t_test_hours * af;

    /* Квантилі хі-квадрат для r = 0: 60% = 1.833, 90% = 4.605 */
    double chi2_60 = 1.833;
    double chi2_90 = 4.605;

    if (rep.equivalent_field_hours > 0.0) {
        rep.fit_60 = (chi2_60 / (2.0 * rep.equivalent_field_hours)) * 1.0e9;
        rep.fit_90 = (chi2_90 / (2.0 * rep.equivalent_field_hours)) * 1.0e9;
        rep.mtbf_hours_60 = 1.0e9 / rep.fit_60;
        rep.mtbf_years_60 = rep.mtbf_hours_60 / HOURS_PER_YEAR;
    } else {
        rep.fit_60 = 0.0;
        rep.fit_90 = 0.0;
        rep.mtbf_hours_60 = 0.0;
        rep.mtbf_years_60 = 0.0;
    }
    return rep;
}

int main(void) {
    printf("=================================================================\n");
    printf("     ІНЖЕНЕРНИЙ РОЗРАХУНОК НАДІЙНОСТІ ТА ЗАКОНУ АРРЕНІУСА         \n");
    printf("=================================================================\n\n");

    /* Тестовий випадок 1: Прискорення для кремнієвого кристала */
    double ea_silicon = 0.70; /* еВ */
    double t_use_ambient = 45.0; /* °C */
    double t_stress_chamber = 125.0; /* °C */
    double af_semi = arrhenius_af(ea_silicon, t_use_ambient, t_stress_chamber);

    printf("1. ТЕМПЕРАТУРНЕ ПРИСКОРЕННЯ HTOL (КРЕМНІЙ):\n");
    printf("   Енергія активації Ea:        %.2f еВ\n", ea_silicon);
    printf("   Робоча температура T_use:    +%.1f °C\n", t_use_ambient);
    printf("   Стресова температура T_test: +%.1f °C\n", t_stress_chamber);
    printf("   -> Коефіцієнт прискорення:   AF = %.2f x\n\n", af_semi);

    /* Тестовий випадок 2: Розрахунок ресурсу електролітичного конденсатора */
    ElectrolyticCapConfig cap = {
        .l0_hours = 5000.0,
        .t_max_c = 105.0,
        .t_ambient_c = 55.0,
        .dt_max_ripple_c = 5.0,
        .i_ripple_actual = 1.6, /* 1.6 А при номіналі 2.0 А */
        .i_ripple_rated = 2.0,
        .v_rated = 35.0,
        .v_actual = 24.0,
        .voltage_exponent = 1.0
    };

    CapLifeReport cap_rep = calc_electrolytic_life(&cap);

    printf("2. РЕСУРС ЕЛЕКТРОЛІТИЧНОГО КОНДЕНСАТОРА (105 °C / 5000 год):\n");
    printf("   Температура довкілля Ta:     +%.1f °C\n", cap.t_ambient_c);
    printf("   Струм пульсацій:             %.2f А / %.2f А (%.0f %%)\n",
           cap.i_ripple_actual, cap.i_ripple_rated, (cap.i_ripple_actual / cap.i_ripple_rated) * 100.0);
    printf("   Джоулів перегрів серцевини:  Delta T = +%.2f °C\n", cap_rep.dt_core_c);
    printf("   Температура серцевини T_core:+%.2f °C\n", cap_rep.t_core_c);
    printf("   Розрахунковий ресурс:        %.0f годин (%.2f років)\n",
           cap_rep.effective_life_hours, cap_rep.life_years);
    if (cap_rep.is_clamped_to_15y) {
        printf("   [!] Розрахунок обмежено стелею 15 років через деградацію гумового ущільнювача\n");
    }
    printf("\n");

    /* Тестовий випадок 3: Кваліфікація партії HTOL */
    int sample_size = 231; /* 3 партії по 77 штук */
    double test_duration = 1000.0; /* годин */
    HtolReport htol_rep = evaluate_htol(sample_size, test_duration, af_semi);

    printf("3. КВАЛІФІКАЦІЯ ПАРТІЇ ВІС ЗА СТАНДАРТОМ JEDEC HTOL:\n");
    printf("   Кількість зразків:           N = %d шт (нуль відмов r = 0)\n", sample_size);
    printf("   Тривалість тесту:            %0.f годин (~42 доби)\n", test_duration);
    printf("   Еквівалентний польовий час:  %.2f млн приладо-годин\n",
           htol_rep.equivalent_field_hours / 1.0e6);
    printf("   Інтенсивність відмов (60 %%):  lambda = %.2f FIT\n", htol_rep.fit_60);
    printf("   Інтенсивність відмов (90 %%):  lambda = %.2f FIT\n", htol_rep.fit_90);
    printf("   Середній MTBF (60 %% довіра):  %.0f годин (%.1f років)\n",
           htol_rep.mtbf_hours_60, htol_rep.mtbf_years_60);
    printf("=================================================================\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <format>
#include <numbers>
#include <algorithm>
#include <string_view>

namespace Reliability {

constexpr double kB_eV = 8.617333262e-5;               // Стала Больцмана (еВ/К)
constexpr double MaxElectrolyticLifeHours = 131400.0; // 15 років стеля
constexpr double HoursPerYear = 8760.0;

// Специфікація конденсатора
struct ElectrolyticCapSpec {
    double l0_hours{5000.0};
    double t_max_c{105.0};
    double dt_max_ripple_c{5.0};
    double v_rated{35.0};
    double i_ripple_rated{2.0};
    double voltage_exponent{1.0};
};

// Робочі умови експлуатації
struct OperatingConditions {
    double t_ambient_c{55.0};
    double v_actual{24.0};
    double i_ripple_actual{1.6};
};

// Звіт розрахунку ресурсу конденсатора
struct CapacitorLifeReport {
    double dt_core_c;
    double t_core_c;
    double raw_life_hours;
    double effective_life_hours;
    double life_years;
    bool is_overheated;
    bool is_clamped_to_15y;
};

// Звіт кваліфікації HTOL
struct HtolReport {
    double equivalent_field_hours;
    double fit_60;
    double fit_90;
    double mtbf_hours_60;
    double mtbf_years_60;
};

// Розрахунок коефіцієнта температурного прискорення Арреніуса
[[nodiscard]] constexpr double arrheniusAccelerationFactor(double ea_ev, double t_use_c, double t_stress_c) noexcept {
    if (ea_ev <= 0.0) return 1.0;
    const double t_use_k = t_use_c + 273.15;
    const double t_stress_k = t_stress_c + 273.15;
    if (t_use_k <= 0.0 || t_stress_k <= 0.0) return 1.0;
    const double inv_diff = (1.0 / t_use_k) - (1.0 / t_stress_k);
    return std::exp((ea_ev / kB_eV) * inv_diff);
}

// Модель Прокоповича-Васкаса для керамічних конденсаторів MLCC
[[nodiscard]] double prokopowiczVaskasFactor(double ea_ev, double t_use_c, double t_stress_c,
                                            double v_use, double v_stress, double n_exponent = 3.0) noexcept {
    const double af_temp = arrheniusAccelerationFactor(ea_ev, t_use_c, t_stress_c);
    double af_volt = 1.0;
    if (v_use > 0.0 && v_stress > 0.0 && n_exponent > 0.0) {
        af_volt = std::pow(v_stress / v_use, n_exponent);
    }
    return af_temp * af_volt;
}

// Розрахунок ресурсу алюмінієвого електролітичного конденсатора
[[nodiscard]] CapacitorLifeReport evaluateCapacitorLife(const ElectrolyticCapSpec& spec,
                                                       const OperatingConditions& op) noexcept {
    double ripple_ratio = (spec.i_ripple_rated > 0.0) ? (op.i_ripple_actual / spec.i_ripple_rated) : 0.0;
    ripple_ratio = std::max(0.0, ripple_ratio);

    const double dt_core = spec.dt_max_ripple_c * (ripple_ratio * ripple_ratio);
    const double t_core = op.t_ambient_c + dt_core;
    const bool overheated = (t_core > spec.t_max_c);

    const double temp_factor = std::pow(2.0, (spec.t_max_c - t_core) / 10.0);

    double volt_factor = 1.0;
    if (spec.voltage_exponent > 0.0 && op.v_actual > 0.0 && op.v_actual <= spec.v_rated) {
        volt_factor = std::pow(spec.v_rated / op.v_actual, spec.voltage_exponent);
    }

    const double raw_life = spec.l0_hours * temp_factor * volt_factor;
    const bool clamped = (raw_life > MaxElectrolyticLifeHours);
    const double final_hours = clamped ? MaxElectrolyticLifeHours : raw_life;

    return CapacitorLifeReport{
        .dt_core_c = dt_core,
        .t_core_c = t_core,
        .raw_life_hours = raw_life,
        .effective_life_hours = final_hours,
        .life_years = final_hours / HoursPerYear,
        .is_overheated = overheated,
        .is_clamped_to_15y = clamped
    };
}

// Розрахунок надійності за тестом HTOL
[[nodiscard]] HtolReport evaluateHtolReliability(int n_samples, double t_test_hours, double af) noexcept {
    const double total_hours = static_cast<double>(n_samples) * t_test_hours * af;
    constexpr double chi2_60 = 1.833; // 60% довіра для r = 0
    constexpr double chi2_90 = 4.605; // 90% довіра для r = 0

    if (total_hours <= 0.0) {
        return HtolReport{0.0, 0.0, 0.0, 0.0, 0.0};
    }

    const double fit60 = (chi2_60 / (2.0 * total_hours)) * 1.0e9;
    const double fit90 = (chi2_90 / (2.0 * total_hours)) * 1.0e9;
    const double mtbf60 = 1.0e9 / fit60;

    return HtolReport{
        .equivalent_field_hours = total_hours,
        .fit_60 = fit60,
        .fit_90 = fit90,
        .mtbf_hours_60 = mtbf60,
        .mtbf_years_60 = mtbf60 / HoursPerYear
    };
}

} // namespace Reliability

int main() {
    using namespace Reliability;
    std::cout << "=================================================================\n";
    std::cout << "     ІНЖЕНЕРНИЙ РОЗРАХУНОК НАДІЙНОСТІ ТА ЗАКОНУ АРРЕНІУСА (C++20) \n";
    std::cout << "=================================================================\n\n";

    // 1. Прискорення для кремнієвого кристала
    constexpr double ea_silicon = 0.70;
    constexpr double t_use = 45.0;
    constexpr double t_stress = 125.0;
    const double af = arrheniusAccelerationFactor(ea_silicon, t_use, t_stress);

    std::cout << std::format("1. ТЕМПЕРАТУРНЕ ПРИСКОРЕННЯ HTOL (КРЕМНІЙ):\n"
                             "   Енергія активації Ea:        {:.2f} еВ\n"
                             "   Робоча температура T_use:    +{:.1f} °C\n"
                             "   Стресова температура T_test: +{:.1f} °C\n"
                             "   -> Коефіцієнт прискорення:   AF = {:.2f} x\n\n",
                             ea_silicon, t_use, t_stress, af);

    // 2. Ресурс електролітичного конденсатора
    const ElectrolyticCapSpec cap_spec{
        .l0_hours = 5000.0,
        .t_max_c = 105.0,
        .dt_max_ripple_c = 5.0,
        .v_rated = 35.0,
        .i_ripple_rated = 2.0,
        .voltage_exponent = 1.0
    };

    const OperatingConditions cap_ops{
        .t_ambient_c = 55.0,
        .v_actual = 24.0,
        .i_ripple_actual = 1.6
    };

    const auto cap_rep = evaluateCapacitorLife(cap_spec, cap_ops);

    std::cout << std::format("2. РЕСУРС ЕЛЕКТРОЛІТИЧНОГО КОНДЕНСАТОРА (105 °C / 5000 год):\n"
                             "   Температура довкілля Ta:     +{:.1f} °C\n"
                             "   Струм пульсацій:             {:.2f} А / {:.2f} А ({:.0f} %)\n"
                             "   Джоулів перегрів серцевини:  Delta T = +{:.2f} °C\n"
                             "   Температура серцевини T_core:+{:.2f} °C\n"
                             "   Розрахунковий ресурс:        {:.0f} годин ({:.2f} років)\n",
                             cap_ops.t_ambient_c, cap_ops.i_ripple_actual, cap_spec.i_ripple_rated,
                             (cap_ops.i_ripple_actual / cap_spec.i_ripple_rated) * 100.0,
                             cap_rep.dt_core_c, cap_rep.t_core_c, cap_rep.effective_life_hours, cap_rep.life_years);
    if (cap_rep.is_clamped_to_15y) {
        std::cout << "   [!] Розрахунок обмежено стелею 15 років через деградацію гумового ущільнювача\n";
    }
    std::cout << "\n";

    // 3. Кваліфікація HTOL
    constexpr int sample_size = 231;
    constexpr double test_duration = 1000.0;
    const auto htol_rep = evaluateHtolReliability(sample_size, test_duration, af);

    std::cout << std::format("3. КВАЛІФІКАЦІЯ ПАРТІЇ ВІС ЗА СТАНДАРТОМ JEDEC HTOL:\n"
                             "   Кількість зразків:           N = {} шт (нуль відмов r = 0)\n"
                             "   Тривалість тесту:            {:.0f} годин (~42 доби)\n"
                             "   Еквівалентний польовий час:  {:.2f} млн приладо-годин\n"
                             "   Інтенсивність відмов (60 %):  lambda = {:.2f} FIT\n"
                             "   Інтенсивність відмов (90 %):  lambda = {:.2f} FIT\n"
                             "   Середній MTBF (60 % довіра):  {:.0f} годин ({:.1f} років)\n"
                             "=================================================================\n",
                             sample_size, test_duration, htol_rep.equivalent_field_hours / 1.0e6,
                             htol_rep.fit_60, htol_rep.fit_90,
                             htol_rep.mtbf_hours_60, htol_rep.mtbf_years_60);

    return 0;
}
```
:::

## Практичний розбір чотирьох типових інженерних сценаріїв

Для демонстрації роботи калькулятора розглянемо реальні кейси проєктування силових та вбудованих систем:

### Сценарій 1: Вихідний фільтр серверного перетворювача 12 В / 50 А
У вторинному колі DC-DC перетворювача встановлено конденсатор `1000 мкФ / 25 В` серії +105 °C із базовим ресурсом `L_0 = 5000 годин` та допустимим струмом `I_rated = 2.8 А` (при `ΔT_max = 5 °C`).

1. **Варіант А (Погане охолодження):** Температура повітря біля плати `T_ambient = +70 °C`, струм пульсацій `I_actual = 2.5 А`.
   - Струмове навантаження: `2.5 / 2.8 = 89.3 %`;
   - Перегрів серцевини: `ΔT_core = 5.0 · (0.893)² = +3.99 °C`;
   - Температура серцевини: `T_core = 70.0 + 3.99 = +73.99 °C`;
   - Ресурс: `L = 5000 · 2^( (105 − 73.99)/10 ) · (25/12)¹ ≈ 5000 · 8.58 · 2.08 ≈ 89 200 годин (~10.2 року)`.

2. **Варіант Б (Оптимізоване охолодження):** Збільшено швидкість обдування вентилятора, `T_ambient` знизилася до +45 °C, а струм розподілено між двома конденсаторами (`I_actual = 1.25 А`).
   - Перегрів серцевини: `ΔT_core = 5.0 · (1.25 / 2.8)² = +1.00 °C`;
   - Температура серцевини: `T_core = 45.0 + 1.00 = +46.0 °C`;
   - Необмежений розрахунковий ресурс: `L_raw = 5000 · 2^( (105 − 46)/10 ) · 2.08 ≈ 618 000 годин (~70.5 року)`.
   - *Ефективний ресурс:* обмежено порогом **15 років (131 400 годин)** через старіння гумового ущільнювача. Зате забезпечено колосальний запас надійності за інтенсивністю відмов (менше 10 FIT).

### Сценарій 2: Підкапотний блок керування двигуном (Automotive ECU)
У блоці керування автомобільним двигуном температура під капотом сягає +105 °C. Інженер обирає між звичайним електролітичним конденсатором (+105 °C, 2000 год) та спеціалізованим гібридним твердотільно-полімерним конденсатором (+125 °C, 4000 год).
- Звичайний електроліт при `T_core = +105 °C` відпрацює рівно `2000 годин` (менше 3 місяців безперервної їзди).
- Високотемпературний гібрид (+125 °C) за температури +105 °C забезпечить:
  ```
  L = 4000 · 2^( (125 − 105)/10 ) = 4000 · 4 = 16 000 годин
  ```
  що повністю покриває нормативний автомобільний ресурс у 15 років типової міської експлуатації (близько 300 000 км пробігу).

### Сценарій 3: Кваліфікація власного кремнієвого ASIC для базових станцій 5G
Для виведення нового телекомунікаційного чипа на ринок необхідно гарантувати інтенсивність відмов менше 30 FIT за робочої температури +55 °C (`E_a = 0.70 еВ`).
- Прискорення в камері при +125 °C становить `AF = 77.63×`;
- За 1000 годин тесту один чип накопичує `77 630 приладо-годин`;
- Щоб отримати `λ_60% ≤ 30 FIT`, сумарне напрацювання має складати:
  ```
  T_total ≥ ( 1.833 / ( 2 · 30 × 10⁻⁹ ) ) = 30 550 000 приладо-годин
  ```
- Необхідна кількість зразків у випробувальній камері:
  ```
  N = T_total / ( t_test · AF ) = 30 550 000 / ( 1000 × 77.63 ) ≈ 394 зразки (або 200 зразків протягом 2000 годин).
  ```

## Інженерні пастки та рекомендації з вимірювань

1. **Коректне вимірювання струму пульсацій `I_ripple`:**
   Ніколи не вимірюйте струм через конденсатор за допомогою звичайного мультиметра: мультиметри розраховані на синусоїдальний струм 50/60 Гц і дають колосальну похибку на високочастотних імпульсних струмах. Вимірювання слід виконувати виключно широкосмуговими струмовими кліщами (наприклад, із смугою до 50–100 МГц) або вимірюванням напруги високочастотних пульсацій на відомому каліброваному низькоіндуктивному шунті за допомогою осцилографа з функцією обчислення True-RMS.

2. **Вплив топології друкованої плати на охолодження:**
   Виводи електролітичного конденсатора є чудовими провідниками тепла всередину рулону фольги. Якщо під'єднати вивід конденсатора до масивного силового полігону, з'єднаного з гарячим польовим транзистором, тепло від транзистора піде прямо всередину серцевини конденсатора через мідь виводів. Для термочутливих конденсаторів силові доріжки повинні мати теплові бар'єри (терморозв'язувальні звуження) або розміщуватися на віддалених охолоджених ділянках плати.

3. **Критерії визначення кінця терміну служби (End of Life, EOL):**
   У силових пристроях конденсатор вважається таким, що вичерпав свій ресурс, задовго до фізичного вибуху чи короткого замикання. Паспортними критеріями настання EOL є:
   - Падіння ємності `ΔC / C > 20 %`;
   - Зростання активного опору `ESR > 200 % ... 300 %` від номіналу;
   - Зростання струму витоку `I_leak` у 2 рази понад норму даташита.
