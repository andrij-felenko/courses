#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double h_x;         /* Ентропія джерела H(X) */
    double h_y;         /* Ентропія приймача H(Y) */
    double h_xy;        /* Спільна ентропія H(X,Y) */
    double h_x_given_y; /* Умовна ентропія H(X|Y) (equivocation) */
    double h_y_given_x; /* Умовна ентропія H(Y|X) (шум каналу) */
    double mutual_info; /* Взаємна інформація I(X;Y) */
} EntropyMetrics;

/**
 * Обчислює інформаційні метрики за матрицею частот.
 * 
 * @param matrix Масив розміром rows * cols з лінійним розгортанням.
 * @param rows Кількість значень величини X.
 * @param cols Кількість значень величини Y.
 * @param out_metrics Вказівник на структуру для збереження результатів.
 * @return true у разі успіху, false при нульовій сумі випробувань або помилці виділення пам'яті.
 */
bool compute_entropy_metrics(const double *matrix, size_t rows, size_t cols, EntropyMetrics *out_metrics) {
    if (!matrix || !out_metrics || rows == 0 || cols == 0) {
        return false;
    }

    double total_count = 0.0;
    for (size_t i = 0; i < rows * cols; ++i) {
        total_count += matrix[i];
    }

    if (total_count <= 0.0) {
        return false;
    }

    double *px = (double *)calloc(rows, sizeof(double));
    double *py = (double *)calloc(cols, sizeof(double));

    if (!px || !py) {
        free(px);
        free(py);
        return false;
    }

    /* 1. Обчислення маргінальних ймовірностей */
    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix[r * cols + c] / total_count;
            px[r] += p_joint;
            py[c] += p_joint;
        }
    }

    double h_x = 0.0;
    for (size_t r = 0; r < rows; ++r) {
        if (px[r] > 0.0) {
            h_x -= px[r] * log2(px[r]);
        }
    }

    double h_y = 0.0;
    for (size_t c = 0; c < cols; ++c) {
        if (py[c] > 0.0) {
            h_y -= py[c] * log2(py[c]);
        }
    }

    double h_xy = 0.0;
    double h_x_given_y = 0.0;
    double h_y_given_x = 0.0;

    /* 2. Обчислення спільної та умовних ентропій */
    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix[r * cols + c] / total_count;
            if (p_joint > 0.0) {
                h_xy -= p_joint * log2(p_joint);

                double p_x_given_y = p_joint / py[c];
                h_x_given_y -= p_joint * log2(p_x_given_y);

                double p_y_given_x = p_joint / px[r];
                h_y_given_x -= p_joint * log2(p_y_given_x);
            }
        }
    }

    free(px);
    free(py);

    out_metrics->h_x = h_x;
    out_metrics->h_y = h_y;
    out_metrics->h_xy = h_xy;
    out_metrics->h_x_given_y = h_x_given_y;
    out_metrics->h_y_given_x = h_y_given_x;
    out_metrics->mutual_info = h_x - h_x_given_y;

    return true;
}

int main(void) {
    /* Приклад: зашумлений симетричний канал BSC із ймовірністю помилки p = 0.1 */
    /* Матриця частот: rows=2 (X in {0,1}), cols=2 (Y in {0,1}) */
    /* N(0,0)=450, N(0,1)=50, N(1,0)=50, N(1,1)=450 (разом 1000 випробувань) */
    double confusion_matrix[2][2] = {
        { 450.0,  50.0 },
        {  50.0, 450.0 }
    };

    EntropyMetrics res;
    if (compute_entropy_metrics((const double *)confusion_matrix, 2, 2, &res)) {
        printf("H(X)     = %.4f бітів\n", res.h_x);
        printf("H(Y)     = %.4f бітів\n", res.h_y);
        printf("H(X,Y)   = %.4f бітів\n", res.h_xy);
        printf("H(X|Y)   = %.4f бітів (equivocation)\n", res.h_x_given_y);
        printf("H(Y|X)   = %.4f бітів (шум)\n", res.h_y_given_x);
        printf("I(X;Y)   = %.4f бітів\n", res.mutual_info);
    }
    return 0;
}
