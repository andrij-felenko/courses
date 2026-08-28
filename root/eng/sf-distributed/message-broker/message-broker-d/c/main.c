#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_QUEUES 8

typedef struct Message {
    uint64_t id;
    char key[64];
    char payload[128];
    uint32_t attempts;
} Message;

typedef struct Queue {
    char name[32];
    Message buffer[64];
    int head, tail, count;
} Queue;

typedef struct Consumer {
    uint32_t id;
    int prefetch_credits;
    uint64_t in_flight_tag;
    Message in_flight_msg;
    bool has_active_lease;
} Consumer;

bool queue_push(Queue* q, const Message* msg) {
    if (q->count >= 64) return false;
    q->buffer[q->tail] = *msg;
    q->tail = (q->tail + 1) % 64;
    q->count++;
    return true;
}

bool queue_pop(Queue* q, Message* msg) {
    if (q->count == 0) return false;
    *msg = q->buffer[q->head];
    q->head = (q->head + 1) % 64;
    q->count--;
    return true;
}

/* Диспетчеризація повідомлення споживачу з урахуванням кредитів */
bool broker_dispatch(Queue* q, Consumer* c, uint64_t tag) {
    if (c->prefetch_credits <= 0 || c->has_active_lease) {
        return false;
    }
    Message msg;
    if (!queue_pop(q, &msg)) {
        return false;
    }
    msg.attempts++;
    c->in_flight_tag = tag;
    c->in_flight_msg = msg;
    c->has_active_lease = true;
    c->prefetch_credits--;
    printf("[DISPATCH] Споживач #%u отримав Tag: %llu (msg_id=%llu). Кредити: %d\n",
           c->id, (unsigned long long)tag, (unsigned long long)msg.id, c->prefetch_credits);
    return true;
}

/* Обробка підтвердження успіху (ACK) */
void broker_ack(Consumer* c, uint64_t tag) {
    if (c->has_active_lease && c->in_flight_tag == tag) {
        c->has_active_lease = false;
        c->prefetch_credits++;
        printf("[ACK] Підтверджено Tag: %llu споживачем #%u. Кредити відновлено до %d\n",
               (unsigned long long)tag, c->id, c->prefetch_credits);
    }
}
