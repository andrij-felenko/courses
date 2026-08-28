#include <stdio.h>
#include <stdlib.h>
#include <string.h>

long long kadane_2d(const int* matrix, int rows, int cols) {
    if (matrix == NULL || rows <= 0 || cols <= 0) return 0;

    int* col_sum = (int*)malloc(sizeof(int) * cols);
    if (col_sum == NULL) return 0;

    long long global_max = matrix[0];

    for (int r1 = 0; r1 < rows; ++r1) {
        memset(col_sum, 0, sizeof(int) * cols);

        for (int r2 = r1; r2 < rows; ++r2) {
            for (int c = 0; c < cols; ++c) {
                col_sum[c] += matrix[r2 * cols + c];
            }

            /* 1D Кадане над зрізом стовпців */
            long long current_sum = col_sum[0];
            long long local_max = col_sum[0];

            for (int c = 1; c < cols; ++c) {
                current_sum = (current_sum < 0) ? col_sum[c] : current_sum + col_sum[c];
                if (current_sum > local_max) local_max = current_sum;
            }

            if (r1 == 0 && r2 == 0) {
                global_max = local_max;
            } else if (local_max > global_max) {
                global_max = local_max;
            }
        }
    }

    free(col_sum);
    return global_max;
}
