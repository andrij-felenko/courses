#include <stdint.h>
#include <stdbool.h>

// Структура цифрового фазочутливого демодулятора LVDT
typedef struct {
    float lpf_alpha;        // Коефіцієнт низькочастотного фільтра (0.0 .. 1.0)
    float filtered_output;  // Відфільтрований вихідний сигнал постійного струму
} lvdt_demodulator_t;

void lvdt_demodulator_init(lvdt_demodulator_t *demod, float alpha) {
    demod->lpf_alpha = alpha;
    demod->filtered_output = 0.0f;
}

// Обробка одного дискретного відліку (викликається в перериванні АЦП)
float lvdt_demodulator_process(lvdt_demodulator_t *demod, float exc_sample, float sec_sample) {
    // Формування опорного прямокутного сигналу зі знаку збудження
    float ref_sign = (exc_sample >= 0.0f) ? 1.0f : -1.0f;
    
    // Перемножування вторинного сигналу на опорну фазу
    float rectified = sec_sample * ref_sign;
    
    // Однополюсний ФНЧ (IIR фільтр першого порядку)
    demod->filtered_output += demod->lpf_alpha * (rectified - demod->filtered_output);
    
    return demod->filtered_output;
}
