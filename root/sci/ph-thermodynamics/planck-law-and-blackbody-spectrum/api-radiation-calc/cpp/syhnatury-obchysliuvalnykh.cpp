namespace blackbody {

/* 
 * Точкова спектральна яскравість B_λ(λ, T) у C++20
 */
[[nodiscard]] constexpr std::expected<double, Status> spectral_radiance(
    double lambda_meters, double temp_kelvin) noexcept;

/* 
 * Об'ємна спектральна густина енергії u_λ(λ, T)
 */
[[nodiscard]] constexpr std::expected<double, Status> energy_density(
    double lambda_meters, double temp_kelvin) noexcept;

/* 
 * Довжина хвилі максимуму випромінювання (Закон Віна)
 */
[[nodiscard]] constexpr std::expected<double, Status> wien_peak(
    double temp_kelvin) noexcept;

/* 
 * Комплексне інтегрування спектра у діапазоні
 */
[[nodiscard]] std::expected<BandResult, Status> integrate_band(
    double temp_kelvin,
    double lambda_min,
    double lambda_max,
    const IntegrationConfig& config = {}) noexcept;

} // namespace blackbody
