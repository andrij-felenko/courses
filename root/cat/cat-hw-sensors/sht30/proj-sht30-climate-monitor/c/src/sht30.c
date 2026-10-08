#include "sht30.h"
#include <math.h>

/**
 * @file sht30.c
 * @brief Реалізація процедурного C-драйвера SHT30.
 */

sht30_err_t sht30_init(sht30_t *dev, uint8_t i2c_addr, void (*delay_fn)(uint32_t ms))
{
    if (dev == NULL || delay_fn == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    if (i2c_addr != SHT30_I2C_ADDR_A && i2c_addr != SHT30_I2C_ADDR_B) {
        return SHT30_ERR_INVALID_ARG;
    }

    dev->i2c_address = i2c_addr;
    dev->use_clock_stretching = false;
    dev->repeatability = SHT30_REPEATABILITY_HIGH;
    dev->timeout_ms = 100;
    dev->delay_ms = delay_fn;

    return SHT30_OK;
}

uint8_t sht30_calc_crc8(const uint8_t *data)
{
    if (data == NULL) {
        return 0;
    }

    uint8_t crc = 0xFF;
    for (size_t i = 0; i < 2; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x31);
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

sht30_err_t sht30_calculate_dew_point(float temp_c, float humidity_percent, float *dew_point_c)
{
    if (dew_point_c == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    /* Перевірка допустимого діапазону відносної вологості */
    if (humidity_percent <= 0.0f || humidity_percent > 100.0f) {
        return SHT30_ERR_DEW_POINT_INVALID;
    }

    /* Коефіцієнти формули Магнуса для температурного діапазону від -40 до +60 градусів C */
    const float a = 17.27f;
    const float b = 237.7f;

    float alpha = ((a * temp_c) / (b + temp_c)) + logf(humidity_percent / 100.0f);
    
    /* Запобігання діленню на нуль */
    float denominator = a - alpha;
    if (denominator == 0.0f) {
        return SHT30_ERR_DEW_POINT_INVALID;
    }

    *dew_point_c = (b * alpha) / denominator;
    return SHT30_OK;
}

sht30_err_t sht30_read_single_shot(sht30_t *dev, sht30_data_t *data)
{
    if (dev == NULL || data == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    uint16_t cmd_code;
    uint32_t meas_delay_ms = 0;

    if (dev->use_clock_stretching) {
        switch (dev->repeatability) {
            case SHT30_REPEATABILITY_HIGH:
                cmd_code = SHT30_CMD_MEAS_CLOCKSTR_HIGH;
                break;
            case SHT30_REPEATABILITY_MEDIUM:
                cmd_code = SHT30_CMD_MEAS_CLOCKSTR_MEDIUM;
                break;
            case SHT30_REPEATABILITY_LOW:
                cmd_code = SHT30_CMD_MEAS_CLOCKSTR_LOW;
                break;
            default:
                cmd_code = SHT30_CMD_MEAS_CLOCKSTR_HIGH;
                break;
        }
    } else {
        switch (dev->repeatability) {
            case SHT30_REPEATABILITY_HIGH:
                cmd_code = SHT30_CMD_MEAS_POLL_HIGH;
                meas_delay_ms = 15;
                break;
            case SHT30_REPEATABILITY_MEDIUM:
                cmd_code = SHT30_CMD_MEAS_POLL_MEDIUM;
                meas_delay_ms = 6;
                break;
            case SHT30_REPEATABILITY_LOW:
                cmd_code = SHT30_CMD_MEAS_POLL_LOW;
                meas_delay_ms = 4;
                break;
            default:
                cmd_code = SHT30_CMD_MEAS_POLL_HIGH;
                meas_delay_ms = 15;
                break;
        }
    }

    uint8_t tx_buf[2];
    tx_buf[0] = (uint8_t)(cmd_code >> 8);
    tx_buf[1] = (uint8_t)(cmd_code & 0xFF);

    uint8_t rx_buf[6] = {0};
    i2c_err_t i2c_res = i2c_bus_write_read(dev->i2c_address,
                                           tx_buf, 2,
                                           rx_buf, 6,
                                           meas_delay_ms,
                                           dev->timeout_ms);
    if (i2c_res != I2C_SUCCESS) {
        return SHT30_ERR_I2C_BUS;
    }

    /* Верифікація контрольних сум CRC-8 для температури та вологості */
    uint8_t calc_temp_crc = sht30_calc_crc8(&rx_buf[0]);
    if (calc_temp_crc != rx_buf[2]) {
        data->is_crc_valid = false;
        return SHT30_ERR_CRC_TEMP;
    }

    uint8_t calc_hum_crc = sht30_calc_crc8(&rx_buf[3]);
    if (calc_hum_crc != rx_buf[5]) {
        data->is_crc_valid = false;
        return SHT30_ERR_CRC_HUMIDITY;
    }

    data->is_crc_valid = true;

    /* Обчислення 16-бітних сирих значень */
    uint16_t raw_temp = (uint16_t)(((uint16_t)rx_buf[0] << 8) | rx_buf[1]);
    uint16_t raw_hum  = (uint16_t)(((uint16_t)rx_buf[3] << 8) | rx_buf[4]);

    /* Математичний перерахунок сирих даних у фізичні одиниці */
    data->temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
    data->humidity_percent = 100.0f * ((float)raw_hum / 65535.0f);

    /* Обмеження вологості фізичним діапазоном 0..100% */
    if (data->humidity_percent < 0.0f) {
        data->humidity_percent = 0.0f;
    } else if (data->humidity_percent > 100.0f) {
        data->humidity_percent = 100.0f;
    }

    /* Розрахунок точки роси */
    sht30_err_t dew_res = sht30_calculate_dew_point(data->temperature_c,
                                                   data->humidity_percent,
                                                   &data->dew_point_c);
    if (dew_res != SHT30_OK) {
        data->dew_point_c = 0.0f;
    }

    return SHT30_OK;
}

sht30_err_t sht30_soft_reset(sht30_t *dev)
{
    if (dev == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    uint8_t tx_buf[2];
    tx_buf[0] = (uint8_t)(SHT30_CMD_SOFT_RESET >> 8);
    tx_buf[1] = (uint8_t)(SHT30_CMD_SOFT_RESET & 0xFF);

    i2c_err_t i2c_res = i2c_bus_write(dev->i2c_address, tx_buf, 2, dev->timeout_ms);
    if (i2c_res != I2C_SUCCESS) {
        return SHT30_ERR_I2C_BUS;
    }

    if (dev->delay_ms) {
        dev->delay_ms(2);
    }

    return SHT30_OK;
}

sht30_err_t sht30_set_heater(sht30_t *dev, bool enable)
{
    if (dev == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    uint16_t cmd_code = enable ? SHT30_CMD_HEATER_ENABLE : SHT30_CMD_HEATER_DISABLE;
    uint8_t tx_buf[2];
    tx_buf[0] = (uint8_t)(cmd_code >> 8);
    tx_buf[1] = (uint8_t)(cmd_code & 0xFF);

    i2c_err_t i2c_res = i2c_bus_write(dev->i2c_address, tx_buf, 2, dev->timeout_ms);
    if (i2c_res != I2C_SUCCESS) {
        return SHT30_ERR_I2C_BUS;
    }

    if (dev->delay_ms) {
        dev->delay_ms(1);
    }

    return SHT30_OK;
}

sht30_err_t sht30_read_status(sht30_t *dev, sht30_status_t *status)
{
    if (dev == NULL || status == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    uint8_t tx_buf[2];
    tx_buf[0] = (uint8_t)(SHT30_CMD_READ_STATUS >> 8);
    tx_buf[1] = (uint8_t)(SHT30_CMD_READ_STATUS & 0xFF);

    uint8_t rx_buf[3] = {0};
    i2c_err_t i2c_res = i2c_bus_write_read(dev->i2c_address,
                                           tx_buf, 2,
                                           rx_buf, 3,
                                           0,
                                           dev->timeout_ms);
    if (i2c_res != I2C_SUCCESS) {
        return SHT30_ERR_I2C_BUS;
    }

    /* Верифікація CRC-8 для 2 байтів регістру статусу */
    uint8_t calc_crc = sht30_calc_crc8(&rx_buf[0]);
    if (calc_crc != rx_buf[2]) {
        return SHT30_ERR_CRC_TEMP;
    }

    uint16_t stat_raw = (uint16_t)(((uint16_t)rx_buf[0] << 8) | rx_buf[1]);
    status->checksum_failed = (stat_raw & (1 << 0)) != 0;
    status->command_failed  = (stat_raw & (1 << 1)) != 0;
    status->system_reset    = (stat_raw & (1 << 4)) != 0;
    status->heater_active   = (stat_raw & (1 << 13)) != 0;
    status->alert_pending   = (stat_raw & (1 << 15)) != 0;

    return SHT30_OK;
}

sht30_err_t sht30_clear_status(sht30_t *dev)
{
    if (dev == NULL) {
        return SHT30_ERR_INVALID_ARG;
    }

    uint8_t tx_buf[2];
    tx_buf[0] = (uint8_t)(SHT30_CMD_CLEAR_STATUS >> 8);
    tx_buf[1] = (uint8_t)(SHT30_CMD_CLEAR_STATUS & 0xFF);

    i2c_err_t i2c_res = i2c_bus_write(dev->i2c_address, tx_buf, 2, dev->timeout_ms);
    if (i2c_res != I2C_SUCCESS) {
        return SHT30_ERR_I2C_BUS;
    }

    if (dev->delay_ms) {
        dev->delay_ms(1);
    }

    return SHT30_OK;
}
