template <class T>
class optional {
public:
    constexpr optional() noexcept;
    constexpr optional(nullopt_t) noexcept;
    constexpr optional(const T& value);
    constexpr optional(T&& value);

    constexpr bool has_value() const noexcept;
    constexpr explicit operator bool() const noexcept;

    constexpr T& value() &; // Кидає std::bad_optional_access у разі порожнечі
    constexpr const T& value() const &;

    constexpr T& operator*() & noexcept; // Доступ без перевірки (UB, якщо порожній)
    constexpr const T* operator->() const noexcept;

    template <class U>
    constexpr T value_or(U&& default_value) const&;

    void reset() noexcept;
    template <class... Args>
    T& emplace(Args&&... args);
};
