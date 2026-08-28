#include <stdint.h>
#include <stdbool.h>

// Статуси виконання процедури відновлення шини
typedef enum {
    I2C_RECOVER_OK = 0,
    I2C_RECOVER_ALREADY_FREE,
    I2C_RECOVER_FAILED_SDA_STUCK,
    I2C_RECOVER_FAILED_SCL_STUCK
} i2c_recover_status_t;

// Прототипи низькорівневих платформозалежних функцій GPIO
// (у реальному проєкті реалізуються через HAL або прямий доступ до регістрів)
extern void platform_delay_us(uint32_t us);
extern void gpio_set_mode_open_drain(uint32_t pin);
extern void gpio_set_mode_alternate_i2c(uint32_t pin);
extern void gpio_write_pin(uint32_t pin, bool level);
extern bool gpio_read_pin(uint32_t pin);

#define I2C_SCL_PIN  6
#define I2C_SDA_PIN  7
#define I2C_CLOCK_HALF_PERIOD_US 5

/**
 * @brief Виконує скидання завислої шини I2C методом 9 тактів SCL
 * @return i2c_recover_status_t Результат процедури
 */
i2c_recover_status_t i2c_bus_recover_9clocks(void)
{
    // Крок 1 і 2: Переналаштування виводів у режим GPIO Open-Drain
    gpio_set_mode_open_drain(I2C_SCL_PIN);
    gpio_set_mode_open_drain(I2C_SDA_PIN);
    
    // Відпускаємо лінії (виставляємо 1, щоб резистори підтягнули шину до VCC)
    gpio_write_pin(I2C_SCL_PIN, true);
    gpio_write_pin(I2C_SDA_PIN, true);
    platform_delay_us(10);

    // Крок 3: Перевірка лінії SCL
    if (!gpio_read_pin(I2C_SCL_PIN)) {
        // Лінія SCL замкнена на GND або ведений виконує Clock Stretching
        return I2C_RECOVER_FAILED_SCL_STUCK;
    }

    // Крок 4: Перевірка лінії SDA
    if (gpio_read_pin(I2C_SDA_PIN)) {
        // Лінія вже у високому стані, відновлення не потрібне
        gpio_set_mode_alternate_i2c(I2C_SCL_PIN);
        gpio_set_mode_alternate_i2c(I2C_SDA_PIN);
        return I2C_RECOVER_ALREADY_FREE;
    }

    // Крок 5: Генерація до 9 тактових імпульсів на лінії SCL
    bool sda_freed = false;
    for (uint8_t i = 0; i < 9; i++) {
        // Опускаємо SCL
        gpio_write_pin(I2C_SCL_PIN, false);
        platform_delay_us(I2C_CLOCK_HALF_PERIOD_US);

        // Піднімаємо SCL
        gpio_write_pin(I2C_SCL_PIN, true);
        platform_delay_us(I2C_CLOCK_HALF_PERIOD_US);

        // Перевіряємо, чи ведений відпустив SDA
        if (gpio_read_pin(I2C_SDA_PIN)) {
            sda_freed = true;
            break;
        }
    }

    // Якщо після 9 тактів SDA все ще на землі — апаратний збій
    if (!sda_freed) {
        return I2C_RECOVER_FAILED_SDA_STUCK;
    }

    // Крок 7: Формування коректної умови STOP (перепад SDA 0 -> 1 при SCL = 1)
    // 1. Опускаємо SCL
    gpio_write_pin(I2C_SCL_PIN, false);
    platform_delay_us(I2C_CLOCK_HALF_PERIOD_US);
    
    // 2. Примусово садимо SDA в нуль
    gpio_write_pin(I2C_SDA_PIN, false);
    platform_delay_us(I2C_CLOCK_HALF_PERIOD_US);

    // 3. Піднімаємо SCL
    gpio_write_pin(I2C_SCL_PIN, true);
    platform_delay_us(I2C_CLOCK_HALF_PERIOD_US);

    // 4. Піднімаємо SDA при високому SCL -> генерується валідний STOP
    gpio_write_pin(I2C_SDA_PIN, true);
    platform_delay_us(10);

    // Крок 8: Повернення виводів периферійному модулю I2C
    gpio_set_mode_alternate_i2c(I2C_SCL_PIN);
    gpio_set_mode_alternate_i2c(I2C_SDA_PIN);

    return I2C_RECOVER_OK;
}
