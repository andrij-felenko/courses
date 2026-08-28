#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MANIFEST_MAGIC      0x5346574D  /* "SFWM" */
#define MAX_KEY_SLOTS       4
#define HASH_SIZE_BYTES     32
#define SIGNATURE_SIZE      64
#define PUBLIC_KEY_SIZE     32

typedef enum {
    BOOT_OK = 0,
    BOOT_ERR_MAGIC,
    BOOT_ERR_INVALID_SLOT,
    BOOT_ERR_KEY_REVOKED,
    BOOT_ERR_ROOT_MISMATCH,
    BOOT_ERR_ROLLBACK_DETECTED,
    BOOT_ERR_SIGNATURE_INVALID,
    BOOT_ERR_FLASH_READ
} BootStatus;

/* Структура бінарного маніфесту прошивки */
typedef struct {
    uint32_t magic;
    uint32_t payload_length;
    uint32_t security_version;
    uint8_t  key_slot_index;
    uint8_t  reserved[3];
    uint8_t  public_key[PUBLIC_KEY_SIZE];
    uint8_t  signature[SIGNATURE_SIZE];
} __attribute__((packed)) FirmwareManifest;

/* Апаратний стан eFuse (емулюється або читається з регістрів чіпа) */
typedef struct {
    uint8_t  root_key_digests[MAX_KEY_SLOTS][HASH_SIZE_BYTES];
    uint8_t  revocation_bits;       /* Бітова маска: біт N = 1 означає, що слот N відкликано */
    uint32_t monotonic_counter;     /* Апаратний лічильник анти-відкату */
} HardwareEfuseMirror;

/* Безпечне побайтове порівняння за сталий час (захист від Timing Attacks) */
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t size) {
    uint8_t result = 0;
    for (size_t i = 0; i < size; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return (result == 0);
}

/* Зовнішні криптографічні функції (наприклад, з mbedTLS або апаратного крипторушія) */
extern void crypto_sha256(const uint8_t *data, size_t len, uint8_t *out_hash);
extern bool crypto_ed25519_verify(const uint8_t *pub_key, const uint8_t *msg_hash, const uint8_t *sig);
extern bool hardware_burn_efuse_revocation(uint8_t slot_index);
extern bool hardware_burn_efuse_counter(uint32_t new_version);

/* Головна функція верифікації та запуску прошивки */
BootStatus bootloader_verify_and_stage(
    const FirmwareManifest *manifest,
    const uint8_t *payload,
    const HardwareEfuseMirror *efuse,
    bool should_commit_rotation
) {
    if (!manifest || !payload || !efuse) {
        return BOOT_ERR_FLASH_READ;
    }

    /* 1. Перевірка магічного числа */
    if (manifest->magic != MANIFEST_MAGIC) {
        return BOOT_ERR_MAGIC;
    }

    /* 2. Перевірка допустимості індексу слота */
    if (manifest->key_slot_index >= MAX_KEY_SLOTS) {
        return BOOT_ERR_INVALID_SLOT;
    }

    /* 3. Перевірка відкликання ключа в eFuse */
    if ((efuse->revocation_bits & (1U << manifest->key_slot_index)) != 0) {
        return BOOT_ERR_KEY_REVOKED;
    }

    /* 4. Звірка відкритого ключа з еталоном Root of Trust */
    uint8_t computed_key_hash[HASH_SIZE_BYTES];
    crypto_sha256(manifest->public_key, PUBLIC_KEY_SIZE, computed_key_hash);

    if (!constant_time_memcmp(computed_key_hash, efuse->root_key_digests[manifest->key_slot_index], HASH_SIZE_BYTES)) {
        return BOOT_ERR_ROOT_MISMATCH;
    }

    /* 5. Захист від відкату версій */
    if (manifest->security_version < efuse->monotonic_counter) {
        return BOOT_ERR_ROLLBACK_DETECTED;
    }

    /* 6. Обчислення хешу тіла прошивки та перевірка підпису */
    uint8_t payload_hash[HASH_SIZE_BYTES];
    crypto_sha256(payload, manifest->payload_length, payload_hash);

    if (!crypto_ed25519_verify(manifest->public_key, payload_hash, manifest->signature)) {
        return BOOT_ERR_SIGNATURE_INVALID;
    }

    /* 7. Фіксація ротації eFuse (якщо це міграційний реліз і система підтвердила старт) */
    if (should_commit_rotation) {
        /* Спалюємо старі скомпрометовані слоти, якщо оновлення перейшло на вищий слот */
        for (uint8_t slot = 0; slot < manifest->key_slot_index; ++slot) {
            if ((efuse->revocation_bits & (1U << slot)) == 0) {
                hardware_burn_efuse_revocation(slot);
            }
        }

        /* Підвищуємо апаратний лічильник анти-відкату */
        if (manifest->security_version > efuse->monotonic_counter) {
            hardware_burn_efuse_counter(manifest->security_version);
        }
    }

    return BOOT_OK;
}
