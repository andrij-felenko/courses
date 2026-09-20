#include "../include/rotary_adc_selector.h"
#include <stdlib.h>

/**
 * @brief Допоміжна функція швидкої медіанної фільтрації для 3 відліків
 */
static uint16_t median_of_three(uint16_t a, uint16_t b, uint16_t c) {
    if ((a <= b && b <= c) || (c <= b && b <= a)) {
        return b;
    }
    if ((b <= a && a <= c) || (c <= a && a <= b)) {
        return a;
    }
    return c;
}

rotary_status_t rotary_selector_init(rotary_selector_t *handle, const rotary_config_t *config) {
    if (handle == NULL || config == NULL) {
        return ROTARY_STATUS_ERR_INVALID_ARG;
    }

    /* Копіювання конфігурації у внутрішній дескриптор */
    handle->config = *config;

    /* Очищення кільцевого буфера фільтра */
    for (uint8_t i = 0; i < ROTARY_MEDIAN_WINDOW_SIZE; i++) {
        handle->median_buffer[i] = 0;
    }

    handle->buffer_index = 0;
    handle->buffer_filled = false;
    handle->current_position = -1;
    handle->last_status = ROTARY_STATUS_OK;

    return ROTARY_STATUS_OK;
}

rotary_status_t rotary_selector_update(rotary_selector_t *handle, uint16_t raw_adc, int8_t *out_position) {
    if (handle == NULL || out_position == NULL) {
        return ROTARY_STATUS_ERR_INVALID_ARG;
    }

    /* 1. Запис нового відліку у кільцевий буфер */
    handle->median_buffer[handle->buffer_index] = raw_adc;
    handle->buffer_index = (handle->buffer_index + 1) % ROTARY_MEDIAN_WINDOW_SIZE;

    if (handle->buffer_index == 0) {
        handle->buffer_filled = true;
    }

    /* 2. Зчитування відфільтрованого значення через медіанний фільтр */
    uint16_t filtered_adc;
    if (handle->buffer_filled) {
        filtered_adc = median_of_three(handle->median_buffer[0],
                                       handle->median_buffer[1],
                                       handle->median_buffer[2]);
    } else {
        filtered_adc = raw_adc; /* До повного заповнення буфера використовується сирий відлік */
    }

    /* 3. Двостороння перевірка крайніх аварійних зон (обрив та КЗ) */
    if (filtered_adc < handle->config.min_valid_adc) {
        handle->current_position = -1;
        handle->last_status = ROTARY_STATUS_ERR_SHORT_GND;
        *out_position = -1;
        return ROTARY_STATUS_ERR_SHORT_GND;
    }

    if (filtered_adc > handle->config.max_valid_adc) {
        handle->current_position = -1;
        handle->last_status = ROTARY_STATUS_ERR_OPEN_CIRCUIT;
        *out_position = -1;
        return ROTARY_STATUS_ERR_OPEN_CIRCUIT;
    }

    /* 4. Пошук найближчої позиції із врахуванням цифрового гістерезису */
    int8_t best_position = -1;
    uint32_t min_delta = 0xFFFFFFFF;

    for (uint8_t i = 0; i < ROTARY_SELECTOR_POSITIONS; i++) {
        uint16_t ref = handle->config.reference_levels[i];
        uint32_t delta = (filtered_adc >= ref) ? (filtered_adc - ref) : (ref - filtered_adc);

        /* Якщо це поточна підтверджена позиція, надаємо їй перевагу за рахунок вікна гістерезису */
        if (i == (uint8_t)handle->current_position) {
            if (delta > handle->config.hysteresis_window) {
                delta -= handle->config.hysteresis_window;
            } else {
                delta = 0;
            }
        }

        if (delta < min_delta) {
            min_delta = delta;
            best_position = (int8_t)i;
        }
    }

    /* 5. Фіксація та підтвердження нової позиції */
    handle->current_position = best_position;
    handle->last_status = ROTARY_STATUS_OK;
    *out_position = best_position;

    return ROTARY_STATUS_OK;
}
