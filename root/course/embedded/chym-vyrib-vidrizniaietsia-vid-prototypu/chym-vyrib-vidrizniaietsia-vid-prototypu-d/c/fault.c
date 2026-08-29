#include "fault.h"

#include "console.h"
#include "crash_log.h"
#include "mcu.h"
#include "safe_state.h"

/* Спільний хвіст для всіх аварійних шляхів. */
__attribute__((noreturn)) static void fault_finish(panic_reason_t reason,
                                                   const fault_context_t *ctx)
{
    /* 1. Механіка. Переривання вимикаємо після знеструмлення, а не до:
     *    робота з BDTR і BSRR — це кілька записів у регістри, вони не
     *    потребують переривань, зате будь-яка затримка тут коштує руху. */
    safe_state_enter();
    mcu_disable_irq();

    /* 2. Діагностика. */
    crash_log_record_panic(reason, ctx);

    /* 3. Останнє слово в діагностичний порт — на випадок, якщо пристрій
     *    зараз на столі в сервісі й радіоканалу немає. Друк іде
     *    опитуванням, без переривань і DMA: у гілці аварії довіряти
     *    можна лише найпростішому. */
    char line[192];
    const size_t n = crash_log_render(line, sizeof(line));
    console_write_blocking("PANIC ", 6U);
    console_write_blocking(line, n);
    console_write_blocking("\r\n", 2U);

    /* 4. Рестарт. Не «продовжуємо як є» і не зависаємо назавжди:
     *    пристрій у полі має спробувати піднятися сам. */
    mcu_system_reset();

    for (;;) {
        /* недосяжно */
    }
}

__attribute__((noreturn)) void panic(panic_reason_t reason)
{
    fault_context_t ctx = {
        .pc = (uint32_t)(uintptr_t)__builtin_return_address(0),
        .lr = 0U,
        .sp = mcu_get_msp(),
        .cfsr = SCB_CFSR,
    };
    fault_finish(reason, &ctx);
}

/* Викликається з асемблерної обгортки нижче. Кадр винятку, який ядро
 * саме поклало на стек: R0 R1 R2 R3 R12 LR PC xPSR. */
__attribute__((noreturn)) void fault_report(const uint32_t *frame, uint32_t exc_return)
{
    fault_context_t ctx = {
        .pc = frame[6],
        .lr = frame[5],
        /* Кадр — вісім слів; дев'яте могло піти на вирівнювання, але
         * для пошуку місця падіння важлива саме межа кадру. */
        .sp = (uint32_t)(uintptr_t)(frame + 8),
        .cfsr = SCB_CFSR,
    };
    (void)exc_return;
    fault_finish(PANIC_HARDFAULT, &ctx);
}

/* Обгортка мусить бути naked: звичайний пролог функції зіпсував би
 * стек, з якого ми зараз дістаємо контекст падіння. Біт 2 у EXC_RETURN
 * каже, з якого стека ядро складало кадр — головного чи процесного. */
__attribute__((naked)) void HardFault_Handler(void)
{
    __asm volatile("tst   lr, #4          \n"
                   "ite   eq              \n"
                   "mrseq r0, msp         \n"
                   "mrsne r0, psp         \n"
                   "mov   r1, lr          \n"
                   "b     fault_report    \n");
}

/* Ті самі кроки для решти винятків ядра: у виробі не буває «невідомого»
 * винятку, який просто зациклює процесор у стандартній заглушці. */
__attribute__((naked)) void MemManage_Handler(void)
{
    __asm volatile("tst   lr, #4          \n"
                   "ite   eq              \n"
                   "mrseq r0, msp         \n"
                   "mrsne r0, psp         \n"
                   "mov   r1, lr          \n"
                   "b     fault_report    \n");
}

__attribute__((naked)) void BusFault_Handler(void)
{
    __asm volatile("tst   lr, #4          \n"
                   "ite   eq              \n"
                   "mrseq r0, msp         \n"
                   "mrsne r0, psp         \n"
                   "mov   r1, lr          \n"
                   "b     fault_report    \n");
}

__attribute__((naked)) void UsageFault_Handler(void)
{
    __asm volatile("tst   lr, #4          \n"
                   "ite   eq              \n"
                   "mrseq r0, msp         \n"
                   "mrsne r0, psp         \n"
                   "mov   r1, lr          \n"
                   "b     fault_report    \n");
}
