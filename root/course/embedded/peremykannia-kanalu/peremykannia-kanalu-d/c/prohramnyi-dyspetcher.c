#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define FAILOVER_MAX_INTERFACES     2
#define FAILOVER_PROBE_INTERVAL_MS  5000
#define FAILOVER_FAIL_THRESHOLD     3
#define FAILOVER_HOLD_DOWN_MS       60000
#define FAILOVER_FALLBACK_DELAY_MS  180000

typedef enum {
    IFACE_STATE_DISABLED = 0,
    IFACE_STATE_STANDBY,
    IFACE_STATE_CONNECTING,
    IFACE_STATE_ONLINE,
    IFACE_STATE_DEGRADED,
    IFACE_STATE_FAILED
} iface_state_t;

typedef struct transport_driver {
    const char* name;
    bool is_primary;
    bool (*power_set)(bool enable);
    bool (*connect)(void);
    void (*disconnect)(void);
    bool (*check_phy_link)(void);
    bool (*send_packet)(const uint8_t *data, size_t len);
    bool (*send_probe)(void);
} transport_driver_t;

typedef struct {
    transport_driver_t *driver;
    iface_state_t state;
    uint32_t last_probe_ms;
    uint32_t state_entered_ms;
    uint8_t consecutive_fails;
    uint8_t consecutive_successes;
} channel_runtime_t;

typedef struct {
    channel_runtime_t channels[FAILOVER_MAX_INTERFACES];
    uint8_t active_idx;
    uint32_t last_switch_ms;
    bool fallback_in_progress;
} failover_manager_t;

void failover_init(failover_manager_t *mgr, transport_driver_t *primary, transport_driver_t *backup) {
    mgr->channels[0].driver = primary;
    mgr->channels[0].state = IFACE_STATE_STANDBY;
    mgr->channels[0].last_probe_ms = 0;
    mgr->channels[0].consecutive_fails = 0;
    mgr->channels[0].consecutive_successes = 0;

    mgr->channels[1].driver = backup;
    mgr->channels[1].state = IFACE_STATE_STANDBY;
    mgr->channels[1].last_probe_ms = 0;
    mgr->channels[1].consecutive_fails = 0;
    mgr->channels[1].consecutive_successes = 0;

    mgr->active_idx = 0;
    mgr->last_switch_ms = 0;
    mgr->fallback_in_progress = false;

    // Вмикаємо основний інтерфейс за замовчуванням
    primary->power_set(true);
    primary->connect();
    mgr->channels[0].state = IFACE_STATE_CONNECTING;
}

void failover_poll(failover_manager_t *mgr, uint32_t now_ms) {
    channel_runtime_t *pri = &mgr->channels[0];
    channel_runtime_t *bak = &mgr->channels[1];

    // 1. Апаратний моніторинг PHY основного каналу
    if (!pri->driver->check_phy_link()) {
        pri->consecutive_fails = FAILOVER_FAIL_THRESHOLD;
        pri->state = IFACE_STATE_FAILED;
    }

    // 2. Періодичне L7 зондування основного каналу
    if (now_ms - pri->last_probe_ms >= FAILOVER_PROBE_INTERVAL_MS) {
        pri->last_probe_ms = now_ms;
        if (pri->driver->check_phy_link() && pri->driver->send_probe()) {
            pri->consecutive_fails = 0;
            pri->consecutive_successes++;
            if (pri->state != IFACE_STATE_ONLINE && pri->consecutive_successes >= 2) {
                pri->state = IFACE_STATE_ONLINE;
            }
        } else {
            pri->consecutive_successes = 0;
            if (pri->consecutive_fails < 255) {
                pri->consecutive_fails++;
            }
            if (pri->consecutive_fails >= FAILOVER_FAIL_THRESHOLD) {
                pri->state = IFACE_STATE_FAILED;
            }
        }
    }

    // 3. Логіка перемикання на резерв (Failover)
    if (mgr->active_idx == 0 && pri->state == IFACE_STATE_FAILED) {
        // Запуск резервного каналу (Cold / Warm Standby)
        bak->driver->power_set(true);
        if (bak->driver->connect()) {
            bak->state = IFACE_STATE_ONLINE;
            mgr->active_idx = 1;
            mgr->last_switch_ms = now_ms;
            mgr->fallback_in_progress = false;
        }
    }

    // 4. Логіка стабілізованого повернення на основний (Fallback Delay)
    if (mgr->active_idx == 1) {
        // Перевіряємо закінчення обов'язкового часу утримання
        bool hold_expired = (now_ms - mgr->last_switch_ms) >= FAILOVER_HOLD_DOWN_MS;

        if (pri->state == IFACE_STATE_ONLINE && hold_expired) {
            if (!mgr->fallback_in_progress) {
                mgr->fallback_in_progress = true;
                pri->state_entered_ms = now_ms;
            } else if (now_ms - pri->state_entered_ms >= FAILOVER_FALLBACK_DELAY_MS) {
                // Основний канал стабільно пропрацював карантинний період
                mgr->active_idx = 0;
                mgr->fallback_in_progress = false;
                mgr->last_switch_ms = now_ms;

                // Переводимо резервний канал назад у стан сну / вимкнення
                bak->driver->disconnect();
                bak->driver->power_set(false);
                bak->state = IFACE_STATE_STANDBY;
            }
        } else {
            // Будь-який збій основного під час карантину скидає таймер
            mgr->fallback_in_progress = false;
        }
    }
}

bool failover_transmit(failover_manager_t *mgr, const uint8_t *payload, size_t len) {
    channel_runtime_t *active = &mgr->channels[mgr->active_idx];
    if (active->state != IFACE_STATE_ONLINE) {
        return false; // Потрібно зберігати в офлайн-буфер
    }
    return active->driver->send_packet(payload, len);
}
