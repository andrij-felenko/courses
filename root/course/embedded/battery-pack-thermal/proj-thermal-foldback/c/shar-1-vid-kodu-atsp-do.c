#include <stdint.h>

#define ADC_MAX     4095        // 12-бітний АЦП
#define R_PULL_OHM  10000       // верхнє плече дільника, Ом

#define OHM_OPEN   (-1)         // обрив давача (опір «нескінченний»)
#define OHM_SHORT  (-2)         // коротке замикання давача (опір нульовий)

// Код АЦП → опір NTC в омах. У нашому дільнику NTC стоїть знизу до землі,
// тож фізика крайніх кодів однозначна:
//   code = ADC_MAX  →  Vadc = Vcc  →  опір NTC «нескінченний»  →  ОБРИВ;
//   code = 0        →  Vadc = 0    →  опір NTC нульовий         →  КЗ.
int32_t adc_to_ohm(uint16_t code) {
    if (code >= ADC_MAX)  return OHM_OPEN;       // прилипло до Vcc → обрив
    if (code == 0)        return OHM_SHORT;      // прилипло до нуля → КЗ
    return (int32_t)R_PULL_OHM * code / (ADC_MAX - code);
}
