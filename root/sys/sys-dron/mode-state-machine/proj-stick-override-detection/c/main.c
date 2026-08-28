#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define RC_CHANNEL_ROLL        0
#define RC_CHANNEL_PITCH       1
#define RC_CHANNEL_YAW         2
#define RC_CHANNEL_THROTTLE    3
#define RC_MAX_CHANNELS        4

#define STICK_OVR_MASK_ROLL     (1u << RC_CHANNEL_ROLL)
#define STICK_OVR_MASK_PITCH    (1u << RC_CHANNEL_PITCH)
#define STICK_OVR_MASK_YAW      (1u << RC_CHANNEL_YAW)
#define STICK_OVR_MASK_THROTTLE (1u << RC_CHANNEL_THROTTLE)
#define STICK_OVR_MASK_ALL_RP   (STICK_OVR_MASK_ROLL | STICK_OVR_MASK_PITCH)
#define STICK_OVR_MASK_ALL      (STICK_OVR_MASK_ALL_RP | STICK_OVR_MASK_YAW | STICK_OVR_MASK_THROTTLE)

typedef enum {
    OVR_STATE_IDLE = 0,
    OVR_STATE_QUALIFYING,
    OVR_STATE_ACTIVE,
    OVR_STATE_RELEASE_HOLD
} StickOverrideState;

typedef enum {
    TARGET_MODE_STABILIZE = 0,
    TARGET_MODE_ALT_HOLD  = 1,
    TARGET_MODE_POS_HOLD  = 2,
    TARGET_MODE_ACRO      = 3
} FallbackFlightMode;

// Калібрувальні параметри апаратного каналу RC
typedef struct {
    uint16_t pwm_min;
    uint16_t pwm_trim;
    uint16_t pwm_max;
    float deadband_norm;      // Мертва зона (0.0 ... 0.2)
    float threshold_norm;     // Поріг активації оверрайду (0.05 ... 0.5)
} RcChannelCalibration;

// Конфігурація модуля Stick Override
typedef struct {
    RcChannelCalibration channels[RC_MAX_CHANNELS];
    uint32_t channel_mask;          // Маска активних каналів детектування
    uint32_t activation_delay_ms;  // Час безперервного відхилення для спрацьовування
    uint32_t release_hold_ms;       // Час утримання блокування після скидання стіків
    float euclidean_threshold_rp;  // Поріг для комбінованої норми Roll+Pitch
    bool use_euclidean_norm;       // Прапорець використання комбінованої норми
} StickOverrideConfig;

// Нормалізовані сигнали керування (-1.0 ... +1.0)
typedef struct {
    float roll;
    float pitch;
    float yaw;
    float throttle;
    bool is_valid;
} NormalizedRcInput;

// Стан детектора перехоплення
typedef struct {
    StickOverrideState state;
    uint32_t state_entry_timestamp_ms;
    uint32_t last_update_timestamp_ms;
    float current_max_deflection;
    bool override_active;
    bool override_latched_event;
    FallbackFlightMode recommended_mode;
} StickOverrideDetector;

// Ініціалізація конфігурації детектора типовими безпечними значеннями
static inline void stick_override_init_config(StickOverrideConfig *cfg) {
    if (!cfg) return;

    for (int i = 0; i < RC_MAX_CHANNELS; ++i) {
        cfg->channels[i].pwm_min = 1000;
        cfg->channels[i].pwm_trim = 1500;
        cfg->channels[i].pwm_max = 2000;
        cfg->channels[i].deadband_norm = 0.05f;    // 5% мертва зона (+-25 мкс)
        cfg->channels[i].threshold_norm = 0.15f;  // 15% поріг оверрайду (+-75 мкс)
    }

    // Канал газу за замовчуванням має більший поріг для уникнення хибних зривів
    cfg->channels[RC_CHANNEL_THROTTLE].threshold_norm = 0.20f;
    cfg->channels[RC_CHANNEL_YAW].threshold_norm = 0.25f;

    cfg->channel_mask = STICK_OVR_MASK_ALL_RP | STICK_OVR_MASK_THROTTLE;
    cfg->activation_delay_ms = 100;    // 100 мс дебаунсинг
    cfg->release_hold_ms = 1000;       // 1000 мс утримання після відпускання
    cfg->euclidean_threshold_rp = 0.18f;
    cfg->use_euclidean_norm = true;
}

