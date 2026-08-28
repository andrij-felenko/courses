/* DO_GPIO_Port / DO_Pin — GPIO_Input, GPIO_NOPULL (підтяжка на платі модуля) */
#include "main.h"
#include <stdbool.h>
#include <stdio.h>

static GPIO_PinState restLevel = GPIO_PIN_SET;   // рівень DO у спокої
static bool          wasHot    = false;          // попередній стан — ловимо ПЕРЕХІД

/* Прочитати «спокій»: кілька замірів, повернути найчастіший рівень. */
static GPIO_PinState ReadRestLevel(void) {
    const int N = 15;
    int highs = 0;
    for (int i = 0; i < N; i++) {
        if (HAL_GPIO_ReadPin(DO_GPIO_Port, DO_Pin) == GPIO_PIN_SET) highs++;
        HAL_Delay(5);
    }
    return (highs > N / 2) ? GPIO_PIN_SET : GPIO_PIN_RESET;   // більшість голосів
}

/* «Гаряче» = стан, протилежний до виміряного спокою — полярність-незалежно. */
static bool IsHot(void) {
    return HAL_GPIO_ReadPin(DO_GPIO_Port, DO_Pin) != restLevel;
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_USART2_UART_Init();

    HAL_Delay(300);                     // дати модулю усталитися після живлення
    restLevel = ReadRestLevel();        // ВАЖЛИВО: тут температура має бути в НОРМІ
    printf("Спокій DO = %s\r\n", restLevel == GPIO_PIN_SET ? "HIGH (гаряче буде LOW)"
                                                           : "LOW (гаряче буде HIGH)");
    while (1) {
        bool hot = IsHot();
        if (hot != wasHot) {            // друкуємо лише перехід
            printf("%s\r\n", hot ? ">> перетнуло поріг: ГАРЯЧЕ"
                                 : "<< нижче порогу: норма");
            wasHot = hot;
        }
        HAL_Delay(20);
    }
}
