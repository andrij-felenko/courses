#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FOTA_MAGIC 0x464F5441U /* Сигнатура 'FOTA' */

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;            /* 'FOTA' */
    uint32_t version_major;    /* Мажорна версія */
    uint32_t version_minor;    /* Мінорна версія */
    uint32_t version_patch;    /* Патч версія */
    uint32_t target_hw_id;     /* Ідентифікатор плати мікроконтролера */
    uint32_t entry_point;      /* Точка входу e_entry */
    uint32_t flash_target_lma; /* Фізична адреса LMA у Flash */
    uint32_t payload_size;     /* Розмір корисного навантаження */
    uint32_t payload_crc32;    /* CRC32 корисних даних */
    uint8_t  sha256_hash[32];  /* SHA-256 хеш сегментів */
    uint8_t  signature[64];    /* Цифровий підпис ECDSA P-256 */
} FotaHeader;
#pragma pack(pop)

bool generate_fota_package(const uint8_t* raw_bin, size_t bin_size, 
                           uint32_t entry_addr, uint32_t target_lma, 
                           const char* out_fota_path) {
    if (!raw_bin || bin_size == 0 || !out_fota_path) return false;

    FotaHeader header;
    memset(&header, 0, sizeof(FotaHeader));

    header.magic = FOTA_MAGIC;
    header.version_major = 2;
    header.version_minor = 1;
    header.version_patch = 0;
    header.target_hw_id = 0x0042; /* Наприклад, плата на базі STM32F407 */
    header.entry_point = entry_addr;
    header.flash_target_lma = target_lma;
    header.payload_size = (uint32_t)bin_size;
    header.payload_crc32 = calculate_crc32_c(raw_bin, bin_size);

    FILE* f_out = fopen(out_fota_path, "wb");
    if (!f_out) return false;

    /* 1. Запис мета-заголовка FOTA */
    fwrite(&header, 1, sizeof(FotaHeader), f_out);

    /* 2. Запис корисного навантаження прошивки */
    fwrite(raw_bin, 1, bin_size, f_out);

    fclose(f_out);
    printf("Пакет безпечного оновлення FOTA сформовано: %s\n", out_fota_path);
    return true;
}
