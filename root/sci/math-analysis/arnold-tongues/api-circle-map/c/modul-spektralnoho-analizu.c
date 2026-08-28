typedef struct {
    size_t fft_size;
    double *real_spectrum;
    double *imag_spectrum;
    double dominant_frequency;
} circle_map_spectrum_t;

/**
 * @brief Обчислює спектр потужності фазової послідовності.
 */
circle_map_status_t circle_map_compute_spectrum(
    const circle_map_config_t *cfg,
    size_t fft_size,
    circle_map_spectrum_t *out_spectrum
);
