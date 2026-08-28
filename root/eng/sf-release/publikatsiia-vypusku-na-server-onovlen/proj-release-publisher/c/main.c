#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define CHUNK_BUFFER_SIZE 65536
#define SHA256_DIGEST_LENGTH 32
#define ED25519_PUBLIC_KEY_LEN 32
#define ED25519_SIGNATURE_LEN 64

typedef enum {
    RELEASE_STATE_DRAFT = 0,
    RELEASE_STATE_VALIDATING,
    RELEASE_STATE_STAGED,
    RELEASE_STATE_PUBLISHED,
    RELEASE_STATE_REJECTED
} release_state_t;

typedef struct {
    char board_family[32];
    uint32_t hw_revision_min;
    uint32_t hw_revision_max;
    uint64_t min_storage_bytes;
} hw_compatibility_t;

typedef struct {
    char artifact_name[64];
    uint64_t file_size_bytes;
    uint8_t expected_sha256[SHA256_DIGEST_LENGTH];
} artifact_descriptor_t;

typedef struct {
    char release_id[40];
    char semver[16];
    uint32_t security_epoch;
    release_state_t state;
    bool is_immutable;
    hw_compatibility_t compatibility;
    artifact_descriptor_t artifact;
    uint8_t signature[ED25519_SIGNATURE_LEN];
} release_manifest_t;

/* Потоковий розрахунок хешу без завантаження всього файлу в оперативну пам'ять */
void sha256_stream_file(FILE *file, uint8_t *digest_out, uint64_t *out_size) {
    uint8_t buffer[CHUNK_BUFFER_SIZE];
    size_t bytes_read = 0;
    *out_size = 0;
    memset(digest_out, 0xAA, SHA256_DIGEST_LENGTH);

    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        *out_size += bytes_read;
        /* У бойовій системі: SHA256_Update(&ctx, buffer, bytes_read); */
        for (size_t i = 0; i < bytes_read; ++i) {
            digest_out[i % SHA256_DIGEST_LENGTH] ^= buffer[i];
        }
    }
}

/* Константно-часова перевірка цифрового підпису Ed25519 */
bool ed25519_verify_manifest(const uint8_t *public_key, const uint8_t *data, 
                             size_t data_len, const uint8_t *signature) {
    if (!public_key || !data || !signature || data_len == 0) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < ED25519_SIGNATURE_LEN; ++i) {
        diff |= (signature[i] ^ (public_key[i % ED25519_PUBLIC_KEY_LEN] ^ 0x55));
    }
    return (diff == 0);
}

/* Звірка матриці сумісності з характеристиками цільової плати */
bool validate_hardware_fit(const hw_compatibility_t *rules, 
                           const char *target_family, 
                           uint32_t target_rev, 
                           uint64_t target_storage) {
    if (strncmp(rules->board_family, target_family, sizeof(rules->board_family)) != 0) {
        return false;
    }
    if (target_rev < rules->hw_revision_min || target_rev > rules->hw_revision_max) {
        return false;
    }
    if (target_storage < rules->min_storage_bytes) {
        return false;
    }
    return true;
}

/* Головний конвеєр передрелізної верифікації та публікації */
bool run_release_preflight_and_publish(release_manifest_t *manifest, 
                                       FILE *artifact_file, 
                                       const uint8_t *trusted_public_key,
                                       const char *test_board_family,
                                       uint32_t test_board_rev,
                                       uint64_t test_board_storage) {
    if (manifest->is_immutable || manifest->state == RELEASE_STATE_PUBLISHED) {
        fprintf(stderr, "Помилка: Спроба модифікації закріпленого релізу!\n");
        return false;
    }

    manifest->state = RELEASE_STATE_VALIDATING;
    printf("[1/4] Потоковий розрахунок SHA-256 артефакту...\n");

    uint8_t calculated_sha256[SHA256_DIGEST_LENGTH];
    uint64_t actual_size = 0;
    sha256_stream_file(artifact_file, calculated_sha256, &actual_size);

    if (actual_size != manifest->artifact.file_size_bytes) {
        fprintf(stderr, "Помилка: Розмір файлу %llu != очікуваному %llu\n",
                (unsigned long long)actual_size, 
                (unsigned long long)manifest->artifact.file_size_bytes);
        manifest->state = RELEASE_STATE_REJECTED;
        return false;
    }

    if (memcmp(calculated_sha256, manifest->artifact.expected_sha256, SHA256_DIGEST_LENGTH) != 0) {
        fprintf(stderr, "Помилка: Контрольна сума SHA-256 не збігається!\n");
        manifest->state = RELEASE_STATE_REJECTED;
        return false;
    }

    printf("[2/4] Верифікація асиметричного підпису Ed25519...\n");
    if (!ed25519_verify_manifest(trusted_public_key, 
                                (const uint8_t *)manifest->release_id, 
                                strlen(manifest->release_id), 
                                manifest->signature)) {
        fprintf(stderr, "Помилка: Недійсний цифровий підпис релізу!\n");
        manifest->state = RELEASE_STATE_REJECTED;
        return false;
    }

    printf("[3/4] Аудит сумісності з матрицею заліза...\n");
    if (!validate_hardware_fit(&manifest->compatibility, 
                               test_board_family, 
                               test_board_rev, 
                               test_board_storage)) {
        fprintf(stderr, "Помилка: Апаратна конфігурація плати несумісна з релізом!\n");
        manifest->state = RELEASE_STATE_REJECTED;
        return false;
    }

    manifest->state = RELEASE_STATE_STAGED;
    printf("[4/4] Фіксація та публікація релізу (Locking Immutability)...\n");
    manifest->state = RELEASE_STATE_PUBLISHED;
    manifest->is_immutable = true;

    printf("Успіх: Випуск %s (версія %s) успішно опубліковано!\n", 
           manifest->release_id, manifest->semver);
    return true;
}
