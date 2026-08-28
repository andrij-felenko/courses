/**
 * @brief Обчислює підтверджувальну відповідь s = (k + c * x) mod q.
 * 
 * @param params Указатель на параметри групи.
 * @param secret_x Приватний ключ доводжувача (розмір q_len).
 * @param k_nonce Тимчасовий secret nonce з фази 1 (розмір q_len).
 * @param challenge Випробовувальний виклик c (розмір q_len).
 * @param out_s Вихідний буфер для відповіді s (розмір q_len).
 * @return ZkpStatus SUCCESS у разі успіху.
 */
ZkpStatus schnorr_respond(
    const SchnorrGroupParams* params,
    const uint8_t*            secret_x,
    const uint8_t*            k_nonce,
    const uint8_t*            challenge,
    uint8_t*                  out_s
);
