#include <cstdint>
#include "stm32f4xx.h"

namespace fault {

struct alignas(4) StackRegisters {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
};

extern "C" void HardFault_Decoder_Cpp(const StackRegisters *regs, uint32_t exc_return) noexcept {
    const uint32_t fault_pc = regs ? regs->pc : 0;
    const uint32_t fault_lr = regs ? regs->lr : 0;
    const uint32_t hfsr = SCB->HFSR;
    const uint32_t cfsr = SCB->CFSR;
    const uint32_t bfar = (cfsr & SCB_CFSR_BFARVALID_Msk) ? SCB->BFAR : 0;

    (void)fault_pc;
    (void)fault_lr;
    (void)hfsr;
    (void)cfsr;
    (void)bfar;
    (void)exc_return;

    NVIC_SystemReset();
}

} // namespace fault

extern "C" __attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4                \n"
        "ite eq                    \n"
        "mrseq r0, msp             \n"
        "mrsne r0, psp             \n"
        "mov r1, lr                \n"
        "b HardFault_Decoder_Cpp   \n"
    );
}
