#include "sensor_driver.h"

#define REG_CHIP_ID       0xD0
#define EXPECTED_CHIP_ID  0x58
#define REG_MEAS_START    0xF4
#define CMD_START_BURST   0xB6
#define REG_DATA_BURST    0xF7
#define CONV_DURATION_US  20000  /* 20 мс час апаратної конверсії */

sensor_status_t sensor_init(sensor_device_t *dev, const sensor_bus_ops_t *ops, void *user_ctx) {
    if (!dev || !ops || !ops->read || !ops->write || !ops->get_time_us) {
        return SENSOR_ERR_NULL_PTR;
    }
    dev->ops = ops;
    dev->user_ctx = user_ctx;
    dev->state = SENSOR_STATE_UNINITIALIZED;
    dev->conv_start_us = 0;
    dev->conv_timeout_us = CONV_DURATION_US;

    /* 1. Перевірка Chip ID для підтвердження наявності чипа на шині */
    uint8_t chip_id = 0;
    sensor_status_t status = dev->ops->read(dev->user_ctx, REG_CHIP_ID, &chip_id, 1);
    if (status != SENSOR_OK) {
        if (dev->ops->recover_bus) {
            dev->ops->recover_bus(dev->user_ctx);
        }
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_BUS_IO;
    }

    if (chip_id != EXPECTED_CHIP_ID) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_CHIP_ID;
    }

    dev->state = SENSOR_STATE_IDLE;
    return SENSOR_OK;
}

sensor_status_t sensor_start_measurement(sensor_device_t *dev) {
    if (!dev || !dev->ops) {
        return SENSOR_ERR_NULL_PTR;
    }
    if (dev->state != SENSOR_STATE_IDLE && dev->state != SENSOR_STATE_DATA_READY) {
        return SENSOR_ERR_INVALID_STATE;
    }

    /* Надсилання команди запуску заміру */
    const uint8_t cmd = CMD_START_BURST;
    sensor_status_t status = dev->ops->write(dev->user_ctx, REG_MEAS_START, &cmd, 1);
    if (status != SENSOR_OK) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_BUS_IO;
    }

    dev->conv_start_us = dev->ops->get_time_us();
    dev->state = SENSOR_STATE_CONVERTING;
    return SENSOR_OK;
}

sensor_status_t sensor_poll(sensor_device_t *dev, sensor_data_t *out_data) {
    if (!dev || !dev->ops || !out_data) {
        return SENSOR_ERR_NULL_PTR;
    }

    if (dev->state != SENSOR_STATE_CONVERTING) {
        return SENSOR_ERR_INVALID_STATE;
    }

    uint32_t now = dev->ops->get_time_us();
    uint32_t elapsed = now - dev->conv_start_us;

    /* Неблокуюча перевірка таймера без блокування процесорного ядра */
    if (elapsed < dev->conv_timeout_us) {
        return SENSOR_ERR_NOT_READY;
    }

    /* Зчитування 7 байтів: 2 байти температури + CRC, 2 байти тиску + CRC, 1 байт статусу */
    sensor_status_t status = dev->ops->read(dev->user_ctx, REG_DATA_BURST, dev->raw_buf, 7);
    if (status != SENSOR_OK) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_BUS_IO;
    }

    /* Верифікація CRC температури */
    uint8_t temp_crc = sensor_calculate_crc8(&dev->raw_buf[0], 2);
    if (temp_crc != dev->raw_buf[2]) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_CRC;
    }

    /* Верифікація CRC тиску */
    uint8_t press_crc = sensor_calculate_crc8(&dev->raw_buf[3], 2);
    if (press_crc != dev->raw_buf[5]) {
        dev->state = SENSOR_STATE_ERROR;
        return SENSOR_ERR_CRC;
    }

    /* Розбір 16-бітного знакового значення температури (доповняльний код, Big-Endian) */
    int16_t raw_temp = (int16_t)(((uint16_t)dev->raw_buf[0] << 8) | dev->raw_buf[1]);
    /* Формула перетворення: T = -45°C + 175 * raw / 65535 */
    out_data->temperature_mdeg_c = (int32_t)(-45000 + ((int64_t)raw_temp * 175000) / 65535);

    /* Розбір 16-бітного беззнакового значення тиску */
    uint16_t raw_press = ((uint16_t)dev->raw_buf[3] << 8) | dev->raw_buf[4];
    /* Формула перетворення: P = 30000 Па + (raw * 80000) / 65535 */
    out_data->pressure_pa = (uint32_t)(30000 + ((uint64_t)raw_press * 80000) / 65535);
    out_data->humidity_mpercent = 0;
    out_data->timestamp_us = now;

    dev->state = SENSOR_STATE_DATA_READY;
    return SENSOR_OK;
}

sensor_status_t sensor_reset_fsm(sensor_device_t *dev) {
    if (!dev) return SENSOR_ERR_NULL_PTR;
    dev->state = SENSOR_STATE_IDLE;
    dev->conv_start_us = 0;
    return SENSOR_OK;
}
