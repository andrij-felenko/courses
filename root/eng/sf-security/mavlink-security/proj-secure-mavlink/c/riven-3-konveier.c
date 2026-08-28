#include <mavlink.h>

// Зовнішня функція розрахунку SHA-256
void sha256_compute(const uint8_t *data, size_t len, uint8_t *digest);

uint16_t sign_mavlink_packet(
    uint8_t *frame_buffer,
    size_t payload_len,
    uint8_t link_id,
    uint64_t *inout_timestamp,
    const uint8_t *secret_key,
    uint8_t crc_extra
) {
    // 1. Забезпечуємо строгу монотонність таймстемпу
    (*inout_timestamp)++;
    uint64_current_ts = *inout_timestamp;

    // 2. Встановлюємо прапорець підпису у полі incompat_flags (байт 2)
    frame_buffer[2] |= MAVLINK_IFLAG_SIGNED;

    // 3. Обчислюємо та записуємо 16-бітну контрольну суму кадру
    uint16_t crc = crc_calculate(&frame_buffer[1], 9 + payload_len);
    crc_accumulate(crc_extra, &crc);
    frame_buffer[10 + payload_len]     = (uint8_t)(crc & 0xFF);
    frame_buffer[10 + payload_len + 1] = (uint8_t)((crc >> 8) & 0xFF);

    // 4. Формуємо блок Link ID та 48-бітного Timestamp у трейлері
    size_t trailer_offset = 12 + payload_len;
    frame_buffer[trailer_offset] = link_id;
    for (int i = 0; i < 6; ++i) {
        frame_buffer[trailer_offset + 1 + i] = (uint8_t)((current_ts >> (8 * i)) & 0xFF);
    }

    // 5. Збираємо лінійний буфер для SHA-256 (розмір = 51 + payload_len)
    uint8_t hash_input[300];
    memcpy(hash_input, secret_key, 32);
    memcpy(hash_input + 32, frame_buffer, 10 + payload_len + 2 + 1 + 6);

    uint8_t digest[32];
    sha256_compute(hash_input, 51 + payload_len, digest);

    // 6. Записуємо перші 6 байтів обрізаного хешу
    memcpy(&frame_buffer[trailer_offset + 7], digest, 6);

    // Очищаємо конфіденційні буфери
    secure_zeroize(hash_input, sizeof(hash_input));
    secure_zeroize(digest, sizeof(digest));

    // Повна фізична довжина підписаного кадру
    return (uint16_t)(10 + payload_len + 2 + 13);
}
