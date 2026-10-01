#include "uart.h"

/**
 * @file main.c
 * @brief Головна програма тестової прошивки модуля ESP-01.
 * 
 * Точка входу в систему: здійснює початкове налаштування послідовного інтерфейсу
 * UART, надсилає стартове повідомлення та у нескінченному циклі передає діагностичні
 * дані на комп'ютер через USB-UART програматор-адаптер.
 */

/**
 * @brief Затримка виконання у мілісекундах (заснована на циклі очікування).
 * 
 * @param ms Кількість мілісекунд для затримки.
 */
static void delay_ms(uint32_t ms) {
    volatile uint32_t count;
    for (uint32_t i = 0; i < ms; i++) {
        // Приблизна кількість ітерацій NOP для 1 мс при частоті ядра 80 МГц
        for (count = 0; count < 8000U; count++) {
            __asm__ volatile("nop");
        }
    }
}

int main(void) {
    // Ініціалізація UART0 на швидкості 115200 бод (стандартний режим зв'язку з ПК)
    uart_init(UART_DEFAULT_BAUD_RATE);

    // Відправка стартового баннера для перевірки успішності прошивання та зв'язку
    uart_send_string("\n==================================================\n");
    uart_send_string("  ESP-01 Programmer Adapter Test Firmware (C)\n");
    uart_send_string("  Target Chip : ESP8266EX / ESP-01 Module\n");
    uart_send_string("  Baud Rate   : 115200 8N1\n");
    uart_send_string("==================================================\n\n");

    uint32_t cycle_counter = 0U;
    uint32_t uptime_ms = 0U;
    const uint32_t loop_interval_ms = 1000U;

    // Головний цикл роботи прошивки
    while (1) {
        cycle_counter++;
        uptime_ms += loop_interval_ms;

        // Передача діагностичного статусу через програматор-адаптер на ПК
        uart_send_diagnostic_status(cycle_counter, uptime_ms);

        // Пауза 1 секунда між відправками даних
        delay_ms(loop_interval_ms);
    }

    return 0;
}
