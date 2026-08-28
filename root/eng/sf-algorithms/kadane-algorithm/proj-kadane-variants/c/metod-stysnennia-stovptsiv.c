#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    long long max_sum;
    int top_row;
    int bottom_row;
    int left_col;
    int right_col;
} MatrixSubarrayResult;

MatrixSubarrayResult kadane_2d_matrix(const int* matrix, int rows, int cols) {
    MatrixSubarrayResult res = { -1000000000LL, 0, 0, 0, 0 };
    if (matrix == NULL || rows <= 0 || cols <= 0) {
        res.max_sum = 0;
        return res;
    }

    /* Виділяємо один буфер під накопичені суми стовпчиків */
    int* col_sum = (int*)malloc(sizeof(int) * cols);
    if (col_sum == NULL) {
        return res;
    }

    long long global_max = matrix[0];
    int best_r1 = 0, best_r2 = 0, best_c1 = 0, best_c2 = 0;

    for (int r1 = 0; r1 < rows; ++r1) {
        /* Обнуляємо масив стиснених стовпчиків перед розширенням r2 */
        memset(col_sum, 0, sizeof(int) * cols);

        for (int r2 = r1; r2 < rows; ++r2) {
            /* Поелементно додаємо новий рядок r2 до поточного зрізу */
            for (int c = 0; c < cols; ++c) {
                col_sum[c] += matrix[r2 * cols + c];
            }

            /* Запуск одновимірного алгоритму Кадане над вектором col_sum */
            long long current_sum = col_sum[0];
            long long local_max = col_sum[0];
            int current_c1 = 0;
            int local_c1 = 0, local_c2 = 0;

            for (int c = 1; c < cols; ++c) {
                if (current_sum < 0) {
                    current_sum = col_sum[c];
                    current_c1 = c;
                } else {
                    current_sum += col_sum[c];
                }

                if (current_sum > local_max) {
                    local_max = current_sum;
                    local_c1 = current_c1;
                    local_c2 = c;
                }
            }

            /* Оновлення абсолютного максимуму матриці */
            if (r1 == 0 && r2 == 0) {
                global_max = local_max;
                best_r1 = r1; best_r2 = r2;
                best_c1 = local_c1; best_c2 = local_c2;
            } else if (local_max > global_max) {
                global_max = local_max;
                best_r1 = r1;
                best_r2 = r2;
                best_c1 = local_c1;
                best_c2 = local_c2;
            }
        }
    }

    free(col_sum);

    res.max_sum = global_max;
    res.top_row = best_r1;
    res.bottom_row = best_r2;
    res.left_col = best_c1;
    res.right_col = best_c2;
    return res;
}
