/**
 * @file driver_bmp280.c
 * @brief Реалізація функцій драйвера BMP280, бітової розпаковки та компенсації.
 */

#include "driver_bmp280.h"

/* Таблиця контрольної суми CRC-8 Dallas/Maxim (поліном x^8 + x^5 + x^4 + 1 = 0x31) */
static const uint8_t crc8_table[256] = {
    0x00U, 0x5EU, 0xBCU, 0xE2U, 0x61U, 0x3FU, 0xDDU, 0x83U,
    0xC2U, 0x9CU, 0x7EU, 0x20U, 0xA3U, 0xFDU, 0x1FU, 0x41U,
    0x9DU, 0xC3U, 0x21U, 0x7FU, 0xFCU, 0xA2U, 0x40U, 0x1EU,
    0x5FU, 0x01U, 0xE3U, 0xBDU, 0x3EU, 0x60U, 0x82U, 0xDCU,
    0x23U, 0x7DU, 0x9FU, 0xC1U, 0x42U, 0x1CU, 0xFEU, 0xA0U,
    0xE1U, 0xBFU, 0x5DU, 0x03U, 0x80U, 0xDEU, 0x3CU, 0x62U,
    0xBEU, 0xE0U, 0x02U, 0x5CU, 0xDFU, 0x81U, 0x63U, 0x3DU,
    0x7CU, 0x22U, 0xC0U, 0x9EU, 0x1DU, 0x43U, 0xA1U, 0xFFU,
    0x46U, 0x18U, 0xFAU, 0xA4U, 0x27U, 0x79U, 0x9BU, 0xC5U,
    0x84U, 0xDAU, 0x38U, 0x66U, 0xE5U, 0xBBU, 0x59U, 0x07U,
    0xDBU, 0x85U, 0x67U, 0x39U, 0xBAU, 0xE4U, 0x06U, 0x58U,
    0x19U, 0x47U, 0xA5U, 0xFBU, 0x78U, 0x26U, 0xC4U, 0x9AU,
    0x65U, 0x3BU, 0xD9U, 0x87U, 0x04U, 0x5AU, 0xB8U, 0xE6U,
    0xA7U, 0xF9U, 0x1BU, 0x45U, 0xC6U, 0x98U, 0x7AU, 0x24U,
    0xF8U, 0xA6U, 0x44U, 0x1AU, 0x99U, 0xC7U, 0x25U, 0x7BU,
    0x3AU, 0x64U, 0x86U, 0xD8U, 0x5BU, 0x05U, 0xE7U, 0xB9U,
    0x8CU, 0xD2U, 0x30U, 0x6EU, 0xEDU, 0xB3U, 0x51U, 0x0FU,
    0x4EU, 0x10U, 0xF2U, 0xACU, 0x2FU, 0x71U, 0x93U, 0xCDU,
    0x11U, 0x4FU, 0xADU, 0xF3U, 0x70U, 0x2EU, 0xCCU, 0x92U,
    0xD3U, 0x8DU, 0x6FU, 0x31U, 0xB2U, 0xECU, 0x0EU, 0x50U,
    0xAFU, 0xF1U, 0x13U, 0x4DU, 0xCEU, 0x90U, 0x72U, 0x2CU,
    0x6DU, 0x33U, 0xD1U, 0x8FU, 0x0CU, 0x52U, 0xB0U, 0xEEU,
    0x32U, 0x6CU, 0x8EU, 0xD0U, 0x53U, 0x0DU, 0xEFU, 0xB1U,
    0xF0U, 0xAEU, 0x4CU, 0x12U, 0x91U, 0xCFU, 0x2DU, 0x73U,
    0xCAU, 0x94U, 0x76U, 0x28U, 0xABU, 0xF5U, 0x17U, 0x49U,
    0x08U, 0x56U, 0xB4U, 0xEAU, 0x69U, 0x37U, 0xD5U, 0x8BU,
    0x57U, 0x09U, 0xEBU, 0xB5U, 0x36U, 0x68U, 0x8AU, 0xD4U,
    0x95U, 0xCBU, 0x29U, 0x77U, 0xF4U, 0xAAU, 0x48U, 0x16U,
    0xE9U, 0xB7U, 0x55U, 0x0BU, 0x88U, 0xD6U, 0x34U, 0x6AU,
    0x2BU, 0x75U, 0x97U, 0xC9U, 0x4AU, 0x14U, 0xF6U, 0xA8U,
    0x74U, 0x2AU, 0xC8U, 0x96U, 0x15U, 0x4BU, 0xA9U, 0xF7U,
    0xB6U, 0xE8U, 0x0AU, 0x54U, 0xD7U, 0x89U, 0x6BU, 0x35U
};

