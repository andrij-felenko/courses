namespace acoustic {

/**
 * @brief C++ ідіоматична обгортка з поверненням std::expected / std::optional.
 */
[[nodiscard]] std::optional<AttenuationResult> calculate_attenuation(
    const Environment& env,
    double frequency_hz
) noexcept;

} // namespace acoustic
