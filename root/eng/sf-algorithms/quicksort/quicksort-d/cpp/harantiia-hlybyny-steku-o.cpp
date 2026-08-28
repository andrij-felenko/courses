template <typename T, typename Compare = std::less<T>>
void quicksort_bounded_stack(std::span<T> data, Compare comp = Compare{}) {
    while (data.size() > 1) {
        size_t p = partition_hoare(data, comp);
        
        std::span<T> left = data.subspan(0, p + 1);
        std::span<T> right = data.subspan(p + 1);
        
        if (left.size() < right.size()) {
            quicksort_bounded_stack(left, comp);
            data = right;
        } else {
            quicksort_bounded_stack(right, comp);
            data = left;
        }
    }
}
