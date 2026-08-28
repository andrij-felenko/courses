#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

#define MAX_NODES 64
#define MAX_SLOTS_PER_FRAME 16
#define MAX_FRAMES 128
#define QUEUE_CAPACITY 1024
#define MAX_ARCS 2
#define MAX_DEFERRED_READS 16

/* ── 1. Типи та структури токена ── */
typedef uint32_t frame_id_t;
typedef uint16_t node_id_t;
typedef uint8_t  port_t;

typedef struct {
    frame_id_t frame_id;
    node_id_t  node_id;
    port_t     port;
    int64_t    value;
} df_token_t;

/* ── 2. Опис графа ── */
typedef enum {
    OP_NOP,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_OUTPUT
} df_opcode_t;

typedef struct {
    node_id_t dest_node;
    port_t    dest_port;
} df_arc_t;

typedef struct {
    df_opcode_t opcode;
    uint8_t     is_binary;
    uint8_t     slot_idx;
    uint8_t     num_arcs;
    df_arc_t    arcs[MAX_ARCS];
} df_node_t;

typedef struct {
    df_node_t nodes[MAX_NODES];
    uint32_t  node_count;
} df_graph_t;

/* ── 3. Explicit Token Store (ETS) Кадри ── */
typedef struct {
    atomic_int has_value;
    int64_t    value;
} ets_slot_t;

typedef struct {
    ets_slot_t slots[MAX_SLOTS_PER_FRAME];
    atomic_bool in_use;
} ets_frame_t;

/* ── 4. Черга токенів ── */
typedef struct {
    df_token_t      items[QUEUE_CAPACITY];
    size_t          head;
    size_t          tail;
    size_t          count;
    pthread_mutex_t lock;
    pthread_cond_t  not_empty;
    pthread_cond_t  not_full;
    bool            shutdown;
} token_queue_t;

/* ── 5. Рушій Dataflow ── */
typedef struct {
    df_graph_t    graph;
    ets_frame_t   frames[MAX_FRAMES];
    token_queue_t queue;
    pthread_t     workers[4];
    uint32_t      num_workers;
    atomic_long   output_sum;
} df_engine_t;

