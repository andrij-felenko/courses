#include "uart.h"

/**
 * @file main.c
 * @brief Головна програма для тестування зв'язку мікроконтролера з ПК через міст CH340.
 */

int main(void) {
    /* Ініціалізація UART на швидкості 9600 бод (стандарт для CH340) */
    uart_init(9600);

    /* Надсилання початкового вітального повідомлення на ПК */
    uart_send_string("\r\n========================================\r\n");
    uart_send_string(" CH340 USB-UART Bridge Test Firmware (C)\r\n");
    uart_send_string(" Status: UART initialized at 9600 baud\r\n");
    uart_send_string(" Interactive echo mode started.\r\n");
    uart_send_string("========================================\r\n\r\n");

    /* Головний цикл роботи (ехо-режим) */
    while (1) {
        uint8_t received_byte = 0;

        /* Перевірка наявності вхідних даних від мікросхеми CH340 */
        if (uart_receive_byte_nonblocking(&received_byte)) {
            /* Відправлення отриманого байта назад на ПК (ехо) */
            uart_send_byte(received_byte);

            /* Автоматичний додаток переводу рядка для зручності відображення у терміналі */
            if (received_byte == '\r') {
                uart_send_byte('\n');
            }
        }
    }

    return 0;
}
