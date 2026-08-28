/* aec_q200_flex_monitor.h / .c — Драйвер випробування на вигин MLCC */
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define FLEX_CRIT_CAP_DROP_PERCENT   5.0f     /* Граничний спад ємності за AEC-Q200: 5% */
#define FLEX_CRIT_LEAKAGE_NA         50.0f    /* Граничний струм витоку: 50 нА */
#define FLEX_DEFAULT_SPAN_MM         90.0f    /* Відстань між опорами стенда L */
#define FLEX_PCB_THICKNESS_MM        1.6f     /* Товщина тестової плати FR-4 t */
#define FLEX_DWELL_TIME_SEC          60.0f    /* Час витримки на максимумі навантаження */
#define FLEX_FILTER_ALPHA            0.15f    /* Коефіцієнт цифрового фільтра EMA */

typedef enum {
    FLEX_STATE_IDLE = 0,
    FLEX_STATE_CALIBRATING,
    FLEX_STATE_DESCENDING,
    FLEX_STATE_DWELLING,
    FLEX_STATE_RETRACTING,
    FLEX_STATE_PASSED,
    FLEX_STATE_FAILED_CAP_DROP,
    FLEX_STATE_FAILED_SHORT_CIRCUIT,
    FLEX_STATE_FAILED_OPEN_CIRCUIT,
    FLEX_STATE_EMERGENCY_STOP
} flex_state_t;

typedef struct {
    float initial_cap_pf;        /* Базова ємність C0 перед вигином */
    float target_deflection_mm;  /* Цільовий прогин (2.0 мм або 5.0 мм) */
    float speed_mm_per_sec;      /* Швидкість опускання (1.0 мм/с) */
    float gauge_factor;          /* Чутливість тензорезистора S_g */
    float span_length_mm;        /* Проліт L */
    float pcb_thickness_mm;      /* Товщина плати t */
} flex_config_t;

typedef struct {
    float current_deflection_mm; /* Поточний прогин пуансона h */
    float current_microstrain;   /* Поточна деформація плати (με) */
    float filtered_strain_ppm;   /* Згладжена деформація після ФНЧ */
    float current_cap_pf;        /* Виміряна поточна ємність */
    float current_leakage_na;    /* Виміряний струм витоку */
    float cap_change_percent;    /* Відхилення Delta C / C0 (%) */
    float dwell_timer_sec;       /* Таймер утримання навантаження */
    float failure_deflection_mm; /* Прогин, на якому сталася відмова */
    float failure_microstrain;   /* Деформація в момент відмови */
    flex_state_t state;          /* Поточний стан випробування */
} flex_telemetry_t;

/* Обчислення теоретичної деформації поверхні балки: eps = 6 * t * h / L^2 */
static inline float calculate_surface_strain_ppm(float h_mm, float t_mm, float l_mm) {
    if (l_mm <= 0.0f) return 0.0f;
    return (6.0f * t_mm * h_mm / (l_mm * l_mm)) * 1.0e6f;
}

/* Ініціалізація структури моніторингу */
void flex_monitor_init(flex_telemetry_t *t, const flex_config_t *cfg, float c0_pf, float leak0_na) {
    t->current_deflection_mm = 0.0f;
    t->current_microstrain = 0.0f;
    t->filtered_strain_ppm = 0.0f;
    t->current_cap_pf = c0_pf;
    t->current_leakage_na = leak0_na;
    t->cap_change_percent = 0.0f;
    t->dwell_timer_sec = 0.0f;
    t->failure_deflection_mm = 0.0f;
    t->failure_microstrain = 0.0f;
    t->state = FLEX_STATE_DESCENDING;
}

/* Періодичний крок опитування стенда (викликається кожні dt_sec, наприклад 0.01 с) */
flex_state_t flex_monitor_step(flex_telemetry_t *t,
                               const flex_config_t *cfg,
                               float measured_cap_pf,
                               float measured_leak_na,
                               float raw_adc_strain_ppm,
                               float dt_sec) {
    if (t->state != FLEX_STATE_DESCENDING && t->state != FLEX_STATE_DWELLING) {
        return t->state;
    }

    t->current_cap_pf = measured_cap_pf;
    t->current_leakage_na = measured_leak_na;

    /* Цифрова фільтрація сигналу тензомоста */
    t->filtered_strain_ppm = FLEX_FILTER_ALPHA * raw_adc_strain_ppm +
                             (1.0f - FLEX_FILTER_ALPHA) * t->filtered_strain_ppm;

    /* Оновлення переміщення під час фази опускання */
    if (t->state == FLEX_STATE_DESCENDING) {
        t->current_deflection_mm += cfg->speed_mm_per_sec * dt_sec;
        if (t->current_deflection_mm >= cfg->target_deflection_mm) {
            t->current_deflection_mm = cfg->target_deflection_mm;
            t->state = FLEX_STATE_DWELLING;
            t->dwell_timer_sec = 0.0f;
        }
    } else if (t->state == FLEX_STATE_DWELLING) {
        t->dwell_timer_sec += dt_sec;
        if (t->dwell_timer_sec >= FLEX_DWELL_TIME_SEC) {
            t->state = FLEX_STATE_PASSED;
            return t->state;
        }
    }

    /* Розрахунок деформації в мікрострейнах за геометрією балки */
    t->current_microstrain = calculate_surface_strain_ppm(
        t->current_deflection_mm, cfg->pcb_thickness_mm, cfg->span_length_mm
    );

    /* Розрахунок відносного відхилення ємності */
    if (cfg->initial_cap_pf > 0.0f) {
        t->cap_change_percent = fabsf(measured_cap_pf - cfg->initial_cap_pf) / cfg->initial_cap_pf * 100.0f;
    }

    /* 1. Контроль короткого замикання (пробій ізоляції / спалах витоку) */
    if (t->current_leakage_na >= FLEX_CRIT_LEAKAGE_NA) {
        t->state = FLEX_STATE_FAILED_SHORT_CIRCUIT;
        t->failure_deflection_mm = t->current_deflection_mm;
        t->failure_microstrain = t->current_microstrain;
        return t->state;
    }

    /* 2. Контроль деградації ємності */
    if (t->cap_change_percent >= FLEX_CRIT_CAP_DROP_PERCENT) {
        t->failure_deflection_mm = t->current_deflection_mm;
        t->failure_microstrain = t->current_microstrain;
        if (measured_cap_pf < (cfg->initial_cap_pf * 0.1f)) {
            t->state = FLEX_STATE_FAILED_OPEN_CIRCUIT;
        } else {
            t->state = FLEX_STATE_FAILED_CAP_DROP;
        }
        return t->state;
    }

    return t->state;
}
