#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

#define MAX_EVENTS 256
#define MAX_NODES  8

typedef enum {
    EVENT_LOCAL,
    EVENT_SEND,
    EVENT_RECV
} EventType;

typedef struct {
    uint64_t logical_time;
    uint32_t process_id;
    uint32_t event_id;
    EventType type;
    uint32_t related_msg_id;
    char description[64];
} EventRecord;

typedef struct {
    uint32_t msg_id;
    uint32_t sender_pid;
    uint32_t receiver_pid;
    uint64_t send_timestamp;
    char payload[32];
} NetworkMessage;

typedef struct {
    uint32_t pid;
    uint64_t clock;
    uint32_t event_counter;
} Node;

typedef struct {
    EventRecord records[MAX_EVENTS];
    size_t count;
} GlobalLog;

static GlobalLog g_log;
static uint32_t g_msg_sequence = 1;

void node_init(Node* node, uint32_t pid) {
    node->pid = pid;
    node->clock = 0;
    node->event_counter = 0;
}

static void log_event(Node* node, EventType type, uint32_t msg_id, const char* desc) {
    assert(g_log.count < MAX_EVENTS);
    EventRecord* rec = &g_log.records[g_log.count++];
    rec->logical_time = node->clock;
    rec->process_id = node->pid;
    rec->event_id = ++node->event_counter;
    rec->type = type;
    rec->related_msg_id = msg_id;
    strncpy(rec->description, desc, sizeof(rec->description) - 1);
    rec->description[sizeof(rec->description) - 1] = '\0';
}

void node_execute_local(Node* node, const char* action) {
    node->clock += 1;
    log_event(node, EVENT_LOCAL, 0, action);
}

NetworkMessage node_send_message(Node* node, uint32_t receiver_pid, const char* payload) {
    node->clock += 1;
    NetworkMessage msg;
    msg.msg_id = g_msg_sequence++;
    msg.sender_pid = node->pid;
    msg.receiver_pid = receiver_pid;
    msg.send_timestamp = node->clock;
    strncpy(msg.payload, payload, sizeof(msg.payload) - 1);
    msg.payload[sizeof(msg.payload) - 1] = '\0';

    char desc[64];
    snprintf(desc, sizeof(desc), "Send msg#%u to Node %u", msg.msg_id, receiver_pid);
    log_event(node, EVENT_SEND, msg.msg_id, desc);
    return msg;
}

void node_receive_message(Node* node, const NetworkMessage* msg) {
    assert(msg->receiver_pid == node->pid);
    uint64_t old_clock = node->clock;
    uint64_t max_ts = (old_clock > msg->send_timestamp) ? old_clock : msg->send_timestamp;
    node->clock = max_ts + 1;

    char desc[64];
    snprintf(desc, sizeof(desc), "Recv msg#%u from Node %u (prev=%llu, msg_ts=%llu)",
             msg->msg_id, msg->sender_pid, (unsigned long long)old_clock, (unsigned long long)msg->send_timestamp);
    log_event(node, EVENT_RECV, msg->msg_id, desc);
}

static int compare_events_total_order(const void* a, const void* b) {
    const EventRecord* ea = (const EventRecord*)a;
    const EventRecord* eb = (const EventRecord*)b;
    if (ea->logical_time != eb->logical_time) {
        return (ea->logical_time < eb->logical_time) ? -1 : 1;
    }
    if (ea->process_id != eb->process_id) {
        return (ea->process_id < eb->process_id) ? -1 : 1;
    }
    return (ea->event_id < eb->event_id) ? -1 : 1;
}

void verify_causality_invariants(void) {
    printf("=== Перевірка причинних інваріантів Лампорта ===\n");
    for (size_t i = 0; i < g_log.count; ++i) {
        if (g_log.records[i].type == EVENT_RECV) {
            uint32_t target_msg = g_log.records[i].related_msg_id;
            uint64_t recv_time = g_log.records[i].logical_time;
            bool found_send = false;
            uint64_t send_time = 0;

            for (size_t j = 0; j < g_log.count; ++j) {
                if (g_log.records[j].type == EVENT_SEND && g_log.records[j].related_msg_id == target_msg) {
                    found_send = true;
                    send_time = g_log.records[j].logical_time;
                    break;
                }
            }

            assert(found_send && "Подія відправлення обов'язково існує для кожного отримання");
            assert(recv_time > send_time && "Інваріант Лампорта: L(recv) > L(send)");
            printf("[OK] Повідомлення #%u: Send (L=%llu) -> Recv (L=%llu)\n",
                   target_msg, (unsigned long long)send_time, (unsigned long long)recv_time);
        }
    }
}

int main(void) {
    g_log.count = 0;
    Node node_a, node_b, node_c;
    node_init(&node_a, 1);
    node_init(&node_b, 2);
    node_init(&node_c, 3);

    // 1. Вузол A виконує локальну дію та надсилає повідомлення вузлу B
    node_execute_local(&node_a, "A: ініціалізація транзакції");
    NetworkMessage msg1 = node_send_message(&node_a, 2, "Запит на списання");

    // 2. Вузол B виконує власну паралельну дію
    node_execute_local(&node_b, "B: фонове оновлення індексу");

    // 3. Вузол B отримує msg1 від A
    node_receive_message(&node_b, &msg1);

    // 4. Вузол B надсилає повідомлення вузлу C
    NetworkMessage msg2 = node_send_message(&node_b, 3, "Підтвердження переказу");

    // 5. Вузол C робить локальні дії і отримує msg2
    node_execute_local(&node_c, "C: підготовка буфера");
    node_execute_local(&node_c, "C: перевірка сертифіката");
    node_receive_message(&node_c, &msg2);
    node_execute_local(&node_c, "C: фіксація в журналі");

    // Перевірка інваріантів причинності
    verify_causality_invariants();

    // Сортування журналу за тотальним порядком (L, PID)
    qsort(g_log.records, g_log.count, sizeof(EventRecord), compare_events_total_order);

    printf("\n=== Глобальний журнал подій (Тотальний порядок за (L, PID)) ===\n");
    for (size_t i = 0; i < g_log.count; ++i) {
        const EventRecord* r = &g_log.records[i];
        printf("Крок %2zu: (L=%2llu, PID=%u) -> %s\n",
               i + 1, (unsigned long long)r->logical_time, r->process_id, r->description);
    }
    return 0;
}
