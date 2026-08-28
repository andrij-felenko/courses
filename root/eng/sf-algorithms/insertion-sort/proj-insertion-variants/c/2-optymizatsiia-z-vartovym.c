#include <stddef.h>

/* Сортування вставками з вартовим елементом (Sentinel Insertion Sort) */
void sentinel_insertion_sort(int *arr, size_t n) {
    if (arr == NULL || n <= 1) {
        return;
    }

    /* Фаза 1: Знаходимо мінімальний елемент і ставимо його на початок (вартовий) */
    size_t min_idx = 0;
    for (size_t i = 1; i < n; ++i) {
        if (arr[i] < arr[min_idx]) {
            min_idx = i;
        }
    }

    if (min_idx != 0) {
        int tmp = arr[0];
        arr[0] = arr[min_idx];
        arr[min_idx] = tmp;
    }

    /* Фаза 2: Сортуємо залишок без перевірки лівої межі масиву */
    for (size_t i = 2; i < n; ++i) {
        int key = arr[i];
        size_t j = i;

        /* Умова j > 0 більше не потрібна: arr[0] <= key завжди! */
        while (arr[j - 1] > key) {
            arr[j] = arr[j - 1];
            --j;
        }
        arr[j] = key;
    }
}
