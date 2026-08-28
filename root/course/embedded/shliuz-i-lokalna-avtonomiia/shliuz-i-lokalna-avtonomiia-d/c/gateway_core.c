// gateway_core.c - Реалізація ядра шлюзу
#include "gateway_core.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

// Локальний апаратний виклик (симуляція відсікання аварійного реле)
static void hardware_set_emergency_interlock(bool trigger) {
    // У реальному коді: запис у GPIO або відправка Modbus команди зупинки
    (void)trigger;
}

// Пряма відправка в мережевий стек MQTT (повертає true при успішній публікації)
static bool network_mqtt_publish(const char *topic, const char *payload, MessagePriority prio) {
    (void)topic;
    (void)payload;
    (void)prio;
    // У реальному коді: виклик mg_mqtt_pub() або esp_mqtt_client_publish()
    return true;
}

void gateway_init(GatewayContext *ctx, float pressure_threshold) {
    memset(ctx, 0, sizeof(GatewayContext));
    ctx->pressure_threshold_bar = pressure_threshold;
    ctx->wan_state = WAN_OFFLINE_BUFFERING;
    ctx->next_record_id = 1;
}

// Додавання повідомлення в чергу Store-and-Forward із захистом від переповнення
static void enqueue_record(GatewayContext *ctx, MessagePriority prio, 
                           const char *topic, const char *payload, uint64_t now_ms) {
    // Якщо черга заповнена, витісняємо найстаріший запис низького пріоритету
    if (ctx->queue_count >= MAX_QUEUE_DEPTH) {
        size_t evict_idx = MAX_QUEUE_DEPTH;
        for (size_t i = 0; i < ctx->queue_count; ++i) {
            if (ctx->queue[i].priority == PRIO_TELEMETRY) {
                evict_idx = i;
                break;
            }
        }
        if (evict_idx == MAX_QUEUE_DEPTH) {
            // Якщо немає телеметрії, шукаємо звичайні події
            for (size_t i = 0; i < ctx->queue_count; ++i) {
                if (ctx->queue[i].priority == PRIO_EVENT) {
                    evict_idx = i;
                    break;
                }
            }
        }
        
        // Зсуваємо чергу, якщо знайшли кандидата на видалення
        if (evict_idx < MAX_QUEUE_DEPTH) {
            memmove(&ctx->queue[evict_idx], &ctx->queue[evict_idx + 1], 
                    (ctx->queue_count - evict_idx - 1) * sizeof(QueueRecord));
            ctx->queue_count--;
        } else {
            // Черга забита виключно аваріями - не можемо записати
            return;
        }
    }

    QueueRecord *rec = &ctx->queue[ctx->queue_count++];
    rec->id = ctx->next_record_id++;
    rec->timestamp_ms = now_ms;
    rec->priority = prio;
    rec->in_flight = false;
    snprintf(rec->topic, sizeof(rec->topic), "%s", topic);
    snprintf(rec->payload, sizeof(rec->payload), "%s", payload);
}

// Локальний швидкий шлях (Fast-Path Rule Engine)
static void evaluate_fast_path_rules(GatewayContext *ctx, uint16_t metric_id, 
                                     float value, uint64_t now_ms) {
    // Правило аварії: Тиск у паровому котлі (Metric ID 100)
    if (metric_id == 100) {
        if (value >= ctx->pressure_threshold_bar) {
            if (!ctx->emergency_shutdown_latched) {
                ctx->emergency_shutdown_latched = true;
                hardware_set_emergency_interlock(true);

                char alarm_payload[MAX_PAYLOAD_LEN];
                snprintf(alarm_payload, sizeof(alarm_payload), 
                         "{\"event\":\"CRITICAL_OVERPRESSURE\",\"val\":%.2f,\"ts\":%llu}", 
                         value, (unsigned long long)now_ms);
                
                enqueue_record(ctx, PRIO_ALARM, "plant/boiler/alarm", alarm_payload, now_ms);
            }
        } else if (value < (ctx->pressure_threshold_bar - 0.5f)) {
            // Гістерезис 0.5 bar для скидання аварійного прапорця
            if (ctx->emergency_shutdown_latched) {
                ctx->emergency_shutdown_latched = false;
                hardware_set_emergency_interlock(false);
            }
        }
    }
}

