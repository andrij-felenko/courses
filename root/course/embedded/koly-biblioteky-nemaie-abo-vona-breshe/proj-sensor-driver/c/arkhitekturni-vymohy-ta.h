#ifndef SENSOR_DRIVER_H
#define SENSOR_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Типізовані статусні коди повернення */
typedef enum {
    SENSOR_OK                    =  0,
    SENSOR_ERR_NULL_PTR          = -1,
    SENSOR_ERR_BUS_IO            = -2,
    SENSOR_ERR_BUS_TIMEOUT       = -3,
    SENSOR_ERR_CHIP_ID           = -4,
    SENSOR_ERR_CRC               = -5,
    SENSOR_ERR_NOT_READY         = -6,
    SENSOR_ERR_INVALID_STATE     = -7,
    SENSOR_ERR_DATA_OUT_OF_RANGE = -8,
    SENSOR_ERR_BUS_STUCK         = -9
} sensor_status_t;

/* Дискретні стани внутрішнього автомата драйвера */
typedef enum {
    SENSOR_STATE_UNINITIALIZED = 0,
    SENSOR_STATE_IDLE,
    SENSOR_STATE_CONVERTING,
    SENSOR_STATE_DATA_READY,
    SENSOR_STATE_ERROR
} sensor_fsm_state_t;

/* Абстрактний інтерфейс апаратної шини (I2C / SPI) */
typedef struct {
    /* Читання блоку байтів із вказаного субрегістра */
    sensor_status_t (*read)(void *user_ctx, uint8_t reg_addr, uint8_t *data, size_t len);
    /* Запис блоку байтів у вказаний субрегістр */
    sensor_status_t (*write)(void *user_ctx, uint8_t reg_addr, const uint8_t *data, size_t len);
    /* Отримання поточного монотонного часу в мікросекундах */
    uint32_t (*get_time_us)(void);
    /* Апаратне розблокування ліній зв'язку (опціонально, може бути NULL) */
    sensor_status_t (*recover_bus)(void *user_ctx);
} sensor_bus_ops_t;

/* Структура вихідних фізичних величин у міжнародній системі SI */
typedef struct {
    int32_t  temperature_mdeg_c;  /* Температура в міліградусах Цельсія (25150 = 25.15 °C) */
    uint32_t humidity_mpercent;   /* Відносна вологість у міліпроцентах (48500 = 48.50 %) */
    uint32_t pressure_pa;         /* Абсолютний тиск у Паскалях (101325 Па) */
    uint32_t timestamp_us;        /* Часова мітка завершення заміру (мкс) */
} sensor_data_t;

/* Дескриптор екземпляра сенсора */
typedef struct {
    const sensor_bus_ops_t *ops;             /* Покажчики на операції шини */
    void                   *user_ctx;        /* Контекст користувача (номер порту, дескриптор) */
    sensor_fsm_state_t      state;           /* Поточний стан автомата */
    uint32_t                conv_start_us;   /* Час старту фізичної конверсії */
    uint32_t                conv_timeout_us; /* Таймаут завершення заміру (мкс) */
    uint8_t                 raw_buf[7];      /* Статичний буфер сирих байтів */
} sensor_device_t;

/* Публічний інтерфейс драйвера */
sensor_status_t sensor_init(sensor_device_t *dev, const sensor_bus_ops_t *ops, void *user_ctx);
sensor_status_t sensor_start_measurement(sensor_device_t *dev);
sensor_status_t sensor_poll(sensor_device_t *dev, sensor_data_t *out_data);
sensor_status_t sensor_reset_fsm(sensor_device_t *dev);
uint8_t sensor_calculate_crc8(const uint8_t *data, size_t len);

#endif /* SENSOR_DRIVER_H */
