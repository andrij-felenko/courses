#include "ff.h"
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define LOG_FILE_SIZE    (16 * 1024 * 1024) // 16 MiB
#define MAX_LOG_FILES    4

typedef struct {
    FIL file;
    uint8_t current_file_idx;
    uint32_t current_offset;
    bool is_open;
} binary_logger_t;

static const char* log_filenames[MAX_LOG_FILES] = {
    "0:/log_0.bin",
    "0:/log_1.bin",
    "0:/log_2.bin",
    "0:/log_3.bin"
};

// Попереднє виділення суцільного простору для всіх файлів ротації
FRESULT logger_init_preallocated(binary_logger_t *logger) {
    FRESULT fr;
    logger->current_file_idx = 0;
    logger->current_offset = 0;
    logger->is_open = false;

    for (int i = 0; i < MAX_LOG_FILES; i++) {
        FIL tmp_file;
        fr = f_open(&tmp_file, log_filenames[i], FA_CREATE_ALWAYS | FA_WRITE | FA_READ);
        if (fr != FR_OK) return fr;

        // Виділення неперервного ланцюжка кластерів
        fr = f_expand(&tmp_file, LOG_FILE_SIZE, 1);
        if (fr != FR_OK) {
            f_close(&tmp_file);
            return fr;
        }
        f_close(&tmp_file);
    }

    // Відкриття першого файлу кільця для потокового запису
    fr = f_open(&logger->file, log_filenames[0], FA_WRITE);
    if (fr == FR_OK) {
        logger->is_open = true;
    }
    return fr;
}

// Запис блоку даних із використанням кільцевої ротації
FRESULT logger_write_chunk(binary_logger_t *logger, const void *data, UINT len) {
    if (!logger->is_open) return FR_INT_ERR;

    // Перевірка межі попередньо виділеного обсягу
    if (logger->current_offset + len > LOG_FILE_SIZE) {
        f_sync(&logger->file);
        f_close(&logger->file);

        // Перехід до наступного файлу у кільці
        logger->current_file_idx = (logger->current_file_idx + 1) % MAX_LOG_FILES;
        logger->current_offset = 0;

        FRESULT fr = f_open(&logger->file, log_filenames[logger->current_file_idx], FA_WRITE);
        if (fr != FR_OK) {
            logger->is_open = false;
            return fr;
        }
        f_lseek(&logger->file, 0);
    }

    UINT bytes_written = 0;
    FRESULT fr = f_write(&logger->file, data, len, &bytes_written);
    if (fr == FR_OK) {
        logger->current_offset += bytes_written;
    }
    return fr;
}
