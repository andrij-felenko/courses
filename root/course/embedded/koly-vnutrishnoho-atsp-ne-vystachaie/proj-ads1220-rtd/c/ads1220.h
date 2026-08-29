#ifndef ADS1220_H
#define ADS1220_H

/* Драйвер 24-бітного дельта-сигма АЦП ADS1220 у режимі 3-провідного PT100:
   два узгоджені струми збудження, логометрична опора на R_ref, одиничне
   перетворення й готовність за апаратним перериванням DRDY. */

#include <stdint.h>

#include "stm32g0xx_hal.h"

typedef enum {
    ADS1220_OK = 0,
    ADS1220_ERR_ARG,      /* некоректний виклик драйвера */
    ADS1220_ERR_SPI,      /* обмін по шині не відбувся */
    ADS1220_ERR_CONFIG,   /* регістри прочиталися не такими, як записані */
    ADS1220_ERR_TIMEOUT,  /* DRDY не впав за відведений час */
    ADS1220_ERR_RANGE     /* код упертий у шкалу: обрив або замикання датчика */
} ads1220_status_t;

typedef struct {
    /* Заповнює виклик перед ads1220_init() */
    SPI_HandleTypeDef *spi;        /* шина в режимі 1: CPOL = 0, CPHA = 1 */
    GPIO_TypeDef      *cs_port;
    uint16_t           cs_pin;
    float              r_ref;      /* еталонний резистор, Ом */
    float              gain;       /* коефіцієнт підсилення PGA */

    /* Внутрішній стан драйвера */
    int32_t            offset_code;
    volatile uint8_t   drdy;       /* прапорець, який ставить обробник переривання */
} ads1220_t;

/* Скидає мікросхему, записує робочу конфігурацію й перечитує її назад. */
ads1220_status_t ads1220_init(ads1220_t *dev);

/* Міряє власне зміщення нуля тракту на закорочених усередині входах. */
ads1220_status_t ads1220_calibrate_offset(ads1220_t *dev);

/* Одне перетворення: повертає логометрично порахований опір датчика. */
ads1220_status_t ads1220_read_resistance(ads1220_t *dev, float *r_ohms);

/* Викликається з обробника зовнішнього переривання на спаді DRDY. */
void ads1220_drdy_isr(ads1220_t *dev);

const char *ads1220_strerror(ads1220_status_t status);

#endif /* ADS1220_H */
