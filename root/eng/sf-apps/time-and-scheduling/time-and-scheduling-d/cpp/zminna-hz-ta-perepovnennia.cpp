/* Безпечне порівняння лічильників тіків у C++20: */
template <std::integral T>
[[nodiscard]] constexpr bool time_after(T a, T b) noexcept {
    using SignedT = std::make_signed_t<T>;
    return static_cast<SignedT>(b - a) < 0;
}

template <std::integral T>
[[nodiscard]] constexpr bool time_before(T a, T b) noexcept {
    return time_after(b, a);
}
