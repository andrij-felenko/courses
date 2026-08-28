#include "emergency_fw_header.h"
#include <string.h>

/* Апаратні та криптографічні залежності мікроконтролера */
extern uint32_t hw_efuse_read_security_version(void);
extern uint32_t hw_get_platform_id(void);
extern bool crypto_sha256(const uint8_t *data, uint32_t len, uint8_t *out_hash);
extern bool crypto_verify_signature(const uint8_t *pubkey, const uint8_t *hash, const uint8_t *sig);

emergency_validation_status_t emergency_validate_firmware(
    const emergency_fw_header_t *header,
    const uint8_t *payload_data,
    uint32_t payload_len,
    const uint8_t *root_pubkey
) {
    if (!header || !payload_data || !root_pubkey) {
        return EMERGENCY_VAL_ERR_BAD_MAGIC;
    }

    /* 1. Перевірка магічного числа 'EMGY' */
    if (header->magic != EMERGENCY_HEADER_MAGIC) {
        return EMERGENCY_VAL_ERR_BAD_MAGIC;
    }

    /* 2. Перевірка версії структури заголовка */
    if (header->header_version != EMERGENCY_HEADER_VERSION) {
        return EMERGENCY_VAL_ERR_UNSUPPORTED_VERSION;
    }

    /* 3. Звірка ідентифікатора апаратної платформи */
    if (header->target_hw_id != hw_get_platform_id()) {
        return EMERGENCY_VAL_ERR_HW_MISMATCH;
    }

    /* 4. Захист від атак відкату (Anti-Rollback) */
    uint32_t current_efuse_sec = hw_efuse_read_security_version();
    if (header->security_counter < current_efuse_sec) {
        return EMERGENCY_VAL_ERR_ROLLBACK_BLOCKED;
    }

    /* 5. Перевірка розміру корисного навантаження */
    if (header->payload_size != payload_len) {
        return EMERGENCY_VAL_ERR_PAYLOAD_BOUNDS;
    }

    /* 6. Обчислення SHA-256 корисного навантаження */
    uint8_t calculated_sha[EMERGENCY_SHA256_SIZE_BYTES];
    if (!crypto_sha256(payload_data, payload_len, calculated_sha)) {
        return EMERGENCY_VAL_ERR_HASH_MISMATCH;
    }

    if (memcmp(calculated_sha, header->payload_sha256, EMERGENCY_SHA256_SIZE_BYTES) != 0) {
        return EMERGENCY_VAL_ERR_HASH_MISMATCH;
    }

    /* 7. Верифікація цифрового підпису заголовка */
    uint8_t header_hash[EMERGENCY_SHA256_SIZE_BYTES];
    uint32_t signed_header_bytes = sizeof(emergency_fw_header_t) - EMERGENCY_SIG_SIZE_BYTES - sizeof(header->reserved);
    
    if (!crypto_sha256((const uint8_t*)header, signed_header_bytes, header_hash)) {
        return EMERGENCY_VAL_ERR_SIGNATURE_INVALID;
    }

    if (!crypto_verify_signature(root_pubkey, header_hash, header->header_signature)) {
        return EMERGENCY_VAL_ERR_SIGNATURE_INVALID;
    }

    return EMERGENCY_VAL_OK;
}
