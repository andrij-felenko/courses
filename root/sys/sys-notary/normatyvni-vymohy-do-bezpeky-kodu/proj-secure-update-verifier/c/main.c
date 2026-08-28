#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define CRA_IMAGE_MAGIC          0x43524155u /* "CRAU" у порядку байтів Little-Endian */
#define CRA_HEADER_VERSION        1u
#define CRA_MAX_IMAGE_SIZE        (4u * 1024u * 1024u) /* Максимальний розмір образу 4 МБ */

#define CRA_TOKEN_SUCCESS        0x5AA55AA5u
#define CRA_TOKEN_FAILURE        0xA55AA55Au

typedef enum {
    CRA_VERIFY_OK = 0,
    CRA_ERR_NULL_POINTER,
    CRA_ERR_BAD_MAGIC,
    CRA_ERR_UNSUPPORTED_HEADER,
    CRA_ERR_IMAGE_TOO_LARGE,
    CRA_ERR_ROLLBACK_DETECTED,
    CRA_ERR_DIGEST_MISMATCH,
    CRA_ERR_INVALID_SIGNATURE
} cra_verify_status_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint16_t header_version;
    uint16_t reserved1;
    uint32_t security_version;
    uint32_t image_size;
    uint8_t  payload_sha256[32];
    uint8_t  signature[64];
    uint8_t  reserved2[16];
} cra_image_header_t;
#pragma pack(pop)

/* Зовнішні криптографічні примітиви апаратного прискорювача або mbedTLS */
extern int crypto_sha256(const uint8_t *data, size_t len, uint8_t hash_out[32]);
extern int crypto_ed25519_verify(const uint8_t sig[64], const uint8_t *msg, size_t msg_len, const uint8_t pubkey[32]);

/* Безпечне порівняння буферів за постійний час для захисту від таймінг-атак */
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

cra_verify_status_t cra_verify_firmware(
    const cra_image_header_t *header,
    const uint8_t *payload,
    uint32_t active_security_version,
    const uint8_t root_public_key[32]
) {
    if (!header || !payload || !root_public_key) {
        return CRA_ERR_NULL_POINTER;
    }

    /* 1. Перевірка магічного числа заголовка */
    if (header->magic != CRA_IMAGE_MAGIC) {
        return CRA_ERR_BAD_MAGIC;
    }

    if (header->header_version != CRA_HEADER_VERSION) {
        return CRA_ERR_UNSUPPORTED_HEADER;
    }

    if (header->image_size == 0 || header->image_size > CRA_MAX_IMAGE_SIZE) {
        return CRA_ERR_IMAGE_TOO_LARGE;
    }

    /* 2. Захист від пониження версії (Anti-Rollback за EN 303 645) */
    if (header->security_version < active_security_version) {
        return CRA_ERR_ROLLBACK_DETECTED;
    }

    /* 3. Перевірка цілісності корисного навантаження через SHA-256 */
    uint8_t computed_digest[32];
    if (crypto_sha256(payload, header->image_size, computed_digest) != 0) {
        return CRA_ERR_DIGEST_MISMATCH;
    }

    if (!constant_time_memcmp(computed_digest, header->payload_sha256, 32)) {
        return CRA_ERR_DIGEST_MISMATCH;
    }

    /* 4. Перевірка цифрового підпису заголовка */
    /* Підписуються перші 48 байтів структури (magic, версії, розмір, геш образу) */
    size_t signed_metadata_len = offsetof(cra_image_header_t, signature);
    uint32_t verify_token = CRA_TOKEN_FAILURE;

    if (crypto_ed25519_verify(header->signature, (const uint8_t *)header, signed_metadata_len, root_public_key) == 0) {
        verify_token = CRA_TOKEN_SUCCESS;
    }

    /* Подвійна перевірка токена проти збоїв у регістрах (glitch attack mitigation) */
    if (verify_token != CRA_TOKEN_SUCCESS || verify_token == CRA_TOKEN_FAILURE) {
        return CRA_ERR_INVALID_SIGNATURE;
    }

    return CRA_VERIFY_OK;
}
