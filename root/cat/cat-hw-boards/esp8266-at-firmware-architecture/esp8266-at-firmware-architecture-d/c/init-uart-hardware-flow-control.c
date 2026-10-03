#include "driver/uart.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>

#define UART_PORT_NUM      UART_NUM_0
#define BUF_SIZE           2048
#define PACKET_SIZE        1460

static const char *TAG = "AT_FLOW_OPT";

// Ініціалізація UART з підтримкою апаратного керування потоком RTS/CTS
void init_uart_hardware_flow_control(void) {
    uart_config_t uart_config = {
        .baud_rate = 460800,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_CTS_RTS, // Апаратний контроль RTS/CTS
        .rx_flow_ctrl_thresh = 122,
    };
    
    ESP_ERROR_CHECK(uart_param_config(UART_PORT_NUM, &uart_config));
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT_NUM, 1, 3, 15, 13)); // TX, RX, RTS, CTS
    ESP_ERROR_CHECK(uart_driver_install(UART_PORT_NUM, BUF_SIZE * 2, BUF_SIZE * 2, 0, NULL, 0));
    ESP_LOGI(TAG, "UART0 успішно ініціалізовано з апаратним контролем RTS/CTS.");
}

// Оптимізована відправка пакетів з урахуванням апаратного потоку та таймаутів
bool send_packet_with_flow_control(const uint8_t *data, size_t len) {
    char send_cmd[32];
    snprintf(send_cmd, sizeof(send_cmd), "AT+CIPSEND=0,%d\r\n", (int)len);

    // Відправка команди запрошення на передачу
    uart_write_bytes(UART_PORT_NUM, send_cmd, strlen(send_cmd));
    
    // Очікування готовності модуля (підтвердження символом '>')
    vTaskDelay(pdMS_TO_TICKS(20));

    // Відправка бінарного кадру через UART з урахуванням CTS сигналу
    int bytes_sent = uart_write_bytes(UART_PORT_NUM, (const char *)data, len);
    if (bytes_sent != len) {
        ESP_LOGE(TAG, "Помилка відправки: передано лише %d з %d байт (призупинено по CTS)", bytes_sent, len);
        return false;
    }
    
    return true;
}
