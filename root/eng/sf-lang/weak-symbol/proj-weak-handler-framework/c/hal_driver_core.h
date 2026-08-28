// ============================================================================
// ФАЙЛ: hal_driver_core.h (C99)
// ============================================================================
#ifndef HAL_DRIVER_CORE_H
#define HAL_DRIVER_CORE_H

#include "hal_event_types.h"

// Публічні слабкі точки розширення драйверів (Weak Callbacks)
__attribute__((weak)) void hal_uart_rx_callback(const hal_event_t* evt);
__attribute__((weak)) void hal_spi_transfer_callback(const hal_event_t* evt);
__attribute__((weak)) void hal_gpio_edge_callback(const hal_event_t* evt);
__attribute__((weak)) void hal_timer_period_callback(const hal_event_t* evt);
__attribute__((weak)) void hal_error_trap_callback(const hal_event_t* evt);

// Слабкі посилання на необов'язкові системні модулі (Weak References)
extern __attribute__((weak)) void hal_telemetry_publish_hook(const hal_event_t* evt);
extern __attribute__((weak)) bool hal_telemetry_crc_check_hook(const uint8_t* buf, size_t len);

// Диспетчер драйверного ядра
void hal_driver_init(void);
void hal_driver_dispatch_interrupt(hal_periph_id_t periph, hal_event_kind_t kind,
                                   const uint8_t* data, size_t len);

#endif // HAL_DRIVER_CORE_H
