void clear() noexcept {
    if constexpr (!std::is_trivially_destructible_v<T>) {
        while (!empty()) {
            pop();
        }
    }
    head_ = 0;
    tail_ = 0;
    size_ = 0;
}
