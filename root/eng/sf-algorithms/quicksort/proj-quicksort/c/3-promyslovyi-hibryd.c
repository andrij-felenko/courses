#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static void swap_int(int *a, int *b) {
    int tmp = *a; *a = *b; *b = tmp;
}

/* Сортування вставленням для малих відрізків n <= 16 */
static void insertion_sort(int *arr, size_t n) {
    for (size_t i = 1; i < n; i++) {
        int key = arr[i];
        size_t j = i;
        while (j > 0 && arr[j - 1] > key) {
            arr[j] = arr[j - 1];
            j--;
        }
        arr[j] = key;
    }
}

/* Просіювання вниз для страхувального Heapsort */
static void sift_down(int *arr, size_t root, size_t n) {
    while (2 * root + 1 < n) {
        size_t child = 2 * root + 1;
        if (child + 1 < n && arr[child] < arr[child + 1]) {
            child++;
        }
        if (arr[root] < arr[child]) {
            swap_int(&arr[root], &arr[child]);
            root = child;
        } else {
            break;
        }
    }
}

static void heapsort_fallback(int *arr, size_t n) {
    if (n < 2) return;
    for (size_t i = n / 2; i > 0; i--) {
        sift_down(arr, i - 1, n);
    }
    for (size_t i = n - 1; i > 0; i--) {
        swap_int(&arr[0], &arr[i]);
        sift_down(arr, 0, i);
    }
}

static size_t partition_lomuto(int *arr, size_t n) {
    int pivot = arr[n - 1];
    size_t i = 0;
    for (size_t j = 0; j < n - 1; j++) {
        if (arr[j] <= pivot) {
            swap_int(&arr[i], &arr[j]);
            i++;
        }
    }
    swap_int(&arr[i], &arr[n - 1]);
    return i;
}

static void introsort_loop(int *arr, size_t n, int depth_limit) {
    while (n > 16) {
        if (depth_limit == 0) {
            /* Перемикання на Heapsort при загрозі O(n²) */
            heapsort_fallback(arr, n);
            return;
        }
        depth_limit--;
        size_t p = partition_lomuto(arr, n);
        
        introsort_loop(arr + p + 1, n - p - 1, depth_limit);
        n = p;
    }
}

void introsort(int *arr, size_t n) {
    if (n < 2) return;
    int depth_limit = (int)(2 * log2((double)n));
    introsort_loop(arr, n, depth_limit);
    insertion_sort(arr, n);
}
