#include <cstdint>
#include <concepts>

namespace arch::riscv {

enum class mtvec_mode : uintptr_t {
    direct   = 0x00,
    vectored = 0x01
};

extern "C" {
    void riscv_trap_entry();
    alignas(128) void riscv_vector_table();
}

class trap_manager {
public:
    static void set_mode(uintptr_t base_address, mtvec_mode mode) noexcept {
        const uintptr_t reg_val = (base_address & ~static_cast<uintptr_t>(0x03)) |
                                  static_cast<uintptr_t>(mode);
        
        asm volatile ("csrw mtvec, %0" : : "r"(reg_val) : "memory");
    }

    static void enable_direct_mode() noexcept {
        set_mode(reinterpret_cast<uintptr_t>(&riscv_trap_entry), mtvec_mode::direct);
    }

    static void enable_vectored_mode() noexcept {
        set_mode(reinterpret_cast<uintptr_t>(&riscv_vector_table), mtvec_mode::vectored);
    }
};

} // namespace arch::riscv
