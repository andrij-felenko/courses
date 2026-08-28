void bubble_sort_last_swap(int *arr, size_t n) {
    if (n < 2) return;
    size_t limit = n - 1;

    while (limit > 0) {
        size_t new_limit = 0;
        for (size_t j = 0; j < limit; ++j) {
            if (arr[j] > arr[j + 1]) {
                swap_int(&arr[j], &arr[j + 1]);
                new_limit = j;
            }
        }
        limit = new_limit;
    }
}
