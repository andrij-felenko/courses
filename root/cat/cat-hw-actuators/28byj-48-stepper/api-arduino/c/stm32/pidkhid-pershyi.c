// 28BYJ-48 через ULN2003. STM32 + HAL. IN1..IN4 — чотири GPIO Output Push-Pull
// (тут PB0..PB3, налаштовані в CubeMX). Бібліотеки крокового двигуна не треба.
#include "main.h"

#define STEPS_PER_REV  2038

typedef struct { GPIO_TypeDef *port; uint16_t pin; } out_t;

static const out_t IN[4] = {           // IN1..IN4 у ФІЗИЧНОМУ порядку
    { GPIOB, GPIO_PIN_0 }, { GPIOB, GPIO_PIN_1 },
    { GPIOB, GPIO_PIN_2 }, { GPIOB, GPIO_PIN_3 },
};

// Повнокрокова послідовність: чергування обмоток уже закладено в таблицю —
// це те саме, що дає Stepper, коли їй передати піни в порядку 8, 10, 9, 11.
static const uint8_t FULL_STEP[4][4] = {
    {1, 1, 0, 0},
    {0, 1, 1, 0},
    {0, 0, 1, 1},
    {1, 0, 0, 1},
};

static int phase = 0;

static void apply_phase(int p) {
  for (int i = 0; i < 4; i++)
    HAL_GPIO_WritePin(IN[i].port, IN[i].pin,
                      FULL_STEP[p][i] ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

// Блокуючий рух на n кроків; step_ms — пауза між тактами. Тік HAL — 1 мс,
// для 28BYJ-48 такої роздільності вистачає з головою.
static void stepper_step(int n, uint32_t step_ms) {
  int dir = (n >= 0) ? 1 : -1;
  int total = n * dir;
  for (int i = 0; i < total; i++) {
    phase = (phase + dir + 4) % 4;
    apply_phase(phase);
    HAL_Delay(step_ms);
  }
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  while (1) {
    stepper_step( STEPS_PER_REV, 3);      // оберт уперед; 3 мс/крок ≈ 10 об/хв
    HAL_Delay(1000);
    stepper_step(-STEPS_PER_REV, 3);      // оберт назад
    HAL_Delay(1000);
  }
}
