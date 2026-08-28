// ============================================================================
// ФАЙЛ: hal_driver_core.hpp (C++20)
// ============================================================================
#pragma once

#include "hal_event_types.hpp"

extern "C" {

// C-ABI сумісні слабкі точки розширення
[[gnu::weak]] void hal_uart_rx_callback_c(const void* evt);
[[gnu::weak]] void hal_spi_transfer_callback_c(const void* evt);
[[gnu::weak]] void hal_gpio_edge_callback_c(const void* evt);
[[gnu::weak]] void hal_timer_period_callback_c(const void* evt);
[[gnu::weak]] void hal_error_trap_callback_c(const void* evt);

// Слабкі посилання на опціональну телеметрію
[[gnu::weak]] void hal_telemetry_publish_hook_c(const void* evt);
[[gnu::weak]] bool hal_telemetry_crc_check_hook_c(const std::uint8_t* buf, std::size_t len);

} // extern "C"

namespace hal::core {

void initialize() noexcept;
void dispatch_interrupt(PeripheralId periph, EventKind kind,
                        std::span<const std::byte> data) noexcept;

} // namespace hal::core
