#include <stdio.h>
#include <stddef.h>

static void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

static size_t median_of_three(int *arr, size_t lo, size_t hi) {
    size_t mid = lo + (hi - lo) / 2;
    if (arr[mid] < arr[lo])  swap(&arr[lo], &arr[mid]);
    if (arr[hi] < arr[lo])   swap(&arr[lo], &arr[hi]);
    if (arr[hi] < arr[mid])  swap(&arr[mid], &arr[hi]);
    return mid;
}

void quicksort(int *arr, size_t lo, size_t hi) {
    while (lo < hi) {
        size_t pivot_idx = median_of_three(arr, lo, hi);
        int pivot = arr[pivot_idx];
        
        size_t i = lo - 1;
        size_t j = hi + 1;
        
        while (1) {
            do { i++; } while (arr[i] < pivot);
            do { j--; } while (arr[j] > pivot);
            if (i >= j) break;
            swap(&arr[i], &arr[j]);
        }
        
        /* Хвостова рекурсія для меншої частини — гарантія O(log n) стеку */
        if (j - lo < hi - j) {
            quicksort(arr, lo, j);
            lo = j + 1;
        } else {
            quicksort(arr, j + 1, hi);
            hi = j;
        }
    }
}
