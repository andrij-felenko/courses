#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_HOPS 16
#define PAYLOAD_SIZE 128
#define QUEUE_CAPACITY 64

// ── 1. Структура конверта повідомлення моста ─────────────────────────────────
typedef struct {
    uint64_t msg_id;
    uint64_t source_offset;
    uint32_t origin_cluster_id;
    uint32_t hop_path[MAX_HOPS];
    size_t hop_count;
    char payload[PAYLOAD_SIZE];
} BridgeMessage;

// ── 2. Обмежена потокобезпечна черга (POSIX Mutex & Cond) ────────────────────
typedef struct {
    BridgeMessage items[QUEUE_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    bool is_shutdown;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty_cv;
    pthread_cond_t not_full_cv;
} BoundedQueue;

static void queue_init(BoundedQueue *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->is_shutdown = false;
    pthread_mutex_init(&q->mutex, NULL);
    pthread_cond_init(&q->not_empty_cv, NULL);
    pthread_cond_init(&q->not_full_cv, NULL);
}

static void queue_destroy(BoundedQueue *q) {
    pthread_mutex_destroy(&q->mutex);
    pthread_cond_destroy(&q->not_empty_cv);
    pthread_cond_destroy(&q->not_full_cv);
}

static bool queue_push(BoundedQueue *q, const BridgeMessage *msg) {
    pthread_mutex_lock(&q->mutex);
    while (q->count == QUEUE_CAPACITY && !q->is_shutdown) {
        pthread_cond_wait(&q->not_full_cv, &q->mutex);
    }

    if (q->is_shutdown) {
        pthread_mutex_unlock(&q->mutex);
        return false;
    }

    q->items[q->tail] = *msg;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;

    pthread_cond_signal(&q->not_empty_cv);
    pthread_mutex_unlock(&q->mutex);
    return true;
}

static bool queue_pop(BoundedQueue *q, BridgeMessage *out_msg) {
    pthread_mutex_lock(&q->mutex);
    while (q->count == 0 && !q->is_shutdown) {
        pthread_cond_wait(&q->not_empty_cv, &q->mutex);
    }

    if (q->count == 0 && q->is_shutdown) {
        pthread_mutex_unlock(&q->mutex);
        return false;
    }

    *out_msg = q->items[q->head];
    q->head = (q->head + 1) % QUEUE_CAPACITY;
    q->count--;

    pthread_cond_signal(&q->not_full_cv);
    pthread_mutex_unlock(&q->mutex);
    return true;
}

static void queue_shutdown(BoundedQueue *q) {
    pthread_mutex_lock(&q->mutex);
    q->is_shutdown = true;
    pthread_cond_broadcast(&q->not_empty_cv);
    pthread_cond_broadcast(&q->not_full_cv);
    pthread_mutex_unlock(&q->mutex);
}

// ── 3. Моделювання брокерів та контексту моста ──────────────────────────────
typedef struct {
    uint32_t bridge_id;
    uint32_t source_cluster_id;
    uint32_t target_cluster_id;
    BoundedQueue queue;
    bool running;
    size_t forwarded_count;
    size_t dropped_loops_count;
} BridgeContext;

static bool detect_cycle(const BridgeMessage *msg, uint32_t target_id) {
    for (size_t i = 0; i < msg->hop_count; ++i) {
        if (msg->hop_path[i] == target_id) {
            return true;
        }
    }
    return false;
}

static void* consumer_thread_func(void *arg) {
    BridgeContext *ctx = (BridgeContext*)arg;
    for (uint64_t offset = 0; offset < 6; ++offset) {
        BridgeMessage msg;
        memset(&msg, 0, sizeof(msg));
        msg.msg_id = 1000 + offset;
        msg.source_offset = offset;

        // Тестова петля на повідомленні 3
        if (offset == 3) {
            msg.origin_cluster_id = ctx->target_cluster_id;
            msg.hop_path[0] = ctx->target_cluster_id;
            msg.hop_path[1] = ctx->source_cluster_id;
            msg.hop_count = 2;
            snprintf(msg.payload, sizeof(msg.payload), "{\"event\":\"echo_test\",\"id\":%lu}", (unsigned long)offset);
        } else {
            msg.origin_cluster_id = ctx->source_cluster_id;
            msg.hop_path[0] = ctx->source_cluster_id;
            msg.hop_count = 1;
            snprintf(msg.payload, sizeof(msg.payload), "{\"event\":\"order_created\",\"offset\":%lu}", (unsigned long)offset);
        }

        // Перевірка петель
        if (detect_cycle(&msg, ctx->target_cluster_id)) {
            printf("  [Міст C] ⚠️ ВИЯВЛЕНО ПЕТЛЮ msg_id=%lu -> ВІДКИДАННЯ\n", (unsigned long)msg.msg_id);
            printf("  [Джерело 0x%02x] Офсет %lu ЗАФІКСОВАНО (Source Ack loop-skip)\n", 
                   ctx->source_cluster_id, (unsigned long)msg.source_offset);
            ctx->dropped_loops_count++;
            continue;
        }

        // Додаємо ціль до шляху
        if (msg.hop_count < MAX_HOPS) {
            msg.hop_path[msg.hop_count++] = ctx->target_cluster_id;
        }

        queue_push(&ctx->queue, &msg);
    }
    return NULL;
}

static void* dispatcher_thread_func(void *arg) {
    BridgeContext *ctx = (BridgeContext*)arg;
    BridgeMessage msg;

    while (queue_pop(&ctx->queue, &msg)) {
        // Симуляція запису в ціль
        usleep(20000); // 20ms
        printf("  [Ціль 0x%02x] Записано msg_id=%lu\n", ctx->target_cluster_id, (unsigned long)msg.msg_id);

        // Фіксація на джерелі (Dual Ack)
        printf("  [Джерело 0x%02x] Офсет %lu успішно ЗАФІКСОВАНО (Source Ack)\n", 
               ctx->source_cluster_id, (unsigned long)msg.source_offset);
        ctx->forwarded_count++;
    }
    return NULL;
}

// ── 4. Запуск демонстраційного конвеєра ──────────────────────────────────────
int main(void) {
    printf("=== ЗАПУСК МОСТА ПОВІДОМЛЕНЬ (POSIX C Pipeline) ===\n");
    BridgeContext ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.bridge_id = 101;
    ctx.source_cluster_id = 0x01;
    ctx.target_cluster_id = 0x02;
    queue_init(&ctx.queue);

    pthread_t consumer_tid, dispatcher_tid;
    pthread_create(&consumer_tid, NULL, consumer_thread_func, &ctx);
    pthread_create(&dispatcher_tid, NULL, dispatcher_thread_func, &ctx);

    pthread_join(consumer_tid, NULL);
    queue_shutdown(&ctx.queue);
    pthread_join(dispatcher_tid, NULL);

    printf("\n=== ПІДСУМОК РОБОТИ МОСТА ===\n");
    printf("Успішно ретрансльовано: %lu повідомлень\n", (unsigned long)ctx.forwarded_count);
    printf("Відсіяно циклічних петель: %lu\n", (unsigned long)ctx.dropped_loops_count);

    queue_destroy(&ctx.queue);
    return 0;
}
