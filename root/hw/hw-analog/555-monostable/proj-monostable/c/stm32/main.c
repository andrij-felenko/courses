#include "main.h"   // BTN_GPIO_Port/BTN_Pin, OUT_GPIO_Port/OUT_Pin — з CubeMX:
                    // вхід GPIO_MODE_INPUT + GPIO_PULLUP, вихід GPIO_MODE_OUTPUT_PP

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();                    // піни налаштовано генератором

    oneshot_t btn;
    oneshot_init(&btn, 30);            // T = 30 мс, трохи довше за брязкіт
    bool prev = true;

    while (1) {
        // підтяжка вгору: RESET = натиснуто
        bool level   = (HAL_GPIO_ReadPin(BTN_GPIO_Port, BTN_Pin) == GPIO_PIN_SET);
        bool falling = prev && !level;
        prev = level;

        // рівно один імпульс 30 мс на натискання: перший спад запускає ACTIVE,
        // а всі дальші стрибки контакту в ці 30 мс потрапляють у «глуху» зону
        HAL_GPIO_WritePin(OUT_GPIO_Port, OUT_Pin,
                          oneshot_poll(&btn, falling, HAL_GetTick())
                              ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }
}
