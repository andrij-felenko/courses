#include "adxl345.h"
#include <stddef.h>

/* Допоміжні функції для роботи з шиною */
static adxl345_status_t write_reg(adxl345_dev_t *dev, uint8_t reg, uint8_t value) {
    if (dev->hal.write(dev->hal.intf_ptr, reg, &value, 1) != 0) {
        return ADXL345_ERR_BUS;
    }
    return ADXL345_OK;
}

static adxl345_status_t read_reg(adxl345_dev_t *dev, uint8_t reg, uint8_t *value) {
    if (dev->hal.read(dev->hal.intf_ptr, reg, value, 1) != 0) {
        return ADXL345_ERR_BUS;
    }
    return ADXL345_OK;
}

adxl345_status_t adxl345_init(adxl345_dev_t *dev, const adxl345_hal_t *hal, const adxl345_config_t *config) {
    if (!dev || !hal || !config || !hal->read || !hal->write) {
        return ADXL345_ERR_INVALID_ARG;
    }

    dev->hal = *hal;
    dev->config = *config;
    dev->initialized = false;

    /* 1. Зчитування та перевірка ідентифікатора DEVID (0xE5) */
    uint8_t dev_id = 0;
    adxl345_status_t status = read_reg(dev, ADXL345_REG_DEVID, &dev_id);
    if (status != ADXL345_OK) {
        return status;
    }
    if (dev_id != ADXL345_DEVICE_ID) {
        return ADXL345_ERR_DEVICE_NOT_FOUND;
    }

    /* 2. Переведення сенсора у режим очікування Standby перед налаштуванням */
    status = write_reg(dev, ADXL345_REG_POWER_CTL, 0x00);
    if (status != ADXL345_OK) {
        return status;
    }

    /* 3. Налаштування частоти оновлення даних (ODR) у регістрі BW_RATE */
    uint8_t bw_rate = (uint8_t)(config->odr & 0x0F);
    status = write_reg(dev, ADXL345_REG_BW_RATE, bw_rate);
    if (status != ADXL345_OK) {
        return status;
    }

    /* 4. Налаштування формату даних: роздільність Full-Res та діапазон вимірювань */
    uint8_t data_format = (uint8_t)(config->range & 0x03);
    if (config->full_resolution) {
        data_format |= ADXL345_DATA_FORMAT_FULL_RES;
    }
    status = write_reg(dev, ADXL345_REG_DATA_FORMAT, data_format);
    if (status != ADXL345_OK) {
        return status;
    }

    /* 5. Налаштування потокового кільцевого буфера Stream FIFO та рівня Watermark */
    uint8_t fifo_samples = config->watermark_samples & 0x1F;
    if (fifo_samples == 0) {
        fifo_samples = 1;
    }
    uint8_t fifo_ctl = (uint8_t)((config->fifo_mode << 6) | fifo_samples);
    status = write_reg(dev, ADXL345_REG_FIFO_CTL, fifo_ctl);
    if (status != ADXL345_OK) {
        return status;
    }

    /* 6. Маршрутизація апаратних переривань (наприклад, Watermark -> INT1, Overrun -> INT2) */
    status = write_reg(dev, ADXL345_REG_INT_MAP, config->int_map_mask);
    if (status != ADXL345_OK) {
        return status;
    }

    /* 7. Активація потрібних джерел переривань у регістрі INT_ENABLE */
    status = write_reg(dev, ADXL345_REG_INT_ENABLE, config->int_enable_mask);
    if (status != ADXL345_OK) {
        return status;
    }

    /* 8. Переведення з Standby у режим вимірювання (Measurement Mode) */
    status = write_reg(dev, ADXL345_REG_POWER_CTL, ADXL345_POWER_CTL_MEASURE);
    if (status != ADXL345_OK) {
        return status;
    }

    dev->initialized = true;
    return ADXL345_OK;
}

adxl345_status_t adxl345_set_measure_mode(adxl345_dev_t *dev, bool enable) {
    if (!dev || !dev->initialized) {
        return ADXL345_ERR_INVALID_ARG;
    }
    uint8_t pwr_val = enable ? ADXL345_POWER_CTL_MEASURE : 0x00;
    return write_reg(dev, ADXL345_REG_POWER_CTL, pwr_val);
}

adxl345_status_t adxl345_read_raw(adxl345_dev_t *dev, adxl345_raw_data_t *raw) {
    if (!dev || !raw || !dev->initialized) {
        return ADXL345_ERR_INVALID_ARG;
    }

    /* Атомарне burst-зчитування 6 регістрів послідовних вихідних даних (DATAX0..DATAZ1).
     * Використання однієї пакетної транзакції запобігає розриву кадрів вимірювань між вісями.
     */
    uint8_t buffer[6];
    if (dev->hal.read(dev->hal.intf_ptr, ADXL345_REG_DATAX0, buffer, 6) != 0) {
        return ADXL345_ERR_BUS;
    }

    /* Формування 16-бітних значень у доповняльному коді (little-endian) */
    raw->x = (int16_t)((uint16_t)buffer[0] | ((uint16_t)buffer[1] << 8));
    raw->y = (int16_t)((uint16_t)buffer[2] | ((uint16_t)buffer[3] << 8));
    raw->z = (int16_t)((uint16_t)buffer[4] | ((uint16_t)buffer[5] << 8));

    return ADXL345_OK;
}

void adxl345_convert_raw_to_g(const adxl345_raw_data_t *raw, adxl345_accel_g_t *accel) {
    if (!raw || !accel) {
        return;
    }
    /* Перерахунок у g з масштабним коефіцієнтом 3.9 мг/МЗР (0.0039 g/МЗР) для Full Resolution */
    accel->x = (float)raw->x * ADXL345_SCALE_FACTOR_G;
    accel->y = (float)raw->y * ADXL345_SCALE_FACTOR_G;
    accel->z = (float)raw->z * ADXL345_SCALE_FACTOR_G;
}

adxl345_status_t adxl345_read_accel(adxl345_dev_t *dev, adxl345_accel_g_t *accel) {
    adxl345_raw_data_t raw;
    adxl345_status_t status = adxl345_read_raw(dev, &raw);
    if (status == ADXL345_OK) {
        adxl345_convert_raw_to_g(&raw, accel);
    }
    return status;
}

adxl345_status_t adxl345_read_int_source(adxl345_dev_t *dev, uint8_t *int_source) {
    if (!dev || !int_source) {
        return ADXL345_ERR_INVALID_ARG;
    }
    return read_reg(dev, ADXL345_REG_INT_SOURCE, int_source);
}

adxl345_status_t adxl345_get_fifo_level(adxl345_dev_t *dev, uint8_t *fifo_entries) {
    if (!dev || !fifo_entries) {
        return ADXL345_ERR_INVALID_ARG;
    }
    uint8_t status_val = 0;
    adxl345_status_t status = read_reg(dev, ADXL345_REG_FIFO_STATUS, &status_val);
    if (status == ADXL345_OK) {
        *fifo_entries = status_val & 0x3F; /* Молодші 6 біт містять кількість записів */
    }
    return status;
}
