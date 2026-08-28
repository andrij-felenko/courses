#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SECURE_BOOT_MAGIC 0x53424F54
#define CURRENT_HW_MASK   0x0002

typedef struct {
    uint32_t magic;
    uint32_t version_packed;
    uint32_t security_counter;
    uint32_t hw_mask;
    uint32_t payload_size;
    uint8_t  payload_sha256[32];
    uint8_t  signature[64];
    uint8_t  reserved[12];
} __attribute__((packed)) ReleaseHeader;

typedef enum {
    RELEASE_OK = 0,
    ERR_INVALID_MAGIC,
    ERR_INCOMPATIBLE_HARDWARE,
    ERR_ANTI_ROLLBACK,
    ERR_BUFFER_OVERFLOW
} ReleaseStatus;

ReleaseStatus validate_image_header(const uint8_t *header_buffer,
                                    size_t buffer_len,
                                    uint32_t active_security_counter,
                                    uint32_t max_allowed_size) {
    if (buffer_len < sizeof(ReleaseHeader)) {
        return ERR_BUFFER_OVERFLOW;
    }

    const ReleaseHeader *hdr = (const ReleaseHeader *)header_buffer;

    if (hdr->magic != SECURE_BOOT_MAGIC) {
        return ERR_INVALID_MAGIC;
    }

    /* Перевірка бітової маски апаратної сумісності */
    if ((hdr->hw_mask & CURRENT_HW_MASK) == 0) {
        return ERR_INCOMPATIBLE_HARDWARE;
    }

    /* Захист від відкату на застарілу вразливу версію */
    if (hdr->security_counter < active_security_counter) {
        return ERR_ANTI_ROLLBACK;
    }

    if (hdr->payload_size > max_allowed_size) {
        return ERR_BUFFER_OVERFLOW;
    }

    return RELEASE_OK;
}
