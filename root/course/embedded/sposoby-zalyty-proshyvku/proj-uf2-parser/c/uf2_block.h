/*
 * Бінарний контракт формату UF2: константи, розкладка 512-байтного блоку
 * і перелік причин відмови. Усе, що стосується ОДНОГО сектора, живе тут.
 */
#ifndef UF2_BLOCK_H
#define UF2_BLOCK_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Дві сигнатури на початку блоку й одна в кінці. */
#define UF2_MAGIC_START0 0x0A324655UL /* "UF2\n" */
#define UF2_MAGIC_START1 0x9E5D5157UL
#define UF2_MAGIC_END    0x0AB16414UL

/* Прапорці з поля flags (біти, які нас справді обходять). */
#define UF2_FLAG_NOT_MAIN_FLASH 0x00000001UL /* блок не для основної Flash — пропустити */
#define UF2_FLAG_FILE_CONTAINER 0x00001000UL /* усередині файл, а не образ прошивки */
#define UF2_FLAG_FAMILY_ID      0x00002000UL /* на зсуві 28 лежить familyID, а не fileSize */

#define UF2_BLOCK_SIZE   512u /* дорівнює логічному сектору емульованого диска */
#define UF2_MAX_PAYLOAD  476u /* стільки байтів фізично вміщає data[] */

typedef enum {
    UF2_OK = 0,
    UF2_SKIPPED,               /* блок валідний, але писати його не треба */
    UF2_ERR_NULL_PTR,
    UF2_ERR_BAD_SECTOR_SIZE,
    UF2_ERR_BAD_MAGIC_START,
    UF2_ERR_BAD_MAGIC_END,
    UF2_ERR_FAMILY_MISMATCH,
    UF2_ERR_PAYLOAD_TOO_LARGE,
    UF2_ERR_INVALID_ADDRESS,
    UF2_ERR_TOTAL_BLOCKS_ZERO,
    UF2_ERR_BLOCK_INDEX_RANGE,
    UF2_ERR_BLOCK_COUNT_MISMATCH, /* два блоки одного файлу кажуть різне numBlocks */
    UF2_ERR_IMAGE_TOO_LARGE,      /* образ не вміщається у бітову карту сеансу */
    UF2_ERR_GEOMETRY,             /* адреса поза картою стертих секторів */
    UF2_ERR_FLASH_ERASE,
    UF2_ERR_FLASH_WRITE
} uf2_status_t;

/*
 * Розкладка сектора один-в-один. Усі поля — little-endian, як і ядро Cortex-M,
 * тож читаємо їх напряму, без перестановки байтів.
 */
typedef struct __attribute__((packed)) {
    uint32_t magic_start0;
    uint32_t magic_start1;
    uint32_t flags;
    uint32_t target_addr;
    uint32_t payload_size;
    uint32_t block_no;
    uint32_t num_blocks;
    uint32_t family_id; /* або file_size, якщо прапорця UF2_FLAG_FAMILY_ID немає */
    uint8_t  data[UF2_MAX_PAYLOAD];
    uint32_t magic_end;
} uf2_raw_block_t;

_Static_assert(sizeof(uf2_raw_block_t) == UF2_BLOCK_SIZE,
               "блок UF2 мусить бути рівно 512 байтів");

/* Те, що лишається від блоку після перевірок: куди писати й що саме. */
typedef struct {
    uint32_t       target_address;
    uint32_t       payload_length;
    uint32_t       block_index;
    uint32_t       total_blocks;
    const uint8_t *data_ptr; /* показує всередину переданого буфера, не копія */
} uf2_block_info_t;

/*
 * Розбирає один дисковий сектор. Повертає UF2_OK і заповнює out_info,
 * UF2_SKIPPED для валідного блоку, який писати не треба, або код відмови.
 * sector_len — скільки байтів реально приніс USB-стек.
 */
uf2_status_t uf2_parse_and_validate_block(const uint8_t *sector_buf,
                                          uint32_t       sector_len,
                                          uint32_t       expected_family_id,
                                          uint32_t       flash_start_addr,
                                          uint32_t       flash_size_bytes,
                                          uf2_block_info_t *out_info);

/*
 * true, якщо сектор просто не є блоком UF2 (службовий запис файлової системи).
 * Такий випадок — не збій носія, і хосту про нього казати не можна.
 */
bool uf2_is_foreign_sector(uf2_status_t status);

const char *uf2_status_str(uf2_status_t status);

#endif /* UF2_BLOCK_H */
