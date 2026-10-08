#include <stdint.h>

typedef struct {
    float gain_mm_per_volt;   // Коефіцієнт масштабування (мм/В)
    float zero_offset_volts;  // Напруга зміщення нуля (В)
    float adc_vref;           // Опорна напруга АЦП (В)
    uint32_t adc_max_codes;   // Максимальне значення АЦП (2^N - 1)
} lvdt_calibration_t;

// Перетворення сирих відліків АЦП у фізичне переміщення осердя LVDT (мм)
float lvdt_calculate_displacement_mm(uint32_t raw_adc_code, const lvdt_calibration_t *cal) {
    if (cal == 0 || cal->adc_max_codes == 0) {
        return 0.0f;
    }
    // 1. Перетворення коду АЦП у напругу в вольтах
    float v_measured = ((float)raw_adc_code / (float)cal->adc_max_codes) * cal->adc_vref;
    
    // 2. Віднімання зсуву нуля та множення на коефіцієнт підсилення
    float displacement_mm = (v_measured - cal->zero_offset_volts) * cal->gain_mm_per_volt;
    return displacement_mm;
}
