#include <cstdint>
#include <concepts>
#include <span>

namespace bootloader {

inline void disable_interrupts() noexcept {
    asm volatile ("cpsid i" : : : "memory");
}

inline void set_msp(uint32_t stack_top) noexcept {
    asm volatile ("msr msp, %0" : : "r"(stack_top) : "memory");
}

inline void dsb() noexcept { asm volatile ("dsb 0xF" : : : "memory"); }
inline void isb() noexcept { asm volatile ("isb 0xF" : : : "memory"); }

class firmware_launcher {
public:
    explicit constexpr firmware_launcher(uintptr_t base_address) noexcept
        : app_base_(base_address) {}

    [[nodiscard]] bool is_valid() const noexcept {
        const auto stack_top = *reinterpret_cast<const uint32_t*>(app_base_);
        const auto entry_addr = *reinterpret_cast<const uint32_t*>(app_base_ + sizeof(uint32_t));

        const bool valid_stack = (stack_top >= 0x20000000UL) && (stack_top <= 0x20040000UL);
        const bool valid_entry = (entry_addr >= app_base_) && (entry_addr < 0x08080000UL) && ((entry_addr & 1UL) != 0);

        return valid_stack && valid_entry;
    }

    [[noreturn]] void launch() const noexcept {
        const auto stack_top = *reinterpret_cast<const uint32_t*>(app_base_);
        const auto entry_addr = *reinterpret_cast<const uint32_t*>(app_base_ + sizeof(uint32_t));

        disable_interrupts();

        // Зупинка SysTick
        auto* const systick_ctrl = reinterpret_cast<uint32_t*>(0xE000E010);
        auto* const systick_load = reinterpret_cast<uint32_t*>(0xE000E014);
        auto* const systick_val  = reinterpret_cast<uint32_t*>(0xE000E018);
        *systick_ctrl = 0;
        *systick_load = 0;
        *systick_val  = 0;

        // Скидання NVIC
        auto* const nvic_icer = reinterpret_cast<uint32_t*>(0xE000E180);
        auto* const nvic_icpr = reinterpret_cast<uint32_t*>(0xE000E280);
        for (std::size_t i = 0; i < 8; ++i) {
            nvic_icer[i] = 0xFFFFFFFFUL;
            nvic_icpr[i] = 0xFFFFFFFFUL;
        }

        // Встановлення VTOR
        auto* const scb_vtor = reinterpret_cast<uint32_t*>(0xE000ED08);
        *scb_vtor = static_cast<uint32_t>(app_base_);

        dsb();
        isb();

        set_msp(stack_top);

        using reset_fn = void (*)() noexcept;
        auto entry_point = reinterpret_cast<reset_fn>(entry_addr);
        entry_point();

        while (true) {
            // Запобіжник у разі збою
        }
    }

private:
    uintptr_t app_base_;
};

} // namespace bootloader
