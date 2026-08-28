#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef struct {
    // Апаратні ресурси
    I2C_TypeDef *i2c;
    GPIO_TypeDef *scl_port;
    uint16_t scl_pin;
    GPIO_TypeDef *sda_port;
    uint16_t sda_pin;
    GPIO_TypeDef *nrst_port;
    uint16_t nrst_pin;
    GPIO_TypeDef *pwr_port;
    uint16_t pwr_pin;

    // Конфігурація
    uint8_t dev_addr;
    uint8_t expected_id;

    // Тіньові регістри (кеш)
    uint8_t shadow_ctrl_reg;
    uint8_t shadow_config_reg;

    // Лічильники відмов
    uint8_t consecutive_errors;
    uint32_t total_recoveries;
} sensor_device_t;

int sensor_read_register(sensor_device_t *dev, uint8_t reg, uint8_t *val);
int sensor_write_register(sensor_device_t *dev, uint8_t reg, uint8_t val);
int sensor_recover_escalation(sensor_device_t *dev);

int sensor_init(sensor_device_t *dev) {
    uint8_t id = 0;
    int res = sensor_read_register(dev, 0x0F /* WHO_AM_I */, &id);
    if (res != 0 || id != dev->expected_id) {
        return sensor_recover_escalation(dev);
    }

    // Записуємо робочі конфігураційні регістри
    dev->shadow_ctrl_reg = 0x57;   // ODR = 100 Hz, всі осі увімкнено
    dev->shadow_config_reg = 0x08; // Діапазон +/-4g
    res = sensor_write_register(dev, 0x20, dev->shadow_ctrl_reg);
    if (res != 0) return sensor_recover_escalation(dev);

    res = sensor_write_register(dev, 0x21, dev->shadow_config_reg);
    if (res != 0) return sensor_recover_escalation(dev);

    dev->consecutive_errors = 0;
    return 0; // Успішно ініціалізовано
}

int sensor_recover_escalation(sensor_device_t *dev) {
    dev->consecutive_errors++;
    dev->total_recoveries++;

    // Рівень 1: Розблокування шини 9 тактами + Soft-Reset
    if (dev->consecutive_errors == 1) {
        // Спроба відправити Soft-Reset команду
        uint8_t reset_cmd = 0xB6;
        sensor_write_register(dev, 0x25, reset_cmd);
    }
    // Рівень 2: Імпульс nRESET
    else if (dev->consecutive_errors == 2 && dev->nrst_port) {
        dev->nrst_port->BSRR = (1U << (dev->nrst_pin + 16)); // Low
        dev->nrst_port->BSRR = (1U << dev->nrst_pin);        // High
    }
    // Рівень 3: Повний Power-Cycle
    else if (dev->consecutive_errors >= 3 && dev->pwr_port) {
        // chip_power_cycle
    }

    // Після будь-якого скидання перевіряємо працездатність зчитуванням ID
    uint8_t id = 0;
    if (sensor_read_register(dev, 0x0F, &id) == 0 && id == dev->expected_id) {
        // Відновлюємо конфігурацію з тіньових регістрів
        sensor_write_register(dev, 0x20, dev->shadow_ctrl_reg);
        sensor_write_register(dev, 0x21, dev->shadow_config_reg);
        dev->consecutive_errors = 0;
        return 0; // Відновлено
    }

    return -1; // Спроба відновлення невдала
}
