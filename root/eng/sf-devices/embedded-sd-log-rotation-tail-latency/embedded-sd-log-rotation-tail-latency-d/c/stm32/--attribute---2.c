#include "ff.h"
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define SECTOR_SIZE         512U
#define LOG_HEADER_MAGIC    0x4C4F4752U

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t version;
    uint32_t write_offset;
    uint32_t read_offset;
    uint32_t total_records;
    uint32_t crc32;
    uint8_t  padding[SECTOR_SIZE - 24U];
} LogHeader_t;

typedef struct {
    FIL         file;
    LogHeader_t header;
    uint32_t    data_start_offset;
    uint32_t    file_total_size;
    bool        is_open;
} LogRotator_t;

/* Скидання актуального заголовка логу на диск */
static FRESULT log_rotator_flush_header(LogRotator_t *rotator) {
    FRESULT res;
    UINT written = 0;

    res = f_lseek(&rotator->file, 0);
    if (res != FR_OK) return res;

    res = f_write(&rotator->file, &rotator->header, sizeof(LogHeader_t), &written);
    if (res != FR_OK || written != sizeof(LogHeader_t)) return res;

    /* Скидання внутрішнього секторного буфера FatFs на карту */
    return f_sync(&rotator->file);
}

/* Запис блоку даних у кільцевий файл без розширення розміру */
FRESULT log_rotator_write_record(LogRotator_t *rotator, const void *data, uint32_t data_len) {
    if (!rotator || !rotator->is_open || !data || data_len == 0) {
        return FR_INVALID_PARAMETER;
    }

    FRESULT res;
    UINT written = 0;
    uint32_t current_pos = rotator->header.write_offset;

    /* Перевірка на переповнення предвиділеної межі файла */
    if (current_pos + data_len > rotator->file_total_size) {
        /* Обгортання вказівника запису на початок області даних */
        current_pos = rotator->data_start_offset;
    }

    /* Позиціонування у визначений зсув суцільного файла */
    res = f_lseek(&rotator->file, current_pos);
    if (res != FR_OK) {
        return res;
    }

    /* Запис даних у зарезервовані сектори диска */
    res = f_write(&rotator->file, data, data_len, &written);
    if (res != FR_OK || written != data_len) {
        return res;
    }

    /* Оновлення вказівника запису та лічильників */
    rotator->header.write_offset = current_pos + data_len;
    rotator->header.total_records++;

    /* Періодичне скидання заголовка при досягненні кожної сотні записів */
    if ((rotator->header.total_records % 100U) == 0U) {
        log_rotator_flush_header(rotator);
    }

    return FR_OK;
}
