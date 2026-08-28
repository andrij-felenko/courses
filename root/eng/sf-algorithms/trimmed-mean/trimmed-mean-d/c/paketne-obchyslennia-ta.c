#include <stddef.h>
#include <stdbool.h>

static void swap_doubles(double *a, double *b) {
    double temp = *a;
    *a = *b;
    *b = temp;
}

/* Розбиття Ломуто для знаходження k-ї порядкової статистики */
static size_t partition(double arr[], size_t left, size_t right, size_t pivot_idx) {
    double pivot_val = arr[pivot_idx];
    swap_doubles(&arr[pivot_idx], &arr[right]);
    size_t store_idx = left;

    for (size_t i = left; i < right; ++i) {
        if (arr[i] < pivot_val) {
            swap_doubles(&arr[store_idx], &arr[i]);
            store_idx++;
        }
    }
    swap_doubles(&arr[right], &arr[store_idx]);
    return store_idx;
}

/* Пошук n-го найменшого елемента за середній час O(N) */
static void quickselect(double arr[], size_t left, size_t right, size_t n) {
    while (left < right) {
        size_t pivot_idx = left + (right - left) / 2;
        pivot_idx = partition(arr, left, right, pivot_idx);

        if (n == pivot_idx) {
            return;
        } else if (n < pivot_idx) {
            right = pivot_idx - 1;
        } else {
            left = pivot_idx + 1;
        }
    }
}

/* Обчислення усіченого середнього за O(N) з частковою модифікацією arr */
bool trimmed_mean_batch(double arr[], size_t n, size_t k, double *result) {
    if (arr == NULL || result == NULL || n == 0 || 2 * k >= n) {
        return false;
    }

    /* Якщо k == 0, рахуємо звичайне середнє */
    if (k == 0) {
        double sum = 0.0;
        for (size_t i = 0; i < n; ++i) {
            sum += arr[i];
        }
        *result = sum / (double)n;
        return true;
    }

    /* Розміщуємо k найменших зліва */
    quickselect(arr, 0, n - 1, k);

    /* Розміщуємо k найбільших справа (індекс n - k - 1) */
    quickselect(arr, k + 1, n - 1, n - k - 1);

    /* Додаємо центральні елементи */
    double sum = 0.0;
    size_t count = n - 2 * k;
    for (size_t i = k; i < n - k; ++i) {
        sum += arr[i];
    }

    *result = sum / (double)count;
    return true;
}
