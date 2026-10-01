#include "esp8266_at_gpio.h"
#include <stdio.h>
#include <string.h>

static void send_string(esp8266_driver_t *drv, const char *str) {
    while (*str) {
        drv->uart_send((uint8_t)*str);
        str++;
    }
}

void esp8266_init(esp8266_driver_t *drv, uart_send_byte_fn send_fn, urc_gpio_event_cb_t urc_cb) {
    if (!drv) return;
    drv->state = ESP_STATE_IDLE;
    drv->uart_send = send_fn;
    drv->urc_callback = urc_cb;
    drv->rx_index = 0;
    drv->timer_ms = 0;
    drv->timeout_ms = 1000;
    drv->response_received = false;
    drv->last_command_ok = false;
    memset(drv->rx_buffer, 0, sizeof(drv->rx_buffer));
}

// Побайтовий аналіз вхідного потоку UART та розбір рядків
void esp8266_process_rx_byte(esp8266_driver_t *drv, char byte) {
    if (!drv) return;

    if (byte == '\n' || byte == '\r') {
        if (drv->rx_index > 0) {
            drv->rx_buffer[drv->rx_index] = '\0';

            // Перевірка на асинхронне сповіщення URC: +GPIO_INT:<pin>,<val>
            if (strncmp(drv->rx_buffer, "+GPIO_INT:", 10) == 0) {
                int pin = 0, val = 0;
                if (sscanf(drv->rx_buffer + 10, "%d,%d", &pin, &val) == 2) {
                    if (drv->urc_callback) {
                        drv->urc_callback((uint8_t)pin, (uint8_t)val);
                    }
                }
            }
            // Перевірка статусних відповідей на команди
            else if (strcmp(drv->rx_buffer, "OK") == 0) {
                drv->last_command_ok = true;
                drv->response_received = true;
                drv->state = ESP_STATE_IDLE;
            } else if (strcmp(drv->rx_buffer, "ERROR") == 0) {
                drv->last_command_ok = false;
                drv->response_received = true;
                drv->state = ESP_STATE_ERROR;
            }

            drv->rx_index = 0;
        }
    } else {
        if (drv->rx_index < RX_BUFFER_SIZE - 1) {
            drv->rx_buffer[drv->rx_index++] = byte;
        }
    }
}

// Оновлення таймера FSM для відстеження таймаутів
void esp8266_update_tick(esp8266_driver_t *drv, uint32_t delta_ms) {
    if (!drv) return;

    if (drv->state == ESP_STATE_WAIT_RESPONSE) {
        drv->timer_ms += delta_ms;
        if (drv->timer_ms >= drv->timeout_ms) {
            drv->state = ESP_STATE_TIMEOUT;
            drv->last_command_ok = false;
        }
    }
}

// Встановлення напрямку виводу (AT+SYSGPIODIR)
bool esp8266_set_gpio_mode(esp8266_driver_t *drv, uint8_t pin, gpio_mode_t mode) {
    if (!drv || drv->state == ESP_STATE_WAIT_RESPONSE) return false;

    char cmd[TX_BUFFER_SIZE];
    snprintf(cmd, sizeof(cmd), "AT+SYSGPIODIR=%d,%d\r\n", pin, (int)mode);

    drv->rx_index = 0;
    drv->response_received = false;
    drv->timer_ms = 0;
    drv->state = ESP_STATE_WAIT_RESPONSE;

    send_string(drv, cmd);
    return true;
}

// Запис логічного рівня на вивід (AT+SYSGPIOWRITE)
bool esp8266_write_gpio(esp8266_driver_t *drv, uint8_t pin, uint8_t value) {
    if (!drv || drv->state == ESP_STATE_WAIT_RESPONSE) return false;

    char cmd[TX_BUFFER_SIZE];
    snprintf(cmd, sizeof(cmd), "AT+SYSGPIOWRITE=%d,%d\r\n", pin, value ? 1 : 0);

    drv->rx_index = 0;
    drv->response_received = false;
    drv->timer_ms = 0;
    drv->state = ESP_STATE_WAIT_RESPONSE;

    send_string(drv, cmd);
    return true;
}

// Зчитування логічного рівня з виводу (AT+SYSGPIOREAD)
bool esp8266_read_gpio(esp8266_driver_t *drv, uint8_t pin) {
    if (!drv || drv->state == ESP_STATE_WAIT_RESPONSE) return false;

    char cmd[TX_BUFFER_SIZE];
    snprintf(cmd, sizeof(cmd), "AT+SYSGPIOREAD=%d\r\n", pin);

    drv->rx_index = 0;
    drv->response_received = false;
    drv->timer_ms = 0;
    drv->state = ESP_STATE_WAIT_RESPONSE;

    send_string(drv, cmd);
    return true;
}
