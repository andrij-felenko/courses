#include "rtd_sensor.h"
#include <math.h>

float rtd_adc_to_voltage(uint32_t raw_adc, const rtd_config_t *config) {
    if (config == NULL || config->adc_max_code == 0 || config->vref_v <= 0.0f) {
        return 0.0f;
    }
    if (raw_adc > config->adc_max_code) {
        raw_adc = config->adc_max_code;
    }
    return ((float)raw_adc / (float)config->adc_max_code) * config->vref_v;
}

float rtd_voltage_to_raw_resistance(float voltage_v, const rtd_config_t *config) {
    if (config == NULL || config->gain <= 0.0f || config->excitation_current_a <= 0.0f) {
        return 0.0f;
    }
    /* Вхідна напруга перед операційним підсилювачем */
    float v_in = voltage_v / config->gain;
    /* За законом Ома: R = V / I_ex */
    return v_in / config->excitation_current_a;
}

float rtd_apply_lead_compensation(float raw_resistance, float r_lead_ohms) {
    /* У 3-провідній схемі вимірювання опір ліній компенсується відніманням опору провідника */
    float compensated = raw_resistance - r_lead_ohms;
    return (compensated < 0.0f) ? 0.0f : compensated;
}

float rtd_apply_calibration(float compensated_resistance, const rtd_calib_t *calib) {
    if (calib == NULL) {
        return compensated_resistance;
    }
    /* Формула двоточкового калібрування: R_cal = (R_comp - offset) * gain_scale */
    float gain_scale = (calib->gain_scale > 0.0f) ? calib->gain_scale : 1.0f;
    return (compensated_resistance - calib->offset_ohms) * gain_scale;
}

rtd_status_t rtd_diagnose_resistance(float resistance_ohms, float r0_ohms) {
    if (r0_ohms <= 0.0f) {
        return RTD_STATUS_ERR_PARAM;
    }

    /* Масштабуємо межі опору відповідно до номіналу (Pt100 або Pt1000) */
    float scale = r0_ohms / RTD_PT100_R0;
    float min_res = RTD_PT100_MIN_RES * scale;
    float max_res = RTD_PT100_MAX_RES * scale;

    /* Порогові значення для виявлення обриву та короткого замикання */
    float open_circuit_thresh = max_res * 1.15f;
    float short_circuit_thresh = min_res * 0.5f;

    if (resistance_ohms > open_circuit_thresh) {
        return RTD_STATUS_ERR_OPEN_CIRCUIT;
    }
    if (resistance_ohms < short_circuit_thresh) {
        return RTD_STATUS_ERR_SHORT_CIRCUIT;
    }
    if (resistance_ohms < min_res || resistance_ohms > max_res) {
        return RTD_STATUS_ERR_OUT_OF_RANGE;
    }

    return RTD_STATUS_OK;
}

