// Двосмуговий планувальник відправки повідомлень (C)
#include <stdint.h>
#include <stdbool.h>

#define DRAIN_RATE_HZ     5   // макс 5 пакетів архіву на секунду
#define DRAIN_INTERVAL_MS (1000 / DRAIN_RATE_HZ)

typedef struct {
    uint32_t last_drain_time;
    uint32_t tokens;
    bool live_pending;
} DualLaneScheduler;

extern bool mqtt_publish(const char *topic, const uint8_t *data, size_t len, int qos);
extern bool flash_queue_pop(uint8_t *buf, size_t *out_len);
extern bool flash_queue_is_empty(void);

void dual_lane_process(DualLaneScheduler *sched, uint32_t now_ms,
                       const uint8_t *live_data, size_len_t live_len) {
    // 1. Високий пріоритет: свіжі Live-дані відправляються негайно
    if (live_data && live_len > 0) {
        mqtt_publish("nodes/01/state", live_data, live_len, 1);
    }

    // 2. Фоновий пріоритет: викачування черги повторів Replay з обмеженням темпу
    if (now_ms - sched->last_drain_time >= DRAIN_INTERVAL_MS) {
        sched->last_drain_time = now_ms;

        if (!flash_queue_is_empty()) {
            uint8_t replay_buf[128];
            size_t replay_len = 0;
            if (flash_queue_pop(replay_buf, &replay_len)) {
                mqtt_publish("nodes/01/replay", replay_buf, replay_len, 1);
            }
        }
    }
}
