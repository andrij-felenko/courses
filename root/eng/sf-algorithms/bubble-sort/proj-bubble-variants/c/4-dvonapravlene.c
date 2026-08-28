void cocktail_shaker_sort(int *arr, size_t n) {
    if (n < 2) return;
    size_t left = 0;
    size_t right = n - 1;

    while (left < right) {
        size_t last_swap = left;

        // Прямий прохід: спливання максимуму праворуч
        for (size_t i = left; i < right; ++i) {
            if (arr[i] > arr[i + 1]) {
                swap_int(&arr[i], &arr[i + 1]);
                last_swap = i;
            }
        }
        right = last_swap;
        if (left >= right) break;

        last_swap = right;

        // Зворотний прохід: занурення мінімуму ліворуч
        for (size_t i = right; i > left; --i) {
            if (arr[i - 1] > arr[i]) {
                swap_int(&arr[i - 1], &arr[i]);
                last_swap = i;
            }
        }
        left = last_swap;
    }
}
