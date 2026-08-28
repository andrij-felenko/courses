namespace std {

template <class E>
class unexpected {
public:
    constexpr unexpected(const unexpected&) = default;
    constexpr unexpected(unexpected&&) = default;
    template <class... Args>
    constexpr explicit unexpected(in_place_t, Args&&... args);
    constexpr explicit unexpected(E e);

    constexpr const E& error() const & noexcept;
    constexpr E& error() & noexcept;
    constexpr const E&& error() const && noexcept;
    constexpr E&& error() && noexcept;

    constexpr void swap(unexpected& other) noexcept(is_nothrow_swappable_v<E>);
};

template <class T, class E>
class expected {
public:
    using value_type = T;
    using error_type = E;
    using unexpected_type = unexpected<E>;

    // Конструктори
    constexpr expected();
    constexpr expected(const expected&);
    constexpr expected(expected&&) noexcept(/* ... */);
    template <class U = T>
    constexpr explicit(/* ... */) expected(U&& v);
    template <class G>
    constexpr explicit(/* ... */) expected(const unexpected<G>& e);
    template <class G>
    constexpr explicit(/* ... */) expected(unexpected<G>&& e);

    // Спостереження стану
    constexpr bool has_value() const noexcept;
    constexpr explicit operator bool() const noexcept;

    // Доступ до значення
    constexpr const T& value() const &;
    constexpr T& value() &;
    constexpr const T&& value() const &&;
    constexpr T&& value() &&;

    // Доступ до помилки
    constexpr const E& error() const & noexcept;
    constexpr E& error() & noexcept;
    constexpr const E&& error() const && noexcept;
    constexpr E&& error() && noexcept;

    // Альтернативні значення
    template <class U>
    constexpr T value_or(U&& default_value) const &;
    template <class U>
    constexpr T value_or(U&& default_value) &&;

    // Монадичні операції конвеєра
    template <class F>
    constexpr auto and_then(F&& f) &;
    template <class F>
    constexpr auto and_then(F&& f) const &;
    template <class F>
    constexpr auto and_then(F&& f) &&;
    template <class F>
    constexpr auto and_then(F&& f) const &&;

    template <class F>
    constexpr auto transform(F&& f) &;
    template <class F>
    constexpr auto transform(F&& f) const &;
    template <class F>
    constexpr auto transform(F&& f) &&;
    template <class F>
    constexpr auto transform(F&& f) const &&;

    template <class F>
    constexpr auto or_else(F&& f) &;
    template <class F>
    constexpr auto or_else(F&& f) const &;
    template <class F>
    constexpr auto or_else(F&& f) &&;
    template <class F>
    constexpr auto or_else(F&& f) const &&;

    template <class F>
    constexpr auto transform_error(F&& f) &;
    template <class F>
    constexpr auto transform_error(F&& f) const &;
    template <class F>
    constexpr auto transform_error(F&& f) &&;
    template <class F>
    constexpr auto transform_error(F&& f) const &&;
};

// Спеціалізація для void (коли операція не продукує результату при успіху)
template <class E>
class expected<void, E> {
public:
    using value_type = void;
    using error_type = E;
    using unexpected_type = unexpected<E>;

    constexpr expected() noexcept;
    constexpr void value() const; // генерує bad_expected_access<E>, якщо помилка
    constexpr const E& error() const & noexcept;
    constexpr E& error() & noexcept;
    constexpr const E&& error() const && noexcept;
    constexpr E&& error() && noexcept;

    constexpr bool has_value() const noexcept;
    constexpr explicit operator bool() const noexcept;
};

} // namespace std
