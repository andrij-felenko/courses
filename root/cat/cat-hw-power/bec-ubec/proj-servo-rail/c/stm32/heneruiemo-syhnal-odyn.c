// ── Керування сервами на UBEC-шині. STM32 (HAL, канал PWM таймера) ──
// Таймер налаштований у CubeMX: прескалер дає тик 1 мкс, ARR = 20000-1
// → кадр 20 мс. Тоді регістр порівняння (CCR) — це ПРЯМО ширина полички
// в мікросекундах, без жодної арифметики скважності.
#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim3;        // TIM3: чотири канали = чотири серва

#define N 4
static const uint32_t CH[N] = {TIM_CHANNEL_1, TIM_CHANNEL_2,
                               TIM_CHANNEL_3, TIM_CHANNEL_4};

static const uint16_t US_MIN = 1000;   // край ходу, мкс (звірити з паспортом!)
static const uint16_t US_MID = 1500;   // центр
static const uint16_t US_MAX = 2000;   // інший край

// градуси 0..180 → мікросекунди 1000..2000 (лінійно)
static uint16_t AngleToUs(uint8_t deg) {
  if (deg > 180) deg = 180;
  return US_MIN + (uint32_t)(US_MAX - US_MIN) * deg / 180;
}

void ServoInit(void) {
  for (uint8_t i = 0; i < N; i++) {
    __HAL_TIM_SET_COMPARE(&htim3, CH[i], US_MID);  // старт із центру
    HAL_TIM_PWM_Start(&htim3, CH[i]);              // таймер починає гнати сигнал
  }
}

// Повернути одне серво в кут: пишемо мікросекунди просто в регістр порівняння.
void ServoMove(uint8_t i, uint8_t deg) {
  __HAL_TIM_SET_COMPARE(&htim3, CH[i], AngleToUs(deg));
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_TIM3_Init();
  ServoInit();
  for (;;) {
    ServoMove(0, 45);    // приклад: розкидати серва по кутах
    ServoMove(1, 135);
    HAL_Delay(1000);
  }
}
