/* У STM32 заводська стала одна — VREFINT_CAL: код внутрішнього опорного джерела,
   знятий на конвеєрі при VDDA = 3.3 В і 12 бітах (F4). Через неї міряють СПРАВЖНЮ
   VDDA конкретної плати, а вже від неї — напругу на повзунку. */
#include "main.h"
#define VREFINT_CAL (*(uint16_t *)0x1FFF7A2AU)   // STM32F4: адреса заводської сталої

// vrefRaw — відлік каналу ADC_CHANNEL_VREFINT, potRaw — відлік повзунка
uint32_t pot_millivolts(uint16_t vrefRaw, uint16_t potRaw) {
  uint32_t vdda_mv = 3300u * VREFINT_CAL / vrefRaw;   // реальне живлення АЦП, мВ
  return vdda_mv * potRaw / 4095u;                    // напруга на повзунку, мВ
}
