/* i2c_scan.h — прохід адресного простору I2C під час оживлення плати.
   Модуль нічого не друкує: він лише стукає в шину й складає звіт.
   Друк і тлумачення результату — справа того, хто цей звіт замовив. */
#ifndef I2C_SCAN_H
#define I2C_SCAN_H

#include <stdbool.h>
#include <stdint.h>

#include "stm32f4xx_hal.h"

/* Стандарт лишає 0x00..0x07 і 0x78..0x7F під службові потреби
   (загальний виклик, 10-бітна адресація), тож скануємо лише середину. */
#define I2C_ADDR_FIRST 0x08u
#define I2C_ADDR_LAST  0x77u
#define I2C_ADDR_COUNT (I2C_ADDR_LAST - I2C_ADDR_FIRST + 1u)

typedef enum {
    I2C_PROBE_ACK = 0, /* ведений притиснув SDA на 9-му такті */
    I2C_PROBE_NACK,    /* тиша: за цією адресою нікого немає */
    I2C_PROBE_BUSY,    /* лінія не звільняється — схоже на залипання SDA */
    I2C_PROBE_ERROR    /* BERR/ARLO: електричний збій усередині кадру */
} i2c_probe_t;

typedef struct {
    uint8_t addr7;      /* 7-бітний ідентифікатор, як його друкує даташит */
    uint8_t write_byte; /* addr7 << 1       — байт у кадрі для запису */
    uint8_t read_byte;  /* (addr7 << 1) | 1 — той самий байт для читання */
} i2c_device_t;

typedef struct {
    i2c_device_t found[I2C_ADDR_COUNT];
    uint8_t  found_count;
    uint16_t probed;    /* скільки адрес встигли опитати */
    uint16_t errors;    /* скільки проб завершилися збоєм шини */
    bool     bus_stuck; /* прохід обірвано: шина не віддає керування */
} i2c_scan_report_t;

/* Одна проба: START + адресний байт + очікування ACK на дев'ятому такті.
   Залишковий стан помилки HAL скидається всередині, тож наступну адресу
   можна пробувати одразу після повернення. */
i2c_probe_t i2c_probe(I2C_HandleTypeDef *bus, uint8_t addr7);

/* Повний прохід 0x08..0x77. Повертає false, якщо прохід обірвано через
   зависання шини; звіт при цьому заповнений тим, що встигли зібрати. */
bool i2c_scan(I2C_HandleTypeDef *bus, i2c_scan_report_t *report);

/* Залипла в нулі SDA підтверджує ACK на КОЖНІЙ адресі: якщо «знайдено»
   підозріло багато пристроїв, вірити такому проходові не можна. */
bool i2c_scan_looks_fake(const i2c_scan_report_t *report);

#endif /* I2C_SCAN_H */
