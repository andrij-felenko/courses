namespace algo {

template <typename T, typename Compare = std::less<T>>
void cocktail_shaker_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() < 2) return;
    std::size_t left = 0;
    std::size_t right = data.size() - 1;

    while (left < right) {
        std::size_t last_swap = left;

        for (std::size_t i = left; i < right; ++i) {
            if (comp(data[i + 1], data[i])) {
                std::swap(data[i], data[i + 1]);
                last_swap = i;
            }
        }
        right = last_swap;
        if (left >= right) break;

        last_swap = right;

        for (std::size_t i = right; i > left; --i) {
            if (comp(data[i], data[i - 1])) {
                std::swap(data[i - 1], data[i]);
                last_swap = i;
            }
        }
        left = last_swap;
    }
}

} // namespace algo
