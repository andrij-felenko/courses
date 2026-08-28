#include <stdio.h>
#include <limits.h>

/* Структура для повернення числового результату та координат підмасиву */
typedef struct {
    long long max_sum;
    int start_index;
    int end_index;
} SubarrayResult;

SubarrayResult kadane_1d_with_indices(const int* arr, int n) {
    SubarrayResult res;
    if (arr == NULL || n <= 0) {
        res.max_sum = 0;
        res.start_index = -1;
        res.end_index = -1;
        return res;
    }

    long long current_sum = arr[0];
    long long max_sum = arr[0];
    int current_start = 0;
    int best_start = 0;
    int best_end = 0;

    for (int i = 1; i < n; ++i) {
        if (current_sum < 0) {
            /* Відкидаємо від'ємний накопичений тягар */
            current_sum = arr[i];
            current_start = i;
        } else {
            /* Продовжуємо накопичення суми */
            current_sum += arr[i];
        }

        /* Оновлення глобального оптимуму */
        if (current_sum > max_sum) {
            max_sum = current_sum;
            best_start = current_start;
            best_end = i;
        }
    }

    res.max_sum = max_sum;
    res.start_index = best_start;
    res.end_index = best_end;
    return res;
}
