#include "fault.h"

#include "trace.h"
#include "stm32f4xx.h"

/*
 * Спільний C-вхід усіх чотирьох обробників. Викликається трампліном, який
 * уже поклав у R0 покажчик стека з кадром аварії, у R1 — EXC_RETURN,
 * у R2 — номер вектора.
 */
void fault_entry_c(uint32_t frame_sp, uint32_t exc_return, uint32_t tag);

void fault_entry_c(uint32_t frame_sp, uint32_t exc_return, uint32_t tag)
{
    fault_report(frame_sp, exc_return, tag);
    trace_flush(); /* дати останнім байтам вийти з UART до скидання */

    /*
     * Не зависаємо у while(1): пристрій у полі має піднятися й працювати далі.
     * Наступний старт побачить у RCC->CSR прапорець SFTRSTF і знатиме, що це
     * був крах, а не подача живлення.
     */
    NVIC_SystemReset();

    for (;;) {
        /* NVIC_SystemReset() не повертається; цикл тут лише щоб компілятор
           не вигадував падіння за кінець функції. */
    }
}

/*
 * Трамплін мусить бути naked: будь-який пролог на C зсунув би покажчик стека
 * і R0 указував би вже не на кадр аварії, а на локальні змінні обробника.
 * Біт 2 регістра LR (EXC_RETURN) каже, на якому стеку лежить кадр:
 * 0 — MSP (bare-metal код або інше переривання), 1 — PSP (задача RTOS).
 */
#define FAULT_TRAMPOLINE(handler, tag_value)      \
    __attribute__((naked)) void handler(void)     \
    {                                             \
        __asm volatile(                           \
            "tst   lr, #4              \n"        \
            "ite   eq                  \n"        \
            "mrseq r0, msp             \n"        \
            "mrsne r0, psp             \n"        \
            "mov   r1, lr              \n"        \
            "mov   r2, %[tag]          \n"        \
            "b     fault_entry_c       \n"        \
            :                                     \
            : [tag] "i"(tag_value)                \
            : "r0", "r1", "r2", "memory");        \
    }

FAULT_TRAMPOLINE(HardFault_Handler, FAULT_TAG_HARD)
FAULT_TRAMPOLINE(MemManage_Handler, FAULT_TAG_MEMMANAGE)
FAULT_TRAMPOLINE(BusFault_Handler, FAULT_TAG_BUS)
FAULT_TRAMPOLINE(UsageFault_Handler, FAULT_TAG_USAGE)

void fault_enable_all(void)
{
    /*
     * Після скидання всі три конфігуровані винятки вимкнені, і будь-яка
     * помилка ескалується в HardFault із бітом HFSR.FORCED. Вмикаємо їх,
     * щоб ловити збій на місці виникнення.
     */
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk |
                  SCB_SHCSR_BUSFAULTENA_Msk |
                  SCB_SHCSR_USGFAULTENA_Msk;

    /* Ділення на нуль і невирівняний доступ за замовчуванням мовчать. */
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk | SCB_CCR_UNALIGN_TRP_Msk;

    /*
     * ACTLR у CMSIS лежить у блоці SCnSCB (system control not in SCB).
     * DISDEFWBUF вимикає буфер запису: кожен STR у периферію стає
     * синхронним, тож помилка шини приходить точною (PRECISERR) і BFAR
     * містить справжню адресу. Ціна — трохи повільніший запис у периферію,
     * тому в серійній прошивці цей біт лишають вимкненим.
     */
    SCnSCB->ACTLR |= SCnSCB_ACTLR_DISDEFWBUF_Msk;

    __DSB();
    __ISB();
}
