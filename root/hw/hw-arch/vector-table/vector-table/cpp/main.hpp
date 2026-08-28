#include <cstdint>

namespace boot {

using entry_point_t = void (*)() noexcept;

inline void jump_to_application(uintptr_t app_base) noexcept {
    asm volatile ("cpsid i" : : : "memory");

    // Зупинка SysTick
    *reinterpret_cast<volatile uint32_t*>(0xE000E010) = 0;

    // Релокація VTOR
    *reinterpret_cast<volatile uint32_t*>(0xE000ED08) = static_cast<uint32_t>(app_base);

    asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");

    const auto stack_top = *reinterpret_cast<const uint32_t*>(app_base);
    const auto entry_addr = *reinterpret_cast<const uint32_t*>(app_base + sizeof(uint32_t));

    asm volatile ("msr msp, %0" : : "r"(stack_top) : "memory");

    auto entry_point = reinterpret_cast<entry_point_t>(entry_addr);
    entry_point();
}

} // namespace boot
