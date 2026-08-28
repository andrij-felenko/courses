/*
 * state_manager.h / state_manager.c
 * Менеджер розподіленого стану IoT-вузла мовою C.
 * Побудований без динамічного виділення пам'яті (MISRA C Compliant).
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_OFFLINE_QUEUE_SIZE 32
#define MAX_TOPIC_LEN          64
#define MAX_PAYLOAD_LEN        128

typedef enum {
    CONN_STATE_DISCONNECTED = 0,
    CONN_STATE_CONNECTING,
    CONN_STATE_CONNECTED,
    CONN_STATE_SYNCING
} connection_state_t;

/* Структура конфігурації об'єкта (наприклад, розумного термостата) */
typedef struct {
    float target_temperature;
    uint16_t fan_speed_rpm;
    bool heating_enabled;
    uint32_t sequence_id; /* Монотонний лічильник версії */
} node_config_t;

/* Елемент офлайн-буфера телеметрії */
typedef struct {
    uint32_t timestamp;
    float measured_temperature;
    uint16_t current_power_watts;
    uint8_t flags;
} telemetry_entry_t;

/* Кільцевий буфер телеметрії для збереження даних під час обриву каналу */
typedef struct {
    telemetry_entry_t buffer[MAX_OFFLINE_QUEUE_SIZE];
    uint16_t head;
    uint16_t tail;
    uint16_t count;
} offline_queue_t;

/* Головний контекст агента стану */
typedef struct {
    node_config_t desired_config;
    node_config_t reported_config;
    node_config_t active_hardware_state;
    connection_state_t conn_state;
    offline_queue_t offline_queue;
    uint32_t last_sync_time;
    bool delta_pending;
} state_agent_t;

/* Ініціалізація агента стану */
void state_agent_init(state_agent_t *agent, const node_config_t *initial_cfg) {
    if (!agent || !initial_cfg) return;
    
    memcpy(&agent->desired_config, initial_cfg, sizeof(node_config_t));
    memcpy(&agent->reported_config, initial_cfg, sizeof(node_config_t));
    memcpy(&agent->active_hardware_state, initial_cfg, sizeof(node_config_t));
    
    agent->conn_state = CONN_STATE_DISCONNECTED;
    agent->offline_queue.head = 0;
    agent->offline_queue.tail = 0;
    agent->offline_queue.count = 0;
    agent->last_sync_time = 0;
    agent->delta_pending = false;
}

/* Додавання телеметрії до офлайн-черги (перетирає найстаріші при переповненні) */
bool state_agent_enqueue_telemetry(state_agent_t *agent, const telemetry_entry_t *entry) {
    if (!agent || !entry) return false;
    
    offline_queue_t *q = &agent->offline_queue;
    q->buffer[q->head] = *entry;
    q->head = (q->head + 1) % MAX_OFFLINE_QUEUE_SIZE;
    
    if (q->count < MAX_OFFLINE_QUEUE_SIZE) {
        q->count++;
    } else {
        /* Буфер заповнений: зсуваємо tail, відкидаючи найстаріший вимір */
        q->tail = (q->tail + 1) % MAX_OFFLINE_QUEUE_SIZE;
    }
    return true;
}

/* Витягнення телеметрії для відправки */
bool state_agent_dequeue_telemetry(state_agent_t *agent, telemetry_entry_t *out_entry) {
    if (!agent || !out_entry || agent->offline_queue.count == 0) return false;
    
    offline_queue_t *q = &agent->offline_queue;
    *out_entry = q->buffer[q->tail];
    q->tail = (q->tail + 1) % MAX_OFFLINE_QUEUE_SIZE;
    q->count--;
    return true;
}

/* Обробка дельти конфігурації, отриманої від хмарного сервісу Device Shadow */
bool state_agent_apply_delta(state_agent_t *agent, const node_config_t *new_desired) {
    if (!agent || !new_desired) return false;

    /* Захист від гонок станів: відкидаємо застарілі та дубльовані версії */
    if (new_desired->sequence_id <= agent->reported_config.sequence_id) {
        return false; /* Застарілий пакет, ігноруємо */
    }

    /* Фізична валідація на краю (Edge Validation) */
    if (new_desired->target_temperature < 5.0f || new_desired->target_temperature > 40.0f) {
        return false; /* Порушення безпечного діапазону температур */
    }
    if (new_desired->fan_speed_rpm > 3000) {
        return false; /* Перевищення ліміту швидкості вентилятора */
    }

    /* Оновлення бажаного стану та маркування необхідності локального застосування */
    agent->desired_config = *new_desired;
    agent->delta_pending = true;
    return true;
}

/* Синхронізація апаратного стану з бажаним (виклик у робочому циклі) */
void state_agent_reconcile_hardware(state_agent_t *agent) {
    if (!agent || !agent->delta_pending) return;

    /* Фізичний запис у залізо (наприклад, ШІМ таймера та реле) */
    agent->active_hardware_state.target_temperature = agent->desired_config.target_temperature;
    agent->active_hardware_state.fan_speed_rpm = agent->desired_config.fan_speed_rpm;
    agent->active_hardware_state.heating_enabled = agent->desired_config.heating_enabled;
    agent->active_hardware_state.sequence_id = agent->desired_config.sequence_id;

    /* Застосовано: фіксуємо reported для подальшого звіту в хмару */
    agent->reported_config = agent->active_hardware_state;
    agent->delta_pending = false;
}

/* Формування payload для публікації Reported State у хмару */
bool state_agent_build_reported_payload(const state_agent_t *agent, char *out_buf, size_t max_len) {
    if (!agent || !out_buf || max_len < 64) return false;

    /* Проста серіалізація стану (у реальному проєкті — jsmmn або cJSON) */
    int written = snprintf(out_buf, max_len,
        "{\"reported\":{\"temp\":%.1f,\"fan\":%u,\"heat\":%s,\"v\":%lu}}",
        agent->reported_config.target_temperature,
        agent->reported_config.fan_speed_rpm,
        agent->reported_config.heating_enabled ? "true" : "false",
        (unsigned long)agent->reported_config.sequence_id);

    return (written > 0 && (size_t)written < max_len);
}
