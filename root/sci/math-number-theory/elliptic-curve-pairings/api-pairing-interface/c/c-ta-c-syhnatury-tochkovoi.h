/**
 * @brief Повертає канонічний генератор групи G1.
 * @param[out] out_generator Вказівник на точку G1 для запису результату.
 */
void bls12_381_g1_generator(bls12_381_g1_affine_t* out_generator);

/**
 * @brief Скалярне множення точки G1 на 256-бітовий скаляр [k]P у константному часі.
 * @param[out] result Точка результату [k]P.
 * @param[in] point Вхідна точка P.
 * @param[in] scalar_bytes Масив з 32 байтів скаляра k (big-endian).
 * @return BLS12_381_SUCCESS у разі успіху.
 */
bls12_381_status_t bls12_381_g1_scalar_mul(
    bls12_381_g1_projective_t* result,
    const bls12_381_g1_affine_t* point,
    const uint8_t scalar_bytes[32]
);

/**
 * @brief Перевіряє, чи належить точка P групи G1 до правильної підгрупи порядку r.
 * @param[in] point Точка для перевірки.
 * @return true якщо точка належить G1, інакше false.
 */
bool bls12_381_g1_is_in_correct_subgroup(const bls12_381_g1_affine_t* point);
