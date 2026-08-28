// Завершення тракту в коді: читаємо АЦП, переводимо код у вагу.
// Підсилення (×400) і антиаліасинг зробило ЗАЛІЗО до цього рядка.
// Тут лишається масштабування й легке цифрове згладжування.

#define ADC_MAX     4095.0f     // 12 біт
#define VREF        3.3f        // опора АЦП, В
#define GAIN        400.0f      // коефіцієнт інструментального підсилювача
#define MV_PER_V    2.0f        // чутливість містка, мВ/В
#define EXC_V       3.3f        // живлення містка, В

// одна цифрова RC-ланка — дочищаємо те, що лишив залізний фільтр
static float smooth = 0.0f;
static const float alpha = 0.05f;   // повільне згладжування

float read_weight_kg(uint16_t adc_code) {
    float v_adc  = (adc_code / ADC_MAX) * VREF;     // код → напруга на вході АЦП
    float v_sens = v_adc / GAIN;                    // знімаємо підсилення → сигнал давача
    float full_scale_v = (MV_PER_V * EXC_V) / 1000.0f;  // сигнал на повній вазі, В
    float kg = (v_sens / full_scale_v) * 50.0f;     // лінійне масштабування у кг

    smooth += alpha * (kg - smooth);                // легке згладжування в коді
    return smooth;
}
