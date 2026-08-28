#include "stm32f4xx_hal.h"
#include <stdbool.h>
#include <stdio.h>

#define SOUND_PORT  GPIOA
#define SOUND_PIN   GPIO_PIN_1          // DO давача — на будь-який вхідний вивід

static GPIO_PinState idle_level;        // рівень, який плата тримає в ТИШІ

void sound_begin(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef io = {0};
    io.Pin  = SOUND_PIN;
    io.Mode = GPIO_MODE_INPUT;
    io.Pull = GPIO_NOPULL;              // підтяжка вже стоїть на модулі
    HAL_GPIO_Init(SOUND_PORT, &io);

    HAL_Delay(50);                      // дати входу усталитися
    idle_level = HAL_GPIO_ReadPin(SOUND_PORT, SOUND_PIN);   // у тиші — «спокій» плати
    printf("Рівень спокою DO = %s\r\n",
           idle_level == GPIO_PIN_SET ? "SET (подія — падіння в RESET)"
                                      : "RESET (подія — зростання в SET)");
}

// true — коли DO відійшов від спокою, тобто звук ПЕРЕВИЩИВ поріг.
bool is_loud(void) {
    return HAL_GPIO_ReadPin(SOUND_PORT, SOUND_PIN) != idle_level;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    sound_begin();
    while (1) {
        printf("%s\r\n", is_loud() ? "гучно" : "тихо");
        HAL_Delay(100);
    }
}
