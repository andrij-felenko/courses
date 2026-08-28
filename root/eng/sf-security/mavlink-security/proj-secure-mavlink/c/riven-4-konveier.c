typedef enum {
    VERIFY_SUCCESS = 0,
    VERIFY_ERR_BAD_CRC,
    VERIFY_ERR_UNSIGNED_REJECTED,
    VERIFY_ERR_REPLAY_ATTACK,
    VERIFY_ERR_BAD_SIGNATURE,
    VERIFY_ERR_STREAM_OVERFLOW
} verify_result_t;

verify_result_t verify_mavlink_packet(
    const uint8_t *frame,
    size_t frame_len,
    stream_table_t *streams,
    const uint8_t *secret_key,
    uint8_t crc_extra,
    bool (*accept_unsigned_cb)(uint32_t msgid)
) {
    if (frame_len < 12) return VERIFY_ERR_BAD_CRC;

    uint8_t payload_len = frame[1];
    uint8_t incompat_flags = frame[2];
    uint8_t sysid = frame[5];
    uint8_t compid = frame[6];
    uint32_t msgid = frame[7] | ((uint32_t)frame[8] << 8) | ((uint32_t)frame[9] << 16);

    // 1. Перевірка контрольної суми CRC-16
    uint16_t expected_crc = frame[10 + payload_len] | ((uint16_t)frame[10 + payload_len + 1] << 8);
    uint16_t calc_crc = crc_calculate(&frame[1], 9 + payload_len);
    crc_accumulate(crc_extra, &calc_crc);
    if (calc_crc != expected_crc) return VERIFY_ERR_BAD_CRC;

    // 2. Обробка пакетів без криптографічного підпису
    if (!(incompat_flags & MAVLINK_IFLAG_SIGNED)) {
        if (accept_unsigned_cb && accept_unsigned_cb(msgid)) {
            return VERIFY_SUCCESS;
        }
        return VERIFY_ERR_UNSIGNED_REJECTED;
    }

    if (frame_len < (size_t)(10 + payload_len + 2 + 13)) return VERIFY_ERR_BAD_SIGNATURE;

    size_t trailer_offset = 12 + payload_len;
    uint8_t link_id = frame[trailer_offset];

    uint64_t incoming_ts = 0;
    for (int i = 0; i < 6; ++i) {
        incoming_ts |= ((uint64_t)frame[trailer_offset + 1 + i]) << (8 * i);
    }

    // 3. Пошук потоку та перевірка на Replay-атаку
    signing_stream_entry_t *stream = stream_table_get(streams, sysid, compid, link_id);
    if (!stream) return VERIFY_ERR_STREAM_OVERFLOW;

    if (stream->last_timestamp != 0 && incoming_ts <= stream->last_timestamp) {
        return VERIFY_ERR_REPLAY_ATTACK;
    }

    // 4. Розрахунок та побайтова звірка SHA-256
    uint8_t hash_input[300];
    memcpy(hash_input, secret_key, 32);
    memcpy(hash_input + 32, frame, 10 + payload_len + 2 + 7);

    uint8_t digest[32];
    sha256_compute(hash_input, 51 + payload_len, digest);

    int cmp = secure_memcmp(&frame[trailer_offset + 7], digest, 6);
    secure_zeroize(hash_input, sizeof(hash_input));
    secure_zeroize(digest, sizeof(digest));

    if (cmp != 0) return VERIFY_ERR_BAD_SIGNATURE;

    // 5. Оновлюємо стан успішного потоку
    stream->last_timestamp = incoming_ts;
    return VERIFY_SUCCESS;
}
