// Наївна критична секція: вимкнули все, зробили, увімкнули все.
// Працює рівно доти, доки функцію ніхто не викликає зсередини іншої секції.
#include <cstdint>

#include "demo/demos.hpp"
#include "mcu/cpu.hpp"

namespace {

volatile std::uint32_t g_system_flags{0};
constexpr std::uint32_t kFlagButton = 1U << 0;

} // namespace

namespace demo {

void update_system_state(std::uint32_t flags) noexcept
{
    mcu::cpu::disable_irq(); // CPSID i
    g_system_flags = g_system_flags | flags;
    mcu::cpu::enable_irq(); // CPSIE i — безумовно, хай що було до входу
}

std::uint32_t system_flags() noexcept { return g_system_flags; }

} // namespace demo

extern "C" void EXTI0_IRQHandler()
{
    g_system_flags = g_system_flags | kFlagButton;
}
