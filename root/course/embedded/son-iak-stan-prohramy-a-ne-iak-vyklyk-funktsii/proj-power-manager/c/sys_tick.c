#include "sys_tick.h"
#include "stm32l4xx.h"

static volatile uint32_t s_ms;

void SysTick_Handler(void)
{
    s_ms++;
}

void sys_tick_init(uint32_t sysclk_hz)
{
    /* Переповнення лічильника — 49 діб; для пристрою на батареї цього мало,
     * тому весь код нижче працює з різницями, а не з абсолютними значеннями. */
    s_ms = 0;
    SysTick_Config(sysclk_hz / 1000u);
}

uint32_t sys_tick_now_ms(void)
{
    return s_ms;
}

void sys_tick_suspend(void)
{
    SysTick->CTRL &= ~(SysTick_CTRL_TICKINT_Msk | SysTick_CTRL_ENABLE_Msk);
    /* Прапорець, що встиг звестися до вимкнення, інакше вистрелить після сну. */
    SCB->ICSR = SCB_ICSR_PENDSTCLR_Msk;
}

void sys_tick_resume(uint32_t slept_ms)
{
    s_ms += slept_ms;
    SysTick->VAL   = 0;
    SysTick->CTRL |= SysTick_CTRL_TICKINT_Msk | SysTick_CTRL_ENABLE_Msk;
}

uint32_t sys_tick_until(uint32_t deadline_ms)
{
    int32_t left = (int32_t)(deadline_ms - s_ms);
    return (left > 0) ? (uint32_t)left : 0u;
}
