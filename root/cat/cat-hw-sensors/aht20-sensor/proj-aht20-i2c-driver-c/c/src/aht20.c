#include "aht20.h"
#include <stdio.h>

/**
 * @file aht20.c
 * @brief Реалізація процедурного C-драйвера цифрового давача температури й вологості AHT20.
 * 
 * Включає керування вимірювальним циклом, перевірку статусного біта готовності (Busy Bit),
 * обчислення CRC-8 (поліном 0x31, початкове значення 0xFF), бітове розпакування 20-бітних
 * вибірок вологості й температури з 7-байтового потоку та їх математичний перерахунок у % RH і °C.
 */

uint8_t aht20_calc_crc8(const uint8_t *data, size_t len) {
    if (!data) return 0;

    uint8_t crc = AHT20_CRC8_INIT_VAL;

    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ AHT20_CRC8_POLYNOMIAL;
            } else {
                crc = (crc << 1);
            }
        }
    }

    return crc;
}

aht20_err_t aht20_init(aht20_t *dev, const i2c_bus_t *i2c) {
    if (!dev || !i2c || !i2c->write || !i2c->read || !i2c->delay_ms || !i2c->get_ticks_ms) {
        return AHT20_ERR_INVALID_PARAM;
    }

    dev->i2c = i2c;
    dev->i2c_addr = AHT20_I2C_ADDR;
    dev->is_initialized = false;

    /* КРОК 1: Затримка стабілізації живлення після подачі напруги (понад 100 мс) */
    dev->i2c->delay_ms(AHT20_DELAY_POWER_ON_MS);

    /* КРОК 2: Зчитування статусного байта для перевірки прапорця калібрування */
    uint8_t status = 0;
    if (dev->i2c->read(dev->i2c_addr, &status, 1) != I2C_SUCCESS) {
        return AHT20_ERR_I2C;
    }

    /*
     * Перевірка біта 3 (0x08): якщо він дорівнює 0, сенсор не відкалібрований.
     * У цьому випадку надсилається команда ініціалізації 0xBE з параметрами 0x08 та 0x00.
     */
    if ((status & AHT20_STATUS_CALIBRATED_MASK) == 0) {
        uint8_t init_cmd[3] = {AHT20_CMD_INIT, AHT20_CMD_INIT_ARG1, AHT20_CMD_INIT_ARG2};
        if (dev->i2c->write(dev->i2c_addr, init_cmd, sizeof(init_cmd)) != I2C_SUCCESS) {
            return AHT20_ERR_I2C;
        }

        dev->i2c->delay_ms(10);

        /* Повторне зчитування статусу після команди ініціалізації */
        if (dev->i2c->read(dev->i2c_addr, &status, 1) != I2C_SUCCESS) {
            return AHT20_ERR_I2C;
        }

        if ((status & AHT20_STATUS_CALIBRATED_MASK) == 0) {
            return AHT20_ERR_NOT_CALIBRATED;
        }
    }

    dev->is_initialized = true;
    return AHT20_OK;
}

aht20_err_t aht20_soft_reset(aht20_t *dev) {
    if (!dev || !dev->i2c) {
        return AHT20_ERR_INVALID_PARAM;
    }

    uint8_t reset_cmd = AHT20_CMD_SOFT_RESET;
    if (dev->i2c->write(dev->i2c_addr, &reset_cmd, 1) != I2C_SUCCESS) {
        return AHT20_ERR_I2C;
    }

    /* Витримка часового інтервалу на перезавантаження внутрішніх регістрів чипа */
    dev->i2c->delay_ms(AHT20_DELAY_SOFT_RESET_MS);
    return AHT20_OK;
}

aht20_err_t aht20_start_measurement(aht20_t *dev) {
    if (!dev || !dev->is_initialized) {
        return AHT20_ERR_INVALID_PARAM;
    }

    /* Надсилання тригера АЦП: 0xAC, 0x33, 0x00 */
    uint8_t trigger_cmd[3] = {
        AHT20_CMD_TRIGGER_MEASURE,
        AHT20_CMD_TRIGGER_ARG1,
        AHT20_CMD_TRIGGER_ARG2
    };

    if (dev->i2c->write(dev->i2c_addr, trigger_cmd, sizeof(trigger_cmd)) != I2C_SUCCESS) {
        return AHT20_ERR_I2C;
    }

    return AHT20_OK;
}

aht20_err_t aht20_is_busy(aht20_t *dev, bool *is_busy) {
    if (!dev || !is_busy || !dev->i2c) {
        return AHT20_ERR_INVALID_PARAM;
    }

    uint8_t status = 0;
    if (dev->i2c->read(dev->i2c_addr, &status, 1) != I2C_SUCCESS) {
        return AHT20_ERR_I2C;
    }

    *is_busy = ((status & AHT20_STATUS_BUSY_MASK) != 0);
    return AHT20_OK;
}

