#include "bme280.h"
#include <stdio.h>

/**
 * @file bme280.c
 * @brief Реалізація C-драйвера Bosch BME280.
 * 
 * Містить функціонал перевірки чип-ID (0x60), зчитування та десеріалізації 
 * 24-байтного й 7-байтного блоків калібрувальних даних із NVM, конфігурації 
 * оверсемплінгу в ctrl_hum (0xF2) та ctrl_meas (0xF4), тригерування Forced Mode,
 * пакетного читання 8 байтів сирих даних (0xF7..0xFE) та 32/64-бітну цілочисельну 
 * компенсацію з обчисленням проміжного значення t_fine.
 */

/* Внутрішня функція перетворення статусів I2C HAL у статуси BME280 */
static bme280_err_t map_hal_error(i2c_hal_err_t hal_err) {
    switch (hal_err) {
        case I2C_HAL_OK:
            return BME280_OK;
        case I2C_HAL_ERR_NULL_PTR:
            return BME280_ERR_NULL_PTR;
        case I2C_HAL_ERR_TIMEOUT:
            return BME280_ERR_TIMEOUT;
        default:
            return BME280_ERR_I2C;
    }
}

bme280_err_t bme280_init(bme280_t *dev, uint8_t i2c_addr) {
    if (dev == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    if (i2c_addr != BME280_I2C_ADDR_PRIM && i2c_addr != BME280_I2C_ADDR_SEC) {
        return BME280_ERR_INVALID_PARAM;
    }

    dev->i2c_addr = i2c_addr;
    dev->t_fine = 0;
    dev->osrs_t = BME280_OVERSAMPLING_1X;
    dev->osrs_p = BME280_OVERSAMPLING_1X;
    dev->osrs_h = BME280_OVERSAMPLING_1X;

    /* 1. Перевірка Chip ID пристрою */
    uint8_t chip_id = 0;
    i2c_hal_err_t hal_err = i2c_hal_read_reg(dev->i2c_addr, BME280_REG_CHIP_ID, &chip_id);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    if (chip_id != BME280_CHIP_ID_VALUE) {
        return BME280_ERR_INVALID_CHIP_ID;
    }

    /* 2. Програмне скидання давача для стабілізації регістрів */
    bme280_err_t err = bme280_soft_reset(dev);
    if (err != BME280_OK) {
        return err;
    }

    /* 3. Зчитування фабричних калібрувальних коефіцієнтів з NVM */
    err = bme280_read_calibration(dev);
    if (err != BME280_OK) {
        return err;
    }

    return BME280_OK;
}

bme280_err_t bme280_soft_reset(bme280_t *dev) {
    if (dev == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    i2c_hal_err_t hal_err = i2c_hal_write_reg(dev->i2c_addr, BME280_REG_RESET, BME280_RESET_CMD);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    /* Час стабілізації після скидання та оновлення NVM регістрів (мінімум 3 мс) */
    i2c_hal_delay_ms(10);

    /* Очікування обнулення прапорця im_update у status */
    uint8_t status = 0;
    uint32_t start_tick = i2c_hal_get_ticks_ms();
    while ((i2c_hal_get_ticks_ms() - start_tick) < 100) {
        hal_err = i2c_hal_read_reg(dev->i2c_addr, BME280_REG_STATUS, &status);
        if (hal_err == I2C_HAL_OK && (status & BME280_STATUS_IM_UPDATE_MSK) == 0) {
            return BME280_OK;
        }
        i2c_hal_delay_ms(2);
    }

    return BME280_ERR_TIMEOUT;
}

bme280_err_t bme280_read_calibration(bme280_t *dev) {
    if (dev == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    /*
     * ЗЧИТАННЯ БЛОКУ 1: 26 байтів з 0x88 по 0xA1 включно
     * Містить dig_T1..T3, dig_P1..P9 та dig_H1 у байті 0xA1.
     */
    uint8_t calib_b1[26];
    i2c_hal_err_t hal_err = i2c_hal_read_bytes(dev->i2c_addr, BME280_REG_DIG_T1_LSB, calib_b1, 26);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    /* Десеріалізація коефіцієнтів температури */
    dev->calib.dig_T1 = (uint16_t)((calib_b1[1] << 8) | calib_b1[0]);
    dev->calib.dig_T2 = (int16_t)((calib_b1[3] << 8) | calib_b1[2]);
    dev->calib.dig_T3 = (int16_t)((calib_b1[5] << 8) | calib_b1[4]);

    /* Десеріалізація коефіцієнтів тиску */
    dev->calib.dig_P1 = (uint16_t)((calib_b1[7] << 8) | calib_b1[6]);
    dev->calib.dig_P2 = (int16_t)((calib_b1[9] << 8) | calib_b1[8]);
    dev->calib.dig_P3 = (int16_t)((calib_b1[11] << 8) | calib_b1[10]);
    dev->calib.dig_P4 = (int16_t)((calib_b1[13] << 8) | calib_b1[12]);
    dev->calib.dig_P5 = (int16_t)((calib_b1[15] << 8) | calib_b1[14]);
    dev->calib.dig_P6 = (int16_t)((calib_b1[17] << 8) | calib_b1[16]);
    dev->calib.dig_P7 = (int16_t)((calib_b1[19] << 8) | calib_b1[18]);
    dev->calib.dig_P8 = (int16_t)((calib_b1[21] << 8) | calib_b1[20]);
    dev->calib.dig_P9 = (int16_t)((calib_b1[23] << 8) | calib_b1[22]);

    /* Калібрування вологості H1 знаходиться в останньому 25-му байті (0xA1 - 0x88 = 25) */
    dev->calib.dig_H1 = calib_b1[25];

    /*
     * ЗЧИТАННЯ БЛОКУ 2: 7 байтів з 0xE1 по 0xE7 включно
     * Містить dig_H2..H6.
     */
    uint8_t calib_b2[7];
    hal_err = i2c_hal_read_bytes(dev->i2c_addr, BME280_REG_DIG_H2_LSB, calib_b2, 7);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    dev->calib.dig_H2 = (int16_t)((calib_b2[1] << 8) | calib_b2[0]);
    dev->calib.dig_H3 = calib_b2[2];

    /*
     * Увага! У давачах Bosch BME280 коефіцієнти dig_H4 та dig_H5 розділені між 
     * регістрами 0xE4, 0xE5 та 0xE6:
     * - dig_H4 складається з 0xE4[7:0] (MSB) та 0xE5[3:0] (LSB)
     * - dig_H5 складається з 0xE6[7:0] (MSB) та 0xE5[7:4] (LSB)
     */
    dev->calib.dig_H4 = (int16_t)(((int8_t)calib_b2[3] << 4) | (calib_b2[4] & 0x0F));
    dev->calib.dig_H5 = (int16_t)(((int8_t)calib_b2[5] << 4) | ((calib_b2[4] >> 4) & 0x0F));
    dev->calib.dig_H6 = (int8_t)calib_b2[6];

    return BME280_OK;
}

bme280_err_t bme280_set_oversampling(bme280_t *dev,
                                    bme280_oversampling_t osrs_t,
                                    bme280_oversampling_t osrs_p,
                                    bme280_oversampling_t osrs_h) {
    if (dev == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    dev->osrs_t = osrs_t;
    dev->osrs_p = osrs_p;
    dev->osrs_h = osrs_h;

    return BME280_OK;
}

bme280_err_t bme280_trigger_forced_measurement(bme280_t *dev) {
    if (dev == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    /*
     * ВАЖЛИВА ОСОБЛИВІСТЬ BOSCH BME280:
     * Запис у регістр ctrl_hum (0xF2) набуває чинності ТІЛЬКИ після 
     * наступного запису в регістр ctrl_meas (0xF4).
     */
    uint8_t ctrl_hum = (uint8_t)(dev->osrs_h & 0x07);
    i2c_hal_err_t hal_err = i2c_hal_write_reg(dev->i2c_addr, BME280_REG_CTRL_HUM, ctrl_hum);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    /* Формуємо вміст ctrl_meas: osrs_t[7:5] | osrs_p[4:2] | mode[1:0] */
    uint8_t ctrl_meas = (uint8_t)(((dev->osrs_t & 0x07) << 5) |
                                  ((dev->osrs_p & 0x07) << 2) |
                                  (BME280_MODE_FORCED & 0x03));

    hal_err = i2c_hal_write_reg(dev->i2c_addr, BME280_REG_CTRL_MEAS, ctrl_meas);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    return BME280_OK;
}

bme280_err_t bme280_is_measuring(bme280_t *dev, bool *is_busy) {
    if (dev == NULL || is_busy == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    uint8_t status = 0;
    i2c_hal_err_t hal_err = i2c_hal_read_reg(dev->i2c_addr, BME280_REG_STATUS, &status);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    *is_busy = ((status & BME280_STATUS_MEASURING_MSK) != 0);
    return BME280_OK;
}

bme280_err_t bme280_read_raw_data(bme280_t *dev, bme280_raw_t *raw) {
    if (dev == NULL || raw == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    /*
     * ПАКЕТНЕ (BURST) ЗЧИТАННЯ 8 БАЙТІВ З 0xF7 ДО 0xFE:
     * 0xF7: press_msb  [19:12]
     * 0xF8: press_lsb  [11:4]
     * 0xF9: press_xlsb [3:0]
     * 0xFA: temp_msb   [19:12]
     * 0xFB: temp_lsb   [11:4]
     * 0xFC: temp_xlsb  [3:0]
     * 0xFD: hum_msb    [15:8]
     * 0xFE: hum_lsb    [7:0]
     */
    uint8_t data[8];
    i2c_hal_err_t hal_err = i2c_hal_read_bytes(dev->i2c_addr, BME280_REG_PRESS_MSB, data, 8);
    if (hal_err != I2C_HAL_OK) {
        return map_hal_error(hal_err);
    }

    raw->raw_pressure    = ((uint32_t)data[0] << 12) | ((uint32_t)data[1] << 4) | ((uint32_t)data[2] >> 4);
    raw->raw_temperature = ((uint32_t)data[3] << 12) | ((uint32_t)data[4] << 4) | ((uint32_t)data[5] >> 4);
    raw->raw_humidity    = ((uint32_t)data[6] << 8)  | (uint32_t)data[7];

    return BME280_OK;
}

/**
 * @brief Обчислення компенсованої температури за 32-бітною цілочисельною формулою Bosch.
 * @details Одночасно розраховує проміжне значення t_fine, необхідне для тиску й вологості.
 */
static int32_t compensate_temperature(bme280_t *dev, uint32_t adc_T) {
    int32_t var1, var2, T;
    const bme280_calib_t *cal = &dev->calib;

    var1 = ((((int32_t)(adc_T >> 3)) - ((int32_t)cal->dig_T1 << 1)) * ((int32_t)cal->dig_T2)) >> 11;
    var2 = (((((int32_t)(adc_T >> 4)) - ((int32_t)cal->dig_T1)) *
             (((int32_t)(adc_T >> 4)) - ((int32_t)cal->dig_T1))) >> 12) * ((int32_t)cal->dig_T3) >> 14;

    dev->t_fine = var1 + var2;
    T = (dev->t_fine * 5 + 128) >> 8;
    return T; /* Повертає температуру в 0.01 °C */
}

/**
 * @brief Обчислення компенсованого атмосферного тиску за 64-бітною цілочисельною формулою Bosch.
 */
static uint32_t compensate_pressure(bme280_t *dev, uint32_t adc_P) {
    int64_t var1, var2, p;
    const bme280_calib_t *cal = &dev->calib;

    var1 = ((int64_t)dev->t_fine) - 128000;
    var2 = var1 * var1 * (int64_t)cal->dig_P6;
    var2 = var2 + ((var1 * (int64_t)cal->dig_P5) << 17);
    var2 = var2 + (((int64_t)cal->dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)cal->dig_P3) >> 8) + ((var1 * (int64_t)cal->dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)cal->dig_P1) >> 33;

    if (var1 == 0) {
        return 0; /* Запобігання діленню на нуль у разі збою */
    }

    p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)cal->dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)cal->dig_P8) * p) >> 19;

    p = ((p + var1 + var2) >> 8) + (((int64_t)cal->dig_P7) << 4);
    return (uint32_t)(p >> 8); /* Повертає тиск у Паскалях (Па) */
}

/**
 * @brief Обчислення компенсованої відносної вологості за 32-бітною цілочисельною формулою Bosch.
 */
static uint32_t compensate_humidity(bme280_t *dev, uint32_t adc_H) {
    int32_t v_x1_u32r;
    const bme280_calib_t *cal = &dev->calib;

    v_x1_u32r = (dev->t_fine - ((int32_t)76800));

    v_x1_u32r = (((((((int32_t)adc_H << 14) - (((int32_t)cal->dig_H4) << 20) -
                     (((int32_t)cal->dig_H5) * v_x1_u32r)) + ((int32_t)16384)) >> 15) *
                  (((((((v_x1_u32r * ((int32_t)cal->dig_H6)) >> 10) *
                       (((v_x1_u32r * ((int32_t)cal->dig_H5)) >> 11) + ((int32_t)32768))) >> 10) +
                     ((int32_t)2097152)) * ((int32_t)cal->dig_H2) + 8192) >> 14)));

    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) *
                               ((int32_t)cal->dig_H3)) >> 4));

    v_x1_u32r = (v_x1_u32r < 0 ? 0 : v_x1_u32r);
    v_x1_u32r = (v_x1_u32r > 419430400 ? 419430400 : v_x1_u32r);

    return (uint32_t)(v_x1_u32r >> 12); /* Повертає вологість у форматі Q22.10 (%RH * 1024) */
}

