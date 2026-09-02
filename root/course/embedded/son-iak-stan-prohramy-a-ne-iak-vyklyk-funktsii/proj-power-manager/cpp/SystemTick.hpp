// SystemTick.hpp — лічильник часу планувальника з бестіковим простоєм.
#pragma once

#include <chrono>
#include <cstdint>

namespace emb::hal {

class SystemTick {
public:
    static void init(std::uint32_t sysclkHz) noexcept;

    [[nodiscard]] static std::chrono::milliseconds now() noexcept;

    // Глушить SysTick на час глибокого сну: інакше він розбудить ядро
    // через мілісекунду й уся економія піде на перезапуск PLL.
    static void suspend() noexcept;

    // Повертає тік і додає проспаний час — планувальник не бачить пропуску.
    static void resume(std::chrono::milliseconds slept) noexcept;

    // Скільки лишилося до дедлайну; різниця рахується зі знаком,
    // тож перехід лічильника через 2^32 нічого не ламає.
    [[nodiscard]] static std::chrono::milliseconds until(std::chrono::milliseconds deadline) noexcept;

    static void onTick() noexcept { ++s_ms; }

private:
    static inline volatile std::uint32_t s_ms{0};
};

} // namespace emb::hal
