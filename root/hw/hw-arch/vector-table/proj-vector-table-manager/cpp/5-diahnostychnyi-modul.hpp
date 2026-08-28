#pragma once

#include "vector_table_types.h"

namespace vtm::diagnostics {

class fault_analyzer {
public:
    static void capture_and_halt(const exception_frame* frame, uintptr_t exc_return) noexcept {
        const uint32_t cfsr_val = *reinterpret_cast<const volatile uint32_t*>(0xE000ED28);
        
        last_report_ = crash_report{
            .frame = *frame,
            .exc_return = exc_return,
            .hfsr = *reinterpret_cast<const volatile uint32_t*>(0xE000ED2C),
            .cfsr = cfsr_val,
            .bfar = *reinterpret_cast<const volatile uint32_t*>(0xE000ED38),
            .mmar = *reinterpret_cast<const volatile uint32_t*>(0xE000ED34),
            .afsr = *reinterpret_cast<const volatile uint32_t*>(0xE000ED3C),
            .bfar_valid = (cfsr_val & (1UL << 15)) != 0,
            .mmar_valid = (cfsr_val & (1UL << 7)) != 0,
            .used_psp = (exc_return & (1UL << 2)) != 0,
            .timestamp = 0
        };

        asm volatile ("" : : "r"(&last_report_) : "memory");

        while (true) {
            asm volatile ("bkpt #1");
        }
    }

    [[nodiscard]] static const crash_report& get_report() noexcept {
        return last_report_;
    }

private:
    static inline crash_report last_report_{};
};

} // namespace vtm::diagnostics

extern "C" [[gnu::naked]] void HardFault_Handler() noexcept {
    asm volatile (
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "mov r1, lr\n"
        "b _ZN3vtm11diagnostics14fault_analyzer16capture_and_haltEPKNS_15exception_frameEj\n"
    );
}
