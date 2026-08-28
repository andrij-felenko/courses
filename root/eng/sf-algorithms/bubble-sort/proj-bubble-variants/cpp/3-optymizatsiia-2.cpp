namespace algo {

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void bubble_sort_last_swap(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() < 2) return;
    std::size_t limit = data.size() - 1;

    while (limit > 0) {
        std::size_t new_limit = 0;
        for (std::size_t j = 0; j < limit; ++j) {
            if (comp(data[j + 1], data[j])) {
                std::swap(data[j], data[j + 1]);
                new_limit = j;
            }
        }
        limit = new_limit;
    }
}

} // namespace algo
