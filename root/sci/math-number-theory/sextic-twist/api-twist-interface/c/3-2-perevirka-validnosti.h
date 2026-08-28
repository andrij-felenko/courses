/**
 * @brief Перевіряє, чи задовольняє точка рівняння твістованої кривої E'
 * @param ctx Контекст кривої
 * @param in_g2_uncompressed Буфер з координатами (x', y') над 𝔽_{p^2}
 * @return TWIST_SUCCESS якщо точка на кривій, TWIST_ERR_NOT_ON_CURVE інакше
 */
twist_status_t twist_g2_is_on_curve(
    const twist_ctx_t* ctx,
    const uint8_t* in_g2_uncompressed
);

/**
 * @brief Перевіряє належність точки до криптографічної підгрупи G₂ порядку r
 * @details Виконує множення r * Q' або оцінку ендоморфізму Фробеніуса Скотта
 * @param ctx Контекст кривої
 * @param in_g2_uncompressed Буфер точки (x', y')
 * @return TWIST_SUCCESS якщо r * Q' == O
 */
twist_status_t twist_g2_validate_subgroup(
    const twist_ctx_t* ctx,
    const uint8_t* in_g2_uncompressed
);
