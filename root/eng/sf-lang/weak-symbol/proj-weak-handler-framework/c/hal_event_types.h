// ============================================================================
// ФАЙЛ: hal_event_types.h (C99)
// ============================================================================
#ifndef HAL_EVENT_TYPES_H
#define HAL_EVENT_TYPES_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_PERIPH_UART1 = 0,
    HAL_PERIPH_UART2 = 1,
    HAL_PERIPH_SPI1  = 2,
    HAL_PERIPH_DMA1  = 3,
    HAL_PERIPH_GPIO  = 4,
    HAL_PERIPH_TIMER = 5
} hal_periph_id_t;

typedef enum {
    HAL_EVT_RX_READY       = 0x01,
    HAL_EVT_TX_COMPLETE    = 0x02,
    HAL_EVT_TRANSFER_DONE  = 0x03,
    HAL_EVT_PIN_EDGE       = 0x04,
    HAL_EVT_PERIOD_ELAPSED = 0x05,
    HAL_EVT_ERROR_OVERRUN  = 0x0E,
    HAL_EVT_ERROR_HARDWARE = 0x0F
} hal_event_kind_t;

typedef struct {
    hal_periph_id_t  periph;
    hal_event_kind_t kind;
    uint32_t         timestamp_us;
    const uint8_t*   payload;
    size_t           length;
    uint32_t         flags;
} hal_event_t;

#endif // HAL_EVENT_TYPES_H
