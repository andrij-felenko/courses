#include <stdio.h>
#include <stdlib.h>

static void swap_int(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

/* Тристороннє розбиття: виділяє групу однакових ключі за один прохід */
void quicksort_3way(int *arr, int lo, int hi) {
    if (lo >= hi) return;
    
    int pivot = arr[lo];
    int lt = lo;      /* arr[lo..lt-1] містить елементи < pivot */
    int gt = hi;      /* arr[gt+1..hi] містить елементи > pivot */
    int i = lo + 1;   /* arr[lt..i-1] містить елементи == pivot */
    
    while (i <= gt) {
        if (arr[i] < pivot) {
            swap_int(&arr[lt], &arr[i]);
            lt++;
            i++;
        } else if (arr[i] > pivot) {
            swap_int(&arr[i], &arr[gt]);
            gt--;
        } else {
            i++;
        }
    }
    
    /* Рекурсивний виклик вилучає групу arr[lt..gt], яка повністю впорядкована */
    quicksort_3way(arr, lo, lt - 1);
    quicksort_3way(arr, gt + 1, hi);
}
