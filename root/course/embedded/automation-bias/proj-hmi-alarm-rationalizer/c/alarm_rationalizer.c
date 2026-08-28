#include "alarm_rationalizer.h"
#include <string.h>

static void add_rate_event(AlarmRationalizer_t *ar, uint64_t now_ms) {
    size_t capacity = sizeof(ar->rate_history) / sizeof(ar->rate_history[0]);
    ar->rate_history[ar->rate_head] = now_ms;
    ar->rate_head = (ar->rate_head + 1) % capacity;
    if (ar->rate_head == ar->rate_tail) {
        ar->rate_tail = (ar->rate_tail + 1) % capacity;
    }
}

static void update_rate_metrics(AlarmRationalizer_t *ar, uint64_t now_ms) {
    size_t capacity = sizeof(ar->rate_history) / sizeof(ar->rate_history[0]);
    uint64_t cutoff = (now_ms >= ALARM_RATE_WINDOW_MS) ? (now_ms - ALARM_RATE_WINDOW_MS) : 0;
    
    while (ar->rate_tail != ar->rate_head) {
        if (ar->rate_history[ar->rate_tail] < cutoff) {
            ar->rate_tail = (ar->rate_tail + 1) % capacity;
        } else {
            break;
        }
    }

    if (ar->rate_head >= ar->rate_tail) {
        ar->alarms_in_rate_window = ar->rate_head - ar->rate_tail;
    } else {
        ar->alarms_in_rate_window = capacity - (ar->rate_tail - ar->rate_head);
    }

    ar->is_alarm_flood_active = (ar->alarms_in_rate_window >= ALARM_FLOOD_THRESHOLD);
}

void alarm_rationalizer_init(AlarmRationalizer_t *ar) {
    if (!ar) return;
    memset(ar, 0, sizeof(AlarmRationalizer_t));
    ar->current_sys_state = SYS_STATE_COLD_BOOT;
}

bool alarm_rationalizer_register(AlarmRationalizer_t *ar, const AlarmConfig_t *cfg) {
    if (!ar || !cfg || ar->count >= MAX_ALARMS) {
        return false;
    }
    size_t idx = ar->count++;
    memcpy(&ar->configs[idx], cfg, sizeof(AlarmConfig_t));
    memset(&ar->runtimes[idx], 0, sizeof(AlarmRuntime_t));
    ar->runtimes[idx].state = ALARM_STATE_NORMAL;
    ar->runtimes[idx].prev_state = ALARM_STATE_NORMAL;
    return true;
}

void alarm_rationalizer_set_system_state(AlarmRationalizer_t *ar, uint32_t sys_state, uint64_t now_ms) {
    if (!ar) return;
    ar->current_sys_state = sys_state;
    (void)now_ms;
}

void alarm_rationalizer_update_value(AlarmRationalizer_t *ar, uint16_t alarm_id, float value, uint64_t now_ms) {
    if (!ar || alarm_id >= ar->count) return;
    (void)now_ms;
    ar->runtimes[alarm_id].current_value = value;
}

static void evaluate_raw_trip_condition(const AlarmConfig_t *cfg, AlarmRuntime_t *rt) {
    if (cfg->is_high_alarm) {
        if (rt->raw_trip_condition) {
            /* Гістерезис для High: скидання лише коли сигнал опустився нижче clear_threshold */
            if (rt->current_value <= cfg->clear_threshold) {
                rt->raw_trip_condition = false;
            }
        } else {
            if (rt->current_value >= cfg->trip_threshold) {
                rt->raw_trip_condition = true;
            }
        }
    } else {
        if (rt->raw_trip_condition) {
            /* Гістерезис для Low: скидання лише коли сигнал піднявся вище clear_threshold */
            if (rt->current_value >= cfg->clear_threshold) {
                rt->raw_trip_condition = false;
            }
        } else {
            if (rt->current_value <= cfg->trip_threshold) {
                rt->raw_trip_condition = true;
            }
        }
    }
}

