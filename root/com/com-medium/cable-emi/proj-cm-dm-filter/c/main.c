#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double* v_dm;
    double* v_cm;
    size_t length;
} ModeDecomposition;

/* Розділення сигналів двох ліній на DM та CM складові */
ModeDecomposition decompose_modes(const double* va, const double* vb, size_t n) {
    ModeDecomposition res;
    res.length = n;
    res.v_dm = (double*)malloc(n * sizeof(double));
    res.v_cm = (double*)malloc(n * sizeof(double));
    if (!res.v_dm || !res.v_cm) {
        free(res.v_dm);
        free(res.v_cm);
        res.v_dm = NULL;
        res.v_cm = NULL;
        res.length = 0;
        return res;
    }

    for (size_t i = 0; i < n; ++i) {
        res.v_dm[i] = va[i] - vb[i];
        res.v_cm[i] = 0.5 * (va[i] + vb[i]);
    }
    return res;
}

void free_decomposition(ModeDecomposition* d) {
    if (d) {
        free(d->v_dm);
        free(d->v_cm);
        d->v_dm = NULL;
        d->v_cm = NULL;
        d->length = 0;
    }
}

/* Адаптивний LMS-фільтр придушення синфазної завади */
void lms_cancel_cm_interference(const double* v_dm_noisy, const double* v_cm,
                                double* v_dm_clean, size_t n, double mu) {
    double w = 0.0; /* поточна оцінка коефіцієнта проникнення CM -> DM */
    for (size_t i = 0; i < n; ++i) {
        double estimated_cm_leak = w * v_cm[i];
        double error = v_dm_noisy[i] - estimated_cm_leak;
        v_dm_clean[i] = error;
        /* Оновлення ваги за стохастичним градієнтом найменших квадратів */
        w += mu * error * v_cm[i];
    }
}

/* Розрахунок наведеної напруги за передавальним імпедансом екрана Z_T */
double calc_induced_shield_voltage(double i_shield_rms, double z_transfer, double length_m) {
    return i_shield_rms * z_transfer * length_m;
}

int main(void) {
    const size_t N = 1000;
    double* va = (double*)malloc(N * sizeof(double));
    double* vb = (double*)malloc(N * sizeof(double));
    double* clean_dm = (double*)malloc(N * sizeof(double));

    if (!va || !vb || !clean_dm) {
        free(va);
        free(vb);
        free(clean_dm);
        return 1;
    }

    const double f_sig = 1000.0;    /* 1 кГц корисний сигнал інформаційного каналу */
    const double f_emi = 50000.0;   /* 50 кГц синфазна завада від силового ШІМ-інвертора */
    const double fs = 500000.0;     /* 500 кГц частота дискретизації АЦП */
    const double alpha_leak = 0.05; /* 5% асиметрія провідників (коефіцієнт перетворення) */

    for (size_t i = 0; i < N; ++i) {
        double t = (double)i / fs;
        double sig_dm = 1.0 * sin(2.0 * M_PI * f_sig * t);
        double emi_cm = 3.0 * sin(2.0 * M_PI * f_emi * t);

        /* Моделювання напруг ліній із перекосом */
        va[i] = (0.5 * sig_dm) + emi_cm;
        vb[i] = (-0.5 * sig_dm) + emi_cm * (1.0 - alpha_leak);
    }

    ModeDecomposition decomp = decompose_modes(va, vb, N);
    if (decomp.v_dm && decomp.v_cm) {
        lms_cancel_cm_interference(decomp.v_dm, decomp.v_cm, clean_dm, N, 0.01);

        printf("Індекс | V_a (В)  | V_b (В)  | V_DM вихідна | V_CM завада | V_DM очищена\n");
        printf("--------------------------------------------------------------------\n");
        for (size_t i = 0; i < 5; ++i) {
            printf("%6zu | %8.4f | %8.4f | %12.4f | %11.4f | %12.4f\n",
                   i, va[i], vb[i], decomp.v_dm[i], decomp.v_cm[i], clean_dm[i]);
        }
    }

    free_decomposition(&decomp);
    free(va);
    free(vb);
    free(clean_dm);
    return 0;
}
