/* gcs_focus_manager.c — Логіка блокування цілі на пульті оператора */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint8_t         focused_target_id;
    bool            is_armed;
    uint32_t        received_token;
    uint32_t        selection_deadline_ms;
    char            target_name[16];
} gcs_target_lock_t;

void gcs_lock_init(gcs_target_lock_t *lock) {
    memset(lock, 0, sizeof(gcs_target_lock_t));
    lock->is_armed = false;
}

/* Обробка кліку оператора на картку вибору апарата */
void gcs_select_vehicle(gcs_target_lock_t *lock, uint8_t target_id, const char *name) {
    lock->focused_target_id = target_id;
    lock->is_armed = false; /* Чекаємо квитанції від борту */
    lock->received_token = 0;
    strncpy(lock->target_name, name, sizeof(lock->target_name) - 1);
}

/* Фіксація підтвердження селекції (SELECT_ACK) */
void gcs_on_select_ack(gcs_target_lock_t *lock, uint8_t from_id, uint32_t token, uint16_t window_ms, uint32_t now_ms) {
    if (from_id == lock->focused_target_id) {
        lock->is_armed = true;
        lock->received_token = token;
        lock->selection_deadline_ms = now_ms + window_ms;
    }
}

/* Безпечна генерація команди: повертає false, якщо ціль не заблокована */
bool gcs_build_operate_packet(gcs_target_lock_t *lock, uint16_t cmd_code, sbo_packet_t *out_pkt, uint32_t now_ms) {
    if (!lock->is_armed || now_ms >= lock->selection_deadline_ms) {
        lock->is_armed = false; /* Тайм-аут вичерпано */
        return false;
    }

    memset(out_pkt, 0, sizeof(sbo_packet_t));
    out_pkt->magic = SBO_MAGIC_BYTE;
    out_pkt->msg_type = SBO_MSG_OPERATE_REQ;
    out_pkt->source_id = 0xFE; /* GCS ID */
    out_pkt->target_id = lock->focused_target_id;
    out_pkt->sbo_token = lock->received_token;
    out_pkt->cmd_code = cmd_code;

    /* Після відправки команди замок скидається локально */
    lock->is_armed = false;
    return true;
}
