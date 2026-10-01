#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef enum {
    AT_STATUS_OK,
    AT_STATUS_ERROR,
    AT_STATUS_TIMEOUT
} at_status_t;

// Перевірка відповіді ESP8266 з урахуванням таймауту
at_status_t esp8266_send_cmd(const char *cmd, uint32_t timeout_ms) {
    uart_send_string(cmd);
    uint32_t start_tick = get_system_ticks();
    char rx_buf[64] = {0};
    uint8_t idx = 0;

    while ((get_system_ticks() - start_tick) < timeout_ms) {
        if (uart_rx_available()) {
            char c = uart_read_byte();
            if (idx < sizeof(rx_buf) - 1) {
                rx_buf[idx++] = c;
                rx_buf[idx] = '\0';
            }
            if (strstr(rx_buf, "OK\r\n") != NULL) {
                return AT_STATUS_OK;
            }
            if (strstr(rx_buf, "ERROR\r\n") != NULL) {
                return AT_STATUS_ERROR;
            }
        }
    }
    return AT_STATUS_TIMEOUT;
}
