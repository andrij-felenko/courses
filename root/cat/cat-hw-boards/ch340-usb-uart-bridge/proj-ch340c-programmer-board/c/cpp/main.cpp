#include "Uart.hpp"

/**
 * @file main.cpp
 * @brief Точка входу прошивки мовою C++ для перевірки роботи моста CH340 USB-UART.
 */

int main() {
    /* Ініціалізація драйвера UART через RAII-об'єкт */
    Uart uart{9600};

    /* Відправка привітання та інформації про режим роботи */
    uart.send_string("\r\n========================================\r\n");
    uart.send_string(" CH340 USB-UART Bridge Test Firmware (C++)\r\n");
    uart.send_string(" Status: Uart object initialized at 9600 baud\r\n");
    uart.send_string(" Echo loop running...\r\n");
    uart.send_string("========================================\r\n\r\n");

    /* Головний цикл обробки даних */
    while (true) {
        uint8_t data = 0;

        if (uart.receive_byte_nonblocking(data)) {
            /* Повернення отриманого байта назад у порт (ехо) */
            uart.send_byte(data);

            /* Форматування переводу рядка для послідовного термінала */
            if (data == '\r') {
                uart.send_byte('\n');
            }
        }
    }

    return 0;
}
