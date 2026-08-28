/* ============================================================================
 * takeoff_fsm.h / takeoff_fsm.c
 * Автомат процедури зльоту безпілотного апарата (C99)
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_MOTORS 8
#define GRAVITY_MSS 9.80665f

typedef enum {
    TAKEOFF_STATE_DISARMED = 0,
    TAKEOFF_STATE_SPOOLUP,
    TAKEOFF_STATE_GROUND_RAMP,
    TAKEOFF_STATE_RAPID_CLIMB,
    TAKEOFF_STATE_LEVEL_OFF,
    TAKEOFF_STATE_COMPLETE,
    TAKEOFF_STATE_ABORT
} takeoff_state_t;

typedef enum {
    ABORT_NONE = 0,
    ABORT_TILT_EXCEEDED,        /* Кут нахилу на землі перевищив 15 градусів */
    ABORT_MOTOR_CURRENT_IMBALANCE,/* Струм одного з моторів суттєво відхилився */
    ABORT_MOTOR_RPM_LOSS,       /* Втрата обертів одного з роторів */
    ABORT_SPOOLUP_TIMEOUT,      /* Розкрутка перевищила ліміт часу */
    ABORT_TAKEOFF_STUCK,        /* Тяга висока, але відриву немає за 1.5 с */
    ABORT_EKF_DIVERGENCE,       /* Розходження навігаційного фільтра */
    ABORT_MANUAL_COMMAND        /* Команда оператора або скидання з пульта */
} takeoff_abort_reason_t;

/* Вхідні телеметричні дані від підсистем літака */
typedef struct {
    float roll_deg;             /* Поточний крен [град] */
    float pitch_deg;            /* Поточний тангаж [град] */
    float yaw_deg;              /* Поточний курс [град] */
    float alt_rel_m;            /* Відносна висота над точкою старту [м] */
    float vz_ms;                /* Вертикальна швидкість (догори > 0) [м/с] */
    float accel_z_mss;          /* Вертикальне прискорення [м/с^2] */
    
    /* Дані GNSS та EKF */
    bool ekf_healthy;           /* Працездатність EKF */
    float ekf_hpos_variance;    /* Горизонтальна дисперсія позиції EKF [м] */
    float ekf_vpos_variance;    /* Вертикальна дисперсія позиції EKF [м] */
    uint8_t gnss_sats;          /* Кількість видимих супутників */
    float gnss_hdop;            /* Geometric dilution of precision */
    
    /* Батарея */
    float battery_voltage;      /* Загальна напруга АКБ [В] */
    float cell_min_voltage;     /* Мінімальна напруга комірки [В] */
    
    /* ESC-телеметрія моторів (DShot / RPM) */
    uint8_t num_motors;
    float motor_currents[MAX_MOTORS]; /* Струм кожного мотора [А] */
    float motor_rpm[MAX_MOTORS];      /* Оберти кожного мотора [об/хв] */
} takeoff_telemetry_t;

/* Налаштування автомата зльоту */
typedef struct {
    float target_alt_m;         /* Цільова висота зльоту (за замовчуванням 5.0 м) */
    float ground_clear_alt_m;   /* Висота виходу з екрана землі (1.2 м) */
    float climb_rate_ms;        /* Швидкість пробиття екрана (2.0 м/с) */
    float hover_throttle;       /* Оцінка газу висіння (0.45 .. 0.55) */
    float idle_throttle;        /* Газ холостого ходу (0.08) */
    float max_tilt_on_ground;   /* Поріг нахилу до відриву (15.0 град) */
    float max_current_imbalance;/* Макс. допустимий перекіс струму [А] (3.5 А) */
    float spoolup_time_s;       /* Тривалість розкрутки (1.0 с) */
    float liftoff_detect_vz_ms; /* Поріг детектування відриву за Vz (0.25 м/с) */
} takeoff_config_t;

/* Керівні команди, що видає автомат у контури стабілізації */
typedef struct {
    float throttle_cmd;         /* Нормалізований сигнал газу [0.0 .. 1.0] */
    float vz_setpoint_ms;       /* Уставка вертикальної швидкості [м/с] */
    float alt_setpoint_m;       /* Уставка висоти [м] */
    bool freeze_integrators;    /* Прапорець заморожування I-складових PID */
    bool arm_command;           /* Команда на зведення моторів */
    bool home_point_latch_req;  /* Вимога зафіксувати Home Point */
} takeoff_control_output_t;

/* Контекст автомата */
typedef struct {
    takeoff_state_t state;
    takeoff_abort_reason_t abort_reason;
    takeoff_config_t config;
    float state_timer_s;
    bool liftoff_confirmed;
    bool home_latched;
} takeoff_fsm_t;

