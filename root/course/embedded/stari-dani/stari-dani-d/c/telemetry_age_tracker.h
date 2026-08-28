/* telemetry_age_tracker.h — Модуль моніторингу віку телеметрії на C */
#ifndef TELEMETRY_AGE_TRACKER_H
#define TELEMETRY_AGE_TRACKER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RECOVERY_CONSECUTIVE_PACKETS 3

typedef enum {
    TELEMETRY_STATE_FRESH,     /* 0..500 мс: свіжі дані, повний контраст */
    TELEMETRY_STATE_DEGRADED,  /* 500..2000 мс: деградація, збліднення, жовта рамка */
    TELEMETRY_STATE_STALE      /* > 2000 мс: недійсні дані, червоний хрест, NO DATA */
} telemetry_state_t;

typedef enum {
    UI_COLOR_NORMAL,
    UI_COLOR_WARNING_AMBER,
    UI_COLOR_STALE_RED
} ui_color_code_t;

typedef struct {
    float           alpha_opacity;        /* Рівень непрозорості: 1.0f -> свіжо, 0.45f -> збліднення */
    ui_color_code_t border_color;         /* Колір рамки віджета */
    bool            cross_out_required;   /* Прапорець: перекреслити віджет червоним хрестом */
    bool            show_age_badge;       /* Прапорець: показати числовий бейдж віку */
    char            age_str[16];          /* Форматований рядок: "+1.4s" або "> 2.0s" */
    telemetry_state_t state;              /* Логічний стан поля */
    uint32_t        age_ms;               /* Точний вік у мілісекундах */
} telemetry_visual_state_t;

typedef struct {
    uint32_t last_rx_monotonic_ms;        /* Час отримання останнього валідного пакету */
    uint32_t last_onboard_boot_ms;        /* Бортова мітка часу (для детекції зависання датчика) */
    uint8_t  last_sequence;               /* Останній лічильник послідовності */
    uint8_t  consecutive_good_frames;     /* Лічильник серії свіжих пакетів для гістерезису */
    bool     has_received_first;          /* Чи надійшов хоча б один пакет */
    bool     is_sensor_frozen;            /* Прапорець зависання бортового датчика */
    
    uint32_t warn_timeout_ms;             /* Поріг переходу в стан DEGRADED (типово 500 мс) */
    uint32_t stale_timeout_ms;            /* Поріг переходу в стан STALE (типово 2000 мс) */
} telemetry_tracker_t;

void telemetry_tracker_init(telemetry_tracker_t *tracker, 
                            uint32_t warn_timeout_ms, 
                            uint32_t stale_timeout_ms);

void telemetry_tracker_update(telemetry_tracker_t *tracker,
                              uint8_t sequence,
                              uint32_t onboard_boot_ms,
                              uint32_t now_monotonic_ms);

telemetry_visual_state_t telemetry_tracker_get_visual_state(const telemetry_tracker_t *tracker,
                                                            uint32_t now_monotonic_ms);

#ifdef __cplusplus
}
#endif

#endif /* TELEMETRY_AGE_TRACKER_H */
