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
