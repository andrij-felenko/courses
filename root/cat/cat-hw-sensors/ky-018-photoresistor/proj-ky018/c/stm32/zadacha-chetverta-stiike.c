#include "main.h"

extern ADC_HandleTypeDef hadc1;     // ADC1, вхід IN0 → PA0, 12 біт

#define DARK_ON    1200   // темніше цього → УВІМКНУТИ (нижній поріг, 12 біт)
#define LIGHT_OFF  1600   // світліше цього → ВИМКНУТИ (верхній поріг)

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

void lamp_loop(void) {              // кликати з main() після MX_*_Init()
  bool lamp_on = false;             // поточний стан — частина рішення!
  for (;;) {
    uint16_t light = ldr_read();    // (краще — уже згладжений; див. збірку нижче)

    if (!lamp_on && light < DARK_ON)       lamp_on = true;   // було світло, стало темно
    else if (lamp_on && light > LIGHT_OFF) lamp_on = false;  // було темно, стало світло
    // якщо відлік між порогами — жодна умова не спрацює, стан лишається

    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,
                      lamp_on ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_Delay(50);
  }
}
