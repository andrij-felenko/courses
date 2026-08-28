#include <stdio.h>
#include <limits.h>

long long kadane_circular(const int* arr, int n) {
    if (arr == NULL || n <= 0) {
        return 0;
    }

    long long total_sum = arr[0];
    long long curr_max = arr[0], max_kadane = arr[0];
    long long curr_min = arr[0], min_kadane = arr[0];

    for (int i = 1; i < n; ++i) {
        int x = arr[i];
        total_sum += x;

        /* Біжучий максимум Кадане */
        curr_max = (curr_max + x > x) ? curr_max + x : x;
        if (curr_max > max_kadane) {
            max_kadane = curr_max;
        }

        /* Біжучий мінімум Кадане */
        curr_min = (curr_min + x < x) ? curr_min + x : x;
        if (curr_min < min_kadane) {
            min_kadane = curr_min;
        }
    }

    /* Критична гранична умова: якщо всі числа від'ємні */
    if (max_kadane < 0) {
        return max_kadane;
    }

    long long circular_max = total_sum - min_kadane;
    return (circular_max > max_kadane) ? circular_max : max_kadane;
}
