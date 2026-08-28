#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_TEST_STEPS 11
#define SAMPLES_PER_STEP 64

typedef enum {
    BENCH_STATE_IDLE = 0,
    BENCH_STATE_PRE_TARE,
    BENCH_STATE_RAMP,
    BENCH_STATE_SETTLE,
    BENCH_STATE_ACQUIRE,
    BENCH_STATE_POST_TARE,
    BENCH_STATE_COOLDOWN,
    BENCH_STATE_EMERGENCY
} bench_state_t;

typedef enum {
    ABORT_NONE = 0,
    ABORT_OVERCURRENT,
    ABORT_MOTOR_STALL,
    ABORT_REVERSE_THRUST,
    ABORT_OVERHEAT,
    ABORT_COMM_TIMEOUT
} abort_reason_t;

typedef struct {
    float max_current_a;
    float max_temp_c;
    float step_settle_time_s;
    float step_acquire_time_s;
    uint8_t step_increment_pct;
} bench_limits_t;

typedef struct {
    uint32_t timestamp_ms;
    float throttle_pct;
    float thrust_grams;
    float voltage_v;
    float current_a;
    float power_w;
    float rpm;
    float eff_grams_per_watt;
    float temp_c;
} bench_record_t;

typedef struct {
    bench_state_t state;
    abort_reason_t abort_reason;
    bench_limits_t limits;
    
    uint8_t current_step_idx;
    uint8_t total_steps;
    float target_throttle;
    float current_throttle;
    
    uint32_t state_entry_time_ms;
    float pre_tare_offset_g;
    float post_tare_offset_g;
    float start_temp_c;
    float end_temp_c;
    
    bench_record_t step_results[MAX_TEST_STEPS];
    
    // Накопичувальні буфери поточної сходинки
    float acc_thrust;
    float acc_voltage;
    float acc_current;
    float acc_rpm;
    float acc_temp;
    uint16_t sample_count;
} thrust_rig_controller_t;

// Зовнішні апаратні функції (HAL)
extern void hal_esc_write_throttle(float throttle_pct);
extern bool hal_hx711_read_grams(float *out_grams);
extern bool hal_ina226_read_power(float *out_v, float *out_a);
extern bool hal_tach_read_rpm(float *out_rpm);
extern bool hal_temp_read_c(float *out_temp_c);
extern uint32_t hal_get_time_ms(void);
extern void hal_uart_stream_record(const bench_record_t *rec);

void rig_init(thrust_rig_controller_t *rig, const bench_limits_t *limits) {
    memset(rig, 0, sizeof(*rig));
    rig->state = BENCH_STATE_IDLE;
    rig->abort_reason = ABORT_NONE;
    rig->limits = *limits;
    rig->total_steps = (100 / limits->step_increment_pct) + 1;
    if (rig->total_steps > MAX_TEST_STEPS) {
        rig->total_steps = MAX_TEST_STEPS;
    }
}

static void rig_emergency_abort(thrust_rig_controller_t *rig, abort_reason_t reason) {
    hal_esc_write_throttle(0.0f);
    rig->current_throttle = 0.0f;
    rig->state = BENCH_STATE_EMERGENCY;
    rig->abort_reason = reason;
}

static bool rig_check_safety(thrust_rig_controller_t *rig, float v, float i, float thrust, float rpm, float temp) {
    if (i > rig->limits.max_current_a) {
        rig_emergency_abort(rig, ABORT_OVERCURRENT);
        return false;
    }
    if (temp > rig->limits.max_temp_c) {
        rig_emergency_abort(rig, ABORT_OVERHEAT);
        return false;
    }
    if (rig->current_throttle > 25.0f && rpm < 300.0f && i > 2.5f) {
        rig_emergency_abort(rig, ABORT_MOTOR_STALL);
        return false;
    }
    if (rig->current_throttle > 30.0f && thrust < -25.0f) {
        rig_emergency_abort(rig, ABORT_REVERSE_THRUST);
        return false;
    }
    return true;
}

void rig_start_sequence(thrust_rig_controller_t *rig) {
    if (rig->state != BENCH_STATE_IDLE) return;
    rig->current_step_idx = 0;
    rig->current_throttle = 0.0f;
    rig->target_throttle = 0.0f;
    rig->acc_thrust = 0.0f;
    rig->sample_count = 0;
    rig->state_entry_time_ms = hal_get_time_ms();
    rig->state = BENCH_STATE_PRE_TARE;
    hal_esc_write_throttle(0.0f);
}

