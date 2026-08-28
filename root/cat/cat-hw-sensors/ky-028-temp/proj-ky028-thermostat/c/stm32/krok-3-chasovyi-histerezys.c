/* DO_GPIO_Port/DO_Pin — GPIO_Input, NOPULL; LOAD_GPIO_Port/LOAD_Pin — GPIO_Output */
#include "main.h"
#include <stdbool.h>
#include <stdio.h>

#define LOCKOUT_MS  2000U                    // «карантин» після зміни стану

static GPIO_PinState restLevel = GPIO_PIN_SET;
static bool          state     = false;      // поточний стан термостата: true = «гаряче»
static uint32_t      lastFlip  = 0;          // коли востаннє перемкнулися (тіки HAL, мс)

static GPIO_PinState ReadRestLevel(void) {
    const int N = 15; int highs = 0;
    for (int i = 0; i < N; i++) {
        if (HAL_GPIO_ReadPin(DO_GPIO_Port, DO_Pin) == GPIO_PIN_SET) highs++;
        HAL_Delay(5);
    }
    return (highs > N / 2) ? GPIO_PIN_SET : GPIO_PIN_RESET;
}

static bool RawHot(void) {
    return HAL_GPIO_ReadPin(DO_GPIO_Port, DO_Pin) != restLevel;
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();

    HAL_Delay(300);
    restLevel = ReadRestLevel();
    state = RawHot();                        // початковий стан — від реальності
    HAL_GPIO_WritePin(LOAD_GPIO_Port, LOAD_Pin, state ? GPIO_PIN_SET : GPIO_PIN_RESET);
    lastFlip = HAL_GetTick();

    while (1) {
        bool hot = RawHot();

        /* Приймаємо зміну стану, ЛИШЕ якщо минув карантин від минулого перемикання. */
        if (hot != state && (HAL_GetTick() - lastFlip) >= LOCKOUT_MS) {
            state = hot;
            lastFlip = HAL_GetTick();
            HAL_GPIO_WritePin(LOAD_GPIO_Port, LOAD_Pin,
                              state ? GPIO_PIN_SET : GPIO_PIN_RESET);
            printf("%s\r\n", state ? ">> увімкнув навантаження (ГАРЯЧЕ)"
                                   : "<< вимкнув навантаження (норма)");
        }

        /* ... тут цикл вільний робити будь-що інше, він не заблокований ... */
    }
}
