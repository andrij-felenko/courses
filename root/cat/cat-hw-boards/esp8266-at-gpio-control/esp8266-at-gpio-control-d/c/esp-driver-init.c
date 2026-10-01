#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    DRIVER_STATE_IDLE,
    DRIVER_STATE_WAIT_RESPONSE,
    DRIVER_STATE_TIMEOUT_RECOVERY
} driver_state_t;

typedef struct {
    driver_state_t state;
    uint32_t timer_ms;
    uint32_t timeout_limit_ms;
    bool response_ok;
    bool response_error;
} esp_driver_t;

void esp_driver_init(esp_driver_t *drv) {
    drv->state = DRIVER_STATE_IDLE;
    drv->timer_ms = 0;
    drv->timeout_limit_ms = 500;
    drv->response_ok = false;
    drv->response_error = false;
}

void esp_driver_parse_line(esp_driver_t *drv, const char *line) {
    if (strncmp(line, "+GPIO_INT:", 10) == 0) {
        // Обробка асинхронного сповіщення URC без зміни стану автомата
        int pin, level;
        if (sscanf(line, "+GPIO_INT:%d,%d", &pin, &level) == 2) {
            // Виклик обробника переривання GPIO
        }
        return;
    }

    if (strcmp(line, "OK") == 0) {
        drv->response_ok = true;
    } else if (strcmp(line, "ERROR") == 0) {
        drv->response_error = true;
    }
}

void esp_driver_process(esp_driver_t *drv, uint32_t delta_ms) {
    if (drv->state == DRIVER_STATE_WAIT_RESPONSE) {
        drv->timer_ms += delta_ms;
        if (drv->response_ok) {
            drv->state = DRIVER_STATE_IDLE;
        } else if (drv->response_error || drv->timer_ms >= drv->timeout_limit_ms) {
            drv->state = DRIVER_STATE_TIMEOUT_RECOVERY;
        }
    }
}
