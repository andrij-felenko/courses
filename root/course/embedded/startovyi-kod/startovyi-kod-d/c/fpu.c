#include "mcu_regs.h"
#include "startup.h"

/* Увімкнення співпроцесора з рухомою комою. Після скидання CP10 і CP11
   (одинарна й подвійна точність) вимкнені задля економії струму, і
   перша ж інструкція vldr дала б UsageFault із прапорцем NOCP. */
bool startup_enable_fpu(void)
{
    SCB_CPACR |= SCB_CPACR_CP10_FULL | SCB_CPACR_CP11_FULL;

    __asm volatile("dsb 0xF" ::: "memory"); /* запис дійшов до регістра */
    __asm volatile("isb 0xF" ::: "memory"); /* конвеєр перезаповнено */

    /* На ядрі без FPU (Cortex-M0/M3) ці біти читаються нулями. Так
       стартовий код дізнається, що прошивку зібрано не для цього чипа. */
    const uint32_t full = SCB_CPACR_CP10_FULL | SCB_CPACR_CP11_FULL;
    return (SCB_CPACR & full) == full;
}