uint8_t bmp280_calc_crc8_dallas(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00U;
    if (data == NULL) {
        return 0x00U;
    }
    for (size_t i = 0; i < len; ++i) {
        crc = crc8_table[crc ^ data[i]];
    }
    return crc;
}

static bmp280_status_t read_calibration_nvm(bmp280_handle_t *dev) {
    uint8_t calib_buf[BMP280_CALIB_DATA_SIZE];
    bmp280_status_t status = dev->bus.read(dev->bus.dev_addr, BMP280_REG_CALIB_START, calib_buf, BMP280_CALIB_DATA_SIZE);
    if (status != BMP280_OK) {
        return status;
    }

    /* Розпаковка Little-Endian коефіцієнтів у структури MISRA-C */
    dev->calib.dig_T1 = (uint16_t)(((uint16_t)calib_buf[1] << 8) | (uint16_t)calib_buf[0]);
    dev->calib.dig_T2 = (int16_t)(((uint16_t)calib_buf[3] << 8) | (uint16_t)calib_buf[2]);
    dev->calib.dig_T3 = (int16_t)(((uint16_t)calib_buf[5] << 8) | (uint16_t)calib_buf[4]);

    dev->calib.dig_P1 = (uint16_t)(((uint16_t)calib_buf[7] << 8) | (uint16_t)calib_buf[6]);
    dev->calib.dig_P2 = (int16_t)(((uint16_t)calib_buf[9] << 8) | (uint16_t)calib_buf[8]);
    dev->calib.dig_P3 = (int16_t)(((uint16_t)calib_buf[11] << 8) | (uint16_t)calib_buf[10]);
    dev->calib.dig_P4 = (int16_t)(((uint16_t)calib_buf[13] << 8) | (uint16_t)calib_buf[12]);
    dev->calib.dig_P5 = (int16_t)(((uint16_t)calib_buf[15] << 8) | (uint16_t)calib_buf[14]);
    dev->calib.dig_P6 = (int16_t)(((uint16_t)calib_buf[17] << 8) | (uint16_t)calib_buf[16]);
    dev->calib.dig_P7 = (int16_t)(((uint16_t)calib_buf[19] << 8) | (uint16_t)calib_buf[18]);
    dev->calib.dig_P8 = (int16_t)(((uint16_t)calib_buf[21] << 8) | (uint16_t)calib_buf[20]);
    dev->calib.dig_P9 = (int16_t)(((uint16_t)calib_buf[23] << 8) | (uint16_t)calib_buf[22]);

    /* Валідація: коефіцієнти dig_T1 та dig_P1 не можуть дорівнювати 0 або 0xFFFF */
    if ((dev->calib.dig_T1 == 0x0000U) || (dev->calib.dig_T1 == 0xFFFFU) ||
        (dev->calib.dig_P1 == 0x0000U) || (dev->calib.dig_P1 == 0xFFFFU)) {
        return BMP280_ERR_CRC_MISMATCH;
    }

    return BMP280_OK;
}

