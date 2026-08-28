#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Структура параметрів магнітозв'язаної пари індуктивностей */
typedef struct {
    double l1;       /* Власна індуктивність 1, Гн */
    double l2;       /* Власна індуктивність 2, Гн */
    double k;        /* Коефіцієнт зв'язку (-1.0 ... +1.0) */
    double dcr1;     /* Активний опір 1, Ом */
    double dcr2;     /* Активний опір 2, Ом */
    double m;        /* Взаємоіндукція M = k * sqrt(L1*L2), Гн */
    double det_l;    /* Детермінант L1*L2 - M^2 */
} CoupledPair;

/* Структура стану струмів у часі */
typedef struct {
    double i1;       /* Струм першої котушки, А */
    double i2;       /* Струм другої котушки, А */
} CircuitState;

/* Ініціалізація та попередній розрахунок детермінанта */
void coupled_pair_init(CoupledPair *cp, double l1, double l2, double k, double dcr1, double dcr2) {
    cp->l1 = l1;
    cp->l2 = l2;
    cp->k = k;
    cp->dcr1 = dcr1;
    cp->dcr2 = dcr2;
    cp->m = k * sqrt(l1 * l2);
    cp->det_l = (l1 * l2) - (cp->m * cp->m);
}

/* Обчислення похідних струмів di1/dt та di2/dt */
void coupled_pair_derivatives(const CoupledPair *cp, const CircuitState *state,
                              double v1_ext, double v2_ext,
                              double *di1_dt, double *di2_dt) {
    /* Напруги безпосередньо на індуктивностях за вирахуванням спаду на DCR */
    double v1_ind = v1_ext - (state->i1 * cp->dcr1);
    double v2_ind = v2_ext - (state->i2 * cp->dcr2);

    /* Множення на обернену матрицю індуктивностей */
    *di1_dt = (cp->l2 * v1_ind - cp->m * v2_ind) / cp->det_l;
    *di2_dt = (-cp->m * v1_ind + cp->l1 * v2_ind) / cp->det_l;
}

/* Крок чисельного інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
void rk4_step(const CoupledPair *cp, CircuitState *state,
              double v1_ext, double v2_ext, double dt) {
    double k1_i1, k1_i2;
    double k2_i1, k2_i2;
    double k3_i1, k3_i2;
    double k4_i1, k4_i2;

    /* Стадія 1 */
    coupled_pair_derivatives(cp, state, v1_ext, v2_ext, &k1_i1, &k1_i2);

    /* Стадія 2 */
    CircuitState s2 = {
        state->i1 + 0.5 * dt * k1_i1,
        state->i2 + 0.5 * dt * k1_i2
    };
    coupled_pair_derivatives(cp, &s2, v1_ext, v2_ext, &k2_i1, &k2_i2);

    /* Стадія 3 */
    CircuitState s3 = {
        state->i1 + 0.5 * dt * k2_i1,
        state->i2 + 0.5 * dt * k2_i2
    };
    coupled_pair_derivatives(cp, &s3, v1_ext, v2_ext, &k3_i1, &k3_i2);

    /* Стадія 4 */
    CircuitState s4 = {
        state->i1 + dt * k3_i1,
        state->i2 + dt * k3_i2
    };
    coupled_pair_derivatives(cp, &s4, v1_ext, v2_ext, &k4_i1, &k4_i2);

    /* Зважене оновлення стану */
    state->i1 += (dt / 6.0) * (k1_i1 + 2.0 * k2_i1 + 2.0 * k3_i1 + k4_i1);
    state->i2 += (dt / 6.0) * (k1_i2 + 2.0 * k2_i2 + 2.0 * k3_i2 + k4_i2);
}

int main(void) {
    /* Сценарій: моделювання 2-фазного VRM зі зв'язаним дроселем */
    CoupledPair vrm_choke;
    double l_nominal = 150e-9; /* 150 нГн на фазу */
    double k_coupling = -0.6;   /* Інверсний зв'язок k = -0.6 */
    double dcr = 0.001;        /* 1 мОм DCR */

    coupled_pair_init(&vrm_choke, l_nominal, l_nominal, k_coupling, dcr, dcr);

    CircuitState state = {0.0, 0.0};
    double dt = 1e-9;          /* Крок симуляції 1 нс */
    double t_total = 4e-6;     /* 4 мкс симуляції (2 періоди комутації) */
    double period = 2e-6;      /* Частота комутації 500 кГц (T = 2 мкс) */
    double duty = 0.25;        /* Коефіцієнт заповнення D = 0.25 (Vout = 3 В від Vin = 12 В) */
    double vin = 12.0;

    printf("=== СИМУЛЯЦІЯ ДВОФАЗНОГО DC-DC ЗІ ЗВ'ЯЗАНИМ ДРОСЕЛЕМ ===\n");
    printf("L = %.1f нГн, k = %.2f, DCR = %.1f мОм\n\n",
           l_nominal * 1e9, k_coupling, dcr * 1000.0);
    printf("Час [мкс] | Напруга SW1 [В] | Напруга SW2 [В] | Струм I1 [А] | Струм I2 [А] | Сумарний I [А]\n");
    printf("----------------------------------------------------------------------------------------\n");

    for (double t = 0; t <= t_total; t += dt) {
        /* Фаза 1 комутується від 0 */
        double phase1_time = fmod(t, period);
        double v1_sw = (phase1_time < (duty * period)) ? vin : 0.0;

        /* Фаза 2 комутується зі зсувом 180 градусів (T/2) */
        double phase2_time = fmod(t + 0.5 * period, period);
        double v2_sw = (phase2_time < (duty * period)) ? vin : 0.0;

        /* Віднімаємо вихідну напругу Vout = 3.0 В */
        double v1_ext = v1_sw - 3.0;
        double v2_ext = v2_sw - 3.0;

        rk4_step(&vrm_choke, &state, v1_ext, v2_ext, dt);

        /* Друк кожні 200 нс */
        if (fmod(t + 1e-12, 200e-9) < dt) {
            printf("%9.3f | %15.1f | %15.1f | %12.3f | %12.3f | %14.3f\n",
                   t * 1e6, v1_sw, v2_sw, state.i1, state.i2, state.i1 + state.i2);
        }
    }

    return 0;
}
