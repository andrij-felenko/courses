/**
 * @brief Стискає точку G₂ з формату (x', y') у формат x' + біт знаку y'
 * @param ctx Контекст кривої
 * @param out_compressed Вихідний буфер розмінності FP2_BYTES
 * @param in_uncompressed Вхідна точка розмінності 2 * FP2_BYTES
 * @return TWIST_SUCCESS у разі успіху
 */
twist_status_t twist_g2_compress(
    const twist_ctx_t* ctx,
    uint8_t* out_compressed,
    const uint8_t* in_uncompressed
);

/**
 * @brief Відновлює нестиснену точку (x', y') зі стисненого буфера
 * @details Обчислює y'^2 = x'^3 + b_twist та знаходить квадратний корінь у 𝔽_{p^2}
 * @param ctx Контекст кривої
 * @param out_uncompressed Вихідний буфер 2 * FP2_BYTES
 * @param in_compressed Вхідний стиснений буфер FP2_BYTES
 * @return TWIST_SUCCESS або TWIST_ERR_DECOMPRESS_FAILED
 */
twist_status_t twist_g2_decompress(
    const twist_ctx_t* ctx,
    uint8_t* out_uncompressed,
    const uint8_t* in_compressed
);