// Ініціалізація об'єкта детектора
static inline void stick_override_detector_init(StickOverrideDetector *det) {
    if (!det) return;
    det->state = OVR_STATE_IDLE;
    det->state_entry_timestamp_ms = 0;
    det->last_update_timestamp_ms = 0;
    det->current_max_deflection = 0.0f;
    det->override_active = false;
    det->override_latched_event = false;
    det->recommended_mode = TARGET_MODE_POS_HOLD;
}

// Функція обчислення симетричної нормалізації з неперервним зняттям мертвої зони
static float normalize_channel_with_deadband(uint16_t pwm_raw, const RcChannelCalibration *cal) {
    if (pwm_raw < cal->pwm_min) pwm_raw = cal->pwm_min;
    if (pwm_raw > cal->pwm_max) pwm_raw = cal->pwm_max;

    float raw_norm = 0.0f;
    if (pwm_raw >= cal->pwm_trim) {
        float span = (float)(cal->pwm_max - cal->pwm_trim);
        if (span > 1.0f) {
            raw_norm = (float)(pwm_raw - cal->pwm_trim) / span;
        }
    } else {
        float span = (float)(cal->pwm_trim - cal->pwm_min);
        if (span > 1.0f) {
            raw_norm = -(float)(cal->pwm_trim - pwm_raw) / span;
        }
    }

    // Безрозривне масштабування мертвої зони
    float abs_val = fabsf(raw_norm);
    float db = cal->deadband_norm;

    if (abs_val <= db) {
        return 0.0f;
    }

    float scaled = (abs_val - db) / (1.0f - db);
    if (scaled > 1.0f) scaled = 1.0f;

    return (raw_norm >= 0.0f) ? scaled : -scaled;
}

// Нормалізація всього пакета радіоканалів
static void process_rc_inputs(const uint16_t raw_pwm[RC_MAX_CHANNELS],
                              const StickOverrideConfig *cfg,
                              NormalizedRcInput *out_norm) {
    if (!raw_pwm || !cfg || !out_norm) return;

    out_norm->roll     = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_ROLL], &cfg->channels[RC_CHANNEL_ROLL]);
    out_norm->pitch    = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_PITCH], &cfg->channels[RC_CHANNEL_PITCH]);
    out_norm->yaw      = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_YAW], &cfg->channels[RC_CHANNEL_YAW]);
    out_norm->throttle = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_THROTTLE], &cfg->channels[RC_CHANNEL_THROTTLE]);
    out_norm->is_valid = true;
}

// Визначення цільового безпечного режиму на основі сенсорного здоров'я
static FallbackFlightMode resolve_fallback_mode(uint32_t sensor_flags) {
    #define SENSOR_EKF_HORIZ_POS (1u << 4)
    #define SENSOR_EKF_VERT_POS  (1u << 3)
    #define SENSOR_AHRS_ATTITUDE (1u << 1)

    if ((sensor_flags & SENSOR_EKF_HORIZ_POS) != 0) {
        return TARGET_MODE_POS_HOLD;
    }
    if ((sensor_flags & SENSOR_EKF_VERT_POS) != 0) {
        return TARGET_MODE_ALT_HOLD;
    }
    if ((sensor_flags & SENSOR_AHRS_ATTITUDE) != 0) {
        return TARGET_MODE_STABILIZE;
    }

    return TARGET_MODE_STABILIZE;
}

