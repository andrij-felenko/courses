#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Структура конфігурації часових параметрів інтегрування */
typedef struct {
    float t_coh_sec;          /* Когерентне вікно, с */
    int   m_noncoh_blocks;    /* Кількість некогерентних блоків */
    float t_total_meas_sec;   /* Повний час вимірювання T_meas, с */
    float expected_sigma_m;   /* Очікувана похибка дальності за CRLB, м */
} timing_config_t;

/* Обчислення оптимального часу вимірювання */
timing_config_t calculate_optimal_measurement_time(
    float cn0_db_hz,          /* Співвідношення сигнал/шум C/N0 */
    float bandwidth_hz,       /* Смуга коду, Гц */
    float vehicle_accel_mps2, /* Поточне прискорення БПЛА, м/с^2 */
    float channel_tc_sec)     /* Час когерентності радіоканалу, с */
{
    timing_config_t cfg;
    const float C_LIGHT = 299792458.0f;
    
    /* 1. Обмеження когерентного вікна часом когерентності та бітовою межею */
    float max_allowed_t_coh = 0.020f; /* 20 мс — тривалість біта GPS */
    if (channel_tc_sec < max_allowed_t_coh) {
        max_allowed_t_coh = channel_tc_sec;
    }
    
    /* При високій динаміці (a > 20 м/с^2) скорочуємо когерентний час до 1-5 мс */
    if (vehicle_accel_mps2 > 20.0f) {
        cfg.t_coh_sec = 0.001f; /* 1 мс */
    } else if (vehicle_accel_mps2 > 5.0f) {
        cfg.t_coh_sec = 0.005f; /* 5 мс */
    } else {
        cfg.t_coh_sec = (max_allowed_t_coh > 0.010f) ? 0.010f : max_allowed_t_coh;
    }
    
    /* 2. Вибір числа некогерентних блоків M за рівнем C/N0 */
    if (cn0_db_hz < 30.0f) {
        /* Слабкий сигнал (приміщення, завади): збільшуємо M для чутливості */
        cfg.m_noncoh_blocks = (vehicle_accel_mps2 > 10.0f) ? 10 : 50;
    } else if (cn0_db_hz < 40.0f) {
        cfg.m_noncoh_blocks = (vehicle_accel_mps2 > 10.0f) ? 5 : 20;
    } else {
        /* Сильний сигнал: мінімальне M для максимальної швидкості оновлення */
        cfg.m_noncoh_blocks = (vehicle_accel_mps2 > 10.0f) ? 1 : 5;
    }
    
    cfg.t_total_meas_sec = cfg.t_coh_sec * (float)cfg.m_noncoh_blocks;
    
    /* 3. Теоретична похибка дальності за межею Крамера-Рао */
    float snr_linear = powf(10.0f, (cn0_db_hz - 10.0f * log10f(bandwidth_hz)) / 10.0f);
    float denom = 2.0f * 3.14159265f * bandwidth_hz * 
                  sqrtf(2.0f * snr_linear * bandwidth_hz * cfg.t_total_meas_sec);
    float sigma_tau = sqrtf(3.0f) / denom;
    cfg.expected_sigma_m = sigma_tau * C_LIGHT;
    
    return cfg;
}
