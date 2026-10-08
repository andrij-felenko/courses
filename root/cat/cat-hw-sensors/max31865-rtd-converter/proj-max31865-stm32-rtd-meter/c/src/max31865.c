#include "max31865.h"
#include <math.h>

/**
 * @file max31865.c
 * @brief Реалізація функцій низькорівневого C-драйвера MAX31865 для STM32 HAL.
 */

#define MAX31865_SPI_TIMEOUT_MS 100

/* --- Приватні допоміжні функції маніпуляції лінією CS --- */

static inline void max31865_cs_select(max31865_t *dev)
{
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_RESET);
}

static inline void max31865_cs_deselect(max31865_t *dev)
{
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_SET);
}

/* --- Запис та зчитування поодиноких регістрів --- */

static max31865_status_t max31865_write_register(max31865_t *dev, uint8_t reg_addr, uint8_t data)
{
    uint8_t tx_buf[2];
    tx_buf[0] = reg_addr | MAX31865_SPI_WRITE_MASK;
    tx_buf[1] = data;

    max31865_cs_select(dev);
    HAL_StatusTypeDef status = HAL_SPI_Transmit(dev->hspi, tx_buf, 2, MAX31865_SPI_TIMEOUT_MS);
    max31865_cs_deselect(dev);

    return (status == HAL_OK) ? MAX31865_OK : MAX31865_ERR_SPI;
}

static max31865_status_t max31865_read_register(max31865_t *dev, uint8_t reg_addr, uint8_t *data)
{
    uint8_t tx_addr = reg_addr & 0x7F;

    max31865_cs_select(dev);
    HAL_StatusTypeDef status_addr = HAL_SPI_Transmit(dev->hspi, &tx_addr, 1, MAX31865_SPI_TIMEOUT_MS);
    HAL_StatusTypeDef status_data = HAL_SPI_Receive(dev->hspi, data, 1, MAX31865_SPI_TIMEOUT_MS);
    max31865_cs_deselect(dev);

    if (status_addr != HAL_OK || status_data != HAL_OK) {
        return MAX31865_ERR_SPI;
    }
    return MAX31865_OK;
}

static max31865_status_t max31865_read_registers(max31865_t *dev, uint8_t start_reg, uint8_t *buffer, uint16_t length)
{
    uint8_t tx_addr = start_reg & 0x7F;

    max31865_cs_select(dev);
    HAL_StatusTypeDef status_addr = HAL_SPI_Transmit(dev->hspi, &tx_addr, 1, MAX31865_SPI_TIMEOUT_MS);
    HAL_StatusTypeDef status_data = HAL_SPI_Receive(dev->hspi, buffer, length, MAX31865_SPI_TIMEOUT_MS);
    max31865_cs_deselect(dev);

    if (status_addr != HAL_OK || status_data != HAL_OK) {
        return MAX31865_ERR_SPI;
    }
    return MAX31865_OK;
}

/* --- Публічні функції драйвера --- */

max31865_status_t max31865_init(max31865_t *dev, SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, const max31865_config_t *config)
{
    if (dev == NULL || hspi == NULL || cs_port == NULL || config == NULL) {
        return MAX31865_ERR_PARAM;
    }

    dev->hspi = hspi;
    dev->cs_port = cs_port;
    dev->cs_pin = cs_pin;
    dev->config = *config;
    dev->last_fault_status = 0;

    max31865_cs_deselect(dev);

    /* Формування конфігураційного байта */
    uint8_t config_byte = MAX31865_CONFIG_VBIAS_ON;

    if (config->auto_conversion) {
        config_byte |= MAX31865_CONFIG_AUTO_CONV;
    }

    if (config->wire_mode == MAX31865_3WIRE) {
        config_byte |= MAX31865_CONFIG_3WIRE;
    }

    if (config->filter_50hz) {
        config_byte |= MAX31865_CONFIG_FILTER_50HZ;
    }

    /* Очищення старих прапорів помилок перед запуском */
    config_byte |= MAX31865_CONFIG_FAULT_CLEAR;

    max31865_status_t status = max31865_write_register(dev, MAX31865_REG_CONFIG, config_byte);
    if (status != MAX31865_OK) {
        return status;
    }

    HAL_Delay(10); /* Пауза для стабілізації напруги VBIAS */
    return MAX31865_OK;
}

