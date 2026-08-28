/* mathieu_solver.c — Чисельний розв'язувач рівняння Матьє мовою C (C99/C11) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double y;
    double v;
} State;

typedef struct {
    double a;
    double q;
    double m11, m12;
    double m21, m22;
    double trace;
    int is_stable;
    double floquet_exponent;
} MathieuResult;

/* Права частина системи диференціальних рівнянь */
static inline State mathieu_rhs(State s, double z, double a, double q) {
    State res;
    res.y = s.v;
    res.v = -(a - 2.0 * q * cos(2.0 * z)) * s.y;
    return res;
}

/* Один крок класичного методу Рунге — Кутти 4-го порядку (RK4) */
static inline State rk4_step(State s, double z, double dz, double a, double q) {
    State k1 = mathieu_rhs(s, z, a, q);
    
    State s_k2 = { s.y + 0.5 * dz * k1.y, s.v + 0.5 * dz * k1.v };
    State k2 = mathieu_rhs(s_k2, z + 0.5 * dz, a, q);
    
    State s_k3 = { s.y + 0.5 * dz * k2.y, s.v + 0.5 * dz * k2.v };
    State k3 = mathieu_rhs(s_k3, z + 0.5 * dz, a, q);
    
    State s_k4 = { s.y + dz * k3.y, s.v + dz * k3.v };
    State k4 = mathieu_rhs(s_k4, z + dz, a, q);
    
    State next_state;
    next_state.y = s.y + (dz / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
    next_state.v = s.v + (dz / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.y);
    return next_state;
}

/* Інтегрування траєкторії від z = 0 до z = pi */
static State integrate_period(State init_state, double a, double q, int steps) {
    double dz = M_PI / (double)steps;
    State curr = init_state;
    double z = 0.0;
    for (int i = 0; i < steps; ++i) {
        curr = rk4_step(curr, z, dz, a, q);
        z += dz;
    }
    return curr;
}

/* Аналіз стійкості точки (q, a) через матрицю монодромії */
MathieuResult analyze_mathieu_point(double a, double q, int steps) {
    State s1_init = { 1.0, 0.0 };
    State s2_init = { 0.0, 1.0 };
    
    State s1_final = integrate_period(s1_init, a, q, steps);
    State s2_final = integrate_period(s2_init, a, q, steps);
    
    MathieuResult res;
    res.a = a;
    res.q = q;
    res.m11 = s1_final.y; res.m12 = s2_final.y;
    res.m21 = s1_final.v; res.m22 = s2_final.v;
    res.trace = res.m11 + res.m22;
    
    double half_trace = res.trace / 2.0;
    if (fabs(half_trace) <= 1.000000001) {
        res.is_stable = 1;
        res.floquet_exponent = 0.0;
    } else {
        res.is_stable = 0;
        res.floquet_exponent = (1.0 / M_PI) * acosh(fabs(half_trace));
    }
    return res;
}

int main(void) {
    printf("Обчислення матриці монодромії та аналіз стійкості рівняння Матьє:\n");
    printf("------------------------------------------------------------------\n");
    
    double test_points[4][2] = {
        { 0.2, 0.1 },  /* Стійка область */
        { 1.0, 0.4 },  /* Нестійка область (головний язик n=1) */
        { 4.0, 0.5 },  /* Стійка область між язиками */
        { 4.0, 1.2 }   /* Другий язик нестійкості n=2 */
    };
    
    for (int i = 0; i < 4; ++i) {
        double a = test_points[i][0];
        double q = test_points[i][1];
        MathieuResult r = analyze_mathieu_point(a, q, 1000);
        printf("Точка (q=%.2f, a=%.2f): Tr(M)=%8.5f | %s | μ = %.5f\n",
               r.q, r.a, r.trace, r.is_stable ? "СТІЙКА   " : "НЕСТІЙКА ", r.floquet_exponent);
    }
    return 0;
}
