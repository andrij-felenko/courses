#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 4
#define LOG_BUFFER_SIZE 64

// Типи системних подій
typedef enum {
    EVENT_NONE = 0,
    EVENT_FLASH_ERASE_START,
    EVENT_FLASH_ERASE_DONE,
    EVENT_MOTOR_START,
    EVENT_MOTOR_OVERCURRENT,
    EVENT_SUPPLY_VOLTAGE_DROP,
    EVENT_EMERGENCY_SHUTDOWN
} event_type_t;

// Векторний логічний годинник
typedef struct {
    uint32_t v[MAX_NODES];
} vector_clock_t;

// Запис події в журналі
typedef struct {
    uint8_t        node_id;        // Ідентифікатор вузла (0 .. MAX_NODES-1)
    uint64_t       phys_time_us;   // Фізичний монотонний час (мкс)
    vector_clock_t vclock;         // Логічний векторний час Лампорта
    event_type_t   type;           // Тип події
    int32_t        payload;        // Числові дані (наприклад, напруга в мВ або струм в мА)
} log_entry_t;

// Контекст локального вузла
typedef struct {
    uint8_t        node_id;
    vector_clock_t current_clock;
    log_entry_t    buffer[LOG_BUFFER_SIZE];
    uint16_t       head;
    uint16_t       count;
} node_context_t;

// Результат порівняння причинності
typedef enum {
    CAUSALITY_BEFORE,      // A причинно передувало B (A -> B)
    CAUSALITY_AFTER,       // B причинно передувало A (B -> A)
    CAUSALITY_CONCURRENT   // Події незалежні / конкурентні (A || B)
} causality_result_t;

// Ініціалізація контексту вузла
void node_init(node_context_t *ctx, uint8_t node_id) {
    if (!ctx || node_id >= MAX_NODES) return;
    memset(ctx, 0, sizeof(node_context_t));
    ctx->node_id = node_id;
}

// Фіксація локальної події
void node_log_event(node_context_t *ctx, uint64_t now_us, event_type_t type, int32_t payload) {
    if (!ctx) return;

    // Крок 1 алгоритму векторного часу: інкремент власного лічильника
    ctx->current_clock.v[ctx->node_id]++;

    // Запис у кільцевий буфер
    uint16_t idx = (ctx->head + ctx->count) % LOG_BUFFER_SIZE;
    if (ctx->count == LOG_BUFFER_SIZE) {
        ctx->head = (ctx->head + 1) % LOG_BUFFER_SIZE; // Перезапис найстарішого
    } else {
        ctx->count++;
    }

    log_entry_t *entry = &ctx->buffer[idx];
    entry->node_id = ctx->node_id;
    entry->phys_time_us = now_us;
    entry->vclock = ctx->current_clock;
    entry->type = type;
    entry->payload = payload;
}

// Оновлення вектора при отриманні мережевого повідомлення (наприклад, з шини CAN)
void node_receive_message_clock(node_context_t *ctx, const vector_clock_t *msg_clock) {
    if (!ctx || !msg_clock) return;

    // Крок 2 алгоритму: покомпонентний максимум
    for (uint8_t i = 0; i < MAX_NODES; i++) {
        if (msg_clock->v[i] > ctx->current_clock.v[i]) {
            ctx->current_clock.v[i] = msg_clock->v[i];
        }
    }
    // Інкремент власного індексу при обробці вхідного повідомлення
    ctx->current_clock.v[ctx->node_id]++;
}

// Порівняння двох векторних годинників для встановлення причинно-наслідкового зв'язку
causality_result_t compare_causality(const vector_clock_t *a, const vector_clock_t *b) {
    bool a_has_less = false;
    bool b_has_less = false;

    for (uint8_t i = 0; i < MAX_NODES; i++) {
        if (a->v[i] < b->v[i]) {
            a_has_less = true;
        } else if (a->v[i] > b->v[i]) {
            b_has_less = true;
        }
    }

    if (a_has_less && !b_has_less) {
        return CAUSALITY_BEFORE; // Всі компоненти a <= b і є хоча б одна < (A -> B)
    }
    if (b_has_less && !a_has_less) {
        return CAUSALITY_AFTER;  // Всі компоненти b <= a і є хоча б одна < (B -> A)
    }
    return CAUSALITY_CONCURRENT; // Події незалежні / конкурентні (A || B)
}

// Аналізатор крос-доменної кореляції між програмною подією та падінням напруги
// Повертає true, якщо підтверджено, що програмна дія викликала просадку напруги
bool analyze_power_drop_correlation(const log_entry_t *prog_event,
                                    const uint16_t *voltage_samples_mv,
                                    uint16_t sample_count,
                                    uint64_t sample_start_us,
                                    uint32_t sample_period_us,
                                    uint16_t threshold_drop_mv,
                                    int64_t *out_latency_us) {
    if (!prog_event || !voltage_samples_mv || sample_count == 0) return false;

    int64_t min_voltage_idx = -1;
    uint16_t min_voltage = 0xFFFF;

    // Пошук точки найглибшої просадки напруги
    for (uint16_t i = 0; i < sample_count; i++) {
        if (voltage_samples_mv[i] < min_voltage) {
            min_voltage = voltage_samples_mv[i];
            min_voltage_idx = i;
        }
    }

    if (min_voltage_idx < 0) return false;

    uint64_t drop_phys_time_us = sample_start_us + ((uint64_t)min_voltage_idx * sample_period_us);
    int64_t latency = (int64_t)drop_phys_time_us - (int64_t)prog_event->phys_time_us;
    if (out_latency_us) *out_latency_us = latency;

    // Якщо просадка сталася в інтервалі від 0 до 5000 мкс після події — підтверджуємо зв'язок
    if (latency >= 0 && latency <= 5000 && min_voltage <= threshold_drop_mv) {
        return true;
    }
    return false;
}
