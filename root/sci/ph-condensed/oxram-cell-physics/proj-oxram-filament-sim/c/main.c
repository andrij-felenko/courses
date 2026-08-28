#include <stdio.h>
#include <math.h>

#define STEPS 400

typedef struct {
    double x_gap;      /* Товщина оксидного зазору (м) */
    double R_on;       /* Опір філамента в LRS (Ом) */
    double E_a;        /* Енергія активації міграції (Дж) */
    double a_lattice;  /* Постійна ґратки (м) */
    double I_comp;     /* Струм обмеження (А) */
} OxRamCell;

void oxram_init(OxRamCell *cell) {
    cell->x_gap = 1.2e-9;
    cell->R_on = 1000.0;
    cell->E_a = 0.85 * 1.602e-19;
    cell->a_lattice = 0.3e-9;
    cell->I_comp = 1e-4;
}

double oxram_step(OxRamCell *cell, double V_app, double dt) {
    const double q = 1.602e-19;
    const double kB = 1.38e-23;
    const double L_W = 2.44e-8;
    const double T0 = 300.0;
    const double v0 = 1e4;

    /* Опір тунельного зазору */
    double R_gap = cell->R_on * exp(10.25e9 * cell->x_gap);
    double R_total = cell->R_on + R_gap;

    double I_cell = V_app / R_total;
    if (fabs(I_cell) > cell->I_comp) {
        I_cell = (I_cell > 0) ? cell->I_comp : -cell->I_comp;
    }

    double V_gap = I_cell * R_gap;
    double E_gap = fabs(V_gap) / (cell->x_gap > 1e-10 ? cell->x_gap : 1e-10);

    /* Локальна температура Кольрауша */
    double T_max = sqrt(T0 * T0 + (V_gap * V_gap) / (4.0 * L_W));

    double arg = (q * cell->a_lattice * E_gap) / (2.0 * kB * T_max);
    if (arg > 50.0) arg = 50.0;

    double v_drift = 2.0 * cell->a_lattice * v0 * exp(-cell->E_a / (kB * T_max)) * sinh(arg);
    double dx_dt = (V_app > 0) ? -v_drift : v_drift * 0.1;

    cell->x_gap += dx_dt * dt;
    if (cell->x_gap < 0.0) cell->x_gap = 0.0;
    if (cell->x_gap > 2.0e-9) cell->x_gap = 2.0e-9;

    return I_cell;
}

int main(void) {
    OxRamCell cell;
    oxram_init(&cell);

    double dt = 1e-6;
    double v_max = 2.0;
    
    printf("Крок | Напруга (В) | Струм (мкА) | Зазор x_gap (нм)\n");
    printf("--------------------------------------------------\n");

    for (int i = 0; i <= 20; i++) {
        double V_app = (i / 20.0) * v_max;
        double I_cell = oxram_step(&cell, V_app, dt);
        printf("%4d | %11.3f | %11.3f | %16.3f\n", 
               i, V_app, I_cell * 1e6, cell->x_gap * 1e9);
    }
    return 0;
}
