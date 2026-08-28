#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

#define SWIM_MAGIC 0x5357
#define MAX_MEMBERS 256
#define MAX_GOSSIP_ITEMS 16
#define PING_INTERVAL_MS 1000
#define ACK_TIMEOUT_MS 200
#define SUSPECT_TIMEOUT_MS 4000
#define RETRANSMIT_COUNT 3
#define INDIRECT_K 3

typedef enum {
    MSG_PING     = 0x01,
    MSG_ACK      = 0x02,
    MSG_PING_REQ = 0x03,
    MSG_SUSPECT  = 0x04,
    MSG_ALIVE    = 0x05,
    MSG_DEAD     = 0x06
} swim_msg_type_t;

typedef enum {
    STATE_ALIVE   = 0,
    STATE_SUSPECT = 1,
    STATE_DEAD    = 2
} swim_state_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint8_t  msg_type;
    uint8_t  flags;
    uint64_t seq_no;
    uint32_t target_ip;
    uint16_t target_port;
} probe_header_t;

typedef struct {
    uint8_t  state;
    uint32_t ip;
    uint16_t port;
    uint64_t incarnation;
} gossip_payload_t;

typedef struct {
    probe_header_t header;
    uint8_t        gossip_count;
    gossip_payload_t gossip[MAX_GOSSIP_ITEMS];
} swim_packet_t;
#pragma pack(pop)

typedef struct {
    uint32_t     ip;
    uint16_t     port;
    swim_state_t state;
    uint64_t     incarnation;
    uint64_t     state_change_time_ms;
} member_node_t;

typedef struct {
    gossip_payload_t payload;
    uint8_t          retransmits_left;
} broadcast_event_t;

typedef struct {
    int               sockfd;
    uint32_t          self_ip;
    uint16_t          self_port;
    uint64_t          self_incarnation;
    uint64_t          seq_counter;
    
    member_node_t     members[MAX_MEMBERS];
    size_t            member_count;
    
    broadcast_event_t bcast_queue[64];
    size_t            bcast_count;
    
    /* Стан активного прямого зонду */
    bool              probe_in_flight;
    uint64_t          probe_seq;
    size_t            probe_target_idx;
    uint64_t          probe_start_ms;
    bool              indirect_sent;
} swim_node_t;

static uint64_t current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static void queue_broadcast(swim_node_t *node, uint8_t state, uint32_t ip, uint16_t port, uint64_t inc) {
    if (node->bcast_count < 64) {
        broadcast_event_t *ev = &node->bcast_queue[node->bcast_count++];
        ev->payload.state = state;
        ev->payload.ip = ip;
        ev->payload.port = port;
        ev->payload.incarnation = inc;
        ev->retransmits_left = RETRANSMIT_COUNT;
    }
}

static member_node_t* find_member(swim_node_t *node, uint32_t ip, uint16_t port) {
    for (size_t i = 0; i < node->member_count; ++i) {
        if (node->members[i].ip == ip && node->members[i].port == port) {
            return &node->members[i];
        }
    }
    return NULL;
}

static void apply_member_state(swim_node_t *node, uint8_t state, uint32_t ip, uint16_t port, uint64_t inc) {
    /* Перевірка на самого себе: чи оголосили нас підозрілими? */
    if (ip == node->self_ip && port == node->self_port) {
        if (state == STATE_SUSPECT && inc >= node->self_incarnation) {
            /* Спростування (Refutation) */
            node->self_incarnation = inc + 1;
            queue_broadcast(node, STATE_ALIVE, node->self_ip, node->self_port, node->self_incarnation);
            printf("[SWIM] Спростування підозри на себе! Нова інкарнація: %lu\n", (unsigned long)node->self_incarnation);
        }
        return;
    }

    member_node_t *m = find_member(node, ip, port);
    if (!m) {
        if (node->member_count < MAX_MEMBERS && state != STATE_DEAD) {
            m = &node->members[node->member_count++];
            m->ip = ip;
            m->port = port;
            m->state = (swim_state_t)state;
            m->incarnation = inc;
            m->state_change_time_ms = current_time_ms();
            printf("[SWIM] Новий вузол зареєстровано: %u:%u (стан=%d, inc=%lu)\n",
                   ip, ntohs(port), state, (unsigned long)inc);
            queue_broadcast(node, state, ip, port, inc);
        }
        return;
    }

    /* Матриця вирішення конфліктів */
    if (inc > m->incarnation) {
        m->incarnation = inc;
        m->state = (swim_state_t)state;
        m->state_change_time_ms = current_time_ms();
        queue_broadcast(node, state, ip, port, inc);
    } else if (inc == m->incarnation) {
        if (m->state == STATE_ALIVE && state == STATE_SUSPECT) {
            m->state = STATE_SUSPECT;
            m->state_change_time_ms = current_time_ms();
            queue_broadcast(node, state, ip, port, inc);
            printf("[SWIM] Вузол %u перейшов у SUSPECT (inc=%lu)\n", ip, (unsigned long)inc);
        } else if (m->state == STATE_SUSPECT && state == STATE_DEAD) {
            m->state = STATE_DEAD;
            m->state_change_time_ms = current_time_ms();
            queue_broadcast(node, state, ip, port, inc);
            printf("[SWIM] Вузол %u перейшов у DEAD (inc=%lu)\n", ip, (unsigned long)inc);
        }
    }
}

