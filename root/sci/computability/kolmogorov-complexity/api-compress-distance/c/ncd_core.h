/* ncd_core.h — Сигнатури C API */

/* Ініціалізація конфігурації за замовчуванням */
ncd_config_t ncd_config_default(void);

/* Обчислення NCD для двох бінарних буферів */
ncd_error_t ncd_compute_pair(const ncd_config_t *config,
                             const uint8_t *buf_a, size_t size_a,
                             const uint8_t *buf_b, size_t size_b,
                             double *out_distance);

/* Обчислення симетричної матриці NCD для N буферів */
ncd_error_t ncd_compute_matrix(const ncd_config_t *config,
                               const uint8_t **buffers, const size_t *sizes,
                               size_t count,
                               double *out_matrix);
