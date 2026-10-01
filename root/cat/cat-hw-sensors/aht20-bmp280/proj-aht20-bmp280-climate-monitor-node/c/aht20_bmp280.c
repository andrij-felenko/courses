#include "aht20_bmp280.h"

/* Регістри та команди AHT20 */
#define AHT20_CMD_INIT          0xBE
#define AHT20_CMD_TRIGGER       0xAC
#define AHT20_CMD_SOFT_RESET    0xBA
#define AHT20_STATUS_BUSY_BIT   0x80
#define AHT20_STATUS_CALIB_BIT  0x08
#define AHT20_MEASURE_DELAY_MS  80

/* Регістри та команди BMP280 */
#define BMP280_REG_CHIP_ID      0xD0
#define BMP280_REG_RESET        0xE0
#define BMP280_REG_STATUS       0xF3
#define BMP280_REG_CTRL_MEAS    0xF4
#define BMP280_REG_CONFIG       0xF5
#define BMP280_REG_PRESS_MSB    0xF7
#define BMP280_REG_CALIB_START  0x88
#define BMP280_CHIP_ID_VALUE    0x58
#define BMP280_RESET_VALUE      0xB6

/**
 * @brief Розрахунок контрольної суми CRC-8 для даних AHT20.
 * Poly: 0x31 (x^8 + x^5 + x^4 + 1), Init: 0xFF.
 */
static uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/**
 * @brief Математична компенсація температури для BMP280 за формулою Bosch.
 */
static float bmp280_compensate_temp(int32_t adc_T, bmp280_calib_param_t *calib, int32_t *t_fine) {
    int32_t var1 = ((((adc_T >> 3) - ((int32_t)calib->dig_T1 << 1))) * ((int32_t)calib->dig_T2)) >> 11;
    int32_t var2 = (((((adc_T >> 4) - ((int32_t)calib->dig_T1)) * ((adc_T >> 4) - ((int32_t)calib->dig_T1))) >> 12) * ((int32_t)calib->dig_T3)) >> 14;
    *t_fine = var1 + var2;
    float t = (*t_fine * 5 + 128) >> 8;
    return t / 100.0f;
}

/**
 * @brief Математична компенсація атмосферного тиску для BMP280 за формулою Bosch.
 */
static float bmp280_compensate_press(int32_t adc_P, bmp280_calib_param_t *calib, int32_t t_fine) {
    int64_t var1, var2, p;
    var1 = ((int64_t)t_fine) - 128000;
    var2 = var1 * var1 * (int64_t)calib->dig_P6;
    var2 = var2 + ((var1 * (int64_t)calib->dig_P5) << 17);
    var2 = var2 + (((int64_t)calib->dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)calib->dig_P3) >> 8) + ((var1 * (int64_t)calib->dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)calib->dig_P1) >> 33;

    if (var1 == 0) {
        return 0.0f; /* Запобігання діленню на нуль */
    }

    p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)calib->dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)calib->dig_P8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (((int64_t)calib->dig_P7) << 4);

    return (float)p / 25600.0f; /* Переведення фіксованої кратності в гПа */
}

/* Ініціалізація медіанного фільтра */
void median_filter_init(median_filter_t *filter) {
    if (!filter) return;
    filter->count = 0;
    filter->index = 0;
    for (uint8_t i = 0; i < MEDIAN_WINDOW_SIZE; i++) {
        filter->buffer[i] = 0.0f;
    }
}

/* Оновлення медіанного фільтра значенням відліку */
float median_filter_update(median_filter_t *filter, float sample) {
    if (!filter) return sample;

    filter->buffer[filter->index] = sample;
    filter->index = (filter->index + 1) % MEDIAN_WINDOW_SIZE;
    if (filter->count < MEDIAN_WINDOW_SIZE) {
        filter->count++;
    }

    /* Локальна копія буфера для сортування */
    float sorted[MEDIAN_WINDOW_SIZE];
    for (uint8_t i = 0; i < filter->count; i++) {
        sorted[i] = filter->buffer[i];
    }

    /* Просте сортування методом бульбашки для малого масиву */
    for (uint8_t i = 0; i < filter->count - 1; i++) {
        for (uint8_t j = 0; j < filter->count - i - 1; j++) {
            if (sorted[j] > sorted[j + 1]) {
                float temp = sorted[j];
                sorted[j] = sorted[j + 1];
                sorted[j + 1] = temp;
            }
        }
    }

    return sorted[filter->count / 2];
}