/* Ініціалізація модуля */
void takeoff_fsm_init(takeoff_fsm_t *fsm, const takeoff_config_t *cfg)
{
    if (!fsm) return;
    if (cfg) {
        fsm->config = *cfg;
    } else {
        /* Значення за замовчуванням */
        fsm->config.target_alt_m = 5.0f;
        fsm->config.ground_clear_alt_m = 1.2f;
        fsm->config.climb_rate_ms = 2.0f;
        fsm->config.hover_throttle = 0.50f;
        fsm->config.idle_throttle = 0.08f;
        fsm->config.max_tilt_on_ground = 15.0f;
        fsm->config.max_current_imbalance = 3.5f;
        fsm->config.spoolup_time_s = 1.0f;
        fsm->config.liftoff_detect_vz_ms = 0.25f;
    }
    fsm->state = TAKEOFF_STATE_DISARMED;
    fsm->abort_reason = ABORT_NONE;
    fsm->state_timer_s = 0.0f;
    fsm->liftoff_confirmed = false;
    fsm->home_latched = false;
}

/* Перевірка передпольотних умов (Pre-Arm Checks) */
bool takeoff_check_prearm(const takeoff_telemetry_t *telem)
{
    if (!telem) return false;
    
    /* 1. Стан навігаційного фільтра EKF */
    if (!telem->ekf_healthy) return false;
    if (telem->ekf_hpos_variance > 1.2f || telem->ekf_vpos_variance > 2.0f) return false;
    
    /* 2. Якість фіксу GNSS */
    if (telem->gnss_sats < 8 || telem->gnss_hdop > 1.4f) return false;
    
    /* 3. Горизонтальне положення на землі */
    if (fabsf(telem->roll_deg) > 10.0f || fabsf(telem->pitch_deg) > 10.0f) return false;
    
    /* 4. Напруга АКБ */
    if (telem->cell_min_voltage < 3.75f) return false;
    
    return true;
}

/* Перевірка симетрії струмів моторів під час розкрутки */
static bool check_motor_current_symmetry(const takeoff_telemetry_t *telem, float max_diff)
{
    if (telem->num_motors < 2) return true;
    
    float sum = 0.0f;
    for (uint8_t i = 0; i < telem->num_motors; ++i) {
        sum += telem->motor_currents[i];
    }
    float avg = sum / (float)telem->num_motors;
    
    for (uint8_t i = 0; i < telem->num_motors; ++i) {
        if (fabsf(telem->motor_currents[i] - avg) > max_diff) {
            return false; /* Виявлено асиметрію: заклинювання або дефект гвинта */
        }
    }
    return true;
}

