#include <stdint.h>
#include <stdbool.h>

#define TCA9548A_BASE_ADDR  0x70
#define SENSOR_I2C_ADDR     0x68

/* Платформозалежні функції I2C драйвера */
extern bool i2c_write_byte(uint8_t dev_addr, uint8_t data);
extern bool i2c_read_bytes(uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint8_t len);

/* Вибір активного каналу комутатора (0..7). Значення >= 8 вимикає всі канали */
bool tca9548a_select_channel(uint8_t mux_addr, uint8_t channel) {
    if (channel > 7) {
        /* Запис 0x00 вимикає всі транзитні ключі */
        return i2c_write_byte(mux_addr, 0x00);
    }
    uint8_t control_mask = (uint8_t)(1U << channel);
    return i2c_write_byte(mux_addr, control_mask);
}

/* Опитування датчика на конкретному каналі комутатора */
bool read_sensor_from_channel(uint8_t mux_addr, uint8_t channel, uint8_t *out_data, uint8_t len) {
    if (!tca9548a_select_channel(mux_addr, channel)) {
        return false;
    }
    /* Датчик доступний за своєю стандартною фіксованою адресою */
    return i2c_read_bytes(SENSOR_I2C_ADDR, 0x00, out_data, len);
}
