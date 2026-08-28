/* rikitake_sim.c - Чисельне моделювання хаотичного динамо Рікітаке мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double x;
    double y;
    double z;
} RikitakeState;

typedef struct {
    double mu;
    double a;
} RikitakeParams;

/* Права частина системи диференціальних рівнянь Рікітаке */
static RikitakeState rikitake_derivatives(RikitakeState s, RikitakeParams p) {
    RikitakeState ds;
    ds.x = -p.mu * s.x + s.y * s.z;
    ds.y = -p.mu * s.y + (s.z - p.a) * s.x;
    ds.z = 1.0 - s.x * s.y;
    return ds;
}

/* Один крок інтегрування методом Рунґе-Кутти 4-го порядку */
static RikitakeState rk4_step(RikitakeState s, RikitakeParams p, double dt) {
    RikitakeState k1 = rikitake_derivatives(s, p);

    RikitakeState s2 = {
        s.x + 0.5 * dt * k1.x,
        s.y + 0.5 * dt * k1.y,
        s.z + 0.5 * dt * k1.z
    };
    RikitakeState k2 = rikitake_derivatives(s2, p);

    RikitakeState s3 = {
        s.x + 0.5 * dt * k2.x,
        s.y + 0.5 * dt * k2.y,
        s.z + 0.5 * dt * k2.z
    };
    RikitakeState k3 = rikitake_derivatives(s3, p);

    RikitakeState s4 = {
        s.x + dt * k3.x,
        s.y + dt * k3.y,
        s.z + dt * k3.z
    };
    RikitakeState k4 = rikitake_derivatives(s4, p);

    RikitakeState next_state;
    next_state.x = s.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    next_state.y = s.y + (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
    next_state.z = s.z + (dt / 6.0) * (k1.z + 2.0 * k2.z + 2.0 * k3.z + k4.z);
    return next_state;
}

int main(void) {
    RikitakeParams params = { .mu = 1.0, .a = 5.0 };
    RikitakeState state = { .x = 0.1, .y = 0.8, .z = 2.0 };

    double dt = 0.01;
    double t_max = 500.0;
    int steps = (int)(t_max / dt);

    FILE *fp = fopen("rikitake_trajectory.csv", "w");
    if (!fp) {
        perror("Помилка відкриття файлу для запису");
        return EXIT_FAILURE;
    }

    fprintf(fp, "time,x,y,z,reversal\n");

    int reversal_count = 0;
    double last_x = state.x;
    double last_reversal_time = 0.0;

    for (int i = 0; i < steps; ++i) {
        double t = i * dt;
        state = rk4_step(state, params, dt);

        /* Детекція зміни знаку струму x(t) - інверсія магнітного поля */
        int is_reversal = 0;
        if ((last_x > 0.0 && state.x < 0.0) || (last_x < 0.0 && state.x > 0.0)) {
            is_reversal = 1;
            reversal_count++;
            double interval = t - last_reversal_time;
            printf("Інверсія #%d на t = %.2f (інтервал: %.2f)\n", reversal_count, t, interval);
            last_reversal_time = t;
        }
        last_x = state.x;

        fprintf(fp, "%.3f,%.5f,%.5f,%.5f,%d\n", t, state.x, state.y, state.z, is_reversal);
    }

    fclose(fp);
    printf("Симуляцію завершено. Усього інверсій: %d. Дані збережено в rikitake_trajectory.csv\n", reversal_count);
    return EXIT_SUCCESS;
}
