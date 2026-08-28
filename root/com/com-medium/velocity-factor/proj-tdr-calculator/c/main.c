#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define C_VACUUM_MM_PS 0.299792458  /* швидкість світла в мм/пс */

typedef struct {
    double velocity_factor;  /* коефіцієнт укорочення (0.0..1.0) */
    double delta_t_ps;        /* час двостороннього пробігу імпульсу в пс */
} TdrInput;

typedef struct {
    double distance_mm;      /* обчислена відстань до пошкодження в мм */
    double propagation_delay;/* погонна затримка в пс/мм */
    bool is_valid;           /* прапорець коректності вхідних даних */
} TdrResult;

typedef struct {
    double length_diff_mm;   /* необхідна компенсаційна довжина меандру в мм */
    double time_skew_ps;     /* часовий зсув сигналів у пс */
} SkewResult;

/* Обчислення відстані до пошкодження методом TDR */
TdrResult calculate_tdr_fault(TdrInput input) {
    TdrResult res = {0.0, 0.0, false};
    if (input.velocity_factor <= 0.0 || input.velocity_factor > 1.0 || input.delta_t_ps < 0.0) {
        return res;
    }

    double v_signal = C_VACUUM_MM_PS * input.velocity_factor; /* швидкість у мм/пс */
    res.distance_mm = (v_signal * input.delta_t_ps) / 2.0;    /* двосторонній шлях */
    res.propagation_delay = 1.0 / v_signal;                   /* пс/мм */
    res.is_valid = true;
    return res;
}

/* Обчислення довжини компенсаційного меандру для вирівнювання трас */
SkewResult calculate_trace_skew(double len1_mm, double len2_mm, double vf) {
    SkewResult res = {0.0, 0.0};
    if (vf <= 0.0 || vf > 1.0) return res;

    double v_signal = C_VACUUM_MM_PS * vf;
    double t_pd = 1.0 / v_signal; /* пс/мм */

    double t1 = len1_mm * t_pd;
    double t2 = len2_mm * t_pd;

    res.time_skew_ps = fabs(t1 - t2);
    res.length_diff_mm = fabs(len1_mm - len2_mm);
    return res;
}

int main(void) {
    /* Приклад 1: Вимірювання кабелю RG-58 (VF = 0.66) за допомогою TDR */
    TdrInput cable_test = { .velocity_factor = 0.66, .delta_t_ps = 101010.0 }; /* 101.01 нс */
    TdrResult tdr_res = calculate_tdr_fault(cable_test);

    if (tdr_res.is_valid) {
        printf("--- TDR Рефлектометрія (C) ---\n");
        printf("Відстань до обриву: %.2f мм (%.3f м)\n", tdr_res.distance_mm, tdr_res.distance_mm / 1000.0);
        printf("Погонна затримка:   %.3f пс/мм (%.2f нс/м)\n", tdr_res.propagation_delay, tdr_res.propagation_delay);
    }

    /* Приклад 2: Вирівнювання трас шини DDR4 на платі FR-4 (VF = 0.55) */
    SkewResult skew = calculate_trace_skew(120.0, 135.0, 0.55);
    printf("\n--- Вирівнювання трас PCB (C) ---\n");
    printf("Часовий зсув сигналів: %.2f пс\n", skew.time_skew_ps);
    printf("Додати меандр довжиною:  %.2f мм\n", skew.length_diff_mm);

    return 0;
}
