#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef enum {
    AT_STATE_IDLE,
    AT_STATE_WAIT_RESPONSE
} at_parser_state_t;

bool parse_at_gpio_response(const char *rx_buffer, int *gpio_val) {
    // Пошук маркерного рядка відповіді "+SYSGPIOREAD:"
    const char *match = strstr(rx_buffer, "+SYSGPIOREAD:");
    if (match != NULL) {
        int pin = 0, val = 0;
        if (sscanf(match, "+SYSGPIOREAD:%d,%d", &pin, &val) == 2) {
            *gpio_val = val;
            return true;
        }
    }
    return false;
}
