template <typename T, typename Compare>
size_t calculate_minrun_impl(size_t n) {
    size_t r = 0;
    while (n >= 64) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

template <typename T, typename Compare>
size_t count_and_reverse_run_impl(std::span<T> data, size_t start, Compare comp) {
    const size_t n = data.size();
    if (start >= n) return 0;
    if (start == n - 1) return 1;

    size_t run_len = 2;
    if (comp(data[start + 1], data[start])) {
        // Строго спадна серія
        while (start + run_len < n && comp(data[start + run_len], data[start + run_len - 1])) {
            run_len++;
        }
        std::reverse(data.begin() + start, data.begin() + start + run_len);
    } else {
        // Неспадна серія
        while (start + run_len < n && !comp(data[start + run_len], data[start + run_len - 1])) {
            run_len++;
        }
    }
    return run_len;
}
