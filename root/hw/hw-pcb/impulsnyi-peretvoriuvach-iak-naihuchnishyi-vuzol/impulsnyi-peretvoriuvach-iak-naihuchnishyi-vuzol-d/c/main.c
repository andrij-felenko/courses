#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double f1_hz;         /* Початкова частота дзвону без снубера */
    double f2_hz;         /* Зміщена частота з тестовим конденсатором */
    double c_test_f;      /* Ємність тестового конденсатора (Ф) */
    double v_in_volts;    /* Вхідна напруга живлення (В) */
    double f_sw_hz;       /* Робоча частота перемикання DC-DC (Гц) */
} RingingMeasureInput;

typedef struct {
    double c_par_f;       /* Розрахована паразитна ємність (Ф) */
    double l_par_h;       /* Розрахована паразитна індуктивність (Гн) */
    double z0_ohms;       /* Характеристичний імпеданс контуру (Ом) */
    double r_snub_ohms;   /* Рекомендований опір снубера (Ом) */
    double c_snub_f;      /* Рекомендована ємність снубера (Ф) */
    double p_loss_watts;  /* Розсіювана теплова потужність на резисторі (Вт) */
    bool is_valid;
} SnubberResult;

SnubberResult calculate_snubber(const RingingMeasureInput* in) {
    SnubberResult res = {0};
    if (!in || in->f1_hz <= 0.0 || in->f2_hz <= 0.0 || in->c_test_f <= 0.0 || in->f2_hz >= in->f1_hz) {
        res.is_valid = false;
        return res;
    }

    /* Розрахунок паразитної ємності: C_par = C_test / ((f1 / f2)^2 - 1) */
    double ratio = in->f1_hz / in->f2_hz;
    res.c_par_f = in->c_test_f / (ratio * ratio - 1.0);

    /* Розрахунок паразитної індуктивності: L_par = 1 / ((2 * pi * f1)^2 * C_par) */
    double omega1 = 2.0 * PI * in->f1_hz;
    res.l_par_h = 1.0 / (omega1 * omega1 * res.c_par_f);

    /* Характеристичний імпеданс: Z0 = sqrt(L_par / C_par) */
    res.z0_ohms = sqrt(res.l_par_h / res.c_par_f);

    /* Оптимальні номінали снубера */
    res.r_snub_ohms = res.z0_ohms;
    res.c_snub_f = 3.0 * res.c_par_f;

    /* Теплові втрати: P = C_snub * V_in^2 * f_sw */
    res.p_loss_watts = res.c_snub_f * (in->v_in_volts * in->v_in_volts) * in->f_sw_hz;
    res.is_valid = true;

    return res;
}

int main(void) {
    RingingMeasureInput meas = {
        .f1_hz = 180.0e6,     /* 180 МГц початковий дзвін */
        .f2_hz = 115.0e6,     /* 115 МГц після додавання 470 пФ */
        .c_test_f = 470.0e-12,
        .v_in_volts = 24.0,
        .f_sw_hz = 500.0e3    /* 500 кГц комутація */
    };

    SnubberResult r = calculate_snubber(&meas);
    if (r.is_valid) {
        printf("--- Параметри паразитного контуру ---\n");
        printf("Паразитна ємність C_par:     %.2f пФ\n", r.c_par_f * 1e12);
        printf("Паразитна індуктивність L_par: %.2f нГн\n", r.l_par_h * 1e9);
        printf("Характеристичний опір Z0:    %.2f Ом\n", r.z0_ohms);
        printf("\n--- Розраховані номінали снубера ---\n");
        printf("Резистор R_snub:              %.2f Ом (вибираємо найближчий ряду E24)\n", r.r_snub_ohms);
        printf("Конденсатор C_snub:           %.2f пФ (клас C0G/NP0)\n", r.c_snub_f * 1e12);
        printf("Теплові втрати на резисторі:  %.3f Вт\n", r.p_loss_watts);
    }
    return 0;
}
