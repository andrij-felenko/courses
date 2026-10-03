#include <stdio.h>
#include <string.h>
#include "driver/uart.h"

// Формування та надсилання кадру AT-команди через UART у C
esp_err_t send_at_command(uart_port_t uart_num, const char *cmd) {
    char frame_buffer[128];
    // Гарантоване долучення термінатора CRLF (\r\n) до командного рядка
    int len = snprintf(frame_buffer, sizeof(frame_buffer), "%s\r\n", cmd);
    
    if (len < 0 || len >= sizeof(frame_buffer)) {
        return ESP_ERR_INVALID_ARG; // Запобігання переповненню буфера
    }

    // Очищення вихідного буфера та передача кадру в послідовний порт
    uart_flush_input(uart_num);
    int bytes_sent = uart_write_bytes(uart_num, frame_buffer, len);
    
    return (bytes_sent == len) ? ESP_OK : ESP_FAIL;
}
