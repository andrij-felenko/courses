/**
 * @brief C++20 адаптивний контролер порогів
 */
struct AdaptiveThresholdPolicy {
    static constexpr std::pair<uint8_t, uint8_t> Calculate(uint8_t m_window, uint32_t glitch_count) noexcept {
        if (glitch_count > 50U) {
            const uint8_t non = (m_window >= 8U) ? static_cast<uint8_t>(m_window - 1U) : m_window;
            return {non, 1U};
        }
        return {static_cast<uint8_t>((m_window * 3U) / 4U), static_cast<uint8_t>(m_window / 4U)};
    }
};
