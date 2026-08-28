#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_EVENTS 16384
#define MAX_WINDOW 128
#define TOTAL_PACKETS 1000

typedef enum {
    PROTO_STOP_AND_WAIT,
    PROTO_GO_BACK_N,
    PROTO_SELECTIVE_REPEAT
} ArqProtocol;

typedef enum {
    EV_FRAME_TX,
    EV_FRAME_RX,
    EV_ACK_RX,
    EV_TIMEOUT
} EventType;

typedef struct {
    double time_us;
    EventType type;
    uint32_t seq_num;
    bool is_corrupted;
} SimEvent;

/* Пріоритетна черга подій на мінімальній купі */
typedef struct {
    SimEvent heap[MAX_EVENTS];
    size_t size;
} EventQueue;

static void eq_push(EventQueue *eq, double t, EventType type, uint32_t seq, bool corrupt) {
    if (eq->size >= MAX_EVENTS) return;
    size_t i = eq->size++;
    while (i > 0) {
        size_t p = (i - 1) / 2;
        if (eq->heap[p].time_us <= t) break;
        eq->heap[i] = eq->heap[p];
        i = p;
    }
    eq->heap[i] = (SimEvent){ .time_us = t, .type = type, .seq_num = seq, .is_corrupted = corrupt };
}

static bool eq_pop(EventQueue *eq, SimEvent *out) {
    if (eq->size == 0) return false;
    *out = eq->heap[0];
    SimEvent last = eq->heap[--eq->size];
    if (eq->size == 0) return true;
    size_t i = 0;
    while (i * 2 + 1 < eq->size) {
        size_t left = i * 2 + 1, right = i * 2 + 2, best = left;
        if (right < eq->size && eq->heap[right].time_us < eq->heap[left].time_us) best = right;
        if (last.time_us <= eq->heap[best].time_us) break;
        eq->heap[i] = eq->heap[best];
        i = best;
    }
    eq->heap[i] = last;
    return true;
}

/* Генератор випадкових чисел [0.0, 1.0) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

typedef struct {
    ArqProtocol proto;
    uint32_t window_size;
    double t_frame_us;
    double t_prop_us;
    double rto_us;
    double p_loss;

    /* Стан передавача */
    uint32_t tx_base;
    uint32_t tx_next_seq;
    double tx_timer[MAX_WINDOW];
    bool tx_acked[TOTAL_PACKETS];

    /* Стан приймача */
    uint32_t rx_expected;
    bool rx_buffered[TOTAL_PACKETS];

    /* Статистика */
    uint32_t total_transmissions;
    uint32_t successful_packets;
    double total_delay_us;
    double packet_start_time[TOTAL_PACKETS];
} SimState;

static void schedule_tx(SimState *st, EventQueue *eq, double current_time, uint32_t seq) {
    st->total_transmissions++;
    if (st->packet_start_time[seq] < 0.0) {
        st->packet_start_time[seq] = current_time;
    }
    bool lost = (rand_uniform() < st->p_loss);
    eq_push(eq, current_time + st->t_frame_us + st->t_prop_us, EV_FRAME_RX, seq, lost);
    
    st->tx_timer[seq % st->window_size] = current_time + st->rto_us;
    eq_push(eq, current_time + st->rto_us, EV_TIMEOUT, seq, false);
}

