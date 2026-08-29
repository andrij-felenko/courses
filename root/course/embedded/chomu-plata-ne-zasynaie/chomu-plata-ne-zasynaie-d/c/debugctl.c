#include "debugctl.h"
#include "pins.h"
#include "regs.h"

#define SWO_PORT  GPIOB
#define SWO_PIN   3u
#define SWDIO_PIN 13u
#define SWCLK_PIN 14u

bool debug_probe_attached(void)
{
    return (CORE_DHCSR & DHCSR_C_DEBUGEN) != 0u;
}

void debug_silence_core(void)
{
    /* 1. Головне: жодного утримання тактових дерев під час WFI. */
    DBGMCU_CR = 0u;

    /* 2. Трасування. TRCENA живить увесь блок DWT/ITM/TPIU; поки він стоїть,
     *    вихідний каскад SWO лишається в режимі надшвидкого фронту. */
    ITM_LAR = ITM_LAR_UNLOCK;
    ITM_TER = 0u;
    ITM_TCR &= ~ITM_TCR_ITMENA;
    DWT_CTRL &= ~DWT_CTRL_CYCCNTENA;
    CORE_DEMCR &= ~DEMCR_TRCENA;

    /* 3. Виводи налагодження в аналоговий режим. Внутрішні підтяжки SWDIO/SWCLK
     *    вимикаються разом з цифровим буфером; зовнішні, у зонді, лишаються —
     *    тому релізний вимір роблять із від'єднаним шлейфом. */
    pin_pull(SWO_PORT, SWO_PIN, PULL_NONE);
    pin_mode(SWO_PORT, SWO_PIN, MODE_ANALOG);
    pin_pull(GPIOA, SWDIO_PIN, PULL_NONE);
    pin_mode(GPIOA, SWDIO_PIN, MODE_ANALOG);
    pin_pull(GPIOA, SWCLK_PIN, PULL_NONE);
    pin_mode(GPIOA, SWCLK_PIN, MODE_ANALOG);
}

void debug_unfreeze_peripherals(void)
{
    /* Заморожування таймерів і сторожового пса на час зупинки — зручність
     * налагодження, яка тримає їхнє тактування живим. */
    DBGMCU_APB1FZR1 = 0u;
    DBGMCU_APB1FZR2 = 0u;
    DBGMCU_APB2FZR  = 0u;
}

void debug_low_power_supervisors(void)
{
    PWR_CR2 &= ~PWR_CR2_PVDE;  /* програмований детектор напруги вимкнено */
    PWR_CR3 |= PWR_CR3_ENULP;  /* BOR і PVD опитуються імпульсно: одиниці сотень нА */
}
