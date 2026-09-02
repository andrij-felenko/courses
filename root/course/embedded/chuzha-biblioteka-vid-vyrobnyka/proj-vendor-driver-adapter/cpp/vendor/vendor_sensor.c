/*
 * Реалізація вендорського драйвера. Збирається компілятором C навіть у
 * C++-проєкті: чужий код лишається чужим, ми його не «покращуємо».
 */
#include "vendor_sensor.h"

#define REG_CALIB00   0x88U
#define REG_CHIP_ID   0xD0U
#define REG_RESET     0xE0U
#define REG_STATUS    0xF3U
#define REG_CTRL_MEAS 0xF4U
#define REG_CONFIG    0xF5U
#define REG_PRESS_MSB 0xF7U

#define RESET_COMMAND     0xB6U
#define STATUS_IM_UPDATE  0x01U
#define STATUS_MEASURING  0x08U

#define CALIB_BLOCK_LEN 24U
#define NVM_WAIT_TRIES  100U

/* Оверсемплінг ×1 по обох каналах; молодші два біти — режим. */
#define CTRL_MEAS_OSRS ((1U << 5) | (1U << 2))

static uint16_t le_u16(const uint8_t *p)
{
    return (uint16_t)(((uint16_t)p[1] << 8) | (uint16_t)p[0]);
}

static int16_t le_s16(const uint8_t *p)
{
    return (int16_t)le_u16(p);
}

static int8_t read_calibration(vendor_sensor_dev_t *dev)
{
    uint8_t buf[CALIB_BLOCK_LEN];
    int8_t rc = dev->read(REG_CALIB00, buf, CALIB_BLOCK_LEN, dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }

    dev->calib.dig_t1 = le_u16(&buf[0]);
    dev->calib.dig_t2 = le_s16(&buf[2]);
    dev->calib.dig_t3 = le_s16(&buf[4]);
    dev->calib.dig_p1 = le_u16(&buf[6]);
    dev->calib.dig_p2 = le_s16(&buf[8]);
    dev->calib.dig_p3 = le_s16(&buf[10]);
    dev->calib.dig_p4 = le_s16(&buf[12]);
    dev->calib.dig_p5 = le_s16(&buf[14]);
    dev->calib.dig_p6 = le_s16(&buf[16]);
    dev->calib.dig_p7 = le_s16(&buf[18]);
    dev->calib.dig_p8 = le_s16(&buf[20]);
    dev->calib.dig_p9 = le_s16(&buf[22]);
    dev->calib.t_fine = 0;

    /* Порожній або незчитаний блок NVM дає нулі. dig_p1 = 0 обертає
       знаменник формули тиску на нуль, тож ловимо це тут. */
    if (dev->calib.dig_t1 == 0U || dev->calib.dig_p1 == 0U) {
        return VENDOR_E_CALIB;
    }
    return VENDOR_OK;
}

static int32_t compensate_temperature(vendor_calib_t *c, int32_t adc_t)
{
    int32_t var1 = ((((adc_t >> 3) - ((int32_t)c->dig_t1 << 1))) *
                    ((int32_t)c->dig_t2)) >> 11;
    int32_t var2 = (((((adc_t >> 4) - ((int32_t)c->dig_t1)) *
                      ((adc_t >> 4) - ((int32_t)c->dig_t1))) >> 12) *
                    ((int32_t)c->dig_t3)) >> 14;

    c->t_fine = var1 + var2;
    return (c->t_fine * 5 + 128) >> 8;
}

