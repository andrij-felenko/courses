// gateway_core.h - Ядро автономного шлюзу на чистому C (C99/C11)
#ifndef GATEWAY_CORE_H
#define GATEWAY_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_METRICS         64
#define MAX_TOPIC_LEN       64
#define MAX_PAYLOAD_LEN     256
#define MAX_QUEUE_DEPTH     512
#define BATCH_DRAIN_LIMIT   16

// Рівні пріоритету повідомлень
typedef enum {
    PRIO_TELEMETRY = 0,     // Регулярні точки (витісняються першими)
    PRIO_EVENT     = 1,     // Зміна стану / Команди
    PRIO_ALARM     = 2      // Критичні аварії (не видаляються ніколи)
} MessagePriority;

// Стани висхідного каналу WAN
typedef enum {
    WAN_ONLINE_STREAMING,   // Пряма публікація в MQTT
    WAN_OFFLINE_BUFFERING,  // Збереження у чергу на диску
    WAN_DRAINING_SYNC       // Порційна передача накопиченої черги
} WanState;

// Запис черги Store-and-Forward
typedef struct {
    uint32_t id;
    uint64_t timestamp_ms;
    MessagePriority priority;
    char topic[MAX_TOPIC_LEN];
    char payload[MAX_PAYLOAD_LEN];
    bool in_flight;
} QueueRecord;

// Стан фізичної величини в пам'яті
typedef struct {
    uint16_t metric_id;
    float current_val;
    float last_sent_val;
    uint64_t last_sampled_time_ms;
    uint64_t last_sent_time_ms;
    float deadband;
    uint64_t max_interval_ms;
    bool is_valid;
} MetricEntry;

// Контекст шлюзу
typedef struct {
    MetricEntry metrics[MAX_METRICS];
    size_t metric_count;
    
    QueueRecord queue[MAX_QUEUE_DEPTH];
    size_t queue_count;
    uint32_t next_record_id;
    
    WanState wan_state;
    bool emergency_shutdown_latched;
    float pressure_threshold_bar;
} GatewayContext;

// Публічний API
void gateway_init(GatewayContext *ctx, float pressure_threshold);
void gateway_ingest_modbus_point(GatewayContext *ctx, uint16_t metric_id, 
                                 float value, uint64_t now_ms);
void gateway_process_lorawan_frame(GatewayContext *ctx, uint32_t dev_addr, 
                                   const uint8_t *payload, size_t len, uint64_t now_ms);
void gateway_set_wan_online(GatewayContext *ctx, bool is_online);
void gateway_poll(GatewayContext *ctx, uint64_t now_ms);

#endif // GATEWAY_CORE_H
