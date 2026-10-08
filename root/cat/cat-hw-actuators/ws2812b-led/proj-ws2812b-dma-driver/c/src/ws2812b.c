#include "ws2812b.h"
#include <string.h>

/**
 * @file ws2812b.c
 * @brief Реалізація високорівневої логіки C-драйвера WS2812B.
 *
 * Виконує конвертацію кольорів пікселів GRB у імпульси скважності TIM PWM,
 * керування стану асинхронного передавача та фонове подвійне буферування під час
 * обробки переривань DMA.
 */

ws2812b_color_t ws2812b_make_color(uint8_t r, uint8_t g, uint8_t b) {
    ws2812b_color_t color;
    color.r = r;
    color.g = g;
    color.b = b;
    return color;
}

ws2812b_err_t ws2812b_init(ws2812b_t *ws, ws2812b_color_t *buffer, uint16_t num_leds, volatile uint32_t *timer_reg) {
    if (!ws || !buffer || num_leds == 0 || !timer_reg) {
        return WS2812B_ERR_INVALID_ARG;
    }

    ws->pixel_buffer = buffer;
    ws->num_leds = num_leds;
    ws->state = WS2812B_STATE_IDLE;
    ws->current_pixel_idx = 0;
    ws->reset_bytes_sent = 0;

    /* Очищення буфера пікселів кадру */
    memset(ws->pixel_buffer, 0, num_leds * sizeof(ws2812b_color_t));

    /* Ініціалізація апаратного шару DMA з передачею callback-функції fill_dma_half */
    if (!ws2812b_dma_init(&ws->dma_hw, timer_reg, ws2812b_fill_dma_half, ws2812b_fill_dma_half)) {
        return WS2812B_ERR_DMA_FAIL;
    }

    return WS2812B_OK;
}

ws2812b_err_t ws2812b_set_pixel_rgb(ws2812b_t *ws, uint16_t index, uint8_t r, uint8_t g, uint8_t b) {
    if (!ws || !ws->pixel_buffer || index >= ws->num_leds) {
        return WS2812B_ERR_INVALID_ARG;
    }

    ws->pixel_buffer[index].r = r;
    ws->pixel_buffer[index].g = g;
    ws->pixel_buffer[index].b = b;

    return WS2812B_OK;
}

ws2812b_err_t ws2812b_set_pixel_color(ws2812b_t *ws, uint16_t index, ws2812b_color_t color) {
    return ws2812b_set_pixel_rgb(ws, index, color.r, color.g, color.b);
}

ws2812b_err_t ws2812b_set_pixel_hsv(ws2812b_t *ws, uint16_t index, uint16_t hue, uint8_t sat, uint8_t val) {
    if (!ws || index >= ws->num_leds) {
        return WS2812B_ERR_INVALID_ARG;
    }

    /* Нормалізація тону у межах 0..359 */
    hue %= 360;

    uint8_t r = 0, g = 0, b = 0;

    if (sat == 0) {
        /* Акроматичний колір (відтінки сірого) */
        r = val;
        g = val;
        b = val;
    } else {
        uint32_t region = hue / 60;
        uint32_t remainder = (hue % 60) * 255 / 60;

        uint8_t p = (val * (255 - sat)) / 255;
        uint8_t q = (val * (255 - ((sat * remainder) / 255))) / 255;
        uint8_t t = (val * (255 - ((sat * (255 - remainder)) / 255))) / 255;

        switch (region) {
            case 0:  r = val; g = t;   b = p;   break;
            case 1:  r = q;   g = val; b = p;   break;
            case 2:  r = p;   g = val; b = t;   break;
            case 3:  r = p;   g = q;   b = val; break;
            case 4:  r = t;   g = p;   b = val; break;
            default: r = val; g = p;   b = q;   break;
        }
    }

    return ws2812b_set_pixel_rgb(ws, index, r, g, b);
}

ws2812b_err_t ws2812b_clear(ws2812b_t *ws) {
    if (!ws || !ws->pixel_buffer) {
        return WS2812B_ERR_INVALID_ARG;
    }

    memset(ws->pixel_buffer, 0, ws->num_leds * sizeof(ws2812b_color_t));
    return WS2812B_OK;
}

