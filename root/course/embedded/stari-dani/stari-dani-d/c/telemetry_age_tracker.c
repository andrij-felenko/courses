/* telemetry_age_tracker.c — Реалізація функцій моніторингу віку телеметрії на C */
#include "telemetry_age_tracker.h"

void telemetry_tracker_init(telemetry_tracker_t *tracker, 
                            uint32_t warn_timeout_ms, 
                            uint32_t stale_timeout_ms) {
    if (!tracker) return;
    tracker->last_rx_monotonic_ms   = 0;
    tracker->last_onboard_boot_ms   = 0;
    tracker->last_sequence          = 0;
    tracker->consecutive_good_frames = 0;
    tracker->has_received_first     = false;
    tracker->is_sensor_frozen       = false;
    tracker->warn_timeout_ms        = warn_timeout_ms;
    tracker->stale_timeout_ms       = stale_timeout_ms;
}

void telemetry_tracker_update(telemetry_tracker_t *tracker,
                              uint8_t sequence,
                              uint32_t onboard_boot_ms,
                              uint32_t now_monotonic_ms) {
    if (!tracker) return;
    
    /* Перевірка на застигання бортового часу */
    if (tracker->has_received_first && 
        onboard_boot_ms == tracker->last_onboard_boot_ms && 
        sequence != tracker->last_sequence) {
        tracker->is_sensor_frozen = true;
        tracker->consecutive_good_frames = 0;
        return;
    }

    tracker->last_sequence          = sequence;
    tracker->last_onboard_boot_ms   = onboard_boot_ms;
    tracker->last_rx_monotonic_ms   = now_monotonic_ms;
    tracker->has_received_first     = true;
    tracker->is_sensor_frozen       = false;

    if (tracker->consecutive_good_frames < RECOVERY_CONSECUTIVE_PACKETS) {
        tracker->consecutive_good_frames++;
    }
}

telemetry_visual_state_t telemetry_tracker_get_visual_state(const telemetry_tracker_t *tracker,
                                                            uint32_t now_monotonic_ms) {
    telemetry_visual_state_t vs;
    
    if (!tracker || !tracker->has_received_first || tracker->is_sensor_frozen) {
        vs.state = TELEMETRY_STATE_STALE;
        vs.alpha_opacity = 0.35f;
        vs.border_color = UI_COLOR_STALE_RED;
        vs.cross_out_required = true;
        vs.show_age_badge = true;
        vs.age_ms = (tracker && tracker->is_sensor_frozen) ? 
                    (tracker->stale_timeout_ms + 1000) : 0xFFFFFFFFU;
        vs.age_str[0] = 'N'; vs.age_str[1] = 'O'; vs.age_str[2] = ' '; 
        vs.age_str[3] = 'D'; vs.age_str[4] = 'A'; vs.age_str[5] = 'T'; 
        vs.age_str[6] = 'A'; vs.age_str[7] = '\0';
        return vs;
    }

    /* Безпечне віднімання беззнакових чисел (Wrap-around arithmetic) */
    uint32_t age = now_monotonic_ms - tracker->last_rx_monotonic_ms;
    vs.age_ms = age;

    bool is_recovered = (tracker->consecutive_good_frames >= RECOVERY_CONSECUTIVE_PACKETS);

    if (age <= tracker->warn_timeout_ms && is_recovered) {
        vs.state = TELEMETRY_STATE_FRESH;
        vs.alpha_opacity = 1.0f;
        vs.border_color = UI_COLOR_NORMAL;
        vs.cross_out_required = false;
        vs.show_age_badge = false;
        vs.age_str[0] = '\0';
    } else if (age <= tracker->stale_timeout_ms) {
        vs.state = TELEMETRY_STATE_DEGRADED;
        
        /* Лінійна інтерполяція прозорості від 0.85 до 0.45 */
        float progress = (float)(age - tracker->warn_timeout_ms) / 
                         (float)(tracker->stale_timeout_ms - tracker->warn_timeout_ms);
        vs.alpha_opacity = 0.85f - (progress * 0.40f);
        vs.border_color = UI_COLOR_WARNING_AMBER;
        vs.cross_out_required = false;
        vs.show_age_badge = true;
        
        /* Форматування рядка віку без динамічної пам'яті */
        uint32_t sec = age / 1000;
        uint32_t tenths = (age % 1000) / 100;
        vs.age_str[0] = '+';
        vs.age_str[1] = (char)('0' + (sec % 10));
        vs.age_str[2] = '.';
        vs.age_str[3] = (char)('0' + tenths);
        vs.age_str[4] = 's';
        vs.age_str[5] = '\0';
    } else {
        vs.state = TELEMETRY_STATE_STALE;
        vs.alpha_opacity = 0.35f;
        vs.border_color = UI_COLOR_STALE_RED;
        vs.cross_out_required = true;
        vs.show_age_badge = true;
        
        vs.age_str[0] = '>'; vs.age_str[1] = '2'; vs.age_str[2] = '.'; 
        vs.age_str[3] = '0'; vs.age_str[4] = 's'; vs.age_str[5] = '\0';
    }

    return vs;
}