static void update_chatter_detector(const AlarmConfig_t *cfg, AlarmRuntime_t *rt, uint64_t now_ms) {
    if (cfg->chatter_limit == 0 || cfg->chatter_window_ms == 0) {
        rt->is_chattering = false;
        return;
    }

    if (rt->first_transition_in_window_ms == 0 || (now_ms - rt->first_transition_in_window_ms) > cfg->chatter_window_ms) {
        rt->first_transition_in_window_ms = now_ms;
        rt->transitions_in_window = 1;
        rt->is_chattering = false;
    } else {
        rt->transitions_in_window++;
        if (rt->transitions_in_window >= cfg->chatter_limit) {
            rt->is_chattering = true;
        }
    }
}

void alarm_rationalizer_process(AlarmRationalizer_t *ar, uint64_t now_ms) {
    if (!ar) return;

    /* Фаза 1: Оцінка пригнічення за станом системи та батьківськими тривогами */
    for (size_t i = 0; i < ar->count; ++i) {
        const AlarmConfig_t *cfg = &ar->configs[i];
        AlarmRuntime_t *rt = &ar->runtimes[i];

        /* Пригнічення за експлуатаційним режимом */
        rt->is_suppressed_by_state = ((ar->current_sys_state & cfg->suppression_state_mask) != 0);

        /* Пригнічення вторинних тривог від первинної причини (Root-Cause Suppression) */
        rt->is_suppressed_by_parent = false;
        if (cfg->parent_alarm_id >= 0 && (size_t)cfg->parent_alarm_id < ar->count) {
            AlarmState_t parent_state = ar->runtimes[cfg->parent_alarm_id].state;
            if (parent_state == ALARM_STATE_UNACK_ALARM || parent_state == ALARM_STATE_ACK_ALARM) {
                rt->is_suppressed_by_parent = true;
            }
        }

        /* Перевірка закінчення терміну тимчасового відкладення (Shelve Timeout) */
        if (rt->state == ALARM_STATE_SHELVED && now_ms >= rt->shelved_until_timestamp_ms) {
            rt->state = rt->raw_trip_condition ? ALARM_STATE_UNACK_ALARM : ALARM_STATE_NORMAL;
            rt->state_change_timestamp_ms = now_ms;
        }
    }

    /* Фаза 2: Обчислення переходів автомата станів ISA-18.2 */
    for (size_t i = 0; i < ar->count; ++i) {
        const AlarmConfig_t *cfg = &ar->configs[i];
        AlarmRuntime_t *rt = &ar->runtimes[i];

        if (rt->state == ALARM_STATE_OUT_OF_SERVICE) {
            continue;
        }

        bool should_suppress = rt->is_suppressed_by_state || rt->is_suppressed_by_parent;
        if (should_suppress) {
            if (rt->state != ALARM_STATE_SUPPRESSED_BY_DESIGN && rt->state != ALARM_STATE_SHELVED) {
                rt->prev_state = rt->state;
                rt->state = ALARM_STATE_SUPPRESSED_BY_DESIGN;
                rt->state_change_timestamp_ms = now_ms;
                ar->total_suppressions++;
            }
            continue;
        } else {
            if (rt->state == ALARM_STATE_SUPPRESSED_BY_DESIGN) {
                rt->state = ALARM_STATE_NORMAL;
                rt->state_change_timestamp_ms = now_ms;
            }
        }

        if (rt->state == ALARM_STATE_SHELVED) {
            continue;
        }

        bool old_raw = rt->raw_trip_condition;
        evaluate_raw_trip_condition(cfg, rt);

        if (old_raw != rt->raw_trip_condition) {
            update_chatter_detector(cfg, rt, now_ms);
            if (rt->is_chattering) {
                ar->total_chatter_events++;
            }
        }

        /* Застосування фільтрів On-Delay та Off-Delay */
        bool active_filtered = false;
        if (rt->raw_trip_condition) {
            rt->clear_start_timestamp_ms = 0;
            if (rt->trip_start_timestamp_ms == 0) {
                rt->trip_start_timestamp_ms = now_ms;
            }
            if ((now_ms - rt->trip_start_timestamp_ms) >= cfg->on_delay_ms) {
                active_filtered = true;
            }
        } else {
            rt->trip_start_timestamp_ms = 0;
            if (rt->clear_start_timestamp_ms == 0) {
                rt->clear_start_timestamp_ms = now_ms;
            }
            if ((now_ms - rt->clear_start_timestamp_ms) < cfg->off_delay_ms) {
                active_filtered = true; /* Ще тримаємо активний стан до закінчення off-delay */
            }
        }

        /* Логіка автомата станів */
        AlarmState_t next_state = rt->state;
        switch (rt->state) {
            case ALARM_STATE_NORMAL:
                if (active_filtered && !rt->is_chattering) {
                    next_state = ALARM_STATE_UNACK_ALARM;
                    ar->total_trips++;
                    add_rate_event(ar, now_ms);
                }
                break;

            case ALARM_STATE_UNACK_ALARM:
                if (!active_filtered) {
                    next_state = ALARM_STATE_RTN_UNACK;
                }
                break;

            case ALARM_STATE_ACK_ALARM:
                if (!active_filtered) {
                    next_state = ALARM_STATE_NORMAL;
                }
                break;

            case ALARM_STATE_RTN_UNACK:
                if (active_filtered) {
                    next_state = ALARM_STATE_UNACK_ALARM;
                }
                break;

            default:
                break;
        }

        if (next_state != rt->state) {
            rt->prev_state = rt->state;
            rt->state = next_state;
            rt->state_change_timestamp_ms = now_ms;
        }
    }

    update_rate_metrics(ar, now_ms);
}

