template <typename T, typename Compare>
void binary_insertion_sort_impl(std::span<T> data, size_t start, size_t len, size_t sorted_len, Compare comp) {
    for (size_t i = sorted_len; i < len; ++i) {
        T key = std::move(data[start + i]);
        // Двійковий пошук правої межі (upper_bound) для збереження стійкості
        auto it = std::upper_bound(data.begin() + start, data.begin() + start + i, key, comp);
        size_t insert_pos = std::distance(data.begin(), it);
        
        // Зсув елементів вправо
        std::move_backward(data.begin() + insert_pos, data.begin() + start + i, data.begin() + start + i + 1);
        data[insert_pos] = std::move(key);
    }
}
