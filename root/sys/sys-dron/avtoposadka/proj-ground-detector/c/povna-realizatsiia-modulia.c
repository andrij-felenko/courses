#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define ACCEL_BUFFER_SIZE 32

typedef enum {
    GROUND_STATE_IN_AIR = 0,
    GROUND_STATE_CONTACT_MAYBE,
    GROUND_STATE_CONTACT_CONFIRMED,
    GROUND_STATE_LANDED,
    GROUND_STATE_DISARMED
} ground_module_state_t;

typedef struct {
    float max_vz_abs;             // Гранична вертикальна швидкість контакту (м/с, 0.15)
    float max_gyro_abs;           // Гранична кутова швидкість (рад/с, 0.20)
    float hover_thr_ratio;        // Максимальний поріг газу від висіння (0.30)
    float conf_threshold_land;    // Поріг довіри для фіксації посадки (0.85)
    float conf_threshold_drop;    // Поріг скидання в політ при відриві (0.20)
    float time_rise_sec;          // Постійна часу наростання довіри (с, 0.50)
    float time_decay_sec;         // Постійна часу витоку довіри (с, 0.25)
    float disarm_ramp_time_sec;   // Час лінійного зняття тяги (с, 0.40)
} ground_detector_params_t;

typedef struct {
    ground_module_state_t state;
    ground_detector_params_t params;
    
    float confidence;             // Поточне значення інтегратора довіри [0.0 .. 1.0]
    float throttle_output_scale;  // Множник вихідної тяги [0.0 .. 1.0]
    bool  freeze_i_terms;         // Сигнал на заморожування I-складових PID
    bool  disarm_requested;       // Сигнал апаратного розброєння
    
    // Кільцевий буфер акселерометра Z
    float accel_buf[ACCEL_BUFFER_SIZE];
    uint8_t accel_buf_idx;
    uint8_t accel_buf_count;
    
    float prev_accel_z;
    float prev_accel_z2;
    float landed_time_accum;
} ground_detector_module_t;

void ground_detector_module_init(ground_detector_module_t *mod,
                                 const ground_detector_params_t *params) {
    memset(mod, 0, sizeof(ground_detector_module_t));
    mod->state = GROUND_STATE_IN_AIR;
    mod->params = *params;
    mod->confidence = 0.0f;
    mod->throttle_output_scale = 1.0f;
    mod->freeze_i_terms = false;
    mod->disarm_requested = false;
}

static float calc_accel_variance(const ground_detector_module_t *mod) {
    if (mod->accel_buf_count < 4) {
        return 0.0f;
    }
    float sum = 0.0f;
    for (uint8_t i = 0; i < mod->accel_buf_count; i++) {
        sum += mod->accel_buf[i];
    }
    float mean = sum / (float)mod->accel_buf_count;
    float sq_diff_sum = 0.0f;
    for (uint8_t i = 0; i < mod->accel_buf_count; i++) {
        float diff = mod->accel_buf[i] - mean;
        sq_diff_sum += diff * diff;
    }
    return sq_diff_sum / (float)(mod->accel_buf_count - 1);
}

