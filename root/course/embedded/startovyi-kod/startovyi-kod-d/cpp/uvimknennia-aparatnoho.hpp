#include <cstdint>

/* Увімкнення FPU у стилі C++ */
namespace mcu::hardware {
    inline void enable_fpu() noexcept {
        constexpr auto cpacr_addr = static_cast<std::uintptr_t>(0xE000ED88UL);
        auto* const scb_cpacr = reinterpret_cast<volatile std::uint32_t*>(cpacr_addr);
        
        constexpr std::uint32_t full_access_mask = (0xFUL << 20);
        *scb_cpacr |= full_access_mask;
        
        asm volatile("dsb\n\tisb" ::: "memory");
    }
}
