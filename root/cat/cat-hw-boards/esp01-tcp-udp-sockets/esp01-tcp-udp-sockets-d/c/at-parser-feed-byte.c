#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    AT_STATE_IDLE,
    AT_STATE_WAIT_PROMPT,
    AT_STATE_STREAMING,
    AT_STATE_WAIT_OK
} at_parser_state_t;

typedef struct {
    at_parser_state_t state;
    uint32_t last_byte_time_ms;
    bool prompt_received;
} at_driver_t;

static at_driver_t g_driver = { .state = AT_STATE_IDLE, .last_byte_time_ms = 0, .prompt_received = false };

// Обробка кожного байта, отриманого з UART переривання
void at_parser_feed_byte(uint8_t byte, uint32_t current_time_ms) {
    g_driver.last_byte_time_ms = current_time_ms;

    switch (g_driver.state) {
        case AT_STATE_WAIT_PROMPT:
            if (byte == '>') {
                g_driver.prompt_received = true;
                g_driver.state = AT_STATE_STREAMING;
            }
            break;
        case AT_STATE_STREAMING:
            // Байти відправляються безпосередньо у сокет
            break;
        case AT_STATE_IDLE:
        default:
            break;
    }
}

// Вихід з наскрізного режиму із дотриманням захисного інтервалу guard time (1000 мс)
bool at_passthrough_exit(void (*uart_send_str)(const char*), uint32_t current_time_ms) {
    if (current_time_ms - g_driver.last_byte_time_ms < 1000) {
        return false; // Захисний інтервал до +++ ще не витримано
    }
    uart_send_str("+++");
    g_driver.state = AT_STATE_WAIT_OK;
    return true;
}
