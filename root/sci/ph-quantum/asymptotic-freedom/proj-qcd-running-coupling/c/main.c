#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Маси порогових переходу кваркових ароматів у ГеВ (MS-bar) */
static const double MASS_CHARM  = 1.27;
static const double MASS_BOTTOM = 4.18;
static const double MASS_TOP    = 172.5;

/* Опорні експериментальні параметри на масі Z-бозона (LEP / PDG) */
static const double MASS_Z_BOSON = 91.1876;
static const double ALPHA_S_MZ_REF = 0.1179;

/* Структура для збереження результатів розрахунку в конкретній точці Q */
typedef struct {
    double q_scale;         /* Енергетичний масштаб Q в ГеВ */
    int n_f;                /* Кількість активних кваркових ароматів */
    double lambda_qcd;      /* Обчислений масштабний параметр Lambda_QCD (ГеВ) */
    double alpha_s_1loop;   /* Значення константи зв'язку у 1-петельному наближенні */
    double alpha_s_2loop;   /* Значення константи зв'язку у 2-петельному наближенні */
} qcd_point_t;

/* Обчислення першого коефіцієнта бета-функції beta0(n_f) */
static double get_beta0(int n_f) {
    return 11.0 - (2.0 / 3.0) * (double)n_f;
}

/* Обчислення другого коефіцієнта бета-функції beta1(n_f) */
static double get_beta1(int n_f) {
    return 102.0 - (38.0 / 3.0) * (double)n_f;
}

/* Визначення кількості активних ароматів n_f для заданого енергетичного масштабу Q */
static int get_active_flavors(double q) {
    if (q < MASS_CHARM)  return 3;
    if (q < MASS_BOTTOM) return 4;
    if (q < MASS_TOP)    return 5;
    return 6;
}

/* Обчислення масштабного параметра Lambda_QCD у 1-петельному наближенні */
static double compute_lambda_1loop(double alpha_ref, double q_ref, int n_f) {
    double b0 = get_beta0(n_f);
    double denom = (b0 / (4.0 * M_PI)) * alpha_ref;
    return q_ref * exp(-1.0 / (2.0 * denom));
}

/* Обчислення alpha_s(Q) у 1-петельному наближенні */
static double compute_alpha_1loop(double q, double lambda, int n_f) {
    if (q <= lambda) {
        return 1.0; /* Фізична межа непертурбативного конфайнменту */
    }
    double b0 = get_beta0(n_f);
    double t = log((q * q) / (lambda * lambda));
    return (4.0 * M_PI) / (b0 * t);
}

/* Обчислення alpha_s(Q) у 2-петельному наближенні */
static double compute_alpha_2loop(double q, double lambda, int n_f) {
    if (q <= lambda) {
        return 1.0;
    }
    double b0 = get_beta0(n_f);
    double b1 = get_beta1(n_f);
    double t = log((q * q) / (lambda * lambda));
    if (t <= 0.1) {
        return 1.0;
    }
    double a1 = (4.0 * M_PI) / (b0 * t);
    double corr = 1.0 - (b1 / (b0 * b0)) * (log(t) / t);
    return a1 * corr;
}

/* Основний каскадний алгоритм обчислення еволюції константи зв'язку */
int compute_qcd_evolution(const double *q_grid, int count, qcd_point_t *out_results) {
    if (!q_grid || !out_results || count <= 0) {
        return -1;
    }

    /* Крок 1: Обчислення початкового Lambda(5) від опорної точки m_Z */
    double lambda5 = compute_lambda_1loop(ALPHA_S_MZ_REF, MASS_Z_BOSON, 5);

    /* Крок 2: Перерахунок порогу b-кварка (n_f = 5 -> n_f = 4) */
    double alpha_b = compute_alpha_1loop(MASS_BOTTOM, lambda5, 5);
    double lambda4 = compute_lambda_1loop(alpha_b, MASS_BOTTOM, 4);

    /* Крок 3: Перерахунок порогу c-кварка (n_f = 4 -> n_f = 3) */
    double alpha_c = compute_alpha_1loop(MASS_CHARM, lambda4, 4);
    double lambda3 = compute_lambda_1loop(alpha_c, MASS_CHARM, 3);

    /* Крок 4: Перерахунок порогу t-кварка (n_f = 5 -> n_f = 6) */
    double alpha_t = compute_alpha_1loop(MASS_TOP, lambda5, 5);
    double lambda6 = compute_lambda_1loop(alpha_t, MASS_TOP, 6);

    /* Крок 5: Заповнення таблиці результатів для заданих імпульсів Q */
    for (int i = 0; i < count; ++i) {
        double q = q_grid[i];
        int nf = get_active_flavors(q);
        double current_lambda = lambda5;

        switch (nf) {
            case 3: current_lambda = lambda3; break;
            case 4: current_lambda = lambda4; break;
            case 5: current_lambda = lambda5; break;
            case 6: current_lambda = lambda6; break;
            default: current_lambda = lambda5; break;
        }

        out_results[i].q_scale = q;
        out_results[i].n_f = nf;
        out_results[i].lambda_qcd = current_lambda;
        out_results[i].alpha_s_1loop = compute_alpha_1loop(q, current_lambda, nf);
        out_results[i].alpha_s_2loop = compute_alpha_2loop(q, current_lambda, nf);
    }

    return 0;
}

int main(void) {
    /* Сітка енергетичних пунктів у ГеВ */
    double test_scales[] = { 0.5, 0.7, 1.0, 1.27, 2.0, 4.18, 10.0, 91.1876, 172.5, 500.0, 1000.0 };
    int n_points = sizeof(test_scales) / sizeof(test_scales[0]);

    qcd_point_t *results = (qcd_point_t *)malloc(n_points * sizeof(qcd_point_t));
    if (!results) {
        fprintf(stderr, "Помилка виділення динамічної пам'яті.\n");
        return 1;
    }

    if (compute_qcd_evolution(test_scales, n_points, results) == 0) {
        printf("===================================================================================\n");
        printf("         ЕВОЛЮЦІЯ ЕФЕКТИВНОЇ КОНСТАНТИ ЗВ'ЯЗКУ КХД alpha_s(Q²) (C99)\n");
        printf("===================================================================================\n");
        printf("%-10s %-6s %-14s %-16s %-16s\n", "Q (ГеВ)", "n_f", "Lambda (ГеВ)", "alpha_s (1-loop)", "alpha_s (2-loop)");
        printf("-----------------------------------------------------------------------------------\n");

        for (int i = 0; i < n_points; ++i) {
            printf("%-10.2f %-6d %-14.4f %-16.5f %-16.5f\n",
                   results[i].q_scale,
                   results[i].n_f,
                   results[i].lambda_qcd,
                   results[i].alpha_s_1loop,
                   results[i].alpha_s_2loop);
        }
        printf("-----------------------------------------------------------------------------------\n");
    }

    free(results);
    return 0;
}