bme280_err_t bme280_compensate_data(bme280_t *dev, const bme280_raw_t *raw, bme280_data_t *data) {
    if (dev == NULL || raw == NULL || data == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    /*
     * КРОК 1: Першою ОБОВ'ЯЗКОВО розраховується температура, оскільки 
     * вона обчислює та оновлює проміжне значення dev->t_fine.
     */
    data->temperature_degc_x100 = compensate_temperature(dev, raw->raw_temperature);

    /* КРОК 2: Розрахунок тиску та вологості на основі отриманого t_fine */
    data->pressure_pa = compensate_pressure(dev, raw->raw_pressure);
    data->humidity_rh_x1024 = compensate_humidity(dev, raw->raw_humidity);

    /* КРОК 3: Обчислення зручних плаваючих значень у фізичних одиницях */
    data->temperature_degc = (float)data->temperature_degc_x100 / 100.0f;
    data->pressure_hpa     = (float)data->pressure_pa / 100.0f;
    data->humidity_rh       = (float)data->humidity_rh_x1024 / 1024.0f;

    return BME280_OK;
}

bme280_err_t bme280_perform_forced_measurement(bme280_t *dev, bme280_data_t *data) {
    if (dev == NULL || data == NULL) {
        return BME280_ERR_NULL_PTR;
    }

    /* 1. Ініціалізація вимірювального циклу в Forced Mode */
    bme280_err_t err = bme280_trigger_forced_measurement(dev);
    if (err != BME280_OK) {
        return err;
    }

    /*
     * 2. Очікування закінчення квантування АЦП за прапорцем measuring у status.
     * Час квантування залежить від коефіцієнтів оверсемплінгу (типово 10..20 мс).
     */
    bool is_busy = true;
    uint32_t start_time = i2c_hal_get_ticks_ms();
    while ((i2c_hal_get_ticks_ms() - start_time) < 100) {
        err = bme280_is_measuring(dev, &is_busy);
        if (err != BME280_OK) {
            return err;
        }
        if (!is_busy) {
            break;
        }
        i2c_hal_delay_ms(2);
    }

    if (is_busy) {
        return BME280_ERR_TIMEOUT;
    }

    /* 3. Зчитування 8-байтного блоку сирих вибірок АЦП */
    bme280_raw_t raw;
    err = bme280_read_raw_data(dev, &raw);
    if (err != BME280_OK) {
        return err;
    }

    /* 4. Виконання компенсаційного розрахунку */
    return bme280_compensate_data(dev, &raw, data);
}

const char* bme280_err_to_str(bme280_err_t err) {
    switch (err) {
        case BME280_OK:
            return "Успішно (OK)";
        case BME280_ERR_NULL_PTR:
            return "Передано нульовий вказівник (NULL)";
        case BME280_ERR_INVALID_CHIP_ID:
            return "Недійсний Chip ID пристрою (очікувалося 0x60)";
        case BME280_ERR_I2C:
            return "Помилка передачі по шині I2C";
        case BME280_ERR_TIMEOUT:
            return "Перевищено таймаут очікування давача";
        case BME280_ERR_INVALID_PARAM:
            return "Некоректний конфігураційний параметр";
        default:
            return "Невідома помилка";
    }
}
