#include "ff.h"
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define LOG_FILE_PATH       "0:/telemetry.bin"
#define LOG_HEADER_MAGIC    0x4C4F4752U  /* 'LOGR' */
#define SECTOR_SIZE         512U

/* Структура заголовка лог-файлу, вирівняна за розміром сектора */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t version;
    uint32_t write_offset;
    uint32_t read_offset;
    uint32_t total_records;
    uint32_t crc32;
    uint8_t  padding[SECTOR_SIZE - 24U];
} LogFileHeader_t;

/* Функція ініціалізації та предвиділення суцільного файла */
FRESULT log_file_preallocate(FIL *fp, FSIZE_t required_bytes) {
    FRESULT res;

    /* 1. Відкриваємо або створюємо файл із правами запису та читання */
    res = f_open(fp, LOG_FILE_PATH, FA_READ | FA_WRITE | FA_OPEN_ALWAYS);
    if (res != FR_OK) {
        return res;
    }

    /* 2. Перевіряємо, чи новий це файл, або чи його розмір менший за необхідний */
    if (f_size(fp) < required_bytes) {
        /* Переміщуємо вказівник на початок для чистої ініціалізації */
        res = f_lseek(fp, 0);
        if (res != FR_OK) {
            f_close(fp);
            return res;
        }

        /* 3. Застосовуємо f_expand для суцільного резервування кластерів (opt = 1) */
        res = f_expand(fp, required_bytes, 1);
        if (res != FR_OK) {
            /* Якщо суцільний блок не виділено, закриваємо файл */
            f_close(fp);
            return res;
        }

        /* 4. Записуємо початковий заголовок лог-файлу */
        LogFileHeader_t header;
        memset(&header, 0, sizeof(header));
        header.magic = LOG_HEADER_MAGIC;
        header.version = 1U;
        header.write_offset = sizeof(LogFileHeader_t);
        header.read_offset = sizeof(LogFileHeader_t);

        UINT bytes_written = 0;
        res = f_write(fp, &header, sizeof(header), &bytes_written);
        if (res != FR_OK || bytes_written != sizeof(header)) {
            f_close(fp);
            return res;
        }

        /* 5. Примусово скидаємо буфери на диск один раз під час ініціалізації */
        res = f_sync(fp);
        if (res != FR_OK) {
            f_close(fp);
            return res;
        }
    }

    /* Встановлюємо вказівник на початок області даних для подальшої роботи */
    return f_lseek(fp, sizeof(LogFileHeader_t));
}
