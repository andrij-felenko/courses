/* 
 * Обчислення точкової спектральної яскравості B_λ(λ, T)
 * λ_meters — довжина хвилі в метрах
 * temp_kelvin — температура в Кельвінах
 * out_radiance — вказівник на змінну для запису результату (Вт/(м²·ст·м))
 */
bb_status_t bb_spectral_radiance(double lambda_meters, double temp_kelvin, double *out_radiance);

/* 
 * Обчислення спектральної густини енергії в об'ємі u_λ(λ, T)
 */
bb_status_t bb_energy_density(double lambda_meters, double temp_kelvin, double *out_density);

/* 
 * Пошук довжини хвилі максимуму (Закон зміщення Віна)
 */
bb_status_t bb_wien_peak(double temp_kelvin, double *out_lambda_max);

/* 
 * Комплексне інтегрування спектра у діапазоні [lambda_min, lambda_max]
 */
bb_status_t bb_integrate_band(
    double temp_kelvin,
    double lambda_min,
    double lambda_max,
    const bb_integration_config_t *config,
    bb_band_result_t *out_result
);
