#include <Arduino.h>
#include <cmath>

struct QuantParams {
    float scale;
    int32_t zero_point;
};

int8_t quantizeFloatToInt8(float x, const QuantParams& params) {
    float scaled = x / params.scale;
    int32_t val = static_cast<int32_t>(std::round(scaled)) + params.zero_point;
    return static_cast<int8_t>(constrain(val, -128, 127));
}

float dotProductQuantizedCpp(const int8_t* activations, const int8_t* weights,
                             size_t len, const QuantParams& p_a, const QuantParams& p_w) {
    int32_t acc_aw = 0;
    int32_t acc_w = 0;
    for (size_t i = 0; i < len; ++i) {
        acc_aw += static_cast<int32_t>(activations[i]) * static_cast<int32_t>(weights[i]);
        acc_w += static_cast<int32_t>(weights[i]);
    }
    int32_t sum_int = acc_aw - p_a.zero_point * acc_w;
    return p_a.scale * p_w.scale * static_cast<float>(sum_int);
}