void rig_update(thrust_rig_controller_t *rig) {
    uint32_t now = hal_get_time_ms();
    uint32_t elapsed = now - rig->state_entry_time_ms;
    
    float raw_thrust = 0.0f, v = 0.0f, i = 0.0f, rpm = 0.0f, temp_c = 25.0f;
    hal_hx711_read_grams(&raw_thrust);
    hal_ina226_read_power(&v, &i);
    hal_tach_read_rpm(&rpm);
    hal_temp_read_c(&temp_c);
    
    if (rig->state != BENCH_STATE_IDLE && rig->state != BENCH_STATE_EMERGENCY) {
        if (!rig_check_safety(rig, v, i, raw_thrust - rig->pre_tare_offset_g, rpm, temp_c)) {
            return;
        }
    }
    
    switch (rig->state) {
        case BENCH_STATE_IDLE:
        case BENCH_STATE_EMERGENCY:
            hal_esc_write_throttle(0.0f);
            break;
            
        case BENCH_STATE_PRE_TARE:
            rig->acc_thrust += raw_thrust;
            rig->acc_temp += temp_c;
            rig->sample_count++;
            if (elapsed >= 1500) {
                rig->pre_tare_offset_g = rig->acc_thrust / (float)rig->sample_count;
                rig->start_temp_c = rig->acc_temp / (float)rig->sample_count;
                rig->current_step_idx = 0;
                rig->target_throttle = 0.0f;
                rig->state = BENCH_STATE_RAMP;
                rig->state_entry_time_ms = now;
            }
            break;
            
        case BENCH_STATE_RAMP:
            // Плавне доведення газу до цілі
            if (rig->current_throttle < rig->target_throttle) {
                rig->current_throttle += 0.5f; // +0.5% на кожен такт оновлення
                if (rig->current_throttle > rig->target_throttle) {
                    rig->current_throttle = rig->target_throttle;
                }
            }
            hal_esc_write_throttle(rig->current_throttle);
            if (rig->current_throttle >= rig->target_throttle) {
                rig->state = BENCH_STATE_SETTLE;
                rig->state_entry_time_ms = now;
            }
            break;
            
        case BENCH_STATE_SETTLE:
            if (elapsed >= (uint32_t)(rig->limits.step_settle_time_s * 1000.0f)) {
                rig->state = BENCH_STATE_ACQUIRE;
                rig->state_entry_time_ms = now;
                rig->acc_thrust = 0.0f;
                rig->acc_voltage = 0.0f;
                rig->acc_current = 0.0f;
                rig->acc_rpm = 0.0f;
                rig->acc_temp = 0.0f;
                rig->sample_count = 0;
            }
            break;
            
        case BENCH_STATE_ACQUIRE:
            rig->acc_thrust += (raw_thrust - rig->pre_tare_offset_g);
            rig->acc_voltage += v;
            rig->acc_current += i;
            rig->acc_rpm += rpm;
            rig->acc_temp += temp_c;
            rig->sample_count++;
            
            if (elapsed >= (uint32_t)(rig->limits.step_acquire_time_s * 1000.0f) && rig->sample_count > 0) {
                bench_record_t *rec = &rig->step_results[rig->current_step_idx];
                rec->timestamp_ms = now;
                rec->throttle_pct = rig->current_throttle;
                rec->thrust_grams = rig->acc_thrust / (float)rig->sample_count;
                rec->voltage_v = rig->acc_voltage / (float)rig->sample_count;
                rec->current_a = rig->acc_current / (float)rig->sample_count;
                rec->power_w = rec->voltage_v * rec->current_a;
                rec->rpm = rig->acc_rpm / (float)rig->sample_count;
                rec->temp_c = rig->acc_temp / (float)rig->sample_count;
                rec->eff_grams_per_watt = (rec->power_w > 0.05f) ? (rec->thrust_grams / rec->power_w) : 0.0f;
                
                hal_uart_stream_record(rec);
                
                rig->current_step_idx++;
                if (rig->current_step_idx < rig->total_steps) {
                    rig->target_throttle = (float)rig->current_step_idx * (float)rig->limits.step_increment_pct;
                    if (rig->target_throttle > 100.0f) rig->target_throttle = 100.0f;
                    rig->state = BENCH_STATE_RAMP;
                    rig->state_entry_time_ms = now;
                } else {
                    // Завершили всі сходинки — скидаємо газ і таруємося на гарячу
                    hal_esc_write_throttle(0.0f);
                    rig->current_throttle = 0.0f;
                    rig->acc_thrust = 0.0f;
                    rig->acc_temp = 0.0f;
                    rig->sample_count = 0;
                    rig->state = BENCH_STATE_POST_TARE;
                    rig->state_entry_time_ms = now;
                }
            }
            break;
            
        case BENCH_STATE_POST_TARE:
            rig->acc_thrust += raw_thrust;
            rig->acc_temp += temp_c;
            rig->sample_count++;
            if (elapsed >= 1500 && rig->sample_count > 0) {
                rig->post_tare_offset_g = rig->acc_thrust / (float)rig->sample_count;
                rig->end_temp_c = rig->acc_temp / (float)rig->sample_count;
                rig->state = BENCH_STATE_COOLDOWN;
                rig->state_entry_time_ms = now;
            }
            break;
            
        case BENCH_STATE_COOLDOWN:
            if (elapsed >= 10000) {
                rig->state = BENCH_STATE_IDLE;
            }
            break;
    }
}
