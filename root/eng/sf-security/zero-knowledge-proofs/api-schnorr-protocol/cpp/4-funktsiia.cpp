/**
 * @brief Автономно будує неінтерактивний доказ π = (r, s) за допомогою хешування Фіата — Шаміра.
 * 
 * @param params Параметри групи.
 * @param secret_x Приватний ключ доводжувача.
 * @param public_y Публічний ключ доводжувача y = g^x mod p.
 * @param out_proof Вихідна структура доказу.
 * @return ZkpStatus SUCCESS у разі успіху.
 */
ZkpStatus schnorr_nizk_prove(
    const SchnorrGroupParams* params,
    const uint8_t*            secret_x,
    const uint8_t*            public_y,
    SchnorrProof*             out_proof
);
