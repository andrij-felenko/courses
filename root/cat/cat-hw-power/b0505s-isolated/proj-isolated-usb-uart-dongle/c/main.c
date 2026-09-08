#include <stdint.h>
#include <stdbool.h>
#include "uart.h"

#define SYSTEM_CLOCK_HZ  16000000UL
#define TARGET_BAUDRATE  115200UL

/**
 * @brief Головна функція програми відлуння через ізольований USB-UART канал.
 * Перевіряє відсутність спотворень фронтів сигналів на високій швидкості 115200 бод
 * при роботі через цифрову розв'язку та ізольоване живлення B0505S-1W.
 */
int main(void) {
    /* Налаштування апаратного UART-контролера */
    uart_init(TARGET_BAUDRATE, SYSTEM_CLOCK_HZ);
    
    uint8_t received_byte = 0;
    
    /* Головний нескінченний цикл відлуння (loopback echo) */
    while (1) {
        /* Неблокуючий прийом вхідного байта від комп'ютера */
        if (uart_read_byte(&received_byte)) {
            /* Очікуємо готовності передавача і негайно повертаємо байт назад хосту */
            while (!uart_write_byte(received_byte)) {
                /* Очікування вивільнення апаратного буфера */
            }
        }
    }
    
    return 0;
}