/* Зчитати калібрувальні коефіцієнти BMP280 */
static sensor_status_t bmp280_read_calibration(sensor_driver_t *driver) {
    uint8_t calib_buf[24];
    sensor_status_t st = driver->i2c_read(BMP280_I2C_ADDR, BMP280_REG_CALIB_START, calib_buf, 24);
    if (st != SENSOR_OK) {
        return SENSOR_ERR_I2C;
    }

    driver->bmp280_calib.dig_T1 = (uint16_t)(calib_buf[1] << 8 | calib_buf[0]);
    driver->bmp280_calib.dig_T2 = (int16_t)(calib_buf[3] << 8 | calib_buf[2]);
    driver->bmp280_calib.dig_T3 = (int16_t)(calib_buf[5] << 8 | calib_buf[4]);
    driver->bmp280_calib.dig_P1 = (uint16_t)(calib_buf[7] << 8 | calib_buf[6]);
    driver->bmp280_calib.dig_P2 = (int16_t)(calib_buf[9] << 8 | calib_buf[8]);
    driver->bmp280_calib.dig_P3 = (int16_t)(calib_buf[11] << 8 | calib_buf[10]);
    driver->bmp280_calib.dig_P4 = (int16_t)(calib_buf[13] << 8 | calib_buf[12]);
    driver->bmp280_calib.dig_P5 = (int16_t)(calib_buf[15] << 8 | calib_buf[14]);
    driver->bmp280_calib.dig_P6 = (int16_t)(calib_buf[17] << 8 | calib_buf[16]);
    driver->bmp280_calib.dig_P7 = (int16_t)(calib_buf[19] << 8 | calib_buf[18]);
    driver->bmp280_calib.dig_P8 = (int16_t)(calib_buf[21] << 8 | calib_buf[20]);
    driver->bmp280_calib.dig_P9 = (int16_t)(calib_buf[23] << 8 | calib_buf[22]);

    return SENSOR_OK;
}

/* Ініціалізація модуля */
sensor_status_t sensor_driver_init(sensor_driver_t *driver,
                                   i2c_read_fn read_fn,
                                   i2c_write_fn write_fn,
                                   uint32_t poll_interval_ms) {
    if (!driver || !read_fn || !write_fn) {
        return SENSOR_ERR_PARAM;
    }

    driver->i2c_read = read_fn;
    driver->i2c_write = write_fn;
    driver->poll_interval_ms = poll_interval_ms;
    driver->last_poll_ms = 0;
    driver->measure_start_ms = 0;
    driver->state = SENSOR_FSM_IDLE;
    driver->is_initialized = false;
    driver->new_data_available = false;

    median_filter_init(&driver->temp_filter);
    median_filter_init(&driver->hum_filter);
    median_filter_init(&driver->press_filter);

    /* Перевірка наявності BMP280 за CHIP ID */
    uint8_t chip_id = 0;
    if (driver->i2c_read(BMP280_I2C_ADDR, BMP280_REG_CHIP_ID, &chip_id, 1) != SENSOR_OK ||
        chip_id != BMP280_CHIP_ID_VALUE) {
        return SENSOR_ERR_I2C;
    }

    /* Зчитування калібрувань BMP280 */
    if (bmp280_read_calibration(driver) != SENSOR_OK) {
        return SENSOR_ERR_CALIB;
    }

    /* Перевірка стану AHT20 та ініціалізація при потребі */
    uint8_t aht_status = 0;
    if (driver->i2c_read(AHT20_I2C_ADDR, 0x00, &aht_status, 1) == SENSOR_OK) {
        if ((aht_status & AHT20_STATUS_CALIB_BIT) == 0) {
            uint8_t init_cmd[2] = {0x08, 0x00};
            driver->i2c_write(AHT20_I2C_ADDR, AHT20_CMD_INIT, init_cmd, 2);
        }
    }

    driver->is_initialized = true;
    return SENSOR_OK;
}

