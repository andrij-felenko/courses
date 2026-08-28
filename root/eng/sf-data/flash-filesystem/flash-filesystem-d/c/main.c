#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include "lfs.h"

#define LOG_FILE_PATH   "/telemetry.log"
#define MAX_LOG_LINE    128

bool append_telemetry_event(lfs_t *lfs, uint32_t timestamp, float voltage, float temperature) {
    lfs_file_t file;
    char buffer[MAX_LOG_LINE];

    /* Форматуємо рядок журналу */
    int len = snprintf(buffer, sizeof(buffer), "TS:%lu;V:%.2f;T:%.2f\n", 
                       (unsigned long)timestamp, voltage, temperature);
    if (len < 0 || len >= (int)sizeof(buffer)) {
        return false;
    }

    /* Відкриваємо файл у режимі дописування: LFS_O_WRONLY | LFS_O_CREAT | LFS_O_APPEND */
    int err = lfs_file_open(lfs, &file, LOG_FILE_PATH, LFS_O_WRONLY | LFS_O_CREAT | LFS_O_APPEND);
    if (err < 0) {
        return false;
    }

    /* Дописуємо рядок у кінець файлу через CTZ-структуру */
    lfs_ssize_t written = lfs_file_write(lfs, &file, buffer, (lfs_size_t)len);
    
    /* Обов'язкове закриття файлу фіксує нові метадані в парі блоків */
    int close_err = lfs_file_close(lfs, &file);

    return (written == len) && (close_err == LFS_ERR_OK);
}

bool dump_telemetry_events(lfs_t *lfs) {
    lfs_file_t file;
    char buffer[MAX_LOG_LINE];

    int err = lfs_file_open(lfs, &file, LOG_FILE_PATH, LFS_O_RDONLY);
    if (err < 0) {
        return false;
    }

    lfs_ssize_t read_bytes;
    while ((read_bytes = lfs_file_read(lfs, &file, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[read_bytes] = '\0';
        printf("%s", buffer);
    }

    lfs_file_close(lfs, &file);
    return read_bytes == 0;
}
