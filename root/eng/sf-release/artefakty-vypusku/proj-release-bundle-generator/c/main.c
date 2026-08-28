#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUNDLE_MAGIC          0x42554E44U /* "BUND" в ASCII */
#define BUNDLE_FORMAT_VERSION 1U
#define SHA256_DIGEST_LEN     32U
#define SIGNATURE_LEN         64U

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;                    /* Магічне число ідентифікації BUNDLE_MAGIC */
    uint16_t header_version;           /* Версія формату заголовка */
    uint16_t reserved;                 /* Вирівнювання структури */
    uint32_t payload_size;             /* Розмір виконуваного бінарного образу в байтах */
    uint32_t target_hw_mask;           /* Бітова маска сумісних ревізій апаратної плати */
    uint32_t anti_rollback_version;    /* Монотонний лічильник захисту від відкату версії */
    uint8_t  payload_sha256[SHA256_DIGEST_LEN]; /* Криптографічний геш SHA-256 образу */
    uint8_t  signature[SIGNATURE_LEN];          /* Цифровий підпис (Ed25519/ECDSA) */
} firmware_header_t;
#pragma pack(pop)

typedef struct {
    char filename[64];
    uint32_t file_size;
    uint8_t  sha256[SHA256_DIGEST_LEN];
    bool     is_mandatory;
} release_artifact_entry_t;

typedef struct {
    uint16_t ver_major;
    uint16_t ver_minor;
    uint16_t ver_patch;
    uint32_t target_hw_mask;
    uint32_t anti_rollback_version;
    size_t   artifact_count;
    release_artifact_entry_t artifacts[8];
} release_bundle_spec_t;

/* Спрощена імітація криптографічного SHA-256 для демонстрації зв'язування даних */
static void compute_sha256_mock(const uint8_t *data, size_t len, uint8_t *out_hash) {
    memset(out_hash, 0, SHA256_DIGEST_LEN);
    uint32_t acc = 0x811C9DC5U;
    for (size_t i = 0; i < len; ++i) {
        acc = (acc ^ data[i]) * 0x01000193U;
        out_hash[i % SHA256_DIGEST_LEN] ^= (uint8_t)(acc & 0xFFU);
    }
}

/* Генерація та валідація бінарного заголовка */
static bool generate_firmware_header(
    const uint8_t *bin_payload,
    size_t bin_size,
    uint32_t hw_mask,
    uint32_t rollback_ver,
    firmware_header_t *out_header
) {
    if (!bin_payload || bin_size == 0 || !out_header) {
        return false;
    }

    out_header->magic = BUNDLE_MAGIC;
    out_header->header_version = BUNDLE_FORMAT_VERSION;
    out_header->reserved = 0;
    out_header->payload_size = (uint32_t)bin_size;
    out_header->target_hw_mask = hw_mask;
    out_header->anti_rollback_version = rollback_ver;

    compute_sha256_mock(bin_payload, bin_size, out_header->payload_sha256);

    /* Імітація накладання підпису приватним ключем релізної станції */
    for (size_t i = 0; i < SIGNATURE_LEN; ++i) {
        out_header->signature[i] = (uint8_t)(out_header->payload_sha256[i % SHA256_DIGEST_LEN] ^ 0xAAU);
    }
    return true;
}

/* Перевірка цілісності релізного пакета */
static bool verify_bundle_integrity(
    const firmware_header_t *header,
    const uint8_t *bin_payload,
    size_t bin_size,
    uint32_t device_hw_revision,
    uint32_t device_current_rollback_ver
) {
    if (!header || !bin_payload) {
        return false;
    }

    if (header->magic != BUNDLE_MAGIC) {
        fprintf(stderr, "Помилка: недійсне магічне число заголовка: 0x%08X\n", header->magic);
        return false;
    }

    if (header->payload_size != bin_size) {
        fprintf(stderr, "Помилка: невідповідність розміру образу: %u != %zu\n", header->payload_size, bin_size);
        return false;
    }

    if ((header->target_hw_mask & (1U << device_hw_revision)) == 0) {
        fprintf(stderr, "Помилка: прошивка не підтримує ревізію плати %u (маска 0x%X)\n",
                device_hw_revision, header->target_hw_mask);
        return false;
    }

    if (header->anti_rollback_version < device_current_rollback_ver) {
        fprintf(stderr, "Атака відкату версії! Поточна версія пристрою: %u, образ: %u\n",
                device_current_rollback_ver, header->anti_rollback_version);
        return false;
    }

    uint8_t calculated_hash[SHA256_DIGEST_LEN];
    compute_sha256_mock(bin_payload, bin_size, calculated_hash);
    if (memcmp(calculated_hash, header->payload_sha256, SHA256_DIGEST_LEN) != 0) {
        fprintf(stderr, "Помилка: не збігається SHA-256 контрольна сума образу!\n");
        return false;
    }

    return true;
}

int main(void) {
    /* Симуляція скомпільованого бінарного коду мікроконтролера */
    uint8_t dummy_binary[1024];
    for (size_t i = 0; i < sizeof(dummy_binary); ++i) {
        dummy_binary[i] = (uint8_t)(i & 0xFF);
    }

    firmware_header_t header;
    const uint32_t target_hw_bitmask = (1U << 1) | (1U << 2); /* Підтримка ревізій Rev.1 та Rev.2 */
    const uint32_t release_rollback_counter = 105;

    if (!generate_firmware_header(dummy_binary, sizeof(dummy_binary),
                                  target_hw_bitmask, release_rollback_counter, &header)) {
        fprintf(stderr, "Не вдалося сформувати заголовок прошивки\n");
        return EXIT_FAILURE;
    }

    printf("Маніфест прошивки сформовано успішно:\n");
    printf("  Магічне число: 0x%08X (OK)\n", header.magic);
    printf("  Розмір тіла:    %u байт\n", header.payload_size);
    printf("  Маска заліза:   0x%08X\n", header.target_hw_mask);
    printf("  Анти-відкат:    %u\n", header.anti_rollback_version);
    printf("  SHA-256 геш:    %02x%02x%02x%02x...%02x\n",
           header.payload_sha256[0], header.payload_sha256[1],
           header.payload_sha256[2], header.payload_sha256[3],
           header.payload_sha256[31]);

    /* Тестування валідації на цільовому пристрої */
    const uint32_t board_rev = 2;
    const uint32_t current_fw_rollback_ver = 104;

    printf("\nВалідація образу для плати Rev.%u (поточний лічильник %u)...\n",
           board_rev, current_fw_rollback_ver);

    if (verify_bundle_integrity(&header, dummy_binary, sizeof(dummy_binary),
                                board_rev, current_fw_rollback_ver)) {
        printf("РЕЗУЛЬТАТ: Пакет успішно валідовано, прошивка дозволена до запису у Flash.\n");
    } else {
        printf("РЕЗУЛЬТАТ: Валідацію провалено! Запис заборонено.\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
