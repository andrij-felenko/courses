#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double Ms;       /* Намагніченість насичення FM (emu/cm³) */
    double t_FM;     /* Товщина FM шару (см) */
    double K_FM;     /* Анізотропія FM (erg/cm³) */
    double J_EB;     /* Обмінна енергія інтерфейсу (erg/cm²) */
    double phi_AFM;  /* Кут спінів AFM (радіани) */
    double psi;      /* Кут поля (радіани) */
} MagneticParams;

typedef struct {
    double H_ext;    /* Поле (Ое) */
    double M_proj;   /* Відносна намагніченість M / Ms */
    double theta;    /* Рівноважний кут (рад) */
} Point;

/* Обчислення повної енергії одиниці площі */
static double calc_energy(double theta, double H_ext, const MagneticParams* p) {
    double e_z = -H_ext * p->Ms * p->t_FM * cos(theta - p->psi);
    double e_k = p->K_FM * p->t_FM * sin(theta) * sin(theta);
    double e_ex = -p->J_EB * cos(theta - p->phi_AFM);
    return e_z + e_k + e_ex;
}

/* Пошук локального мінімуму енергії */
static double find_min_theta(double H_ext, double init_theta, const MagneticParams* p) {
    double best_t = init_theta;
    double min_e = calc_energy(init_theta, H_ext, p);
    int i;

    for (i = -90; i <= 90; i++) {
        double t = init_theta + (i * M_PI / 180.0);
        while (t < 0.0) t += 2.0 * M_PI;
        while (t >= 2.0 * M_PI) t -= 2.0 * M_PI;

        double e = calc_energy(t, H_ext, p);
        if (e < min_e) {
            min_e = e;
            best_t = t;
        }
    }
    return best_t;
}

int main(void) {
    MagneticParams p = {800.0, 5.0e-7, 1.0e4, 0.15, 0.0, 0.0};
    double h_max = 800.0;
    int steps = 80;
    int total_pts = (steps + 1) * 2;
    int i, idx = 0;

    Point* loop = (Point*)malloc(sizeof(Point) * (size_t)total_pts);
    if (!loop) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    double h_eb_theory = p.J_EB / (p.Ms * p.t_FM);
    printf("Теоретичне поле зміщення H_EB = %.2f Oe\n\n", h_eb_theory);

    double cur_t = p.psi;
    double dh = (2.0 * h_max) / steps;

    /* Зворотний хід: +H_max -> -H_max */
    for (i = 0; i <= steps; i++) {
        double h = h_max - i * dh;
        cur_t = find_min_theta(h, cur_t, &p);
        loop[idx].H_ext = h;
        loop[idx].M_proj = cos(cur_t - p.psi);
        loop[idx].theta = cur_t;
        idx++;
    }

    /* Прямий хід: -H_max -> +H_max */
    for (i = 0; i <= steps; i++) {
        double h = -h_max + i * dh;
        cur_t = find_min_theta(h, cur_t, &p);
        loop[idx].H_ext = h;
        loop[idx].M_proj = cos(cur_t - p.psi);
        loop[idx].theta = cur_t;
        idx++;
    }

    printf("--- Таблиця результатів симуляції (перші 10 точок) ---\n");
    printf("  H (Oe)    |   M / Ms   |   Theta (град)\n");
    printf("------------+------------+----------------\n");
    for (i = 0; i < 10; i++) {
        printf("%9.2f   |   %8.2f |   %9.2f\n", 
               loop[i].H_ext, loop[i].M_proj, loop[i].theta * 180.0 / M_PI);
    }

    free(loop);
    return 0;
}
