/* simulation_zeta.c — Числова симуляція Zeta-перетворювача методом RK4 */
#include <stdio.h>
#include <math.h>

typedef struct {
    double Vin;       /* Вхідна напруга живлення, В */
    double R_load;    /* Опір навантаження, Ом */
    double f_sw;      /* Частота комутації, Гц */
    double D;         /* Коефіцієнт заповнення ШІМ [0..1] */
    double L1;        /* Вхідна індуктивність, Гн */
    double L2;        /* Вихідна індуктивність, Гн */
    double k_mag;     /* Коефіцієнт магнітного зв'язку [0..1) */
    double Cc;        /* Розділовий конденсатор, Ф */
    double Cout;      /* Вихідний фільтруючий конденсатор, Ф */
    double Ron;       /* Опір відкритого каналу Q1, Ом */
    double V_diode;   /* Пряме падіння на діоді D1, В */
} ZetaParams;

typedef struct {
    double i1;        /* Струм індуктивності L1, А */
    double i2;        /* Струм вихідної індуктивності L2, А */
    double v_cc;      /* Напруга на розділовому конденсаторі Cc, В */
    double v_out;     /* Вихідна напруга Vвих, В */
} ZetaState;

/* Обчислення похідних вектора стану системи */
static void get_derivatives(const ZetaParams *p, const ZetaState *s, double t, ZetaState *deriv) {
    double T = 1.0 / p->f_sw;
    double t_phase = fmod(t, T);
    int q1_on = (t_phase < p->D * T);

    double v_L1_applied, v_L2_applied;
    double i_Cc;

    if (q1_on) {
        /* Фаза 1: Q1 замкнений, D1 закритий */
        double v_sw1 = p->Vin - (s->i1 + s->i2) * p->Ron;
        double v_sw2 = v_sw1 + s->v_cc;
        v_L1_applied = v_sw1;
        v_L2_applied = v_sw2 - s->v_out;
        i_Cc = -s->i2;
    } else {
        /* Фаза 2: Q1 розімкнений, D1 відкритий */
        double v_sw2 = -p->V_diode;
        double v_sw1 = v_sw2 - s->v_cc;
        v_L1_applied = v_sw1;
        v_L2_applied = v_sw2 - s->v_out;
        i_Cc = s->i1;
    }

    /* Врахування матриці взаємоіндукції */
    double M = p->k_mag * sqrt(p->L1 * p->L2);
    double detL = p->L1 * p->L2 - M * M;

    deriv->i1 = (p->L2 * v_L1_applied - M * v_L2_applied) / detL;
    deriv->i2 = (p->L1 * v_L2_applied - M * v_L1_applied) / detL;
    deriv->v_cc = i_Cc / p->Cc;
    deriv->v_out = (s->i2 - s->v_out / p->R_load) / p->Cout;
}

/* Крок інтегрування методом Рунге-Кутти 4-го порядку */
static void rk4_step(const ZetaParams *p, ZetaState *s, double t, double dt) {
    ZetaState k1, k2, k3, k4, temp;

    get_derivatives(p, s, t, &k1);

    temp.i1 = s->i1 + 0.5 * dt * k1.i1;
    temp.i2 = s->i2 + 0.5 * dt * k1.i2;
    temp.v_cc = s->v_cc + 0.5 * dt * k1.v_cc;
    temp.v_out = s->v_out + 0.5 * dt * k1.v_out;
    get_derivatives(p, &temp, t + 0.5 * dt, &k2);

    temp.i1 = s->i1 + 0.5 * dt * k2.i1;
    temp.i2 = s->i2 + 0.5 * dt * k2.i2;
    temp.v_cc = s->v_cc + 0.5 * dt * k2.v_cc;
    temp.v_out = s->v_out + 0.5 * dt * k2.v_out;
    get_derivatives(p, &temp, t + 0.5 * dt, &k3);

    temp.i1 = s->i1 + dt * k3.i1;
    temp.i2 = s->i2 + dt * k3.i2;
    temp.v_cc = s->v_cc + dt * k3.v_cc;
    temp.v_out = s->v_out + dt * k3.v_out;
    get_derivatives(p, &temp, t + dt, &k4);

    s->i1 += (dt / 6.0) * (k1.i1 + 2.0 * k2.i1 + 2.0 * k3.i1 + k4.i1);
    s->i2 += (dt / 6.0) * (k1.i2 + 2.0 * k2.i2 + 2.0 * k3.i2 + k4.i2);
    s->v_cc += (dt / 6.0) * (k1.v_cc + 2.0 * k2.v_cc + 2.0 * k3.v_cc + k4.v_cc);
    s->v_out += (dt / 6.0) * (k1.v_out + 2.0 * k2.v_out + 2.0 * k3.v_out + k4.v_out);
}

int main(void) {
    ZetaParams cfg = {
        .Vin = 12.0, .R_load = 6.0, .f_sw = 250000.0, .D = 0.512,
        .L1 = 27e-6, .L2 = 33e-6, .k_mag = 0.90,
        .Cc = 14.1e-6, .Cout = 91e-6,
        .Ron = 0.015, .V_diode = 0.45
    };

    ZetaState state = { .i1 = 0.0, .i2 = 0.0, .v_cc = 0.0, .v_out = 0.0 };

    double dt = 2.0e-8;   /* Крок інтегрування 20 нс */
    double t_end = 0.004; /* 4 мс загального часу симуляції */

    printf("# Симуляція Zeta-перетворювача (Зв'язані індуктивності k=%.2f)\n", cfg.k_mag);
    printf("# Час(мс)   I_L1(A)    I_L2(A)    V_Cc(V)    V_out(V)\n");

    int step_count = 0;
    int print_decimation = 2500;

    for (double t = 0.0; t < t_end; t += dt, step_count++) {
        rk4_step(&cfg, &state, t, dt);

        if (step_count % print_decimation == 0) {
            printf("%8.3f   %8.4f   %8.4f   %8.3f   %8.3f\n",
                   t * 1000.0, state.i1, state.i2, state.v_cc, state.v_out);
        }
    }

    printf("\n# Результати усталеного стану:\n");
    printf("Вихідна напруга V_out = %.3f В (Ціль: 12.0 В)\n", state.v_out);
    printf("Напруга на Cc   V_Cc  = %.3f В (Теорія V_Cc=V_out: %.3f В)\n", state.v_cc, state.v_out);
    printf("Вхідний струм   I_L1  = %.3f А, Вихідний струм I_L2 = %.3f А\n", state.i1, state.i2);

    return 0;
}
