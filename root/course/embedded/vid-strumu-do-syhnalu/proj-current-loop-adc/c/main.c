#include <stdint.h>
#include <stdbool.h>

// Діагностичні стани лінії за стандартом NAMUR NE 43
typedef enum {
    CURRENT_LOOP_OK = 0,
    CURRENT_LOOP_WARN_UNDER_RANGE,
    CURRENT_LOOP_WARN_OVER_RANGE,
    CURRENT_LOOP_ERROR_WIRE_BREAK,
    CURRENT_LOOP_ERROR_SHORT_CIRCUIT
} CurrentLoopStatus;

// Структура конфігурації вимірювального каналу
typedef struct {
    float r_shunt_ohms;       // Опір вимірювального шунта (100.0 або 250.0 Ом)
    float v_ref_volts;        // Опорна напруга АЦП (3.30 або 5.00 В)
    uint32_t adc_max_ticks;   // Максимальний код АЦП (4095 для 12 біт)
    float filter_alpha;       // Вага експоненційного фільтра (0.05..0.20)
    float phys_zero;          // Фізичне значення при 4.0 мА (наприклад, 0.0 бар)
    float phys_span;          // Фізичне значення при 20.0 мА (наприклад, 16.0 бар)
    
    // Внутрішній стан фільтрації та калібрування
    float filtered_voltage;   // Поточна згладжена напруга на шунті
    bool is_initialized;      // Прапорець первинного прогріву фільтра
} CurrentLoopChannel;

// Структура результату обробки
typedef struct {
    float current_ma;         // Струм петлі в міліамперах
    float physical_value;     // Обчислена фізична величина
    CurrentLoopStatus status; // Діагностичний стан лінії
} LoopMeasurement;

void current_loop_init(CurrentLoopChannel *ch, float r_shunt, float v_ref, 
                       uint32_t adc_max, float alpha, float p_zero, float p_span) {
    ch->r_shunt_ohms = r_shunt;
    ch->v_ref_volts = v_ref;
    ch->adc_max_ticks = adc_max;
    ch->filter_alpha = alpha;
    ch->phys_zero = p_zero;
    ch->phys_span = p_span;
    ch->filtered_voltage = 0.0f;
    ch->is_initialized = false;
}

LoopMeasurement current_loop_process(CurrentLoopChannel *ch, uint16_t raw_adc) {
    LoopMeasurement result;
    
    // Перетворення вибірки АЦП на напругу шунта
    float raw_voltage = ((float)raw_adc / (float)ch->adc_max_ticks) * ch->v_ref_volts;
    
    // Експоненційне згладжування завад
    if (!ch->is_initialized) {
        ch->filtered_voltage = raw_voltage;
        ch->is_initialized = true;
    } else {
        ch->filtered_voltage += ch->filter_alpha * (raw_voltage - ch->filtered_voltage);
    }
    
    // Розрахунок струму в міліамперах: I = (U / R) * 1000
    float current_ma = (ch->filtered_voltage / ch->r_shunt_ohms) * 1000.0f;
    result.current_ma = current_ma;
    
    // Класифікація стану згідно з NAMUR NE 43
    if (current_ma < 3.60f) {
        result.status = CURRENT_LOOP_ERROR_WIRE_BREAK;
        result.physical_value = ch->phys_zero;
    } else if (current_ma < 3.80f) {
        result.status = CURRENT_LOOP_WARN_UNDER_RANGE;
        result.physical_value = ch->phys_zero;
    } else if (current_ma > 21.00f) {
        result.status = CURRENT_LOOP_ERROR_SHORT_CIRCUIT;
        result.physical_value = ch->phys_span;
    } else if (current_ma > 20.50f) {
        result.status = CURRENT_LOOP_WARN_OVER_RANGE;
        result.physical_value = ch->phys_span;
    } else {
        result.status = CURRENT_LOOP_OK;
        // Лінійна інтерполяція в діапазоні 4.0..20.0 мА
        float fraction = (current_ma - 4.0f) / (20.0f - 4.0f);
        result.physical_value = ch->phys_zero + fraction * (ch->phys_span - ch->phys_zero);
    }
    
    return result;
}
