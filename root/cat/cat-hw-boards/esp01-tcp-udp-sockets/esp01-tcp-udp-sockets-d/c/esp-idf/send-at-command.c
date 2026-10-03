#include <stdio.h>
#include <string.h>
#include "driver/uart.h"
#include "esp_log.h"

#define UART_PORT_NUM UART_NUM_1
static const char *TAG = "AT_SOCKET_INIT";

// Відправка AT-команди через UART та очікування відповіді
esp_err_t send_at_command(const char *cmd, const char *expected_resp) {
    uart_write_bytes(UART_PORT_NUM, cmd, strlen(cmd));
    ESP_LOGI(TAG, "Надіслано команду: %s", cmd);
    
    uint8_t data[256];
    int len = uart_read_bytes(UART_PORT_NUM, data, sizeof(data) - 1, pdMS_TO_TICKS(2000));
    if (len > 0) {
        data[len] = '\0';
        if (strstr((char*)data, expected_resp) != NULL) {
            ESP_LOGI(TAG, "Успішно отримано відповідь: %s", expected_resp);
            return ESP_OK;
        }
    }
    ESP_LOGE(TAG, "Помилка виконання команди: %s", cmd);
    return ESP_FAIL;
}

// Ініціалізація множинного режиму та TCP-сервера
void init_esp01_tcp_server(void) {
    // Встановлення множинного режиму з'єднань (CIPMUX=1)
    if (send_at_command("AT+CIPMUX=1\r\n", "OK") == ESP_OK) {
        // Запуск TCP-сервера на порту 8080
        send_at_command("AT+CIPSERVER=1,8080\r\n", "OK");
    }
}
