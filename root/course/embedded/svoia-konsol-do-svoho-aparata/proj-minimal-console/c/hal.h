#ifndef HAL_H
#define HAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Контракт із платою. Усе, що нижче, реалізує BSP конкретного мікроконтролера
// (ESP32-S3 або STM32G4); прошивка пульта нижче цього рівня не лізе.

// Буфери, у які пише DMA, мусять лежати у внутрішній SRAM і бути вирівняні
// на рядок кешу — інакше інвалідація зачепить сусідні дані.
#define HAL_DMA_ATTR __attribute__((aligned(32)))

#define HAL_ADC_AXES 4
#define HAL_LCD_COLS 128

typedef enum {
    PIN_RADIO_NSS = 0,
    PIN_RADIO_BUSY,
    PIN_RADIO_RESET,
    PIN_RADIO_DIO1,
    PIN_POWER_LATCH,
    PIN_RAIL_GOOD
} hal_pin_t;

// Тумблери й кнопки, як вони приходять з hal_switch_bits().
#define SW_ARM        0x0001
#define SW_RATE_HIGH  0x0002
#define SW_PAYLOAD    0x0004
#define SW_PAY_UP     0x0008
#define SW_PAY_DN     0x0010

void hal_board_init(void);   // такти, GPIO, SPI 18 МГц Mode 0, АЦП + DMA
void hal_gpio_write(hal_pin_t pin, bool level);
bool hal_gpio_read(hal_pin_t pin);

// Обмін по SPI через DMA, блокує до кінця транзакції; rx може бути NULL.
void hal_spi_xfer(const uint8_t *tx, uint8_t *rx, size_t len);

uint32_t hal_micros(void);
uint32_t hal_millis(void);
void hal_delay_us(uint32_t us);

// Когерентність кешу даних: DMA ходить повз L1 ядра.
void hal_cache_invalidate(const void *addr, size_t len);
void hal_cache_writeback(const void *addr, size_t len);

// Буфер injected-АЦП: чотири осі Холла, наповнює DMA за стробом таймера.
const uint16_t *hal_adc_axes(void);
uint16_t hal_adc_vbat_raw(void);

uint16_t hal_switch_bits(void);
void hal_haptic(uint8_t duty);          // вібромотор, 0..255

void hal_timer_start_1khz(void (*isr)(void));
void hal_watchdog_start(uint32_t timeout_ms);
void hal_watchdog_kick(void);

// Одна сторінка дисплея: 128 байтів, кожен — вісім вертикальних пікселів.
void hal_display_page(uint8_t page, const uint8_t *cols, size_t len);

#endif
