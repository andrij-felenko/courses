#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Коди помилок драйвера
typedef enum {
    SHT3X_OK = 0,
    SHT3X_ERR_I2C_WRITE,
    SHT3X_ERR_I2C_READ,
    SHT3X_ERR_CRC_TEMP,
    SHT3X_ERR_CRC_HUMI,
    SHT3X_ERR_INVALID_PARAM
} sht3x_status_t;

// Результат вимірювання у фізичних величинах
typedef struct {
    float temperature_c;
    float humidity_rh;
} sht3x_data_t;

// Абстракція платформно-залежних функцій I2C
typedef struct {
    bool (*i2c_write)(uint8_t addr_7bit, const uint8_t *data, size_t len);
    bool (*i2c_read)(uint8_t addr_7bit, uint8_t *data, size_t len);
    void (*delay_ms)(uint32_t ms);
    uint8_t address_7bit;
} sht3x_handle_t;

#define SHT3X_CMD_MEAS_HIGH_REP_NO_STRETCH 0x2400

static uint8_t calculate_crc8_c(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x31) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

sht3x_status_t sht3x_read_measurement(const sht3x_handle_t *dev, sht3x_data_t *result) {
    if (!dev || !result || !dev->i2c_write || !dev->i2c_read || !dev->delay_ms) {
        return SHT3X_ERR_INVALID_PARAM;
    }

    // 1. Відправка 16-бітної команди запуску
    uint8_t cmd_buf[2] = {
        (uint8_t)(SHT3X_CMD_MEAS_HIGH_REP_NO_STRETCH >> 8),
        (uint8_t)(SHT3X_CMD_MEAS_HIGH_REP_NO_STRETCH & 0xFF)
    };
    if (!dev->i2c_write(dev->address_7bit, cmd_buf, 2)) {
        return SHT3X_ERR_I2C_WRITE;
    }

    // 2. Очікування завершення перетворення t_meas
    dev->delay_ms(15);

    // 3. Зчитування 6-байтного кадру
    uint8_t rx_buf[6] = {0};
    if (!dev->i2c_read(dev->address_7bit, rx_buf, 6)) {
        return SHT3X_ERR_I2C_READ;
    }

    // 4. Перевірка контрольної суми температури (байти 0, 1 проти 2)
    if (calculate_crc8_c(&rx_buf[0], 2) != rx_buf[2]) {
        return SHT3X_ERR_CRC_TEMP;
    }

    // 5. Перевірка контрольної суми вологості (байти 3, 4 проти 5)
    if (calculate_crc8_c(&rx_buf[3], 2) != rx_buf[5]) {
        return SHT3X_ERR_CRC_HUMI;
    }

    // 6. Перерахунок сирих відліків у фізичні значення
    uint16_t raw_temp = (uint16_t)((rx_buf[0] << 8) | rx_buf[1]);
    uint16_t raw_humi = (uint16_t)((rx_buf[3] << 8) | rx_buf[4]);

    result->temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
    result->humidity_rh   = 100.0f * ((float)raw_humi / 65535.0f);

    return SHT3X_OK;
}
