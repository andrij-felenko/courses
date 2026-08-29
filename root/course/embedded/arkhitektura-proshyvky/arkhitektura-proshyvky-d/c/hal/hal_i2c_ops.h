/* hal/hal_i2c_ops.h — таблиця операцій шини I2C: сторона того, ХТО реалізує.
 * Цей заголовок включає порт (stm32_hal_i2c.c, mock_hal_i2c.c), а не драйвер.
 * Драйверові вистачає hal/hal_i2c.h: тут зобов'язання, там виклики. */
#ifndef HAL_I2C_OPS_H
#define HAL_I2C_OPS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
    HAL_I2C_OK = 0,
    HAL_I2C_ERR_NACK,      /* мікросхема не підтвердила адресу чи байт */
    HAL_I2C_ERR_BUS,       /* втрата арбітражу, залипла лінія SDA, шум */
    HAL_I2C_ERR_TIMEOUT,   /* контролер не дочекався готовності */
    HAL_I2C_ERR_ARG        /* аргументи виклику не мають сенсу */
} hal_i2c_status_t;

/* Порт заповнює цю таблицю своїми функціями. Аргумент ctx — приватний
 * покажчик порту: I2C_HandleTypeDef на STM32, структура імітованої
 * мікросхеми в тесті на комп'ютері розробника. Шар вище про нього
 * нічого не знає й ніколи його не розіменовує. */
typedef struct {
    hal_i2c_status_t (*write)(void *ctx, uint8_t dev_addr,
                              const uint8_t *data, size_t len);

    hal_i2c_status_t (*read)(void *ctx, uint8_t dev_addr,
                             uint8_t *data, size_t len);

    /* Необов'язкова операція: передати й одразу прочитати без відпускання
     * шини (повторний START). Якщо порт її не має, hal_i2c.c складе те саме
     * з write + read — трохи повільніше, зате працює всюди. */
    hal_i2c_status_t (*write_read)(void *ctx, uint8_t dev_addr,
                                   const uint8_t *wdata, size_t wlen,
                                   uint8_t *rdata, size_t rlen);
} hal_i2c_ops_t;

/* Дескриптор шини: таблиця операцій плюс приватний контекст порту.
 * Драйвер тримає покажчик на цю структуру й більше нічого про залізо не знає. */
typedef struct {
    const hal_i2c_ops_t *ops;
    void                *ctx;
} hal_i2c_bus_t;

const char *hal_i2c_status_str(hal_i2c_status_t status);

#endif /* HAL_I2C_OPS_H */
