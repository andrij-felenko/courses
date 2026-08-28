#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define NUM_NODES 3
#define MAX_QUEUE 64

typedef enum {
    MSG_APP_TRANSFER,
    MSG_MARKER
} MessageType;

typedef struct {
    MessageType type;
    int from;
    int to;
    int amount;
} Message;

typedef struct {
    Message buffer[MAX_QUEUE];
    int head;
    int tail;
    int count;
} FifoQueue;

static void queue_init(FifoQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

static bool queue_push(FifoQueue* q, Message msg) {
    if (q->count >= MAX_QUEUE) return false;
    q->buffer[q->tail] = msg;
    q->tail = (q->tail + 1) % MAX_QUEUE;
    q->count++;
    return true;
}

static bool queue_pop(FifoQueue* q, Message* msg) {
    if (q->count == 0) return false;
    *msg = q->buffer[q->head];
    q->head = (q->head + 1) % MAX_QUEUE;
    q->count--;
    return true;
}

typedef struct {
    int id;
    int balance;
    
    /* Стан знімка */
    bool snapshot_taken;
    int recorded_balance;
    
    /* Запис стану вхідних каналів: channel_recording[src] == true */
    bool channel_recording[NUM_NODES];
    bool marker_received[NUM_NODES];
    int recorded_channel_sum[NUM_NODES];
} Node;

typedef struct {
    Node nodes[NUM_NODES];
    FifoQueue channels[NUM_NODES][NUM_NODES];
} Network;

void network_init(Network* net, const int initial_balances[NUM_NODES]) {
    for (int i = 0; i < NUM_NODES; i++) {
        net->nodes[i].id = i;
        net->nodes[i].balance = initial_balances[i];
        net->nodes[i].snapshot_taken = false;
        net->nodes[i].recorded_balance = 0;
        
        for (int j = 0; j < NUM_NODES; j++) {
            net->nodes[i].channel_recording[j] = false;
            net->nodes[i].marker_received[j] = false;
            net->nodes[i].recorded_channel_sum[j] = 0;
            queue_init(&net->channels[i][j]);
        }
    }
}

void node_send_marker_to_all(Network* net, int node_id) {
    for (int dst = 0; dst < NUM_NODES; dst++) {
        if (dst == node_id) continue;
        Message marker = {
            .type = MSG_MARKER,
            .from = node_id,
            .to = dst,
            .amount = 0
        };
        queue_push(&net->channels[node_id][dst], marker);
    }
}

void node_initiate_snapshot(Network* net, int node_id) {
    Node* node = &net->nodes[node_id];
    node->snapshot_taken = true;
    node->recorded_balance = node->balance;
    
    /* Ініціатор записує всі вхідні канали від сусідів */
    for (int src = 0; src < NUM_NODES; src++) {
        if (src != node_id) {
            node->channel_recording[src] = true;
            node->marker_received[src] = false;
        }
    }
    
    node_send_marker_to_all(net, node_id);
    printf("[Вузол %d] Ініціював знімок. Зафіксований баланс = %d\n", node_id, node->recorded_balance);
}

void node_send_money(Network* net, int from, int to, int amount) {
    if (net->nodes[from].balance < amount) return;
    
    net->nodes[from].balance -= amount;
    Message msg = {
        .type = MSG_APP_TRANSFER,
        .from = from,
        .to = to,
        .amount = amount
    };
    queue_push(&net->channels[from][to], msg);
}

void node_process_message(Network* net, int to, Message msg) {
    Node* node = &net->nodes[to];
    int from = msg.from;
    
    if (msg.type == MSG_MARKER) {
        if (!node->snapshot_taken) {
            /* Перший маркер: зберігаємо стан процесу */
            node->snapshot_taken = true;
            node->recorded_balance = node->balance;
            node->marker_received[from] = true;
            node->channel_recording[from] = false; /* Канал прибуття порожній */
            node->recorded_channel_sum[from] = 0;
            
            /* Вмикаємо запис для решти вхідних каналів */
            for (int src = 0; src < NUM_NODES; src++) {
                if (src != to && src != from) {
                    node->channel_recording[src] = true;
                    node->marker_received[src] = false;
                }
            }
            
            node_send_marker_to_all(net, to);
            printf("[Вузол %d] Отримав перший маркер від %d. Баланс = %d, канал C_%d%d = 0\n",
                   to, from, node->recorded_balance, from, to);
        } else {
            /* Наступний маркер: зупиняємо запис цього каналу */
            node->marker_received[from] = true;
            node->channel_recording[from] = false;
            printf("[Вузол %d] Отримав наступний маркер від %d. Стан каналу C_%d%d = %d\n",
                   to, from, from, to, node->recorded_channel_sum[from]);
        }
    } else {
        /* Звичайний грошовий переказ */
        node->balance += msg.amount;
        
        /* Якщо канал записується, фіксуємо транзитні гроші */
        if (node->channel_recording[from]) {
            node->recorded_channel_sum[from] += msg.amount;
            printf("[Вузол %d] Зафіксовано транзит у C_%d%d: +%d грн\n", to, from, to, msg.amount);
        }
    }
}

void deliver_one_message(Network* net, int from, int to) {
    Message msg;
    if (queue_pop(&net->channels[from][to], &msg)) {
        node_process_message(net, to, msg);
    }
}

int main(void) {
    Network net;
    int initial[NUM_NODES] = {500, 300, 200};
    network_init(&net, initial);
    
    printf("=== Старт симуляції Чанді-Лампорта ===\n");
    printf("Початковий загальний баланс: %d грн\n\n", initial[0] + initial[1] + initial[2]);
    
    /* 1. Початок роботи: P0 переказує P1 100 грн (у дорозі) */
    node_send_money(&net, 0, 1, 100);
    
    /* 2. P0 ініціює знімок */
    node_initiate_snapshot(&net, 0);
    
    /* 3. P0 надсилає P1 ще 50 грн (після маркера) */
    node_send_money(&net, 0, 1, 50);
    
    /* 4. P1 отримує 100 грн ДО маркера */
    deliver_one_message(&net, 0, 1);
    
    /* 5. P1 отримує маркер від P0 */
    deliver_one_message(&net, 0, 1);
    
    /* 6. Доставляємо маркери до P2 та назад до P0 */
    deliver_one_message(&net, 0, 2);
    deliver_one_message(&net, 1, 2);
    deliver_one_message(&net, 1, 0);
    deliver_one_message(&net, 2, 0);
    deliver_one_message(&net, 2, 1);
    
    /* 7. Доставляємо останній платіж на 50 грн */
    deliver_one_message(&net, 0, 1);
    
    /* Підсумок знімка */
    int total_nodes = 0;
    int total_channels = 0;
    
    printf("\n=== Результат розподіленого знімка ===\n");
    for (int i = 0; i < NUM_NODES; i++) {
        printf("Вузол P%d: зафіксований стан = %d грн\n", i, net.nodes[i].recorded_balance);
        total_nodes += net.nodes[i].recorded_balance;
        
        for (int j = 0; j < NUM_NODES; j++) {
            if (i != j && net.nodes[i].recorded_channel_sum[j] > 0) {
                printf("  Канал C_%d%d (у польоті) = %d грн\n", j, i, net.nodes[i].recorded_channel_sum[j]);
                total_channels += net.nodes[i].recorded_channel_sum[j];
            }
        }
    }
    
    int snapshot_sum = total_nodes + total_channels;
    printf("\nСума вузлів: %d грн\n", total_nodes);
    printf("Сума каналів: %d грн\n", total_channels);
    printf("Загальна сума знімка: %d грн\n", snapshot_sum);
    printf("Інваріант збереження: %s\n", (snapshot_sum == 1000) ? "ВИКОНАНО" : "ПОРУШЕНО");
    
    return 0;
}
