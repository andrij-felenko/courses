#include <math.h>
#include <stdbool.h>

typedef struct {
    float v_ref;
    float adc_max;
    float sensitivity_v_g;
    float zero_offset_raw;
    float alpha_hpf;
    float prev_x;
    float prev_y;
    float threshold_g;
} piezo_processor_t;

void piezo_init(piezo_processor_t *proc, float v_ref, float adc_bits, float sensitivity) {
    proc->v_ref = v_ref;
    proc->adc_max = powf(2.0f, adc_bits) - 1.0f;
    proc->sensitivity_v_g = sensitivity;
    proc->zero_offset_raw = proc->adc_max / 2.0f;
    proc->alpha_hpf = 0.95f;
    proc->prev_x = 0.0f;
    proc->prev_y = 0.0f;
    proc->threshold_g = 1.5f;
}

bool piezo_process_sample(piezo_processor_t *proc, float raw_adc, float *accel_g) {
    // 1. Компенсація зміщення нуля та конвертація в напругу
    float delta_adc = raw_adc - proc->zero_offset_raw;
    float v_signal = (delta_adc * proc->v_ref) / proc->adc_max;

    // 2. Розрахунок фізичного прискорення (g)
    float accel_raw = v_signal / proc->sensitivity_v_g;

    // 3. IIR фільтрація високих частот (усунення дрейфу)
    float accel_filtered = proc->alpha_hpf * (proc->prev_y + accel_raw - proc->prev_x);
    proc->prev_x = accel_raw;
    proc->prev_y = accel_filtered;

    *accel_g = accel_filtered;

    // 4. Порогова детекція динамічної події
    return fabsf(accel_filtered) >= proc->threshold_g;
}
