#include "main.h"       // CubeMX: PA0 — вхід без підтяжки, PC13 — вихід push-pull

#define SOUND_PORT  GPIOA
#define SOUND_PIN   GPIO_PIN_0      // вивід OUT давача
#define LED_PORT    GPIOC
#define LED_PIN     GPIO_PIN_13     // світлодіод плати

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();         // підтяжка не потрібна: вона вже є на платі давача
    MX_USART2_UART_Init();  // printf перенаправлено на UART

    uint32_t last_hit = 0;  // HAL_GetTick() останньої зарахованої події
    uint32_t count = 0;

    while (1) {
        // GPIO_PIN_SET = тиша, GPIO_PIN_RESET = гучний звук
        GPIO_PinState level = HAL_GPIO_ReadPin(SOUND_PORT, SOUND_PIN);
        HAL_GPIO_WritePin(LED_PORT, LED_PIN,
                          level == GPIO_PIN_RESET ? GPIO_PIN_SET : GPIO_PIN_RESET);

        // рахуємо подію, але не частіше ніж раз на 150 мс —
        // інакше один плеск дасть чергу спрацювань
        uint32_t now = HAL_GetTick();
        if (level == GPIO_PIN_RESET && now - last_hit > 150) {
            last_hit = now;
            printf("гучний звук #%lu\r\n", (unsigned long)++count);
        }
        HAL_Delay(2);   // щільний цикл, щоб не проґавити короткий імпульс
    }
}