static int8_t compensate_pressure(const vendor_calib_t *c, int32_t adc_p,
                                  uint32_t *out)
{
    int64_t var1 = (int64_t)c->t_fine - 128000;
    int64_t var2 = var1 * var1 * (int64_t)c->dig_p6;
    int64_t p;

    var2 = var2 + ((var1 * (int64_t)c->dig_p5) << 17);
    var2 = var2 + (((int64_t)c->dig_p4) << 35);
    var1 = ((var1 * var1 * (int64_t)c->dig_p3) >> 8) +
           ((var1 * (int64_t)c->dig_p2) << 12);
    var1 = ((((int64_t)1 << 47) + var1)) * ((int64_t)c->dig_p1) >> 33;

    if (var1 == 0) {
        /* Саме тут «нульове калібрування» перетворилося б на ділення на нуль. */
        return VENDOR_E_CALIB;
    }

    p = 1048576 - adc_p;
    p = (((p << 31) - var2) / var1) * 3125;
    var1 = (((int64_t)c->dig_p9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)c->dig_p8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (((int64_t)c->dig_p7) << 4);

    if (p < 0) {
        return VENDOR_E_CALIB;
    }
    *out = (uint32_t)p;
    return VENDOR_OK;
}

int8_t vendor_sensor_init(vendor_sensor_dev_t *dev)
{
    uint8_t cmd = RESET_COMMAND;
    uint8_t status = 0U;
    uint8_t chip_id = 0U;
    uint8_t ctrl;
    int8_t rc;
    uint32_t tries;

    if (dev == 0 || dev->read == 0 || dev->write == 0 || dev->delay_us == 0) {
        return VENDOR_E_NULL_PTR;
    }

    rc = dev->write(REG_RESET, &cmd, 1U, dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }
    dev->delay_us(2000U, dev->intf_ptr);   /* час старту кремнію */

    /* Поки прапорець im_update стоїть, коефіцієнти читати не можна. */
    for (tries = 0U; tries < NVM_WAIT_TRIES; ++tries) {
        rc = dev->read(REG_STATUS, &status, 1U, dev->intf_ptr);
        if (rc != VENDOR_OK) {
            return rc;
        }
        if ((status & STATUS_IM_UPDATE) == 0U) {
            break;
        }
        dev->delay_us(1000U, dev->intf_ptr);
    }
    if (tries == NVM_WAIT_TRIES) {
        return VENDOR_E_COMM_FAIL;
    }

    rc = dev->read(REG_CHIP_ID, &chip_id, 1U, dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }
    if (chip_id != VENDOR_CHIP_ID_BMP280 && chip_id != VENDOR_CHIP_ID_BME280) {
        return VENDOR_E_DEV_NOT_FOUND;
    }
    dev->chip_id = chip_id;

    rc = read_calibration(dev);
    if (rc != VENDOR_OK) {
        return rc;
    }

    ctrl = 0U;
    rc = dev->write(REG_CONFIG, &ctrl, 1U, dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }
    ctrl = (uint8_t)(CTRL_MEAS_OSRS | VENDOR_MODE_SLEEP);
    return dev->write(REG_CTRL_MEAS, &ctrl, 1U, dev->intf_ptr);
}

int8_t vendor_sensor_set_mode(vendor_sensor_dev_t *dev, uint8_t mode)
{
    uint8_t ctrl = 0U;
    int8_t rc;

    if (dev == 0 || dev->read == 0 || dev->write == 0) {
        return VENDOR_E_NULL_PTR;
    }

    /* Читання-модифікація-запис: оверсемплінг у старших бітах треба зберегти. */
    rc = dev->read(REG_CTRL_MEAS, &ctrl, 1U, dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }
    ctrl = (uint8_t)((ctrl & (uint8_t)~0x03U) | (mode & 0x03U));
    return dev->write(REG_CTRL_MEAS, &ctrl, 1U, dev->intf_ptr);
}

int8_t vendor_sensor_is_measuring(vendor_sensor_dev_t *dev, uint8_t *busy)
{
    uint8_t status = 0U;
    int8_t rc;

    if (dev == 0 || busy == 0) {
        return VENDOR_E_NULL_PTR;
    }
    rc = dev->read(REG_STATUS, &status, 1U, dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }
    *busy = ((status & STATUS_MEASURING) != 0U) ? 1U : 0U;
    return VENDOR_OK;
}

int8_t vendor_sensor_get_data(vendor_sensor_dev_t *dev, vendor_data_t *out)
{
    uint8_t raw[6] = {0};
    int32_t adc_p, adc_t;
    int8_t rc;

    if (dev == 0 || out == 0 || dev->read == 0) {
        return VENDOR_E_NULL_PTR;
    }

    /* Один пакетний перебіг: розрив дав би відліки з різних перетворень. */
    rc = dev->read(REG_PRESS_MSB, raw, sizeof(raw), dev->intf_ptr);
    if (rc != VENDOR_OK) {
        return rc;
    }

    adc_p = (int32_t)(((uint32_t)raw[0] << 12) | ((uint32_t)raw[1] << 4) |
                      ((uint32_t)raw[2] >> 4));
    adc_t = (int32_t)(((uint32_t)raw[3] << 12) | ((uint32_t)raw[4] << 4) |
                      ((uint32_t)raw[5] >> 4));

    /* Порядок обов'язковий: тиск рахується через t_fine від температури. */
    out->temperature = compensate_temperature(&dev->calib, adc_t);
    return compensate_pressure(&dev->calib, adc_p, &out->pressure_q24_8);
}
