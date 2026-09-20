#include <stdint.h>
#include <stdbool.h>

// Функція зчитування 8-бітного конфігураційного байта через зсувний регістр 74HC165
uint8_t shift_register_read_byte(void) {
    uint8_t raw_data = 0;

    // Фіксація паралельних даних у внутрішньому масиві 74HC165 (імпульс PL LOW)
    gpio_set_pin_low(PIN_PL);
    delay_us(1);
    gpio_set_pin_high(PIN_PL);

    // Зчитування 8 бітів послідовно через лінію Q7 та CLK
    for (uint8_t i = 0; i < 8; ++i) {
        raw_data <<= 1;
        if (gpio_read_pin(PIN_Q7)) {
            raw_data |= 0x01;
        }
        // Формування тактового імпульсу CLK (наростаючий фронт)
        gpio_set_pin_high(PIN_CLK);
        delay_us(1);
        gpio_set_pin_low(PIN_CLK);
    }

    // Інвертування інверсної Pull-Up логіки
    return (uint8_t)(~raw_data);
}
