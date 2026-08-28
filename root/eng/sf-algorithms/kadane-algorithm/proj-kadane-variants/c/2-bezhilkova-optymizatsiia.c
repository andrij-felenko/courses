#include <stdio.h>

long long kadane_branchless(const int* arr, int n) {
    if (arr == NULL || n <= 0) {
        return 0;
    }

    long long current_sum = arr[0];
    long long max_sum = arr[0];

    for (int i = 1; i < n; ++i) {
        long long x = arr[i];
        /* Безгілкове скидання від'ємної суми до нуля */
        long long prev_positive = (current_sum > 0) ? current_sum : 0;
        current_sum = prev_positive + x;
        max_sum = (current_sum > max_sum) ? current_sum : max_sum;
    }

    return max_sum;
}
