typedef struct {
    bool has_avx2_support;
    bool has_fp16_support;
    size_t simd_vector_width;
} circle_map_capabilities_t;

/**
 * @brief Отримує апаратні характеристики процесора.
 */
circle_map_status_t circle_map_get_capabilities(
    circle_map_capabilities_t *out_caps
);
