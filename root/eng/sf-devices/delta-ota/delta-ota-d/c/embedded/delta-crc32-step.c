#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define DELTA_MAGIC         0x44454C54U /* Символи "DELT" у форматі Little-Endian */
#define FLASH_PAGE_SIZE     256U        /* Фізичний розмір сторінки програмування Flash */
#define FLASH_SECTOR_SIZE   4096U       /* Розмір сектора стирання Flash */

/* Коди результату виконання операцій дельта-рушія */
typedef enum {
    DELTA_OK = 0,
    DELTA_ERR_MAGIC,
    DELTA_ERR_SOURCE_HASH,
    DELTA_ERR_TARGET_HASH,
    DELTA_ERR_FLASH_IO,
    DELTA_ERR_STREAM_CORRUPT
} delta_status_t;

/* Заголовок бінарного пакета дельта-оновлення */
typedef struct {
    uint32_t magic;
    uint8_t  version;
    uint8_t  compression_type;
    uint16_t sector_size;
    uint32_t source_size;
    uint32_t target_size;
    uint32_t patch_size;
    uint8_t  sha256_source[32];
    uint8_t  sha256_target[32];
    uint32_t crc32_header;
} __attribute__((packed)) delta_header_t;

/* Абстрактний інтерфейс драйвера Flash-пам'яті (FAL) */
typedef struct {
    bool (*read)(uint32_t address, uint8_t *dst, uint32_t len);
    bool (*write)(uint32_t address, const uint8_t *src, uint32_t len);
    bool (*erase_sector)(uint32_t sector_address);
} delta_flash_ops_t;

/* Робочий контекст дельта-реконструктора у статичній пам'яті */
typedef struct {
    delta_header_t header;
    const delta_flash_ops_t *flash;
    uint32_t source_base_addr;
    uint32_t target_base_addr;
    uint32_t current_old_offset;
    uint32_t current_new_offset;
    uint8_t  page_buffer[FLASH_PAGE_SIZE];
    uint16_t page_buf_idx;
    uint32_t running_crc;
} delta_context_t;

/* Проста цілочисельна функція оновлення CRC-32 без таблиць для економії ROM */
static uint32_t delta_crc32_step(uint32_t crc, uint8_t data) {
    crc ^= data;
    for (uint8_t bit = 0; bit < 8; bit++) {
        if (crc & 1U) {
            crc = (crc >> 1) ^ 0xEDB88320U;
        } else {
            crc = (crc >> 1);
        }
    }
    return crc;
}

/* Ініціалізація контексту та валідація службового заголовка */
delta_status_t delta_init(delta_context_t *ctx,
                          const delta_header_t *hdr,
                          const delta_flash_ops_t *flash_ops,
                          uint32_t src_addr,
                          uint32_t dst_addr) {
    if (!ctx || !hdr || !flash_ops) {
        return DELTA_ERR_STREAM_CORRUPT;
    }

    if (hdr->magic != DELTA_MAGIC) {
        return DELTA_ERR_MAGIC;
    }

    ctx->header = *hdr;
    ctx->flash = flash_ops;
    ctx->source_base_addr = src_addr;
    ctx->target_base_addr = dst_addr;
    ctx->current_old_offset = 0;
    ctx->current_new_offset = 0;
    ctx->page_buf_idx = 0;
    ctx->running_crc = 0xFFFFFFFFU;

    return DELTA_OK;
}

/* Скидання накопиченого буфера сторінки на фізичний кристал Flash */
static delta_status_t delta_flush_page(delta_context_t *ctx) {
    if (ctx->page_buf_idx == 0) {
        return DELTA_OK;
    }

    /* Якщо сторінка на межі сектора — виконуємо апаратне стирання перед записом */
    uint32_t target_addr = ctx->target_base_addr + ctx->current_new_offset;
    if ((target_addr % FLASH_SECTOR_SIZE) == 0) {
        if (!ctx->flash->erase_sector(target_addr)) {
            return DELTA_ERR_FLASH_IO;
        }
    }

    /* Програмування сторінки через шар абстракції FAL */
    if (!ctx->flash->write(target_addr, ctx->page_buffer, ctx->page_buf_idx)) {
        return DELTA_ERR_FLASH_IO;
    }

    ctx->current_new_offset += ctx->page_buf_idx;
    ctx->page_buf_idx = 0;
    return DELTA_OK;
}

/* Потокова обробка блоку додавання: Target[k] = (Old[k] + Diff[k]) mod 256 */
delta_status_t delta_apply_add_chunk(delta_context_t *ctx,
                                     const uint8_t *diff_data,
                                     uint32_t len) {
    uint8_t old_byte;

    for (uint32_t i = 0; i < len; i++) {
        /* Зчитування вихідного байта базового образу */
        uint32_t old_addr = ctx->source_base_addr + ctx->current_old_offset;
        if (!ctx->flash->read(old_addr, &old_byte, 1)) {
            return DELTA_ERR_FLASH_IO;
        }

        /* Арифметичне додавання за модулем 256 */
        uint8_t reconstructed = (uint8_t)(old_byte + diff_data[i]);
        ctx->page_buffer[ctx->page_buf_idx++] = reconstructed;
        ctx->running_crc = delta_crc32_step(ctx->running_crc, reconstructed);
        ctx->current_old_offset++;

        /* Запис на фізичний кристал при заповненні апаратної сторінки */
        if (ctx->page_buf_idx >= FLASH_PAGE_SIZE) {
            delta_status_t res = delta_flush_page(ctx);
            if (res != DELTA_OK) {
                return res;
            }
        }
    }
    return DELTA_OK;
}

/* Обробка вставки абсолютно нових даних (extra-потік) */
delta_status_t delta_apply_copy_chunk(delta_context_t *ctx,
                                      const uint8_t *extra_data,
                                      uint32_t len) {
    for (uint32_t i = 0; i < len; i++) {
        ctx->page_buffer[ctx->page_buf_idx++] = extra_data[i];
        ctx->running_crc = delta_crc32_step(ctx->running_crc, extra_data[i]);

        if (ctx->page_buf_idx >= FLASH_PAGE_SIZE) {
            delta_status_t res = delta_flush_page(ctx);
            if (res != DELTA_OK) {
                return res;
            }
        }
    }
    return DELTA_OK;
}

/* Зсув показчика базового образу старої прошивки */
void delta_seek_old(delta_context_t *ctx, int32_t seek_offset) {
    ctx->current_old_offset = (uint32_t)((int32_t)ctx->current_old_offset + seek_offset);
}

/* Фіналізація: виштовхування залишку байтів та перевірка повної довжини */
delta_status_t delta_finalize(delta_context_t *ctx) {
    delta_status_t res = delta_flush_page(ctx);
    if (res != DELTA_OK) {
        return res;
    }

    if (ctx->current_new_offset != ctx->header.target_size) {
        return DELTA_ERR_STREAM_CORRUPT;
    }

    return DELTA_OK;
}