void run_simulation(ArqProtocol proto, uint32_t win, double p_loss, double a_ratio) {
    EventQueue eq = { .size = 0 };
    SimState st = {
        .proto = proto,
        .window_size = win,
        .t_frame_us = 100.0,
        .t_prop_us = 100.0 * a_ratio,
        .p_loss = p_loss,
        .tx_base = 0,
        .tx_next_seq = 0,
        .rx_expected = 0,
        .total_transmissions = 0,
        .successful_packets = 0,
        .total_delay_us = 0.0
    };
    st.rto_us = st.t_frame_us + 2.0 * st.t_prop_us + 50.0;
    for (int i = 0; i < TOTAL_PACKETS; i++) {
        st.tx_acked[i] = false;
        st.rx_buffered[i] = false;
        st.packet_start_time[i] = -1.0;
    }

    double now = 0.0;
    /* Стартове заповнення вікна */
    while (st.tx_next_seq < st.tx_base + st.window_size && st.tx_next_seq < TOTAL_PACKETS) {
        schedule_tx(&st, &eq, now, st.tx_next_seq++);
    }

    SimEvent ev;
    while (eq_pop(&eq, &ev) && st.successful_packets < TOTAL_PACKETS) {
        now = ev.time_us;

        switch (ev.type) {
        case EV_FRAME_RX:
            if (ev.is_corrupted) break;

            if (st.proto == PROTO_STOP_AND_WAIT || st.proto == PROTO_GO_BACK_N) {
                if (ev.seq_num == st.rx_expected) {
                    st.rx_expected++;
                    eq_push(&eq, now + st.t_prop_us, EV_ACK_RX, ev.seq_num, false);
                } else {
                    /* Повторне надсилання останнього успішного ACK */
                    if (st.rx_expected > 0) {
                        eq_push(&eq, now + st.t_prop_us, EV_ACK_RX, st.rx_expected - 1, false);
                    }
                }
            } else if (st.proto == PROTO_SELECTIVE_REPEAT) {
                if (ev.seq_num < TOTAL_PACKETS) {
                    st.rx_buffered[ev.seq_num] = true;
                    eq_push(&eq, now + st.t_prop_us, EV_ACK_RX, ev.seq_num, false);
                    while (st.rx_expected < TOTAL_PACKETS && st.rx_buffered[st.rx_expected]) {
                        st.rx_expected++;
                    }
                }
            }
            break;

        case EV_ACK_RX:
            if (st.proto == PROTO_STOP_AND_WAIT) {
                if (ev.seq_num == st.tx_base) {
                    st.tx_acked[ev.seq_num] = true;
                    st.total_delay_us += (now - st.packet_start_time[ev.seq_num]);
                    st.successful_packets++;
                    st.tx_base++;
                    if (st.tx_next_seq < TOTAL_PACKETS) {
                        schedule_tx(&st, &eq, now, st.tx_next_seq++);
                    }
                }
            } else if (st.proto == PROTO_GO_BACK_N) {
                if (ev.seq_num >= st.tx_base) {
                    while (st.tx_base <= ev.seq_num && st.tx_base < TOTAL_PACKETS) {
                        if (!st.tx_acked[st.tx_base]) {
                            st.tx_acked[st.tx_base] = true;
                            st.total_delay_us += (now - st.packet_start_time[st.tx_base]);
                            st.successful_packets++;
                        }
                        st.tx_base++;
                    }
                    while (st.tx_next_seq < st.tx_base + st.window_size && st.tx_next_seq < TOTAL_PACKETS) {
                        schedule_tx(&st, &eq, now, st.tx_next_seq++);
                    }
                }
            } else if (st.proto == PROTO_SELECTIVE_REPEAT) {
                if (ev.seq_num < TOTAL_PACKETS && !st.tx_acked[ev.seq_num]) {
                    st.tx_acked[ev.seq_num] = true;
                    st.total_delay_us += (now - st.packet_start_time[ev.seq_num]);
                    st.successful_packets++;
                    while (st.tx_base < TOTAL_PACKETS && st.tx_acked[st.tx_base]) {
                        st.tx_base++;
                    }
                    while (st.tx_next_seq < st.tx_base + st.window_size && st.tx_next_seq < TOTAL_PACKETS) {
                        schedule_tx(&st, &eq, now, st.tx_next_seq++);
                    }
                }
            }
            break;

        case EV_TIMEOUT:
            if (ev.seq_num < TOTAL_PACKETS && !st.tx_acked[ev.seq_num]) {
                if (st.proto == PROTO_STOP_AND_WAIT) {
                    schedule_tx(&st, &eq, now, ev.seq_num);
                } else if (st.proto == PROTO_GO_BACK_N) {
                    /* Повтор усіх непідтверджених кадрів починаючи з base */
                    if (ev.seq_num == st.tx_base) {
                        for (uint32_t s = st.tx_base; s < st.tx_next_seq; s++) {
                            schedule_tx(&st, &eq, now, s);
                        }
                    }
                } else if (st.proto == PROTO_SELECTIVE_REPEAT) {
                    /* Вибірковий повтор тільки одного втраченого кадру */
                    schedule_tx(&st, &eq, now, ev.seq_num);
                }
            }
            break;
        }
    }

    double efficiency = (double)TOTAL_PACKETS / (double)st.total_transmissions;
    double avg_delay_ms = (st.total_delay_us / TOTAL_PACKETS) / 1000.0;
    const char *names[] = { "Stop-and-Wait", "Go-Back-N", "Selective Repeat" };

    printf("[%s] Win=%u, Pf=%.2f, a=%.1f -> Ефективність: %.3f, Середня затримка: %.2f мс (Передач: %u)\n",
           names[proto], win, p_loss, a_ratio, efficiency, avg_delay_ms, st.total_transmissions);
}

int main(void) {
    srand(42);
    printf("=== Результати імітаційного моделювання ARQ (1000 пакетів) ===\n");
    run_simulation(PROTO_STOP_AND_WAIT, 1, 0.05, 5.0);
    run_simulation(PROTO_GO_BACK_N, 16, 0.05, 5.0);
    run_simulation(PROTO_SELECTIVE_REPEAT, 16, 0.05, 5.0);
    return 0;
}
