// Драйвер діагностики та керування смарт-ключами (C99)
#include <stdint.h>
#include <stdbool.h>

#define CHANNELS_COUNT        4U
#define CS_ADC_VREF_MV        3300U
#define CS_ADC_MAX_CODE       4095U
#define CS_RESISTOR_OHMS      1000U
#define CURRENT_RATIO_K       1000U     // K_ratio = 1000 (1 мА на CS = 1 А на виході)
#define CURRENT_MAX_LIMIT_MA  2500U     // Поріг аварії за струмом 2.5 А
#define OPEN_LOAD_LIMIT_MA    10U       // Поріг детекції обриву навантаження

typedef enum {
    LOAD_OK = 0,
    LOAD_OPEN_CIRCUIT,
    LOAD_OVERCURRENT,
    LOAD_THERMAL_SHUTDOWN
} channel_diagnostic_t;

typedef struct {
    bool enabled_target;
    bool is_hardware_fault;
    uint32_t load_current_ma;
    channel_diagnostic_t status;
    uint32_t fault_timestamp_ms;
} channel_state_t;

static channel_state_t channels[CHANNELS_COUNT];

// Переведення коду АЦП виводу Current Sense у міліампери
static uint32_t calculate_current_ma(uint16_t adc_code) {
    uint32_t v_sense_mv = ((uint32_t)adc_code * CS_ADC_VREF_MV) / CS_ADC_MAX_CODE;
    // I_cs = V_sense / R_cs; I_out = I_cs * K_ratio
    uint32_t i_out_ma = (v_sense_mv * CURRENT_RATIO_K) / CS_RESISTOR_OHMS;
    return i_out_ma;
}

void smart_switch_init(void) {
    for (uint8_t i = 0; i < CHANNELS_COUNT; ++i) {
        channels[i].enabled_target = false;
        channels[i].is_hardware_fault = false;
        channels[i].load_current_ma = 0;
        channels[i].status = LOAD_OK;
        channels[i].fault_timestamp_ms = 0;
    }
}

// Періодичний цикл опитування діагностики (виклик раз на 10 мс)
void smart_switch_process(uint8_t ch, bool fault_pin_active, uint16_t cs_adc_code, uint32_t now_ms) {
    if (ch >= CHANNELS_COUNT) return;
    
    channel_state_t *c = &channels[ch];
    c->load_current_ma = calculate_current_ma(cs_adc_code);
    c->is_hardware_fault = fault_pin_active;

    if (fault_pin_active) {
        // Апаратне вимкнення за перегрівом кристала
        c->status = LOAD_THERMAL_SHUTDOWN;
        c->enabled_target = false;
        c->fault_timestamp_ms = now_ms;
        return;
    }

    if (c->enabled_target) {
        if (c->load_current_ma > CURRENT_MAX_LIMIT_MA) {
            c->status = LOAD_OVERCURRENT;
            c->enabled_target = false;
            c->fault_timestamp_ms = now_ms;
        } else if (c->load_current_ma < OPEN_LOAD_LIMIT_MA) {
            c->status = LOAD_OPEN_CIRCUIT;
        } else {
            c->status = LOAD_OK;
        }
    } else {
        // Якщо канал вимкнено, скидаємо статус після охолодження
        if (c->status != LOAD_OK && (now_ms - c->fault_timestamp_ms > 3000U)) {
            c->status = LOAD_OK;
        }
    }
}
