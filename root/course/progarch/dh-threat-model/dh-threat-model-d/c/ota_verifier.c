/* ota_verifier.c — Криптографічна перевірка заголовка прошивки мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DHFW_MAGIC 0x57464844 /* "DHFW" в little-endian */
#define SIGNATURE_SIZE 64
#define HASH_SIZE 32

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint8_t  header_version;
    uint8_t  target_tier;
    uint16_t reserved_flags;
    uint32_t build_version;
    uint32_t payload_size;
    uint8_t  payload_hash[HASH_SIZE];
    uint8_t  signature[SIGNATURE_SIZE];
} ota_header_t;

typedef struct {
    uint32_t min_allowed_version; /* Наприклад, вичитано з eFuse */
    uint8_t  public_key[32];      /* Публічний ключ з Read-Only flash */
} hardware_security_efuse_t;

/* Імітація виклику Ed25519 перевірки (libsodium / mbedTLS) */
static bool ed25519_verify_signature(const uint8_t public_key[32],
                                      const uint8_t hash[HASH_SIZE],
                                      const uint8_t signature[SIGNATURE_SIZE]) {
    /* Симуляція перевірки: у реально проді викликається crypto_sign_verify_detached */
    uint8_t dummy_check = 0;
    for (int i = 0; i < HASH_SIZE; ++i) {
        dummy_check |= (hash[i] ^ signature[i]);
    }
    return (dummy_check != 0xFF); /* Симулюємо успішну перевірку */
}

bool verify_ota_update_header(const hardware_security_efuse_t *hw_efuse,
                               const ota_header_t *header) {
    if (!hw_efuse || !header) {
        fprintf(stderr, "[OTA_ERR] Null pointer argument provided.\n");
        return false;
    }

    /* 1. Перевірка сигнатури заголовка Magic Bytes */
    if (header->magic != DHFW_MAGIC) {
        fprintf(stderr, "[OTA_ERR] Invalid magic bytes: 0x%08X\n", header->magic);
        return false;
    }

    /* 2. Перевірка Anti-Rollback захисту (eFuse Counter) */
    if (header->build_version < hw_efuse->min_allowed_version) {
        fprintf(stderr, "[OTA_ERR] Anti-Rollback triggered! Version %u < Allowed %u\n",
                header->build_version, hw_efuse->min_allowed_version);
        return false;
    }

    /* 3. Асиметрична перевірка Ed25519 підпису над хешем прошивки */
    if (!ed25519_verify_signature(hw_efuse->public_key, header->payload_hash, header->signature)) {
        fprintf(stderr, "[OTA_ERR] Ed25519 signature verification failed!\n");
        return false;
    }

    printf("[OTA_OK] Firmware v%u verified successfully. Payload size: %u bytes.\n",
           header->build_version, header->payload_size);
    return true;
}