/* Скінченний автомат обробки вимірювань (FSM) */
sensor_status_t sensor_driver_update_fsm(sensor_driver_t *driver, uint32_t current_time_ms) {
    if (!driver || !driver->is_initialized) {
        return SENSOR_ERR_PARAM;
    }

    switch (driver->state) {
        case SENSOR_FSM_IDLE: {
            if (current_time_ms - driver->last_poll_ms >= driver->poll_interval_ms ||
                driver->last_poll_ms == 0) {
                driver->state = SENSOR_FSM_START_MEASURE;
            }
            break;
        }

        case SENSOR_FSM_START_MEASURE: {
            /* 1. Запуск вимірювання AHT20 */
            uint8_t aht_cmd[2] = {0x33, 0x00};
            if (driver->i2c_write(AHT20_I2C_ADDR, AHT20_CMD_TRIGGER, aht_cmd, 2) != SENSOR_OK) {
                driver->state = SENSOR_FSM_ERROR;
                return SENSOR_ERR_I2C;
            }

            /* 2. Запуск вимірювання BMP280 у режим Forced Mode (osrs_t x2, osrs_p x16, mode forced) */
            uint8_t bmp_ctrl = (2 << 5) | (5 << 2) | 0x01;
            if (driver->i2c_write(BMP280_I2C_ADDR, BMP280_REG_CTRL_MEAS, &bmp_ctrl, 1) != SENSOR_OK) {
                driver->state = SENSOR_FSM_ERROR;
                return SENSOR_ERR_I2C;
            }

            driver->measure_start_ms = current_time_ms;
            driver->state = SENSOR_FSM_WAIT_MEASURE;
            break;
        }

        case SENSOR_FSM_WAIT_MEASURE: {
            /* Очікування без блокування виконання головного циклу */
            if (current_time_ms - driver->measure_start_ms >= AHT20_MEASURE_DELAY_MS) {
                uint8_t bmp_status = 0;
                driver->i2c_read(BMP280_I2C_ADDR, BMP280_REG_STATUS, &bmp_status, 1);
                /* Якщо BMP280 завершив вимірювання (біт measuring == 0) */
                if ((bmp_status & 0x08) == 0) {
                    driver->state = SENSOR_FSM_READ_DATA;
                }
            }
            break;
        }

        case SENSOR_FSM_READ_DATA: {
            driver->state = SENSOR_FSM_PROCESS_DATA;
            break;
        }

        case SENSOR_FSM_PROCESS_DATA: {
            uint8_t aht_buf[7] = {0};
            uint8_t bmp_buf[6] = {0};

            /* Зчитування відліків AHT20 */
            if (driver->i2c_read(AHT20_I2C_ADDR, 0x00, aht_buf, 7) != SENSOR_OK) {
                driver->state = SENSOR_FSM_ERROR;
                return SENSOR_ERR_I2C;
            }

            /* Валідація контрольної суми CRC-8 для AHT20 */
            if (aht20_calculate_crc8(aht_buf, 6) != aht_buf[6]) {
                driver->state = SENSOR_FSM_ERROR;
                return SENSOR_ERR_CRC;
            }

            /* Зчитування відліків BMP280 */
            if (driver->i2c_read(BMP280_I2C_ADDR, BMP280_REG_PRESS_MSB, bmp_buf, 6) != SENSOR_OK) {
                driver->state = SENSOR_FSM_ERROR;
                return SENSOR_ERR_I2C;
            }

            /* 1. Декодування AHT20 */
            uint32_t raw_hum = ((uint32_t)aht_buf[1] << 12) | ((uint32_t)aht_buf[2] << 4) | ((uint32_t)aht_buf[3] >> 4);
            uint32_t raw_temp_aht = (((uint32_t)aht_buf[3] & 0x0F) << 16) | ((uint32_t)aht_buf[4] << 8) | (uint32_t)aht_buf[5];

            float hum_val = ((float)raw_hum / 1048576.0f) * 100.0f;
            float temp_aht_val = ((float)raw_temp_aht / 1048576.0f) * 200.0f - 50.0f;

            /* 2. Декодування та компенсація BMP280 */
            int32_t adc_P = ((int32_t)bmp_buf[0] << 12) | ((int32_t)bmp_buf[1] << 4) | ((int32_t)bmp_buf[2] >> 4);
            int32_t adc_T = ((int32_t)bmp_buf[3] << 12) | ((int32_t)bmp_buf[4] << 4) | ((int32_t)bmp_buf[5] >> 4);

            float temp_bmp_val = bmp280_compensate_temp(adc_T, &driver->bmp280_calib, &driver->bmp280_t_fine);
            float press_val = bmp280_compensate_press(adc_P, &driver->bmp280_calib, driver->bmp280_t_fine);

            /* 3. Усереднення температури з двох датчиків та медіанне фільтрування */
            float avg_temp = (temp_aht_val + temp_bmp_val) / 2.0f;

            driver->climate_data.temperature_c = median_filter_update(&driver->temp_filter, avg_temp);
            driver->climate_data.humidity_percent = median_filter_update(&driver->hum_filter, hum_val);
            driver->climate_data.pressure_hpa = median_filter_update(&driver->press_filter, press_val);
            driver->climate_data.valid = true;
            driver->climate_data.timestamp_ms = current_time_ms;

            driver->last_poll_ms = current_time_ms;
            driver->new_data_available = true;
            driver->state = SENSOR_FSM_IDLE;
            break;
        }

        case SENSOR_FSM_ERROR: {
            /* Відновлення після помилки: повторна спроба через 1000 мс */
            driver->climate_data.valid = false;
            if (current_time_ms - driver->last_poll_ms >= 1000) {
                driver->last_poll_ms = current_time_ms;
                driver->state = SENSOR_FSM_IDLE;
            }
            break;
        }
    }

    return SENSOR_OK;
}

/* Отримання підсумкових даних */
bool sensor_driver_get_climate(sensor_driver_t *driver, climate_data_t *out_data) {
    if (!driver || !out_data || !driver->new_data_available) {
        return false;
    }
    *out_data = driver->climate_data;
    driver->new_data_available = false;
    return true;
}