bmp280_status_t bmp280_init(bmp280_handle_t *dev, const bmp280_bus_t *bus) {
    if ((dev == NULL) || (bus == NULL) || (bus->read == NULL) || (bus->write == NULL)) {
        return BMP280_ERR_NULL_PTR;
    }

    dev->bus = *bus;
    dev->state = BMP280_STATE_UNINITIALIZED;
    dev->t_fine = 0;
    dev->error_count = 0;
    dev->recovery_count = 0;

    /* 1. Перевірка Chip ID */
    uint8_t chip_id = 0x00U;
    bmp280_status_t status = dev->bus.read(dev->bus.dev_addr, BMP280_REG_CHIP_ID, &chip_id, 1U);
    if (status != BMP280_OK) {
        dev->state = BMP280_STATE_RECOVERY;
        return status;
    }

    if (chip_id != BMP280_CHIP_ID_VALUE) {
        dev->state = BMP280_STATE_FATAL_ERROR;
        return BMP280_ERR_INVALID_ID;
    }

    /* 2. Програмне скидання чипа */
    dev->state = BMP280_STATE_RESETTING;
    uint8_t rst_cmd = BMP280_SOFT_RESET_CMD;
    status = dev->bus.write(dev->bus.dev_addr, BMP280_REG_RESET, &rst_cmd, 1U);
    if (status != BMP280_OK) {
        return status;
    }

    if (dev->bus.delay_ms != NULL) {
        dev->bus.delay_ms(10U); /* Очікування POR (Power-on Reset) */
    }

    /* 3. Зчитування фабричних коефіцієнтів NVM */
    dev->state = BMP280_STATE_READING_NVM;
    status = read_calibration_nvm(dev);
    if (status != BMP280_OK) {
        dev->state = BMP280_STATE_FATAL_ERROR;
        return status;
    }

    dev->state = BMP280_STATE_IDLE;
    return BMP280_OK;
}

bmp280_status_t bmp280_configure(bmp280_handle_t *dev,
                                 bmp280_osr_t osr_t,
                                 bmp280_osr_t osr_p,
                                 bmp280_mode_t mode,
                                 bmp280_filter_t filter,
                                 bmp280_standby_t standby) {
    if (dev == NULL) {
        return BMP280_ERR_NULL_PTR;
    }

    dev->state = BMP280_STATE_CONFIGURING;

    /* Конфігурація регістра CONFIG (0xF5) */
    uint8_t config_reg = (uint8_t)(((uint8_t)standby << 5) | ((uint8_t)filter << 2));
    bmp280_status_t status = dev->bus.write(dev->bus.dev_addr, BMP280_REG_CONFIG, &config_reg, 1U);
    if (status != BMP280_OK) {
        return status;
    }

    /* Конфігурація регістра CTRL_MEAS (0xF4) */
    uint8_t ctrl_meas = (uint8_t)(((uint8_t)osr_t << 5) | ((uint8_t)osr_p << 2) | (uint8_t)mode);
    status = dev->bus.write(dev->bus.dev_addr, BMP280_REG_CTRL_MEAS, &ctrl_meas, 1U);
    if (status != BMP280_OK) {
        return status;
    }

    dev->state = BMP280_STATE_IDLE;
    return BMP280_OK;
}

