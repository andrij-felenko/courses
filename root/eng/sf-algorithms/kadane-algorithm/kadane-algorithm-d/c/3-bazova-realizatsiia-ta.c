#include <stdio.h>

long long kadane_basic(const int* arr, int n) {
    if (arr == NULL || n <= 0) {
        return 0;
    }

    long long current_sum = arr[0];
    long long max_sum = arr[0];

    for (int i = 1; i < n; ++i) {
        /* Якщо попередня сума від'ємна, скидаємо до arr[i] */
        if (current_sum < 0) {
            current_sum = arr[i];
        } else {
            current_sum += arr[i];
        }

        /* Оновлюємо глобальний оптимум */
        if (current_sum > max_sum) {
            max_sum = current_sum;
        }
    }

    return max_sum;
}
