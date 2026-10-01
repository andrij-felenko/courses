#include <stdio.h>
#include <string.h>
#include "driver/uart.h"
#include "esp_log.h"

static const char *TAG = "AT_SOCKET";

void send_tcp_data(uint8_t link_id, const char *payload) {
    char cmd[32];
    size_t len = strlen(payload);
    snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%u,%zu\r\n", link_id, len);
    
    uart_write_bytes(UART_NUM_1, cmd, strlen(cmd));
    // Очікування запрошення '>' перед відправкою буфера
    vTaskDelay(pdMS_TO_TICKS(50));
    uart_write_bytes(UART_NUM_1, payload, len);
}
