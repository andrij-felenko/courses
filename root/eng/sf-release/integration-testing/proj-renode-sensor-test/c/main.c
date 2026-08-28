#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SENSOR_I2C_ADDR      (0x44 << 1)
#define SENSOR_CMD_MEASURE   0x2C06
#define CRC8_POLYNOMIAL      0x31
#define CRC8_INIT            0xFF
#define MAX_RETRY_COUNT      3
#define I2C_TIMEOUT_CYCLES   50000

typedef enum {
    SENSOR_OK = 0,
    SENSOR_ERR_I2C = 1,
    SENSOR_ERR_CRC = 2,
    SENSOR_ERR_TIMEOUT = 3
} sensor_status_t;

/* Обчислення контрольної суми CRC-8-Dallas/Maxim */
static uint8_t crc8_calculate(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

/* Прототипи апаратного рівня */
extern bool hal_i2c_write(uint8_t dev_addr, const uint8_t *buf, uint16_t len, uint32_t timeout);
extern bool hal_i2c_read(uint8_t dev_addr, uint8_t *buf, uint16_t len, uint32_t timeout);
extern void hal_i2c_bus_recover_9_clocks(void);

sensor_status_t sensor_read_temperature(float *temperature_c) {
    uint8_t cmd[2] = { (uint8_t)(SENSOR_CMD_MEASURE >> 8), (uint8_t)(SENSOR_CMD_MEASURE & 0xFF) };
    uint8_t rx_buf[3] = { 0 };

    for (int attempt = 0; attempt < MAX_RETRY_COUNT; ++attempt) {
        /* Надсилання команди запуску вимірювання */
        if (!hal_i2c_write(SENSOR_I2C_ADDR, cmd, sizeof(cmd), I2C_TIMEOUT_CYCLES)) {
            /* Збій на шині — спроба скинути апаратний замок лінії SDA */
            hal_i2c_bus_recover_9_clocks();
            continue;
        }

        /* Зчитування 2 байтів температури + 1 байта CRC */
        if (!hal_i2c_read(SENSOR_I2C_ADDR, rx_buf, sizeof(rx_buf), I2C_TIMEOUT_CYCLES)) {
            hal_i2c_bus_recover_9_clocks();
            continue;
        }

        /* Валідація контрольної суми */
        uint8_t expected_crc = crc8_calculate(rx_buf, 2);
        if (expected_crc != rx_buf[2]) {
            /* Помилка CRC: повторити спробу */
            continue;
        }

        uint16_t raw_temp = (uint16_t)((rx_buf[0] << 8) | rx_buf[1]);
        *temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
        return SENSOR_OK;
    }

    return SENSOR_ERR_CRC;
}