rtd_status_t rtd_resistance_to_temperature_cvd(float resistance_ohms, float r0_ohms, float *out_temp_c) {
    if (out_temp_c == NULL || r0_ohms <= 0.0f) {
        return RTD_STATUS_ERR_PARAM;
    }

    rtd_status_t diag_status = rtd_diagnose_resistance(resistance_ohms, r0_ohms);
    if (diag_status == RTD_STATUS_ERR_OPEN_CIRCUIT || diag_status == RTD_STATUS_ERR_SHORT_CIRCUIT) {
        *out_temp_c = (diag_status == RTD_STATUS_ERR_OPEN_CIRCUIT) ? RTD_MAX_TEMP_C : RTD_MIN_TEMP_C;
        return diag_status;
    }

    /* 1. Визначення температури для додатних температур (T >= 0 °C, R >= R0) */
    if (resistance_ohms >= r0_ohms) {
        /*
         * Рівняння Каллендара — Ван Дюзена для T >= 0 °C:
         * R(T) = R0 * (1 + A*T + B*T^2)
         * Квадратне рівняння: B*T^2 + A*T + (1 - R/R0) = 0
         * Дискримінант: D = A^2 - 4*B*(1 - R/R0)
         * Корінь: T = (-A + sqrt(D)) / (2*B)
         */
        float ratio = resistance_ohms / r0_ohms;
        float discriminant = (RTD_CVD_A * RTD_CVD_A) - 4.0f * RTD_CVD_B * (1.0f - ratio);

        if (discriminant < 0.0f) {
            *out_temp_c = RTD_MAX_TEMP_C;
            return RTD_STATUS_ERR_OUT_OF_RANGE;
        }

        float temp = (-RTD_CVD_A + sqrtf(discriminant)) / (2.0f * RTD_CVD_B);
        *out_temp_c = temp;
    } else {
        /*
         * 2. Для від'ємних температур (T < 0 °C, R < R0) використовується повне рівняння 4-го степеня:
         * R(T) = R0 * [1 + A*T + B*T^2 + C*(T - 100)*T^3]
         * Початкове наближення беруть із квадратного рішення для додатних температур,
         * після чого уточнено чисельним методом Ньютона — Рафсона.
         */
        float ratio = resistance_ohms / r0_ohms;
        float discriminant = (RTD_CVD_A * RTD_CVD_A) - 4.0f * RTD_CVD_B * (1.0f - ratio);
        float temp = (-RTD_CVD_A + sqrtf(discriminant)) / (2.0f * RTD_CVD_B);

        /* Ітерації Ньютона — Рафсона для підвищення точності в субнульовому діапазоні */
        for (int i = 0; i < 4; i++) {
            float t2 = temp * temp;
            float t3 = t2 * temp;
            float t4 = t3 * temp;

            /* Значення функції f(T) = R_calc(T) - R_measured */
            float f = r0_ohms * (1.0f + RTD_CVD_A * temp + RTD_CVD_B * t2 + RTD_CVD_C * (temp - 100.0f) * t3) - resistance_ohms;

            /* Похідна f'(T) = R0 * [A + 2*B*T + 4*C*T^3 - 300*C*T^2] */
            float df = r0_ohms * (RTD_CVD_A + 2.0f * RTD_CVD_B * temp + 4.0f * RTD_CVD_C * t3 - 300.0f * RTD_CVD_C * t2);

            if (fabsf(df) < 1e-9f) {
                break;
            }
            temp = temp - (f / df);
        }
        *out_temp_c = temp;
    }

    if (*out_temp_c < RTD_MIN_TEMP_C || *out_temp_c > RTD_MAX_TEMP_C) {
        return RTD_STATUS_ERR_OUT_OF_RANGE;
    }

    return RTD_STATUS_OK;
}

rtd_status_t rtd_process_adc_sample(uint32_t raw_adc, 
                                    const rtd_config_t *config, 
                                    const rtd_calib_t *calib, 
                                    float *out_resistance_ohms, 
                                    float *out_temp_c) {
    if (config == NULL || out_resistance_ohms == NULL || out_temp_c == NULL) {
        return RTD_STATUS_ERR_PARAM;
    }

    /* 1. Конверсія коду АЦП у напругу */
    float voltage = rtd_adc_to_voltage(raw_adc, config);

    /* 2. Перетворення напруги в опір аналогового тракту */
    float raw_resistance = rtd_voltage_to_raw_resistance(voltage, config);

    /* 3. Компенсація опору провідників 3-провідної лінії */
    float comp_resistance = rtd_apply_lead_compensation(raw_resistance, config->r_lead_ohms);

    /* 4. Застосування калібрувальних коефіцієнтів */
    float cal_resistance = rtd_apply_calibration(comp_resistance, calib);
    *out_resistance_ohms = cal_resistance;

    /* 5. Обчислення температури за формулою CVD та діагностика */
    return rtd_resistance_to_temperature_cvd(cal_resistance, config->r0_ohms, out_temp_c);
}
