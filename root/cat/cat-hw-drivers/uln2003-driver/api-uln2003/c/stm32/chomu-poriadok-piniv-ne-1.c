// Готової бібліотеки нема — обгортка над рівнем 1. Уся «магія» Stepper
// зводиться ось до цих двох масивів: виводи в МАГНІТНОМУ порядку 1-3-2-4,
// а не так, як ідуть дроти.
static GPIO_TypeDef *const MP[4] = { IN1_GPIO_Port, IN3_GPIO_Port,
                                     IN2_GPIO_Port, IN4_GPIO_Port };
static const uint16_t      MN[4] = { IN1_Pin, IN3_Pin, IN2_Pin, IN4_Pin };

#define STEPS_PER_REV 2038   // ПОВНИХ кроків вала, ≈ 32 · 63.684 (НЕ 2048!)

// Повнокрокова послідовність (саме її ганяє Stepper): по дві сусідні обмотки.
static const uint8_t full_seq[4][4] = {
  {1,1,0,0}, {0,1,1,0}, {0,0,1,1}, {1,0,0,1},
};

static uint32_t step_ms = 3;   // ≈ 10 об/хв при 2038 кроках на оберт

static void stepper_step(int32_t steps) {
  static uint8_t s = 0;
  int8_t dir = steps > 0 ? +1 : -1;
  for (int32_t i = 0; i < (steps > 0 ? steps : -steps); i++) {
    s = (s + dir + 4) % 4;
    for (uint8_t k = 0; k < 4; k++)
      HAL_GPIO_WritePin(MP[k], MN[k], full_seq[s][k] ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_Delay(step_ms);
  }
}
