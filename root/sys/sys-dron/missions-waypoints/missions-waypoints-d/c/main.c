#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MISSION_MAX_ITEMS           500u
#define MISSION_TIMEOUT_MS          1500u
#define MISSION_MAX_RETRIES         5u

typedef enum {
    MISSION_STATE_IDLE = 0,
    MISSION_STATE_UPLOADING,
    MISSION_STATE_DOWNLOADING,
    MISSION_STATE_ACTIVE,
    MISSION_STATE_PAUSED
} mission_fsm_state_t;

typedef struct __attribute__((packed)) {
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint16_t seq;
    uint16_t command;
    uint8_t frame;
    uint8_t current;
    uint8_t autocontinue;
    uint8_t mission_type;
} mission_item_t;

typedef struct {
    mission_fsm_state_t state;
    mission_item_t active_items[MISSION_MAX_ITEMS];
    mission_item_t staging_items[MISSION_MAX_ITEMS];
    uint16_t active_count;
    uint16_t staging_count;
    uint16_t transfer_seq;
    uint16_t current_active_seq;
    uint32_t last_transfer_time_ms;
    uint8_t retry_count;
    uint8_t partner_sysid;
    uint8_t partner_compid;
} mission_manager_t;

// Зовнішні функції надсилання MAVLink повідомлень
extern void mavlink_send_mission_request_int(uint8_t sysid, uint8_t compid, uint16_t seq);
extern void mavlink_send_mission_ack(uint8_t sysid, uint8_t compid, uint8_t result_type);
extern void mavlink_send_mission_current(uint16_t current_seq);
extern void mavlink_send_mission_item_reached(uint16_t reached_seq);

void mission_manager_init(mission_manager_t *mgr) {
    memset(mgr, 0, sizeof(mission_manager_t));
    mgr->state = MISSION_STATE_IDLE;
    mgr->active_count = 0;
    mgr->current_active_seq = 0;
}

// Обробка вхідного кадру MISSION_COUNT від GCS
void mission_manager_on_count(mission_manager_t *mgr, uint8_t sysid, uint8_t compid, uint16_t count, uint32_t now_ms) {
    if (count > MISSION_MAX_ITEMS) {
        mavlink_send_mission_ack(sysid, compid, 4); // MAV_MISSION_NO_SPACE
        return;
    }

    if (count == 0) {
        // Повне очищення місії
        mgr->active_count = 0;
        mgr->current_active_seq = 0;
        mgr->state = MISSION_STATE_IDLE;
        mavlink_send_mission_ack(sysid, compid, 0); // MAV_MISSION_ACCEPTED
        return;
    }

    mgr->state = MISSION_STATE_UPLOADING;
    mgr->staging_count = count;
    mgr->transfer_seq = 0;
    mgr->retry_count = 0;
    mgr->partner_sysid = sysid;
    mgr->partner_compid = compid;
    mgr->last_transfer_time_ms = now_ms;

    // Запитуємо перший елемент seq = 0
    mavlink_send_mission_request_int(sysid, compid, 0);
}

// Обробка вхідного дескриптора точки MISSION_ITEM_INT
void mission_manager_on_item(mission_manager_t *mgr, const mission_item_t *item, uint32_t now_ms) {
    if (mgr->state != MISSION_STATE_UPLOADING) {
        return;
    }

    if (item->seq != mgr->transfer_seq) {
        // Порушення черговості — повторюємо запит актуального індексу
        mavlink_send_mission_request_int(mgr->partner_sysid, mgr->partner_compid, mgr->transfer_seq);
        return;
    }

    // Зберігаємо точку в буфері
    mgr->staging_items[mgr->transfer_seq] = *item;
    mgr->transfer_seq++;
    mgr->retry_count = 0;
    mgr->last_transfer_time_ms = now_ms;

    if (mgr->transfer_seq < mgr->staging_count) {
        // Запитуємо наступний елемент
        mavlink_send_mission_request_int(mgr->partner_sysid, mgr->partner_compid, mgr->transfer_seq);
    } else {
        // Усі точки отримано — атомарна фіксація
        memcpy(mgr->active_items, mgr->staging_items, mgr->staging_count * sizeof(mission_item_t));
        mgr->active_count = mgr->staging_count;
        mgr->current_active_seq = (mgr->active_count > 1) ? 1 : 0;
        mgr->state = MISSION_STATE_IDLE;

        mavlink_send_mission_ack(mgr->partner_sysid, mgr->partner_compid, 0); // MAV_MISSION_ACCEPTED
        mavlink_send_mission_current(mgr->current_active_seq);
    }
}

// Періодичний сторожовий таймер транзакцій (виклик з частотою 10-50 Гц)
void mission_manager_tick(mission_manager_t *mgr, uint32_t now_ms) {
    if (mgr->state == MISSION_STATE_UPLOADING) {
        if ((now_ms - mgr->last_transfer_time_ms) >= MISSION_TIMEOUT_MS) {
            if (mgr->retry_count < MISSION_MAX_RETRIES) {
                mgr->retry_count++;
                mgr->last_transfer_time_ms = now_ms;
                mavlink_send_mission_request_int(mgr->partner_sysid, mgr->partner_compid, mgr->transfer_seq);
            } else {
                // Вичерпано ліміт спроб — скасування транзакції
                mgr->state = MISSION_STATE_IDLE;
                mavlink_send_mission_ack(mgr->partner_sysid, mgr->partner_compid, 15); // MAV_MISSION_OPERATION_CANCELLED
            }
        }
    }
}

// Перемикання на наступну точку після завершення поточної
bool mission_manager_advance(mission_manager_t *mgr) {
    if (mgr->active_count == 0 || mgr->current_active_seq >= mgr->active_count - 1) {
        return false;
    }

    mavlink_send_mission_item_reached(mgr->current_active_seq);
    mgr->current_active_seq++;
    mavlink_send_mission_current(mgr->current_active_seq);
    return true;
}
