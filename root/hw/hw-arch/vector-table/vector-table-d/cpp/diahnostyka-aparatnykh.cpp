#include <cstdint>
#include <span>

namespace diagnostics {

struct alignas(4) stack_frame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
};

struct fault_registers {
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t bfar;
    uint32_t mmar;
};

extern "C" void hard_fault_decoder(const stack_frame* frame, uintptr_t exc_return) noexcept {
    const fault_registers regs{
        .hfsr = *reinterpret_cast<const volatile uint32_t*>(0xE000ED2C),
        .cfsr = *reinterpret_cast<const volatile uint32_t*>(0xE000ED28),
        .bfar = *reinterpret_cast<const volatile uint32_t*>(0xE000ED38),
        .mmar = *reinterpret_cast<const volatile uint32_t*>(0xE000ED34)
    };

    // Запобігання видаленню компілятором при оптимізації
    asm volatile ("" : : "r"(frame), "r"(&regs), "r"(exc_return) : "memory");

    while (true) {
        asm volatile ("bkpt #0");
    }
}

extern "C" [[gnu::naked]] void HardFault_Handler() noexcept {
    asm volatile (
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "mov r1, lr\n"
        "b hard_fault_decoder\n"
    );
}

} // namespace diagnostics
