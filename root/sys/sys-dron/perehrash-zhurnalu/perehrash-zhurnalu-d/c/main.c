#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_QUEUE_SIZE 1024

/* Типи сенсорних повідомлень для впорскування в EKF */
typedef enum {
    MSG_TYPE_IMU  = 1,
    MSG_TYPE_MAG  = 2,
    MSG_TYPE_BARO = 3,
    MSG_TYPE_GPS  = 4
} sensor_msg_type_t;

/* Структура бінарного кадру сенсора */
typedef struct {
    uint64_t timestamp_us;
    sensor_msg_type_t type;
    uint16_t size;
    uint8_t payload[64];
} replay_packet_t;

/* Пріоритетна черга з мінімальною купою (Min-Heap) за timestamp */
typedef struct {
    replay_packet_t data[MAX_QUEUE_SIZE];
    size_t size;
} priority_queue_t;

static void pq_init(priority_queue_t *pq) {
    pq->size = 0;
}

static void pq_push(priority_queue_t *pq, const replay_packet_t *pkt) {
    if (pq->size >= MAX_QUEUE_SIZE) {
        fprintf(stderr, "Помилка: переповнення черги переграшу!\n");
        return;
    }
    size_t i = pq->size++;
    while (i > 0) {
        size_t parent = (i - 1) / 2;
        if (pq->data[parent].timestamp_us <= pkt->timestamp_us) {
            break;
        }
        pq->data[i] = pq->data[parent];
        i = parent;
    }
    pq->data[i] = *pkt;
}

static bool pq_pop(priority_queue_t *pq, replay_packet_t *out_pkt) {
    if (pq->size == 0) return false;
    *out_pkt = pq->data[0];
    replay_packet_t last = pq->data[--pq->size];
    if (pq->size == 0) return true;

    size_t i = 0;
    while (i * 2 + 1 < pq->size) {
        size_t left = i * 2 + 1;
        size_t right = left + 1;
        size_t smallest = left;
        if (right < pq->size && pq->data[right].timestamp_us < pq->data[left].timestamp_us) {
            smallest = right;
        }
        if (last.timestamp_us <= pq->data[smallest].timestamp_us) {
            break;
        }
        pq->data[i] = pq->data[smallest];
        i = smallest;
    }
    pq->data[i] = last;
    return true;
}

/* Емуляція функції публікації в шину uORB */
static void mock_orb_publish(sensor_msg_type_t type, uint64_t t_sim, const uint8_t *payload, uint16_t size) {
    (void)payload;
    (void)size;
    const char *type_name = "НЕВІДОМИЙ";
    switch (type) {
        case MSG_TYPE_IMU:  type_name = "IMU (1000 Гц)"; break;
        case MSG_TYPE_MAG:  type_name = "MAG (50 Гц)";   break;
        case MSG_TYPE_BARO: type_name = "BARO (100 Гц)"; break;
        case MSG_TYPE_GPS:  type_name = "GPS (10 Гц)";   break;
    }
    printf("[t_sim = %10llu мкс] Впорскування топіка uORB -> %s\n", 
           (unsigned long long)t_sim, type_name);
}

/* Диспетчер детерміністичного кроку переграшу */
void run_replay_event_loop(priority_queue_t *pq) {
    uint64_t t_sim = 0;
    replay_packet_t pkt;

    while (pq_pop(pq, &pkt)) {
        /* Просування віртуального часу вперед без джитера */
        if (pkt.timestamp_us > t_sim) {
            t_sim = pkt.timestamp_us;
        }
        /* Впорскування даних у цільові контури автопілота */
        mock_orb_publish(pkt.type, t_sim, pkt.payload, pkt.size);
    }
    printf("[Завершення переграшу] Усі кадри успішно оброблено. Кінцевий t_sim = %llu мкс\n", 
           (unsigned long long)t_sim);
}
