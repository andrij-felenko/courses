// ============================================================================
// ФАЙЛ: hal_driver_core.cpp (C++20)
// ============================================================================
#include "hal_driver_core.hpp"
#include <iostream>
#include <atomic>

namespace {
    std::atomic<std::uint32_t> g_system_tick_mock{1000};
}

extern "C" {

void hal_default_event_stub_c(const void* evt) noexcept
{
    (void)evt;
}

void hal_default_error_trap_c(const void* evt) noexcept
{
    const auto* e = static_cast<const hal::Event*>(evt);
    if (e) {
        std::cout << "[HAL CORE FATAL C++] Помилка периферії: "
                  << static_cast<int>(e->periph) << '\n';
    }
}

void hal_uart_rx_callback_c(const void* evt) noexcept
    [[gnu::weak, gnu::alias("hal_default_event_stub_c")]];

void hal_spi_transfer_callback_c(const void* evt) noexcept
    [[gnu::weak, gnu::alias("hal_default_event_stub_c")]];

void hal_gpio_edge_callback_c(const void* evt) noexcept
    [[gnu::weak, gnu::alias("hal_default_event_stub_c")]];

void hal_timer_period_callback_c(const void* evt) noexcept
    [[gnu::weak, gnu::alias("hal_default_event_stub_c")]];

void hal_error_trap_callback_c(const void* evt) noexcept
    [[gnu::weak, gnu::alias("hal_default_error_trap_c")]];

} // extern "C"

namespace hal::core {

void initialize() noexcept
{
    std::cout << "[HAL CORE C++20] Ініціалізація диспетчера зворотних викликів.\n";
}

void dispatch_interrupt(PeripheralId periph, EventKind kind,
                        std::span<const std::byte> data) noexcept
{
    Event evt{
        .periph = periph,
        .kind = kind,
        .timestamp_us = g_system_tick_mock.fetch_add(1, std::memory_order_relaxed),
        .payload = data,
        .flags = 0
    };

    if (hal_telemetry_crc_check_hook_c != nullptr) {
        if (!data.empty()) {
            const auto* raw = reinterpret_cast<const std::uint8_t*>(data.data());
            if (!hal_telemetry_crc_check_hook_c(raw, data.size())) {
                evt.kind = EventKind::ErrorHardware;
                hal_error_trap_callback_c(&evt);
                return;
            }
        }
    }

    switch (periph) {
    case PeripheralId::Uart1:
    case PeripheralId::Uart2:
        hal_uart_rx_callback_c(&evt);
        break;
    case PeripheralId::Spi1:
        hal_spi_transfer_callback_c(&evt);
        break;
    case PeripheralId::Gpio:
        hal_gpio_edge_callback_c(&evt);
        break;
    case PeripheralId::Timer:
        hal_timer_period_callback_c(&evt);
        break;
    default:
        hal_error_trap_callback_c(&evt);
        break;
    }

    if (hal_telemetry_publish_hook_c != nullptr) {
        hal_telemetry_publish_hook_c(&evt);
    }
}

} // namespace hal::core
