#include "main.h"
#include <stdio.h>                 // printf перенаправлено на UART

#define LOCKOUT   60u              // придушення торохтіння, мс
#define GAP_END  800u              // тиша, що означає «серія скінчилась», мс
#define MAXN      12u              // стелю візерунка обмежуємо

volatile uint8_t knockFlag = 0;
void HAL_GPIO_EXTI_Callback(uint16_t pin) { if (pin == GPIO_PIN_0) knockFlag = 1; }
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); }

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0;           // PA0 — вивід S
    g.Mode = GPIO_MODE_IT_FALLING; // переривання на фронті спаду
    g.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &g);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

    uint32_t last = 0, gaps[MAXN];  // проміжки між сусідніми стуками, мс
    uint8_t nGaps = 0, nHits = 0, inSeries = 0;

    while (1) {
        uint32_t now = HAL_GetTick();

        // 1) зафіксувати новий стук (з локаутом проти торохтіння)
        if (knockFlag) {
            knockFlag = 0;
            if (now - last > LOCKOUT) {
                if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - last;
                last = now;
                nHits++;
                inSeries = 1;
            }
        }

        // 2) достатньо довга тиша після стуку → серія скінчилась, розбираємо
        if (inSeries && now - last > GAP_END) {
            printf("серія: %u стук(и), проміжки[мс]:", (unsigned)nHits);
            for (uint8_t i = 0; i < nGaps; i++) printf(" %lu", (unsigned long)gaps[i]);
            printf("\r\n");
            nGaps = 0;
            nHits = 0;
            inSeries = 0;
        }
    }
}