/* ── Математичне ядро компенсації (Fixed-point Q-format) ───────────────────── */
bmp280_status_t bmp280_compensate(bmp280_handle_t *dev, const uint8_t *raw_6b, bmp280_sample_t *out_sample) {
    if ((dev == NULL) || (raw_6b == NULL) || (out_sample == NULL)) {
        return BMP280_ERR_NULL_PTR;
    }

    /* 1. Розпаковка 20-бітних даних тиску та температури з 6 байтів burst read */
    int32_t adc_P = (int32_t)((((uint32_t)raw_6b[0]) << 12) |
                             (((uint32_t)raw_6b[1]) << 4)  |
                             (((uint32_t)raw_6b[2]) >> 4));

    int32_t adc_T = (int32_t)((((uint32_t)raw_6b[3]) << 12) |
                             (((uint32_t)raw_6b[4]) << 4)  |
                             (((uint32_t)raw_6b[5]) >> 4));

    /* 2. Компенсація температури (32-бітна цілочисельна арифметика) */
    int32_t var1_T = ((((adc_T >> 3) - ((int32_t)dev->calib.dig_T1 << 1))) * ((int32_t)dev->calib.dig_T2)) >> 11;
    int32_t var2_T = (((((adc_T >> 4) - ((int32_t)dev->calib.dig_T1)) *
                       ((adc_T >> 4) - ((int32_t)dev->calib.dig_T1))) >> 12) *
                      ((int32_t)dev->calib.dig_T3)) >> 14;

    dev->t_fine = var1_T + var2_T;
    out_sample->temperature_centidegrees = (dev->t_fine * 5 + 128) >> 8;

    /* 3. Компенсація тиску (64-бітна цілочисельна арифметика для запобігання переповненню) */
    int64_t var1_P = ((int64_t)dev->t_fine) - 128000;
    int64_t var2_P = var1_P * var1_P * (int64_t)dev->calib.dig_P6;
    var2_P = var2_P + ((var1_P * (int64_t)dev->calib.dig_P5) << 17);
    var2_P = var2_P + (((int64_t)dev->calib.dig_P4) << 35);
    var1_P = ((var1_P * var1_P * (int64_t)dev->calib.dig_P3) >> 8) +
             ((var1_P * (int64_t)dev->calib.dig_P2) << 12);
    var1_P = (((((int64_t)1) << 47) + var1_P)) * ((int64_t)dev->calib.dig_P1) >> 33;

    if (var1_P == 0) {
        out_sample->pressure_pascals = 0;
        out_sample->pressure_q24_8 = 0;
        out_sample->valid = false;
        return BMP280_ERR_OVERFLOW;
    }

    int64_t p = 1048576 - adc_P;
    p = (((p << 31) - var2_P) * 3125) / var1_P;
    var1_P = (((int64_t)dev->calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2_P = (((int64_t)dev->calib.dig_P8) * p) >> 19;

    p = ((p + var1_P + var2_P) >> 8) + (((int64_t)dev->calib.dig_P7) << 4);

    out_sample->pressure_q24_8 = (uint32_t)p;
    out_sample->pressure_pascals = (uint32_t)(p >> 8);
    out_sample->valid = true;

    return BMP280_OK;
}

bmp280_status_t bmp280_read_sync(bmp280_handle_t *dev, bmp280_sample_t *sample) {
    if ((dev == NULL) || (sample == NULL)) {
        return BMP280_ERR_NULL_PTR;
    }

    dev->state = BMP280_STATE_MEASURING;
    uint8_t raw_data[BMP280_BURST_DATA_SIZE];

    /* Атомарний Burst Read 6 байтів починаючи з регістра 0xF7 (PRESS_MSB) */
    bmp280_status_t status = dev->bus.read(dev->bus.dev_addr, BMP280_REG_PRESS_MSB, raw_data, BMP280_BURST_DATA_SIZE);
    if (status != BMP280_OK) {
        dev->error_count++;
        dev->state = BMP280_STATE_RECOVERY;
        return status;
    }

    dev->state = BMP280_STATE_COMPENSATING;
    status = bmp280_compensate(dev, raw_data, sample);
    if (status == BMP280_OK) {
        dev->last_sample = *sample;
        dev->state = BMP280_STATE_IDLE;
    }
    return status;
}

bmp280_status_t bmp280_start_read_async_dma(bmp280_handle_t *dev) {
    if ((dev == NULL) || (dev->bus.read_dma_start == NULL)) {
        return BMP280_ERR_NULL_PTR;
    }

    if (dev->state == BMP280_STATE_BURST_READ_DMA) {
        return BMP280_ERR_BUSY;
    }

    dev->state = BMP280_STATE_BURST_READ_DMA;
    bmp280_status_t status = dev->bus.read_dma_start(dev->bus.dev_addr,
                                                     BMP280_REG_PRESS_MSB,
                                                     dev->dma_rx_buf,
                                                     BMP280_BURST_DATA_SIZE);
    if (status != BMP280_OK) {
        dev->error_count++;
        dev->state = BMP280_STATE_RECOVERY;
    }
    return status;
}

void bmp280_dma_complete_callback(bmp280_handle_t *dev) {
    if (dev == NULL) {
        return;
    }

    dev->state = BMP280_STATE_COMPENSATING;
    bmp280_sample_t sample;
    bmp280_status_t status = bmp280_compensate(dev, dev->dma_rx_buf, &sample);
    if (status == BMP280_OK) {
        dev->last_sample = sample;
        dev->state = BMP280_STATE_IDLE;
    } else {
        dev->error_count++;
        dev->state = BMP280_STATE_RECOVERY;
    }
}

bmp280_status_t bmp280_recover_bus(bmp280_handle_t *dev) {
    if (dev == NULL) {
        return BMP280_ERR_NULL_PTR;
    }

    dev->state = BMP280_STATE_RECOVERY;
    dev->recovery_count++;

    if (dev->bus.bus_recover != NULL) {
        dev->bus.bus_recover();
    }

    if (dev->bus.delay_ms != NULL) {
        dev->bus.delay_ms(15U);
    }

    /* Повторна спроба ініціалізації */
    return bmp280_init(dev, &dev->bus);
}
