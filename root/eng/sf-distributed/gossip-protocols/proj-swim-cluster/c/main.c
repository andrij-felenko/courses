#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/select.h>

#define MAX_NODES 64
#define INDIRECT_K 3
#define PROBE_TIMEOUT_MS 500
#define SUSPECT_TIMEOUT_MS 3000

typedef enum {
    MSG_PING = 1,
    MSG_ACK = 2,
    MSG_PING_REQ = 3,
    MSG_SUSPECT = 4,
    MSG_ALIVE = 5,
    MSG_DEAD = 6
} MessageType;

typedef enum {
    STATE_ALIVE = 0,
    STATE_SUSPECT = 1,
    STATE_DEAD = 2
} NodeState;

#pragma pack(push, 1)
typedef struct {
    uint8_t  type;
    uint16_t seq;
    uint32_t from_id;
    uint32_t incarnation;
    uint32_t target_id;       /* Використовується для PING_REQ */
    uint32_t target_ip;
    uint16_t target_port;
} SwimPacket;
#pragma pack(pop)

typedef struct {
    uint32_t id;
    struct sockaddr_in addr;
    uint32_t incarnation;
    NodeState state;
    time_t suspect_started_at;
} NodeInfo;

typedef struct {
    uint32_t self_id;
    uint32_t self_incarnation;
    int socket_fd;
    NodeInfo nodes[MAX_NODES];
    size_t node_count;
    uint16_t next_seq;
} SwimCluster;

void swim_init(SwimCluster *cluster, uint32_t id, uint16_t port) {
    cluster->self_id = id;
    cluster->self_incarnation = 0;
    cluster->node_count = 0;
    cluster->next_seq = 1;

    cluster->socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in bind_addr = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(port)
    };
    bind(cluster->socket_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr));
}

void swim_add_node(SwimCluster *cluster, uint32_t id, const char *ip, uint16_t port) {
    if (cluster->node_count >= MAX_NODES) return;
    NodeInfo *n = &cluster->nodes[cluster->node_count++];
    n->id = id;
    n->incarnation = 0;
    n->state = STATE_ALIVE;
    n->suspect_started_at = 0;
    n->addr.sin_family = AF_INET;
    n->addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &n->addr.sin_addr);
}

void swim_send_packet(SwimCluster *cluster, const SwimPacket *pkt, const struct sockaddr_in *dest) {
    sendto(cluster->socket_fd, pkt, sizeof(*pkt), 0,
           (const struct sockaddr *)dest, sizeof(*dest));
}

/* Обробка отриманого пакету */
void swim_handle_packet(SwimCluster *cluster, const SwimPacket *pkt, const struct sockaddr_in *from) {
    /* Якщо хтось оголосив нас підозрілим або мертвим, негайно спростовуємо */
    if (pkt->target_id == cluster->self_id &&
        (pkt->type == MSG_SUSPECT || pkt->type == MSG_DEAD)) {
        if (pkt->incarnation >= cluster->self_incarnation) {
            cluster->self_incarnation = pkt->incarnation + 1;
            SwimPacket alive_pkt = {
                .type = MSG_ALIVE,
                .seq = cluster->next_seq++,
                .from_id = cluster->self_id,
                .incarnation = cluster->self_incarnation,
                .target_id = cluster->self_id
            };
            swim_send_packet(cluster, &alive_pkt, from);
        }
        return;
    }

    switch (pkt->type) {
        case MSG_PING: {
            SwimPacket ack_pkt = {
                .type = MSG_ACK,
                .seq = pkt->seq,
                .from_id = cluster->self_id,
                .incarnation = cluster->self_incarnation,
                .target_id = pkt->from_id
            };
            swim_send_packet(cluster, &ack_pkt, from);
            break;
        }
        case MSG_PING_REQ: {
            /* Посередник пінгує цільовий вузол */
            struct sockaddr_in target_addr = {
                .sin_family = AF_INET,
                .sin_port = pkt->target_port,
                .sin_addr.s_addr = pkt->target_ip
            };
            SwimPacket fwd_ping = {
                .type = MSG_PING,
                .seq = pkt->seq,
                .from_id = cluster->self_id,
                .incarnation = cluster->self_incarnation,
                .target_id = pkt->target_id
            };
            swim_send_packet(cluster, &fwd_ping, &target_addr);
            break;
        }
        case MSG_ALIVE: {
            for (size_t i = 0; i < cluster->node_count; ++i) {
                if (cluster->nodes[i].id == pkt->target_id) {
                    if (pkt->incarnation > cluster->nodes[i].incarnation) {
                        cluster->nodes[i].incarnation = pkt->incarnation;
                        cluster->nodes[i].state = STATE_ALIVE;
                        cluster->nodes[i].suspect_started_at = 0;
                    }
                    break;
                }
            }
            break;
        }
        default:
            break;
    }
}

/* Виконання одного раунду зондування */
void swim_probe_round(SwimCluster *cluster) {
    if (cluster->node_count == 0) return;

    size_t target_idx = rand() % cluster->node_count;
    NodeInfo *target = &cluster->nodes[target_idx];
    if (target->state == STATE_DEAD) return;

    uint16_t seq = cluster->next_seq++;
    SwimPacket ping_pkt = {
        .type = MSG_PING,
        .seq = seq,
        .from_id = cluster->self_id,
        .incarnation = cluster->self_incarnation,
        .target_id = target->id
    };

    swim_send_packet(cluster, &ping_pkt, &target->addr);

    /* Очікування прямого підтвердження через select() */
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(cluster->socket_fd, &fds);
    struct timeval tv = { .tv_sec = 0, .tv_usec = PROBE_TIMEOUT_MS * 1000 };

    int res = select(cluster->socket_fd + 1, &fds, NULL, NULL, &tv);
    if (res > 0) {
        SwimPacket ack;
        struct sockaddr_in from;
        socklen_t from_len = sizeof(from);
        recvfrom(cluster->socket_fd, &ack, sizeof(ack), 0, (struct sockaddr *)&from, &from_len);
        if (ack.type == MSG_ACK && ack.seq == seq) {
            target->state = STATE_ALIVE;
            return;
        }
    }

    /* Прямий пінг не вдався -> Непряме зондування через k посередників */
    for (size_t i = 0; i < INDIRECT_K && i < cluster->node_count; ++i) {
        size_t helper_idx = rand() % cluster->node_count;
        if (helper_idx == target_idx) continue;

        SwimPacket ping_req = {
            .type = MSG_PING_REQ,
            .seq = seq,
            .from_id = cluster->self_id,
            .incarnation = cluster->self_incarnation,
            .target_id = target->id,
            .target_ip = target->addr.sin_addr.s_addr,
            .target_port = target->addr.sin_port
        };
        swim_send_packet(cluster, &ping_req, &cluster->nodes[helper_idx].addr);
    }

    /* Якщо відповіді немає, переводимо ціль у підозру */
    if (target->state == STATE_ALIVE) {
        target->state = STATE_SUSPECT;
        target->suspect_started_at = time(NULL);
    }
}