/* Ініціалізація черги токенів */
static void queue_init(token_queue_t* q) {
    q->head = q->tail = q->count = 0;
    q->shutdown = false;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

static bool queue_push(token_queue_t* q, df_token_t tok) {
    pthread_mutex_lock(&q->lock);
    while (q->count == QUEUE_CAPACITY && !q->shutdown) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }
    if (q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    q->items[q->tail] = tok;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

static bool queue_pop(token_queue_t* q, df_token_t* out_tok) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    if (q->count == 0 && q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_tok = q->items[q->head];
    q->head = (q->head + 1) % QUEUE_CAPACITY;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Виділення кадру активації з пулу ETS */
static frame_id_t frame_alloc(df_engine_t* eng) {
    for (uint32_t i = 0; i < MAX_FRAMES; ++i) {
        bool expected = false;
        if (atomic_compare_exchange_strong(&eng->frames[i].in_use, &expected, true)) {
            for (uint32_t s = 0; s < MAX_SLOTS_PER_FRAME; ++s) {
                atomic_store(&eng->frames[i].slots[s].has_value, 0);
            }
            return (frame_id_t)i;
        }
    }
    fprintf(stderr, "Помилка: пул кадрів ETS вичерпано!\n");
    exit(1);
}

/* Виконання операції вузла в ALU */
static void execute_node(df_engine_t* eng, frame_id_t fid, const df_node_t* node, int64_t v1, int64_t v2) {
    int64_t result = 0;
    switch (node->opcode) {
        case OP_ADD: result = v1 + v2; break;
        case OP_SUB: result = v1 - v2; break;
        case OP_MUL: result = v1 * v2; break;
        case OP_OUTPUT:
            atomic_fetch_add(&eng->output_sum, v1);
            printf("[C Рушій] Отримано фінальний результат: %ld (Кадр %u)\n", (long)v1, fid);
            return;
        default: return;
    }

    /* Емісія токенів-наступників по вихідних дугах */
    for (uint8_t i = 0; i < node->num_arcs; ++i) {
        df_token_t out_tok = {
            .frame_id = fid,
            .node_id  = node->arcs[i].dest_node,
            .port     = node->arcs[i].dest_port,
            .value    = result
        };
        queue_push(&eng->queue, out_tok);
    }
}

/* Робочий потік процесорного кільця */
static void* worker_thread_fn(void* arg) {
    df_engine_t* eng = (df_engine_t*)arg;
    df_token_t tok;

    while (queue_pop(&eng->queue, &tok)) {
        const df_node_t* node = &eng->graph.nodes[tok.node_id];

        if (!node->is_binary) {
            /* Унарна інструкція: негайне виконання */
            execute_node(eng, tok.frame_id, node, tok.value, 0);
        } else {
            /* Бінарна інструкція: атомарне зіставлення в ETS слоті */
            ets_slot_t* slot = &eng->frames[tok.frame_id].slots[node->slot_idx];
            
            int expected = 0;
            if (atomic_compare_exchange_strong(&slot->has_value, &expected, 1)) {
                /* Прибув перший операнд: зберегти значення в слоті */
                slot->value = tok.value;
            } else {
                /* Прибув другий операнд: повний набір операндів готовий! */
                int64_t first_val = slot->value;
                atomic_store(&slot->has_value, 0); /* Звільнити слот */

                int64_t left  = (tok.port == 0) ? tok.value : first_val;
                int64_t right = (tok.port == 0) ? first_val : tok.value;

                execute_node(eng, tok.frame_id, node, left, right);
            }
        }
    }
    return NULL;
}

int main(void) {
    df_engine_t eng;
    memset(&eng, 0, sizeof(eng));
    queue_init(&eng.queue);

    /* Побудова графа для обчислення: (a + b) * (c - d) */
    /* Вузол 0: ADD (слот 0) -> відправляє в порт 0 Вузла 2 */
    eng.graph.nodes[0] = (df_node_t){
        .opcode = OP_ADD, .is_binary = 1, .slot_idx = 0, .num_arcs = 1,
        .arcs = {{ .dest_node = 2, .dest_port = 0 }}
    };
    /* Вузол 1: SUB (слот 1) -> відправляє в порт 1 Вузла 2 */
    eng.graph.nodes[1] = (df_node_t){
        .opcode = OP_SUB, .is_binary = 1, .slot_idx = 1, .num_arcs = 1,
        .arcs = {{ .dest_node = 2, .dest_port = 1 }}
    };
    /* Вузол 2: MUL (слот 2) -> відправляє у Вузол 3 */
    eng.graph.nodes[2] = (df_node_t){
        .opcode = OP_MUL, .is_binary = 1, .slot_idx = 2, .num_arcs = 1,
        .arcs = {{ .dest_node = 3, .dest_port = 0 }}
    };
    /* Вузол 3: OUTPUT (термінальний вузол) */
    eng.graph.nodes[3] = (df_node_t){
        .opcode = OP_OUTPUT, .is_binary = 0, .slot_idx = 0, .num_arcs = 0
    };

    /* Запуск пулу робочих потоків */
    eng.num_workers = 4;
    for (uint32_t i = 0; i < eng.num_workers; ++i) {
        pthread_create(&eng.workers[i], NULL, worker_thread_fn, &eng);
    }

    /* Виділення кадру активації та запуск обчислення (10 + 20) * (50 - 15) = 30 * 35 = 1050 */
    frame_id_t fid1 = frame_alloc(&eng);

    queue_push(&eng.queue, (df_token_t){ fid1, 0, 0, 10 }); /* a = 10 */
    queue_push(&eng.queue, (df_token_t){ fid1, 0, 1, 20 }); /* b = 20 */
    queue_push(&eng.queue, (df_token_t){ fid1, 1, 0, 50 }); /* c = 50 */
    queue_push(&eng.queue, (df_token_t){ fid1, 1, 1, 15 }); /* d = 15 */

    /* Паралельний запуск другого незалежного кадру (100 + 200) * (40 - 30) = 300 * 10 = 3000 */
    frame_id_t fid2 = frame_alloc(&eng);

    queue_push(&eng.queue, (df_token_t){ fid2, 0, 0, 100 });
    queue_push(&eng.queue, (df_token_t){ fid2, 0, 1, 200 });
    queue_push(&eng.queue, (df_token_t){ fid2, 1, 0, 40 });
    queue_push(&eng.queue, (df_token_t){ fid2, 1, 1, 30 });

    /* Очікування завершення обчислень */
    sleep(1);

    pthread_mutex_lock(&eng.queue.lock);
    eng.queue.shutdown = true;
    pthread_cond_broadcast(&eng.queue.not_empty);
    pthread_mutex_unlock(&eng.queue.lock);

    for (uint32_t i = 0; i < eng.num_workers; ++i) {
        pthread_join(eng.workers[i], NULL);
    }

    printf("Сумарний результат усіх виконаних графів: %ld\n", atomic_load(&eng.output_sum));
    return 0;
}
