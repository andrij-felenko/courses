#include <string.h>
#include "esp_timer.h"

// Ті самі три кроки. Замість String — буфер виклику: у прошивці без
// динамічних рядків видно, скільки пам'яті коштує відповідь.
bool send_at(const char *cmd, char *resp, size_t cap, uint32_t timeout_ms) {
    // 1) очистити «хвіст» попередньої відповіді з приймального буфера драйвера
    uart_flush_input(BT_UART);

    // 2) надіслати команду + ОБОВ'ЯЗКОВІ \r\n
    uart_write_bytes(BT_UART, cmd, strlen(cmd));
    uart_write_bytes(BT_UART, "\r\n", 2);

    // 3) збирати відповідь, доки не побачимо кінець рядка або не вийде час
    size_t n = 0;
    int64_t start = esp_timer_get_time();          // мікросекунди від старту
    while ((esp_timer_get_time() - start) / 1000 < timeout_ms) {
        uint8_t c;
        if (uart_read_bytes(BT_UART, &c, 1, pdMS_TO_TICKS(10)) != 1) continue;
        if (n < cap - 1) resp[n++] = (char)c;
        if (c == '\n') {                           // рядок готовий
            resp[n] = '\0';
            return strstr(resp, "OK") != NULL;     // є "OK" → успіх
        }
    }
    resp[n] = '\0';
    return false;   // час вийшов, повного рядка так і не прийшло
}
