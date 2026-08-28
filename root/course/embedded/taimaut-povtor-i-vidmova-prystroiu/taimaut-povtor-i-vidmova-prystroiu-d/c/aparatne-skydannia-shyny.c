#include <stdint.h>
#include <stdbool.h>

/* Абстракція платформних викликів керування ніжками GPIO */
extern void gpio_set_mode_gpio_opendrain(void);
extern void gpio_set_mode_i2c_alternate(void);
extern void gpio_set_scl(bool level);
extern bool gpio_read_sda(void);
extern void platform_delay_us(uint32_t us);

/* Процедура апаратного розблокування завислої шини I2C */
bool i2c_hardware_bus_recover(void) {
    /* 1. Переводимо лінії в режим прямого керування GPIO Open-Drain */
    gpio_set_mode_gpio_opendrain();
    platform_delay_us(10);

    /* 2. Якщо SDA вже висока — шина не затиснута веденим */
    if (gpio_read_sda()) {
        gpio_set_mode_i2c_alternate();
        return true;
    }

    /* 3. Генеруємо до 9 тактових імпульсів на SCL для виштовхування біта */
    bool recovered = false;
    for (uint8_t i = 0; i < 9; i++) {
        gpio_set_scl(false);
        platform_delay_us(5);
        gpio_set_scl(true);
        platform_delay_us(5);

        if (gpio_read_sda()) {
            recovered = true;
            break;
        }
    }

    /* 4. Формуємо примусову умову STOP для скидання автоматів ведених чипів */
    gpio_set_scl(false);
    platform_delay_us(5);
    /* SDA примусово притягуємо до нуля */
    /* SCL піднімаємо до 1 */
    gpio_set_scl(true);
    platform_delay_us(5);
    /* Відпускаємо SDA у високий рівень при високому SCL -> умова STOP */
    platform_delay_us(5);

    /* 5. Повертаємо ніжки під контроль апаратного модуля I2C */
    gpio_set_mode_i2c_alternate();
    return recovered;
}
