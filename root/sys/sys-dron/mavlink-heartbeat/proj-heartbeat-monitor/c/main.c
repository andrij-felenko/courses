#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_TRACKED_NODES          16
#define HEARTBEAT_PERIOD_MS        1000   // Інтервал відправки 1 Гц
#define HEARTBEAT_WARN_TIMEOUT_MS  3000   // Поріг попередження (3 с)
#define HEARTBEAT_LOST_TIMEOUT_MS  4500   // Поріг втрати лінку (4.5 с)

// Рівні стану зв'язку з віддаленим вузлом
typedef enum {
    NODE_LINK_OFFLINE = 0,
    NODE_LINK_ONLINE,
    NODE_LINK_WARNING,
    NODE_LINK_LOST
} node_link_state_t;

// Структура обліку окремого віддаленого вузла мережі
typedef struct {
    uint8_t           system_id;
    uint8_t           component_id;
    uint8_t           type;
    uint8_t           autopilot;
    uint8_t           base_mode;
    uint32_t          custom_mode;
    uint8_t           system_status;
    uint64_t          last_heartbeat_ms;
    node_link_state_t state;
    bool              is_active;
} tracked_node_t;

// Структура головного контексту монітора
typedef struct {
    uint8_t        my_sysid;
    uint8_t        my_compid;
    uint8_t        my_type;
    uint8_t        my_autopilot;
    uint64_t       last_tx_ms;
    tracked_node_t nodes[MAX_TRACKED_NODES];
    void (*on_failsafe_event)(uint8_t sysid, uint8_t compid, node_link_state_t new_state);
} mavlink_monitor_t;

// Отримання поточного монотонного часу процесора в мілісекундах
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
}

// Ініціалізація структури монітора
void mavlink_monitor_init(mavlink_monitor_t* mon, uint8_t sysid, uint8_t compid,
                          uint8_t type, uint8_t autopilot,
                          void (*failsafe_cb)(uint8_t, uint8_t, node_link_state_t)) {
    memset(mon, 0, sizeof(mavlink_monitor_t));
    mon->my_sysid = sysid;
    mon->my_compid = compid;
    mon->my_type = type;
    mon->my_autopilot = autopilot;
    mon->last_tx_ms = 0;
    mon->on_failsafe_event = failsafe_cb;
}

// Обробка вхідного розпарсеного повідомлення HEARTBEAT
void mavlink_monitor_handle_heartbeat(mavlink_monitor_t* mon, uint8_t sysid, uint8_t compid,
                                      uint8_t type, uint8_t autopilot, uint8_t base_mode,
                                      uint32_t custom_mode, uint8_t system_status) {
    uint64_t now = get_monotonic_ms();
    int empty_slot = -1;

    // Пошук вузла в таблиці за парою (sysid, compid)
    for (int i = 0; i < MAX_TRACKED_NODES; ++i) {
        if (mon->nodes[i].is_active &&
            mon->nodes[i].system_id == sysid &&
            mon->nodes[i].component_id == compid) {
            
            mon->nodes[i].type = type;
            mon->nodes[i].autopilot = autopilot;
            mon->nodes[i].base_mode = base_mode;
            mon->nodes[i].custom_mode = custom_mode;
            mon->nodes[i].system_status = system_status;
            mon->nodes[i].last_heartbeat_ms = now;

            // Якщо зв'язок відновився після деградації або обриву
            if (mon->nodes[i].state != NODE_LINK_ONLINE) {
                mon->nodes[i].state = NODE_LINK_ONLINE;
                if (mon->on_failsafe_event) {
                    mon->on_failsafe_event(sysid, compid, NODE_LINK_ONLINE);
                }
            }
            return;
        }

        if (!mon->nodes[i].is_active && empty_slot == -1) {
            empty_slot = i;
        }
    }

    // Реєстрація нового раніше невідомого вузла
    if (empty_slot != -1) {
        tracked_node_t* node = &mon->nodes[empty_slot];
        node->is_active = true;
        node->system_id = sysid;
        node->component_id = compid;
        node->type = type;
        node->autopilot = autopilot;
        node->base_mode = base_mode;
        node->custom_mode = custom_mode;
        node->system_status = system_status;
        node->last_heartbeat_ms = now;
        node->state = NODE_LINK_ONLINE;

        if (mon->on_failsafe_event) {
            mon->on_failsafe_event(sysid, compid, NODE_LINK_ONLINE);
        }
    }
}

// Періодичний крок оновлення таймерів (виклик із головного циклу)
void mavlink_monitor_tick(mavlink_monitor_t* mon,
                          void (*send_hb_fn)(uint8_t sysid, uint8_t compid, uint8_t type,
                                            uint8_t autopilot, uint8_t base_mode,
                                            uint32_t custom_mode, uint8_t system_status)) {
    uint64_t now = get_monotonic_ms();

    // 1. Трансляція власного HEARTBEAT з частотою 1 Гц
    if (now - mon->last_tx_ms >= HEARTBEAT_PERIOD_MS) {
        mon->last_tx_ms = now;
        if (send_hb_fn) {
            // Прапорці базового режиму: ARMED (0x80) | STABILIZE (0x10) | CUSTOM (0x01)
            uint8_t base_mode = 0x80 | 0x10 | 0x01;
            uint32_t custom_mode = 0x00030000; // PX4 POSCTL
            uint8_t system_status = 4;          // MAV_STATE_ACTIVE
            send_hb_fn(mon->my_sysid, mon->my_compid, mon->my_type,
                       mon->my_autopilot, base_mode, custom_mode, system_status);
        }
    }

    // 2. Перевірка сторожових таймерів для всіх активних вузлів
    for (int i = 0; i < MAX_TRACKED_NODES; ++i) {
        if (!mon->nodes[i].is_active) continue;

        uint64_t elapsed_ms = now - mon->nodes[i].last_heartbeat_ms;

        if (elapsed_ms >= HEARTBEAT_LOST_TIMEOUT_MS) {
            if (mon->nodes[i].state != NODE_LINK_LOST) {
                mon->nodes[i].state = NODE_LINK_LOST;
                if (mon->on_failsafe_event) {
                    mon->on_failsafe_event(mon->nodes[i].system_id,
                                           mon->nodes[i].component_id,
                                           NODE_LINK_LOST);
                }
            }
        } else if (elapsed_ms >= HEARTBEAT_WARN_TIMEOUT_MS) {
            if (mon->nodes[i].state == NODE_LINK_ONLINE) {
                mon->nodes[i].state = NODE_LINK_WARNING;
                if (mon->on_failsafe_event) {
                    mon->on_failsafe_event(mon->nodes[i].system_id,
                                           mon->nodes[i].component_id,
                                           NODE_LINK_WARNING);
                }
            }
        }
    }
}
