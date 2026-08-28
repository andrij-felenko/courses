// Функція відновлення шини I2C після зависання веденого пристрою (C)
#include <stdint.h>
#include <stdbool.h>

extern void gpio_set_mode_output_od(uint8_t pin);
extern void gpio_set_level(uint8_t pin, uint8_t level);
extern uint8_t gpio_get_level(uint8_t pin);
extern void delay_us(uint32_t us);
extern void i2c_hardware_init(void);

#define PIN_SCL 22
#define PIN_SDA 21

bool i2c_bus_recover_lockup(void) {
    gpio_set_mode_output_od(PIN_SCL);
    gpio_set_mode_output_od(PIN_SDA);

    gpio_set_level(PIN_SDA, 1);
    gpio_set_level(PIN_SCL, 1);
    delay_us(5);

    // Якщо SDA вільна, відновлення не потрібне
    if (gpio_get_level(PIN_SDA) == 1) {
        i2c_hardware_init();
        return true;
    }

    // Тактування 9 імпульсів на SCL для виштовхування застряглого біта
    for (int i = 0; i < 9; ++i) {
        gpio_set_level(PIN_SCL, 0);
        delay_us(5);
        gpio_set_level(PIN_SCL, 1);
        delay_us(5);

        if (gpio_get_level(PIN_SDA) == 1) {
            break; // Ведений відпустив шину
        }
    }

    // Генерація ручної STOP-умови
    gpio_set_level(PIN_SDA, 0);
    delay_us(5);
    gpio_set_level(PIN_SCL, 1);
    delay_us(5);
    gpio_set_level(PIN_SDA, 1);
    delay_us(5);

    bool success = (gpio_get_level(PIN_SDA) == 1);
    i2c_hardware_init();
    return success;
}
