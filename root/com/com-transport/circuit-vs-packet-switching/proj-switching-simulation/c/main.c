#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_SOURCES 100
#define QUEUE_CAPACITY 200

typedef struct {
    double time_on_mean;
    double time_off_mean;
    double peak_rate_bps;
    bool is_on;
    double next_state_change;
    double session_end_time;
    int channel_id;
    double last_packet_time;
} Source;

typedef struct {
    double arrival_time;
    int source_id;
} Packet;

typedef struct {
    Packet buffer[QUEUE_CAPACITY];
    int head;
    int tail;
    int count;
    int max_capacity;
} PacketQueue;

static void queue_init(PacketQueue *q, int cap) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->max_capacity = cap;
}

static bool queue_push(PacketQueue *q, Packet pkt) {
    if (q->count >= q->max_capacity) return false;
    q->buffer[q->tail] = pkt;
    q->tail = (q->tail + 1) % q->max_capacity;
    q->count++;
    return true;
}

static bool queue_pop(PacketQueue *q, Packet *out) {
    if (q->count == 0) return false;
    *out = q->buffer[q->head];
    q->head = (q->head + 1) % q->max_capacity;
    q->count--;
    return true;
}

static double rand_exp(double mean) {
    double u = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return -mean * log(u);
}

int main(void) {
    srand(42);

    const double sim_duration = 100.0; /* 100 секунд симуляції */
    const double dt = 0.0001;          /* Крок симуляції: 100 мкс */
    const double link_capacity_bps = 10000000.0; /* 10 Мбіт/с */
    const double peak_rate_bps = 1000000.0;       /* 1 Мбіт/с на джерело */
    const int num_sources = 35;
    const int num_circuits = (int)(link_capacity_bps / peak_rate_bps); /* 10 каналів */
    const int packet_size_bits = 8000; /* 1000 байтів */
    const double packet_interval = (double)packet_size_bits / peak_rate_bps; /* 8 мс */
    const double packet_tx_time = (double)packet_size_bits / link_capacity_bps; /* 0.8 мс */

    /* Ініціалізація джерел */
    Source sources[MAX_SOURCES];
    for (int i = 0; i < num_sources; i++) {
        sources[i].time_on_mean = 0.2;
        sources[i].time_off_mean = 1.8;
        sources[i].peak_rate_bps = peak_rate_bps;
        sources[i].is_on = false;
        sources[i].next_state_change = rand_exp(sources[i].time_off_mean);
        sources[i].session_end_time = 0.0;
        sources[i].channel_id = -1;
        sources[i].last_packet_time = 0.0;
    }

    /* Стан комутації каналів */
    bool circuit_busy[MAX_SOURCES];
    memset(circuit_busy, 0, sizeof(circuit_busy));
    long circuit_requests_total = 0;
    long circuit_requests_blocked = 0;
    double circuit_bits_transferred = 0.0;

    /* Стан комутації пакетів */
    PacketQueue pkt_queue;
    queue_init(&pkt_queue, 50);
    long packets_generated = 0;
    long packets_dropped = 0;
    long packets_served = 0;
    double total_packet_delay = 0.0;
    double total_packet_delay_sq = 0.0;
    double packet_server_busy_until = 0.0;
    double packet_bits_transferred = 0.0;

    for (double t = 0.0; t < sim_duration; t += dt) {
        /* 1. Оновлення джерел та генерація подій */
        for (int i = 0; i < num_sources; i++) {
            if (t >= sources[i].next_state_change) {
                if (!sources[i].is_on) {
                    /* Перехід у стан ON */
                    sources[i].is_on = true;
                    double duration = rand_exp(sources[i].time_on_mean);
                    sources[i].next_state_change = t + duration;
                    sources[i].session_end_time = t + duration;
                    sources[i].last_packet_time = t;

                    /* Спроба виділення каналу в Circuit Switching */
                    circuit_requests_total++;
                    int free_ch = -1;
                    for (int ch = 0; ch < num_circuits; ch++) {
                        if (!circuit_busy[ch]) {
                            free_ch = ch;
                            break;
                        }
                    }
                    if (free_ch != -1) {
                        circuit_busy[free_ch] = true;
                        sources[i].channel_id = free_ch;
                    } else {
                        sources[i].channel_id = -1;
                        circuit_requests_blocked++;
                    }
                } else {
                    /* Перехід у стан OFF */
                    sources[i].is_on = false;
                    sources[i].next_state_change = t + rand_exp(sources[i].time_off_mean);
                    if (sources[i].channel_id != -1) {
                        circuit_busy[sources[i].channel_id] = false;
                        sources[i].channel_id = -1;
                    }
                }
            }

            /* Генерація бітів/пакетів від активних джерел */
            if (sources[i].is_on) {
                /* Circuit: передача, якщо канал виділено */
                if (sources[i].channel_id != -1) {
                    circuit_bits_transferred += peak_rate_bps * dt;
                }

                /* Packet: генерація окремих пакетів кожні packet_interval */
                if (t - sources[i].last_packet_time >= packet_interval) {
                    sources[i].last_packet_time = t;
                    packets_generated++;
                    Packet p = { .arrival_time = t, .source_id = i };
                    if (!queue_push(&pkt_queue, p)) {
                        packets_dropped++;
                    }
                }
            }
        }

        /* 2. Обслуговування пакетного сервера (Store-and-Forward лінія) */
        if (t >= packet_server_busy_until && pkt_queue.count > 0) {
            Packet p;
            if (queue_pop(&pkt_queue, &p)) {
                packet_server_busy_until = t + packet_tx_time;
                double delay = (t + packet_tx_time) - p.arrival_time;
                total_packet_delay += delay;
                total_packet_delay_sq += delay * delay;
                packets_served++;
                packet_bits_transferred += packet_size_bits;
            }
        }
    }

    /* Обчислення підсумкових метрик */
    double circuit_utilization = (circuit_bits_transferred / (link_capacity_bps * sim_duration)) * 100.0;
    double circuit_block_rate = ((double)circuit_requests_blocked / circuit_requests_total) * 100.0;

    double packet_utilization = (packet_bits_transferred / (link_capacity_bps * sim_duration)) * 100.0;
    double packet_loss_rate = ((double)packets_dropped / packets_generated) * 100.0;
    double avg_delay_ms = (total_packet_delay / packets_served) * 1000.0;
    double var_delay = (total_packet_delay_sq / packets_served) - ((total_packet_delay / packets_served) * (total_packet_delay / packets_served));
    double jitter_ms = sqrt(var_delay > 0.0 ? var_delay : 0.0) * 1000.0;

    printf("================ РЕЗУЛЬТАТИ СИМУЛЯЦІЇ (100 с) ================\n");
    printf("Кількість підключених джерел: %d | Смуга каналу: %.1f Мбіт/с\n\n", num_sources, link_capacity_bps / 1e6);
    printf("1. КОМУТАЦІЯ КАНАЛІВ (CIRCUIT SWITCHING):\n");
    printf("   • Утилізація вихідного лінка:  %.2f %%\n", circuit_utilization);
    printf("   • Загальна кількість викликів: %ld\n", circuit_requests_total);
    printf("   • Блокування нових викликів:   %.2f %% (%ld відхилено)\n", circuit_block_rate, circuit_requests_blocked);
    printf("   • Джитер та варіація затримки: 0.00 мс (суворий детермінізм)\n\n");
    printf("2. КОМУТАЦІЯ ПАКЕТІВ (PACKET SWITCHING):\n");
    printf("   • Утилізація вихідного лінка:  %.2f %%\n", packet_utilization);
    printf("   • Згенеровано пакетів:         %ld\n", packets_generated);
    printf("   • Втрати через буфер:          %.2f %% (%ld втрачено)\n", packet_loss_rate, packets_dropped);
    printf("   • Середня затримка пакета:     %.2f мс\n", avg_delay_ms);
    printf("   • Джитер (std dev затримки):   %.2f мс\n", jitter_ms);
    printf("===============================================================\n");

    return 0;
}
