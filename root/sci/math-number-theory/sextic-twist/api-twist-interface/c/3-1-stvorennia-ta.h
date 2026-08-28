/**
 * @brief Ініціалізує контекст твістованої кривої E'
 * @param ctx Повертає вказівник на створений контекст
 * @param curve_id Ідентифікатор кривої (BN254 = 1, BLS12_381 = 2)
 * @param twist_type Тип твісту (D_TYPE = 0, M_TYPE = 1)
 * @return TWIST_SUCCESS у разі успіху
 */
twist_status_t twist_ctx_init(
    twist_ctx_t** ctx,
    uint32_t curve_id,
    uint32_t twist_type
);

/**
 * @brief Звільняє ресурси контексту кривої
 */
void twist_ctx_free(twist_ctx_t* ctx);
