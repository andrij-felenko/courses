#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

#define MAX_NODES 32
#define MAX_ROUNDS 100
#define VALUE_NONE -1

typedef enum {
    MSG_PROPOSE,
    MSG_RATIFY
} MsgType;

typedef struct {
    int from;
    int to;
    int round;
    MsgType type;
    int value; /* 0, 1 або VALUE_NONE для '?' */
    int deliver_tick;
} Message;

typedef struct {
    int id;
    int current_round;
    int preference;
    int decided_value;
    bool has_decided;
    bool is_crashed;
    
    /* Буфери отриманих повідомлень поточного раунду */
    int propose_votes[2];
    int propose_count;
    int ratify_votes[2];
    int ratify_unknown_count;
    int ratify_count;
    bool phase1_done;
} Node;

typedef struct {
    Message msgs[4096];
    int head;
    int tail;
    int count;
} MessageQueue;

static void queue_init(MessageQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

static void queue_push(MessageQueue* q, Message msg) {
    if (q->count < 4096) {
        q->msgs[q->tail] = msg;
        q->tail = (q->tail + 1) % 4096;
        q->count++;
    }
}

static bool queue_pop_ready(MessageQueue* q, int current_tick, Message* out_msg) {
    for (int i = 0; i < q->count; ++i) {
        int idx = (q->head + i) % 4096;
        if (q->msgs[idx].deliver_tick <= current_tick) {
            *out_msg = q->msgs[idx];
            /* Вилучаємо елемент зсувом */
            for (int j = i; j < q->count - 1; ++j) {
                int curr = (q->head + j) % 4096;
                int next = (q->head + j + 1) % 4096;
                q->msgs[curr] = q->msgs[next];
            }
            q->tail = (q->tail - 1 + 4096) % 4096;
            q->count--;
            return true;
        }
    }
    return false;
}

static void send_broadcast(MessageQueue* q, int from, int n, int round, MsgType type, int val, int current_tick) {
    for (int i = 0; i < n; ++i) {
        Message msg;
        msg.from = from;
        msg.to = i;
        msg.round = round;
        msg.type = type;
        msg.value = val;
        /* Випадкова затримка доставки від 1 до 5 тактів */
        msg.deliver_tick = current_tick + 1 + (rand() % 5);
        queue_push(q, msg);
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    
    const int n = 5;
    const int f = 2; /* f < n/2 (2 < 2.5) */
    const int quorum = n - f; /* 3 */
    
    Node nodes[MAX_NODES];
    for (int i = 0; i < n; ++i) {
        nodes[i].id = i;
        nodes[i].current_round = 1;
        nodes[i].preference = (i % 2 == 0) ? 0 : 1; /* Різні початкові входи */
        nodes[i].decided_value = VALUE_NONE;
        nodes[i].has_decided = false;
        nodes[i].is_crashed = (i == 0); /* Вузол 0 зазнав аварійної зупинки */
        nodes[i].propose_votes[0] = 0;
        nodes[i].propose_votes[1] = 0;
        nodes[i].propose_count = 0;
        nodes[i].ratify_votes[0] = 0;
        nodes[i].ratify_votes[1] = 0;
        nodes[i].ratify_unknown_count = 0;
        nodes[i].ratify_count = 0;
        nodes[i].phase1_done = false;
    }
    
    MessageQueue queue;
    queue_init(&queue);
    
    int tick = 0;
    /* Стартове розсилання PROPOSE для першого раунду */
    for (int i = 0; i < n; ++i) {
        if (!nodes[i].is_crashed) {
            send_broadcast(&queue, i, n, 1, MSG_PROPOSE, nodes[i].preference, tick);
        }
    }
    
    bool all_decided = false;
    while (tick < 1000 && !all_decided) {
        tick++;
        Message msg;
        while (queue_pop_ready(&queue, tick, &msg)) {
            Node* node = &nodes[msg.to];
            if (node->is_crashed || msg.round != node->current_round) {
                continue;
            }
            
            if (msg.type == MSG_PROPOSE && !node->phase1_done) {
                if (msg.value == 0 || msg.value == 1) {
                    node->propose_votes[msg.value]++;
                }
                node->propose_count++;
                
                if (node->propose_count >= quorum) {
                    node->phase1_done = true;
                    int send_ratify_val = VALUE_NONE;
                    if (node->propose_votes[0] > n / 2) {
                        send_ratify_val = 0;
                    } else if (node->propose_votes[1] > n / 2) {
                        send_ratify_val = 1;
                    }
                    send_broadcast(&queue, node->id, n, node->current_round, MSG_RATIFY, send_ratify_val, tick);
                }
            } else if (msg.type == MSG_RATIFY && node->phase1_done) {
                if (msg.value == 0 || msg.value == 1) {
                    node->ratify_votes[msg.value]++;
                } else {
                    node->ratify_unknown_count++;
                }
                node->ratify_count++;
                
                if (node->ratify_count >= quorum) {
                    /* Перевірка умов завершення або переходу на наступний раунд */
                    if (node->ratify_votes[0] >= f + 1) {
                        node->decided_value = 0;
                        node->has_decided = true;
                        node->preference = 0;
                    } else if (node->ratify_votes[1] >= f + 1) {
                        node->decided_value = 1;
                        node->has_decided = true;
                        node->preference = 1;
                    } else if (node->ratify_votes[0] > 0) {
                        node->preference = 0;
                    } else if (node->ratify_votes[1] > 0) {
                        node->preference = 1;
                    } else {
                        /* Підкидання монети (Coin Flip) */
                        node->preference = rand() % 2;
                    }
                    
                    /* Підготовка до наступного раунду */
                    node->current_round++;
                    node->propose_votes[0] = 0;
                    node->propose_votes[1] = 0;
                    node->propose_count = 0;
                    node->ratify_votes[0] = 0;
                    node->ratify_votes[1] = 0;
                    node->ratify_unknown_count = 0;
                    node->ratify_count = 0;
                    node->phase1_done = false;
                    
                    send_broadcast(&queue, node->id, n, node->current_round, MSG_PROPOSE, node->preference, tick);
                }
            }
        }
        
        /* Перевірка, чи всі працюючі вузли дійшли рішення */
        all_decided = true;
        for (int i = 0; i < n; ++i) {
            if (!nodes[i].is_crashed && !nodes[i].has_decided) {
                all_decided = false;
                break;
            }
        }
    }
    
    printf("Результати консенсусу Бена-Ора (тактів: %d):\n", tick);
    for (int i = 0; i < n; ++i) {
        if (nodes[i].is_crashed) {
            printf("  Вузол %d: [ЗБІЙ/CRASHED]\n", i);
        } else {
            printf("  Вузол %d: Рішення = %d (Раунд = %d)\n",
                   i, nodes[i].decided_value, nodes[i].current_round);
        }
    }
    
    return 0;
}
