#include "adxl345.h"

/**
 * @brief Допоміжна функція оновлення масштабного коефіцієнта (g/LSB).
 */
static void update_scale_factor(adxl345_dev_t *dev)
{
    if (dev->full_res) {
        /* У режимі Full-Res роздільна здатність стабільна: 3.9 mg/LSB (1/256 g/LSB) */
        dev->scale_factor = 0.00390625f;
    } else {
        /* У 10-бітному режимі масштаб залежить від вибраного діапазону */
        switch (dev->range) {
            case ADXL345_RANGE_2G:
                dev->scale_factor = 0.00390625f; /* +-2g / 1024 LSB */
                break;
            case ADXL345_RANGE_4G:
                dev->scale_factor = 0.0078125f;  /* +-4g / 1024 LSB */
                break;
            case ADXL345_RANGE_8G:
                dev->scale_factor = 0.015625f;   /* +-8g / 1024 LSB */
                break;
            case ADXL345_RANGE_16G:
                dev->scale_factor = 0.03125f;    /* +-16g / 1024 LSB */
                break;
            default:
                dev->scale_factor = 0.00390625f;
                break;
        }
    }
}

adxl345_status_t adxl345_init(adxl345_dev_t *dev)
{
    if (dev == NULL || dev->read == NULL || dev->write == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t dev_id = 0;
    if (dev->read(dev->user_handle, ADXL345_REG_DEVID, &dev_id, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    if (dev_id != ADXL345_DEVICE_ID) {
        return ADXL345_ERR_DEV_ID;
    }

    /* Значення за замовчуванням */
    dev->range = ADXL345_RANGE_2G;
    dev->full_res = true;
    update_scale_factor(dev);

    /* Конфігурація формату за замовчуванням (+-2g, Full Resolution) */
    adxl345_status_t status = adxl345_set_data_format(dev, dev->range, dev->full_res);
    if (status != ADXL345_OK) {
        return status;
    }

    /* Активація вимірювання: встановлюємо біт MEASURE в регістрі POWER_CTL */
    uint8_t power_ctl = ADXL345_POWER_CTL_MEASURE;
    if (dev->write(dev->user_handle, ADXL345_REG_POWER_CTL, &power_ctl, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    return ADXL345_OK;
}

adxl345_status_t adxl345_set_data_format(adxl345_dev_t *dev, adxl345_range_t range, bool full_res)
{
    if (dev == NULL || dev->write == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t reg_val = (uint8_t)range & 0x03U;
    if (full_res) {
        reg_val |= ADXL345_DATA_FORMAT_FULL_RES;
    }

    if (dev->write(dev->user_handle, ADXL345_REG_DATA_FORMAT, &reg_val, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    dev->range = range;
    dev->full_res = full_res;
    update_scale_factor(dev);

    return ADXL345_OK;
}

adxl345_status_t adxl345_set_bandwidth(adxl345_dev_t *dev, adxl345_odr_t bw_rate)
{
    if (dev == NULL || dev->write == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t reg_val = (uint8_t)bw_rate & 0x0FU;
    if (dev->write(dev->user_handle, ADXL345_REG_BW_RATE, &reg_val, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    return ADXL345_OK;
}

adxl345_status_t adxl345_set_fifo_config(adxl345_dev_t *dev, adxl345_fifo_mode_t mode, uint8_t watermark_samples)
{
    if (dev == NULL || dev->write == NULL) {
        return ADXL345_ERR_PARAM;
    }

    if (watermark_samples > 32U) {
        watermark_samples = 32U;
    }

    uint8_t reg_val = (((uint8_t)mode & 0x03U) << 6) | (watermark_samples & 0x1FU);
    if (dev->write(dev->user_handle, ADXL345_REG_FIFO_CTL, &reg_val, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    return ADXL345_OK;
}

adxl345_status_t adxl345_configure_interrupts(adxl345_dev_t *dev, uint8_t enable_mask, uint8_t map_mask)
{
    if (dev == NULL || dev->write == NULL) {
        return ADXL345_ERR_PARAM;
    }

    /* Спочатку призначаємо канали переривань INT1/INT2 */
    if (dev->write(dev->user_handle, ADXL345_REG_INT_MAP, &map_mask, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    /* Вмикаємо вибрані джерела переривань */
    if (dev->write(dev->user_handle, ADXL345_REG_INT_ENABLE, &enable_mask, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    return ADXL345_OK;
}

adxl345_status_t adxl345_read_raw_frame(adxl345_dev_t *dev, adxl345_raw_data_t *raw)
{
    if (dev == NULL || raw == NULL || dev->read == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t buffer[6];
    /* Пакетне розширене (burst) читання 6 послідовних байтів від DATAX0 до DATAZ1 */
    if (dev->read(dev->user_handle, ADXL345_REG_DATAX0, buffer, 6) != 0) {
        return ADXL345_ERR_BUS;
    }

    /* ADXL345 зберігає значення у форматі Little-Endian (LSB спочатку) */
    raw->x = (int16_t)(((uint16_t)buffer[1] << 8) | buffer[0]);
    raw->y = (int16_t)(((uint16_t)buffer[3] << 8) | buffer[2]);
    raw->z = (int16_t)(((uint16_t)buffer[5] << 8) | buffer[4]);

    return ADXL345_OK;
}

adxl345_status_t adxl345_read_fifo_entries(adxl345_dev_t *dev, uint8_t *entries)
{
    if (dev == NULL || entries == NULL || dev->read == NULL) {
        return ADXL345_ERR_PARAM;
    }

    uint8_t status_reg = 0;
    if (dev->read(dev->user_handle, ADXL345_REG_FIFO_STATUS, &status_reg, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    /* Маска 0x3F витягує біти ENTRIES[5:0] */
    *entries = status_reg & 0x3FU;
    return ADXL345_OK;
}

adxl345_status_t adxl345_read_interrupt_source(adxl345_dev_t *dev, uint8_t *int_source)
{
    if (dev == NULL || int_source == NULL || dev->read == NULL) {
        return ADXL345_ERR_PARAM;
    }

    if (dev->read(dev->user_handle, ADXL345_REG_INT_SOURCE, int_source, 1) != 0) {
        return ADXL345_ERR_BUS;
    }

    return ADXL345_OK;
}

void adxl345_convert_raw_to_g(const adxl345_dev_t *dev, const adxl345_raw_data_t *raw, adxl345_accel_t *accel)
{
    if (dev == NULL || raw == NULL || accel == NULL) {
        return;
    }

    accel->x = (float)raw->x * dev->scale_factor;
    accel->y = (float)raw->y * dev->scale_factor;
    accel->z = (float)raw->z * dev->scale_factor;
}
