#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Спрощений інтерфейс криптобібліотеки (mbedTLS / Monocypher) */
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
    VERIFY_OK = 0,
    VERIFY_ERR_MAGIC = 1,
    VERIFY_ERR_HW_MISMATCH = 2,
    VERIFY_ERR_ROLLBACK = 3,
    VERIFY_ERR_SIGNATURE = 4,
    VERIFY_ERR_HASH = 5
} verify_status_t;

/* Зовнішні апаратні функції платформи */
extern uint32_t bsp_get_hardware_id(void);
extern uint8_t  bsp_get_board_revision(void);
extern uint32_t bsp_get_otp_security_version(void);
extern const uint8_t* bsp_get_root_public_key(void);
extern int crypto_ed25519_verify(const uint8_t sig[64], const uint8_t *msg, size_t len, const uint8_t pubkey[32]);
extern void crypto_sha256_stream(const uint8_t *data, size_t len, uint8_t out_digest[32]);

verify_status_t bootloader_verify_image(const firmware_header_t *hdr, const uint8_t *payload) {
    /* 1. Перевірка магічного числа */
    if (hdr->magic_word != 0x46574D46U || hdr->header_version != 1U) {
        return VERIFY_ERR_MAGIC;
    }

    /* 2. Перевірка сумісності із залізом */
    if (hdr->target_hw_id != bsp_get_hardware_id()) {
        return VERIFY_ERR_HW_MISMATCH;
    }
    uint8_t current_rev = bsp_get_board_revision();
    if (current_rev < hdr->hw_rev_min || current_rev > hdr->hw_rev_max) {
        return VERIFY_ERR_HW_MISMATCH;
    }

    /* 3. Перевірка на атаку відкату (Anti-rollback) */
    if (hdr->security_version < bsp_get_otp_security_version()) {
        return VERIFY_ERR_ROLLBACK;
    }

    /* 4. Верифікація криптографічного підпису заголовка */
    const uint8_t *pubkey = bsp_get_root_public_key();
    if (crypto_ed25519_verify(hdr->signature, (const uint8_t*)hdr, 64, pubkey) != 0) {
        return VERIFY_ERR_SIGNATURE;
    }

    /* 5. Потокова перевірка цілісності корисного коду */
    uint8_t calculated_hash[32];
    crypto_sha256_stream(payload, hdr->payload_size, calculated_hash);
    if (memcmp(calculated_hash, hdr->payload_sha256, 32) != 0) {
        return VERIFY_ERR_HASH;
    }

    return VERIFY_OK;
}
