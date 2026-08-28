#include <stddef.h>
#include <stdbool.h>

/* Класичне сортування вставками для масиву цілих чисел */
void insertion_sort_int(int *arr, size_t n) {
    if (arr == NULL || n <= 1) {
        return;
    }

    for (size_t i = 1; i < n; ++i) {
        int key = arr[i];
        size_t j = i;

        /* Зсуваємо елементи, що більші за key, праворуч.
           Уникаємо знакового переповнення індексу: перевіряємо j > 0 перед arr[j - 1] */
        while (j > 0 && arr[j - 1] > key) {
            arr[j] = arr[j - 1];
            --j;
        }
        arr[j] = key;
    }
}
