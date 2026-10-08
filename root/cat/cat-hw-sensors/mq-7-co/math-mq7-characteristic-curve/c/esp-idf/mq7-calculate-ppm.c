#include <math.h>

typedef struct {
    float r_l_kohm;     // Опір R_L у кОм
    float r_0_kohm;     // Калібрований опір R_0 у кОм
    float v_cc;         // Напруга живлення (В)
    float v_ref;        // Опорна напруга АЦП (В)
    uint32_t adc_max;   // Максимальний відлік АЦП (напр. 4095 для 12 біт)
    float coeff_a;      // Степеневий коефіцієнт a
    float coeff_b;      // Степеневий коефіцієнт b
} mq7_config_t;

float mq7_calculate_ppm(uint32_t adc_raw, float temp, float hum, const mq7_config_t* config) {
    if (adc_raw == 0 || config->r_0_kohm <= 0.0f) {
        return 0.0f;
    }

    float v_out = ((float)adc_raw * config->v_ref) / (float)config->adc_max;
    float r_s = config->r_l_kohm * (config->v_cc - v_out) / v_out;

    float k_factor = calculate_k_factor(temp, hum);
    float r_s_corr = r_s / k_factor;

    float ratio = r_s_corr / config->r_0_kohm;
    return config->coeff_a * powf(ratio, config->coeff_b);
}