aht20_err_t aht20_read_data(aht20_t *dev, aht20_data_t *data) {
    if (!dev || !data || !dev->is_initialized) {
        return AHT20_ERR_INVALID_PARAM;
    }

    /* КРОК 1: Запуск вимірювального циклу надсиланням команди 0xAC 0x33 0x00 */
    aht20_err_t err = aht20_start_measurement(dev);
    if (err != AHT20_OK) {
        return err;
    }

    /* КРОК 2: Базова витримка часу АЦП-перетворення (80 мс) */
    dev->i2c->delay_ms(AHT20_DELAY_MEASUREMENT_MS);

    /* КРОК 3: Опитування статусного біта готовності (Busy Bit, bit 7) з тайм-аутом */
    uint32_t start_ticks = dev->i2c->get_ticks_ms();
    bool busy = true;

    while (busy) {
        err = aht20_is_busy(dev, &busy);
        if (err != AHT20_OK) {
            return err;
        }

        if (busy) {
            if ((dev->i2c->get_ticks_ms() - start_ticks) > AHT20_TIMEOUT_BUSY_POLL_MS) {
                return AHT20_ERR_TIMEOUT;
            }
            dev->i2c->delay_ms(2);
        }
    }

    /*
     * КРОК 4: Зчитування 7-байтового пакета даних з AHT20:
     * - Байт 0: Статус (State byte)
     * - Байт 1: Humidity [19:12]
     * - Байт 2: Humidity [11:4]
     * - Байт 3: High nibble = Humidity [3:0], Low nibble = Temperature [19:16]
     * - Байт 4: Temperature [15:8]
     * - Байт 5: Temperature [7:0]
     * - Байт 6: Контрольна сума CRC-8 (обчислена для байтів 0..5)
     */
    uint8_t buffer[7] = {0};
    if (dev->i2c->read(dev->i2c_addr, buffer, sizeof(buffer)) != I2C_SUCCESS) {
        return AHT20_ERR_I2C;
    }

    /* КРОК 5: Верифікація цілісності прийнятого пакета за допомогою CRC-8 */
    uint8_t calculated_crc = aht20_calc_crc8(buffer, 6);
    data->crc_ok = (calculated_crc == buffer[6]);

    if (!data->crc_ok) {
        return AHT20_ERR_CRC;
    }

    /*
     * КРОК 6: Бітове розпакування 20-бітних вибірок АЦП з байтового потоку:
     * 
     * Raw Humidity (20 бітів):
     * - buffer[1] зміщується на 12 бітів вліво (займає біти 19..12)
     * - buffer[2] зміщується на 4 біти вліво (займає біти 11..4)
     * - buffer[3] зміщується на 4 біти вправо для виділення старшого напівбайта (біти 3..0)
     */
    data->raw_humidity = ((uint32_t)buffer[1] << 12) |
                         ((uint32_t)buffer[2] << 4)  |
                         ((uint32_t)buffer[3] >> 4);

    /*
     * Raw Temperature (20 бітів):
     * - (buffer[3] & 0x0F) виділяє молодший напівбайт і зміщується на 16 бітів вліво (біти 19..16)
     * - buffer[4] зміщується на 8 бітів вліво (біти 15..8)
     * - buffer[5] додається без зміщення (біти 7..0)
     */
    data->raw_temp = (((uint32_t)buffer[3] & 0x0F) << 16) |
                     ((uint32_t)buffer[4] << 8)         |
                     ((uint32_t)buffer[5]);

    /*
     * КРОК 7: Математичний перерахунок вибірок АЦП у фізичні величини:
     * 
     * Формула відносної вологості (% RH):
     * RH (%) = (Raw_Humidity / 2^20) * 100% = (Raw_Humidity / 1048576) * 100%
     */
    data->humidity_rh = ((float)data->raw_humidity / 1048576.0f) * 100.0f;

    /*
     * Формула температури (°C):
     * T (°C) = (Raw_Temp / 2^20) * 200 - 50 = (Raw_Temp / 1048576) * 200 - 50
     */
    data->temperature_c = ((float)data->raw_temp / 1048576.0f) * 200.0f - 50.0f;

    return AHT20_OK;
}

const char* aht20_err_to_string(aht20_err_t err) {
    switch (err) {
        case AHT20_OK:
            return "Успішне виконання (AHT20_OK)";
        case AHT20_ERR_I2C:
            return "Помилка зв'язку по шині I2C (AHT20_ERR_I2C)";
        case AHT20_ERR_TIMEOUT:
            return "Перевищено тайм-аут очікування готовності (AHT20_ERR_TIMEOUT)";
        case AHT20_ERR_NOT_CALIBRATED:
            return "Давач не відкалібрований (AHT20_ERR_NOT_CALIBRATED)";
        case AHT20_ERR_CRC:
            return "Невідповідність контрольної суми CRC-8 (AHT20_ERR_CRC)";
        case AHT20_ERR_INVALID_PARAM:
            return "Некоректний параметр або NULL-вказівник (AHT20_ERR_INVALID_PARAM)";
        default:
            return "Невідома помилка";
    }
}
