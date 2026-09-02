#ifndef FS_STORAGE_H
#define FS_STORAGE_H

/* Двозбірне зберігання блока параметрів у секторі NOR Flash.
 * Свіжішим вважається банк із більшим лічильником транзакцій seq,
 * тому окремого прапорця "активний" у пам'яті не потрібно. */

#include "fs_params.h"

#define FS_SECTOR_SIZE          256u
#define FS_PARAM_MAGIC          0x30425346u  /* "FSB0" у little-endian */
#define FS_SCHEMA_VERSION       3u
#define FS_HDR_SIZE             12u          /* magic + schema + count + seq */

typedef enum {
    FS_STORE_OK = 0,
    FS_STORE_ERR_ERASED,   /* сектор стертий: суцільні 0xFF */
    FS_STORE_ERR_MAGIC,
    FS_STORE_ERR_CRC,
    FS_STORE_ERR_VERSION,  /* схема новіша за ту, яку розуміє прошивка */
    FS_STORE_ERR_FLASH,    /* запис не підтвердився зчитуванням */
    FS_STORE_ERR_NO_BANK   /* жоден банк не придатний, узято заводські дефолти */
} fs_store_status_t;

typedef struct {
    uint8_t data[FS_SECTOR_SIZE];
} fs_flash_sector_t;

typedef struct {
    fs_flash_sector_t bank[2];
    int               active;    /* банк, з якого востаннє успішно читали */
    uint32_t          last_seq;
} fs_param_store_t;

uint32_t fs_crc32(const uint8_t *data, uint32_t len);

void              fs_store_init(fs_param_store_t *st);
fs_store_status_t fs_store_decode(const fs_flash_sector_t *sec, fs_param_block_t *out,
                                  uint32_t *seq_out, int *migrated_out);
fs_store_status_t fs_store_load(fs_param_store_t *st, fs_param_block_t *out, int *bank_out);
fs_store_status_t fs_store_save(fs_param_store_t *st, const fs_param_block_t *b);

/* Стендовий гачок: імітує деградацію комірки Flash, щоб побачити роботу CRC. */
void fs_store_flip_bit(fs_param_store_t *st, int bank, uint32_t byte_off, int bit);

const char *fs_store_status_str(fs_store_status_t s);

#endif /* FS_STORAGE_H */
