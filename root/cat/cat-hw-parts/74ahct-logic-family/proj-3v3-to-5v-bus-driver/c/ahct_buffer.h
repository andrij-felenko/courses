#ifndef AHCT_BUFFER_H
#define AHCT_BUFFER_H

#include "gpio_hal.h"

typedef struct {
    bool is_enabled;
} ahct_buffer_t;

static inline void ahct_buffer_init(ahct_buffer_t *buf) {
    buf->is_enabled = false;
    gpio_hal_init();
    /* Гарантуємо вимкнений стан буфера на старті */
    gpio_set_oe(false);
}

static inline void ahct_buffer_enable(ahct_buffer_t *buf) {
    buf->is_enabled = true;
    gpio_set_oe(true);
}

static inline void ahct_buffer_disable(ahct_buffer_t *buf) {
    buf->is_enabled = false;
    gpio_set_oe(false);
}

static inline void ahct_buffer_verify_signal(const ahct_buffer_t *buf) {
    if (buf->is_enabled) {
        /* Генеруємо тестовий імпульс лише коли буфер активовано */
        gpio_pulse_signal();
    }
}

#endif /* AHCT_BUFFER_H */