void ground_detector_module_update(ground_detector_module_t *mod,
                                   float vz_ekf,
                                   float gyro_norm_rad_s,
                                   float accel_z_m_s2,
                                   float current_throttle,
                                   float hover_throttle,
                                   float dt_sec) {
    if (dt_sec <= 0.0001f || dt_sec > 0.2f) {
        dt_sec = 0.02f; // Захист від аномального таймауту
    }

    // 1. Оновлення кільцевого буфера прискорень
    mod->accel_buf[mod->accel_buf_idx] = accel_z_m_s2;
    mod->accel_buf_idx = (mod->accel_buf_idx + 1) % ACCEL_BUFFER_SIZE;
    if (mod->accel_buf_count < ACCEL_BUFFER_SIZE) {
        mod->accel_buf_count++;
    }

    // 2. Детектування високочастотного ударного імпульсу
    float jerk_indicator = fabsf(accel_z_m_s2 - 2.0f * mod->prev_accel_z + mod->prev_accel_z2);
    mod->prev_accel_z2 = mod->prev_accel_z;
    mod->prev_accel_z = accel_z_m_s2;

    float p_impact = (jerk_indicator > 6.0f) ? 1.0f : 0.0f;

    // 3. Оцінка часткових ймовірностей
    // Фактор тяги
    float max_allowed_thr = hover_throttle * mod->params.hover_thr_ratio;
    float p_thrust = 0.0f;
    if (current_throttle <= max_allowed_thr && max_allowed_thr > 0.0001f) {
        p_thrust = 1.0f - (current_throttle / max_allowed_thr) * 0.5f;
    }

    // Фактор вертикальної швидкості
    float abs_vz = fabsf(vz_ekf);
    float p_vel = 0.0f;
    if (abs_vz <= mod->params.max_vz_abs && mod->params.max_vz_abs > 0.0001f) {
        p_vel = 1.0f - (abs_vz / mod->params.max_vz_abs) * 0.4f;
    }

    // Фактор кутових швидкостей
    float p_gyro = (gyro_norm_rad_s <= mod->params.max_gyro_abs) ? 1.0f : 0.0f;

    // 4. Сумарна миттєва впевненість
    float s_raw = 0.40f * p_thrust + 0.35f * p_vel + 0.15f * p_gyro + 0.10f * p_impact;

    // 5. Динаміка витікаючого інтегратора
    if (s_raw >= 0.60f) {
        // Накопичення довіри
        float alpha_rise = dt_sec / mod->params.time_rise_sec;
        if (alpha_rise > 1.0f) alpha_rise = 1.0f;
        mod->confidence += (1.0f - mod->confidence) * alpha_rise;
    } else {
        // Витік довіри (експоненційний спад)
        float decay_factor = expf(-dt_sec / mod->params.time_decay_sec);
        mod->confidence *= decay_factor;
    }

    // Затискання в діапазоні [0.0 .. 1.0]
    if (mod->confidence > 1.0f) mod->confidence = 1.0f;
    if (mod->confidence < 0.0f) mod->confidence = 0.0f;

    // 6. Кінцевий автомат станів
    switch (mod->state) {
        case GROUND_STATE_IN_AIR: {
            mod->freeze_i_terms = false;
            mod->disarm_requested = false;
            mod->throttle_output_scale = 1.0f;
            mod->landed_time_accum = 0.0f;

            if (mod->confidence >= 0.35f) {
                mod->state = GROUND_STATE_CONTACT_MAYBE;
            }
            break;
        }

        case GROUND_STATE_CONTACT_MAYBE: {
            if (mod->confidence < mod->params.conf_threshold_drop) {
                mod->state = GROUND_STATE_IN_AIR;
                break;
            }

            if (mod->confidence >= 0.60f) {
                mod->state = GROUND_STATE_CONTACT_CONFIRMED;
                mod->freeze_i_terms = true; // Заморожуємо інтегратори
            }
            break;
        }

        case GROUND_STATE_CONTACT_CONFIRMED: {
            if (mod->confidence < mod->params.conf_threshold_drop) {
                mod->state = GROUND_STATE_IN_AIR;
                mod->freeze_i_terms = false;
                break;
            }

            if (mod->confidence >= mod->params.conf_threshold_land) {
                mod->state = GROUND_STATE_LANDED;
                mod->landed_time_accum = 0.0f;
            }
            break;
        }

        case GROUND_STATE_LANDED: {
            mod->freeze_i_terms = true;
            mod->landed_time_accum += dt_sec;

            if (mod->landed_time_accum < mod->params.disarm_ramp_time_sec) {
                // Лінійне скидання газу
                float ramp = 1.0f - (mod->landed_time_accum / mod->params.disarm_ramp_time_sec);
                mod->throttle_output_scale = (ramp > 0.0f) ? ramp : 0.0f;
            } else {
                mod->throttle_output_scale = 0.0f;
                mod->disarm_requested = true;
                mod->state = GROUND_STATE_DISARMED;
            }
            break;
        }

        case GROUND_STATE_DISARMED:
        default: {
            mod->throttle_output_scale = 0.0f;
            mod->disarm_requested = true;
            mod->freeze_i_terms = true;
            break;
        }
    }
}