// Основний польотний цикл обробки детектора Stick Override
void stick_override_update(StickOverrideDetector *det,
                           const StickOverrideConfig *cfg,
                           const NormalizedRcInput *rc,
                           uint32_t sensor_flags,
                           uint32_t current_time_ms) {
    if (!det || !cfg || !rc || !rc->is_valid) {
        return;
    }

    det->last_update_timestamp_ms = current_time_ms;
    det->override_latched_event = false;

    // Розрахунок нормованих відхилень за каналами
    float defl_roll     = fabsf(rc->roll);
    float defl_pitch    = fabsf(rc->pitch);
    float defl_yaw      = fabsf(rc->yaw);
    float defl_throttle = fabsf(rc->throttle);

    bool threshold_exceeded = false;
    float max_deflection = 0.0f;

    // Поканальна перевірка з урахуванням маски
    if ((cfg->channel_mask & STICK_OVR_MASK_ROLL) && (defl_roll >= cfg->channels[RC_CHANNEL_ROLL].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_roll > max_deflection) max_deflection = defl_roll;
    }
    if ((cfg->channel_mask & STICK_OVR_MASK_PITCH) && (defl_pitch >= cfg->channels[RC_CHANNEL_PITCH].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_pitch > max_deflection) max_deflection = defl_pitch;
    }
    if ((cfg->channel_mask & STICK_OVR_MASK_YAW) && (defl_yaw >= cfg->channels[RC_CHANNEL_YAW].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_yaw > max_deflection) max_deflection = defl_yaw;
    }
    if ((cfg->channel_mask & STICK_OVR_MASK_THROTTLE) && (defl_throttle >= cfg->channels[RC_CHANNEL_THROTTLE].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_throttle > max_deflection) max_deflection = defl_throttle;
    }

    // Комбінована норма площини горизонту
    if (cfg->use_euclidean_norm && ((cfg->channel_mask & STICK_OVR_MASK_ALL_RP) == STICK_OVR_MASK_ALL_RP)) {
        float euclidean_rp = sqrtf(rc->roll * rc->roll + rc->pitch * rc->pitch);
        if (euclidean_rp >= cfg->euclidean_threshold_rp) {
            threshold_exceeded = true;
            if (euclidean_rp > max_deflection) max_deflection = euclidean_rp;
        }
    }

    det->current_max_deflection = max_deflection;

    // Кінцевий автомат дебаунсингу та утримання
    switch (det->state) {
        case OVR_STATE_IDLE:
            det->override_active = false;
            if (threshold_exceeded) {
                det->state = OVR_STATE_QUALIFYING;
                det->state_entry_timestamp_ms = current_time_ms;
            }
            break;

        case OVR_STATE_QUALIFYING:
            det->override_active = false;
            if (!threshold_exceeded) {
                // Відхилення було короткочасним шумом
                det->state = OVR_STATE_IDLE;
            } else {
                uint32_t elapsed = current_time_ms - det->state_entry_timestamp_ms;
                if (elapsed >= cfg->activation_delay_ms) {
                    det->state = OVR_STATE_ACTIVE;
                    det->state_entry_timestamp_ms = current_time_ms;
                    det->override_active = true;
                    det->override_latched_event = true;
                    det->recommended_mode = resolve_fallback_mode(sensor_flags);
                }
            }
            break;

        case OVR_STATE_ACTIVE:
            det->override_active = true;
            det->recommended_mode = resolve_fallback_mode(sensor_flags);
            if (!threshold_exceeded) {
                // Стіки повернулися в нейтраль, перехід у фазу фіксації
                det->state = OVR_STATE_RELEASE_HOLD;
                det->state_entry_timestamp_ms = current_time_ms;
            }
            break;

        case OVR_STATE_RELEASE_HOLD:
            // Під час утримання оверрайд вважається формально завершеним,
            // але повторний вхід у стан IDLE заблоковано на час затримки
            det->override_active = false;
            if (threshold_exceeded) {
                // Пілот знову смикнув стік під час відліку паузи
                det->state = OVR_STATE_ACTIVE;
                det->state_entry_timestamp_ms = current_time_ms;
                det->override_active = true;
            } else {
                uint32_t elapsed = current_time_ms - det->state_entry_timestamp_ms;
                if (elapsed >= cfg->release_hold_ms) {
                    det->state = OVR_STATE_IDLE;
                }
            }
            break;

        default:
            det->state = OVR_STATE_IDLE;
            det->override_active = false;
            break;
    }
}
