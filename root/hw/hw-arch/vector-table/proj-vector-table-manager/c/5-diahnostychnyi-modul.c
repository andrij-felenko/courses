#include "vector_table_types.h"

#define SCB_HFSR_REG         (*(volatile uint32_t*)0xE000ED2CUL)
#define SCB_CFSR_REG         (*(volatile uint32_t*)0xE000ED28UL)
#define SCB_BFAR_REG         (*(volatile uint32_t*)0xE000ED38UL)
#define SCB_MMFAR_REG        (*(volatile uint32_t*)0xE000ED34UL)
#define SCB_AFSR_REG         (*(volatile uint32_t*)0xE000ED3CUL)

/* Область Backup SRAM для збереження дампу аварії */
static hardfault_crash_report_t persistent_crash_dump;

void hard_fault_diagnostic_c(const exception_stack_frame_t *frame, uint32_t exc_return) {
    persistent_crash_dump.frame = *frame;
    persistent_crash_dump.exc_return_code = exc_return;

    persistent_crash_dump.hfsr = SCB_HFSR_REG;
    persistent_crash_dump.cfsr = SCB_CFSR_REG;
    persistent_crash_dump.bfar = SCB_BFAR_REG;
    persistent_crash_dump.mmar = SCB_MMFAR_REG;
    persistent_crash_dump.afsr = SCB_AFSR_REG;

    persistent_crash_dump.bfar_valid = (persistent_crash_dump.cfsr & (1UL << 15)) != 0;
    persistent_crash_dump.mmar_valid = (persistent_crash_dump.cfsr & (1UL << 7)) != 0;
    persistent_crash_dump.is_psp_active = (exc_return & (1UL << 2)) != 0;

    /* Зупинка відлагоджувача через апаратну інструкцію BKPT */
    while (1) {
        __asm__ volatile ("bkpt #1");
    }
}

__attribute__((naked)) void HardFault_Handler(void) {
    __asm__ volatile (
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "mov r1, lr\n"
        "b hard_fault_diagnostic_c\n"
    );
}

const hardfault_crash_report_t* hardfault_get_last_crash_dump(void) {
    return &persistent_crash_dump;
}
