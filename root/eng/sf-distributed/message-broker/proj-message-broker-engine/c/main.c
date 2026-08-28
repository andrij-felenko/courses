#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#define MAX_TOKEN_LEN 64
#define MAX_TOKENS 16
#define MAX_CHILDREN 32
#define MAX_DELIVERY_ATTEMPTS 3
#define LEASE_TIMEOUT_SEC 5

typedef struct Message {
    uint64_t id;
    char routing_key[128];
    char payload[256];
    uint32_t delivery_count;
} Message;

typedef struct Queue {
    char name[64];
    Message items[128];
    int head;
    int tail;
    int count;
    bool is_dlq;
} Queue;

typedef struct TopicNode {
    char token[MAX_TOKEN_LEN];
    Queue* bound_queues[16];
    int queue_count;
    struct TopicNode* children[MAX_CHILDREN];
    int child_count;
} TopicNode;

typedef struct InFlight {
    uint64_t delivery_tag;
    Message msg;
    time_t dispatched_at;
    bool active;
} InFlight;

typedef struct Consumer {
    uint32_t id;
    int prefetch_credits;
    InFlight in_flight[16];
    int in_flight_count;
} Consumer;

typedef struct BrokerCore {
    TopicNode* root;
    Queue main_queue;
    Queue dead_letter_queue;
    uint64_t next_delivery_tag;
} BrokerCore;

/* Ініціалізація вузла дерева маршрутизації */
TopicNode* topic_node_create(const char* token) {
    TopicNode* node = (TopicNode*)calloc(1, sizeof(TopicNode));
    if (token) {
        strncpy(node->token, token, MAX_TOKEN_LEN - 1);
    }
    return node;
}

