/* Уніфікований неблокуючий диспетчер шин I2C та SPI (STM32 HAL + DMA).
 *
 * Один екземпляр bus_t обслуговує ОДИН апаратний контролер: I2C1, SPI1, SPI2 тощо.
 * Клієнт кладе транзакцію в чергу й одразу повертається до своєї роботи — передачу
 * веде DMA, а завершення приходить колбеком із переривання.
 *
 * Буфери tx/rx належать клієнтові й мусять жити до виклику колбека: диспетчер
 * копіює лише сам опис транзакції, а не дані.
 */
#ifndef BUS_H
#define BUS_H

#include <stdbool.h>
#include <stdint.h>

#include "stm32h7xx_hal.h"

#define BUS_QUEUE_LEN           16u
#define BUS_MAX_CMD_BYTES        4u
#define BUS_DEFAULT_TIMEOUT_MS   5u

typedef enum {
    BUS_KIND_I2C,
    BUS_KIND_SPI
} bus_kind_t;

typedef enum {
    BUS_OP_READ,      /* команда -> дані від веденого */
    BUS_OP_WRITE,     /* команда + дані до веденого */
    BUS_OP_TRANSFER   /* повний дуплекс, лише SPI */
} bus_op_t;

typedef enum {
    BUS_OK = 0,
    BUS_ERR_HAL,        /* периферія відмовила або віддала помилку в ISR */
    BUS_ERR_TIMEOUT,    /* DMA мовчить довше за дозволене транзакції */
    BUS_ERR_BUS_LOCKED  /* лінію SDA не вдалося звільнити навіть розблокуванням */
} bus_result_t;

/* Лінії I2C у режимі GPIO — потрібні, щоб вручну відкачати завислу шину. */
typedef struct {
    GPIO_TypeDef *scl_port;
    uint16_t      scl_pin;
    GPIO_TypeDef *sda_port;
    uint16_t      sda_pin;
    uint8_t       alternate;  /* GPIO_AF4_I2C1 тощо — куди повернути піни після лікування */
} i2c_lines_t;

/* Розблокування шини за пасткою «I2C Bus Lockup»: 9 тактів SCL + ручний СТОП.
 * Реалізація — i2c_recovery.c. Повертає true, якщо SDA відпущено. */
bool i2c_bus_recover(I2C_HandleTypeDef *i2c, const i2c_lines_t *lines);

/* Опис веденого пристрою. Для I2C значуща лише адреса, для SPI — лінія CS
 * і власний режим тактування: диспетчер перемикає CPOL/CPHA ДО опускання CS. */
typedef struct {
    uint16_t      i2c_addr;       /* 7-бітна адреса, без зсуву вліво */
    GPIO_TypeDef *cs_port;
    uint16_t      cs_pin;
    uint32_t      spi_polarity;   /* SPI_POLARITY_LOW / SPI_POLARITY_HIGH */
    uint32_t      spi_phase;      /* SPI_PHASE_1EDGE / SPI_PHASE_2EDGE */
    uint32_t      spi_prescaler;  /* SPI_BAUDRATEPRESCALER_x */
} bus_device_t;

/* Колбек завершення. Викликається З КОНТЕКСТУ ПЕРЕРИВАННЯ — усередині можна
 * покласти в чергу наступну транзакцію, але не можна чекати чи блокуватися. */
typedef void (*bus_done_fn)(bus_result_t result, void *ctx);

typedef struct {
    const bus_device_t *dev;
    bus_op_t            op;
    uint8_t             cmd[BUS_MAX_CMD_BYTES];  /* адреса регістра або команда чипа */
    uint8_t             cmd_len;                 /* 0 — звертання без регістра */
    const uint8_t      *tx;
    uint8_t            *rx;
    uint16_t            len;
    uint16_t            timeout_ms;              /* 0 — узяти BUS_DEFAULT_TIMEOUT_MS */
    bus_done_fn         done;
    void               *ctx;
} bus_txn_t;

typedef enum {
    BUS_PHASE_IDLE,
    BUS_PHASE_CMD,    /* SPI: віддаємо байти команди, CS уже притиснуто */
    BUS_PHASE_DATA
} bus_phase_t;

typedef struct {
    bus_kind_t   kind;
    void        *handle;          /* I2C_HandleTypeDef* або SPI_HandleTypeDef* */
    i2c_lines_t  lines;           /* значуще лише для BUS_KIND_I2C */

    bus_txn_t    queue[BUS_QUEUE_LEN];
    volatile uint8_t     head;
    volatile uint8_t     tail;
    volatile bool        busy;
    volatile bus_phase_t phase;
    volatile bool        needs_recovery;
    uint32_t     started_ms;

    uint32_t stat_done;
    uint32_t stat_failed;
    uint32_t stat_dropped;    /* скільки транзакцій відкинуто через повну чергу */
    uint32_t stat_recovered;
} bus_t;

void bus_init_i2c(bus_t *bus, I2C_HandleTypeDef *i2c, const i2c_lines_t *lines);
void bus_init_spi(bus_t *bus, SPI_HandleTypeDef *spi);

/* Кладе транзакцію в чергу; false — черга переповнена (клієнт занадто швидкий). */
bool bus_submit(bus_t *bus, const bus_txn_t *txn);

/* Викликати з головного циклу: нагляд за таймаутом і відкладене лікування I2C. */
void bus_poll(bus_t *bus);

#endif /* BUS_H */
