// main.cpp — користувацький сильний обробник переривання на C++20
#include <cstdint>
#include <atomic>

namespace {
    std::atomic<std::uint32_t> g_system_ticks{0};
}

extern "C" {

// Сильне визначення SysTick_Handler (STB_GLOBAL)
void SysTick_Handler() noexcept
{
    g_system_ticks.fetch_add(1, std::memory_order_relaxed);
}

} // extern "C"
