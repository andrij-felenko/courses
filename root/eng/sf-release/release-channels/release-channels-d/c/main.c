#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_VER_STR 32
#define HASH_HEX_LEN 65
#define MAX_KEYS_COUNT 4

typedef enum {
    CHAN_NIGHTLY = 0,
    CHAN_BETA    = 1,
    CHAN_STABLE  = 2,
    CHAN_LTS     = 3,
    CHAN_UNKNOWN = 255
} channel_id_t;

typedef struct {
    uint8_t raw_pubkey[32];
    uint32_t key_id;
    bool revoked;
} channel_key_entry_t;

typedef struct {
    channel_id_t channel;
    size_t count;
    channel_key_entry_t keys[MAX_KEYS_COUNT];
} channel_keyring_store_t;

typedef struct {
    char version[MAX_VER_STR];
    channel_id_t target_channel;
    uint32_t rollback_index;
    char sha256_hex[HASH_HEX_LEN];
    uint8_t signature[64];
    size_t signature_bytes;
} update_manifest_record_t;

typedef struct {
    channel_id_t efuse_hardware_lock;
    uint32_t current_rollback_index;
    char active_bank; // 'A' або 'B'
} node_security_state_t;

// Емуляція валідації Ed25519
static bool verify_ed25519_signature(const uint8_t *pubkey, const char *digest,
                                     const uint8_t *sig, size_t sig_len) {
    if (!pubkey || !digest || !sig || sig_len == 0) return false;
    return (sig[0] == 0xAA && pubkey[0] != 0x00);
}

int evaluate_channel_update(
    const node_security_state_t *node,
    const channel_keyring_store_t *keyrings,
    size_t keyrings_total,
    const update_manifest_record_t *manifest,
    char *out_target_bank
) {
    if (!node || !keyrings || !manifest || !out_target_bank) {
        return -1;
    }

    // 1. Апаратний захист: блокування eFuse
    if (node->efuse_hardware_lock == CHAN_LTS && manifest->target_channel != CHAN_LTS) {
        fprintf(stderr, "[ВІДХИЛЕНО] Апаратний eFuse блокує перехід на не-LTS канал!\n");
        return -2;
    }

    // 2. Захист від атак відкоту версії (Anti-Rollback)
    if (manifest->rollback_index < node->current_rollback_index) {
        fprintf(stderr, "[ВІДХИЛЕНО] Спроба відкоту версії: індекс %u < поточного %u\n",
                manifest->rollback_index, node->current_rollback_index);
        return -3;
    }

    // 3. Пошук зв'язки ключів для цільового каналу
    const channel_keyring_store_t *active_ring = NULL;
    for (size_t i = 0; i < keyrings_total; ++i) {
        if (keyrings[i].channel == manifest->target_channel) {
            active_ring = &keyrings[i];
            break;
        }
    }

    if (!active_ring || active_ring->count == 0) {
        fprintf(stderr, "[ПОМИЛКА] Відсутні довірені публічні ключі для каналу %d\n", 
                manifest->target_channel);
        return -4;
    }

    // 4. Перевірка підпису ключами каналу
    bool signature_valid = false;
    for (size_t k = 0; k < active_ring->count; ++k) {
        if (active_ring->keys[k].revoked) continue;

        if (verify_ed25519_signature(active_ring->keys[k].raw_pubkey,
                                     manifest->sha256_hex,
                                     manifest->signature,
                                     manifest->signature_bytes)) {
            signature_valid = true;
            break;
        }
    }

    if (!signature_valid) {
        fprintf(stderr, "[КРИТИЧНО] Цифровий підпис не відповідає ключам каналу %d!\n",
                manifest->target_channel);
        return -5;
    }

    // 5. Вибір неактивного банку пам'яті
    *out_target_bank = (node->active_bank == 'A') ? 'B' : 'A';
    return 0;
}
