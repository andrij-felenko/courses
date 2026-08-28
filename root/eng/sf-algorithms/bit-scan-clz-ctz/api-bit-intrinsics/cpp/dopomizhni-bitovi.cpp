// В C++20 еквіваленти виражаються через стандартні шаблони
template <std::unsigned_integral T>
[[nodiscard]] constexpr int find_first_set(T x) noexcept {
    return x == 0 ? 0 : std::countr_zero(x) + 1;
}

template <std::unsigned_integral T>
[[nodiscard]] constexpr bool parity(T x) noexcept {
    return (std::popcount(x) % 2) != 0;
}
