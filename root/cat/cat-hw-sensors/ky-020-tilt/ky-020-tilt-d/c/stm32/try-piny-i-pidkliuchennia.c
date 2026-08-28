#include "main.h"          // CubeMX: PA0 — GPIO_Input без підтяжки (10 кОм уже на
                           // модулі), PC13 — GPIO_Output push-pull

#define TILT_PORT GPIOA
#define TILT_PIN  GPIO_PIN_0      // пін S давача
#define LED_PORT  GPIOC
#define LED_PIN   GPIO_PIN_13     // світлодіод плати

void tilt_loop(void) {            // викликати з main() після MX_GPIO_Init()
    while (1) {
        // УВАГА: логіка перевернута — нахил дає RESET, спокій SET
        GPIO_PinState raw = HAL_GPIO_ReadPin(TILT_PORT, TILT_PIN);
        GPIO_PinState tilted = (raw == GPIO_PIN_RESET) ? GPIO_PIN_SET : GPIO_PIN_RESET;
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, tilted);   // світимо, поки нахилено
        if (raw == GPIO_PIN_RESET) printf("нахил!\r\n");  // printf виведено в UART
        HAL_Delay(50);
    }
}
