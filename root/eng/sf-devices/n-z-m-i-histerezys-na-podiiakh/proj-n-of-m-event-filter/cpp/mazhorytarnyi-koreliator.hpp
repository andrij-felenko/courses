/**
 * @brief Шаблонний C++20 корелятор послідовностей
 */
template <std::size_t M, uint32_t Pattern, std::size_t Threshold>
    requires (M <= 32 && Threshold <= M)
[[nodiscard]] constexpr bool MatchPattern(uint32_t window) noexcept {
    constexpr uint32_t Mask = (M == 32) ? 0xFFFFFFFFU : ((1U << M) - 1U);
    const uint32_t diff = (window ^ Pattern) & Mask;
    const auto mismatches = static_cast<std::size_t>(std::popcount(diff));
    return (M - mismatches) >= Threshold;
}
