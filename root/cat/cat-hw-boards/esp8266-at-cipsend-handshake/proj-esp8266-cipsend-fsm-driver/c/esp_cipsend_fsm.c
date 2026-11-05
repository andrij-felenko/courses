#include "esp_cipsend_fsm.h"
#include <stdio.h>
#include <string.h>

void esp_cipsend_init(esp_cipsend_t *ctx, esp_uart_hal_t *hal) {
    ctx->state = CIPSEND_STATE_IDLE;
    ctx->hal = hal;
    ctx->tx_data = NULL;
    ctx->tx_len = 0;
    ctx->timer_start = 0;
    ctx->timeout_ms = 0;
}

bool esp_cipsend_start(esp_cipsend_t *ctx, const uint8_t *data, uint16_t len, uint32_t timeout_ms) {
    if (ctx->state != CIPSEND_STATE_IDLE && ctx->state != CIPSEND_STATE_ERROR) {
        return false; // Вже щось передаємо
    }

    ctx->tx_data = data;
    ctx->tx_len = len;
    ctx->timeout_ms = timeout_ms;
    
    // Формуємо та відправляємо команду AT+CIPSEND
    char cmd[32];
    int cmd_len = snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%u\r\n", len);
    ctx->hal->uart_write((const uint8_t *)cmd, (uint16_t)cmd_len);
    
    ctx->timer_start = ctx->hal->get_tick_ms();
    ctx->state = CIPSEND_STATE_WAIT_PROMPT;
    
    return true;
}

void esp_cipsend_tick(esp_cipsend_t *ctx) {
    uint8_t c;
    
    // Перевірка таймауту
    if (ctx->state == CIPSEND_STATE_WAIT_PROMPT || ctx->state == CIPSEND_STATE_WAIT_OK) {
        if (ctx->hal->get_tick_ms() - ctx->timer_start > ctx->timeout_ms) {
            ctx->state = CIPSEND_STATE_ERROR;
            return;
        }
    }

    switch (ctx->state) {
        case CIPSEND_STATE_WAIT_PROMPT:
            // Читаємо UART по символу, чекаємо на символ '>'
            while (ctx->hal->uart_read_char(&c)) {
                if (c == '>') {
                    // Модем готовий приймати дані
                    ctx->hal->uart_write(ctx->tx_data, ctx->tx_len);
                    ctx->timer_start = ctx->hal->get_tick_ms();
                    ctx->state = CIPSEND_STATE_WAIT_OK;
                    break;
                } else if (c == 'E') {
                    // Спрощений приклад обробки "ERROR" (наївний)
                    // У реальному житті варто збирати буфер і шукати підрядок "ERROR"
                    // ctx->state = CIPSEND_STATE_ERROR;
                }
            }
            break;

        case CIPSEND_STATE_WAIT_OK:
            // Чекаємо на "SEND OK", шукаючи 'K' (спрощено)
            while (ctx->hal->uart_read_char(&c)) {
                if (c == 'K') { 
                    ctx->state = CIPSEND_STATE_IDLE; // Успішно завершено
                    break;
                }
            }
            break;
            
        case CIPSEND_STATE_IDLE:
        case CIPSEND_STATE_ERROR:
        default:
            // Нічого не робимо
            break;
    }
}

esp_cipsend_state_t esp_cipsend_get_state(const esp_cipsend_t *ctx) {
    return ctx->state;
}
