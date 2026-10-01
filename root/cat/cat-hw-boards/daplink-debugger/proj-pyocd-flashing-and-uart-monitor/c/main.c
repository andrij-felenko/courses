#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "uart.h"

// Програмна затримка в мілісекундах для демонстрації періодичної роботи
static void delay_ms(uint32_t ms) {
    for (uint32_t i = 0; i < ms; i++) {
        for (volatile uint32_t count = 0; count < 8000U; count++) {
            __asm__("nop");
        }
    }
}

int main(void) {
    // Ініціалізація модуля UART зі швидкістю 115200 бод (стандарт для VCP WeAct Mini Debugger)
    uart_init(115200);

    // Вивід початкового банера в термінал дебагера
    uart_send_string("\r\n============================================\r\n");
    uart_send_string("   WeAct Mini Debugger (DAPLink / ST-Link)  \r\n");
    uart_send_string("   ARM Cortex-M UART VCP Test Firmware (C)  \r\n");
    uart_send_string("============================================\r\n\r\n");

    uint32_t packet_counter = 0;
    char buffer[128];

    while (1) {
        packet_counter++;

        // Форматування інформаційного рядка з індикатором активності прошивки
        int len = snprintf(buffer, sizeof(buffer),
                           "[DAPLink VCP] Пакет #%lu | Стан: Норма | System Alive\r\n",
                           (unsigned long)packet_counter);

        if (len > 0) {
            uart_send_string(buffer);
        }

        // Перевірка наявності вхідних символів від послідовного порту дебагера
        char rx_char;
        if (uart_receive_char(&rx_char)) {
            uart_send_string(" -> Отримано команду з термінала: '");
            uart_send_char(rx_char);
            uart_send_string("'\r\n");
        }

        // Пауза 1 секунда між циклами
        delay_ms(1000);
    }

    return 0;
}
