#include <stddef.h>

/*
 * Стійке сортування вибором (замість swap виконується зсув елементів).
 * Зберігає відносний порядок однакових елементів.
 */
void stable_selection_sort(int *arr, size_t n) {
    if (arr == NULL || n < 2) {
        return;
    }

    for (size_t i = 0; i < n - 1; ++i) {
        size_t min_idx = i;

        for (size_t j = i + 1; j < n; ++j) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }

        if (min_idx != i) {
            int key = arr[min_idx];
            for (size_t k = min_idx; k > i; --k) {
                arr[k] = arr[k - 1];
            }
            arr[i] = key;
        }
    }
}
