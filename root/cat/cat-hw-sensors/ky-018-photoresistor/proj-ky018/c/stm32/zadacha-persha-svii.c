#include "main.h"

extern ADC_HandleTypeDef hadc1;  // CubeMX: ADC1, вхід IN0 → PA0, 12 біт

static uint16_t ldr_read(void) {
  HAL_ADC_Start(&hadc1);
  HAL_ADC_PollForConversion(&hadc1, 10);
  uint16_t v = HAL_ADC_GetValue(&hadc1);
  HAL_ADC_Stop(&hadc1);
  return v;
}

static int raw_min = 4095;   // «перевернуті» межі, щоб перший же відлік їх стягнув
static int raw_max = 0;

static void calibrate(uint16_t seconds) {
  uint32_t until = HAL_GetTick() + (uint32_t)seconds * 1000;
  while (HAL_GetTick() < until) {
    int v = ldr_read();
    if (v < raw_min) raw_min = v;  // побачили темніше — опустили дно
    if (v > raw_max) raw_max = v;  // побачили світліше — підняли стелю
    HAL_Delay(5);
  }
}
