#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SECURE_BOOT_MAGIC 0x53424F54
#define HW_REV_CURRENT    0x0002 /* Hardware Rev B */

typedef struct {
    uint32_t magic;
    uint32_t version_code;
    uint32_t security_counter;
    uint32_t hw_compatibility_mask;
    uint32_t payload_size;
    uint8_t  sha256_digest[32];
    uint8_t  signature[64];
} __attribute__((packed)) ImageHeader;

typedef enum {
    VERIFY_OK = 0,
    ERR_BAD_MAGIC,
    ERR_HW_INCOMPATIBLE,
    ERR_ROLLBACK_DETECTED,
    ERR_IMAGE_TOO_LARGE,
    ERR_DIGEST_MISMATCH
} VerifyResult;

VerifyResult verify_release_header(const ImageHeader *hdr,
                                   uint32_t current_efuse_counter,
                                   uint32_t max_flash_size) {
    if (hdr->magic != SECURE_BOOT_MAGIC) {
        return ERR_BAD_MAGIC;
    }

    /* Перевірка сумісності з поточною апаратною ревізією */
    if ((hdr->hw_compatibility_mask & (1U << HW_REV_CURRENT)) == 0) {
        return ERR_HW_INCOMPATIBLE;
    }

    /* Захист від відкату версії (anti-rollback) */
    if (hdr->security_counter < current_efuse_counter) {
        return ERR_ROLLBACK_DETECTED;
    }

    /* Перевірка лімітів пам'яті */
    if (hdr->payload_size > max_flash_size) {
        return ERR_IMAGE_TOO_LARGE;
    }

    return VERIFY_OK;
}
