template <typename T, std::size_t N>
struct array {
    T elements_[N];

    constexpr std::size_t size() const noexcept { return N; }
    constexpr T* data() noexcept { return elements_; }
    constexpr const T* data() const noexcept { return elements_; }
    constexpr T& operator[](std::size_t index) noexcept { return elements_[index]; }
    constexpr const T& operator[](std::size_t index) const noexcept { return elements_[index]; }
};
