#ifndef BSP_PORT_H
#define BSP_PORT_H

#include "bsp/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Порт BSP — вузька межа вниз, до вендорного шару (HAL/LL, регістри, RTOS).
 * Усе, чого BSP вимагає від платформи, перелічено ТУТ; перенесення плати на
 * інший мікроконтролер — це переписати реалізацію цього файла, не чіпаючи
 * ані board.c, ані застосунок.
 */

/** Умовні номери портів GPIO у нотації плати. */
#define BSP_GPIO_PORT_A 0u
#define BSP_GPIO_PORT_B 1u
#define BSP_GPIO_PORT_C 2u

/** Канал АЦП внутрішнього опорного джерела (платформозалежний). */
#define BSP_PORT_ADC_CH_VREFINT 17u

/** Фізичний вивід: порт + номер лінії. */
typedef struct {
    uint8_t port;
    uint8_t pin;
} bsp_pin_t;

/** Режими виводу, потрібні BSP. */
typedef enum {
    BSP_PIN_MODE_ANALOG = 0,  /**< Hi-Z без підтяжок і без вхідного буфера (нуль витоку) */
    BSP_PIN_MODE_INPUT,       /**< Цифровий вхід без підтяжки */
    BSP_PIN_MODE_INPUT_PU,    /**< Цифровий вхід із внутрішньою підтяжкою до VDD */
    BSP_PIN_MODE_OUTPUT_PP,   /**< Двотактний вихід */
    BSP_PIN_MODE_OUTPUT_OD,   /**< Вихід із відкритим стоком */
    BSP_PIN_MODE_ALTERNATE    /**< Вивід віддано периферії (I2C, SPI, UART) */
} bsp_pin_mode_t;

/** Тактування: перехід на штатну частоту з HSE; до 50 мс. */
bsp_status_t bsp_port_clock_init(void);

void bsp_port_pin_mode(bsp_pin_t pin, bsp_pin_mode_t mode);
void bsp_port_pin_write(bsp_pin_t pin, bool level);
bool bsp_port_pin_read(bsp_pin_t pin);

/** Підняти/погасити контролер I2C і віддати/забрати його виводи. */
bsp_status_t bsp_port_i2c_init(void);
void bsp_port_i2c_deinit(void);

/*
 * Транзакції I2C. Тайм-аут відповіді — усередині порту; він же розрізняє
 * мовчання (BSP_STATUS_ERR_TIMEOUT) і збій лінії чи NACK (ERR_BUS_FAULT).
 */
bsp_status_t bsp_port_i2c_write(uint8_t addr, const uint8_t *tx, size_t tx_len);
bsp_status_t bsp_port_i2c_read(uint8_t addr, uint8_t *rx, size_t rx_len);
bsp_status_t bsp_port_i2c_write_read(uint8_t addr,
                                     const uint8_t *tx, size_t tx_len,
                                     uint8_t *rx, size_t rx_len);

bsp_status_t bsp_port_adc_init(void);
void bsp_port_adc_deinit(void);

/** Оцифрування каналу з апаратним усередненням 16 вибірок; 12 біт. */
bsp_status_t bsp_port_adc_read_avg16(uint8_t channel, uint16_t *out_raw);

/** Заводська константа Vrefint (код АЦП, знятий на 3.000 В при 30 °C). */
uint16_t bsp_port_vrefint_cal(void);

uint32_t bsp_port_tick_ms(void);
void bsp_port_delay_us(uint32_t us);

/*
 * М'ютекс спільної шини з успадкуванням пріоритетів. У складанні без RTOS —
 * прапорець зайнятості. Тайм-аут дає BSP_STATUS_ERR_BUSY.
 */
bsp_status_t bsp_port_bus_lock(uint32_t timeout_ms);
void bsp_port_bus_unlock(void);

/** Дочекатися спустошення черг UART і завершення активних передач DMA. */
bsp_status_t bsp_port_flush_async_io(uint32_t timeout_ms);

/** Зупинити ядро до пробудження від RTC або зовнішньої лінії. */
bsp_status_t bsp_port_enter_stop(bool deep, uint32_t timeout_ms);

/** Чи виконується код у контексті обробника переривання. */
bool bsp_port_in_isr(void);

#ifdef __cplusplus
}
#endif

#endif /* BSP_PORT_H */
