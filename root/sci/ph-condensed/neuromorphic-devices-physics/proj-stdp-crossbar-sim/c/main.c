#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define ROWS 4
#define COLS 4

/* Фізичні параметри штучного синапсу OxRAM (HfO2) */
#define G_MIN 1e-6    /* 1 мкСм (HRS - стан високого опору R = 1 МОм) */
#define G_MAX 100e-6  /* 100 мкСм (LRS - стан низького опору R = 10 кОм) */
#define A_PLUS 5e-6   /* Амплітуда потенціації LTP (5 мкСм) */
#define A_MINUS 4e-6  /* Амплітуда депресії LTD (4 мкСм) */
#define TAU_PLUS 20.0 /* Часове вікно потенціації (мс) */
#define TAU_MINUS 20.0/* Часове вікно депресії (мс) */

typedef struct {
    double G[ROWS][COLS];
} SynapticCrossbar;

/* Ініціалізація кросбару випадковими провідностями у межах [G_MIN, G_MAX] */
void crossbar_init(SynapticCrossbar *cb) {
    for (int i = 0; i < ROWS; ++i) {
        for (int j = 0; j < COLS; ++j) {
            double r = (double)rand() / RAND_MAX;
            cb->G[i][j] = G_MIN + r * (G_MAX - G_MIN);
        }
    }
}

/* Аналогове множення вектор-матриця: I_j = sum_i (V_i * G_ij) */
void crossbar_mvm(const SynapticCrossbar *cb, const double v_in[ROWS], double i_out[COLS]) {
    for (int j = 0; j < COLS; ++j) {
        i_out[j] = 0.0;
        for (int i = 0; i < ROWS; ++i) {
            i_out[j] += v_in[i] * cb->G[i][j];
        }
    }
}

/* Оновлення провідностей за правилом STDP: dt = t_post - t_pre */
void crossbar_update_stdp(SynapticCrossbar *cb, const double t_pre[ROWS], const double t_post[COLS]) {
    for (int i = 0; i < ROWS; ++i) {
        for (int j = 0; j < COLS; ++j) {
            double dt = t_post[j] - t_pre[i];
            double dG = 0.0;

            if (dt > 0.0) {
                /* LTP: Пост-спайк після пре-спайку → Причинний зв'язок → Потенціація */
                dG = A_PLUS * exp(-dt / TAU_PLUS);
            } else if (dt < 0.0) {
                /* LTD: Пост-спайк перед пре-спайком → Апричинний зв'язок → Депресія */
                dG = -A_MINUS * exp(dt / TAU_MINUS);
            }

            cb->G[i][j] += dG;

            /* Жорстке затискання провідності у межах [G_MIN, G_MAX] */
            if (cb->G[i][j] > G_MAX) {
                cb->G[i][j] = G_MAX;
            } else if (cb->G[i][j] < G_MIN) {
                cb->G[i][j] = G_MIN;
            }
        }
    }
}

int main(void) {
    SynapticCrossbar cb;
    crossbar_init(&cb);

    double v_in[ROWS] = {1.0, 0.5, 0.0, 1.2}; /* Вхідні напруги рядків (Вольти) */
    double i_out[COLS];

    printf("=== До навчання: MVM аналогові струми ===\n");
    crossbar_mvm(&cb, v_in, i_out);
    for (int j = 0; j < COLS; ++j) {
        printf("Стовпець %d: Струм I = %.4f мкА\n", j, i_out[j] * 1e6);
    }

    /* Моделювання спайків: часові мітки пре- та пост-нейронів (мілісекунди) */
    double t_pre[ROWS] = {10.0, 15.0, 30.0, 40.0};
    double t_post[COLS] = {25.0, 10.0, 35.0, 20.0};

    crossbar_update_stdp(&cb, t_pre, t_post);

    printf("\n=== Після навчання STDP: Нові MVM аналогові струми ===\n");
    crossbar_mvm(&cb, v_in, i_out);
    for (int j = 0; j < COLS; ++j) {
        printf("Стовпець %d: Струм I = %.4f мкА\n", j, i_out[j] * 1e6);
    }

    return 0;
}
