// Політика повного маскування. Зберігає PRIMASK на вході й повертає САМЕ ЙОГО
// на виході, тому вкладення будь-якої глибини лишається безпечним: вкладена
// секція відновлює одиницю, а не «увімкнути все».
#pragma once

#include <cstdint>

#include "mcu/cpu.hpp"

namespace mcu {

struct PrimaskLock {
    using state_type = std::uint32_t;

    [[nodiscard]] static state_type enter() noexcept
    {
        const state_type saved = cpu::primask(); // 1. що було до нас
        cpu::disable_irq();                      // 2. CPSID i
        cpu::barrier();                          // 3. оптимізатор лишається за межею
        return saved;
    }

    static void exit(state_type saved) noexcept
    {
        cpu::barrier();          // 4. усі записи вже дійшли до памʼяті
        cpu::set_primask(saved); // 5. рівно той стан, який був
    }

    // Ціна політики: жоден обробник, навіть аварійний, не виконається,
    // доки секція не завершиться.
    static constexpr bool blocks_zero_latency_isr = true;
};

} // namespace mcu
