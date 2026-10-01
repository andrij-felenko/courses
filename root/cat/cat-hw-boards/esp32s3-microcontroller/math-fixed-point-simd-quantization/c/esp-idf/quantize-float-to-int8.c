#include <stdint.h>
#include <math.h>

// Структура параметрів афінного квантування
typedef struct {
    float scale;
    int32_t zero_point;
} quant_params_t;

// Квантування дійсного значення в INT8
int8_t quantize_float_to_int8(float x, quant_params_t params) {
    float scaled = x / params.scale;
    int32_t val = (int32_t)roundf(scaled) + params.zero_point;
    if (val < -128) return -128;
    if (val > 127) return 127;
    return (int8_t)val;
}

// Скалярний добуток квантованих векторів із симетричними вагами (Z_w = 0)
float dot_product_quantized_c(const int8_t *activations, const int8_t *weights,
                              int len, quant_params_t p_a, quant_params_t p_w) {
    int32_t acc_aw = 0;
    int32_t acc_w = 0;
    for (int i = 0; i < len; i++) {
        acc_aw += (int32_t)activations[i] * (int32_t)weights[i];
        acc_w += (int32_t)weights[i];
    }
    int32_t sum_int = acc_aw - p_a.zero_point * acc_w;
    return p_a.scale * p_w.scale * (float)sum_int;
}
