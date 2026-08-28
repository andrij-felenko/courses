#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "matrix_perm.h"

int main(void) {
    /* 0/1 матриця суміжності двочасткового графа 4x4 */
    const uint64_t matrix[16] = {
        1, 1, 0, 1,
        1, 0, 1, 0,
        0, 1, 1, 1,
        1, 1, 0, 1
    };
    const size_t n = 4;

    perm_config_t cfg = {
        .algorithm   = PERM_ALG_RYSER_GRAY,
        .num_threads = 1,
        .use_simd    = true
    };

    uint64_t perm_val = 0;
    perm_status_t status = perm_compute_u64(matrix, n, &cfg, &perm_val);

    if (status == PERM_SUCCESS) {
        printf("Перманент матриці 4x4 дорівнює: %lu\n", perm_val);
    } else {
        fprintf(stderr, "Помилка обчислення з кодом: %d\n", status);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
