/* Вразлива реалізація на C++: вихід за першим незбігом */
[[nodiscard]] int naive_memcmp(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    const size_t len = std::min(a.size(), b.size());
    for (size_t i = 0; i < len; ++i) {
        if (a[i] != b[i]) {
            return static_cast<int>(a[i]) - static_cast<int>(b[i]);
        }
    }
    return static_cast<int>(a.size()) - static_cast<int>(b.size());
}
