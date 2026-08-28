/* Реалізація мовою C: пошук відрізка з кратністю за модулем m */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t start_idx;
    size_t end_idx;
    bool found;
} SubarrayResult;

SubarrayResult find_subarray_divisible_by_m(const int32_t* arr, size_t n, int32_t m) {
    SubarrayResult res = {0, 0, false};
    if (!arr || n == 0 || m <= 0) return res;

    /* Динамічний масив для збереження індексів першої появи остач mod m */
    int64_t* first_seen = (int64_t*)malloc((size_t)m * sizeof(int64_t));
    if (!first_seen) return res;

    for (int32_t i = 0; i < m; ++i) {
        first_seen[i] = -1; /* -1 означає, що остача ще не зустрічалася */
    }
    first_seen[0] = 0; /* P_0 = 0 має індекс 0 */

    int64_t current_prefix = 0;
    for (size_t j = 0; j < n; ++j) {
        current_prefix += arr[j];
        
        /* Коректне зведення від'ємних остач у діапазон [0, m-1] */
        int32_t rem = (int32_t)(current_prefix % m);
        if (rem < 0) rem += m;

        if (first_seen[rem] != -1) {
            res.start_idx = (size_t)first_seen[rem];
            res.end_idx = j;
            res.found = true;
            free(first_seen);
            return res;
        } else {
            first_seen[rem] = (int64_t)(j + 1);
        }
    }

    free(first_seen);
    return res;
}