/**
 * @brief Допоміжна функція кодування одного 24-бітного значення кольору (GRB) 
 * у масив тривалостей скважності PWM (24 елементи uint16_t).
 */
static void encode_grb_to_pwm(ws2812b_color_t color, uint16_t *dest) {
    /* Формат передачі WS2812B: 8 бітів Green (MSB first), 8 бітів Red, 8 бітів Blue */
    uint32_t grb_24bit = ((uint32_t)color.g << 16) |
                         ((uint32_t)color.r << 8)  |
                         ((uint32_t)color.b);

    for (int bit = 23; bit >= 0; bit--) {
        if ((grb_24bit >> bit) & 0x01) {
            *dest++ = WS2812B_DUTY_BIT_1;
        } else {
            *dest++ = WS2812B_DUTY_BIT_0;
        }
    }
}

ws2812b_err_t ws2812b_update(ws2812b_t *ws) {
    if (!ws) {
        return WS2812B_ERR_INVALID_ARG;
    }

    if (ws->state != WS2812B_STATE_IDLE) {
        return WS2812B_ERR_BUSY;
    }

    ws->state = WS2812B_STATE_SENDING;
    ws->current_pixel_idx = 0;
    ws->reset_bytes_sent = 0;

    /* Заповнюємо першу половину буфера DMA (піксель 0) */
    ws2812b_fill_dma_half(ws, 0);

    /* Заповнюємо другу половину буфера DMA (піксель 1 або нулі, якщо стрічка з 1 пікселя) */
    ws2812b_fill_dma_half(ws, 1);

    /* Запускаємо апаратний DMA обмін у круговому режимі */
    if (!ws2812b_dma_start(&ws->dma_hw)) {
        ws->state = WS2812B_STATE_IDLE;
        return WS2812B_ERR_DMA_FAIL;
    }

    return WS2812B_OK;
}

bool ws2812b_is_busy(const ws2812b_t *ws) {
    return (ws != NULL) && (ws->state != WS2812B_STATE_IDLE);
}

void ws2812b_fill_dma_half(ws2812b_t *ws, uint8_t half_idx) {
    if (!ws || half_idx > 1) {
        return;
    }

    /* Отримуємо вказівник на відповідне крило подвійного буфера DMA */
    uint16_t *dma_half_ptr = &ws->dma_hw.dma_buffer[half_idx * WS2812B_DMA_HALF_BUFFER_SIZE];

    if (ws->state == WS2812B_STATE_SENDING) {
        if (ws->current_pixel_idx < ws->num_leds) {
            /* Перетворюємо поточний піксель з колірного кадру GRB у 24 значення PWM */
            encode_grb_to_pwm(ws->pixel_buffer[ws->current_pixel_idx], dma_half_ptr);
            ws->current_pixel_idx++;
        } else {
            /* Передачу даних усіх пікселів завершено, переходимо до паузи скидання (RESET) */
            ws->state = WS2812B_STATE_RESETTING;
            memset(dma_half_ptr, 0, WS2812B_DMA_HALF_BUFFER_SIZE * sizeof(uint16_t));
            ws->reset_bytes_sent += WS2812B_DMA_HALF_BUFFER_SIZE;
        }
    } else if (ws->state == WS2812B_STATE_RESETTING) {
        /* Формуємо логічний нуль для паузи скидання WS2812B (RESET pulse > 50 мкс) */
        memset(dma_half_ptr, 0, WS2812B_DMA_HALF_BUFFER_SIZE * sizeof(uint16_t));
        ws->reset_bytes_sent += WS2812B_DMA_HALF_BUFFER_SIZE;

        if (ws->reset_bytes_sent >= WS2812B_RESET_BITS_COUNT) {
            /* Паузу скидання сформовано, зупиняємо DMA та переходимо у стан IDLE */
            ws2812b_dma_stop(&ws->dma_hw);
            ws->state = WS2812B_STATE_IDLE;
        }
    } else {
        /* Якщо перебуваємо у IDLE, заповнюємо нулями */
        memset(dma_half_ptr, 0, WS2812B_DMA_HALF_BUFFER_SIZE * sizeof(uint16_t));
    }
}
