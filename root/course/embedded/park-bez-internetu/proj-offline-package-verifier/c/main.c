#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UPKG_MAGIC              0x47504B55  /* "UPKG" в Little-Endian */
#define UPKG_HEADER_SIZE        128
#define UPKG_SIGNATURE_SIZE     64
#define UPKG_HASH_SIZE          32
#define UPKG_CHUNK_SIZE         4096

typedef enum {
    UPKG_OK = 0,
    UPKG_ERR_INVALID_MAGIC,
    UPKG_ERR_HW_MISMATCH,
    UPKG_ERR_ROLLBACK_DETECTED,
    UPKG_ERR_SIGNATURE_INVALID,
    UPKG_ERR_CHUNK_HASH_MISMATCH,
    UPKG_ERR_FINAL_HASH_MISMATCH,
    UPKG_ERR_FLASH_WRITE
} upkg_status_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t format_version;
    uint16_t target_hw_id;
    uint32_t version_monotonic;
    uint32_t payload_size;
    uint32_t chunk_count;
    uint8_t  final_sha256[UPKG_HASH_SIZE];
    uint8_t  reserved[40];
    uint8_t  signature[UPKG_SIGNATURE_SIZE];
} upkg_header_t;

typedef struct {
    uint16_t my_hw_id;
    uint32_t my_min_allowed_version;
    const uint8_t *root_public_key;
    /* Абстракція запису Flash */
    bool (*flash_erase_slot_b)(uint32_t total_size);
    bool (*flash_write_chunk)(uint32_t offset, const uint8_t *data, uint32_t size);
    /* Криптографічні виклики */
    bool (*ed25519_verify)(const uint8_t *msg, size_t msg_len,
                           const uint8_t *sig, const uint8_t *pub_key);
    void (*sha256_calc)(const uint8_t *data, size_t len, uint8_t *out_hash);
} upkg_verifier_ctx_t;

/* Валідація заголовка офлайн-пакета */
upkg_status_t upkg_validate_header(const upkg_verifier_ctx_t *ctx,
                                    const upkg_header_t *hdr) {
    if (hdr->magic != UPKG_MAGIC) {
        return UPKG_ERR_INVALID_MAGIC;
    }
    if (hdr->target_hw_id != ctx->my_hw_id) {
        return UPKG_ERR_HW_MISMATCH;
    }
    if (hdr->version_monotonic <= ctx->my_min_allowed_version) {
        return UPKG_ERR_ROLLBACK_DETECTED;
    }

    /* Підпис охоплює поля заголовка безпосередньо перед сигнатурою */
    const size_t signed_header_len = sizeof(upkg_header_t) - UPKG_SIGNATURE_SIZE;
    if (!ctx->ed25519_verify((const uint8_t *)hdr, signed_header_len,
                             hdr->signature, ctx->root_public_key)) {
        return UPKG_ERR_SIGNATURE_INVALID;
    }

    return UPKG_OK;
}

/* Обробка одного потокового чанка */
upkg_status_t upkg_process_chunk(const upkg_verifier_ctx_t *ctx,
                                  uint32_t chunk_idx,
                                  const uint8_t *chunk_data,
                                  uint32_t chunk_size,
                                  const uint8_t *expected_chunk_hash) {
    uint8_t calculated_hash[UPKG_HASH_SIZE];
    ctx->sha256_calc(chunk_data, chunk_size, calculated_hash);

    if (memcmp(calculated_hash, expected_chunk_hash, UPKG_HASH_SIZE) != 0) {
        return UPKG_ERR_CHUNK_HASH_MISMATCH;
    }

    uint32_t flash_offset = chunk_idx * UPKG_CHUNK_SIZE;
    if (!ctx->flash_write_chunk(flash_offset, chunk_data, chunk_size)) {
        return UPKG_ERR_FLASH_WRITE;
    }

    return UPKG_OK;
}
