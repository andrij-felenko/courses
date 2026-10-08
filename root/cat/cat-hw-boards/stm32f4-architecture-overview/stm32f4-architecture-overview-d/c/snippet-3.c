// C: Налаштування тактування RCC від 8 МГц HSE до 168 МГц HCLK та генерації ШІМ через TIM1 (LL драйвери)
#include "stm32f4xx_ll_rcc.h"
#include "stm32f4xx_ll_system.h"
#include "stm32f4xx_ll_bus.h"
#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_gpio.h"

void SystemClock_Config_168MHz(void) {
    // 1. Ввімкнення зовнішнього кварцю HSE (8 МГц)
    LL_RCC_HSE_Enable();
    while(!LL_RCC_HSE_IsReady());

    // 2. Налаштування тактів очікування Flash (5 WS при 168 МГц і 3.3В) та ввімкнення ART Accelerator
    LL_FLASH_SetLatency(LL_FLASH_LATENCY_5);
    LL_FLASH_EnableInstCache();
    LL_FLASH_EnableDataCache();
    LL_FLASH_EnablePrefetch();

    // 3. Конфігурація головного PLL: M=8, N=336, P=2, Q=7 (VCOin=1MHz, VCOout=336MHz, SYSCLK=168MHz, PLL48=48MHz)
    LL_RCC_PLL_ConfigDomain_SYS(LL_RCC_PLLSOURCE_HSE, LL_RCC_PLLM_DIV_8, 336, LL_RCC_PLLP_DIV_2);
    LL_RCC_PLL_Enable();
    while(!LL_RCC_PLL_IsReady());

    // 4. Налаштування дільників шин AHB=1 (168MHz), APB1=4 (42MHz), APB2=2 (84MHz)
    LL_RCC_SetAHBPrescaler(LL_RCC_SYSCLK_DIV_1);
    LL_RCC_SetAPB1Prescaler(LL_RCC_APB1_DIV_4);
    LL_RCC_SetAPB2Prescaler(LL_RCC_APB2_DIV_2);

    // 5. Перемикання системного тактування на вихід PLL
    LL_RCC_SetSysClkSource(LL_RCC_SYSCLK_SOURCE_PLL);
    while(LL_RCC_GetSysClkSource() != LL_RCC_SYSCLK_STATUS_PLL);
}