/* Головний такт оновлення автомата зльоту */
void takeoff_fsm_update(takeoff_fsm_t *fsm,
                        const takeoff_telemetry_t *telem,
                        float dt,
                        takeoff_control_output_t *out)
{
    if (!fsm || !telem || !out) return;
    
    fsm->state_timer_s += dt;
    
    /* За замовчуванням безпечні виходи */
    out->throttle_cmd = 0.0f;
    out->vz_setpoint_ms = 0.0f;
    out->alt_setpoint_m = 0.0f;
    out->freeze_integrators = true;
    out->arm_command = false;
    out->home_point_latch_req = false;
    
    /* Загальний захист: перевищення кута нахилу до повного набору висоти */
    float tilt = sqrtf(telem->roll_deg * telem->roll_deg + telem->pitch_deg * telem->pitch_deg);
    if (fsm->state >= TAKEOFF_STATE_SPOOLUP && fsm->state <= TAKEOFF_STATE_GROUND_RAMP) {
        if (tilt > fsm->config.max_tilt_on_ground) {
            fsm->state = TAKEOFF_STATE_ABORT;
            fsm->abort_reason = ABORT_TILT_EXCEEDED;
        }
    }
    
    switch (fsm->state) {
    case TAKEOFF_STATE_DISARMED:
        out->arm_command = false;
        out->throttle_cmd = 0.0f;
        out->freeze_integrators = true;
        break;
        
    case TAKEOFF_STATE_SPOOLUP:
        out->arm_command = true;
        out->freeze_integrators = true;
        
        /* Плавна рампа газу холостого ходу */
        {
            float progress = fsm->state_timer_s / fsm->config.spoolup_time_s;
            if (progress > 1.0f) progress = 1.0f;
            out->throttle_cmd = fsm->config.idle_throttle * progress;
        }
        
        /* Перевірка симетрії наприкінці розкрутки */
        if (fsm->state_timer_s >= fsm->config.spoolup_time_s) {
            if (!check_motor_current_symmetry(telem, fsm->config.max_current_imbalance)) {
                fsm->state = TAKEOFF_STATE_ABORT;
                fsm->abort_reason = ABORT_MOTOR_CURRENT_IMBALANCE;
            } else {
                /* Перехід до набору тяги відриву */
                fsm->state = TAKEOFF_STATE_GROUND_RAMP;
                fsm->state_timer_s = 0.0f;
            }
        }
        break;
        
    case TAKEOFF_STATE_GROUND_RAMP:
        out->arm_command = true;
        out->freeze_integrators = true;
        
        /* Форсована тяга відриву: 1.25 від тяги висіння */
        {
            float target_takeoff_thr = fsm->config.hover_throttle * 1.25f;
            float ramp = fsm->state_timer_s / 0.5f; /* 0.5 с на досягнення */
            if (ramp > 1.0f) ramp = 1.0f;
            out->throttle_cmd = fsm->config.idle_throttle + 
                               (target_takeoff_thr - fsm->config.idle_throttle) * ramp;
        }
        
        /* Детектування відриву */
        if (telem->vz_ms > fsm->config.liftoff_detect_vz_ms || telem->alt_rel_m > 0.15f) {
            fsm->liftoff_confirmed = true;
            if (!fsm->home_latched) {
                out->home_point_latch_req = true;
                fsm->home_latched = true;
            }
            fsm->state = TAKEOFF_STATE_RAPID_CLIMB;
            fsm->state_timer_s = 0.0f;
        } else if (fsm->state_timer_s > 1.5f) {
            /* Тяга піднята, але вертикального руху немає — апарат застряг */
            fsm->state = TAKEOFF_STATE_ABORT;
            fsm->abort_reason = ABORT_TAKEOFF_STUCK;
        }
        break;
        
    case TAKEOFF_STATE_RAPID_CLIMB:
        out->arm_command = true;
        out->freeze_integrators = false; /* Розморожуємо інтегратори після відриву */
        out->vz_setpoint_ms = fsm->config.climb_rate_ms;
        out->throttle_cmd = fsm->config.hover_throttle * 1.20f;
        
        /* Перевірка виходу із зони екрана */
        if (telem->alt_rel_m >= fsm->config.ground_clear_alt_m) {
            fsm->state = TAKEOFF_STATE_LEVEL_OFF;
            fsm->state_timer_s = 0.0f;
        }
        break;
        
    case TAKEOFF_STATE_LEVEL_OFF:
        out->arm_command = true;
        out->freeze_integrators = false;
        out->alt_setpoint_m = fsm->config.target_alt_m;
        
        /* Пропорційне гасіння вертикальної швидкості при наближенні до цілі */
        {
            float remaining = fsm->config.target_alt_m - telem->alt_rel_m;
            if (remaining < 0.8f) {
                out->vz_setpoint_ms = fsm->config.climb_rate_ms * (remaining / 0.8f);
                if (out->vz_setpoint_ms < 0.2f) out->vz_setpoint_ms = 0.2f;
            } else {
                out->vz_setpoint_ms = fsm->config.climb_rate_ms;
            }
        }
        
        /* Завершення зльоту при досягненні 95% висоти */
        if (telem->alt_rel_m >= (fsm->config.target_alt_m * 0.95f) && fabsf(telem->vz_ms) < 0.3f) {
            fsm->state = TAKEOFF_STATE_COMPLETE;
            fsm->state_timer_s = 0.0f;
        }
        break;
        
    case TAKEOFF_STATE_COMPLETE:
        out->arm_command = true;
        out->freeze_integrators = false;
        out->alt_setpoint_m = fsm->config.target_alt_m;
        out->vz_setpoint_ms = 0.0f;
        out->throttle_cmd = fsm->config.hover_throttle;
        break;
        
    case TAKEOFF_STATE_ABORT:
    default:
        out->arm_command = false; /* Негайний Disarm */
        out->throttle_cmd = 0.0f;
        out->vz_setpoint_ms = 0.0f;
        out->freeze_integrators = true;
        break;
    }
}

/* Запуск процедури зльоту за командою оператора */
bool takeoff_fsm_start(takeoff_fsm_t *fsm, const takeoff_telemetry_t *telem)
{
    if (!fsm || !telem) return false;
    if (fsm->state != TAKEOFF_STATE_DISARMED) return false;
    
    if (!takeoff_check_prearm(telem)) {
        return false; /* Передпольотні перевірки не пройшли */
    }
    
    fsm->state = TAKEOFF_STATE_SPOOLUP;
    fsm->abort_reason = ABORT_NONE;
    fsm->state_timer_s = 0.0f;
    fsm->liftoff_confirmed = false;
    fsm->home_latched = false;
    return true;
}
