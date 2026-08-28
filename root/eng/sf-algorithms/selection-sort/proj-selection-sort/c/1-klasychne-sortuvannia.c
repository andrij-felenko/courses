#include <stddef.h>
#include <stdbool.h>

/*
 * Класичне сортування вибором для масиву цілих чисел.
 * Не виконує фізичний swap, якщо мінімум вже стоїть на поточній позиції.
 */
void selection_sort_int(int *arr, size_t n) {
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
            int temp = arr[i];
            arr[i] = arr[min_idx];
            arr[min_idx] = temp;
        }
    }
}

/*
 * Універсальне сортування вибором для довільного типу даних через void* та компаратор.
 */
typedef int (*comparator_t)(const void *, const void *);

void selection_sort_generic(void *base, size_t num, size_t size, comparator_t cmp) {
    if (base == NULL || num < 2 || size == 0 || cmp == NULL) {
        return;
    }

    char *bytes = (char *)base;

    for (size_t i = 0; i < num - 1; ++i) {
        size_t min_idx = i;

        for (size_t j = i + 1; j < num; ++j) {
            void *elem_j = bytes + (j * size);
            void *elem_min = bytes + (min_idx * size);

            if (cmp(elem_j, elem_min) < 0) {
                min_idx = j;
            }
        }

        if (min_idx != i) {
            char *p1 = bytes + (i * size);
            char *p2 = bytes + (min_idx * size);

            for (size_t k = 0; k < size; ++k) {
                char tmp = p1[k];
                p1[k] = p2[k];
                p2[k] = tmp;
            }
        }
    }
}
