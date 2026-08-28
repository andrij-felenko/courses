#include <stdint.h>
#include <stdbool.h>

// Діагностичні статуси струмової петлі за NAMUR NE 43
typedef enum {
    LOOP_STATE_OK = 0,
    LOOP_STATE_UNDER_RANGE_WARN,
    LOOP_STATE_OVER_RANGE_WARN,
    LOOP_STATE_FAULT_WIRE_BREAK,
    LOOP_STATE_FAULT_SHORT_CIRCUIT
} LoopDiagnosticState;

// Конфігурація аналогового струмового каналу
typedef struct {
    float r_shunt_ohms;      // Номінал шунта (наприклад, 100.0 Ом)
    float v_reference_volts; // Опорна напруга АЦП (3.30 В)
    uint32_t adc_resolution; // Максимальний код АЦП (4095 для 12 біт)
    float filter_weight;     // Коефіцієнт експоненційного фільтра (0.05..0.2)
    float phys_scale_zero;   // Значення величини при 4.0 мА (0.0 бар)
    float phys_scale_span;   // Значення величини при 20.0 мА (16.0 бар)
    
    // Внутрішній стан каналу
    float smoothed_voltage;  // Згладжена напруга шунта (В)
    bool is_warmed_up;       // Прапорець завершення ініціалізації
} AnalogCurrentLoop;

// Результат вимірювання
typedef struct {
    float current_milliamps; // Розрахований струм лінії (мА)
    float measured_value;    // Фізична величина
    LoopDiagnosticState state; // Стан лінії
} LoopReading;

void analog_loop_init(AnalogCurrentLoop *inst, float r_shunt, float v_ref, 
                      uint32_t adc_max, float alpha, float p_zero, float p_span) {
    inst->r_shunt_ohms = r_shunt;
    inst->v_reference_volts = v_ref;
    inst->adc_resolution = adc_max;
    inst->filter_weight = alpha;
    inst->phys_scale_zero = p_zero;
    inst->phys_scale_span = p_span;
    inst->smoothed_voltage = 0.0f;
    inst->is_warmed_up = false;
}

LoopReading analog_loop_update(AnalogCurrentLoop *inst, uint16_t adc_raw_code) {
    LoopReading out;
    
    // Перетворення вибірки АЦП на напругу на клемах шунта
    float instant_voltage = ((float)adc_raw_code / (float)inst->adc_resolution) * inst->v_reference_volts;
    
    // Експоненційне згладжування шуму: y[k] = y[k-1] + alpha * (x[k] - y[k-1])
    if (!inst->is_warmed_up) {
        inst->smoothed_voltage = instant_voltage;
        inst->is_warmed_up = true;
    } else {
        inst->smoothed_voltage += inst->filter_weight * (instant_voltage - inst->smoothed_voltage);
    }
    
    // Струм петлі в міліамперах: I = (V / R) * 1000
    float current_ma = (inst->smoothed_voltage / inst->r_shunt_ohms) * 1000.0f;
    out.current_milliamps = current_ma;
    
    // Діагностика лінії за критеріями NAMUR NE 43
    if (current_ma < 3.60f) {
        out.state = LOOP_STATE_FAULT_WIRE_BREAK;
        out.measured_value = inst->phys_scale_zero;
    } else if (current_ma < 3.80f) {
        out.state = LOOP_STATE_UNDER_RANGE_WARN;
        out.measured_value = inst->phys_scale_zero;
    } else if (current_ma > 21.00f) {
        out.state = LOOP_STATE_FAULT_SHORT_CIRCUIT;
        out.measured_value = inst->phys_scale_span;
    } else if (current_ma > 20.50f) {
        out.state = LOOP_STATE_OVER_RANGE_WARN;
        out.measured_value = inst->phys_scale_span;
    } else {
        out.state = LOOP_STATE_OK;
        // Лінійне масштабування: 4.0 мА -> Zero, 20.0 мА -> Span
        float fraction = (current_ma - 4.0f) / (20.0f - 4.0f);
        out.measured_value = inst->phys_scale_zero + fraction * (inst->phys_scale_span - inst->phys_scale_zero);
    }
    
    return out;
}
