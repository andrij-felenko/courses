#include <stdio.h>

long long max_product_subarray(const int* arr, int n) {
    if (arr == NULL || n <= 0) {
        return 0;
    }

    long long max_prod = arr[0];
    long long min_prod = arr[0];
    long long global_max = arr[0];

    for (int i = 1; i < n; ++i) {
        int x = arr[i];

        if (x < 0) {
            /* Від'ємний множник інвертує порядок екстремумів */
            long long temp = max_prod;
            max_prod = min_prod;
            min_prod = temp;
        }

        /* Обчислення нових меж накопичення */
        long long cand_max = (max_prod * x > x) ? max_prod * x : x;
        long long cand_min = (min_prod * x < x) ? min_prod * x : x;

        max_prod = cand_max;
        min_prod = cand_min;

        if (max_prod > global_max) {
            global_max = max_prod;
        }
    }

    return global_max;
}
