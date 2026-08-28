// ============================================================================
// ФАЙЛ: app_main.cpp (C++20) — користувацький модуль із сильними перекриттями
// ============================================================================
#include "hal_driver_core.hpp"
#include <iostream>
#include <array>
#include <atomic>

namespace {
    constexpr std::size_t RingBufferSize = 128;
    std::array<std::uint8_t, RingBufferSize> g_rx_ring_buffer{};
    std::size_t g_rx_head = 0;
    std::atomic<std::uint32_t> g_button_press_count{0};
}

extern "C" {

// СИЛЬНЕ ПЕРЕКРИТТЯ: обробка байтів UART
void hal_uart_rx_callback_c(const void* evt) noexcept
{
    std::cout << "[APP C++20] Сильний обробник UART RX активовано!\n";
    const auto* e = static_cast<const hal::Event*>(evt);
    if (e && !e->payload.empty()) {
        for (auto byte : e->payload) {
            g_rx_ring_buffer[g_rx_head] = static_cast<std::uint8_t>(byte);
            g_rx_head = (g_rx_head + 1) % RingBufferSize;
        }
        std::cout << "  -> Збережено " << e->payload.size() << " байтів у кільцевий буфер.\n";
    }
}

// СИЛЬНЕ ПЕРЕКРИТТЯ: обробка кнопки
void hal_gpio_edge_callback_c(const void* evt) noexcept
{
    auto count = g_button_press_count.fetch_add(1, std::memory_order_relaxed) + 1;
    std::cout << "[APP C++20] Кнопку натиснуто! Загальний лічильник: " << count << '\n';
}

} // extern "C"
