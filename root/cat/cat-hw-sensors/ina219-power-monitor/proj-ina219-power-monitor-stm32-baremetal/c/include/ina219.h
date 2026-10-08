#ifndef INA219_H
#define INA219_H

#include <stdint.h>
#include <stdbool.h>
#include "i2c_driver.h"

/**
 * @file ina219.h
 * @brief Оголошення bare-metal C-драйвера монітора струму й напруги INA219 для STM32.
 */

/* Стандартна 7-бітна I2C адреса пристрою INA219 (A0=GND, A1=GND) */
#define INA219_I2C_ADDR_DEFAULT       0x40

/* Адреси 16-бітних регістрів INA219 */
#define INA219_REG_CONFIG             0x00
#define INA219_REG_SHUNT_VOLTAGE      0x01
#define INA219_REG_BUS_VOLTAGE        0x02
#define INA219_REG_POWER              0x03
#define INA219_REG_CURRENT            0x04
#define INA219_REG_CALIBRATION        0x05

/* Бітові маски та зсуви регістру конфігурації (Configuration Register 0x00) */
#define INA219_CONFIG_RESET           (1U << 15)  /* Програмний скид пристрою */

#define INA219_CONFIG_BRNG_MASK       (1U << 13)  /* Маска діапазону напруги шини */
#define INA219_CONFIG_BRNG_16V        (0U << 13)  /* Шкала напруги шини 16 В */
#define INA219_CONFIG_BRNG_32V        (1U << 13)  /* Шкала напруги шини 32 В */

#define INA219_CONFIG_PGA_MASK        (3U << 11)  /* Маска підсилення PGA */
#define INA219_CONFIG_PGA_1_40MV      (0U << 11)  /* PGA /1 (діапазон ±40 мВ) */
#define INA219_CONFIG_PGA_2_80MV      (1U << 11)  /* PGA /2 (діапазон ±80 мВ) */
#define INA219_CONFIG_PGA_4_160MV     (2U << 11)  /* PGA /4 (діапазон ±160 мВ) */
#define INA219_CONFIG_PGA_8_320MV     (3U << 11)  /* PGA /8 (діапазон ±320 мВ) */

#define INA219_CONFIG_BADC_MASK       (0xFU << 7) /* Маска налаштування Bus ADC */
#define INA219_CONFIG_BADC_SHIFT      7

#define INA219_CONFIG_SADC_MASK       (0xFU << 3) /* Маска налаштування Shunt ADC */
#define INA219_CONFIG_SADC_SHIFT      3

#define INA219_CONFIG_MODE_MASK       (7U << 0)   /* Маска режиму роботи */
#define INA219_CONFIG_MODE_SHIFT      0

/* Бітові маски регістру напруги шини (Bus Voltage Register 0x02) */
#define INA219_BUS_VOLTAGE_RAW_MASK   (0xFFF8U)   /* Данi напруги в бітах [15:3] */
#define INA219_BUS_VOLTAGE_RAW_SHIFT  3
#define INA219_BUS_VOLTAGE_CNVR       (1U << 1)   /* Прапорець готовності конверсії (CNVR) */
#define INA219_BUS_VOLTAGE_OVF        (1U << 0)   /* Прапорець математичного переповнення (OVF) */

/**
 * @brief Перелічення діапазонів напруги шини (BRNG).
 */
typedef enum {
    INA219_BUS_RANGE_16V = 0,
    INA219_BUS_RANGE_32V = 1
} ina219_bus_range_t;

/**
 * @brief Перелічення підсилення програмованого підсилювача (PGA).
 */
typedef enum {
    INA219_PGA_GAIN_1_40MV  = 0,
    INA219_PGA_GAIN_2_80MV  = 1,
    INA219_PGA_GAIN_4_160MV = 2,
    INA219_PGA_GAIN_8_320MV = 3
} ina219_pga_gain_t;

/**
 * @brief Перелічення роздільної здатності та усереднення АЦП (BADC / SADC).
 */
