#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define SLOT_TIME_US    9
#define SIFS_US         16
#define DIFS_SLOTS      4     /* DIFS 34 мкс ≈ 4 слоти по 9 мкс */
#define PACKET_SLOTS    30    /* 1500 байтів на швидкості 54 Мбіт/с */
#define ACK_SLOTS       3     /* Службовий кадр ACK з інтервалом SIFS */
#define CW_MIN          15
#define CW_MAX          1023
#define MAX_RETRIES     7

typedef enum {
    NODE_WAIT_DIFS,
    NODE_BACKOFF,
    NODE_TRANSMITTING
} node_state_t;

typedef struct {
    int id;
    node_state_t state;
    int cw;
    int backoff_counter;
    int difs_counter;
    int retry_count;
    uint64_t successful_frames;
    uint64_t collision_count;
} wifi_node_t;

static inline int rand_range(int min_val, int max_val) {
    return min_val + rand() % (max_val - min_val + 1);
}

void node_init(wifi_node_t *node, int id) {
    node->id = id;
    node->state = NODE_WAIT_DIFS;
    node->cw = CW_MIN;
    node->retry_count = 0;
    node->difs_counter = DIFS_SLOTS;
    node->backoff_counter = rand_range(0, node->cw);
    node->successful_frames = 0;
    node->collision_count = 0;
}

void run_simulation(int num_nodes, uint64_t total_slots) {
    wifi_node_t *nodes = (wifi_node_t *)malloc(sizeof(wifi_node_t) * num_nodes);
    if (!nodes) return;

    for (int i = 0; i < num_nodes; i++) {
        node_init(&nodes[i], i);
    }

    int channel_busy_until_slot = 0;
    uint64_t total_successful_frames = 0;
    uint64_t total_collisions = 0;
    uint64_t channel_busy_slots = 0;

    for (uint64_t current_slot = 0; current_slot < total_slots; current_slot++) {
        bool channel_busy = (current_slot < (uint64_t)channel_busy_until_slot);
        if (channel_busy) {
            channel_busy_slots++;
        }

        int transmitting_nodes[128];
        int tx_count = 0;

        if (!channel_busy) {
            for (int i = 0; i < num_nodes; i++) {
                wifi_node_t *n = &nodes[i];

                if (n->state == NODE_WAIT_DIFS) {
                    n->difs_counter--;
                    if (n->difs_counter <= 0) {
                        n->state = NODE_BACKOFF;
                    }
                } else if (n->state == NODE_BACKOFF) {
                    if (n->backoff_counter == 0) {
                        if (tx_count < 128) {
                            transmitting_nodes[tx_count++] = i;
                        }
                    } else {
                        n->backoff_counter--;
                    }
                }
            }
        } else {
            /* Канал зайнятий: станції скидають лічильник DIFS і заморожують backoff */
            for (int i = 0; i < num_nodes; i++) {
                if (nodes[i].state == NODE_WAIT_DIFS) {
                    nodes[i].difs_counter = DIFS_SLOTS;
                }
            }
        }

        /* Обробка результатів виходу в ефір */
        if (tx_count == 1) {
            int winner_idx = transmitting_nodes[0];
            wifi_node_t *winner = &nodes[winner_idx];

            winner->successful_frames++;
            total_successful_frames++;
            winner->cw = CW_MIN;
            winner->retry_count = 0;
            winner->difs_counter = DIFS_SLOTS;
            winner->backoff_counter = rand_range(0, winner->cw);
            winner->state = NODE_WAIT_DIFS;

            int duration = PACKET_SLOTS + ACK_SLOTS;
            channel_busy_until_slot = current_slot + duration;
        } else if (tx_count > 1) {
            total_collisions++;
            for (int k = 0; k < tx_count; k++) {
                wifi_node_t *collided = &nodes[transmitting_nodes[k]];
                collided->collision_count++;
                collided->retry_count++;

                if (collided->retry_count >= MAX_RETRIES) {
                    collided->cw = CW_MIN;
                    collided->retry_count = 0;
                } else {
                    collided->cw = (collided->cw + 1) * 2 - 1;
                    if (collided->cw > CW_MAX) {
                        collided->cw = CW_MAX;
                    }
                }
                collided->difs_counter = DIFS_SLOTS;
                collided->backoff_counter = rand_range(0, collided->cw);
                collided->state = NODE_WAIT_DIFS;
            }

            channel_busy_until_slot = current_slot + PACKET_SLOTS;
        }
    }

    printf("=== Результати симуляції CSMA/CA (C) ===\n");
    printf("Кількість вузлів:  %d, Загалом слотів: %llu\n", num_nodes, (unsigned long long)total_slots);
    printf("Успішних кадрів:   %llu\n", (unsigned long long)total_successful_frames);
    printf("Кількість колізій: %llu\n", (unsigned long long)total_collisions);
    printf("Зайнятість ефіру:  %.2f%%\n", (double)channel_busy_slots / total_slots * 100.0);
    printf("Корисна віддача:   %.2f%%\n", (double)(total_successful_frames * PACKET_SLOTS) / total_slots * 100.0);

    free(nodes);
}

int main(void) {
    srand(42);
    run_simulation(10, 500000);
    return 0;
}
