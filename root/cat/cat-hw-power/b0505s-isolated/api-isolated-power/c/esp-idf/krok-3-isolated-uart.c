/* ============================================================================
   krok-3-isolated-uart.c — ESP-IDF: безпечний ізольований UART
   ========================================================================== */

#include <stdio.h>
#include <string.h>
#include "driver/uart.h"
#include "esp_log.h"

static const char *TAG = "ISO_UART";

#define ISO_UART_PORT        UART_NUM_1
#define PIN_TXD              GPIO_NUM_17
#define PIN_RXD              GPIO_NUM_16

extern bool is_isolated_power_healthy(void);

esp_err_t isolated_uart_write(const uint8_t *data, size_t len) {
    // 1. Перевірка наявності ізольованого живлення перед відправкою
    if (!is_isolated_power_healthy()) {
        ESP_LOGE(TAG, "Помилка передачі: вторинний домен B0505S знеструмлений!");
        return ESP_ERR_INVALID_STATE;
    }

    // 2. Відправка даних через цифровий ізолятор (ADuM1201)
    int bytes_sent = uart_write_bytes(ISO_UART_PORT, (const char*)data, len);
    if (bytes_sent != len) {
        return ESP_FAIL;
    }

    return ESP_OK;
}
