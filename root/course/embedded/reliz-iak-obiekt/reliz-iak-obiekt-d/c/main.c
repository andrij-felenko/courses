#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FW_HEADER_MAGIC 0x46574D46U /* "FWMF" */

typedef struct {
    uint32_t magic_word;
    uint32_t header_version;
    uint32_t target_hw_id;
    uint8_t  hw_rev_min;
    uint8_t  hw_rev_max;
    uint16_t flags;
    uint8_t  ver_major;
    uint8_t  ver_minor;
    uint8_t  ver_patch;
    uint8_t  ver_pre_flags;
    uint32_t security_version;
    uint32_t payload_size;
    uint32_t load_address;
    uint8_t  payload_sha256[32];
    uint8_t  signature[64];
} __attribute__((packed)) firmware_header_t;

typedef enum {
    VERIFY_SUCCESS = 0,
    VERIFY_ERR_BAD_MAGIC = 1,
    VERIFY_ERR_HW_INCOMPATIBLE = 2,
    VERIFY_ERR_ROLLBACK_ATTACK = 3,
    VERIFY_ERR_INVALID_SIGNATURE = 4,
    VERIFY_ERR_HASH_MISMATCH = 5
} verify_result_t;

/* Зовнішні системні функції апаратної платформи */
extern uint32_t bsp_read_hw_platform_id(void);
extern uint8_t  bsp_read_pcb_revision(void);
extern uint32_t bsp_read_otp_security_counter(void);
extern const uint8_t* bsp_get_root_public_key(void);
extern int crypto_verify_ed25519(const uint8_t sig[64], const uint8_t *msg, size_t len, const uint8_t pk[32]);
extern void crypto_calc_sha256(const uint8_t *data, size_t len, uint8_t out_hash[32]);

verify_result_t verify_firmware_release(const firmware_header_t *hdr, const uint8_t *payload) {
    /* 1. Перевірка магічного числа */
    if (hdr->magic_word != FW_HEADER_MAGIC || hdr->header_version != 1U) {
        return VERIFY_ERR_BAD_MAGIC;
    }

    /* 2. Контроль сумісності із залізом */
    if (hdr->target_hw_id != bsp_read_hw_platform_id()) {
        return VERIFY_ERR_HW_INCOMPATIBLE;
    }
    uint8_t current_pcb_rev = bsp_read_pcb_revision();
    if (current_pcb_rev < hdr->hw_rev_min || current_pcb_rev > hdr->hw_rev_max) {
        return VERIFY_ERR_HW_INCOMPATIBLE;
    }

    /* 3. Захист від відкату (Anti-rollback) */
    if (hdr->security_version < bsp_read_otp_security_counter()) {
        return VERIFY_ERR_ROLLBACK_ATTACK;
    }

    /* 4. Верифікація підпису заголовка (перші 64 байти) */
    const uint8_t *root_pk = bsp_get_root_public_key();
    if (crypto_verify_ed25519(hdr->signature, (const uint8_t*)hdr, 64, root_pk) != 0) {
        return VERIFY_ERR_INVALID_SIGNATURE;
    }

    /* 5. Перевірка цілісності корисного коду */
    uint8_t calculated_sha[32];
    crypto_calc_sha256(payload, hdr->payload_size, calculated_sha);
    if (memcmp(calculated_sha, hdr->payload_sha256, 32) != 0) {
        return VERIFY_ERR_HASH_MISMATCH;
    }

    return VERIFY_SUCCESS;
}