static void pack_and_send(swim_node_t *node, uint8_t msg_type, uint64_t seq,
                          uint32_t dest_ip, uint16_t dest_port,
                          uint32_t target_ip, uint16_t target_port) {
    swim_packet_t pkt;
    memset(&pkt, 0, sizeof(pkt));
    pkt.header.magic = htons(SWIM_MAGIC);
    pkt.header.msg_type = msg_type;
    pkt.header.seq_no = htobe64(seq);
    pkt.header.target_ip = target_ip;
    pkt.header.target_port = target_port;

    /* Пакуємо плітки з черги */
    uint8_t count = 0;
    for (size_t i = 0; i < node->bcast_count && count < MAX_GOSSIP_ITEMS; ++i) {
        if (node->bcast_queue[i].retransmits_left > 0) {
            pkt.gossip[count] = node->bcast_queue[i].payload;
            pkt.gossip[count].incarnation = htobe64(pkt.gossip[count].incarnation);
            node->bcast_queue[i].retransmits_left--;
            count++;
        }
    }
    pkt.gossip_count = count;

    struct sockaddr_in dst;
    memset(&dst, 0, sizeof(dst));
    dst.sin_family = AF_INET;
    dst.sin_addr.s_addr = dest_ip;
    dst.sin_port = dest_port;

    size_t send_len = sizeof(probe_header_t) + 1 + count * sizeof(gossip_payload_t);
    sendto(node->sockfd, &pkt, send_len, 0, (struct sockaddr*)&dst, sizeof(dst));
}

void swim_tick(swim_node_t *node) {
    uint64_t now = current_time_ms();

    /* 1. Перевірка активного прямого зондування */
    if (node->probe_in_flight) {
        if (now - node->probe_start_ms > ACK_TIMEOUT_MS && !node->indirect_sent) {
            /* Відправляємо непрямі запити PING_REQ через k випадкових вузлів */
            member_node_t *target = &node->members[node->probe_target_idx];
            size_t sent_k = 0;
            for (size_t i = 0; i < node->member_count && sent_k < INDIRECT_K; ++i) {
                if (i != node->probe_target_idx && node->members[i].state == STATE_ALIVE) {
                    pack_and_send(node, MSG_PING_REQ, node->probe_seq,
                                  node->members[i].ip, node->members[i].port,
                                  target->ip, target->port);
                    sent_k++;
                }
            }
            node->indirect_sent = true;
        } else if (now - node->probe_start_ms > PING_INTERVAL_MS) {
            /* Повний таймаут раунду: переводимо ціль у SUSPECT */
            member_node_t *target = &node->members[node->probe_target_idx];
            if (target->state == STATE_ALIVE) {
                apply_member_state(node, STATE_SUSPECT, target->ip, target->port, target->incarnation);
            }
            node->probe_in_flight = false;
        }
    } else if (node->member_count > 0) {
        /* Запуск нового раунду прямого зондування */
        node->probe_target_idx = (size_t)rand() % node->member_count;
        member_node_t *target = &node->members[node->probe_target_idx];
        if (target->state != STATE_DEAD) {
            node->probe_seq = ++node->seq_counter;
            node->probe_start_ms = now;
            node->probe_in_flight = true;
            node->indirect_sent = false;
            pack_and_send(node, MSG_PING, node->probe_seq, target->ip, target->port, 0, 0);
        }
    }

    /* 2. Перевірка таймаутів підозри (Suspect -> Dead) */
    for (size_t i = 0; i < node->member_count; ++i) {
        if (node->members[i].state == STATE_SUSPECT) {
            if (now - node->members[i].state_change_time_ms > SUSPECT_TIMEOUT_MS) {
                apply_member_state(node, STATE_DEAD, node->members[i].ip,
                                   node->members[i].port, node->members[i].incarnation);
            }
        }
    }
}
