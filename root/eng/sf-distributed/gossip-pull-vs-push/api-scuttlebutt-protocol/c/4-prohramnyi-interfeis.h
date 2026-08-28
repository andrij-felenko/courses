typedef enum {
    SCUT_STATUS_OK = 0,
    SCUT_ERR_TRUNCATED_PAYLOAD = 1,
    SCUT_ERR_CHECKSUM_MISMATCH = 2,
    SCUT_ERR_UNSUPPORTED_VERSION = 3,
    SCUT_ERR_BUFFER_OVERFLOW = 4
} ScuttlebuttStatus;

/* Формування первинного повідомлення SYN (Крок 1) */
ScuttlebuttStatus scuttlebutt_build_syn(
    uint32_t self_id,
    const DigestEntry *local_digests,
    size_t digest_count,
    uint8_t *out_buf,
    size_t out_capacity,
    size_t *out_size
);

/* Обробка SYN на стороні відповідача та формування ACK (Крок 2) */
ScuttlebuttStatus scuttlebutt_process_syn_and_build_ack(
    uint32_t self_id,
    const uint8_t *syn_payload,
    size_t syn_size,
    const DigestEntry *local_digests,
    size_t local_digest_count,
    uint8_t *out_ack_buf,
    size_t ack_capacity,
    size_t *ack_size
);

/* Обробка ACK на стороні ініціатора та формування ACK2 (Крок 3) */
ScuttlebuttStatus scuttlebutt_process_ack_and_build_ack2(
    uint32_t self_id,
    const uint8_t *ack_payload,
    size_t ack_size,
    uint8_t *out_ack2_buf,
    size_t ack2_capacity,
    size_t *ack2_size
);

/* Застосування фінального повідомлення ACK2 відповідачем */
ScuttlebuttStatus scuttlebutt_apply_ack2(
    uint32_t self_id,
    const uint8_t *ack2_payload,
    size_t ack2_size
);
