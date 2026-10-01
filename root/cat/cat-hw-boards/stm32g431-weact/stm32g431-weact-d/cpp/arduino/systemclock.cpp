#include <stm32g4xx_ll_rcc.h>
#include <stm32g4xx_ll_system.h>
#include <stm32g4xx_ll_utils.h>

class SystemClock {
public:
    static void setup170MHz() {
        LL_FLASH_SetLatency(FLASH, LL_FLASH_LATENCY_4);
        LL_RCC_HSE_Enable();
        while(!LL_RCC_HSE_IsReady());

        LL_RCC_PLL_ConfigDomain_SYS(LL_RCC_PLLSOURCE_HSE, LL_RCC_PLLM_DIV_2, 85, LL_RCC_PLLR_DIV_2);
        LL_RCC_PLL_Enable();
        LL_RCC_PLL_EnableDomain_SYS();
        while(!LL_RCC_PLL_IsReady());

        LL_RCC_SetSysClkSource(LL_RCC_SYSCLKSOURCE_PLL);
        while(LL_RCC_GetSysClkSource() != LL_RCC_SYSCLKSOURCE_STATUS_PLL);
    }
};
