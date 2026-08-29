/* chip_dev.h — дескриптор пристрою (Device Context).
 *
 * Увесь стан драйвера живе тут і тільки тут. У драйвері немає жодної
 * глобальної чи статичної змінної стану, тому два однакові чипи на різних
 * шинах — це просто два екземпляри цієї структури.
 *
 * Пам'ять під структуру виділяє викликач: статично в .bss, у пулі об'єктів
 * або на стеку задачі. Драйвер не звертається до купи ніколи.
 */
#ifndef CHIP_DEV_H
#define CHIP_DEV_H

#include <stdbool.h>
#include <stdint.h>

#include "chip_bus.h"
#include "chip_regs.h"

/* Заводські (або зняті на стенді) коефіцієнти корекції окремого екземпляра:
 * зміщення нуля в сирих відліках і масштабний коефіцієнт кожної осі. */
typedef struct {
    int16_t offset_raw[3]; /* що чип видає, лежачи нерухомо                   */
    float   gain[3];       /* 1.0f — корекції немає (шлях із FPU)             */
    int32_t gain_milli[3]; /* той самий коефіцієнт ×1000 для цілого шляху     */
} chip_calib_t;

typedef struct {
    float x; /* м/с² */
    float y;
    float z;
} chip_accel_si_t;

/* Той самий відлік для ядер без FPU: цілі мілігравітації. */
typedef struct {
    int32_t x; /* мг */
    int32_t y;
    int32_t z;
} chip_accel_mg_t;

/* Він же одразу в SI, але теж цілим: міліметри на секунду в квадраті. */
typedef struct {
    int32_t x; /* мм/с² */
    int32_t y;
    int32_t z;
} chip_accel_mm_s2_t;

typedef struct {
    /* --- 1. Апаратні хендли (Рівень 1) --- */
    const chip_bus_ops_t  *bus_ops;  /* читання/запис/пауза платформи         */
    const chip_gpio_ops_t *gpio_ops; /* лінії SCL/SDA для скидання; може NULL */
    void                  *user_ctx; /* непрозорий контекст платформи         */
    void                  *gpio_ctx; /* контекст ліній: часто той самий       */
    uint8_t                dev_addr; /* 7-бітна адреса I2C або індекс CS      */

    /* --- 2. Політика надійності транспорту --- */
    uint8_t  max_retries;    /* скільки разів повторити збиту транзакцію      */
    uint32_t retry_delay_ms; /* базова пауза між спробами (далі подвоюється)  */

    /* --- 3. Робоча конфігурація чипа --- */
    chip_range_t      range;
    chip_odr_t        odr;
    chip_resolution_t resolution;
    float             scale_si;  /* (м/с²) на відлік для поточного діапазону  */
    int32_t           scale_ug;  /* та сама чутливість у мікро-g на відлік    */

    /* --- 4. Тіньові копії регістрів конфігурації в ОЗП --- */
    uint8_t shadow_ctrl1;
    uint8_t shadow_ctrl3;
    uint8_t shadow_ctrl4;
    uint8_t shadow_ctrl5;
    uint8_t shadow_fifo_ctrl;

    /* --- 5. Калібрування й стан життєвого циклу --- */
    chip_calib_t calib;
    bool         is_initialized;
} chip_dev_t;

#endif /* CHIP_DEV_H */
