#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MERGE_INSERTION_CUTOFF 16

/* Локальне сортування вставками для підмасиву arr[lo..hi] */
static void insertion_sort_range(int *arr, size_t lo, size_t hi) {
    for (size_t i = lo + 1; i <= hi; ++i) {
        int key = arr[i];
        size_t j = i;
        while (j > lo && arr[j - 1] > key) {
            arr[j] = arr[j - 1];
            --j;
        }
        arr[j] = key;
    }
}

/* Злиття двох впорядкованих підмасивів arr[lo..mid] та arr[mid+1..hi] */
static void merge(int *arr, int *aux, size_t lo, size_t mid, size_t hi) {
    /* Копіюємо робочий діапазон у допоміжний буфер */
    for (size_t k = lo; k <= hi; ++k) {
        aux[k] = arr[k];
    }

    size_t i = lo;
    size_t j = mid + 1;
    size_t k = lo;

    /* Двопоінтерне злиття зі збереженням стійкості (<=) */
    while (i <= mid && j <= hi) {
        if (aux[i] <= aux[j]) {
            arr[k++] = aux[i++];
        } else {
            arr[k++] = aux[j++];
        }
    }

    /* Докопіювання залишку лівої частини (якщо права вичерпалася) */
    while (i <= mid) {
        arr[k++] = aux[i++];
    }
    /* Залишок правої частини вже стоїть на своїх місцях у масиві arr */
}

/* Внутрішня рекурсивна функція */
static void merge_sort_recursive(int *arr, int *aux, size_t lo, size_t hi) {
    if (hi - lo + 1 <= MERGE_INSERTION_CUTOFF) {
        insertion_sort_range(arr, lo, hi);
        return;
    }

    size_t mid = lo + (hi - lo) / 2;
    merge_sort_recursive(arr, aux, lo, mid);
    merge_sort_recursive(arr, aux, mid + 1, hi);

    /* Оптимізація: пропуск злиття, якщо половини вже впорядковані */
    if (arr[mid] <= arr[mid + 1]) {
        return;
    }

    merge(arr, aux, lo, mid, hi);
}

/* Публічний інтерфейс сортування злиттям */
bool merge_sort(int *arr, size_t n) {
    if (!arr || n <= 1) {
        return true;
    }

    int *aux = (int *)malloc(n * sizeof(int));
    if (!aux) {
        return false; /* Помилка виділення пам'яті */
    }

    merge_sort_recursive(arr, aux, 0, n - 1);
    free(aux);
    return true;
}
