#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ALARMS          32
#define CHATTERING_LIMIT    3
#define CHATTERING_WINDOW_MS 60000

typedef enum {
    ALARM_PRIO_INFO     = 0,
    ALARM_PRIO_WARNING  = 1,
    ALARM_PRIO_CRITICAL = 2,
    ALARM_PRIO_COUNT
} AlarmPriority;

typedef enum {
    ALARM_STATE_NORMAL       = 0,
    ALARM_STATE_UNACK_ACTIVE = 1,
    ALARM_STATE_ACK_ACTIVE   = 2,
    ALARM_STATE_UNACK_CLEARED= 3
} AlarmState;

typedef struct {
    const char*     name;
    AlarmPriority   priority;
    uint32_t        parent_mask;     // Бітова маска батьківських тривог
    uint32_t        on_delay_ms;     // Затримка включення
    uint32_t        off_delay_ms;    // Затримка вимкнення
    uint32_t        escalation_ms;   // Час до повторної ескалації

    // Внутрішній динамічний стан
    AlarmState      state;
    bool            is_suppressed;
    bool            is_chattering;
    uint32_t        raw_active_time_ms;
    uint32_t        raw_clear_time_ms;
    uint32_t        ack_time_ms;
    uint32_t        transition_count;
    uint32_t        last_transition_time_ms;
} AlarmDescriptor;

typedef struct {
    AlarmDescriptor alarms[MAX_ALARMS];
    uint32_t        alarm_count;
    uint32_t        active_mask;
    uint32_t        unack_mask;
    bool            audio_silenced;
    uint32_t        silence_timestamp_ms;
} AlarmManager;

void alarm_mgr_init(AlarmManager* mgr) {
    memset(mgr, 0, sizeof(AlarmManager));
}

int alarm_mgr_register(AlarmManager* mgr, const char* name, AlarmPriority prio,
                       uint32_t parent_mask, uint32_t on_delay_ms, 
                       uint32_t off_delay_ms, uint32_t esc_ms) {
    if (mgr->alarm_count >= MAX_ALARMS) return -1;
    uint32_t id = mgr->alarm_count++;
    AlarmDescriptor* desc = &mgr->alarms[id];
    desc->name = name;
    desc->priority = prio;
    desc->parent_mask = parent_mask;
    desc->on_delay_ms = on_delay_ms;
    desc->off_delay_ms = off_delay_ms;
    desc->escalation_ms = esc_ms;
    desc->state = ALARM_STATE_NORMAL;
    return (int)id;
}

void alarm_mgr_update(AlarmManager* mgr, uint32_t id, bool raw_condition, 
                      uint32_t now_ms, uint32_t dt_ms) {
    if (id >= mgr->alarm_count) return;
    AlarmDescriptor* d = &mgr->alarms[id];

    // 1. Перевірка придушення батьківськими вузлами
    d->is_suppressed = false;
    if (d->parent_mask & mgr->active_mask) {
        d->is_suppressed = true;
    }

    // 2. Детекція деренчання (Chattering / Flapping)
    if (now_ms - d->last_transition_time_ms > CHATTERING_WINDOW_MS) {
        d->transition_count = 0;
    }

    // 3. Обробка таймерів дебаунсу
    if (raw_condition) {
        d->raw_clear_time_ms = 0;
        d->raw_active_time_ms += dt_ms;
    } else {
        d->raw_active_time_ms = 0;
        d->raw_clear_time_ms += dt_ms;
    }

    bool debounced_active = (d->raw_active_time_ms >= d->on_delay_ms);
    bool debounced_clear  = (d->raw_clear_time_ms >= d->off_delay_ms);

    // 4. Автомат життєвого циклу ISA-18.2
    AlarmState prev_state = d->state;
    switch (d->state) {
        case ALARM_STATE_NORMAL:
            if (debounced_active && !d->is_suppressed) {
                d->state = ALARM_STATE_UNACK_ACTIVE;
                d->transition_count++;
                d->last_transition_time_ms = now_ms;
            }
            break;

        case ALARM_STATE_UNACK_ACTIVE:
            if (debounced_clear) {
                d->state = ALARM_STATE_UNACK_CLEARED;
            }
            break;

        case ALARM_STATE_ACK_ACTIVE:
            if (debounced_clear) {
                d->state = ALARM_STATE_NORMAL;
                d->ack_time_ms = 0;
            } else if (d->escalation_ms > 0 && 
                      (now_ms - d->ack_time_ms >= d->escalation_ms)) {
                // Ескалація: повторний перехід у неквітований стан
                d->state = ALARM_STATE_UNACK_ACTIVE;
                mgr->audio_silenced = false;
            }
            break;

        case ALARM_STATE_UNACK_CLEARED:
            if (debounced_active && !d->is_suppressed) {
                d->state = ALARM_STATE_UNACK_ACTIVE;
            }
            break;
    }

    // Блокування при деренчанні
    if (d->transition_count >= CHATTERING_LIMIT) {
        d->is_chattering = true;
    }

    // Оновлення глобальних бітових масок
    uint32_t bit = (1U << id);
    if (d->state == ALARM_STATE_UNACK_ACTIVE || d->state == ALARM_STATE_ACK_ACTIVE) {
        mgr->active_mask |= bit;
    } else {
        mgr->active_mask &= ~bit;
    }

    if (d->state == ALARM_STATE_UNACK_ACTIVE || d->state == ALARM_STATE_UNACK_CLEARED) {
        mgr->unack_mask |= bit;
    } else {
        mgr->unack_mask &= ~bit;
    }
}

void alarm_mgr_acknowledge(AlarmManager* mgr, uint32_t id, uint32_t now_ms) {
    if (id >= mgr->alarm_count) return;
    AlarmDescriptor* d = &mgr->alarms[id];
    if (d->state == ALARM_STATE_UNACK_ACTIVE) {
        d->state = ALARM_STATE_ACK_ACTIVE;
        d->ack_time_ms = now_ms;
    } else if (d->state == ALARM_STATE_UNACK_CLEARED) {
        d->state = ALARM_STATE_NORMAL;
    }
}

void alarm_mgr_silence(AlarmManager* mgr, uint32_t now_ms) {
    mgr->audio_silenced = true;
    mgr->silence_timestamp_ms = now_ms;
}

AlarmPriority alarm_mgr_get_highest_priority(const AlarmManager* mgr) {
    AlarmPriority highest = ALARM_PRIO_INFO;
    bool any_unack = false;

    for (uint32_t i = 0; i < mgr->alarm_count; ++i) {
        const AlarmDescriptor* d = &mgr->alarms[i];
        if (d->state == ALARM_STATE_UNACK_ACTIVE && !d->is_suppressed) {
            any_unack = true;
            if (d->priority > highest) {
                highest = d->priority;
            }
        }
    }
    return any_unack ? highest : ALARM_PRIO_INFO;
}
