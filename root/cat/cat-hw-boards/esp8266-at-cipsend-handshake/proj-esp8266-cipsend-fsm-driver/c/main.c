#include "esp_cipsend_fsm.h"
#include "uart_hal.h"
#include <stdio.h>

int main(void) {
    // 1. Ініціалізація апаратного HAL
    esp_uart_hal_t hal = {
        .uart_write = platform_uart_write,
        .uart_read_char = platform_uart_read_char,
        .get_tick_ms = platform_get_tick_ms
    };

    // 2. Ініціалізація контексту FSM
    esp_cipsend_t cipsend;
    esp_cipsend_init(&cipsend, &hal);

    const uint8_t payload[] = "Hello ESP8266!";
    bool transfer_started = false;

    // Головний неблокуючий цикл мікроконтролера
    while (1) {
        // Умовно, коли треба відправити дані:
        if (!transfer_started) {
            if (esp_cipsend_start(&cipsend, payload, sizeof(payload)-1, 5000)) {
                transfer_started = true;
                printf("Transfer started...\n");
            }
        }

        // Обслуговування автомата в фоні
        esp_cipsend_tick(&cipsend);

        // Перевірка стану
        esp_cipsend_state_t state = esp_cipsend_get_state(&cipsend);
        if (transfer_started) {
            if (state == CIPSEND_STATE_IDLE) {
                printf("Transfer completed successfully!\n");
                transfer_started = false;
                break; 
            } else if (state == CIPSEND_STATE_ERROR) {
                printf("Transfer failed!\n");
                transfer_started = false;
                break;
            }
        }
    }

    return 0;
}
