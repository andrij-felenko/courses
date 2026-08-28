// Підписання вихідного повідомлення та запис повного кадру в буфер
uint16_t mavlink_sign_packet(
    mavlink_channel_t chan,
    uint8_t *out_buffer,
    const mavlink_message_t *msg,
    mavlink_signing_t *signing_ctx
);

// Перевірка підпису вхідного повідомлення
bool mavlink_check_signature(
    const mavlink_message_t *msg,
    const mavlink_status_t *status,
    mavlink_signing_t *signing_ctx
);

// Прототип функції зворотного виклику для вибіркового дозволу непідписаних повідомлень
typedef bool (*mavlink_accept_unsigned_t)(
    const mavlink_status_t *status,
    uint32_t msgid
);
