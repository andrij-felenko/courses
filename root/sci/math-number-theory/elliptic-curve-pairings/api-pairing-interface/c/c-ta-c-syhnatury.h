/**
 * @brief Стискає точку G1 у 48-байтний масив.
 * @param[out] out_bytes Буфер розміром 48 байтів.
 * @param[in] point Точка для кодування.
 */
bls12_381_status_t bls12_381_g1_compress(
    uint8_t out_bytes[48],
    const bls12_381_g1_affine_t* point
);

/**
 * @brief Безпечно відображає довільне повідомлення у точку групи G1 (HashToG1).
 * @param[out] out_point Результат у групі G1.
 * @param[in] msg Вказівник на байтове повідомлення.
 * @param[in] msg_len Довжина повідомлення у байтах.
 * @param[in] dst Доменний розділювач контексту (Domain Separation Tag, DST).
 * @param[in] dst_len Довжина DST.
 */
bls12_381_status_t bls12_381_hash_to_g1(
    bls12_381_g1_projective_t* out_point,
    const uint8_t* msg,
    size_t msg_len,
    const uint8_t* dst,
    size_t dst_len
);
