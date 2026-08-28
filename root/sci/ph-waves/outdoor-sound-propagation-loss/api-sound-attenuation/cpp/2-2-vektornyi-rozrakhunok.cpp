namespace acoustic {

/**
 * @brief Безоб'єктний векторний розрахунок із використанням std::span.
 */
[[nodiscard]] std::vector<double> calculate_spectrum(
    const Environment& env,
    std::span<const double> frequencies_hz
);

} // namespace acoustic
