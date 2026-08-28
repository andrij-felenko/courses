// Перевірка правдоподібності показу NTC. Повертає true, якщо значення робоче.
// adc — сирий код 12-бітного АЦП (0..4095) з дільника термістора.
#include <stdint.h>
#include <stdbool.h>

#define ADC_OPEN   60     // нижче — схоже на обрив (термістор «зник»)
#define ADC_SHORT  4035   // вище — схоже на коротке (термістор у нуль)

bool ntc_plausible(uint16_t adc) {
    if (adc <= ADC_OPEN)  return false;   // обрив дроту до термістора
    if (adc >= ADC_SHORT) return false;   // коротке або відпаяний дільник
    return true;                          // у робочому вікні — віримо
}
