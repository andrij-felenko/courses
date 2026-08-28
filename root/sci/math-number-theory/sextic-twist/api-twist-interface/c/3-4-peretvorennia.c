/**
 * @brief Обчислює розтвістовані коефіцієнти для кроку алгоритму Міллера
 * @details Переводить Q' = (x', y') ∈ E'(𝔽_{p^2}) у розріджений елемент (x' w^2, y' w^3)
 * @param ctx Контекст кривої
 * @param out_x_coeff Вихідний коефіцієнт біля w^2 (в 𝔽_{p^2})
 * @param out_y_coeff Вихідний коефіцієнт біля w^3 (в 𝔽_{p^2})
 * @param in_g2_point Вхідна точка твістованої кривої
 * @return TWIST_SUCCESS
 */
twist_status_t twist_g2_untwist_for_miller(
    const twist_ctx_t* ctx,
    uint8_t* out_x_coeff,
    uint8_t* out_y_coeff,
    const uint8_t* in_g2_point
);
