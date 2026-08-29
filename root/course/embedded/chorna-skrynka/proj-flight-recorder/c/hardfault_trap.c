/* hardfault_trap.c — перехоплювач фатальних винятків ARM Cortex-M.
 * Ланцюжок один: витягти стековий кадр -> записати три кадри аварії ->
 * вивантажити том у FRAM -> скинути ядро. */
#include "flight_recorder_core.h"
#include "spi_emergency_dump.h"
#include "mcu_port.h"

/* Адреса слота дампа в енергонезалежному носії. */
#define BLACKBOX_NV_SLOT_ADDR 0x000000U

/* Обробник викликає цю функцію з двома аргументами: r0 — покажчик на
 * апаратний стековий кадр, r1 — EXC_RETURN, за яким видно, чий це був стек. */
void prvGetRegistersFromStack(uint32_t* stack_frame, uint32_t exc_return) {
    BlackBoxFault_t fault;

    /* Апаратний кадр: R0, R1, R2, R3, R12, LR, PC, xPSR */
    fault.lr  = stack_frame[5];
    fault.pc  = stack_frame[6];
    fault.psr = stack_frame[7];
    fault.exc_return = exc_return;

    fault.cfsr = mcu_reg_read(SCB_CFSR_ADDR);
    fault.hfsr = mcu_reg_read(SCB_HFSR_ADDR);

    /* MMFAR і BFAR тримають сміття, доки не стоїть їхній біт дійсності:
     * записати їх наосліп означає надіслати слідчого хибним слідом. */
    fault.fault_addr = 0U;
    fault.addr_valid = 0U;
    if ((fault.cfsr & CFSR_MMARVALID) != 0U) {
        fault.fault_addr = mcu_reg_read(SCB_MMFAR_ADDR);
        fault.addr_valid |= 0x01U;
    } else if ((fault.cfsr & CFSR_BFARVALID) != 0U) {
        fault.fault_addr = mcu_reg_read(SCB_BFAR_ADDR);
        fault.addr_valid |= 0x02U;
    }

    blackbox_panic(&fault);

    /* Знімок у SRAM переживе скидання, але не переживе знеструмлення, тому
     * той самий том одразу лягає в носій. Помилка запису тут нікуди не
     * повідомляється: доповісти вже нема кому, а копія в .noinit лишилась. */
    (void)spi_emergency_write(BLACKBOX_NV_SLOT_ADDR);

    mcu_system_reset();
}

/* Асемблерний перехідник. Він голий (naked) навмисно: компілятор не має
 * права поставити пролог, який зачепить зіпсований стек. Другий біт
 * EXC_RETURN каже, куди ядро склало кадр — у MSP чи в PSP потоку. */
#if defined(__ARM_ARCH_6M__)
/* Cortex-M0/M0+: без IT-блоків і без умовних mrs — розгалуження явне. */
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "movs r0, #4       \n"
        "mov  r1, lr       \n"
        "tst  r0, r1       \n"
        "beq  1f           \n"
        "mrs  r0, psp      \n"
        "b    2f           \n"
        "1:                \n"
        "mrs  r0, msp      \n"
        "2:                \n"
        "b    prvGetRegistersFromStack \n"
    );
}
#else
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst  lr, #4       \n"
        "ite  eq           \n"
        "mrseq r0, msp     \n"
        "mrsne r0, psp     \n"
        "mov  r1, lr       \n"
        "b    prvGetRegistersFromStack \n"
    );
}

/* Налаштовані винятки, доки їх не ескалювали в HardFault, приходять сюди
 * своїми векторами — і мають лягти в чорну скриньку так само. */
__attribute__((alias("HardFault_Handler"))) void MemManage_Handler(void);
__attribute__((alias("HardFault_Handler"))) void BusFault_Handler(void);
__attribute__((alias("HardFault_Handler"))) void UsageFault_Handler(void);
#endif
