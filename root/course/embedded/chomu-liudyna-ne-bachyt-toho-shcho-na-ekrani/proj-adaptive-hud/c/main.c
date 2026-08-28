#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAX_WIDGETS 16
#define EMA_ALPHA   0.25f

typedef enum {
    SEVERITY_NORMAL = 0,
    SEVERITY_WARNING,
    SEVERITY_CRITICAL
} SeverityLevel;

typedef enum {
    HUD_MODE_FULL = 0,        /* Спокійний моніторинг: всі параметри */
    HUD_MODE_PILOTING,        /* Активне пілотування: приховати інфошум */
    HUD_MODE_EMERGENCY        /* Аварія: суворе розхаращення, фокус на біді */
} HudDisplayMode;

typedef enum {
    PRIO_LOW = 0,             /* Фонова статистика (GPS HDOP, пакети) */
    PRIO_MEDIUM,              /* Поточний стан (температура, висота) */
    PRIO_HIGH                 /* Життєво важливі (напруга, крен, зв'язок) */
} WidgetPriority;

typedef struct {
    char name[20];
    float value;
    float prev_value;
    float filtered_rate;      /* dx/dt після експоненційного згладжування */
    uint32_t last_update_ms;
    float warn_threshold;
    float crit_threshold;
    float max_safe_rate;      /* Поріг швидкості зміни (захист від Change Blindness) */
    WidgetPriority priority;
    SeverityLevel severity;
    bool is_visible;
} TelemetryWidget;

typedef struct {
    TelemetryWidget widgets[MAX_WIDGETS];
    size_t widget_count;
    HudDisplayMode mode;
    uint32_t last_stick_activity_ms;
    bool has_critical_alarm;
} AdaptiveHudEngine;

void hud_init(AdaptiveHudEngine *hud) {
    memset(hud, 0, sizeof(AdaptiveHudEngine));
    hud->mode = HUD_MODE_FULL;
}

bool hud_register_widget(AdaptiveHudEngine *hud, const char *name,
                         WidgetPriority prio, float warn_th, float crit_th,
                         float max_rate) {
    if (hud->widget_count >= MAX_WIDGETS) {
        return false;
    }
    TelemetryWidget *w = &hud->widgets[hud->widget_count++];
    strncpy(w->name, name, sizeof(w->name) - 1);
    w->name[sizeof(w->name) - 1] = '\0';
    w->priority = prio;
    w->warn_threshold = warn_th;
    w->crit_threshold = crit_th;
    w->max_safe_rate = max_rate;
    w->severity = SEVERITY_NORMAL;
    w->is_visible = true;
    return true;
}

void hud_update_metric(AdaptiveHudEngine *hud, size_t index, float new_val,
                       uint32_t timestamp_ms) {
    if (index >= hud->widget_count) return;
    TelemetryWidget *w = &hud->widgets[index];

    float dt = (timestamp_ms - w->last_update_ms) / 1000.0f;
    if (dt > 0.001f && w->last_update_ms > 0) {
        float raw_rate = fabsf(new_val - w->value) / dt;
        w->filtered_rate = (EMA_ALPHA * raw_rate) + ((1.0f - EMA_ALPHA) * w->filtered_rate);
    }

    w->prev_value = w->value;
    w->value = new_val;
    w->last_update_ms = timestamp_ms;

    /* Визначення рівня небезпеки за значенням та швидкістю зміни */
    if (w->value >= w->crit_threshold) {
        w->severity = SEVERITY_CRITICAL;
    } else if (w->value >= w->warn_threshold || (w->max_safe_rate > 0 && w->filtered_rate >= w->max_safe_rate)) {
        w->severity = SEVERITY_WARNING;
    } else {
        w->severity = SEVERITY_NORMAL;
    }
}

void hud_evaluate_state(AdaptiveHudEngine *hud, float stick_magnitude, uint32_t now_ms) {
    /* 1. Моніторинг активності оператора */
    if (stick_magnitude > 0.3f) {
        hud->last_stick_activity_ms = now_ms;
    }

    /* 2. Перевірка наявності критичних тривог */
    hud->has_critical_alarm = false;
    for (size_t i = 0; i < hud->widget_count; ++i) {
        if (hud->widgets[i].severity == SEVERITY_CRITICAL) {
            hud->has_critical_alarm = true;
            break;
        }
    }

    /* 3. Автомат перемикання режимів відображення */
    if (hud->has_critical_alarm) {
        hud->mode = HUD_MODE_EMERGENCY;
    } else if (now_ms - hud->last_stick_activity_ms < 2000) {
        hud->mode = HUD_MODE_PILOTING;
    } else {
        hud->mode = HUD_MODE_FULL;
    }

    /* 4. Фільтрація видимості віджетів (Decluttering) */
    for (size_t i = 0; i < hud->widget_count; ++i) {
        TelemetryWidget *w = &hud->widgets[i];

        switch (hud->mode) {
        case HUD_MODE_EMERGENCY:
            /* В аварії показуємо лише критичний віджет та базові життєві параметри */
            w->is_visible = (w->severity == SEVERITY_CRITICAL) || (w->priority == PRIO_HIGH);
            break;

        case HUD_MODE_PILOTING:
            /* Під час активного маневру ховаємо фоновий шум */
            w->is_visible = (w->priority >= PRIO_MEDIUM) || (w->severity != SEVERITY_NORMAL);
            break;

        case HUD_MODE_FULL:
        default:
            w->is_visible = true;
            break;
        }
    }
}

void hud_render_console(const AdaptiveHudEngine *hud) {
    const char *mode_str = (hud->mode == HUD_MODE_EMERGENCY) ? "EMERGENCY (Суворе розхаращення)"
                         : (hud->mode == HUD_MODE_PILOTING)  ? "PILOTING (Приглушений шум)"
                                                             : "FULL MONITORING (Спокій)";

    printf("\n=== HUD РЕЖИМ: %s ===\n", mode_str);
    for (size_t i = 0; i < hud->widget_count; ++i) {
        const TelemetryWidget *w = &hud->widgets[i];
        if (!w->is_visible) {
            continue; /* Приховано автоматом розхаращення для розвантаження уваги */
        }

        const char *color_code = (w->severity == SEVERITY_CRITICAL) ? "\033[1;31m[КРИТИЧНО]\033[0m"
                               : (w->severity == SEVERITY_WARNING)  ? "\033[1;33m[УВАГА]   \033[0m"
                                                                    : "\033[0;37m[НОРМА]   \033[0m";

        printf("%s %-14s = %6.2f | dX/dt = %5.2f/с\n",
               color_code, w->name, w->value, w->filtered_rate);
    }
}
