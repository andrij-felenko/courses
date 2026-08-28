#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_PAYLOAD_SIZE 512
#define MAX_MESSAGES     1024
#define WAL_MAGIC        0x51554555 /* "QUEU" */

typedef enum {
    MSG_STATE_EMPTY = 0,
    MSG_STATE_READY,
    MSG_STATE_IN_FLIGHT,
    MSG_STATE_ACKED
} msg_state_t;

typedef enum {
    WAL_OP_ENQUEUE = 1,
    WAL_OP_ACQUIRE = 2,
    WAL_OP_ACK     = 3,
    WAL_OP_NACK    = 4
} wal_op_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint32_t crc32;
    uint64_t msg_id;
    uint8_t  op_type;
    uint32_t payload_len;
} wal_header_t;
#pragma pack(pop)

typedef struct {
    uint64_t    id;
    msg_state_t state;
    uint64_t    lease_deadline_ms;
    uint32_t    attempts;
    uint32_t    payload_len;
    char        payload[MAX_PAYLOAD_SIZE];
} queue_item_t;

typedef struct {
    queue_item_t    items[MAX_MESSAGES];
    uint64_t        next_msg_id;
    int             wal_fd;
    pthread_mutex_t lock;
    pthread_cond_t  cond_ready;
    bool            running;
} p2p_queue_t;

static uint64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

static void wal_append_record(p2p_queue_t *q, wal_op_t op, uint64_t msg_id,
                              const char *payload, uint32_t len) {
    if (q->wal_fd < 0) return;

    wal_header_t hdr;
    hdr.magic = WAL_MAGIC;
    hdr.msg_id = msg_id;
    hdr.op_type = (uint8_t)op;
    hdr.payload_len = len;
    hdr.crc32 = calc_crc32((const uint8_t *)payload, len);

    write(q->wal_fd, &hdr, sizeof(hdr));
    if (len > 0 && payload != NULL) {
        write(q->wal_fd, payload, len);
    }
    fdatasync(q->wal_fd);
}

int p2p_queue_init(p2p_queue_t *q, const char *wal_path) {
    memset(q, 0, sizeof(*q));
    q->next_msg_id = 1;
    q->running = true;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->cond_ready, NULL);

    q->wal_fd = open(wal_path, O_CREAT | O_RDWR | O_APPEND, 0644);
    if (q->wal_fd < 0) {
        perror("open wal");
        return -1;
    }

    /* Відновлення стану з журналу WAL */
    lseek(q->wal_fd, 0, SEEK_SET);
    wal_header_t hdr;
    while (read(q->wal_fd, &hdr, sizeof(hdr)) == sizeof(hdr)) {
        if (hdr.magic != WAL_MAGIC) break;

        char buf[MAX_PAYLOAD_SIZE];
        if (hdr.payload_len > 0) {
            read(q->wal_fd, buf, hdr.payload_len);
        }

        uint32_t slot = hdr.msg_id % MAX_MESSAGES;
        if (hdr.op_type == WAL_OP_ENQUEUE) {
            q->items[slot].id = hdr.msg_id;
            q->items[slot].state = MSG_STATE_READY;
            q->items[slot].payload_len = hdr.payload_len;
            memcpy(q->items[slot].payload, buf, hdr.payload_len);
            if (hdr.msg_id >= q->next_msg_id) {
                q->next_msg_id = hdr.msg_id + 1;
            }
        } else if (hdr.op_type == WAL_OP_ACK) {
            q->items[slot].state = MSG_STATE_ACKED;
        } else if (hdr.op_type == WAL_OP_NACK) {
            q->items[slot].state = MSG_STATE_READY;
        }
    }
    lseek(q->wal_fd, 0, SEEK_END);
    return 0;
}

