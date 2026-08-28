void quicksort_bounded_stack(int *arr, size_t lo, size_t hi) {
    while (lo < hi) {
        size_t p = partition_hoare(arr, lo, hi);
        
        /* Спочатку рекурсивно сортуємо МЕНШУ частину */
        if (p - lo < hi - p) {
            quicksort_bounded_stack(arr, lo, p);
            lo = p + 1; /* більшу частину сортуємо в циклі */
        } else {
            quicksort_bounded_stack(arr, p + 1, hi);
            hi = p; /* більшу частину сортуємо в циклі */
        }
    }
}
