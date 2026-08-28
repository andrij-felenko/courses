#include <cstdint>

/* Безпечна релокація таблиці векторів у C++ */
namespace mcu::system {
    inline void relocate_vector_table(std::uintptr_t new_base_address) noexcept {
        constexpr auto vtor_reg_addr = static_cast<std::uintptr_t>(0xE000ED08UL);
        auto* const scb_vtor = reinterpret_cast<volatile std::uint32_t*>(vtor_reg_addr);
        
        *scb_vtor = static_cast<std::uint32_t>(new_base_address);
        asm volatile("dsb\n\tisb" ::: "memory");
    }
}
