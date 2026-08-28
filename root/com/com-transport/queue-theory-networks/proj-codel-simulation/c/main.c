#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_QUEUE 256
#define TARGET_TIME_MS 5.0
#define INTERVAL_MS 100.0

/* Структура мережевого пакета з міткою часу прибуття */
typedef struct {
    int id;
    int size_bytes;
    double enqueue_time_ms;
} Packet;

/* Черга з пасивним скиданням з кінця (Tail Drop) */
typedef struct {
    Packet buffer[MAX_QUEUE];
    int head;
    int tail;
    int count;
    int capacity;
    long total_enqueued;
    long total_dropped;
    double max_sojourn_ms;
    double sum_sojourn_ms;
    long served_packets;
} TailDropQueue;

void td_init(TailDropQueue *q, int capacity) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->capacity = (capacity > MAX_QUEUE) ? MAX_QUEUE : capacity;
    q->total_enqueued = 0;
    q->total_dropped = 0;
    q->max_sojourn_ms = 0.0;
    q->sum_sojourn_ms = 0.0;
    q->served_packets = 0;
}

bool td_enqueue(TailDropQueue *q, Packet pkt) {
    q->total_enqueued++;
    if (q->count >= q->capacity) {
        q->total_dropped++;
        return false; /* скидання при переповненні буфера */
    }
    q->buffer[q->tail] = pkt;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;
    return true;
}

bool td_dequeue(TailDropQueue *q, double now_ms, Packet *out_pkt) {
    if (q->count == 0) return false;
    *out_pkt = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    double sojourn = now_ms - out_pkt->enqueue_time_ms;
    if (sojourn > q->max_sojourn_ms) q->max_sojourn_ms = sojourn;
    q->sum_sojourn_ms += sojourn;
    q->served_packets++;
    return true;
}

/* Черга з активним керуванням затримкою CoDel */
typedef struct {
    Packet buffer[MAX_QUEUE];
    int head;
    int tail;
    int count;
    int capacity;

    bool dropping;
    double first_above_time_ms;
    double drop_next_ms;
    int drop_count;

    long total_enqueued;
    long total_dropped;
    double max_sojourn_ms;
    double sum_sojourn_ms;
    long served_packets;
} CodelQueue;

void codel_init(CodelQueue *q, int capacity) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->capacity = (capacity > MAX_QUEUE) ? MAX_QUEUE : capacity;
    q->dropping = false;
    q->first_above_time_ms = 0.0;
    q->drop_next_ms = 0.0;
    q->drop_count = 0;
    q->total_enqueued = 0;
    q->total_dropped = 0;
    q->max_sojourn_ms = 0.0;
    q->sum_sojourn_ms = 0.0;
    q->served_packets = 0;
}

bool codel_enqueue(CodelQueue *q, Packet pkt) {
    q->total_enqueued++;
    if (q->count >= q->capacity) {
        q->total_dropped++;
        return false; /* аварійне скидання при вичерпанні буфера */
    }
    q->buffer[q->tail] = pkt;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;
    return true;
}

static double control_law(double now_ms, int count) {
    return now_ms + INTERVAL_MS / sqrt((double)count);
}

bool codel_dequeue(CodelQueue *q, double now_ms, Packet *out_pkt) {
    while (q->count > 0) {
        Packet candidate = q->buffer[q->head];
        q->head = (q->head + 1) % q->capacity;
        q->count--;

        double sojourn = now_ms - candidate.enqueue_time_ms;
        if (sojourn > q->max_sojourn_ms) q->max_sojourn_ms = sojourn;

        bool ok_to_drop = false;
        /* Якщо черга опустилася нижче TARGET або в ній лишилося менше 1 пакета */
        if (sojourn < TARGET_TIME_MS || q->count < 1) {
            q->first_above_time_ms = 0.0;
        } else {
            if (q->first_above_time_ms == 0.0) {
                q->first_above_time_ms = now_ms + INTERVAL_MS;
            } else if (now_ms >= q->first_above_time_ms) {
                ok_to_drop = true;
            }
        }

        if (q->dropping) {
            if (!ok_to_drop) {
                q->dropping = false;
            } else if (now_ms >= drop_next_ms) {
                q->total_dropped++;
                q->drop_count++;
                q->drop_next_ms = control_law(now_ms, q->drop_count);
                continue; /* скидаємо поточний пакет і переходимо до наступного */
            }
        } else if (ok_to_drop) {
            q->dropping = true;
            q->total_dropped++;
            q->drop_count = 1;
            q->drop_next_ms = control_law(now_ms, 1);
            continue; /* скидаємо перший пакет при переході в стан DROPPING */
        }

        *out_pkt = candidate;
        q->sum_sojourn_ms += sojourn;
        q->served_packets++;
        return true;
    }
    return false;
}

int main(void) {
    const double line_rate_mbps = 10.0; /* швидкість лінії 10 Мбіт/с */
    const double bytes_per_ms = (line_rate_mbps * 1e6) / (8.0 * 1000.0);
    const int sim_packets = 5000;

    TailDropQueue td;
    CodelQueue codel;
    td_init(&td, 100);
    codel_init(&codel, 100);

    double now_td = 0.0, next_tx_td = 0.0;
    double now_codel = 0.0, next_tx_codel = 0.0;

    for (int i = 0; i < sim_packets; ++i) {
        /* Імітація трафіку: періодичні сплески кожні 200 пакетів */
        double arrival_delta = (i % 200 < 50) ? 0.4 : 1.5;
        now_td += arrival_delta;
        now_codel += arrival_delta;

        Packet pkt = { .id = i, .size_bytes = 1500, .enqueue_time_ms = now_td };
        td_enqueue(&td, pkt);
        codel_enqueue(&codel, pkt);

        /* Моделювання передачі в лінії для Tail Drop */
        while (next_tx_td <= now_td) {
            Packet tx_pkt;
            if (!td_dequeue(&td, next_tx_td, &tx_pkt)) break;
            double tx_time_ms = tx_pkt.size_bytes / bytes_per_ms;
            next_tx_td += tx_time_ms;
        }
        if (next_tx_td < now_td) next_tx_td = now_td;

        /* Моделювання передачі в лінії для CoDel */
        while (next_tx_codel <= now_codel) {
            Packet tx_pkt;
            if (!codel_dequeue(&codel, next_tx_codel, &tx_pkt)) break;
            double tx_time_ms = tx_pkt.size_bytes / bytes_per_ms;
            next_tx_codel += tx_time_ms;
        }
        if (next_tx_codel < now_codel) next_tx_codel = now_codel;
    }

    printf("=== Результати симуляції (5000 пакетів по 1500 байтів) ===\n");
    printf("Tail Drop: Сер. затримка = %.2f мс, Макс. затримка = %.2f мс, Скинуто = %ld\n",
           td.served_packets ? td.sum_sojourn_ms / td.served_packets : 0.0,
           td.max_sojourn_ms, td.total_dropped);
    printf("CoDel:     Сер. затримка = %.2f мс, Макс. затримка = %.2f мс, Скинуто = %ld\n",
           codel.served_packets ? codel.sum_sojourn_ms / codel.served_packets : 0.0,
           codel.max_sojourn_ms, codel.total_dropped);

    return 0;
}
