// ── Те саме на STM32 HAL: структура стану + функції. Один екземпляр = один канал ADC.
#include "main.h"
#include <stdbool.h>
#include <stdlib.h>

#define ADC_MAX 4095                 // 12 біт, поле Resolution в MX_ADCx_Init

typedef struct {
  ADC_HandleTypeDef *hadc;
  uint8_t shift;
  int  deadband, calMin, calMax, lastAccepted;
  long ema;                          // стан EMA у масштабі ×2^shift
} pot_t;

static int clampi(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }
static int scale(int v, int iLo, int iHi, int oLo, int oHi) {    // замість map()
  return (v - iLo) * (oHi - oLo) / (iHi - iLo) + oLo;
}
static int sample(pot_t *p) {        // старт → дочекатись → забрати
  HAL_ADC_Start(p->hadc);
  HAL_ADC_PollForConversion(p->hadc, 10);
  int v = (int)HAL_ADC_GetValue(p->hadc);
  HAL_ADC_Stop(p->hadc);
  return v;
}

// Викликати раз на старті: ініціалізувати фільтр першим відліком.
void pot_begin(pot_t *p, ADC_HandleTypeDef *hadc, uint8_t shift, int deadband) {
  p->hadc = hadc; p->shift = shift; p->deadband = deadband;
  p->calMin = ADC_MAX; p->calMax = 0; p->lastAccepted = -10000;
  p->ema = (long)sample(p) << shift;
}

// Згладжене СИРЕ значення 0..ADC_MAX (оновлює фільтр). Основа для решти.
int pot_raw(pot_t *p) {
  long delta = ((long)sample(p) << p->shift) - p->ema;
  p->ema += (delta >> p->shift);
  return (int)((p->ema + (1 << (p->shift - 1))) >> p->shift);   // з округленням
}

// Викликати в циклі, поки користувач крутить ручку від упору до упору.
void pot_calibrate(pot_t *p) {
  int v = pot_raw(p);                // калібруємо по ЗГЛАДЖЕНОМУ, не по сирому
  if (v < p->calMin) p->calMin = v;
  if (v > p->calMax) p->calMax = v;
}
void pot_use_full_range(pot_t *p) { p->calMin = 0; p->calMax = ADC_MAX; }

// Згладжене й КАЛІБРОВАНЕ значення в [outLo..outHi]; outLo>outHi → інверсія.
int pot_value(pot_t *p, int outLo, int outHi) {
  int lo = outLo < outHi ? outLo : outHi, hi = outLo < outHi ? outHi : outLo;
  return clampi(scale(pot_raw(p), p->calMin, p->calMax, outLo, outHi), lo, hi);
}

// true й записує *out, ЛИШЕ коли значення відійшло від прийнятого далі за мертву зону.
// Мертва зона працює в СИРИХ одиницях, тож стабільна незалежно від масштабу виходу.
bool pot_changed(pot_t *p, int *out, int outLo, int outHi) {
  int now = pot_raw(p);
  if (abs(now - p->lastAccepted) < p->deadband) return false;
  p->lastAccepted = now;
  int lo = outLo < outHi ? outLo : outHi, hi = outLo < outHi ? outHi : outLo;
  *out = clampi(scale(now, p->calMin, p->calMax, outLo, outHi), lo, hi);
  return true;
}
