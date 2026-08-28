#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// I2C адреса SCD30
#define SCD30_I2C_ADDR                     0x61

// Команди сенсора
#define SCD30_CMD_START_CONTINUOUS         0x0010
#define SCD30_CMD_STOP_CONTINUOUS          0x0104
#define SCD30_CMD_SET_MEASUREMENT_INTERVAL 0x4600
#define SCD30_CMD_GET_DATA_READY           0x0202
#define SCD30_CMD_READ_MEASUREMENT         0x0300
#define SCD30_CMD_SET_AUTO_CALIBRATION     0x5306
#define SCD30_CMD_SET_FORCED_RECALIBRATION 0x5204
#define SCD30_CMD_SET_TEMP_OFFSET          0x5403
#define SCD30_CMD_SOFT_RESET               0xD304

typedef struct {
    float co2_ppm;
    float temperature_c;
    float relative_humidity_pct;
} scd30_data_t;

// Апаратний інтерфейс I2C (впроваджується користувачем)
typedef struct {
    int (*i2c_write)(uint8_t addr, const uint8_t *data, size_t len);
    int (*i2c_read)(uint8_t addr, uint8_t *data, size_t len);
    void (*delay_ms)(uint32_t ms);
} scd30_i2c_hal_t;

typedef struct {
    scd30_i2c_hal_t hal;
    bool is_measuring;
} scd30_driver_t;

static uint8_t scd30_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            crc = (crc & 0x80) ? ((crc << 1) ^ 0x31) : (crc << 1);
        }
    }
    return crc;
}

static int scd30_send_cmd_arg(scd30_driver_t *drv, uint16_t cmd, uint16_t arg) {
    uint8_t buf[5];
    buf[0] = (uint8_t)(cmd >> 8);
    buf[1] = (uint8_t)(cmd & 0xFF);
    buf[2] = (uint8_t)(arg >> 8);
    buf[3] = (uint8_t)(arg & 0xFF);
    buf[4] = scd30_crc8(&buf[2], 2);
    return drv->hal.i2c_write(SCD30_I2C_ADDR, buf, sizeof(buf));
}

int scd30_init(scd30_driver_t *drv, const scd30_i2c_hal_t *hal) {
    if (!drv || !hal) return -1;
    drv->hal = *hal;
    drv->is_measuring = false;
    return 0;
}

int scd30_start_measurement(scd30_driver_t *drv, uint16_t ambient_pressure_mbar) {
    // ambient_pressure_mbar: 0 - вимкнено, або 700..1200 гПа
    int res = scd30_send_cmd_arg(drv, SCD30_CMD_START_CONTINUOUS, ambient_pressure_mbar);
    if (res == 0) {
        drv->is_measuring = true;
    }
    return res;
}

int scd30_check_data_ready(scd30_driver_t *drv, bool *ready) {
    uint8_t cmd[2] = { (uint8_t)(SCD30_CMD_GET_DATA_READY >> 8), (uint8_t)(SCD30_CMD_GET_DATA_READY & 0xFF) };
    if (drv->hal.i2c_write(SCD30_I2C_ADDR, cmd, 2) != 0) return -1;
    
    drv->hal.delay_ms(3);
    
    uint8_t rx[3];
    if (drv->hal.i2c_read(SCD30_I2C_ADDR, rx, 3) != 0) return -1;
    if (scd30_crc8(rx, 2) != rx[2]) return -2; // Помилка CRC

    uint16_t status = ((uint16_t)rx[0] << 8) | rx[1];
    *ready = (status == 1);
    return 0;
}

int scd30_read_measurement(scd30_driver_t *drv, scd30_data_t *out) {
    uint8_t cmd[2] = { (uint8_t)(SCD30_CMD_READ_MEASUREMENT >> 8), (uint8_t)(SCD30_CMD_READ_MEASUREMENT & 0xFF) };
    if (drv->hal.i2c_write(SCD30_I2C_ADDR, cmd, 2) != 0) return -1;

    drv->hal.delay_ms(3);

    uint8_t rx[18];
    if (drv->hal.i2c_read(SCD30_I2C_ADDR, rx, 18) != 0) return -1;

    // Перевірка 6 CRC байтів
    for (int i = 0; i < 6; ++i) {
        if (scd30_crc8(&rx[i * 3], 2) != rx[i * 3 + 2]) {
            return -2; // Помилка CRC блоку
        }
    }

    uint32_t raw_co2 = ((uint32_t)rx[0] << 24) | ((uint32_t)rx[1] << 16) | ((uint32_t)rx[3] << 8) | rx[4];
    uint32_t raw_temp = ((uint32_t)rx[6] << 24) | ((uint32_t)rx[7] << 16) | ((uint32_t)rx[9] << 8) | rx[10];
    uint32_t raw_rh = ((uint32_t)rx[12] << 24) | ((uint32_t)rx[13] << 16) | ((uint32_t)rx[15] << 8) | rx[16];

    memcpy(&out->co2_ppm, &raw_co2, sizeof(float));
    memcpy(&out->temperature_c, &raw_temp, sizeof(float));
    memcpy(&out->relative_humidity_pct, &raw_rh, sizeof(float));

    return 0;
}

int scd30_set_auto_calibration(scd30_driver_t *drv, bool enable) {
    return scd30_send_cmd_arg(drv, SCD30_CMD_SET_AUTO_CALIBRATION, enable ? 1 : 0);
}
