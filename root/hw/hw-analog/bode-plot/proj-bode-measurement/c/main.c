#include <math.h>
#include <stdint.h>

#define ADC_FS    3.3f      // повна шкала АЦП, В
#define ADC_MAX   4095.0f   // 12-бітний АЦП
#define SETTLE_MS 50        // > 5·τ кола (тут τ ≈ 160 мкс для f_c=1 кГц)
#define WINDOW    2000      // скільки вибірок беремо на одну точку

// зовнішні примітиви плати:
void  gen_set_freq(float hz);         // перелаштувати DDS/ШІМ-генератор
void  delay_ms(uint32_t ms);
float adc_read(uint8_t ch);           // одна вибірка, у вольтах

// розмах (peak-to-peak) каналу за вікно вибірок
static float measure_pp(uint8_t ch) {
    float vmin = ADC_FS, vmax = 0.0f;
    for (int i = 0; i < WINDOW; i++) {
        float v = adc_read(ch);
        if (v < vmin) vmin = v;
        if (v > vmax) vmax = v;
    }
    return vmax - vmin;                // подвоєна амплітуда
}

// одна точка АЧХ: повертає підсилення в децибелах
static float bode_point(float f) {
    gen_set_freq(f);                  // крок 1: частота змінилась…
    delay_ms(SETTLE_MS);              // крок 2: …дати колу встановитися
    float a_in  = measure_pp(0);      // крок 3: CH0 — вхід кола
    float a_out = measure_pp(1);      //         CH1 — вихід кола
    return 20.0f * log10f(a_out / a_in); // крок 4: відношення → дБ
}

void bode_sweep(float f_min, float f_max, int per_decade) {
    float mult = powf(10.0f, 1.0f / per_decade);   // лог-крок: рівний множник
    for (float f = f_min; f <= f_max * 1.001f; f *= mult) {
        float g = bode_point(f);
        printf("%8.1f Hz   %+6.1f dB\n", f, g);    // у файл/UART → у графік
    }
}
