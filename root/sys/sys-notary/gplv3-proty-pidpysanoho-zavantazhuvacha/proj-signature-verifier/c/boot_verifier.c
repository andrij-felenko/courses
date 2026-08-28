/* boot_verifier.c — Процедурна реалізація криптографічного валідатора для C99/C11 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/sha.h>

#define SECURE_BOOT_MAGIC 0x53454355U /* "SECU" */

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t header_version;
    uint32_t firmware_version;
    uint32_t payload_size;
    uint32_t signature_size;
    uint8_t  key_id[16];
    uint8_t  reserved[28];
} ImageHeader;

typedef enum {
    VERIFY_SUCCESS = 0,
    ERR_INVALID_MAGIC,
    ERR_ROLLBACK_DETECTED,
    ERR_IMAGE_TOO_SHORT,
    ERR_UNKNOWN_KEY,
    ERR_SIGNATURE_FAILED,
    ERR_CRYPTO_ENGINE
} VerifyResult;

typedef struct {
    uint8_t key_id[16];
    EVP_PKEY *pubkey;
    bool is_user_mok;
} KeyEntry;

typedef struct {
    KeyEntry *keys;
    size_t key_count;
    uint32_t min_anti_rollback_ver;
} BootKeystore;

static EVP_PKEY *load_pubkey_from_pem(const char *pem_str) {
    BIO *bio = BIO_new_mem_buf(pem_str, -1);
    if (!bio) return NULL;
    EVP_PKEY *pkey = PEM_read_bio_PUBKEY(bio, NULL, NULL, NULL);
    BIO_free(bio);
    return pkey;
}

VerifyResult verify_boot_image(const BootKeystore *keystore,
                               const uint8_t *raw_data,
                               size_t total_size,
                               bool *out_is_user_authorized) {
    if (total_size < sizeof(ImageHeader)) {
        return ERR_IMAGE_TOO_SHORT;
    }

    const ImageHeader *hdr = (const ImageHeader *)raw_data;
    if (hdr->magic != SECURE_BOOT_MAGIC) {
        return ERR_INVALID_MAGIC;
    }

    if (hdr->firmware_version < keystore->min_anti_rollback_ver) {
        return ERR_ROLLBACK_DETECTED;
    }

    /* Захист від цілочисельного переповнення під час розрахунку загального розміру */
    if (hdr->payload_size > total_size || hdr->signature_size > total_size) {
        return ERR_IMAGE_TOO_SHORT;
    }

    size_t expected_total = sizeof(ImageHeader) + hdr->payload_size + hdr->signature_size;
    if (expected_total < sizeof(ImageHeader) || total_size < expected_total) {
        return ERR_IMAGE_TOO_SHORT;
    }

    const uint8_t *payload = raw_data + sizeof(ImageHeader);
    const uint8_t *sig = payload + hdr->payload_size;

    /* Пошук публічного ключа за ідентифікатором key_id */
    const KeyEntry *matched_key = NULL;
    for (size_t i = 0; i < keystore->key_count; ++i) {
        if (memcmp(keystore->keys[i].key_id, hdr->key_id, 16) == 0) {
            matched_key = &keystore->keys[i];
            break;
        }
    }

    if (!matched_key || !matched_key->pubkey) {
        return ERR_UNKNOWN_KEY;
    }

    /* Криптографічна перевірка підпису через OpenSSL EVP API */
    EVP_MD_CTX *md_ctx = EVP_MD_CTX_new();
    if (!md_ctx) {
        return ERR_CRYPTO_ENGINE;
    }

    VerifyResult result = ERR_SIGNATURE_FAILED;
    if (EVP_DigestVerifyInit(md_ctx, NULL, EVP_sha256(), NULL, matched_key->pubkey) != 1) {
        result = ERR_CRYPTO_ENGINE;
        goto cleanup;
    }

    if (EVP_DigestVerifyUpdate(md_ctx, payload, hdr->payload_size) != 1) {
        result = ERR_CRYPTO_ENGINE;
        goto cleanup;
    }

    if (EVP_DigestVerifyFinal(md_ctx, sig, hdr->signature_size) == 1) {
        result = VERIFY_SUCCESS;
        if (out_is_user_authorized) {
            *out_is_user_authorized = matched_key->is_user_mok;
        }
    }

cleanup:
    EVP_MD_CTX_free(md_ctx);
    return result;
}
