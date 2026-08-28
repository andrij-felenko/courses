#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double v;
} State2D;

typedef struct {
    double t;
    double x_exact;
    double x_bm1;
    double x_bm2;
    double err_bm1;
    double err_bm2;
} SimResult;

/* Праві частини вихідної системи осцилятора Ван дер Поля */
static inline State2D vdp_derivatives(State2D s, double eps) {
    State2D d;
    d.x = s.v;
    d.v = -s.x + eps * (1.0 - s.x * s.x) * s.v;
    return d;
}

/* Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
static State2D rk4_step(State2D s, double eps, double h) {
    State2D k1 = vdp_derivatives(s, eps);
    
    State2D s_k2 = {s.x + 0.5 * h * k1.x, s.v + 0.5 * h * k1.v};
    State2D k2 = vdp_derivatives(s_k2, eps);
    
    State2D s_k3 = {s.x + 0.5 * h * k2.x, s.v + 0.5 * h * k2.v};
    State2D k3 = vdp_derivatives(s_k3, eps);
    
    State2D s_k4 = {s.x + h * k3.x, s.v + h * k3.v};
    State2D k4 = vdp_derivatives(s_k4, eps);
    
    State2D next_s;
    next_s.x = s.x + (h / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    next_s.v = s.v + (h / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v);
    return next_s;
}

/* Аналітичний розв'язок першого наближення БМ для Ван дер Поля */
static void bm1_solution(double a0, double psi0, double eps, double t, double *out_x, double *out_a) {
    /* Точний розв'язок усередненого рівняння амплітуди da/dt = (eps/2)*a*(1 - a^2/4) */
    double exp_t = exp(eps * t);
    double a_t = 2.0 * a0 / sqrt(a0 * a0 + (4.0 - a0 * a0) * exp(-eps * t));
    double psi_t = psi0; /* B1(a) = 0 */
    
    *out_a = a_t;
    *out_x = a_t * cos(t + psi_t);
}

/* Аналітичний розв'язок второго наближення БМ для Ван дер Поля */
static void bm2_solution(double a0, double psi0, double eps, double t, double *out_x) {
    double a_t = 2.0 * a0 / sqrt(a0 * a0 + (4.0 - a0 * a0) * exp(-eps * t));
    /* Зсув частоти другого порядку B2(2) = -1/16 */
    double psi_t = psi0 - (eps * eps / 16.0) * t;
    double theta = t + psi_t;
    
    /* Перша осцилююча поправка u1(a, theta) = - (a^3 / 32) * sin(3*theta) */
    double u1 = - (pow(a_t, 3.0) / 32.0) * sin(3.0 * theta);
    
    *out_x = a_t * cos(theta) + eps * u1;
}

int main(void) {
    double eps = 0.1;
    double t_max = 100.0;
    double h = 0.01;
    size_t n_steps = (size_t)(t_max / h);
    
    State2D state = {1.0, 0.0}; /* x(0) = 1, v(0) = 0 */
    double a0 = 1.0;
    double psi0 = 0.0;
    
    SimResult *results = (SimResult *)malloc(n_steps * sizeof(SimResult));
    if (!results) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }
    
    double max_err1 = 0.0;
    double max_err2 = 0.0;
    
    for (size_t i = 0; i < n_steps; ++i) {
        double t = i * h;
        double x_bm1, a_bm1, x_bm2;
        
        bm1_solution(a0, psi0, eps, t, &x_bm1, &a_bm1);
        bm2_solution(a0, psi0, eps, t, &x_bm2);
        
        double err1 = fabs(state.x - x_bm1);
        double err2 = fabs(state.x - x_bm2);
        
        if (err1 > max_err1) max_err1 = err1;
        if (err2 > max_err2) max_err2 = err2;
        
        results[i].t = t;
        results[i].x_exact = state.x;
        results[i].x_bm1 = x_bm1;
        results[i].x_bm2 = x_bm2;
        results[i].err_bm1 = err1;
        results[i].err_bm2 = err2;
        
        state = rk4_step(state, eps, h);
    }
    
    printf("=== Результати порівняння для eps = %.3f ===\n", eps);
    printf("Максимальна похибка BM-1 (O(eps)):   %.6f\n", max_err1);
    printf("Максимальна похибка BM-2 (O(eps^2)): %.6f\n", max_err2);
    printf("Коефіцієнт покращення точності:       %.2fx\n", max_err1 / max_err2);
    
    free(results);
    return 0;
}
