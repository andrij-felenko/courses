// Виклик функції шифрування AES-GCM (на базі апаратного блоку або криптобібліотеки)
int aes_gcm_encrypt(
    const uint8_t *key,
    const uint8_t *iv, size_t iv_len,
    const uint8_t *aad, size_t aad_len,
    const uint8_t *input, size_t input_len,
    uint8_t *output,
    uint8_t *tag, size_t tag_len
);

uint16_t pack_encrypted_mavlink_tunnel(
    uint8_t *out_frame,
    uint8_t target_sys,
    uint8_t target_comp,
    const uint8_t *plain_mavlink_msg,
    size_t msg_len,
    const uint8_t *aes_key,
    uint64_t *inout_nonce_counter
) {
    if (msg_len > 100) return 0; // Максимальна місткість буфера TUNNEL payload (128 - 12 - 16 = 100 байт)

    mavlink_tunnel_t tunnel = {0};
    tunnel.payload_type = 100; // Користувацький тип: AES-256-GCM Encapsulation
    tunnel.target_system = target_sys;
    tunnel.target_component = target_comp;

    // 1. Формуємо 12-байтовий Nonce з монотонного лічильника
    (*inout_nonce_counter)++;
    uint8_t iv[12] = {0};
    memcpy(iv, inout_nonce_counter, sizeof(uint64_t));
    memcpy(tunnel.payload, iv, 12);

    // 2. Шифруємо дані та отримуємо 16-байтовий тег автентичності
    uint8_t tag[16];
    aes_gcm_encrypt(
        aes_key,
        iv, 12,
        NULL, 0,
        plain_mavlink_msg, msg_len,
        &tunnel.payload[12],
        tag, 16
    );

    memcpy(&tunnel.payload[12 + msg_len], tag, 16);
    tunnel.payload_length = (uint8_t)(12 + msg_len + 16);

    // 3. Кодуємо у стандартне повідомлення TUNNEL
    mavlink_message_t msg;
    mavlink_msg_tunnel_encode(255, 190, &msg, &tunnel);
    return mavlink_msg_to_send_buffer(out_frame, &msg);
}