max31865_status_t max31865_read_raw(max31865_t *dev, uint16_t *raw_adc, bool *fault_detected)
{
    if (dev == NULL || raw_adc == NULL || fault_detected == NULL) {
        return MAX31865_ERR_PARAM;
    }

    uint8_t raw_bytes[2];
    max31865_status_t status = max31865_read_registers(dev, MAX31865_REG_RTD_MSB, raw_bytes, 2);
    if (status != MAX31865_OK) {
        return status;
    }

    uint16_t full_word = ((uint16_t)raw_bytes[0] << 8) | raw_bytes[1];
    
    /* Молодший біт D0 вказує на наявність апаратної помилки */
    *fault_detected = (full_word & 0x0001) != 0;
    
    /* Отримання 15-бітного цифрового значення коду АЦП (зсув праворуч на 1 біт) */
    *raw_adc = full_word >> 1;

    return MAX31865_OK;
}

max31865_status_t max31865_read_fault(max31865_t *dev, uint8_t *fault_status)
{
    if (dev == NULL || fault_status == NULL) {
        return MAX31865_ERR_PARAM;
    }

    max31865_status_t status = max31865_read_register(dev, MAX31865_REG_FAULT_STATUS, fault_status);
    if (status == MAX31865_OK) {
        dev->last_fault_status = *fault_status;
    }
    return status;
}

max31865_status_t max31865_clear_fault(max31865_t *dev)
{
    if (dev == NULL) {
        return MAX31865_ERR_PARAM;
    }

    uint8_t config_byte = 0;
    max31865_status_t status = max31865_read_register(dev, MAX31865_REG_CONFIG, &config_byte);
    if (status != MAX31865_OK) {
        return status;
    }

    /* Встановлення біта примусового скидання статусів помилок */
    config_byte |= MAX31865_CONFIG_FAULT_CLEAR;
    return max31865_write_register(dev, MAX31865_REG_CONFIG, config_byte);
}

float max31865_calculate_temperature(uint16_t raw_adc, float rref_ohms, float r0_ohms)
{
    /* Обчислення опору датчика RTD відносно опорного резистора Rref (15-бітний АЦП) */
    float resistance = ((float)raw_adc / 32768.0f) * rref_ohms;
    float r_ratio = resistance / r0_ohms;

    /* Коефіцієнти стандарту IEC 60751 (ITS-90) для платинових датчиків */
    const float a = 3.9083e-3f;
    const float b = -5.775e-7f;

    if (r_ratio >= 1.0f) {
        /* Формула для позитивних температур (T >= 0 °C) з квадратного рівняння */
        float discriminant = (a * a) - (4.0f * b * (1.0f - r_ratio));
        if (discriminant < 0.0f) {
            discriminant = 0.0f;
        }
        return (-a + sqrtf(discriminant)) / (2.0f * b);
    } else {
        /* Поліноміальне наближення 5-го степеня для негативних температур (T < 0 °C) */
        float r100 = r_ratio * 100.0f;
        float r100_2 = r100 * r100;
        float r100_3 = r100_2 * r100;
        float r100_4 = r100_3 * r100;
        float r100_5 = r100_4 * r100;

        return -242.02f + (2.2228f * r100) + (2.5859e-3f * r100_2) -
               (4.8260e-6f * r100_3) - (2.8183e-8f * r100_4) + (1.5243e-10f * r100_5);
    }
}

max31865_status_t max31865_read_temperature(max31865_t *dev, float *temperature_c, float *resistance_ohms)
{
    if (dev == NULL || temperature_c == NULL || resistance_ohms == NULL) {
        return MAX31865_ERR_PARAM;
    }

    uint16_t raw_adc = 0;
    bool fault = false;

    max31865_status_t status = max31865_read_raw(dev, &raw_adc, &fault);
    if (status != MAX31865_OK) {
        return status;
    }

    if (fault) {
        uint8_t fault_reg = 0;
        max31865_read_fault(dev, &fault_reg);
        return MAX31865_ERR_FAULT;
    }

    float r0 = (dev->config.rtd_type == MAX31865_RTD_PT1000) ? 1000.0f : 100.0f;
    *resistance_ohms = ((float)raw_adc / 32768.0f) * dev->config.rref_ohms;
    *temperature_c = max31865_calculate_temperature(raw_adc, dev->config.rref_ohms, r0);

    return MAX31865_OK;
}