uint64_t p2p_queue_publish(p2p_queue_t *q, const char *payload, uint32_t len) {
    if (len > MAX_PAYLOAD_SIZE) return 0;

    pthread_mutex_lock(&q->lock);
    uint64_t msg_id = q->next_msg_id++;
    uint32_t slot = msg_id % MAX_MESSAGES;

    q->items[slot].id = msg_id;
    q->items[slot].state = MSG_STATE_READY;
    q->items[slot].attempts = 0;
    q->items[slot].lease_deadline_ms = 0;
    q->items[slot].payload_len = len;
    memcpy(q->items[slot].payload, payload, len);

    wal_append_record(q, WAL_OP_ENQUEUE, msg_id, payload, len);

    pthread_cond_signal(&q->cond_ready);
    pthread_mutex_unlock(&q->lock);
    return msg_id;
}

bool p2p_queue_acquire(p2p_queue_t *q, uint64_t lease_duration_ms,
                       uint64_t *out_msg_id, char *out_buf, uint32_t *out_len) {
    pthread_mutex_lock(&q->lock);

    while (q->running) {
        uint64_t now = get_time_ms();
        for (size_t i = 0; i < MAX_MESSAGES; ++i) {
            if (q->items[i].state == MSG_STATE_READY) {
                q->items[i].state = MSG_STATE_IN_FLIGHT;
                q->items[i].lease_deadline_ms = now + lease_duration_ms;
                q->items[i].attempts++;

                *out_msg_id = q->items[i].id;
                *out_len = q->items[i].payload_len;
                memcpy(out_buf, q->items[i].payload, q->items[i].payload_len);

                wal_append_record(q, WAL_OP_ACQUIRE, q->items[i].id, NULL, 0);

                pthread_mutex_unlock(&q->lock);
                return true;
            }
        }

        struct timespec to;
        clock_gettime(CLOCK_REALTIME, &to);
        to.tv_sec += 1;
        pthread_cond_timedwait(&q->cond_ready, &q->lock, &to);
    }

    pthread_mutex_unlock(&q->lock);
    return false;
}

void p2p_queue_ack(p2p_queue_t *q, uint64_t msg_id) {
    pthread_mutex_lock(&q->lock);
    uint32_t slot = msg_id % MAX_MESSAGES;
    if (q->items[slot].id == msg_id && q->items[slot].state == MSG_STATE_IN_FLIGHT) {
        q->items[slot].state = MSG_STATE_ACKED;
        wal_append_record(q, WAL_OP_ACK, msg_id, NULL, 0);
    }
    pthread_mutex_unlock(&q->lock);
}

void p2p_queue_nack(p2p_queue_t *q, uint64_t msg_id) {
    pthread_mutex_lock(&q->lock);
    uint32_t slot = msg_id % MAX_MESSAGES;
    if (q->items[slot].id == msg_id && q->items[slot].state == MSG_STATE_IN_FLIGHT) {
        q->items[slot].state = MSG_STATE_READY;
        q->items[slot].lease_deadline_ms = 0;
        wal_append_record(q, WAL_OP_NACK, msg_id, NULL, 0);
        pthread_cond_signal(&q->cond_ready);
    }
    pthread_mutex_unlock(&q->lock);
}

void p2p_queue_reclaim_expired(p2p_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    uint64_t now = get_time_ms();
    bool signaled = false;

    for (size_t i = 0; i < MAX_MESSAGES; ++i) {
        if (q->items[i].state == MSG_STATE_IN_FLIGHT && now >= q->items[i].lease_deadline_ms) {
            printf("[Брокер] Оренда повідомлення #%lu вичерпана! Повертаємо в чергу READY.\n",
                   (unsigned long)q->items[i].id);
            q->items[i].state = MSG_STATE_READY;
            q->items[i].lease_deadline_ms = 0;
            signaled = true;
        }
    }

    if (signaled) {
        pthread_cond_broadcast(&q->cond_ready);
    }
    pthread_mutex_unlock(&q->lock);
}

void p2p_queue_destroy(p2p_queue_t *q) {
    pthread_mutex_lock(&q->lock);
    q->running = false;
    pthread_cond_broadcast(&q->cond_ready);
    pthread_mutex_unlock(&q->lock);

    if (q->wal_fd >= 0) {
        close(q->wal_fd);
    }
    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->cond_ready);
}
