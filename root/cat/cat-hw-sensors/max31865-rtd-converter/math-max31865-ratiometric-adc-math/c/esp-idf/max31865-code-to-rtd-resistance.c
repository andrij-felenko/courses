#include <stdio.h>
#include <stdint.h>

// Номінал опорного резистора R_REF в Омах (для PT100)
#define R_REF_NOMINAL 400.0f
#define ADC_FULL_SCALE 32768.0f

/**
 * @brief Обчислення опору RTD за 15-бітним кодом АЦП MAX31865
 * @param adc_code 15-бітний цифровий код АЦП (0..32767)
 * @param r_ref Точне значення опорного резистора в Омах
 * @return Опір RTD в Омах
 */
float max31865_code_to_rtd_resistance(uint16_t adc_code, float r_ref) {
    // Вхідний код очищується від прапорця помилки (біту 0)
    uint16_t raw_code = adc_code >> 1;
    return ((float)raw_code * r_ref) / ADC_FULL_SCALE;
}

void app_main(void) {
    uint16_t raw_adc = 16384; // Приклад: півшкали АЦП
    float r_rtd = max31865_code_to_rtd_resistance(raw_adc << 1, R_REF_NOMINAL);
    
    printf("Код АЦП: %u, Обчислений опір RTD: %.4f Ом\n", raw_adc, r_rtd);
}
