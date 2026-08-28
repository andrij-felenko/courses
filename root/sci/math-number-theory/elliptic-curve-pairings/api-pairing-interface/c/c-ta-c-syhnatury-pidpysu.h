/**
 * @brief Генерує підпис BLS для повідомлення.
 * @param[out] out_signature Підпис σ = [sk] HashToG1(m) у групі G1 (48 байтів стиснуто).
 * @param[in] secret_key Секретний ключ sk (32 байти).
 * @param[in] msg Повідомлення для підпису.
 * @param[in] msg_len Довжина повідомлення.
 */
bls12_381_status_t bls_sign(
    uint8_t out_signature[48],
    const uint8_t secret_key[32],
    const uint8_t* msg,
    size_t msg_len
);

/**
 * @brief Перевіряє один підпис BLS: e(σ, P2) == e(H(m), PK).
 * @param[in] signature_bytes Стиснутий підпис σ (48 байтів).
 * @param[in] public_key_bytes Стиснутий відкритий ключ PK (96 байтів).
 * @param[in] msg Повідомлення.
 * @param[in] msg_len Довжина повідомлення.
 * @return BLS12_381_SUCCESS у разі успішної перевірки підпису.
 */
bls12_381_status_t bls_verify(
    const uint8_t signature_bytes[48],
    const uint8_t public_key_bytes[96],
    const uint8_t* msg,
    size_t msg_len
);
