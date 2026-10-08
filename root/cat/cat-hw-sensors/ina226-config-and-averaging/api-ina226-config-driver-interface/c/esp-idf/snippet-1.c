#ifndef INA226_TYPES_H
#define INA226_TYPES_H

#include <stdint.h>
#include <stdbool.h>

// Режими роботи INA226 (біти MODE2:MODE0)
typedef enum {
    INA226_MODE_POWER_DOWN           = 0x00,
    INA226_MODE_SHUNT_TRIGGERED      = 0x01,
    INA226_MODE_BUS_TRIGGERED        = 0x02,
    INA226_MODE_ALL_TRIGGERED        = 0x03,
    INA226_MODE_POWER_DOWN_ALT       = 0x04,
    INA226_MODE_SHUNT_CONTINUOUS     = 0x05,
    INA226_MODE_BUS_CONTINUOUS       = 0x06,
    INA226_MODE_ALL_CONTINUOUS       = 0x07
} ina226_mode_t;

// Час конверсії для каналів шунта та шини (біти VSH CT та VBUS CT)
typedef enum {
    INA226_CONV_TIME_140US  = 0x00,
    INA226_CONV_TIME_204US  = 0x01,
    INA226_CONV_TIME_332US  = 0x02,
    INA226_CONV_TIME_588US  = 0x03,
    INA226_CONV_TIME_1100US = 0x04, // За замовчуванням (1.1 мс)
    INA226_CONV_TIME_2116US = 0x05,
    INA226_CONV_TIME_4156US = 0x06,
    INA226_CONV_TIME_8244US = 0x07
} ina226_conv_time_t;

// Кількість зразків усереднення (біти AVG2:AVG0)
typedef enum {
    INA226_AVG_1    = 0x00, // Без усереднення
    INA226_AVG_4    = 0x01,
    INA226_AVG_16   = 0x02,
    INA226_AVG_64   = 0x03,
    INA226_AVG_128  = 0x04,
    INA226_AVG_256  = 0x05,
    INA226_AVG_512  = 0x06,
    INA226_AVG_1024 = 0x07
} ina226_averaging_t;

// Конфігураційна структура драйвера INA226
typedef struct {
    ina226_mode_t       mode;          // Режим вимірювання
    ina226_conv_time_t  vsh_conv_time;  // Час конверсії шунта
    ina226_conv_time_t  vbus_conv_time; // Час конверсії шини
    ina226_averaging_t  avg_samples;    // Кількість усереднень
} ina226_config_t;

#endif // INA226_TYPES_H
