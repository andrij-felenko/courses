namespace algo {

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void bubble_sort_flag(std::span<T> data, Compare comp = Compare{}) {
    const std::size_t n = data.size();
    if (n < 2) return;

    for (std::size_t i = 0; i < n - 1; ++i) {
        bool swapped = false;
        for (std::size_t j = 0; j < n - 1 - i; ++j) {
            if (comp(data[j + 1], data[j])) {
                std::swap(data[j], data[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) {
            break;
        }
    }
}

} // namespace algo
