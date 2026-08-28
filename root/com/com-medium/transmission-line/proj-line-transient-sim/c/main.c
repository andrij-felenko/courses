#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_NODES 200
#define TOTAL_STEPS 600

typedef struct {
    double z0;          /* Характеристичний імпеданс лінії, Ом */
    double v_prop;      /* Фазова швидкість поширення хвилі, м/с */
    double length;      /* Фізична довжина лінії передачі, м */
    double r0;          /* Погонний опір втрат у металі, Ом/м */
    double g0;          /* Погонна провідність витоку діелектрика, См/м */
    double z_load;      /* Опір навантаження на кінці лінії, Ом */
    double r_src;       /* Внутрішній опір генератора сигналу, Ом */
} tline_config_t;

void run_tline_simulation(const tline_config_t *cfg, double *v_in_history) {
    double dz = cfg->length / (NUM_NODES - 1);
    double l0 = cfg->z0 / cfg->v_prop;
    double c0 = 1.0 / (cfg->z0 * cfg->v_prop);
    double dt = 0.9 * (dz / cfg->v_prop); /* Умова Куранта CFL */

    double V[NUM_NODES] = {0.0};
    double I[NUM_NODES - 1] = {0.0};

    /* Коефіцієнти загасання для схеми FDTD */
    double c_i1 = (1.0 - (cfg->r0 * dt / (2.0 * l0))) / (1.0 + (cfg->r0 * dt / (2.0 * l0)));
    double c_i2 = (dt / (l0 * dz)) / (1.0 + (cfg->r0 * dt / (2.0 * l0)));

    double c_v1 = (1.0 - (cfg->g0 * dt / (2.0 * c0))) / (1.0 + (cfg->g0 * dt / (2.0 * c0)));
    double c_v2 = (dt / (c0 * dz)) / (1.0 + (cfg->g0 * dt / (2.0 * c0)));

    for (int t = 0; t < TOTAL_STEPS; t++) {
        /* 1. Генерирація ступені напруги генератора 1.0 В з часом наростання */
        double e_src = (t < 10) ? (1.0 * t / 10.0) : 1.0;

        /* 2. Оновлення струмів у напівцілих вузлах сітки */
        for (int i = 0; i < NUM_NODES - 1; i++) {
            double dV = V[i + 1] - V[i];
            I[i] = c_i1 * I[i] - c_i2 * dV;
        }

        /* 3. Оновлення внутрішніх напруг у цілих вузлах */
        for (int i = 1; i < NUM_NODES - 1; i++) {
            double dI = I[i] - I[i - 1];
            V[i] = c_v1 * V[i] - c_v2 * dI;
        }

        /* 4. Гранична умова на вхідному кінці z = 0 (включаючи джерело) */
        double i_in_src = (e_src - V[0]) / cfg->r_src;
        V[0] = V[0] + (2.0 * dt / (c0 * dz)) * (i_in_src - I[0]);

        /* 5. Гранична умова на вихідному кінці z = L (навантаження Z_L) */
        if (cfg->z_load > 1e6) {
            /* Холостий хід: струм відсутній, шар заряду накопичується */
            V[NUM_NODES - 1] += (2.0 * dt / (c0 * dz)) * I[NUM_NODES - 2];
        } else if (cfg->z_load < 1e-3) {
            /* Коротке замикання: напруга дорівнює нулю */
            V[NUM_NODES - 1] = 0.0;
        } else {
            /* Омічне навантаження */
            V[NUM_NODES - 1] = I[NUM_NODES - 2] * cfg->z_load;
        }

        /* Запис осцилограми вхідної напруги для аналізу TDR */
        v_in_history[t] = V[0];
    }
}

int main(void) {
    tline_config_t cfg = {
        .z0 = 50.0,
        .v_prop = 2.0e8,  /* 200,000 км/с */
        .length = 10.0,   /* 10 метрів */
        .r0 = 0.02,       /* Втрати в міді */
        .g0 = 0.0,
        .z_load = 100.0,  /* Неузгоджене навантаження 100 Ом */
        .r_src = 50.0     /* Узгоджений опір генератора 50 Ом */
    };

    double history[TOTAL_STEPS];
    run_tline_simulation(&cfg, history);

    printf("=== Симуляція часової рефлектометрії TDR (C-реалізація) ===\n");
    printf("Крок 50  (падаюча хвиля V_in): %.3f В\n", history[50]);
    printf("Крок 250 (відбита хвиля V_ref): %.3f В\n", history[250]);

    return 0;
}
