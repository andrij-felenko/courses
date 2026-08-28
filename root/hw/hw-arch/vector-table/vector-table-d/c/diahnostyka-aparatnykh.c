#include <stdint.h>

/* Структура збереженого апаратурою стек-фрейму */
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
} hw_stack_frame_t;

/* C-функція аналізу стану ядра */
void hard_fault_handler_c(hw_stack_frame_t *frame, uint32_t lr_value) {
    volatile uint32_t hfsr = *(volatile uint32_t*)0xE000ED2C;
    volatile uint32_t cfsr = *(volatile uint32_t*)0xE000ED28;
    volatile uint32_t bfar = *(volatile uint32_t*)0xE000ED38;
    volatile uint32_t mmar = *(volatile uint32_t*)0xE000ED34;

    /* Регістри аварійного стану доступні для аналізу або збереження в EEPROM / RTC RAM */
    (void)frame;
    (void)lr_value;
    (void)hfsr;
    (void)cfsr;
    (void)bfar;
    (void)mmar;

    while (1) {
        __asm__ volatile ("bkpt #0"); /* Зупинка відлагоджувача */
    }
}

/* Асемблерний трамплін для вибору активного покажчика стека */
__attribute__((naked)) void HardFault_Handler(void) {
    __asm__ volatile (
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "mov r1, lr\n"
        "b hard_fault_handler_c\n"
    );
}
