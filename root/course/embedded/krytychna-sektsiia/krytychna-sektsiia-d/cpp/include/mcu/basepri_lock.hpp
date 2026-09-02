// Політика селективного маскування: блокуємо лише переривання рівня ОС,
// а обробники 0..4 (аварія за струмом, ШІМ, енкодер) працюють далі.
#pragma once

#include <cstdint>

#include "mcu/cpu.hpp"

namespace mcu {

static_assert(cpu::kHasBasepri,
              "Cortex-M0/M0+ не має BASEPRI — на цих ядрах беріть PrimaskLock");

// Той самий поріг, що його FreeRTOS тримає в configMAX_SYSCALL_INTERRUPT_PRIORITY.
// Пріоритет NVIC живе в СТАРШИХ бітах байта, тому число зсунуте.
inline constexpr std::uint32_t kMaxSyscallPriority = 5U << (8U - cpu::kNvicPrioBits);

static_assert(kMaxSyscallPriority != 0U,
              "BASEPRI = 0 означає «маскування вимкнено»: секція вийшла б порожньою");

struct BasepriLock {
    using state_type = std::uint32_t;

    [[nodiscard]] static state_type enter() noexcept
    {
        const state_type saved = cpu::basepri();
        cpu::set_basepri_max(kMaxSyscallPriority);
        cpu::barrier();
        return saved;
    }

    static void exit(state_type saved) noexcept
    {
        cpu::barrier();
        cpu::set_basepri(saved);
    }

    static constexpr bool blocks_zero_latency_isr = false;
};

// Чи має обробник із таким пріоритетом право звертатися до API ОС.
// Перевірку зручно робити на етапі компіляції, поруч із таблицею пріоритетів.
[[nodiscard]] constexpr bool may_call_rtos_api(std::uint32_t nvic_priority) noexcept
{
    return (nvic_priority << (8U - cpu::kNvicPrioBits)) >= kMaxSyscallPriority;
}

static_assert(!may_call_rtos_api(0U), "аварійний ISR нульового пріоритету API ОС не кличе");
static_assert(may_call_rtos_api(6U), "обробник UART рівня ОС має право ставити в чергу");

} // namespace mcu
