#include "stm32f4xx.h"
#include <stdint.h>
#include <stdbool.h>

#define HYST_V_ON_RAW    3908U  /* ~3.15 В */
#define HYST_V_OFF_RAW   3660U  /* ~2.95 В */

typedef enum {
    POWER_HYST_STATE_LOW  = 0,
    POWER_HYST_STATE_HIGH = 1
} PowerHystState_t;

static PowerHystState_t g_hyst_state = POWER_HYST_STATE_HIGH;

static void Debug_ITM_SendString(const char *str) {
    while (*str) {
        if (((ITM->TCR & ITM_TCR_ITMENA_Msk) != 0U) &&
            ((ITM->TER & (1U << 0)) != 0U)) {
            while (ITM->PORT[0].u32 == 0U);
            ITM->PORT[0].u8 = (uint8_t)*str;
        }
        str++;
    }
}

void PowerHW_ProcessHysteresisDebug(uint32_t current_filtered_raw) {
    switch (g_hyst_state) {
        case POWER_HYST_STATE_HIGH:
            if (current_filtered_raw < HYST_V_OFF_RAW) {
                g_hyst_state = POWER_HYST_STATE_LOW;
                
                /* Сигналізація через відлагоджувальний вивід GPIO PA5 */
                GPIOA->BSRR = GPIO_BSRR_BS5;
                
                Debug_ITM_SendString("[POWER]: Drop detected! Switching to LOW POWER mode.\n");
                
                /* Переведення системних периферійних модулів у режим енергозбереження */
                RCC->APB2ENR &= ~RCC_APB2ENR_SPI1EN;
            }
            break;

        case POWER_HYST_STATE_LOW:
            if (current_filtered_raw > HYST_V_ON_RAW) {
                g_hyst_state = POWER_HYST_STATE_HIGH;
                
                GPIOA->BSRR = GPIO_BSRR_BR5;
                
                Debug_ITM_SendString("[POWER]: Voltage restored. Normal operation resumed.\n");
                
                RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
            }
            break;
    }
}
