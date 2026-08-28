#include <stddef.h>

void double_selection_sort(int *arr, size_t n) {
    if (arr == NULL || n < 2) {
        return;
    }

    size_t left = 0;
    size_t right = n - 1;

    while (left < right) {
        size_t min_idx = left;
        size_t max_idx = left;

        for (size_t i = left; i <= right; ++i) {
            if (arr[i] < arr[min_idx]) {
                min_idx = i;
            }
            if (arr[i] > arr[max_idx]) {
                max_idx = i;
            }
        }

        /* Обмін мінімуму з лівою межею */
        if (min_idx != left) {
            int temp = arr[left];
            arr[left] = arr[min_idx];
            arr[min_idx] = temp;
        }

        /* Пастка: якщо максимум був на позиції left, він перемістився на min_idx */
        if (max_idx == left) {
            max_idx = min_idx;
        }

        /* Обмін максимуму з правою межею */
        if (max_idx != right) {
            int temp = arr[right];
            arr[right] = arr[max_idx];
            arr[max_idx] = temp;
        }

        left++;
        right--;
    }
}
