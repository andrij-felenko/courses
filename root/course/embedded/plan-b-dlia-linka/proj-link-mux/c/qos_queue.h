#ifndef QOS_QUEUE_H
#define QOS_QUEUE_H

#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define QOS_MAX_PAYLOAD     256u
#define RX_RING_SLOTS       16u   /* мусить бути степенем двійки */
#define TX_SLOTS_CRITICAL   16u
#define TX_SLOTS_TELEMETRY  8u
#define TX_SLOTS_VIDEO      4u

typedef enum {
    PRIO_CRITICAL  = 0,   /* ручне пілотування, DISARM, RTL — не скидаємо ніколи */
    PRIO_TELEMETRY = 1,   /* кути, координати, напруга — цінний лише найсвіжіший */
    PRIO_VIDEO     = 2,   /* стиснений кадр — перше, чим жертвуємо */
    PRIO_COUNT     = 3
} packet_prio_t;

/* Кадр цілком статичний: масив на місці, жодного вузла в купі.
   Поля rssi/snr заповнює приймач, len/payload — застосунок. */
typedef struct {
    uint16_t seq;
    uint16_t len;
    uint32_t stamp_ms;
    uint8_t  bearer;
    uint8_t  prio;
    int16_t  rssi_dbm;
    int8_t   snr_db;
    uint8_t  payload[QOS_MAX_PAYLOAD];
} packet_t;

/* --- Кільце «ISR пише, задача читає» ---------------------------------------
   head рухає лише продюсер (переривання), tail лише консюмер (задача).
   Лічильники ростуть без обгортання, у слот перетворюються маскою — тому
   «повне» і «порожнє» розрізняються без жодного зайвого слота й без замка. */
typedef struct {
    packet_t         slots[RX_RING_SLOTS];
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
    uint32_t         overruns;   /* кадри, що не влізли: задача не встигла */
} rx_ring_t;

void rx_ring_init(rx_ring_t *r);
bool rx_ring_push(rx_ring_t *r, const packet_t *pkt);   /* контекст переривання */
bool rx_ring_pop(rx_ring_t *r, packet_t *out);          /* контекст задачі */

/* --- Черга на передачу -----------------------------------------------------
   Живе цілком у контексті задачі арбітра (кладе застосунок, забирає той самий
   цикл), тому атомарні лічильники тут були б обманом: конкурента немає. */
typedef enum {
    TX_FULL_REJECT = 0,    /* критичне: повна черга — це помилка, а не тиша */
    TX_FULL_DROP_OLDEST,   /* телеметрія: свіжі координати важать більше за старі */
    TX_FULL_DROP_NEW       /* відео: смуги немає — новий кадр просто не беремо */
} tx_full_policy_t;

typedef struct {
    packet_t        *slots;
    uint32_t         capacity;   /* степінь двійки */
    uint32_t         mask;
    uint32_t         head;
    uint32_t         tail;
    tx_full_policy_t policy;
    uint32_t         dropped;
    uint32_t         peak;
} tx_queue_t;

void            tx_queue_init(tx_queue_t *q, packet_t *storage, uint32_t capacity,
                              tx_full_policy_t policy);
bool            tx_queue_push(tx_queue_t *q, const packet_t *pkt);
const packet_t *tx_queue_front(const tx_queue_t *q);
void            tx_queue_pop_front(tx_queue_t *q);
void            tx_queue_flush(tx_queue_t *q);
uint32_t        tx_queue_count(const tx_queue_t *q);

#endif /* QOS_QUEUE_H */
