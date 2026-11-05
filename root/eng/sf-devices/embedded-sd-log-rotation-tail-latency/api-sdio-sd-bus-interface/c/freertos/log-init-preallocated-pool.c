#include "ff.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define LOG_FILE_COUNT      4
#define LOG_FILE_SIZE       (10 * 1024 * 1024) // 10 МБ на файл
#define SECTOR_SIZE         512
#define BUFFER_SECTORS      8
#define RAM_BUFFER_SIZE     (SECTOR_SIZE * BUFFER_SECTORS) // 4096 байтів

typedef struct {
    uint32_t timestamp_ms;
    uint16_t event_id;
    uint16_t payload_len;
    uint8_t  data[56];
} __attribute__((packed)) log_entry_t;

static FIL g_log_file;
static uint8_t g_ram_buffer[RAM_BUFFER_SIZE] __attribute__((aligned(4)));
static uint32_t g_buffer_offset = 0;
static uint32_t g_current_file_idx = 0;
static uint32_t g_bytes_written_in_file = 0;

FRESULT log_init_preallocated_pool(void) {
    FRESULT res;
    char file_name[32];

    for (uint32_t i = 0; i < LOG_FILE_COUNT; i++) {
        snprintf(file_name, sizeof(file_name), "0:/LOG_%03lu.BIN", (unsigned long)i);
        res = f_open(&g_log_file, file_name, FA_WRITE | FA_OPEN_ALWAYS);
        if (res != FR_OK) return res;

        // Попереднє виділення суцільного ланцюжка кластерів на диску
        res = f_expand(&g_log_file, LOG_FILE_SIZE, 1);
        if (res != FR_OK && res != FR_EXIST) {
            f_close(&g_log_file);
            return res;
        }
        f_close(&g_log_file);
    }

    // Відкриття першого файла для запису з позиції 0
    snprintf(file_name, sizeof(file_name), "0:/LOG_%03lu.BIN", (unsigned long)g_current_file_idx);
    res = f_open(&g_log_file, file_name, FA_WRITE | FA_OPEN_EXISTING);
    if (res == FR_OK) {
        res = f_lseek(&g_log_file, 0);
    }
    return res;
}

static FRESULT log_flush_buffer_to_sd(void) {
    if (g_buffer_offset == 0) return FR_OK;

    UINT bw = 0;
    FRESULT res = f_write(&g_log_file, g_ram_buffer, g_buffer_offset, &bw);
    if (res == FR_OK) {
        g_bytes_written_in_file += bw;
        g_buffer_offset = 0;
    }
    return res;
}

FRESULT log_write_entry(const log_entry_t *entry) {
    FRESULT res = FR_OK;
    const uint8_t *src = (const uint8_t *)entry;
    uint32_t bytes_to_copy = sizeof(log_entry_t);

    // Ротація файла при досягненні ліміту розміру
    if (g_bytes_written_in_file + g_buffer_offset + bytes_to_copy >= LOG_FILE_SIZE) {
        log_flush_buffer_to_sd();
        f_sync(&g_log_file);
        f_close(&g_log_file);

        g_current_file_idx = (g_current_file_idx + 1) % LOG_FILE_COUNT;
        g_bytes_written_in_file = 0;

        char file_name[32];
        snprintf(file_name, sizeof(file_name), "0:/LOG_%03lu.BIN", (unsigned long)g_current_file_idx);
        res = f_open(&g_log_file, file_name, FA_WRITE | FA_OPEN_EXISTING);
        if (res != FR_OK) return res;
        
        // Скидаємо покажчик на початок без видалення файла
        res = f_lseek(&g_log_file, 0);
        if (res != FR_OK) return res;
    }

    // Накопичення в RAM буфері до розміру сектора
    while (bytes_to_copy > 0) {
        uint32_t space_left = RAM_BUFFER_SIZE - g_buffer_offset;
        uint32_t chunk = (bytes_to_copy < space_left) ? bytes_to_copy : space_left;

        memcpy(&g_ram_buffer[g_buffer_offset], src, chunk);
        g_buffer_offset += chunk;
        src += chunk;
        bytes_to_copy -= chunk;

        if (g_buffer_offset >= RAM_BUFFER_SIZE) {
            res = log_flush_buffer_to_sd();
            if (res != FR_OK) break;
        }
    }
    return res;
}
