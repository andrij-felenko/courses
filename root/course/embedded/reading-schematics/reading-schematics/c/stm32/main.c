#include "stm32f4xx_hal.h"

#define BTN_PORT GPIOC
#define BTN_PIN  GPIO_PIN_13   // вивід, до якого підключена кнопка
#define LED_PORT GPIOA
#define LED_PIN  GPIO_PIN_5    // вивід зі світлодіодом

int main(void) {
    HAL_Init();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef g = {0};
    g.Pin  = BTN_PIN;
    g.Mode = GPIO_MODE_INPUT;
    g.Pull = GPIO_PULLUP;              // підтяжка тримає вхід у «1»
    HAL_GPIO_Init(BTN_PORT, &g);

    g.Pin  = LED_PIN;
    g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(LED_PORT, &g);

    while (1) {
        // кнопка притискає вхід до «0» → натиск = GPIO_PIN_RESET
        bool pressed = (HAL_GPIO_ReadPin(BTN_PORT, BTN_PIN) == GPIO_PIN_RESET);
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, pressed ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_Delay(10);
    }
}
