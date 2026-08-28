#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define POWER_SAMPLE_WINDOW_SIZE 200

typedef enum {
    CURRENT_SENSOR_TYPE_CT,
    CURRENT_SENSOR_TYPE_ROGOWSKI
} CurrentSensorType;

typedef struct {
    CurrentSensorType sensor_type;
    float sample_rate_hz;
    float vref_volts;
    uint32_t adc_max_counts;
    
    // Параметри для CT
    float ct_turns_ratio;       // N2 / N1 (наприклад 2000.0f)
    float ct_burden_resistor;   // Rb в Омах (наприклад 33.0f)
    float ct_phase_cal_deg;     // Фазова компенсація в градусах
    
    // Параметри для Rogowski
    float rogowski_mutual_inductance; // M в Генрі (наприклад 1.2e-7f)
    float rogowski_analog_gain;       // Підсилення аналогового каскаду
    float rogowski_leaky_lambda;      // Коефіцієнт витоку (наприклад 0.9992f)
} CurrentSensorConfig;

typedef struct {
    CurrentSensorConfig config;
    
    // Стан фільтра DC-Blocker
    float dc_filter_x_prev;
    float dc_filter_y_prev;
    float dc_filter_alpha;
    
    // Стан інтегратора Роговського
    float integrator_state;
    float integrator_x_prev;
    
    // Буфер та акумулятори потужності
    float sum_i_squared;
    float sum_v_squared;
    float sum_active_power;
    uint32_t sample_count;
    
    // Поточні розраховані результати
    float i_rms_amperes;
    float v_rms_volts;
    float active_power_watts;
    float apparent_power_va;
    float power_factor;
} CurrentSenseDriver;

void current_sensor_init(CurrentSenseDriver *drv, const CurrentSensorConfig *cfg) {
    drv->config = *cfg;
    drv->dc_filter_x_prev = 0.0f;
    drv->dc_filter_y_prev = 0.0f;
    
    // Розрахунок коефіцієнта ФВЧ для зрізу на 0.5 Гц
    float dt = 1.0f / cfg->sample_rate_hz;
    float rc = 1.0f / (2.0f * 3.1415926535f * 0.5f);
    drv->dc_filter_alpha = rc / (rc + dt);
    
    drv->integrator_state = 0.0f;
    drv->integrator_x_prev = 0.0f;
    
    drv->sum_i_squared = 0.0f;
    drv->sum_v_squared = 0.0f;
    drv->sum_active_power = 0.0f;
    drv->sample_count = 0;
    
    drv->i_rms_amperes = 0.0f;
    drv->v_rms_volts = 0.0f;
    drv->active_power_watts = 0.0f;
    drv->apparent_power_va = 0.0f;
    drv->power_factor = 1.0f;
}

// Обробка одного циклу вимірювання (струм + напруга мережі)
void current_sensor_process_sample(CurrentSenseDriver *drv, uint32_t raw_adc_i, float voltage_instant_v) {
    // 1. Переведення сирого відліку АЦП у вольти
    float v_adc = ((float)raw_adc_i / (float)drv->config.adc_max_counts) * drv->config.vref_volts;
    
    // 2. Блокування постійної складової (DC-Offset removal)
    float x_ac = v_adc - drv->dc_filter_x_prev + drv->dc_filter_alpha * drv->dc_filter_y_prev;
    drv->dc_filter_x_prev = v_adc;
    drv->dc_filter_y_prev = x_ac;
    
    float current_amperes = 0.0f;
    
    // 3. Обробка згідно з типом датчика
    if (drv->config.sensor_type == CURRENT_SENSOR_TYPE_CT) {
        // Для CT: струм через резистор навантаження Rb
        float i_secondary = x_ac / drv->config.ct_burden_resistor;
        current_amperes = i_secondary * drv->config.ct_turns_ratio;
    } else {
        // Для котушки Роговського: дискретне чисельне інтегрування Трапецій (Tustin)
        float dt = 1.0f / drv->config.sample_rate_hz;
        drv->integrator_state = (drv->config.rogowski_leaky_lambda * drv->integrator_state) + 
                                (0.5f * dt * (x_ac + drv->integrator_x_prev));
        drv->integrator_x_prev = x_ac;
        
        // Масштабування: i(t) = (1 / M) * v_int / G_analog
        float gain = drv->config.rogowski_mutual_inductance * drv->config.rogowski_analog_gain;
        if (gain > 1e-12f) {
            current_amperes = drv->integrator_state / gain;
        }
    }
    
    // 4. Накопичення середньоквадратичних та енергетичних сум
    drv->sum_i_squared += current_amperes * current_amperes;
    drv->sum_v_squared += voltage_instant_v * voltage_instant_v;
    drv->sum_active_power += voltage_instant_v * current_amperes;
    drv->sample_count++;
    
    // 5. Оновлення вихідних метрик при накопиченні вікна
    if (drv->sample_count >= POWER_SAMPLE_WINDOW_SIZE) {
        float inv_n = 1.0f / (float)drv->sample_count;
        
        drv->i_rms_amperes = sqrtf(drv->sum_i_squared * inv_n);
        drv->v_rms_volts = sqrtf(drv->sum_v_squared * inv_n);
        drv->active_power_watts = drv->sum_active_power * inv_n;
        drv->apparent_power_va = drv->v_rms_volts * drv->i_rms_amperes;
        
        if (drv->apparent_power_va > 1e-3f) {
            drv->power_factor = drv->active_power_watts / drv->apparent_power_va;
            if (drv->power_factor > 1.0f) drv->power_factor = 1.0f;
            if (drv->power_factor < -1.0f) drv->power_factor = -1.0f;
        } else {
            drv->power_factor = 1.0f;
        }
        
        // Скидання акумуляторів
        drv->sum_i_squared = 0.0f;
        drv->sum_v_squared = 0.0f;
        drv->sum_active_power = 0.0f;
        drv->sample_count = 0;
    }
}
