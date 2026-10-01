#include "sir_adc.h"
#include <math.h>

void sir_adc_init(SirAdcChannel_t *channel) {
    if (!channel) return;

    for (uint8_t i = 0; i < SIR_FILTER_WINDOW_SIZE; i++) {
        channel->raw_samples[i] = 0;
    }
    channel->sample_index = 0;
    channel->buffer_filled = false;
    channel->measured_voltage = 0.0f;
    channel->leakage_current_ua = 0.0f;
    channel->sir_resistance_mohm = 0.0f;
    channel->status = SIR_STATUS_OK;
    channel->alarm_active = false;
}

float sir_adc_calculate_resistance(float voltage_v) {
    /* Запобігання діленню на нуль при відсутності струму витоку */
    if (voltage_v <= 0.0001f) {
        return 99999.0f; /* Нескінченно високий опір (чиста плата) */
    }

    /* Струм витоку через поверхню плати та баластний резистор: I = V_adc / R_sense */
    float current_amperes = voltage_v / SIR_SENSE_RESISTOR_OHM;
    
    /* Опір ізоляції за законом Ома: R_sir = (V_test - V_adc) / I */
    float r_sir_ohms = (SIR_TEST_VOLTAGE_VOLTS - voltage_v) / current_amperes;
    
    /* Переведення в Мегаоми (1 MOm = 1e6 Om) */
    return r_sir_ohms / 1000000.0f;
}

SirStatus_t sir_adc_evaluate_status(float resistance_mohm) {
    if (resistance_mohm >= SIR_THRESHOLD_PASS_MOHM) {
        return SIR_STATUS_OK;
    } else if (resistance_mohm >= SIR_THRESHOLD_WARN_MOHM) {
        return SIR_STATUS_WARNING;
    } else {
        return SIR_STATUS_CRITICAL_LEAKAGE;
    }
}

bool sir_adc_update_sample(SirAdcChannel_t *channel, uint16_t raw_adc_value) {
    if (!channel) return false;

    /* Запис нового відліку у кільцевий буфер */
    channel->raw_samples[channel->sample_index] = raw_adc_value;
    channel->sample_index = (channel->sample_index + 1) % SIR_FILTER_WINDOW_SIZE;
    
    if (channel->sample_index == 0) {
        channel->buffer_filled = true;
    }

    /* Обчислення ковзного усереднення для придушення високочастотних шумів */
    uint32_t sum = 0;
    uint8_t count = channel->buffer_filled ? SIR_FILTER_WINDOW_SIZE : channel->sample_index;
    
    if (count == 0) return false;

    for (uint8_t i = 0; i < count; i++) {
        sum += channel->raw_samples[i];
    }
    
    float avg_raw = (float)sum / (float)count;

    /* Перетворення цифрового коду в напругу: V = (ADC_code / (2^N - 1)) * Vref */
    float max_code = (float)((1 << SIR_ADC_RESOLUTION_BITS) - 1);
    channel->measured_voltage = (avg_raw / max_code) * SIR_ADC_VREF_VOLTS;

    /* Розрахунок струму витоку в мікроамперах (мкА) */
    channel->leakage_current_ua = (channel->measured_voltage / SIR_SENSE_RESISTOR_OHM) * 1000000.0f;

    /* Обчислення поверхневого опору ізоляції SIR */
    channel->sir_resistance_mohm = sir_adc_calculate_resistance(channel->measured_voltage);

    /* Оцінка діелектричного стану та спрацювання сигналізації */
    channel->status = sir_adc_evaluate_status(channel->sir_resistance_mohm);
    channel->alarm_active = (channel->status == SIR_STATUS_CRITICAL_LEAKAGE);

    return true;
}
