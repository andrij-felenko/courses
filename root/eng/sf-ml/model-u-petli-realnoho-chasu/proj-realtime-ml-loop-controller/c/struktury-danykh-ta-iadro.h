#ifndef REALTIME_ML_CONTROLLER_H
#define REALTIME_ML_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <string.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RT_ML_MAX_DIM 4
#define CACHE_LINE_SIZE 64

/* Структура кадру передбачення нейромережі */
typedef struct {
    float values[RT_ML_MAX_DIM];
    uint64_t timestamp_us;
    uint32_t frame_id;
    float confidence;
} rt_ml_frame_t;

/* Структура потрійного буфера з вирівнюванням для усунення False Sharing */
typedef struct {
    alignas(CACHE_LINE_SIZE) rt_ml_frame_t slots[3];
    alignas(CACHE_LINE_SIZE) atomic_uint_fast8_t clean_idx;
    uint8_t write_idx;
    uint8_t read_idx;
} rt_triple_buffer_t;

/* Стани автомата дедлайнів */
typedef enum {
    RT_ML_STATUS_FRESH = 0,        /* Отримано свіжі дані в межах дедлайну */
    RT_ML_STATUS_EXTRAPOLATED,    /* Затримка в межах норми, застосовано екстраполяцію */
    RT_ML_STATUS_FALLBACK_PID,    /* Глибоке запізнення, активний бекап-регулятор */
    RT_ML_STATUS_EMERGENCY_STOP   /* Фатальний таймаут NPU, аварійна зупинка */
} rt_ml_status_t;

/* Конфігурація монітора дедлайнів */
typedef struct {
    uint64_t deadline_limit_us;    /* Поріг свіжості кадру (наприклад, 40 000 мкс) */
    uint64_t max_extrap_us;        /* Максимальний час екстраполяції (наприклад, 90 000 мкс) */
    uint64_t fatal_timeout_us;     /* Час до аварійної зупинки (наприклад, 400 000 мкс) */
    float decay_lambda;            /* Коефіцієнт експоненційного згасання екстраполяції */
    float max_slew_rate;           /* Максимальна швидкість наростання сигналу (од/сек) */
} rt_watchdog_config_t;

/* Контролер узгодження та моніторингу */
typedef struct {
    rt_watchdog_config_t cfg;
    rt_ml_frame_t last_valid_frame;
    float last_derivatives[RT_ML_MAX_DIM];
    float last_applied_output[RT_ML_MAX_DIM];
    
    /* Статистика для профілювання */
    uint32_t total_frames_received;
    uint32_t deadline_miss_count;
    uint32_t fallback_trigger_count;
    uint64_t max_observed_latency_us;
} rt_ml_controller_t;

/* Конфігурація та стан детермінованого ПІД-контролера */
typedef struct {
    float kp;
    float ki;
    float kd;
    float ts_sec;
    float out_min;
    float out_max;
    
    float integral_accum;
    float prev_error;
} rt_fallback_pid_t;

/* Публічні функції інтерфейсу C99 */
void rt_triple_buffer_init(rt_triple_buffer_t *tb);
void rt_triple_buffer_write(rt_triple_buffer_t *tb, const rt_ml_frame_t *frame);
bool rt_triple_buffer_read(rt_triple_buffer_t *tb, rt_ml_frame_t *out_frame);

void rt_ml_controller_init(rt_ml_controller_t *ctrl, const rt_watchdog_config_t *cfg);
rt_ml_status_t rt_ml_controller_update(
    rt_ml_controller_t *ctrl,
    const rt_ml_frame_t *incoming_frame,
    bool is_fresh,
    uint64_t current_time_us,
    float out_correction[RT_ML_MAX_DIM]);

void rt_fallback_pid_init(rt_fallback_pid_t *pid, float kp, float ki, float kd, float ts, float min_val, float max_val);
float rt_fallback_pid_step(rt_fallback_pid_t *pid, float setpoint, float feedback, float external_active_u, bool is_fallback_active);

#ifdef __cplusplus
}
#endif

#endif /* REALTIME_ML_CONTROLLER_H */
