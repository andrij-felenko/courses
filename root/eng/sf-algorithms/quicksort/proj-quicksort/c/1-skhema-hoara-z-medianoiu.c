#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

static void swap_int(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

/* Обчислення медіани трьох: першого, середнього та останнього елементів */
static size_t median_of_three(int *arr, size_t lo, size_t hi) {
    size_t mid = lo + (hi - lo) / 2;
    if (arr[mid] < arr[lo])  swap_int(&arr[lo], &arr[mid]);
    if (arr[hi] < arr[lo])   swap_int(&arr[lo], &arr[hi]);
    if (arr[hi] < arr[mid])  swap_int(&arr[mid], &arr[hi]);
    return mid;
}

/* Розбиття за схемою Гоара */
static size_t partition_hoare(int *arr, size_t lo, size_t hi) {
    size_t pivot_idx = median_of_three(arr, lo, hi);
    int pivot = arr[pivot_idx];
    
    size_t i = lo - 1;
    size_t j = hi + 1;
    
    while (1) {
        do { i++; } while (arr[i] < pivot);
        do { j--; } while (arr[j] > pivot);
        
        if (i >= j) {
            return j;
        }
        swap_int(&arr[i], &arr[j]);
    }
}

/* Головна функція Quicksort з гарантією стеку O(log n) */
void quicksort_hoare(int *arr, size_t lo, size_t hi) {
    while (lo < hi) {
        size_t p = partition_hoare(arr, lo, hi);
        
        /* Спочатку рекурсивно сортуємо МЕНШУ частину, 
           а БІЛЬШУ обробляємо ітеративно у цьому ж циклі */
        if (p - lo < hi - p) {
            quicksort_hoare(arr, lo, p);
            lo = p + 1;
        } else {
            quicksort_hoare(arr, p + 1, hi);
            hi = p;
        }
    }
}
