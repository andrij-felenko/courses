/* hadc1 налаштовано на канал, куди заведено AO; роздільність 12 біт (0..4095).
   LOAD_GPIO_Port / LOAD_Pin — GPIO_Output. */
#include "main.h"
#include <stdbool.h>
#include <stdio.h>

/* Пороги в одиницях (4095 - сире): БІЛЬШЕ = тепліше.
   Зазор WARM_OFF..WARM_ON — і є гістерезис; підібрати під свою намистину. */
#define WARM_ON   2560
#define WARM_OFF  2400

extern ADC_HandleTypeDef hadc1;

static bool state = false;          // true = навантаження ввімкнене
static int  warmS = 0;              // згладжене значення (проти шуму АЦП)

static int ReadWarm(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    int raw = (int)HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    return 4095 - raw;              // інвертуємо: більше = тепліше
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_ADC1_Init();
    MX_USART2_UART_Init();

    warmS = ReadWarm();             // початкове наповнення фільтра

    while (1) {
        int warm = ReadWarm();
        warmS += (warm - warmS) / 4;                 // згладжувальна ланка (шум АЦП)

        /* Гістерезис ЗА РІВНЕМ: два різні пороги вгору й униз. */
        if (!state && warmS >= WARM_ON) {            /* вище верхнього → вмикаємо */
            state = true;
            HAL_GPIO_WritePin(LOAD_GPIO_Port, LOAD_Pin, GPIO_PIN_SET);
            printf(">> ГАРЯЧЕ (warm вище верхнього порогу)\r\n");
        } else if (state && warmS <= WARM_OFF) {     /* нижче нижнього → вимикаємо */
            state = false;
            HAL_GPIO_WritePin(LOAD_GPIO_Port, LOAD_Pin, GPIO_PIN_RESET);
            printf("<< норма (warm нижче нижнього порогу)\r\n");
        }
        /* у зоні WARM_OFF..WARM_ON стан НЕ міняється — тремтіння погашене */

        printf("warm = %d\r\n", warmS);              /* для підбору порогів */
        HAL_Delay(50);
    }
}
