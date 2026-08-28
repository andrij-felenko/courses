/**
 * @brief Генерує випадкове зобов'язання r = g^k mod p та зберігає секретний nonce k.
 * 
 * @param params Указатель на валідовані параметри групи.
 * @param out_k Вихідний буфер для збереження тимчасового secret nonce k (розмір q_len).
 * @param out_r Вихідний буфер для публічного зобов'язання r (розмір p_len).
 * @return ZkpStatus SUCCESS у разі успіху, інакше код помилки.
 */
ZkpStatus schnorr_commit(
    const SchnorrGroupParams* params,
    uint8_t*                  out_k,
    uint8_t*                  out_r
);
