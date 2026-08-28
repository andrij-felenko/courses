#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Статуси результату відновлення шини I2C
 */
typedef enum {
    I2C_RECOVER_OK = 0,               /**< Шина вільна і готова до роботи */
    I2C_RECOVER_SCL_STUCK_LOW,        /**< Лінія SCL закорочена на нуль (SCL Lockup) */
    I2C_RECOVER_SDA_STUCK_LOW,        /**< Лінія SDA не відновилася після 9 тактів */
    I2C_RECOVER_HARDWARE_RESET_DONE,  /**< Успішно відновлено через Power Cycle */
    I2C_RECOVER_FATAL_ERROR           /**< Повна відмова шини навіть після скидання живлення */
} i2c_recovery_status_t;

/**
 * @brief Апаратна абстракція керування виводами GPIO (HAL)
 */
typedef struct {
    void (*set_scl_mode_open_drain)(void);
    void (*set_sda_mode_open_drain)(void);
    void (*set_scl_mode_i2c)(void);
    void (*set_sda_mode_i2c)(void);
    void (*write_scl)(bool level);
    void (*write_sda)(bool level);
    bool (*read_scl)(void);
    bool (*read_sda)(void);
    void (*set_power_switch)(bool enable); /**< Керування High-Side ключем */
    void (*delay_us)(uint32_t us);
    void (*delay_ms)(uint32_t ms);
} i2c_bus_hal_t;

/**
 * @brief Конфігураційні часові параметри відновлення (Standard-mode 100 кГц)
 */
#define I2C_RECOVERY_CLOCK_DELAY_US    5
#define I2C_RECOVERY_MAX_PULSES        9
#define I2C_POWER_CYCLE_OFF_MS        50
#define I2C_POWER_CYCLE_SETTLE_MS     20

/**
 * @brief Програмний алгоритм 9-тактового відновлення шини (Bus Clear)
 */
static i2c_recovery_status_t i2c_bus_clear_9clocks(const i2c_bus_hal_t *hal) {
    // Крок 1: Переведення пінів у режим GPIO Open-Drain
    hal->set_scl_mode_open_drain();
    hal->set_sda_mode_open_drain();
    hal->write_scl(true);
    hal->write_sda(true);
    hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);

    // Крок 2: Перевірка стану SCL
    if (!hal->read_scl()) {
        return I2C_RECOVER_SCL_STUCK_LOW;
    }

    // Якщо SDA вже висока — шина чиста, генеруємо тільки STOP
    bool sda_released = hal->read_sda();

    // Крок 3: Тактування SCL (до 9 імпульсів)
    for (int i = 0; i < I2C_RECOVERY_MAX_PULSES && !sda_released; ++i) {
        // Формуємо спадний фронт SCL
        hal->write_scl(false);
        hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);

        // Формуємо наростаючий фронт SCL
        hal->write_scl(true);
        hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);

        // Перевіряємо стан SCL на випадок Clock Stretching від слейва
        uint32_t stretch_timeout = 100;
        while (!hal->read_scl() && stretch_timeout > 0) {
            hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);
            stretch_timeout--;
        }
        if (stretch_timeout == 0) {
            return I2C_RECOVER_SCL_STUCK_LOW;
        }

        // Опитуємо SDA при високому SCL
        if (hal->read_sda()) {
            sda_released = true;
            break;
        }
    }

    // Якщо ведений так і не відпустив SDA за 9 тактів
    if (!hal->read_sda()) {
        return I2C_RECOVER_SDA_STUCK_LOW;
    }

    // Крок 4: Формування коректної умови STOP (SDA: LOW -> HIGH при SCL = HIGH)
    hal->write_scl(false);
    hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);
    hal->write_sda(false);
    hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);

    hal->write_scl(true);
    hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);
    hal->write_sda(true);
    hal->delay_us(I2C_RECOVERY_CLOCK_DELAY_US);

    // Крок 5: Фінальна верифікація спокою на шині
    if (hal->read_scl() && hal->read_sda()) {
        return I2C_RECOVER_OK;
    }

    return I2C_RECOVER_SDA_STUCK_LOW;
}

/**
 * @brief Повний відмовостійкий цикл відновлення (9-Clock + Power Cycle Fallback)
 */
i2c_recovery_status_t i2c_bus_recover_full(const i2c_bus_hal_t *hal) {
    if (hal == 0) {
        return I2C_RECOVER_FATAL_ERROR;
    }

    // 1-ша лінія захисту: програмне тактування (швидко, без знеструмлення)
    i2c_recovery_status_t status = i2c_bus_clear_9clocks(hal);

    if (status == I2C_RECOVER_OK) {
        hal->set_scl_mode_i2c();
        hal->set_sda_mode_i2c();
        return I2C_RECOVER_OK;
    }

    // 2-га лінія захисту: апаратний Power Cycle (якщо доступний силовий ключ)
    if (hal->set_power_switch != 0) {
        // Правило 2: Заземлити піни GPIO перед вимкненням VCC
        hal->set_scl_mode_open_drain();
        hal->set_sda_mode_open_drain();
        hal->write_scl(false);
        hal->write_sda(false);

        // Знеструмити датчики через High-Side ключ
        hal->set_power_switch(false);
        hal->delay_ms(I2C_POWER_CYCLE_OFF_MS);

        // Відновити живлення
        hal->set_power_switch(true);
        hal->delay_ms(I2C_POWER_CYCLE_SETTLE_MS);

        // Відпустити лінії та виконати повторне тактування
        hal->write_scl(true);
        hal->write_sda(true);

        status = i2c_bus_clear_9clocks(hal);
        hal->set_scl_mode_i2c();
        hal->set_sda_mode_i2c();

        if (status == I2C_RECOVER_OK) {
            return I2C_RECOVER_HARDWARE_RESET_DONE;
        }
    }

    // Повертаємо виводи у режим I2C навіть у разі помилки
    hal->set_scl_mode_i2c();
    hal->set_sda_mode_i2c();
    return status;
}
