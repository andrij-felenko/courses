/* hadc1 налаштовано на канал, куди заведено AO; 12 біт (0..4095) */
#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;

static int      warmS    = 0;       // згладжене «тепло» (більше = тепліше)
static int      prevWarm = 0;       // попереднє згладжене — для швидкості
static uint32_t tPrev    = 0;

static int ReadWarm(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    int raw = (int)HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    return 4095 - raw;              // інверсія: більше = тепліше
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_ADC1_Init();
    MX_USART2_UART_Init();

    warmS = prevWarm = ReadWarm();
    tPrev = HAL_GetTick();

    while (1) {
        warmS += (ReadWarm() - warmS) / 8;       /* сильніше згладжування для тренду */

        if (HAL_GetTick() - tPrev >= 500) {      /* раз на пів секунди — швидкість */
            int rate = warmS - prevWarm;         /* зміна за інтервал (відносна!) */
            const char *dir = rate > 2 ? "тепліє"
                            : rate < -2 ? "холоне"
                            : "стабільно";
            printf("тренд: %s   швидкість (відносна): %d\r\n", dir, rate);
            prevWarm = warmS;
            tPrev = HAL_GetTick();
        }
        HAL_Delay(20);
    }
}
