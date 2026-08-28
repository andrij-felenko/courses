#ifndef NET_ADAPTER_H
#define NET_ADAPTER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    NET_PRIO_LOW = 0,     /* Фонова телеметрія, логи */
    NET_PRIO_NORMAL = 1,  /* Регулярні виміри, звіти */
    NET_PRIO_CRITICAL = 2 /* Команди керування, аварійні зупинки */
} net_priority_t;

typedef enum {
    NET_STATE_OFFLINE,
    NET_STATE_CONNECTING,
    NET_STATE_ONLINE,
    NET_STATE_SLEEPING,
    NET_STATE_ERROR
} net_state_t;

typedef struct {
    uint16_t msg_id;
    uint8_t  payload[64];
    uint8_t  len;
    net_priority_t priority;
} net_packet_t;

/* Інтерфейс зворотного виклику для вхідних даних */
typedef void (*net_rx_callback_t)(const net_packet_t *pkt, void *user_data);

typedef struct net_adapter {
    const struct net_adapter_api *api;
    void *driver_ctx;
    net_rx_callback_t rx_cb;
    void *user_data;
} net_adapter_t;

struct net_adapter_api {
    bool (*init)(net_adapter_t *self);
    void (*poll)(net_adapter_t *self, uint32_t now_ms);
    bool (*send)(net_adapter_t *self, const net_packet_t *pkt);
    net_state_t (*get_state)(const net_adapter_t *self);
};

#endif /* NET_ADAPTER_H */
