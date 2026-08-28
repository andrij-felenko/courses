/* phase_portrait.c — Чисельний двигун фазового портрета мовою C (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Вектор стану у фазовому просторі: (координата q, імпульс/швидкість p) */
typedef struct {
    double q;
    double p;
} PhaseState;

/* Параметри фізичної системи (наприклад, нелінійного маятника) */
typedef struct {
    double omega0_sq; /* квадрат власної частоти g/L */
    double damping;   /* коефіцієнт згасання gamma */
} PendulumParams;

/* Сигнатура функції векторного поля: F(X) = (dq/dt, dp/dt) */
typedef void (*VectorFieldFunc)(const PhaseState* state, const void* params, PhaseState* deriv);

/* Права частина рівнянь маятника: dq/dt = p, dp/dt = -omega0^2 * sin(q) - damping * p */
static void pendulum_rhs(const PhaseState* state, const void* params, PhaseState* deriv) {
    const PendulumParams* p = (const PendulumParams*)params;
    deriv->q = state->p;
    deriv->p = -p->omega0_sq * sin(state->q) - p->damping * state->p;
}

/* Один крок чисельного інтегрування методом Рунґе-Кутти 4-го порядку (RK4) */
static PhaseState rk4_step(PhaseState current, double h, VectorFieldFunc field, const void* params) {
    PhaseState k1, k2, k3, k4;
    PhaseState temp;

    /* k1 = F(X) */
    field(&current, params, &k1);

    /* k2 = F(X + 0.5*h*k1) */
    temp.q = current.q + 0.5 * h * k1.q;
    temp.p = current.p + 0.5 * h * k1.p;
    field(&temp, params, &k2);

    /* k3 = F(X + 0.5*h*k2) */
    temp.q = current.q + 0.5 * h * k2.q;
    temp.p = current.p + 0.5 * h * k2.p;
    field(&temp, params, &k3);

    /* k4 = F(X + h*k3) */
    temp.q = current.q + h * k3.q;
    temp.p = current.p + h * k3.p;
    field(&temp, params, &k4);

    /* X_{n+1} = X + (h/6)*(k1 + 2*k2 + 2*k3 + k4) */
    PhaseState next_state;
    next_state.q = current.q + (h / 6.0) * (k1.q + 2.0 * k2.q + 2.0 * k3.q + k4.q);
    next_state.p = current.p + (h / 6.0) * (k1.p + 2.0 * k2.p + 2.0 * k3.p + k4.p);
    return next_state;
}

/* Інтегрування однієї траєкторії та збереження у CSV-файл */
static int simulate_trajectory(const char* filename, PhaseState initial_state, double h, int steps,
                               VectorFieldFunc field, const void* params) {
    FILE* fp = fopen(filename, "w");
    if (!fp) {
        perror("Не вдалося відкрити файл для запису траєкторії");
        return -1;
    }

    fprintf(fp, "step,t,q,p\n");
    PhaseState state = initial_state;
    double t = 0.0;

    for (int i = 0; i <= steps; ++i) {
        fprintf(fp, "%d,%.5f,%.6f,%.6f\n", i, t, state.q, state.p);
        state = rk4_step(state, h, field, params);
        t += h;
    }

    fclose(fp);
    return 0;
}

/* Генерація сітки векторного поля у заданому прямокутнику */
static int generate_vector_grid(const char* filename, double q_min, double q_max, int q_res,
                                double p_min, double p_max, int p_res,
                                VectorFieldFunc field, const void* params) {
    FILE* fp = fopen(filename, "w");
    if (!fp) {
        perror("Не вдалося відкрити файл для запису векторного поля");
        return -1;
    }

    fprintf(fp, "q,p,dq_dt,dp_dt,magnitude\n");
    double dq = (q_max - q_min) / (q_res - 1);
    double dp = (p_max - p_min) / (p_res - 1);

    for (int i = 0; i < q_res; ++i) {
        double q = q_min + i * dq;
        for (int j = 0; j < p_res; ++j) {
            double p = p_min + j * dp;
            PhaseState state = {q, p};
            PhaseState deriv;
            field(&state, params, &deriv);
            double mag = sqrt(deriv.q * deriv.q + deriv.p * deriv.p);
            fprintf(fp, "%.5f,%.5f,%.6f,%.6f,%.6f\n", q, p, deriv.q, deriv.p, mag);
        }
    }

    fclose(fp);
    return 0;
}

int main(void) {
    PendulumParams p_conservative = {.omega0_sq = 1.0, .damping = 0.0};
    PendulumParams p_damped       = {.omega0_sq = 1.0, .damping = 0.2};

    printf("Обчислення консервативних та дисипативних фазових траєкторій...\n");

    /* Збереження сітки векторного поля */
    generate_vector_grid("pendulum_field.csv", -6.28, 6.28, 30, -3.0, 3.0, 30, pendulum_rhs, &p_damped);

    /* Траєкторія 1: Малі коливання навколо центра (q0 = 0.5, p0 = 0) */
    PhaseState s1 = {0.5, 0.0};
    simulate_trajectory("traj_center.csv", s1, 0.01, 2000, pendulum_rhs, &p_conservative);

    /* Траєкторія 2: Рух поблизу сепаратриси (q0 = 3.10, p0 = 0) */
    PhaseState s2 = {3.10, 0.0};
    simulate_trajectory("traj_separatrix.csv", s2, 0.01, 2000, pendulum_rhs, &p_conservative);

    /* Траєкторія 3: Згасаюче коливання до стійкого фокуса */
    PhaseState s3 = {3.0, 1.5};
    simulate_trajectory("traj_damped_focus.csv", s3, 0.01, 2000, pendulum_rhs, &p_damped);

    printf("Символьні обчислення завершено. Дані збережено у CSV-файли.\n");
    return 0;
}
