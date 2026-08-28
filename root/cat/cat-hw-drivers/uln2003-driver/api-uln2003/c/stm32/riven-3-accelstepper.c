#include <math.h>

// На STM32 трапецію природно веде ТАЙМЕР, і головний цикл не задіяно взагалі.
// TIM2 у CubeMX: такт 1 МГц (Prescaler = SystemCoreClock/1e6 - 1), переривання
// ввімкнено. Кожне переповнення = один півкрок; ARR = інтервал у мікросекундах.
#define VMAX   700.0f
#define ACCEL  400.0f

volatile int32_t position = 0, remaining = 0;
volatile int8_t  dir = +1;
static   float   v = 1.0f;

void moveTo(int32_t target) {
  remaining = (target > position) ? target - position : position - target;
  dir = (target > position) ? +1 : -1;
  v = 1.0f;
  __HAL_TIM_SET_AUTORELOAD(&htim2, (uint32_t)(1000000.0f / v) - 1);
  HAL_TIM_Base_Start_IT(&htim2);        // далі все робить переривання
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance != TIM2) return;
  if (remaining == 0) { HAL_TIM_Base_Stop_IT(&htim2); return; }

  idx = (idx + dir + 8) % 8;
  apply_step(idx);
  position += dir;
  remaining--;

  float vt = fminf(VMAX, sqrtf(2.0f * ACCEL * (float)remaining));
  if (v < vt) v += ACCEL / v;           // приріст за час одного кроку
  if (v > vt) v = vt;
  __HAL_TIM_SET_AUTORELOAD(htim, (uint32_t)(1000000.0f / v) - 1);
}
