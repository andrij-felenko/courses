#ifndef MAX31865_H
#define MAX31865_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "stm32f4xx_hal.h"

/**
 * @file max31865.h
 * @brief Драйвер C для прецизійного перетворювача опору платинових датчиків MAX31865 (STM32 HAL).
 */

/* --- Адреси регістрів MAX31865 (Read: addr & 0x7F, Write: addr | 0x80) --- */
#define MAX31865_REG_CONFIG           0x00
#define MAX31865_REG_RTD_MSB          0x01
#define MAX31865_REG_RTD_LSB          0x02
#define MAX31865_REG_HIGH_FAULT_MSB   0x03
#define MAX31865_REG_HIGH_FAULT_LSB   0x04
#define MAX31865_REG_LOW_FAULT_MSB    0x05
#define MAX31865_REG_LOW_FAULT_LSB    0x06
#define MAX31865_REG_FAULT_STATUS     0x07

#define MAX31865_SPI_WRITE_MASK       0x80

/* --- Бітові маски конфігураційного регістру (CONFIG) --- */
#define MAX31865_CONFIG_VBIAS_ON      0x80  /* Увімкнення напруги зміщення VBIAS */
#define MAX31865_CONFIG_AUTO_CONV     0x40  /* Автоматичний режим безперервної конверсії */
#define MAX31865_CONFIG_1SHOT         0x20  /* Запуск одиночного перетворення АЦП */
#define MAX31865_CONFIG_3WIRE         0x10  /* 3-провідне підключення RTD (1 = 3-wire, 0 = 2/4-wire) */
#define MAX31865_CONFIG_FAULT_DET_AUTO 0x04 /* Автоматичний цикл виявлення помилок */
#define MAX31865_CONFIG_FAULT_CLEAR   0x02  /* Скидання прапорів у регістрі FAULT_STATUS */
#define MAX31865_CONFIG_FILTER_50HZ   0x01  /* Фільтр придушення мережевої завади 50 Гц */
#define MAX31865_CONFIG_FILTER_60HZ   0x00  /* Фільтр придушення мережевої завади 60 Гц */

/* --- Бітові маски регістру статусів помилок (FAULT_STATUS) --- */
#define MAX31865_FAULT_HIGH_THRESH    0x80  /* Перевищення верхнього порогу опору (High Fault) */
#define MAX31865_FAULT_LOW_THRESH     0x40  /* Вихід за нижній поріг опору (Low Fault) */
#define MAX31865_FAULT_REFIN_HIGH     0x20  /* Напруга REFIN- > 0.85 * VBIAS (обрив Rref) */
#define MAX31865_FAULT_REFIN_LOW      0x10  /* Напруга REFIN- < 0.85 * VBIAS (FORCE- open) */
#define MAX31865_FAULT_RTDIN_LOW      0x08  /* Напруга RTDIN- < 0.85 * VBIAS (FORCE- open) */
#define MAX31865_FAULT_OV_UV          0x04  /* Перенапруга або знижена напруга живлення */

/**
 * @brief Тип платинового термоопору (RTD).
 */
typedef enum {
    MAX31865_RTD_PT100  = 0,  /* PT100: R0 = 100.0 Ом */
    MAX31865_RTD_PT1000 = 1   /* PT1000: R0 = 1000.0 Ом */
} max31865_rtd_type_t;

/**
 * @brief Схема підключення термоперетворювача.
 */
typedef enum {
    MAX31865_2WIRE = 0,  /* 2-провідне підключення */
    MAX31865_3WIRE = 1,  /* 3-провідне підключення */
    MAX31865_4WIRE = 2   /* 4-провідне підключення */
} max31865_wire_mode_t;

/**
 * @brief Коди повернення та статус виконання функцій драйвера.
 */
typedef enum {
    MAX31865_OK          =  0,  /* Операцію виконано успішно */
    MAX31865_ERR_SPI     = -1,  /* Помилка обміну по шині SPI */
    MAX31865_ERR_PARAM   = -2,  /* Некоректні вхідні параметри */
    MAX31865_ERR_FAULT   = -3   /* Виявлено апаратний збій вимірювального тракту */
} max31865_status_t;

/**
 * @brief Структура конфігурації MAX31865.
 */
typedef struct {
    max31865_rtd_type_t  rtd_type;        /* Тип давача (PT100 або PT1000) */
    max31865_wire_mode_t wire_mode;       /* Схема підключення (2-, 3- або 4-провідна) */
    float                rref_ohms;       /* Номінал опорного резистора Rref (Ом) */
    bool                 filter_50hz;     /* true = 50 Гц, false = 60 Гц */
    bool                 auto_conversion; /* true = автоматичний режим, false = 1-shot */
} max31865_config_t;

/**
 * @brief Контекст екземпляра драйвера MAX31865.
 */
typedef struct {
    SPI_HandleTypeDef   *hspi;               /* Вказівник на хендл SPI STM32 HAL */
    GPIO_TypeDef        *cs_port;            /* Порт GPIO для Chip Select (CS) */
    uint16_t             cs_pin;             /* Вивід GPIO для Chip Select (CS) */
    max31865_config_t    config;             /* Налаштування режимів АЦП */
    uint8_t              last_fault_status;  /* Останній зчитаний байт статусів помилок */
} max31865_t;

/* --- Прототипи функцій драйвера MAX31865 --- */

/**
 * @brief Ініціалізація драйвера MAX31865 та запис конфігурації в мікросхему.
 */
max31865_status_t max31865_init(max31865_t *dev, SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, const max31865_config_t *config);

/**
 * @brief Зчитування сирого 15-бітного значення АЦП та перевірка прапора помилки.
 */
max31865_status_t max31865_read_raw(max31865_t *dev, uint16_t *raw_adc, bool *fault_detected);

/**
 * @brief Зчитування регістру статусів апаратних помилок FAULT_STATUS.
 */
max31865_status_t max31865_read_fault(max31865_t *dev, uint8_t *fault_status);

/**
 * @brief Скидання прапорів помилок у конфігураційному регістрі MAX31865.
 */
max31865_status_t max31865_clear_fault(max31865_t *dev);

/**
 * @brief Зчитування виміряних значень: обчислення опору та температури (°C).
 */
max31865_status_t max31865_read_temperature(max31865_t *dev, float *temperature_c, float *resistance_ohms);

/**
 * @brief Математичний розрахунок температури за рівнянням Каллендара — Ван Дюзена.
 */
float max31865_calculate_temperature(uint16_t raw_adc, float rref_ohms, float r0_ohms);

#endif /* MAX31865_H */
