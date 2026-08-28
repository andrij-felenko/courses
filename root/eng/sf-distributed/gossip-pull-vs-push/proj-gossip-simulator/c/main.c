#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_NODES 2048
#define DEFAULT_FANOUT 2

typedef enum {
    MODE_PUSH,
    MODE_PULL,
    MODE_PUSH_PULL
} GossipMode;

typedef struct {
    uint32_t node_id;
    uint64_t state_version; /* версія даних, що поширюються */
} Node;

typedef struct {
    uint32_t total_messages;
    uint64_t total_payload_bytes;
    uint32_t rounds_to_converge;
} SimMetrics;

/* Генератор псевдовипадкових чисел xorshift64 */
static inline uint64_t xorshift64(uint64_t *state) {
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    return *state = x;
}

static inline double random_double(uint64_t *rng) {
    return (double)(xorshift64(rng) & 0xFFFFFFFFFFFFULL) / (double)0x1000000000000ULL;
}

static inline uint32_t random_peer(uint32_t self_id, uint32_t num_nodes, uint64_t *rng) {
    uint32_t peer;
    do {
        peer = (uint32_t)(xorshift64(rng) % num_nodes);
    } while (peer == self_id);
    return peer;
}

SimMetrics run_simulation(uint32_t num_nodes, uint32_t fanout, GossipMode mode, double loss_rate, uint64_t target_version) {
    Node current_nodes[MAX_NODES];
    Node next_nodes[MAX_NODES];
    uint64_t rng = 0x9E3779B97F4A7C15ULL ^ (uint64_t)time(NULL);

    SimMetrics metrics = {0, 0, 0};

    /* Ініціалізація: лише вузол 0 має цільову версію target_version */
    for (uint32_t i = 0; i < num_nodes; ++i) {
        current_nodes[i].node_id = i;
        current_nodes[i].state_version = (i == 0) ? target_version : 0;
        next_nodes[i] = current_nodes[i];
    }

    uint32_t max_rounds = 100;
    for (uint32_t r = 0; r < max_rounds; ++r) {
        uint32_t infected_count = 0;
        for (uint32_t i = 0; i < num_nodes; ++i) {
            if (current_nodes[i].state_version == target_version) {
                infected_count++;
            }
        }

        if (infected_count == num_nodes) {
            metrics.rounds_to_converge = r;
            return metrics;
        }

        /* Виконання раунду пліток */
        for (uint32_t i = 0; i < num_nodes; ++i) {
            for (uint32_t f = 0; f < fanout; ++f) {
                uint32_t peer = random_peer(i, num_nodes, &rng);

                if (mode == MODE_PUSH) {
                    /* Push: надсилає лише інфікований вузол */
                    if (current_nodes[i].state_version == target_version) {
                        metrics.total_messages++;
                        metrics.total_payload_bytes += 64; /* розмір пакета з даними */

                        if (random_double(&rng) >= loss_rate) {
                            next_nodes[peer].state_version = target_version;
                        }
                    }
                } else if (mode == MODE_PULL) {
                    /* Pull: неінфікований вузол запитує сусіда */
                    if (current_nodes[i].state_version < target_version) {
                        metrics.total_messages += 2; /* запит + відповідь */
                        metrics.total_payload_bytes += 8; /* запит: 8B дайджест */

                        if (random_double(&rng) >= loss_rate) {
                            if (current_nodes[peer].state_version == target_version) {
                                metrics.total_payload_bytes += 64; /* відповідь з даними */
                                next_nodes[i].state_version = target_version;
                            }
                        }
                    }
                } else if (mode == MODE_PUSH_PULL) {
                    /* Push-Pull: симетричний обмін дайджестами та дельтами */
                    metrics.total_messages += 2;
                    metrics.total_payload_bytes += 16; /* обмін дайджестами */

                    if (random_double(&rng) >= loss_rate) {
                        /* Push-фаза: i оновлює peer */
                        if (current_nodes[i].state_version > current_nodes[peer].state_version) {
                            metrics.total_payload_bytes += 64;
                            next_nodes[peer].state_version = current_nodes[i].state_version;
                        }
                        /* Pull-фаза: peer оновлює i */
                        if (current_nodes[peer].state_version > current_nodes[i].state_version) {
                            metrics.total_payload_bytes += 64;
                            next_nodes[i].state_version = current_nodes[peer].state_version;
                        }
                    }
                }
            }
        }

        /* Синхронізація станів на кінець раунду */
        memcpy(current_nodes, next_nodes, sizeof(Node) * num_nodes);
    }

    metrics.rounds_to_converge = max_rounds;
    return metrics;
}

int main(void) {
    uint32_t cluster_size = 1000;
    uint32_t fanout = DEFAULT_FANOUT;
    double loss_rate = 0.05; /* 5% втрат пакетів */
    uint64_t target_v = 42;

    printf("=== Симуляція пліток (Кластер: %u вузлів, Втрати: %.1f%%) ===\n\n", cluster_size, loss_rate * 100.0);

    const char *names[] = {"Pure Push", "Pure Pull", "Hybrid Push-Pull"};
    GossipMode modes[] = {MODE_PUSH, MODE_PULL, MODE_PUSH_PULL};

    for (int m = 0; m < 3; ++m) {
        SimMetrics met = run_simulation(cluster_size, fanout, modes[m], loss_rate, target_v);
        printf("[%s]\n", names[m]);
        printf("  • Раундів до 100%% узгодженості: %u\n", met.rounds_to_converge);
        printf("  • Сумарно повідомлень:         %u\n", met.total_messages);
        printf("  • Сумарно трафіку:             %.2f КБ\n\n", (double)met.total_payload_bytes / 1024.0);
    }

    return 0;
}
