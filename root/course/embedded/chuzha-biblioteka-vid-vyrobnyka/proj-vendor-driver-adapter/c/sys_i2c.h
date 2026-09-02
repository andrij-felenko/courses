/*
 * Системний контракт: усе, що бачить бізнес-логіка прошивки.
 * Тут немає жодного вендорського типу й жодного номера регістра чипа.
 */
#ifndef SYS_I2C_H
#define SYS_I2C_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Системні коди результату. Коди помилок вендорського SDK назовні не
   просочуються — адаптер перекладає їх у цей перелік. */
typedef enum {
    SYS_OK = 0,
    SYS_ERR_PARAM,    /* некоректні аргументи виклику */
    SYS_ERR_COMM,     /* шина не відповіла: NACK, втрата арбітражу, обрив */
    SYS_ERR_DEVICE,   /* на адресі стоїть не той чип */
    SYS_ERR_TIMEOUT,  /* вимірювання не завершилось у відведений час */
    SYS_ERR_CALIB,    /* калібрувальні коефіцієнти непридатні для розрахунку */
    SYS_ERR_NO_SLOT   /* вичерпано статичний пул адаптерів */
} sys_status_t;

static inline const char *sys_status_str(sys_status_t st)
{
    switch (st) {
    case SYS_OK:          return "OK";
    case SYS_ERR_PARAM:   return "ERR_PARAM";
    case SYS_ERR_COMM:    return "ERR_COMM";
    case SYS_ERR_DEVICE:  return "ERR_DEVICE";
    case SYS_ERR_TIMEOUT: return "ERR_TIMEOUT";
    case SYS_ERR_CALIB:   return "ERR_CALIB";
    case SYS_ERR_NO_SLOT: return "ERR_NO_SLOT";
    default:              return "ERR_UNKNOWN";
    }
}

/*
 * Абстракція апаратної шини I2C. Реалізацію підставляє платформа:
 * STM32 HAL/LL, ESP-IDF I2C driver, або програмний мок у модульних тестах.
 * Обидві операції — «регістрові»: адреса пристрою, адреса регістра, буфер.
 * Повертають true, якщо транзакція завершилась підтвердженням.
 */
typedef struct sys_i2c_bus {
    bool (*read_reg)(void *bus_ctx, uint8_t dev_addr, uint8_t reg,
                     uint8_t *buf, size_t len);
    bool (*write_reg)(void *bus_ctx, uint8_t dev_addr, uint8_t reg,
                      const uint8_t *buf, size_t len);
    void *bus_ctx;   /* непрозорий контекст конкретної реалізації */
} sys_i2c_bus_t;

/* Результат вимірювання у величинах SI — цілими, без плаваючої коми. */
typedef struct {
    int32_t temperature_centi_deg;  /* соті частки °C: 2508 = 25.08 °C */
    uint32_t pressure_pa;           /* Паскалі */
} sensor_data_t;

#endif /* SYS_I2C_H */
