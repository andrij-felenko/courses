#include "stm32f4xx_hal.h"

#define DO_PORT  GPIOA
#define DO_PIN   GPIO_PIN_0                // вивід DO давача; PA0 = вхід (готує CubeMX)

static GPIO_PinState idle_level;           // рівень DO у тиші (визначимо самі)

// Прочитати рівень, що переважає в тиші: беремо більшість із багатьох відліків.
static GPIO_PinState detect_idle_level(uint16_t samples) {
    uint16_t highs = 0;
    for (uint16_t i = 0; i < samples; i++) {
        if (HAL_GPIO_ReadPin(DO_PORT, DO_PIN) == GPIO_PIN_SET) highs++;
        HAL_Delay(1);                      // крок 1 мс; загалом ~200 мс на всю оцінку
    }
    // Якщо більшість відліків були SET — спокій це SET, інакше RESET.
    return (highs > samples / 2) ? GPIO_PIN_SET : GPIO_PIN_RESET;
}

void ky038_init(void) {                    // кличемо з main() після MX_GPIO_Init()
    HAL_Delay(300);                        // дати мікрофону встановити зсув після ввімкнення
    idle_level = detect_idle_level(200);
    printf("рівень спокою DO = %s\r\n",
           idle_level == GPIO_PIN_SET ? "SET (звук → RESET)" : "RESET (звук → SET)");
}
