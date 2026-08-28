#include "main.h"
#include <math.h>
#include <stdio.h>

#define LOCKOUT   60u
#define GAP_END  800u
#define MAXN      12u
#define TOL     0.25f                 // допуск на частку (безрозмірний)

volatile uint8_t knockFlag = 0;
void HAL_GPIO_EXTI_Callback(uint16_t pin) { if (pin == GPIO_PIN_0) knockFlag = 1; }
void EXTI0_IRQHandler(void) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0); }

/* normalize() і rhythmMatches() — байт-у-байт ті самі, що у вкладці Arduino:
   чиста арифметика над масивом проміжків, HAL до неї стосунку не має */
static void normalize(const uint32_t *src, uint8_t n, float *out);
static uint8_t rhythmMatches(const uint32_t *a, uint8_t na, const uint32_t *b, uint8_t nb);

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0;
    g.Mode = GPIO_MODE_IT_FALLING;
    g.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOA, &g);
    g.Pin   = GPIO_PIN_13;            // PC13 — «замок»: SET = відчинено
    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &g);
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    printf("Відстукайте секретний ритм — він стане ключем.\r\n");

    uint32_t last = 0, gaps[MAXN], secret[MAXN];
    uint8_t nGaps = 0, nHits = 0, secretN = 0, inSeries = 0, learning = 1;

    while (1) {
        uint32_t now = HAL_GetTick();

        if (knockFlag) {
            knockFlag = 0;
            if (now - last > LOCKOUT) {
                if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - last;
                last = now; nHits++; inSeries = 1;
            }
        }

        if (inSeries && now - last > GAP_END) {
            if (learning) {                   // перша серія → запам'ятати як ключ
                for (uint8_t i = 0; i < nGaps; i++) secret[i] = gaps[i];
                secretN = nGaps; learning = 0;
                printf("Ключ записано: %u стук(и). Тепер відстукайте його.\r\n",
                       (unsigned)nHits);
            } else if (rhythmMatches(gaps, nGaps, secret, secretN)) {
                printf(">>> ВІРНО — відчинено\r\n");
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
            } else {
                printf("... не той ритм\r\n");
                HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
            }
            nGaps = 0; nHits = 0; inSeries = 0;
        }
    }
}
