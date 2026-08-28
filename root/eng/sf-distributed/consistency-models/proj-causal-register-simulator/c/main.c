#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_NODES 3
#define MAX_BUFFER 16

typedef enum {
    CONSISTENCY_LINEARIZABLE,
    CONSISTENCY_CAUSAL,
    CONSISTENCY_EVENTUAL
} consistency_mode_t;

typedef struct {
    uint32_t clock[MAX_NODES];
} vector_clock_t;

typedef struct {
    int value;
    uint64_t timestamp;
    vector_clock_t vc;
    int origin_node;
} register_entry_t;

typedef struct {
    int id;
    register_entry_t current;
    register_entry_t buffer[MAX_BUFFER];
    int buffer_count;
} replica_node_t;

typedef struct {
    replica_node_t nodes[MAX_NODES];
    consistency_mode_t mode;
    uint64_t physical_timer;
} cluster_t;

static void vc_init(vector_clock_t *vc) {
    memset(vc->clock, 0, sizeof(vc->clock));
}

static bool vc_is_causally_ready(const vector_clock_t *msg_vc, const vector_clock_t *node_vc, int origin) {
    /* Повідомлення готове до застосування, якщо:
       1. Подія від origin є строго наступною: msg_vc[origin] == node_vc[origin] + 1
       2. Для всіх інших вузлів k: msg_vc[k] <= node_vc[k] */
    if (msg_vc->clock[origin] != node_vc->clock[origin] + 1) {
        return false;
    }
    for (int i = 0; i < MAX_NODES; ++i) {
        if (i != origin && msg_vc->clock[i] > node_vc->clock[i]) {
            return false;
        }
    }
    return true;
}

static void cluster_init(cluster_t *c, consistency_mode_t mode) {
    c->mode = mode;
    c->physical_timer = 100;
    for (int i = 0; i < MAX_NODES; ++i) {
        c->nodes[i].id = i;
        c->nodes[i].current.value = 0;
        c->nodes[i].current.timestamp = 0;
        c->nodes[i].current.origin_node = -1;
        vc_init(&c->nodes[i].current.vc);
        c->nodes[i].buffer_count = 0;
    }
}

/* Запис значення у кластер */
static void cluster_write(cluster_t *c, int target_node, int value) {
    replica_node_t *node = &c->nodes[target_node];
    c->physical_timer += 10;
    node->current.value = value;
    node->current.timestamp = c->physical_timer;
    node->current.origin_node = target_node;
    node->current.vc.clock[target_node]++;

    printf("[WRITE] Вузол %d: запис value=%d (VC: [%u, %u, %u], t=%llu)\n",
           target_node, value,
           node->current.vc.clock[0],
           node->current.vc.clock[1],
           node->current.vc.clock[2],
           (unsigned long long)node->current.timestamp);

    if (c->mode == CONSISTENCY_LINEARIZABLE) {
        /* Строгий синхронний кворум: миттєва реплікація на більшість вузлів */
        for (int i = 0; i < MAX_NODES; ++i) {
            c->nodes[i].current = node->current;
        }
        printf("  -> [Кворум W=3] Стан синхронізовано на всі вузли.\n");
    }
}

