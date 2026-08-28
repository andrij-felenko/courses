#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура коефіцієнтів 2D системи */
typedef struct {
    double gamma;   /* Коефіцієнт згасання стійкої моди (gamma > 0) */
    double f20, f11, f02, f30; /* Нелінійності dx/dt */
    double g20, g11, g02;      /* Нелінійності dy/dt */
} cm_system_2d_t;

/* Структура обчисленого центрального многовиду y = h(x) = h2*x^2 + h3*x^3 */
typedef struct {
    double h2;
    double h3;
} cm_manifold_2d_t;

/* Обчислення коефіцієнтів центрального многовиду */
cm_manifold_2d_t cm_compute_manifold(const cm_system_2d_t *sys) {
    cm_manifold_2d_t res;
    if (sys->gamma <= 0.0) {
        fprintf(stderr, "Помилка: gamma повинна бути строго додатною!\n");
        res.h2 = 0.0;
        res.h3 = 0.0;
        return res;
    }
    
    /* Обчислення коефіцієнта при x^2: h2 = g20 / gamma */
    res.h2 = sys->g20 / sys->gamma;
    
    /* Обчислення коефіцієнта при x^3: враховуємо перехресні нелінійності */
    res.h3 = (sys->g11 * res.h2 + 2.0 * res.h2 * sys->f20) / sys->gamma;
    
    return res;
}

/* Обчислення значення h(x) */
double cm_eval_h(const cm_manifold_2d_t *mf, double x) {
    return mf->h2 * x * x + mf->h3 * x * x * x;
}

/* Права частина повної 2D системи */
void cm_full_rhs(const cm_system_2d_t *sys, double x, double y, double *dxdt, double *dydt) {
    *dxdt = sys->f20 * x * x + sys->f11 * x * y + sys->f02 * y * y + sys->f30 * x * x * x;
    *dydt = -sys->gamma * y + sys->g20 * x * x + sys->g11 * x * y + sys->g02 * y * y;
}

/* Права частина редукованої 1D системи на W^c */
double cm_reduced_rhs(const cm_system_2d_t *sys, const cm_manifold_2d_t *mf, double x) {
    double y_h = cm_eval_h(mf, x);
    return sys->f20 * x * x + sys->f11 * x * y_h + sys->f02 * y_h * y_h + sys->f30 * x * x * x;
}

/* Крок інтегрування RK4 для повної системи */
void cm_step_full_rk4(const cm_system_2d_t *sys, double *x, double *y, double dt) {
    double k1x, k1y, k2x, k2y, k3x, k3y, k4x, k4y;
    
    cm_full_rhs(sys, *x, *y, &k1x, &k1y);
    cm_full_rhs(sys, *x + 0.5 * dt * k1x, *y + 0.5 * dt * k1y, &k2x, &k2y);
    cm_full_rhs(sys, *x + 0.5 * dt * k2x, *y + 0.5 * dt * k2y, &k3x, &k3y);
    cm_full_rhs(sys, *x + dt * k3x, *y + dt * k3y, &k4x, &k4y);
    
    *x += (dt / 6.0) * (k1x + 2.0 * k2x + 2.0 * k3x + k4x);
    *y += (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y);
}

/* Крок інтегрування RK4 для редукованої системи */
void cm_step_reduced_rk4(const cm_system_2d_t *sys, const cm_manifold_2d_t *mf, double *x, double dt) {
    double k1 = cm_reduced_rhs(sys, mf, *x);
    double k2 = cm_reduced_rhs(sys, mf, *x + 0.5 * dt * k1);
    double k3 = cm_reduced_rhs(sys, mf, *x + 0.5 * dt * k2);
    double k4 = cm_reduced_rhs(sys, mf, *x + dt * k3);
    
    *x += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
}

int main(void) {
    cm_system_2d_t sys = {
        .gamma = 10.0, /* Сильне згасання */
        .f20 = 0.5, .f11 = 1.0, .f02 = -0.2, .f30 = -1.2,
        .g20 = 2.0, .g11 = -0.5, .g02 = 0.1
    };
    
    cm_manifold_2d_t mf = cm_compute_manifold(&sys);
    printf("=== Обчислення центрального многовиду ===\n");
    printf("h2 (коефіцієнт при x^2): %f\n", mf.h2);
    printf("h3 (коефіцієнт при x^3): %f\n\n", mf.h3);
    
    /* Початкові умови */
    double x_full = 0.4, y_full = 0.8; /* y далі від багатовиду */
    double x_red = 0.4;
    double t = 0.0;
    double dt = 0.01;
    int steps = 100;
    
    printf("t\t\tx_full\t\ty_full\t\tx_red\t\ty_h(x_red)\tабс. похибка\n");
    printf("----------------------------------------------------------------------------------\n");
    
    for (int i = 0; i <= steps; i++) {
        double y_h = cm_eval_h(&mf, x_red);
        double err = fabs(x_full - x_red);
        
        if (i % 10 == 0) {
            printf("%.2f\t\t%.6f\t%.6f\t%.6f\t%.6f\t%.6e\n", t, x_full, y_full, x_red, y_h, err);
        }
        
        cm_step_full_rk4(&sys, &x_full, &y_full, dt);
        cm_step_reduced_rk4(&sys, &mf, &x_red, dt);
        t += dt;
    }
    
    return 0;
}
