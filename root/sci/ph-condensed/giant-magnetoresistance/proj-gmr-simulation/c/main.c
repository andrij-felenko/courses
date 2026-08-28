#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура фізичних параметрів спинового клапана GMR */
typedef struct {
    double r_p;     /* Опір паралельного стану (Ом) */
    double r_ap;    /* Опір антипаралельного стану (Ом) */
    double h_c;     /* Коерцитивна сила вільного шару (мТл) */
    double h_ex;    /* Поле обмінного зсуву закріпленого шару (мТл) */
} gmr_sim_t;

/* Структура результату розрахунку для однієї точки поля */
typedef struct {
    double h_field;
    double theta_free;
    double resistance;
    int is_sweep_up;
} gmr_point_t;

/* Ініціалізація симулятора */
gmr_sim_t gmr_init(double r_p, double gmr_ratio, double h_c, double h_ex) {
    gmr_sim_t sim;
    sim.r_p = r_p;
    sim.r_ap = r_p * (1.0 + gmr_ratio);
    sim.h_c = h_c;
    sim.h_ex = h_ex;
    return sim;
}

/* Обчислення кута намагніченості вільного шару */
double gmr_calc_free_angle(const gmr_sim_t* sim, double h_field, int is_sweep_up) {
    if (is_sweep_up) {
        if (h_field < -sim->h_c) return M_PI;
        if (h_field > sim->h_c) return 0.0;
        return M_PI;
    } else {
        if (h_field > sim->h_c) return 0.0;
        if (h_field < -sim->h_c) return M_PI;
        return 0.0;
    }
}

/* Обчислення кута закріпленого шару під дією exchange bias */
double gmr_calc_pinned_angle(const gmr_sim_t* sim, double h_field) {
    return (h_field > -sim->h_ex) ? 0.0 : M_PI;
}

/* Обчислення електричного опору за формулою Мотта */
double gmr_calc_resistance(const gmr_sim_t* sim, double t_free, double t_pinned) {
    double cos_angle = cos(t_free - t_pinned);
    return sim->r_p + 0.5 * (sim->r_ap - sim->r_p) * (1.0 - cos_angle);
}

int main(void) {
    gmr_sim_t sim = gmr_init(100.0, 0.10, 0.8, 20.0);
    double h_min = -30.0;
    double h_max = 30.0;
    int steps = 10;
    double step_size = (h_max - h_min) / steps;

    printf(" H (mT) | theta_free (rad) | R (Ohm)\n");
    printf("------------------------------------\n");

    for (int i = 0; i <= steps; ++i) {
        double h = h_min + i * step_size;
        double tf = gmr_calc_free_angle(&sim, h, 1);
        double tp = gmr_calc_pinned_angle(&sim, h);
        double r = gmr_calc_resistance(&sim, tf, tp);
        printf("%7.2f | %16.3f | %7.2f\n", h, tf, r);
    }

    return 0;
}
