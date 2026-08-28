/* dcr_sense_math.c - Реалізація алгоритму калібрування та термокорекції (C99) */
#include "dcr_sense_math.h"

void Dcr_Init(DcrChannel *ch, const DcrCalibParams *params) {
    if (!ch || !params) return;
    ch->params = *params;
    ch->current_temp_c = 25.0f;
    ch->effective_dcr = params->dcr_25c_ohm;
    ch->last_current_a = 0.0f;
    ch->params.adc_zero_offset = 0;
}

void Dcr_CalibrateZeroOffset(DcrChannel *ch, uint16_t raw_zero_adc) {
    if (!ch) return;
    ch->params.adc_zero_offset = (int16_t)raw_zero_adc;
}

void Dcr_UpdateTemperature(DcrChannel *ch, float temp_c) {
    if (!ch) return;
    ch->current_temp_c = temp_c;
    /* Оновлення значення омічного опору за лінійним законом міді */
    ch->effective_dcr = ch->params.dcr_25c_ohm * (1.0f + DCR_TCR_COPPER * (temp_c - 25.0f));
}

float Dcr_ProcessCurrentSample(DcrChannel *ch, uint16_t raw_adc) {
    if (!ch) return 0.0f;

    int32_t net_adc = (int32_t)raw_adc - (int32_t)ch->params.adc_zero_offset;
    if (net_adc <= 0) {
        ch->last_current_a = 0.0f;
        return 0.0f;
    }

    /* 1. Розрахунок напруги на вході АЦП */
    float v_adc = ((float)net_adc / DCR_ADC_RESOLUTION) * DCR_ADC_VREF;

    /* 2. Відновлення напруги на вимірювальному конденсаторі C_s */
    float v_cs = v_adc / ch->params.amp_gain;

    /* 3. Обчислення фізичного струму за відновленим DCR(T) */
    float current = v_cs / ch->effective_dcr;

    /* 4. Корекція нелінійності при роботі в зоні часткового насичення осердя */
    if (current > ch->params.isat_threshold_a) {
        float delta_i = current - ch->params.isat_threshold_a;
        current -= delta_i * delta_i * ch->params.sat_derate_coeff;
    }

    ch->last_current_a = current;
    return current;
}
