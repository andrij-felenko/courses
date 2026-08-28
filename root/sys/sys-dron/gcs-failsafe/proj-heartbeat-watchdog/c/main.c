#include <stdint.h>
#include <stdbool.h>

#define LINK_WARNING_TIMEOUT_MS  1500u
#define LINK_FAILSAFE_TIMEOUT_MS 3500u
#define LINK_RECOVERY_PACKETS    3u
#define PACKET_WINDOW_SIZE       64u

typedef enum {
    LINK_STATE_LOST = 0,
    LINK_STATE_DEGRADED = 1,
    LINK_STATE_CONNECTED = 2
} link_state_t;

typedef struct {
    uint32_t last_heartbeat_ms;
    uint32_t last_any_packet_ms;
    uint32_t smoothed_rtt_ms;
    uint32_t rtt_variance_ms;
    uint8_t  last_sequence;
    uint64_t packet_history_mask; // 1 = отримано, 0 = втрачено
    uint32_t consecutive_valid_hb;
    link_state_t current_state;
    bool has_received_any;
} link_monitor_t;

// Підрахунок кількості одиничних бітів у 64-бітному числі (алгоритм Браяна Кернігана)
static inline uint32_t count_set_bits(uint64_t v) {
    uint32_t count = 0;
    while (v > 0) {
        v &= (v - 1);
        count++;
    }
    return count;
}

// Ініціалізація внутрішнього стану монітора
void link_monitor_init(link_monitor_t *mon) {
    mon->last_heartbeat_ms = 0;
    mon->last_any_packet_ms = 0;
    mon->smoothed_rtt_ms = 0;
    mon->rtt_variance_ms = 0;
    mon->last_sequence = 0;
    mon->packet_history_mask = 0;
    mon->consecutive_valid_hb = 0;
    mon->current_state = LINK_STATE_LOST;
    mon->has_received_any = false;
}

// Реєстрація надходження будь-якого кадру MAVLink для аналізу лічильника seq
void link_monitor_feed_packet(link_monitor_t *mon, uint8_t seq, uint32_t now_ms) {
    mon->last_any_packet_ms = now_ms;
    if (!mon->has_received_any) {
        mon->has_received_any = true;
        mon->last_sequence = seq;
        mon->packet_history_mask = 1ULL;
        return;
    }

    uint8_t diff = (uint8_t)(seq - mon->last_sequence);
    if (diff > 0 && diff < 128) {
        // Зсув маски на кількість пропущених пакетів
        if (diff >= PACKET_WINDOW_SIZE) {
            mon->packet_history_mask = 0;
        } else {
            mon->packet_history_mask <<= diff;
        }
        mon->packet_history_mask |= 1ULL; // Поточний пакет успішно отримано
        mon->last_sequence = seq;
    } else if (diff == 0) {
        // Дублікат кадру: стан послідовності не змінюється
    } else {
        // Запізнілий пакет або пакет з іншого каналу
    }
}

// Оновлення згладженої затримки RTT та її варіації за формулою EWMA
void link_monitor_feed_rtt(link_monitor_t *mon, uint32_t measured_rtt_ms) {
    if (mon->smoothed_rtt_ms == 0) {
        mon->smoothed_rtt_ms = measured_rtt_ms;
        mon->rtt_variance_ms = measured_rtt_ms / 2;
    } else {
        int32_t delta = (int32_t)measured_rtt_ms - (int32_t)mon->smoothed_rtt_ms;
        if (delta < 0) delta = -delta;
        
        // Варіація RTT: beta = 1/4 -> (3 * var + delta) / 4
        mon->rtt_variance_ms = (mon->rtt_variance_ms * 3u + (uint32_t)delta) >> 2;
        
        // Згладжене RTT: alpha = 1/8 -> (7 * smoothed + measured) / 8
        mon->smoothed_rtt_ms = (mon->smoothed_rtt_ms * 7u + measured_rtt_ms) >> 3;
    }
}

// Реєстрація надходження службового кадру пульсу (HEARTBEAT)
void link_monitor_feed_heartbeat(link_monitor_t *mon, uint8_t seq, uint32_t now_ms) {
    link_monitor_feed_packet(mon, seq, now_ms);
    mon->last_heartbeat_ms = now_ms;
    mon->consecutive_valid_hb++;

    if (mon->current_state == LINK_STATE_LOST) {
        if (mon->consecutive_valid_hb >= LINK_RECOVERY_PACKETS) {
            mon->current_state = LINK_STATE_CONNECTED;
        }
    }
}

// Обчислення відсотка втрачених пакетів у ковзному вікні (діапазон 0..100 %)
uint8_t link_monitor_get_loss_percent(const link_monitor_t *mon) {
    if (!mon->has_received_any) return 100;
    uint32_t received = count_set_bits(mon->packet_history_mask);
    return (uint8_t)(100u - (received * 100u / PACKET_WINDOW_SIZE));
}

// Розрахунок адаптивного порогу таймауту на основі RTT та варіації
uint32_t link_monitor_get_adaptive_timeout_ms(const link_monitor_t *mon) {
    if (mon->smoothed_rtt_ms == 0) {
        return LINK_FAILSAFE_TIMEOUT_MS;
    }
    uint32_t timeout = mon->smoothed_rtt_ms + (mon->rtt_variance_ms << 2);
    if (timeout < 1000u) timeout = 1000u;
    if (timeout > LINK_FAILSAFE_TIMEOUT_MS) timeout = LINK_FAILSAFE_TIMEOUT_MS;
    return timeout;
}

// Періодична функція оновлення автоматів станів (викликається в циклі таймера)
link_state_t link_monitor_update(link_monitor_t *mon, uint32_t now_ms) {
    if (!mon->has_received_any) {
        mon->current_state = LINK_STATE_LOST;
        return mon->current_state;
    }

    uint32_t dt = now_ms - mon->last_heartbeat_ms;
    uint8_t loss = link_monitor_get_loss_percent(mon);

    if (dt >= LINK_FAILSAFE_TIMEOUT_MS) {
        mon->current_state = LINK_STATE_LOST;
        mon->consecutive_valid_hb = 0;
    } else if (dt >= LINK_WARNING_TIMEOUT_MS || loss > 40) {
        if (mon->current_state != LINK_STATE_LOST) {
            mon->current_state = LINK_STATE_DEGRADED;
        }
    } else {
        if (mon->current_state == LINK_STATE_DEGRADED) {
            mon->current_state = LINK_STATE_CONNECTED;
        }
    }

    return mon->current_state;
}
