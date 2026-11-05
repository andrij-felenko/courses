#include "lvc_buffer.h"

/**
 * @file lvc_buffer.c
 * @brief Реалізація драйвера 74LVC1G125 з апаратною затримкою безпечного перемикання.
 */

/* Зовнішня функція апаратної затримки платформи в мікросекундах (наприклад, delay_us із SDK) */
extern void platform_delay_us(uint32_t us);

bool lvc_buffer_init(lvc_buffer_t *buf, const lvc_buffer_config_t *config) {
    if (buf == NULL || config == NULL || config->set_oe_pin == NULL) {
        return false;
    }

    buf->config = *config;
    
    /* За замовчуванням при ініціалізації переводимо буфер у безпечний стан Hi-Z (/OE = HIGH) */
    buf->current_state = LVC_BUFFER_STATE_HI_Z;
    buf->config.set_oe_pin(true);

    return true;
}

void lvc_buffer_enable(lvc_buffer_t *buf) {
    if (buf == NULL) {
        return;
    }

    if (buf->current_state != LVC_BUFFER_STATE_ENABLED) {
        buf->current_state = LVC_BUFFER_STATE_ENABLED;
        /* /OE активний на низькому рівні (LOW) */
        buf->config.set_oe_pin(false);
    }
}

void lvc_buffer_disable(lvc_buffer_t *buf) {
    if (buf == NULL) {
        return;
    }

    if (buf->current_state != LVC_BUFFER_STATE_HI_Z) {
        buf->current_state = LVC_BUFFER_STATE_HI_Z;
        /* /OE неактивний на високому рівні (HIGH) -> стан Hi-Z */
        buf->config.set_oe_pin(true);
    }
}

void lvc_buffer_switch_channel(lvc_buffer_t *active_buf, lvc_buffer_t *next_buf) {
    /* 1. Break: вимикаємо поточний активний передавач (якщо він заданий і ввімкнений) */
    if (active_buf != NULL && active_buf->current_state == LVC_BUFFER_STATE_ENABLED) {
        lvc_buffer_disable(active_buf);
        
        /* Витримуємо захисний інтервал break-before-make для гарантованого переходу в Hi-Z */
        if (active_buf->config.delay_us > 0) {
            platform_delay_us(active_buf->config.delay_us);
        }
    } else if (next_buf != NULL && next_buf->config.delay_us > 0) {
        /* Якщо активного не було, але задана затримка наступного */
        platform_delay_us(next_buf->config.delay_us);
    }

    /* 2. Make: вмикаємо новий буфер (якщо заданий) */
    if (next_buf != NULL) {
        lvc_buffer_enable(next_buf);
    }
}
