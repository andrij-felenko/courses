namespace algo {

void bubble_sort_restricted_cpp(int * __restrict arr, std::size_t n) {
    if (n < 2) return;
    for (std::size_t i = 0; i < n - 1; ++i) {
        for (std::size_t j = 0; j < n - 1 - i; ++j) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

} // namespace algo
