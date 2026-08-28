#ifndef HUMIDITY_API_H
#define HUMIDITY_API_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок API */
typedef enum {
    HUMIDITY_OK                   =  0,
    HUMIDITY_ERR_NULL_PTR         = -1,
    HUMIDITY_ERR_I2C_COMM         = -2,
    HUMIDITY_ERR_CRC_MISMATCH     = -3,
    HUMIDITY_ERR_OUT_OF_BOUNDS    = -4,
    HUMIDITY_ERR_HEATER_OVERHEAT  = -5,
    HUMIDITY_ERR_NOT_READY        = -6
} humidity_error_t;

/* Режими точності вимірювання */
typedef enum {
    HUMIDITY_PRECISION_LOW = 0,
    HUMIDITY_PRECISION_MEDIUM,
    HUMIDITY_PRECISION_HIGH
} humidity_precision_t;

/* Структура конфігурації шини та сенсора */
typedef struct {
    uint8_t i2c_address;        /* I2C адреса (0x44 або 0x45) */
    uint32_t timeout_ms;        /* Таймаут зчитування в мілісекундах */
    humidity_precision_t precision; /* Точність */
    bool enable_auto_heater;   /* Автоматичне ввімкнення нагрівача при RH > 95% */
    
    /* Вказівники на функції низького рівня адаптера шини (HAL) */
    int (*i2c_write)(uint8_t addr, const uint8_t *data, uint16_t len);
    int (*i2c_read)(uint8_t addr, uint8_t *data, uint16_t len);
    void (*delay_ms)(uint32_t ms);
} humidity_sensor_config_t;

/* Повні сирі та термодинамічні дані */
typedef struct {
    uint16_t raw_temperature;   /* Сирий код ADC температури */
    uint16_t raw_humidity;      /* Сирий код ADC вологості */
    float temperature_c;        /* Обчислена температура, °C */
    float relative_humidity;    /* Обчислена відносна вологість, % */
    float dew_point_c;          /* Температура точки роси, °C */
    float vapor_pressure_pa;    /* Парціальний тиск водяної пари, Па */
    float absolute_humidity_g_m3;/* Абсолютна вологість, г/м³ */
} humidity_data_t;

/* Публічні функції API */

/**
 * @brief Ініціалізація модуля та перевірка зв'язку
 * @param cfg Вказівник на конфігураційну структуру
 * @return HUMIDITY_OK у разі успіху
 */
humidity_error_t humidity_sensor_init(const humidity_sensor_config_t *cfg);

/**
 * @brief Виконання одноразового вимірювання
 * @param cfg Вказівник на конфігурацію
 * @param data Вказівник на структуру результату
 * @return HUMIDITY_OK у разі успіху
 */
humidity_error_t humidity_sensor_read_single(
    const humidity_sensor_config_t *cfg, 
    humidity_data_t *data
);

/**
 * @brief Керування внутрішнім нагрівачем деконденсації
 * @param cfg Вказівник на конфігурацію
 * @param enable true для увімкнення, false для вимкнення
 * @return HUMIDITY_OK у разі успіху
 */
humidity_error_t humidity_sensor_set_heater(
    const humidity_sensor_config_t *cfg, 
    bool enable
);

/**
 * @brief Перевірка контрольної суми CRC-8
 * @param data Вказівник на 2 байти даних
 * @param checksum Очікуваний байт CRC
 * @return true якщо CRC вірний
 */
bool humidity_crc8_verify(const uint8_t *data, uint8_t checksum);

#ifdef __cplusplus
}
#endif

#endif /* HUMIDITY_API_H */