typedef enum {
    INA219_ADC_RES_9BIT   = 0x0, /* 9-бітний режим (час конверсії 84 мкс) */
    INA219_ADC_RES_10BIT  = 0x1, /* 10-бітний режим (час конверсії 148 мкс) */
    INA219_ADC_RES_11BIT  = 0x2, /* 11-бітний режим (час конверсії 276 мкс) */
    INA219_ADC_RES_12BIT  = 0x3, /* 12-бітний режим (час конверсії 532 мкс) */
    INA219_ADC_AVG_2      = 0x9, /* Усереднення 2 вибірок (1.06 мс) */
    INA219_ADC_AVG_4      = 0xA, /* Усереднення 4 вибірок (2.13 мс) */
    INA219_ADC_AVG_8      = 0xB, /* Усереднення 8 вибірок (4.26 мс) */
    INA219_ADC_AVG_16     = 0xC, /* Усереднення 16 вибірок (8.51 мс) */
    INA219_ADC_AVG_32     = 0xD, /* Усереднення 32 вибірок (17.02 мс) */
    INA219_ADC_AVG_64     = 0xE, /* Усереднення 64 вибірок (34.05 мс) */
    INA219_ADC_AVG_128    = 0xF  /* Усереднення 128 вибірок (68.10 мс) */
} ina219_adc_mode_t;

/**
 * @brief Режими роботи INA219 (MODE).
 */
typedef enum {
    INA219_MODE_POWER_DOWN          = 0,
    INA219_MODE_SHUNT_TRIGGERED     = 1,
    INA219_MODE_BUS_TRIGGERED       = 2,
    INA219_MODE_SHUNT_BUS_TRIGGERED = 3,
    INA219_MODE_ADC_OFF             = 4,
    INA219_MODE_SHUNT_CONTINUOUS    = 5,
    INA219_MODE_BUS_CONTINUOUS      = 6,
    INA219_MODE_SHUNT_BUS_CONTINUOUS= 7
} ina219_mode_t;

/**
 * @brief Структура конфігурації параметрів INA219.
 */
typedef struct {
    uint8_t i2c_addr;             /* I2C адреса веденого пристрою */
    ina219_bus_range_t bus_range; /* Максимальна напруга шини (16V / 32V) */
    ina219_pga_gain_t pga_gain;   /* Діапазон напруги шунта PGA */
    ina219_adc_mode_t bus_adc;    /* Режим АЦП шини напруги */
    ina219_adc_mode_t shunt_adc;  /* Режим АЦП шунта */
    ina219_mode_t mode;           /* Режим вимірювання */
    float r_shunt_ohms;           /* Опір вимірювального шунта в Омах (наприклад, 0.1) */
    float max_expected_i;         /* Максимальний очікуваний струм в Амперах */
} ina219_config_t;

/**
 * @brief Структура для збереження зчитаних телеметричних даних.
 */
typedef struct {
    float voltage_v;        /* Напруга шини у Вольтах */
    float shunt_voltage_mv; /* Спад напруги на шунті в мілівольтах */
    float current_ma;       /* Виміряний струм у міліамперах */
    float power_mw;         /* Обчислена потужність у міліватах */
    bool conversion_ready;  /* Прапорець готовності вибірки CNVR */
    bool math_overflow;     /* Прапорець математичного переповнення OVF */
} ina219_data_t;

/**
 * @brief Дескриптор пристрою INA219.
 */
typedef struct {
    i2c_bus_t *i2c;        /* Вказівник на екземпляр I2C шини */
    ina219_config_t config;/* Налаштування пристрою */
    uint16_t cal_value;    /* Значення регістру Calibration */
    float current_lsb_a;   /* Дискретність струму (Ампер/LSB) */
    float power_lsb_w;     /* Дискретність потужності (Ват/LSB) */
} ina219_t;

/* Прототипи публічних функцій драйвера */
i2c_status_t ina219_init(ina219_t *dev, i2c_bus_t *i2c, const ina219_config_t *cfg);
i2c_status_t ina219_reset(ina219_t *dev);
uint16_t ina219_calculate_calibration(float r_shunt_ohms, float max_expected_i, float *out_current_lsb);
i2c_status_t ina219_write_calibration(ina219_t *dev);
i2c_status_t ina219_read_bus_voltage(ina219_t *dev, float *voltage_v, bool *cnvr, bool *ovf);
i2c_status_t ina219_read_shunt_voltage(ina219_t *dev, float *shunt_mv);
i2c_status_t ina219_read_current(ina219_t *dev, float *current_ma);
i2c_status_t ina219_read_power(ina219_t *dev, float *power_mw);
i2c_status_t ina219_read_telemetry(ina219_t *dev, ina219_data_t *data);

#endif /* INA219_H */
