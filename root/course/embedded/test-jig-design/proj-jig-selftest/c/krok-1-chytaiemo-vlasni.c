#include <stdint.h>

// Місткість 12-бітного АЦП і паспортна напруга внутрішнього bandgap-еталона.
#define ADC_FULL_SCALE   4095u
#define VREFINT_MV       1200u     // ~1.20 В, з даташита конкретного МК

// Прочитати канал АЦП кілька разів і повернути усереднений сирий відлік.
// (чому усереднюємо — розберемо в пастці про шум; поки просто беремо середнє)
uint16_t adc_read_avg(uint8_t channel) {
    uint32_t acc = 0;
    for (int i = 0; i < 16; i++) {
        acc += adc_read_raw(channel);   // одиничне перетворення на каналі
    }
    return (uint16_t)(acc / 16u);
}

// Впізнати справжню опорну напругу через внутрішній bandgap.
// Ідея: bandgap дає ВІДОМІ VREFINT_MV. АЦП міряє його як vrefint_raw.
// Якщо повна шкала = Vref, то Vref_mv = VREFINT_MV * FULL_SCALE / vrefint_raw.
uint16_t measure_vref_mv(void) {
    uint16_t vrefint_raw = adc_read_avg(ADC_CH_VREFINT);
    if (vrefint_raw == 0) return 0;                 // захист від ділення на нуль
    return (uint16_t)((uint32_t)VREFINT_MV * ADC_FULL_SCALE / vrefint_raw);
}

// Перевести відлік будь-якого каналу у мілівольти, знаючи справжню Vref.
uint16_t adc_to_mv(uint16_t raw, uint16_t vref_mv) {
    return (uint16_t)((uint32_t)raw * vref_mv / ADC_FULL_SCALE);
}
