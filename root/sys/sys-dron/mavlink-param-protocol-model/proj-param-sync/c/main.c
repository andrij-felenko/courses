#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define MAX_PARAMS_CAPACITY 2048
#define PARAM_ID_LEN 16
#define MAX_LIST_RETRIES 3
#define MAX_HOLE_RETRIES 5
#define BURST_TIMEOUT_MS 500
#define READ_TIMEOUT_MS 800
#define LIST_TIMEOUT_MS 1000

typedef enum {
    SYNC_STATE_IDLE,
    SYNC_STATE_REQUEST_LIST,
    SYNC_STATE_RECEIVING_BURST,
    SYNC_STATE_RESOLVING_HOLES,
    SYNC_STATE_COMPLETED,
    SYNC_STATE_FAILED
} param_sync_state_t;

typedef struct {
    char     id[PARAM_ID_LEN + 1];
    float    raw_value;
    uint8_t  type;
    uint16_t index;
    bool     valid;
} param_entry_t;

typedef struct {
    uint8_t target_sys;
    uint8_t target_comp;
    param_sync_state_t state;

    uint16_t param_count;
    uint16_t received_count;

    // Бітова маска отриманих індексів (2048 бітів = 256 байтів)
    uint8_t  index_bitmask[MAX_PARAMS_CAPACITY / 8];
    param_entry_t entries[MAX_PARAMS_CAPACITY];

    // Змінні таймерів і повторів
    uint32_t last_packet_time_ms;
    uint16_t current_hole_index;
    uint8_t  retry_count;
} param_sync_engine_t;

// Встановлення біта в масці
static inline void bitmask_set(uint8_t *mask, uint16_t index) {
    mask[index / 8] |= (uint8_t)(1u << (index % 8));
}

// Перевірка стану біта в масці
static inline bool bitmask_test(const uint8_t *mask, uint16_t index) {
    return (mask[index / 8] & (uint8_t)(1u << (index % 8))) != 0;
}

// Ініціалізація структури рушія
void param_sync_init(param_sync_engine_t *eng, uint8_t sys_id, uint8_t comp_id) {
    memset(eng, 0, sizeof(param_sync_engine_t));
    eng->target_sys = sys_id;
    eng->target_comp = comp_id;
    eng->state = SYNC_STATE_IDLE;
}

// Зовнішні інтерфейси відправлення MAVLink-повідомлень у фізичний драйвер
extern void send_mavlink_request_list(uint8_t sys_id, uint8_t comp_id);
extern void send_mavlink_request_read(uint8_t sys_id, uint8_t comp_id, int16_t index);

// Запуск повної синхронізації
void param_sync_start(param_sync_engine_t *eng, uint32_t current_time_ms) {
    memset(eng->index_bitmask, 0, sizeof(eng->index_bitmask));
    eng->received_count = 0;
    eng->param_count = 0;
    eng->state = SYNC_STATE_REQUEST_LIST;
    eng->retry_count = 0;
    eng->last_packet_time_ms = current_time_ms;

    send_mavlink_request_list(eng->target_sys, eng->target_comp);
}

// Обробник вхідного повідомлення PARAM_VALUE
void param_sync_on_param_value(param_sync_engine_t *eng,
                               const char wire_id[16],
                               float val,
                               uint8_t type,
                               uint16_t count,
                               uint16_t index,
                               uint32_t current_time_ms) {
    if (index >= MAX_PARAMS_CAPACITY || count > MAX_PARAMS_CAPACITY) {
        return;
    }

    eng->last_packet_time_ms = current_time_ms;

    if (eng->param_count == 0 && count > 0) {
        eng->param_count = count;
    }

    // Якщо цей індекс ще не було зафіксовано в масці
    if (!bitmask_test(eng->index_bitmask, index)) {
        bitmask_set(eng->index_bitmask, index);
        eng->received_count++;

        param_entry_t *e = &eng->entries[index];
        memcpy(e->id, wire_id, PARAM_ID_LEN);
        e->id[PARAM_ID_LEN] = '\0';
        e->raw_value = val;
        e->type = type;
        e->index = index;
        e->valid = true;
    }

    // Перемикання станів автомата
    if (eng->state == SYNC_STATE_REQUEST_LIST) {
        eng->state = SYNC_STATE_RECEIVING_BURST;
    }

    // Якщо ми в режимі усунення прогалин і прийшов поточний очікуваний індекс
    if (eng->state == SYNC_STATE_RESOLVING_HOLES && index == eng->current_hole_index) {
        eng->retry_count = 0;
    }
}

// Пошук найближчого нульового біта в масці
static int32_t find_next_hole(const param_sync_engine_t *eng, uint16_t start_idx) {
    for (uint16_t i = start_idx; i < eng->param_count; ++i) {
        if (!bitmask_test(eng->index_bitmask, i)) {
            return (int32_t)i;
        }
    }
    return -1;
}

// Неблокуюче періодичне опитування стану (викликається в головному циклі)
void param_sync_poll(param_sync_engine_t *eng, uint32_t current_time_ms) {
    switch (eng->state) {
        case SYNC_STATE_REQUEST_LIST:
            if (current_time_ms - eng->last_packet_time_ms > LIST_TIMEOUT_MS) {
                if (eng->retry_count < MAX_LIST_RETRIES) {
                    eng->retry_count++;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_list(eng->target_sys, eng->target_comp);
                } else {
                    eng->state = SYNC_STATE_FAILED;
                }
            }
            break;

        case SYNC_STATE_RECEIVING_BURST:
            // Перевірка повного отримання всіх елементів
            if (eng->received_count >= eng->param_count && eng->param_count > 0) {
                eng->state = SYNC_STATE_COMPLETED;
                break;
            }
            // Перевірка затишшя потоку
            if (current_time_ms - eng->last_packet_time_ms > BURST_TIMEOUT_MS) {
                int32_t first_hole = find_next_hole(eng, 0);
                if (first_hole >= 0) {
                    eng->state = SYNC_STATE_RESOLVING_HOLES;
                    eng->current_hole_index = (uint16_t)first_hole;
                    eng->retry_count = 0;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_read(eng->target_sys, eng->target_comp, (int16_t)first_hole);
                } else {
                    eng->state = SYNC_STATE_COMPLETED;
                }
            }
            break;

        case SYNC_STATE_RESOLVING_HOLES:
            // Якщо поточну дірку успішно закрито
            if (bitmask_test(eng->index_bitmask, eng->current_hole_index)) {
                int32_t next = find_next_hole(eng, eng->current_hole_index + 1);
                if (next >= 0) {
                    eng->current_hole_index = (uint16_t)next;
                    eng->retry_count = 0;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_read(eng->target_sys, eng->target_comp, (int16_t)next);
                } else {
                    eng->state = (eng->received_count >= eng->param_count) ?
                                  SYNC_STATE_COMPLETED : SYNC_STATE_FAILED;
                }
            } else if (current_time_ms - eng->last_packet_time_ms > READ_TIMEOUT_MS) {
                if (eng->retry_count < MAX_HOLE_RETRIES) {
                    eng->retry_count++;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_read(eng->target_sys, eng->target_comp, (int16_t)eng->current_hole_index);
                } else {
                    // Вичерпано ліміт спроб для окремого індексу
                    eng->state = SYNC_STATE_FAILED;
                }
            }
            break;

        case SYNC_STATE_IDLE:
        case SYNC_STATE_COMPLETED:
        case SYNC_STATE_FAILED:
            break;
    }
}
