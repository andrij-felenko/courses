#ifndef GOSSIP_DISSEMINATOR_H
#define GOSSIP_DISSEMINATOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    GOSSIP_OK = 0,
    GOSSIP_ERR_INVALID_PARAM = -1,
    GOSSIP_ERR_BUFFER_OVERFLOW = -2,
    GOSSIP_ERR_NODE_UNKNOWN = -3,
    GOSSIP_ERR_STALE_VERSION = -4,
    GOSSIP_ERR_CHECKSUM_MISMATCH = -5,
    GOSSIP_ERR_MTU_EXCEEDED = -6,
    GOSSIP_ERR_NOT_ACTIVE = -7
} GossipStatus;

typedef struct GossipInstance GossipInstance;

typedef struct {
    uint32_t cluster_id;
    uint32_t local_node_id;
    uint16_t bind_port;
    uint32_t fanout_k;                 /* Кількість випадкових партнерів у раунді (зазвичай 3) */
    uint32_t gossip_interval_ms;        /* Інтервал раунду чуток (зазвичай 100-200 мс) */
    uint32_t anti_entropy_interval_ms; /* Інтервал фонової анти-ентропії (зазвичай 1000 мс) */
    uint32_t tombstone_grace_sec;      /* Час утримання надгробків перед GC (зазвичай 86400 с) */
    size_t max_packet_size;            /* Максимальний розмір UDP-пакета (зазвичай 1400 байтів) */
} GossipConfig;

typedef void (*GossipStateChangeCallback)(
    uint32_t node_id,
    const char *key,
    const char *value,
    uint64_t version,
    bool is_tombstone,
    void *user_ctx
);

/* Створення та запуск екземпляра рушія */
GossipStatus gossip_create(const GossipConfig *config, GossipInstance **out_instance);
GossipStatus gossip_start(GossipInstance *instance);
GossipStatus gossip_stop(GossipInstance *instance);
void gossip_destroy(GossipInstance *instance);

/* Реєстрація зворотного виклику для реакції на оновлення стану */
GossipStatus gossip_subscribe(GossipInstance *instance, GossipStateChangeCallback cb, void *user_ctx);

/* Публікація нового значення (створює нову монотонну версію та запускає чутку) */
GossipStatus gossip_set_value(GossipInstance *instance, const char *key, const char *value, size_t val_len);

/* Видалення ключа (публікація надгробка / Tombstone) */
GossipStatus gossip_delete_key(GossipInstance *instance, const char *key);

/* Отримання актуального значення ключа конкретного вузла */
GossipStatus gossip_get_value(
    GossipInstance *instance,
    uint32_t node_id,
    const char *key,
    char *out_val,
    size_t val_buf_size,
    uint64_t *out_version
);

#ifdef __cplusplus
}
#endif

#endif /* GOSSIP_DISSEMINATOR_H */
