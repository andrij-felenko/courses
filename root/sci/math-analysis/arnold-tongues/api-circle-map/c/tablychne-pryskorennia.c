typedef struct {
    size_t table_size;
    const double *lut_values;
} circle_map_lut_config_t;

/**
 * @brief Ініціалізує та повертає конфігурацію LUT для прискорення.
 */
circle_map_status_t circle_map_init_lut(
    size_t table_size,
    circle_map_lut_config_t *out_lut
);
