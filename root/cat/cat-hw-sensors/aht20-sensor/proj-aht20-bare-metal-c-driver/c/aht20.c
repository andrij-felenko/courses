#include "aht20.h"

/**
 * @file aht20.c
 * @brief Реалізація функцій драйвера AHT20.
 */

uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF; // Початкове значення за специфікацією AHT20
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x31); // Поліном x^8 + x^5 + x^4 + 1 (0x31)
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

aht20_status_t aht20_init(aht20_t *dev,
                          uint8_t dev_addr,
                          aht20_i2c_read_fn read_fn,
                          aht20_i2c_write_fn write_fn,
                          aht20_get_tick_ms_fn tick_fn,
                          void *user_data) {
    if (!dev || !read_fn || !write_fn || !tick_fn) {
        return AHT20_ERR_INVALID_ARG;
    }

    dev->dev_addr = dev_addr;
    dev->i2c_read = read_fn;
    dev->i2c_write = write_fn;
    dev->get_tick = tick_fn;
    dev->user_data = user_data;
    dev->state = AHT20_STATE_IDLE;
    dev->start_tick = 0;
    dev->is_calibrated = false;

    // Зчитуємо статус пристрою для перевірки прапорця калібрування
    uint8_t status = 0;
    if (!dev->i2c_read(dev->dev_addr, &status, 1, dev->user_data)) {
        return AHT20_ERR_I2C;
    }

    // Перевіряємо біт 3 статусного байта (0x08 - прапорець калібрування)
    if ((status & AHT20_STATUS_CALIBRATED_BIT) == 0) {
        // Якщо давач не відкалібрований, надсилаємо команду ініціалізації 0xBE 0x08 0x00
        uint8_t init_cmd[3] = {AHT20_CMD_INIT, 0x08, 0x00};
        if (!dev->i2c_write(dev->dev_addr, init_cmd, 3, dev->user_data)) {
            return AHT20_ERR_I2C;
        }

        // Перевіряємо статус повторно після команди ініціалізації
        if (!dev->i2c_read(dev->dev_addr, &status, 1, dev->user_data)) {
            return AHT20_ERR_I2C;
        }

        if ((status & AHT20_STATUS_CALIBRATED_BIT) == 0) {
            return AHT20_ERR_NOT_CALIBRATED;
        }
    }

    dev->is_calibrated = true;
    return AHT20_OK;
}

aht20_status_t aht20_reset(aht20_t *dev) {
    if (!dev || !dev->i2c_write) {
        return AHT20_ERR_INVALID_ARG;
    }

    uint8_t reset_cmd = AHT20_CMD_SOFT_RESET;
    if (!dev->i2c_write(dev->dev_addr, &reset_cmd, 1, dev->user_data)) {
        return AHT20_ERR_I2C;
    }

    dev->state = AHT20_STATE_IDLE;
    dev->is_calibrated = false;
    return AHT20_OK;
}

aht20_status_t aht20_start_measurement(aht20_t *dev) {
    if (!dev || !dev->i2c_write || !dev->get_tick) {
        return AHT20_ERR_INVALID_ARG;
    }

    if (dev->state != AHT20_STATE_IDLE) {
        return AHT20_BUSY;
    }

    // Команда вимірювання: 0xAC, 0x33, 0x00
    uint8_t trigger_cmd[3] = {AHT20_CMD_TRIGGER, 0x33, 0x00};
    if (!dev->i2c_write(dev->dev_addr, trigger_cmd, 3, dev->user_data)) {
        return AHT20_ERR_I2C;
    }

    dev->start_tick = dev->get_tick();
    dev->state = AHT20_STATE_MEASURING;

    return AHT20_OK;
}

aht20_status_t aht20_update(aht20_t *dev, aht20_data_t *data) {
    if (!dev || !dev->i2c_read || !dev->get_tick) {
        return AHT20_ERR_INVALID_ARG;
    }

    if (dev->state == AHT20_STATE_IDLE) {
        return AHT20_OK;
    }

    uint32_t current_tick = dev->get_tick();
    uint32_t elapsed = current_tick - dev->start_tick;

    // Очікуємо щонайменше 80 мс завершення вимірювання
    if (elapsed < AHT20_MEASURE_DELAY_MS) {
        return AHT20_BUSY;
    }

    // Зчитуємо 7 байтів: [0] Статус, [1..3] Вологість, [3..5] Температура, [6] CRC8
    uint8_t buffer[7] = {0};
    if (!dev->i2c_read(dev->dev_addr, buffer, 7, dev->user_data)) {
        dev->state = AHT20_STATE_IDLE;
        return AHT20_ERR_I2C;
    }

    // Перевіряємо біт 7 (Busy bit)
    if (buffer[0] & AHT20_STATUS_BUSY_BIT) {
        return AHT20_BUSY;
    }

    // Перевірка контрольної суми CRC-8 по перших 6 байтах
    uint8_t calculated_crc = aht20_calculate_crc8(buffer, 6);
    if (calculated_crc != buffer[6]) {
        dev->state = AHT20_STATE_IDLE;
        return AHT20_ERR_CRC;
    }

    if (data != NULL) {
        // Конвертація 20-бітного значення вологості (байти 1, 2 та старші 4 біти байта 3)
        uint32_t raw_humidity = ((uint32_t)buffer[1] << 12) |
                                ((uint32_t)buffer[2] << 4)  |
                                ((uint32_t)buffer[3] >> 4);

        // Конвертація 20-бітного значення температури (молодші 4 біти байта 3, байти 4 та 5)
        uint32_t raw_temperature = (((uint32_t)buffer[3] & 0x0F) << 16) |
                                   ((uint32_t)buffer[4] << 8)         |
                                   (uint32_t)buffer[5];

        // Формули за специфікацією AHT20:
        // RH (%) = (raw_humidity / 2^20) * 100
        // Temp (C) = (raw_temperature / 2^20) * 200 - 50
        data->humidity = ((float)raw_humidity / 1048576.0f) * 100.0f;
        data->temperature = (((float)raw_temperature / 1048576.0f) * 200.0f) - 50.0f;
    }

    dev->state = AHT20_STATE_IDLE;
    return AHT20_OK;
}

aht20_status_t aht20_read_blocking(aht20_t *dev, aht20_data_t *data, void (*delay_ms)(uint32_t)) {
    if (!dev || !delay_ms) {
        return AHT20_ERR_INVALID_ARG;
    }

    aht20_status_t status = aht20_start_measurement(dev);
    if (status != AHT20_OK) {
        return status;
    }

    // Затримка 80 мс до завершення вимірювання
    delay_ms(AHT20_MEASURE_DELAY_MS);

    return aht20_update(dev, data);
}
