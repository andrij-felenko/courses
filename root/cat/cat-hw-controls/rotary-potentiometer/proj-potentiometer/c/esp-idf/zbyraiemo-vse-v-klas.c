// ── Те саме мовою ESP-IDF: структура стану + функції над нею (ідіоматичний C).
#include "esp_adc/adc_oneshot.h"
#include <stdbool.h>
#include <stdlib.h>

#define ADC_MAX 4095                 // 12 біт, задано .bitwidth каналу

typedef struct {
  adc_oneshot_unit_handle_t unit;
  adc_channel_t chan;
  uint8_t shift;
  int  deadband, calMin, calMax, lastAccepted;
  long ema;                          // стан EMA у масштабі ×2^shift
} pot_t;

static int  clampi(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }
static int  scale(int v, int iLo, int iHi, int oLo, int oHi) {   // замість map()
  return (v - iLo) * (oHi - oLo) / (iHi - iLo) + oLo;
}
static int  sample(pot_t *p) { int v = 0; ESP_ERROR_CHECK(adc_oneshot_read(p->unit, p->chan, &v)); return v; }

// Викликати раз на старті: ініціалізувати фільтр першим відліком.
void pot_begin(pot_t *p, adc_oneshot_unit_handle_t unit, adc_channel_t ch,
               uint8_t shift, int deadband) {
  p->unit = unit; p->chan = ch; p->shift = shift; p->deadband = deadband;
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
