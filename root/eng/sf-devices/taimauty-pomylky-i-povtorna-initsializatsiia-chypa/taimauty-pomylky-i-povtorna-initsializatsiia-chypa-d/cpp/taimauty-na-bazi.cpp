#include <atomic>
#include <cstdint>

inline std::atomic<uint32_t> g_system_tick_ms{0};

extern "C" void SysTick_Handler() {
    g_system_tick_ms.fetch_add(1, std::memory_order_relaxed);
}

inline bool systick_timeout_is_expired(uint32_t start_tick, uint32_t timeout_ms) noexcept {
    return static_cast<uint32_t>(g_system_tick_ms.load(std::memory_order_relaxed) - start_tick) >= timeout_ms;
}
