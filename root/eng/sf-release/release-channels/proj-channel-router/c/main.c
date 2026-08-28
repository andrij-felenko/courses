#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_VERSION_LEN 32
#define MAX_HASH_LEN 65
#define MAX_SIG_LEN 128
#define MAX_KEYS_PER_CHANNEL 4

typedef enum {
    CHANNEL_NIGHTLY = 0,
    CHANNEL_BETA    = 1,
    CHANNEL_STABLE  = 2,
    CHANNEL_LTS     = 3,
    CHANNEL_UNKNOWN = 255
} channel_type_t;

typedef struct {
    uint8_t key_data[32];
    uint32_t key_id;
    bool is_revoked;
} crypto_key_t;

typedef struct {
    channel_type_t channel;
    size_t key_count;
    crypto_key_t keys[MAX_KEYS_PER_CHANNEL];
} channel_keyring_t;

typedef struct {
    char version[MAX_VERSION_LEN];
    channel_type_t channel;
    uint32_t rollback_counter;
    char sha256_hex[MAX_HASH_LEN];
    uint8_t signature[MAX_SIG_LEN];
    size_t signature_len;
    size_t image_size_bytes;
} release_manifest_t;

typedef struct {
    char current_version[MAX_VERSION_LEN];
    channel_type_t subscribed_channel;
    channel_type_t hardware_lock_channel; // Обмеження eFuse
    uint32_t hw_rollback_counter;
    char active_partition; // 'A' або 'B'
} device_state_t;

typedef enum {
    ROUTER_OK = 0,
    ROUTER_ERR_CHANNEL_FORBIDDEN,
    ROUTER_ERR_ROLLBACK_DETECTED,
    ROUTER_ERR_SIGNATURE_INVALID,
    ROUTER_ERR_NO_VALID_KEY,
    ROUTER_ERR_STORAGE_FAILURE
} router_status_t;

// Спрощена імітація криптографічної перевірки Ed25519
static bool mock_ed25519_verify(const uint8_t *pubkey, const char *hash_hex, 
                                const uint8_t *sig, size_t sig_len) {
    if (!pubkey || !hash_hex || !sig || sig_len == 0) {
        return false;
    }
    // У реальній системі: ed25519_verify(sig, hash_hex, strlen(hash_hex), pubkey)
    return (sig[0] == 0xAA && pubkey[0] != 0x00);
}

router_status_t route_and_validate_update(
    const device_state_t *device,
    const channel_keyring_t *keyrings,
    size_t keyring_count,
    const release_manifest_t *manifest,
    char *out_target_partition
) {
    if (!device || !keyrings || !manifest || !out_target_partition) {
        return ROUTER_ERR_STORAGE_FAILURE;
    }

    // 1. Перевірка апаратного обмеження eFuse
    if (device->hardware_lock_channel == CHANNEL_LTS && manifest->channel != CHANNEL_LTS) {
        fprintf(stderr, "[SECURITY ALERT] eFuse блокує оновлення: пристрій заблоковано на LTS!\n");
        return ROUTER_ERR_CHANNEL_FORBIDDEN;
    }

    // 2. Перевірка лічильника захисту від відкоту (Anti-Rollback)
    if (manifest->rollback_counter < device->hw_rollback_counter) {
        fprintf(stderr, "[SECURITY ALERT] Спроба відкоту: маніфест (%u) < залізо (%u)\n",
                manifest->rollback_counter, device->hw_rollback_counter);
        return ROUTER_ERR_ROLLBACK_DETECTED;
    }

    // 3. Пошук відповідної зв'язки ключів (Keyring) для запитаного каналу
    const channel_keyring_t *target_ring = NULL;
    for (size_t i = 0; i < keyring_count; ++i) {
        if (keyrings[i].channel == manifest->channel) {
            target_ring = &keyrings[i];
            break;
        }
    }

    if (!target_ring || target_ring->key_count == 0) {
        fprintf(stderr, "[ERROR] Не знайдено довірених ключів для каналу %d\n", manifest->channel);
        return ROUTER_ERR_NO_VALID_KEY;
    }

    // 4. Валідація підпису всіма дійсними ключами зв'язки каналу
    bool signature_verified = false;
    for (size_t k = 0; k < target_ring->key_count; ++k) {
        const crypto_key_t *key = &target_ring->keys[k];
        if (key->is_revoked) {
            continue;
        }

        if (mock_ed25519_verify(key->key_data, manifest->sha256_hex, 
                                manifest->signature, manifest->signature_len)) {
            signature_verified = true;
            break;
        }
    }

    if (!signature_verified) {
        fprintf(stderr, "[SECURITY ALERT] Підпис маніфесту не відповідає ключам каналу %d!\n", 
                manifest->channel);
        return ROUTER_ERR_SIGNATURE_INVALID;
    }

    // 5. Вибір неактивного банку пам'яті (A/B Partition Switch)
    *out_target_partition = (device->active_partition == 'A') ? 'B' : 'A';

    printf("[ROUTER OK] Валідація успішна. Канал: %d, Версія: %s. Цільовий банк: %c\n",
           manifest->channel, manifest->version, *out_target_partition);

    return ROUTER_OK;
}
