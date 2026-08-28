/**
 * @brief Перевіряє тотожність g^s ≡ r * y^c (mod p).
 * 
 * @param params Параметри групи.
 * @param public_y Публічний ключ доводжувача y.
 * @param proof Структура доказу (r, s).
 * @return ZkpStatus SUCCESS якщо доказ дійсний, ERR_VERIFICATION_FAIL якщо некоректний.
 */
ZkpStatus schnorr_nizk_verify(
    const SchnorrGroupParams* params,
    const uint8_t*            public_y,
    const SchnorrProof*       proof
);