bool alarm_rationalizer_ack(AlarmRationalizer_t *ar, uint16_t alarm_id, uint64_t now_ms) {
    if (!ar || alarm_id >= ar->count) return false;
    AlarmRuntime_t *rt = &ar->runtimes[alarm_id];

    if (rt->state == ALARM_STATE_UNACK_ALARM) {
        rt->prev_state = rt->state;
        rt->state = ALARM_STATE_ACK_ALARM;
        rt->state_change_timestamp_ms = now_ms;
        ar->total_acks++;
        return true;
    } else if (rt->state == ALARM_STATE_RTN_UNACK) {
        rt->prev_state = rt->state;
        rt->state = ALARM_STATE_NORMAL;
        rt->state_change_timestamp_ms = now_ms;
        ar->total_acks++;
        return true;
    }
    return false;
}

bool alarm_rationalizer_shelve(AlarmRationalizer_t *ar, uint16_t alarm_id, uint32_t duration_ms, uint64_t now_ms) {
    if (!ar || alarm_id >= ar->count || duration_ms == 0) return false;
    AlarmRuntime_t *rt = &ar->runtimes[alarm_id];

    if (rt->state == ALARM_STATE_UNACK_ALARM || rt->state == ALARM_STATE_ACK_ALARM) {
        rt->prev_state = rt->state;
        rt->state = ALARM_STATE_SHELVED;
        rt->shelved_until_timestamp_ms = now_ms + duration_ms;
        rt->state_change_timestamp_ms = now_ms;
        return true;
    }
    return false;
}

bool alarm_rationalizer_unshelve(AlarmRationalizer_t *ar, uint16_t alarm_id, uint64_t now_ms) {
    if (!ar || alarm_id >= ar->count) return false;
    AlarmRuntime_t *rt = &ar->runtimes[alarm_id];

    if (rt->state == ALARM_STATE_SHELVED) {
        rt->prev_state = rt->state;
        rt->state = rt->raw_trip_condition ? ALARM_STATE_UNACK_ALARM : ALARM_STATE_NORMAL;
        rt->shelved_until_timestamp_ms = 0;
        rt->state_change_timestamp_ms = now_ms;
        return true;
    }
    return false;
}

size_t alarm_rationalizer_get_active_hmi_alarms(const AlarmRationalizer_t *ar, uint16_t *out_ids, size_t max_out) {
    if (!ar || !out_ids || max_out == 0) return 0;

    size_t count = 0;
    /* Спочатку збираємо критичні, потім високі, середні тощо */
    for (int p = (int)ALARM_PRIO_CRITICAL; p >= (int)ALARM_PRIO_DIAGNOSTIC; --p) {
        for (size_t i = 0; i < ar->count && count < max_out; ++i) {
            if ((int)ar->configs[i].priority != p) continue;
            AlarmState_t s = ar->runtimes[i].state;
            if (s == ALARM_STATE_UNACK_ALARM || s == ALARM_STATE_ACK_ALARM || s == ALARM_STATE_RTN_UNACK) {
                out_ids[count++] = (uint16_t)i;
            }
        }
    }
    return count;
}
