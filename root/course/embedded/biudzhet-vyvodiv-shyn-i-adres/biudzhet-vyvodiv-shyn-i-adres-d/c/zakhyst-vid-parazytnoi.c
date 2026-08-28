#include <stdint.h>

/* Призначення керуючих виводів GPIO для дешифратора 74HC138 */
extern void gpio_set_pin(uint8_t pin, uint8_t level);

#define PIN_CS_A0   12
#define PIN_CS_A1   13
#define PIN_CS_A2   14
#define PIN_CS_EN   15  /* Підключено до інверсного входу E2 або E3 */

/* Вибір цільового SPI-пристрою (0..7) з апаратним захистом від глічів */
void spi_cs_select(uint8_t device_id) {
    /* 1. Блокуємо всі виходи дешифратора */
    gpio_set_pin(PIN_CS_EN, 1);

    /* 2. Виставляємо двійкову адресу цільового пристрою */
    gpio_set_pin(PIN_CS_A0, (device_id >> 0) & 0x01);
    gpio_set_pin(PIN_CS_A1, (device_id >> 1) & 0x01);
    gpio_set_pin(PIN_CS_A2, (device_id >> 2) & 0x01);

    /* 3. Дозволяємо вихід дешифратора — відповідний Yn падає в 0 */
    gpio_set_pin(PIN_CS_EN, 0);
}

/* Деактивація всіх ліній Chip Select */
void spi_cs_deselect(void) {
    gpio_set_pin(PIN_CS_EN, 1);
}