/* Розбиття ключа на токени за роздільником крапки */
int tokenize_key(const char* key, char tokens[MAX_TOKENS][MAX_TOKEN_LEN]) {
    char buffer[256];
    strncpy(buffer, key, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    int count = 0;
    char* saveptr = NULL;
    char* tok = strtok_r(buffer, ".", &saveptr);
    while (tok && count < MAX_TOKENS) {
        strncpy(tokens[count++], tok, MAX_TOKEN_LEN - 1);
        tok = strtok_r(NULL, ".", &saveptr);
    }
    return count;
}

/* Додавання правила підписки в дерево */
void broker_bind(TopicNode* root, const char* pattern, Queue* q) {
    char tokens[MAX_TOKENS][MAX_TOKEN_LEN];
    int num_tokens = tokenize_key(pattern, tokens);
    TopicNode* curr = root;

    for (int i = 0; i < num_tokens; ++i) {
        TopicNode* next = NULL;
        for (int j = 0; j < curr->child_count; ++j) {
            if (strcmp(curr->children[j]->token, tokens[i]) == 0) {
                next = curr->children[j];
                break;
            }
        }
        if (!next) {
            next = topic_node_create(tokens[i]);
            curr->children[curr->child_count++] = next;
        }
        curr = next;
    }
    curr->bound_queues[curr->queue_count++] = q;
}

/* Рекурсивний пошук цільових черг за шаблонами '*' та '#' */
void match_recursive(TopicNode* node, char tokens[MAX_TOKENS][MAX_TOKEN_LEN],
                     int idx, int total, Queue** matched, int* match_count) {
    if (idx == total) {
        for (int i = 0; i < node->queue_count; ++i) {
            matched[(*match_count)++] = node->bound_queues[i];
        }
    }

    for (int i = 0; i < node->child_count; ++i) {
        TopicNode* child = node->children[i];
        if (strcmp(child->token, "#") == 0) {
            /* '#' зіставляється з 0 або більше токенами */
            for (int k = idx; k <= total; ++k) {
                match_recursive(child, tokens, k, total, matched, match_count);
            }
        } else if (idx < total && (strcmp(child->token, "*") == 0 || strcmp(child->token, tokens[idx]) == 0)) {
            /* '*' або точне слово */
            match_recursive(child, tokens, idx + 1, total, matched, match_count);
        }
    }
}

/* Запис повідомлення в чергу */
bool queue_push(Queue* q, const Message* msg) {
    if (q->count >= 128) return false;
    q->items[q->tail] = *msg;
    q->tail = (q->tail + 1) % 128;
    q->count++;
    return true;
}

/* Вибірка повідомлення з черги */
bool queue_pop(Queue* q, Message* out_msg) {
    if (q->count == 0) return false;
    *out_msg = q->items[q->head];
    q->head = (q->head + 1) % 128;
    q->count--;
    return true;
}

/* Публікація повідомлення в брокер */
void broker_publish(BrokerCore* broker, const char* routing_key, const char* payload) {
    char tokens[MAX_TOKENS][MAX_TOKEN_LEN];
    int num_tokens = tokenize_key(routing_key, tokens);

    Queue* matched_queues[16];
    int match_count = 0;
    match_recursive(broker->root, tokens, 0, num_tokens, matched_queues, &match_count);

    Message msg = {
        .id = (uint64_t)rand(),
        .delivery_count = 0
    };
    strncpy(msg.routing_key, routing_key, sizeof(msg.routing_key) - 1);
    strncpy(msg.payload, payload, sizeof(msg.payload) - 1);

    for (int i = 0; i < match_count; ++i) {
        queue_push(matched_queues[i], &msg);
        printf("[BROKER] Повідомлення '%s' (Key: %s) додано в чергу '%s'\n",
               msg.payload, routing_key, matched_queues[i]->name);
    }
}

/* Диспетчеризація повідомлення споживачу з урахуванням кредитів */
bool broker_dispatch(BrokerCore* broker, Queue* q, Consumer* c) {
    if (c->prefetch_credits <= 0) {
        return false; /* Кредити вичерпано, чекаємо ACK */
    }

    Message msg;
    if (!queue_pop(q, &msg)) {
        return false; /* Черга порожня */
    }

    msg.delivery_count++;
    uint64_t tag = ++broker->next_delivery_tag;

    /* Реєстрація в In-Flight таблиці */
    for (int i = 0; i < 16; ++i) {
        if (!c->in_flight[i].active) {
            c->in_flight[i].active = true;
            c->in_flight[i].delivery_tag = tag;
            c->in_flight[i].msg = msg;
            c->in_flight[i].dispatched_at = time(NULL);
            c->in_flight_count++;
            break;
        }
    }

    c->prefetch_credits--;
    printf("[DISPATCH] Споживачу #%u видано msg_id=%llu (Tag: %llu, Спроба: %u). Залишок кредитів: %d\n",
           c->id, (unsigned long long)msg.id, (unsigned long long)tag,
           msg.delivery_count, c->prefetch_credits);
    return true;
}

/* Обробка підтвердження успіху (ACK) */
void broker_ack(BrokerCore* broker, Consumer* c, uint64_t delivery_tag) {
    for (int i = 0; i < 16; ++i) {
        if (c->in_flight[i].active && c->in_flight[i].delivery_tag == delivery_tag) {
            c->in_flight[i].active = false;
            c->in_flight_count--;
            c->prefetch_credits++;
            printf("[ACK] Підтверджено Tag: %llu від споживача #%u. Кредити відновлено до %d\n",
                   (unsigned long long)delivery_tag, c->id, c->prefetch_credits);
            return;
        }
    }
}

/* Обробка відхилення або помилки (NACK) */
void broker_nack(BrokerCore* broker, Queue* q, Consumer* c, uint64_t delivery_tag, bool requeue) {
    for (int i = 0; i < 16; ++i) {
        if (c->in_flight[i].active && c->in_flight[i].delivery_tag == delivery_tag) {
            Message msg = c->in_flight[i].msg;
            c->in_flight[i].active = false;
            c->in_flight_count--;
            c->prefetch_credits++;

            if (requeue && msg.delivery_count < MAX_DELIVERY_ATTEMPTS) {
                queue_push(q, &msg);
                printf("[NACK] Tag: %llu повернено в чергу '%s' (Спроба %u/%d)\n",
                       (unsigned long long)delivery_tag, q->name, msg.delivery_count, MAX_DELIVERY_ATTEMPTS);
            } else {
                queue_push(&broker->dead_letter_queue, &msg);
                printf("[DLQ] Tag: %llu перевищив ліміт спроб! Перенаправлено в Dead Letter Queue\n",
                       (unsigned long long)delivery_tag);
            }
            return;
        }
    }
}

/* Перевірка завислих оренд (Lease Timeout Monitor) */
void broker_check_timeouts(BrokerCore* broker, Queue* q, Consumer* c) {
    time_t now = time(NULL);
    for (int i = 0; i < 16; ++i) {
        if (c->in_flight[i].active && (now - c->in_flight[i].dispatched_at) >= LEASE_TIMEOUT_SEC) {
            printf("[TIMEOUT] Оренда для Tag: %llu минула (%d с без ACK)!\n",
                   (unsigned long long)c->in_flight[i].delivery_tag, LEASE_TIMEOUT_SEC);
            broker_nack(broker, q, c, c->in_flight[i].delivery_tag, true);
        }
    }
}
