#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define KB_EV 8.617333e-5 /* Константа Больцмана в еВ/К */

/* Структура параметрів температурного старіння (Arrhenius) */
typedef struct {
    double t_use_c;     /* Експлуатаційна температура, °C */
    double t_stress_c;  /* Стресова температура випробувань, °C */
    double ea_ev;       /* Енергія активації, еВ (напр. 0.7) */
} ArrheniusParams;

/* Структура параметрів низькоциклової втоми пайки (Norris-Landzberg) */
typedef struct {
    double dt_use_c;        /* Розмах температур у полі Delta T, °C */
    double dt_stress_c;     /* Розмах температур у камері Delta T, °C */
    double f_use_cpd;       /* Частота циклів у полі (циклів на добу) */
    double f_stress_cph;     /* Частота циклів у камері (циклів на годину) */
    double t_max_use_c;     /* Максимальна температура циклу в полі, °C */
    double t_max_stress_c;  /* Максимальна температура циклу в камері, °C */
    double m_exp;           /* Втомний показник (2.65 для SAC305) */
    double n_exp;           /* Частотний показник (0.33) */
    double ea_ev;           /* Активаційна енергія (0.122 еВ) */
} NorrisLandzbergParams;

/* Структура параметрів вологості (Peck) */
typedef struct {
    double rh_use_pct;      /* Експлуатаційна вологість, % RH */
    double rh_stress_pct;   /* Вологість у камері, % RH (напр. 85.0) */
    double t_use_c;         /* Експлуатаційна температура, °C */
    double t_stress_c;      /* Температура в камері, °C */
    double n_rh;            /* Показник вологості (напр. 2.7) */
    double ea_ev;           /* Енергія активації (напр. 0.8) */
} PeckParams;

/* Розрахунок коефіцієнта прискорення Арреніуса */
double calc_arrhenius_af(const ArrheniusParams* p) {
    if (!p) return 0.0;
    double t_use_k = p->t_use_c + 273.15;
    double t_stress_k = p->t_stress_c + 273.15;
    if (t_use_k <= 0.0 || t_stress_k <= 0.0) return 0.0;

    double diff = (1.0 / t_use_k) - (1.0 / t_stress_k);
    return exp((p->ea_ev / KB_EV) * diff);
}

/* Розрахунок коефіцієнта прискорення термоциклів Норріса-Ландзберга */
double calc_norris_landzberg_af(const NorrisLandzbergParams* p) {
    if (!p || p->dt_use_c <= 0.0 || p->f_use_cpd <= 0.0) return 0.0;
    
    /* Приведення частот до однакових одиниць (1/добу) */
    double f_stress_cpd = p->f_stress_cph * 24.0;
    
    double t_max_use_k = p->t_max_use_c + 273.15;
    double t_max_stress_k = p->t_max_stress_c + 273.15;

    double term_dt = pow(p->dt_stress_c / p->dt_use_c, p->m_exp);
    double term_f = pow(p->f_use_cpd / f_stress_cpd, p->n_exp);
    double term_t = exp((p->ea_ev / KB_EV) * ((1.0 / t_max_use_k) - (1.0 / t_max_stress_k)));

    return term_dt * term_f * term_t;
}

/* Розрахунок коефіцієнта прискорення вологості Пека */
double calc_peck_af(const PeckParams* p) {
    if (!p || p->rh_use_pct <= 0.0) return 0.0;
    double t_use_k = p->t_use_c + 273.15;
    double t_stress_k = p->t_stress_c + 273.15;

    double term_rh = pow(p->rh_stress_pct / p->rh_use_pct, p->n_rh);
    double term_t = exp((p->ea_ev / KB_EV) * ((1.0 / t_use_k) - (1.0 / t_stress_k)));

    return term_rh * term_t;
}

int main(void) {
    printf("=== Інженерний калькулятор прискорених випробувань ===\n\n");

    /* 1. Температурне старіння: 10 років (87600 год) при 45°C -> тест при 125°C */
    ArrheniusParams arr_p = { .t_use_c = 45.0, .t_stress_c = 125.0, .ea_ev = 0.70 };
    double af_arr = calc_arrhenius_af(&arr_p);
    double test_hours_arr = 87600.0 / af_arr;

    printf("[1] Термічне старіння (Arrhenius):\n");
    printf("    AF = %.2f\n", af_arr);
    printf("    Еквівалент 10 років (87600 год): %.1f год (%.1f діб при 125°C)\n\n",
           test_hours_arr, test_hours_arr / 24.0);

    /* 2. Термоцикли пайки: 10 років (3 цикли/добу, DT=40°C) -> камера DT=165°C, 1 цикл/год */
    NorrisLandzbergParams nl_p = {
        .dt_use_c = 40.0,
        .dt_stress_c = 165.0,
        .f_use_cpd = 3.0,
        .f_stress_cph = 1.0,
        .t_max_use_c = 50.0,
        .t_max_stress_c = 125.0,
        .m_exp = 2.65,
        .n_exp = 0.33,
        .ea_ev = 0.122
    };
    double af_nl = calc_norris_landzberg_af(&nl_p);
    double total_field_cycles = 10.0 * 365.0 * 3.0; /* 10950 циклів */
    double test_cycles_nl = total_field_cycles / af_nl;

    printf("[2] Термомеханічна втома пайки (Norris-Landzberg SAC305):\n");
    printf("    AF = %.2f\n", af_nl);
    printf("    Еквівалент 10 років (%0.f циклів): %.0f циклів у камері (%.1f діб)\n\n",
           total_field_cycles, ceil(test_cycles_nl), (test_cycles_nl / 1.0) / 24.0);

    /* 3. Вологість та HAST: 10 років при 40°C / 60% RH -> автоклав 130°C / 85% RH */
    PeckParams peck_p = {
        .rh_use_pct = 60.0,
        .rh_stress_pct = 85.0,
        .t_use_c = 40.0,
        .t_stress_c = 130.0,
        .n_rh = 2.7,
        .ea_ev = 0.80
    };
    double af_peck = calc_peck_af(&peck_p);
    double test_hours_peck = 87600.0 / af_peck;

    printf("[3] Кліматична деградація та вологість (Peck HAST):\n");
    printf("    AF = %.2f\n", af_peck);
    printf("    Еквівалент 10 років вологи: %.1f год в автоклаві HAST\n", test_hours_peck);

    return 0;
}
