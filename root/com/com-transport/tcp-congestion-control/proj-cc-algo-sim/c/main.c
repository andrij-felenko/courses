#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define MSS 1460
#define INITIAL_SSTHRESH 65535

typedef enum {
    TCP_STATE_SLOW_START,
    TCP_STATE_CONGESTION_AVOIDANCE,
    TCP_STATE_FAST_RECOVERY
} tcp_cc_state_t;

typedef enum {
    TCP_ALGO_TAHOE,
    TCP_ALGO_RENO
} tcp_algo_type_t;

typedef struct {
    tcp_algo_type_t algo;
    tcp_cc_state_t state;
    uint32_t cwnd;           /* Розмір вікна заторів (у байтах) */
    uint32_t ssthresh;       /* Поріг повільного старту (у байтах) */
    uint32_t dup_ack_count;  /* Лічильник повторних ACK */
    uint32_t bytes_acked_in_rtt; /* Обсяг підтверджених байтів у поточному RTT */
} tcp_socket_sim_t;

void tcp_sim_init(tcp_socket_sim_t *sock, tcp_algo_type_t algo) {
    sock->algo = algo;
    sock->state = TCP_STATE_SLOW_START;
    sock->cwnd = 1 * MSS;
    sock->ssthresh = INITIAL_SSTHRESH;
    sock->dup_ack_count = 0;
    sock->bytes_acked_in_rtt = 0;
}

/* Обробка нового (не повторного) підтвердження ACK */
void tcp_sim_on_new_ack(tcp_socket_sim_t *sock, uint32_t acked_bytes) {
    sock->dup_ack_count = 0;

    switch (sock->state) {
    case TCP_STATE_SLOW_START:
        /* Експоненціальне зростання: збільшуємо cwnd на кожен підтверджений байт */
        sock->cwnd += acked_bytes;
        if (sock->cwnd >= sock->ssthresh) {
            sock->state = TCP_STATE_CONGESTION_AVOIDANCE;
        }
        break;

    case TCP_STATE_CONGESTION_AVOIDANCE:
        /* Лінійне зростання (AIMD): +1 MSS за весь круг RTT */
        sock->bytes_acked_in_rtt += acked_bytes;
        if (sock->bytes_acked_in_rtt >= sock->cwnd) {
            sock->cwnd += MSS;
            sock->bytes_acked_in_rtt -= sock->cwnd;
        }
        break;

    case TCP_STATE_FAST_RECOVERY:
        /* Вихід із Fast Recovery при отриманні нового ACK (Reno) */
        sock->cwnd = sock->ssthresh;
        sock->bytes_acked_in_rtt = 0;
        sock->state = TCP_STATE_CONGESTION_AVOIDANCE;
        break;
    }
}

/* Обробка дубльованого ACK (дублікат підтвердження) */
void tcp_sim_on_dup_ack(tcp_socket_sim_t *sock) {
    sock->dup_ack_count++;

    if (sock->dup_ack_count == 3) {
        /* Реакція на потрійний dupACK (3x dupACK) */
        sock->ssthresh = sock->cwnd / 2;
        if (sock->ssthresh < 2 * MSS) {
            sock->ssthresh = 2 * MSS;
        }

        if (sock->algo == TCP_ALGO_TAHOE) {
            /* Tahoe: повне скидання до 1 MSS і повернення в Slow Start */
            sock->cwnd = 1 * MSS;
            sock->state = TCP_STATE_SLOW_START;
        } else {
            /* Reno: Fast Recovery — штучне роздування вікна під час очікування */
            sock->cwnd = sock->ssthresh + 3 * MSS;
            sock->state = TCP_STATE_FAST_RECOVERY;
        }
    } else if (sock->state == TCP_STATE_FAST_RECOVERY) {
        /* У стані Fast Recovery кожен наступний dupACK додає 1 MSS (Reno) */
        sock->cwnd += MSS;
    }
}

/* Реакція на тайм-аут (RTO) — важка втрата пакетів */
void tcp_sim_on_timeout(tcp_socket_sim_t *sock) {
    sock->ssthresh = sock->cwnd / 2;
    if (sock->ssthresh < 2 * MSS) {
        sock->ssthresh = 2 * MSS;
    }
    sock->cwnd = 1 * MSS;
    sock->dup_ack_count = 0;
    sock->bytes_acked_in_rtt = 0;
    sock->state = TCP_STATE_SLOW_START;
}

int main(void) {
    tcp_socket_sim_t sock_reno;
    tcp_sim_init(&sock_reno, TCP_ALGO_RENO);

    printf("=== Симуляція TCP Reno (15 тактів RTT) ===\n");
    printf("Крок | Стан                | cwnd (байти) | cwnd (MSS) | ssthresh\n");
    printf("-----+---------------------+--------------+------------+---------\n");

    for (int step = 1; step <= 15; step++) {
        const char *state_str = "SLOW_START";
        if (sock_reno.state == TCP_STATE_CONGESTION_AVOIDANCE) state_str = "CONG_AVOID";
        if (sock_reno.state == TCP_STATE_FAST_RECOVERY)      state_str = "FAST_RECOV";

        printf("%4d | %-19s | %12u | %10u | %8u\n",
               step, state_str, sock_reno.cwnd, sock_reno.cwnd / MSS, sock_reno.ssthresh);

        /* Симуляція подій: на кроці 7 моделюємо потрійний dupACK */
        if (step == 7) {
            printf(" ---> [ПОДІЯ] Потрійний dupACK! Виявлено втрату пакета.\n");
            tcp_sim_on_dup_ack(&sock_reno);
            tcp_sim_on_dup_ack(&sock_reno);
            tcp_sim_on_dup_ack(&sock_reno);
        } else if (step == 8) {
            /* Приходить підтвердження втраченого пакета */
            tcp_sim_on_new_ack(&sock_reno, sock_reno.cwnd);
        } else {
            /* Звичайне проходження RTT без втрат */
            tcp_sim_on_new_ack(&sock_reno, sock_reno.cwnd);
        }
    }

    return 0;
}
