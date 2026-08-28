// ── Монітор просадки UBEC-шини. STM32 (HAL, ADC1) ──
// Дільник зменшує 5 В до вікна АЦП (опорна = 3.3 В); читаємо відлік
// і множимо назад. Канал і 12 біт налаштовані в CubeMX.
// Дільник: R1=15к (згори, від шини), R2=10к (до землі) → k = 0.4.
//   Uвузол = 5.0 · 0.4 = 2.0 В  (< 3.3 В — безпечно)
//   назад:  Uшини = Uвузол · (R1+R2)/R2 = Uвузол · 2.5
#include "stm32f4xx_hal.h"

extern ADC_HandleTypeDef hadc1;       // вхід шини заведено на канал ADC1

#define DIV         2.5f              // (15к+10к)/10к
#define VREF_MV     3300.0f           // опорна плати
#define ADC_FULL    4095.0f           // 12 біт
#define BROWNOUT_MV 4600              // поріг тривоги, мВ на шині

uint16_t RailReadMv(void) {
  uint32_t acc = 0;
  for (uint8_t i = 0; i < 8; i++) {   // усереднення 8 вибірок — прибрати шум
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    acc += HAL_ADC_GetValue(&hadc1);
  }
  HAL_ADC_Stop(&hadc1);
  float nodeMv = (acc / 8.0f) * VREF_MV / ADC_FULL;
  return (uint16_t)(nodeMv * DIV);    // назад у мілівольти шини
}

// Викликати нечасто (напр. раз на 100 мс) з головного циклу — не блокує.
void RailMonitorService(void) {
  static uint32_t last = 0;
  if (HAL_GetTick() - last < 100) return;
  last = HAL_GetTick();

  uint16_t mv = RailReadMv();
  if (mv < BROWNOUT_MV) {
    printf("BROWNOUT! шина = %u мВ — рознеси рухи / послаб навантаження\r\n", mv);
    // тут-таки реакція: НЕ починати нову розкладку серв, поки шина не встане,
    // запалити червоний LED, знизити кількість одночасних серв…
  }
}
