/* simulation_cuk.c — Числова симуляція перетворювача Cuk методом RK4 */
#include <stdio.h>
#include <math.h>

typedef struct {
    double Vin;      /* Вхідна напруга, В */
    double R_load;   /* Опір навантаження, Ом */
    double f_sw;     /* Частота комутації, Гц */
    double D;        /* Коефіцієнт заповнення [0..1] */
    double L1;       /* Вхідна індуктивність, Гн */
    double L2;       /* Вихідна індуктивність, Гн */
    double k_mag;    /* Коефіцієнт магнітного зв'язку [0..1) */
    double C1;       /* Передавальний конденсатор, Ф */
    double Cout;     /* Вихідний конденсатор, Ф */
    double Ron;      /* Опір ключа Q1, Ом */
    double V_diode;  /* Пряме падіння на діоді D1, В */
} CukParams;

typedef struct {
    double i1;       /* Струм L1, А */
    double i2;       /* Струм L2, А */
    double v1;       /* Напруга C1, В */
    double v2;       /* Напруга Cout (|Vвих|), В */
} CukState;

/* Обчислення похідних вектора стану */
static void get_derivatives(const CukParams *p, const CukState *s, double t, CukState *deriv) {
    double T = 1.0 / p->f_sw;
    double t_phase = fmod(t, T);
    int q1_on = (t_phase < p->D * T);

    double v_L1_applied, v_L2_applied;
    double i_C1;

    if (q1_on) {
        /* Фаза 1: Q1 замкнений на землю, D1 закритий */
        v_L1_applied = p->Vin - s->i1 * p->Ron;
        v_L2_applied = -s->v1 + s->v2;
        i_C1 = -s->i2;
    } else {
        /* Фаза 2: Q1 розімкнений, D1 відкритий */
        v_L1_applied = p->Vin - s->v1 + p->V_diode;
        v_L2_applied = s->v2 - p->V_diode;
        i_C1 = s->i1;
    }

    /* Матриця магнітного зв'язку */
    double M = p->k_mag * sqrt(p->L1 * p->L2);
    double detL = p->L1 * p->L2 - M * M;

    deriv->i1 = (p->L2 * v_L1_applied - M * v_L2_applied) / detL;
    deriv->i2 = (p->L1 * v_L2_applied - M * v_L1_applied) / detL;
    deriv->v1 = i_C1 / p->C1;
    deriv->v2 = (s->i2 - s->v2 / p->R_load) / p->Cout;
}

/* Крок інтегрування Рунге-Кутти 4-го порядку */
static void rk4_step(const CukParams *p, CukState *s, double t, double dt) {
    CukState k1, k2, k3, k4, temp;

    get_derivatives(p, s, t, &k1);

    temp.i1 = s->i1 + 0.5 * dt * k1.i1;
    temp.i2 = s->i2 + 0.5 * dt * k1.i2;
    temp.v1 = s->v1 + 0.5 * dt * k1.v1;
    temp.v2 = s->v2 + 0.5 * dt * k1.v2;
    get_derivatives(p, &temp, t + 0.5 * dt, &k2);

    temp.i1 = s->i1 + 0.5 * dt * k2.i1;
    temp.i2 = s->i2 + 0.5 * dt * k2.i2;
    temp.v1 = s->v1 + 0.5 * dt * k2.v1;
    temp.v2 = s->v2 + 0.5 * dt * k2.v2;
    get_derivatives(p, &temp, t + 0.5 * dt, &k3);

    temp.i1 = s->i1 + dt * k3.i1;
    temp.i2 = s->i2 + dt * k3.i2;
    temp.v1 = s->v1 + dt * k3.v1;
    temp.v2 = s->v2 + dt * k3.v2;
    get_derivatives(p, &temp, t + dt, &k4);

    s->i1 += (dt / 6.0) * (k1.i1 + 2.0 * k2.i1 + 2.0 * k3.i1 + k4.i1);
    s->i2 += (dt / 6.0) * (k1.i2 + 2.0 * k2.i2 + 2.0 * k3.i2 + k4.i2);
    s->v1 += (dt / 6.0) * (k1.v1 + 2.0 * k2.v1 + 2.0 * k3.v1 + k4.v1);
    s->v2 += (dt / 6.0) * (k1.v2 + 2.0 * k2.v2 + 2.0 * k3.v2 + k4.v2);
}

int main(void) {
    CukParams cfg = {
        .Vin = 24.0, .R_load = 10.0, .f_sw = 200000.0, .D = 0.3846,
        .L1 = 220e-6, .L2 = 150e-6, .k_mag = 0.88,
        .C1 = 9.4e-6, .Cout = 91e-6,
        .Ron = 0.020, .V_diode = 0.45
    };

    CukState state = { .i1 = 0.0, .i2 = 0.0, .v1 = 0.0, .v2 = 0.0 };

    double dt = 2.5e-8;  /* Крок інтегрування 25 нс */
    double t_end = 0.005; /* 5 мс симуляції */

    printf("# Симуляція перетворювача Cuk (Зв'язані індуктивності k=%.2f)\n", cfg.k_mag);
    printf("# Час(мс)   I_in(A)    I_out(A)   V_C1(V)    V_out(V)\n");

    int print_decimation = 2000;
    int step_count = 0;

    for (double t = 0.0; t < t_end; t += dt, step_count++) {
        rk4_step(&cfg, &state, t, dt);

        if (step_count % print_decimation == 0) {
            printf("%8.3f   %8.4f   %8.4f   %8.3f   %8.3f\n",
                   t * 1000.0, state.i1, state.i2, state.v1, -state.v2);
        }
    }

    printf("\n# Усталений стан на t = %.2f мс:\n", t_end * 1000.0);
    printf("V_out = %.3f В (Ціль: -15.0 В)\n", -state.v2);
    printf("I_in  = %.3f А, I_out = %.3f А\n", state.i1, state.i2);
    printf("V_C1  = %.3f В (Теорія: %.3f В)\n", state.v1, cfg.Vin + state.v2);

    return 0;
}
