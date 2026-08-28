// Ідіоматична типобезпечна обгортка властивості в C++
template <typename T>
class Property {
    T value_{};
public:
    constexpr Property() = default;
    constexpr explicit Property(T val) : value_(std::move(val)) {}
    constexpr const T& get() const noexcept { return value_; }
    constexpr void set(T val) noexcept { value_ = std::move(val); }
};