/* Асинхронне надходження повідомлення реплікації */
static void cluster_deliver_replication(cluster_t *c, int to_node, register_entry_t entry) {
    replica_node_t *dest = &c->nodes[to_node];

    if (c->mode == CONSISTENCY_EVENTUAL) {
        /* Last-Write-Wins за фізичною часовою міткою */
        if (entry.timestamp >= dest->current.timestamp) {
            dest->current = entry;
            printf("[EVENTUAL DELIVER] Вузол %d застосував value=%d (t=%llu)\n",
                   to_node, entry.value, (unsigned long long)entry.timestamp);
        } else {
            printf("[EVENTUAL DROP] Вузол %d відкинув старіший запис value=%d (t=%llu < %llu)\n",
                   to_node, entry.value, (unsigned long long)entry.timestamp,
                   (unsigned long long)dest->current.timestamp);
        }
        return;
    }

    if (c->mode == CONSISTENCY_CAUSAL) {
        /* Перевірка готовності векторного годинника */
        if (vc_is_causally_ready(&entry.vc, &dest->current.vc, entry.origin_node)) {
            dest->current.value = entry.value;
            dest->current.timestamp = entry.timestamp;
            dest->current.vc.clock[entry.origin_node] = entry.vc.clock[entry.origin_node];
            printf("[CAUSAL DELIVER] Вузол %d застосував value=%d (Новий VC: [%u, %u, %u])\n",
                   to_node, entry.value,
                   dest->current.vc.clock[0],
                   dest->current.vc.clock[1],
                   dest->current.vc.clock[2]);

            /* Спроба розблокувати відкладені повідомлення з буфера */
            bool progressed = true;
            while (progressed) {
                progressed = false;
                for (int b = 0; b < dest->buffer_count; ++b) {
                    register_entry_t buf_e = dest->buffer[b];
                    if (vc_is_causally_ready(&buf_e.vc, &dest->current.vc, buf_e.origin_node)) {
                        dest->current.value = buf_e.value;
                        dest->current.timestamp = buf_e.timestamp;
                        dest->current.vc.clock[buf_e.origin_node] = buf_e.vc.clock[buf_e.origin_node];
                        printf("  -> [CAUSAL UNBUFFER] Вузол %d розблокував із буфера value=%d\n",
                               to_node, buf_e.value);

                        /* Видалення з буфера */
                        dest->buffer[b] = dest->buffer[dest->buffer_count - 1];
                        dest->buffer_count--;
                        progressed = true;
                        break;
                    }
                }
            }
        } else {
            /* Причинні залежності ще не надійшли: буферизуємо */
            if (dest->buffer_count < MAX_BUFFER) {
                dest->buffer[dest->buffer_count++] = entry;
                printf("[CAUSAL BUFFER] Вузол %d відклав value=%d у буфер (очікує попередні події)\n",
                       to_node, entry.value);
            }
        }
    }
}

/* Читання значення з вузла */
static int cluster_read(const cluster_t *c, int target_node) {
    const replica_node_t *node = &c->nodes[target_node];
    printf("[READ] Читання з Вузла %d -> value=%d (VC: [%u, %u, %u])\n",
           target_node, node->current.value,
           node->current.vc.clock[0],
           node->current.vc.clock[1],
           node->current.vc.clock[2]);
    return node->current.value;
}

int main(void) {
    cluster_t sim;

    printf("=== 1. ТЕСТ ПРИЧИННОЇ КОНСИСТЕНТНОСТІ (Causal Consistency) ===\n");
    cluster_init(&sim, CONSISTENCY_CAUSAL);

    /* Аліса на Вузлі 0 пише пост (value=10) */
    cluster_write(&sim, 0, 10);
    register_entry_t post_alice = sim.nodes[0].current;

    /* Боб на Вузлі 1 зчитує пост Аліси через реплікацію та пише відповідь (value=20) */
    cluster_deliver_replication(&sim, 1, post_alice);
    cluster_write(&sim, 1, 20);
    register_entry_t reply_bob = sim.nodes[1].current;

    /* Повідомлення Боба (reply_bob) прибуває на Вузол 2 РАНІШЕ за пост Аліси (перевпорядкування в мережі) */
    printf("\n--- Мережевий збій: відповідь Боба прибула на Вузол 2 раніше за пост Аліси ---\n");
    cluster_deliver_replication(&sim, 2, reply_bob);
    cluster_read(&sim, 2); /* Має повернути 0, бо відповідь заблокована в буфері */

    /* Тепер до Вузла 2 нарешті доходить пост Аліси */
    printf("\n--- Пост Аліси нарешті дійшов до Вузла 2 ---\n");
    cluster_deliver_replication(&sim, 2, post_alice);
    cluster_read(&sim, 2); /* Має автоматично розблокувати відповідь Боба й повернути 20 */

    return 0;
}
