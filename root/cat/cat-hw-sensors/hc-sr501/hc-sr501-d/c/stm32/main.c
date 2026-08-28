#include "main.h"          // CubeMX: PA0 — GPIO_Input без підтяжки (давач штовхає
                           // рівень сам), PC13 — GPIO_Output push-pull

#define PIR_PORT  GPIOA
#define PIR_PIN   GPIO_PIN_0      // OUT давача
#define LED_PORT  GPIOC
#define LED_PIN   GPIO_PIN_13     // світлодіод плати

void pir_loop(void) {              // викликати з main() після MX_GPIO_Init()
    while (1) {
        GPIO_PinState motion = HAL_GPIO_ReadPin(PIR_PORT, PIR_PIN);  // SET = є рух
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, motion);
        if (motion == GPIO_PIN_SET) printf("рух!\r\n");   // printf виведено в UART
        HAL_Delay(50);
    }
}
