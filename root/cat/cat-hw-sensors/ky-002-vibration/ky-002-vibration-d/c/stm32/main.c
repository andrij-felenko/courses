#include "main.h"   // CubeMX: SHOCK_Pin — вхід із GPIO_PULLUP, LED_Pin — вихід

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();            // підтяжка вгору на SHOCK_Pin: спокій = 1, струс тягне до 0
    MX_USART2_UART_Init();     // printf перенаправлено на UART

    uint32_t last_hit = 0;     // мілісекунди останнього зарахованого струсу
    uint32_t count    = 0;

    while (1) {
        // 1 = спокій, 0 = контакт замкнувся
        GPIO_PinState level = HAL_GPIO_ReadPin(SHOCK_GPIO_Port, SHOCK_Pin);

        // світимо, поки бачимо замикання
        HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,
                          level == GPIO_PIN_RESET ? GPIO_PIN_SET : GPIO_PIN_RESET);

        // рахуємо струс, але не частіше ніж раз на 200 мс — гасимо торохтіння пружини
        uint32_t now = HAL_GetTick();
        if (level == GPIO_PIN_RESET && now - last_hit > 200) {
            last_hit = now;
            printf("струс #%lu\r\n", (unsigned long)++count);
        }
        HAL_Delay(5);   // щільний цикл, щоб не проґавити короткий контакт
    }
}