// Обробка показань Modbus RTU
void gateway_ingest_modbus_point(GatewayContext *ctx, uint16_t metric_id, 
                                 float value, uint64_t now_ms) {
    MetricEntry *entry = NULL;
    for (size_t i = 0; i < ctx->metric_count; ++i) {
        if (ctx->metrics[i].metric_id == metric_id) {
            entry = &ctx->metrics[i];
            break;
        }
    }

    if (!entry) {
        if (ctx->metric_count >= MAX_METRICS) return;
        entry = &ctx->metrics[ctx->metric_count++];
        entry->metric_id = metric_id;
        entry->deadband = 0.2f;
        entry->max_interval_ms = 300000; // 5 хв
        entry->is_valid = false;
    }

    entry->current_val = value;
    entry->last_sampled_time_ms = now_ms;

    // 1. Негайне виконання правил захисту (< 1 мс)
    evaluate_fast_path_rules(ctx, metric_id, value, now_ms);

    // 2. Апертурна фільтрація (Deadband)
    bool should_send = false;
    if (!entry->is_valid) {
        should_send = true;
        entry->is_valid = true;
    } else {
        float delta = fabsf(value - entry->last_sent_val);
        if (delta >= entry->deadband) {
            should_send = true;
        } else if ((now_ms - entry->last_sent_time_ms) >= entry->max_interval_ms) {
            should_send = true; // Серцебиття
        }
    }

    if (should_send) {
        entry->last_sent_val = value;
        entry->last_sent_time_ms = now_ms;

        char topic[MAX_TOPIC_LEN];
        char payload[MAX_PAYLOAD_LEN];
        snprintf(topic, sizeof(topic), "plant/sensor/%u/telemetry", metric_id);
        snprintf(payload, sizeof(payload), "{\"val\":%.2f,\"ts\":%llu}", 
                 value, (unsigned long long)now_ms);

        if (ctx->wan_state == WAN_ONLINE_STREAMING && ctx->queue_count == 0) {
            // Канал вільний - публікуємо напряму
            if (!network_mqtt_publish(topic, payload, PRIO_TELEMETRY)) {
                // При невдачі перемикаємося в офлайн і кладемо в чергу
                ctx->wan_state = WAN_OFFLINE_BUFFERING;
                enqueue_record(ctx, PRIO_TELEMETRY, topic, payload, now_ms);
            }
        } else {
            // Канал офлайн або йде злив черги - зберігаємо у Store-and-Forward
            enqueue_record(ctx, PRIO_TELEMETRY, topic, payload, now_ms);
        }
    }
}

// Декодування пакета LoRaWAN Cayenne LPP
void gateway_process_lorawan_frame(GatewayContext *ctx, uint32_t dev_addr, 
                                   const uint8_t *payload, size_t len, uint64_t now_ms) {
    if (len < 4) return; // Мінімум 1 канал: Channel(1) + Type(1) + Val(2)

    size_t offset = 0;
    while (offset + 2 <= len) {
        uint8_t channel = payload[offset++];
        uint8_t type = payload[offset++];

        if (type == 0x67 && (offset + 2 <= len)) { // Температура (0.1 °C знакове)
            int16_t raw_temp = (int16_t)((payload[offset] << 8) | payload[offset + 1]);
            offset += 2;
            float temperature = raw_temp * 0.1f;
            uint16_t synthetic_id = (uint16_t)((dev_addr & 0xFF) * 100 + channel);
            gateway_ingest_modbus_point(ctx, synthetic_id, temperature, now_ms);
        } else {
            break; // Невідомий тип для стислості
        }
    }
}

void gateway_set_wan_online(GatewayContext *ctx, bool is_online) {
    if (is_online) {
        if (ctx->wan_state == WAN_OFFLINE_BUFFERING) {
            ctx->wan_state = (ctx->queue_count > 0) ? WAN_DRAINING_SYNC : WAN_ONLINE_STREAMING;
        }
    } else {
        ctx->wan_state = WAN_OFFLINE_BUFFERING;
    }
}

// Періодичний виклик зливу черги
void gateway_poll(GatewayContext *ctx, uint64_t now_ms) {
    (void)now_ms;
    if (ctx->wan_state != WAN_DRAINING_SYNC) return;

    if (ctx->queue_count == 0) {
        ctx->wan_state = WAN_ONLINE_STREAMING;
        return;
    }

    size_t batch_size = (ctx->queue_count < BATCH_DRAIN_LIMIT) ? ctx->queue_count : BATCH_DRAIN_LIMIT;
    size_t acked_count = 0;

    for (size_t i = 0; i < batch_size; ++i) {
        QueueRecord *rec = &ctx->queue[i];
        if (network_mqtt_publish(rec->topic, rec->payload, rec->priority)) {
            acked_count++;
        } else {
            // Збій висхідного каналу під час зливу
            ctx->wan_state = WAN_OFFLINE_BUFFERING;
            break;
        }
    }

    // Видаляємо успішно відправлені записи
    if (acked_count > 0) {
        memmove(&ctx->queue[0], &ctx->queue[acked_count], 
                (ctx->queue_count - acked_count) * sizeof(QueueRecord));
        ctx->queue_count -= acked_count;
    }
}
