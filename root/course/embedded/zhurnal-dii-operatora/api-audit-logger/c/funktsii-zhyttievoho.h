/* Структура дескриптора контексту логера аудиту */
typedef struct {
    const audit_flash_hal_t *hal;
    uint64_t current_seq_id;
    uint32_t active_sector_idx;
    uint32_t next_slot_offset;
    uint8_t  last_hash[AUDIT_HASH_SIZE];
    bool     initialized;
} audit_context_t;

/*
 * audit_logger_init:
 *   Ініціалізує контекст, сканує Flash-пам'ять, знаходить активний сектор,
 *   відновлює Sequence ID та останній валідний хеш ланцюга.
 */
audit_status_t audit_logger_init(audit_context_t *ctx, const audit_flash_hal_t *hal);

/*
 * audit_logger_record_command:
 *   Формує новий запис аудиту, прив'язує його до попереднього хешу,
 *   обчислює SHA-256 і атомарно записує кадр у відкритий слот Flash.
 */
audit_status_t audit_logger_record_command(
    audit_context_t *ctx,
    uint64_t timestamp_utc_ms,
    uint64_t operator_id,
    uint16_t command_id,
    uint8_t subsystem_id,
    audit_flags_t flags,
    const uint8_t *payload,
    uint8_t payload_len,
    uint64_t *out_seq_id
);

/*
 * audit_logger_update_ack:
 *   Фіксує результат виконання раніше зареєстрованої команди (ACK).
 */
audit_status_t audit_logger_update_ack(
    audit_context_t *ctx,
    uint64_t target_seq_id,
    uint64_t timestamp_utc_ms,
    audit_exec_status_t exec_status,
    uint32_t error_code
);

/*
 * audit_logger_verify_chain:
 *   Зчитує всі записи від TAIL до HEAD та перевіряє неперервність ланцюга SHA-256.
 *   Повертає AUDIT_OK якщо підробок немає, або AUDIT_ERR_CHAIN_CORRUPTED із
 *   номером скомпрометованого запису в out_corrupted_seq.
 */
audit_status_t audit_logger_verify_chain(
    const audit_context_t *ctx,
    uint64_t *out_corrupted_seq
);
