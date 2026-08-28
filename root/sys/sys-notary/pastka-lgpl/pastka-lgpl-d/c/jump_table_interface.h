/* jump_table_interface.h — Інтерфейс виклику LGPL-модуля у Flash */
#pragma once
#include <stdint.h>
#include <stddef.h>

/* Фіксована адреса таблиці функцій у секторі LGPL */
#define LGPL_MODULE_BASE_ADDR 0x08080000

typedef struct {
    uint32_t magic_header;
    uint32_t api_version;
    int (*init)(void);
    int (*compress)(const uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len);
    int (*decompress)(const uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len);
} lgpl_driver_api_t;

/* Отримання покажчика на інтерфейс модуля */
static inline const lgpl_driver_api_t* get_lgpl_driver(void) {
    const lgpl_driver_api_t *driver = (const lgpl_driver_api_t *)LGPL_MODULE_BASE_ADDR;
    if (driver->magic_header != 0x4C47504C) { /* "LGPL" marker */
        return NULL;
    }
    return driver;
}
