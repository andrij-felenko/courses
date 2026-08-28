#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <sched.h>

#define BUFFER_CAPACITY 64
#define TEST_ITERATIONS 10000
#define PACKET_SIZE 8

typedef struct {
    uint8_t data[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    bool inject_flakiness;
} RingBuffer;

typedef struct {
    RingBuffer* rb;
    size_t errors_detected;
    size_t dropped_packets;
    bool stop_flag;
} TestContext;

static void ring_buffer_init(RingBuffer* rb, bool inject_flakiness) {
    memset(rb->data, 0, sizeof(rb->data));
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    rb->inject_flakiness = inject_flakiness;
    pthread_mutex_init(&rb->lock, NULL);
    pthread_cond_init(&rb->not_empty, NULL);
    pthread_cond_init(&rb->not_full, NULL);
}

static void ring_buffer_destroy(RingBuffer* rb) {
    pthread_mutex_destroy(&rb->lock);
    pthread_cond_destroy(&rb->not_empty);
    pthread_cond_destroy(&rb->not_full);
}

/* Запис у кільцевий буфер */
static bool ring_buffer_push(RingBuffer* rb, const uint8_t* src, size_t len) {
    pthread_mutex_lock(&rb->lock);

    while (rb->count + len > BUFFER_CAPACITY) {
        /* При штучній нестабільності симулюємо відсутність блокування */
        if (rb->inject_flakiness) {
            pthread_mutex_unlock(&rb->lock);
            return false; /* Втрата пакета через переповнення */
        }
        pthread_cond_wait(&rb->not_full, &rb->lock);
    }

    for (size_t i = 0; i < len; ++i) {
        rb->data[rb->head] = src[i];
        rb->head = (rb->head + 1) % BUFFER_CAPACITY;
    }
    rb->count += len;

    pthread_cond_signal(&rb->not_empty);
    pthread_mutex_unlock(&rb->lock);
    return true;
}

/* Зчитування з кільцевого буфера */
static bool ring_buffer_pop(RingBuffer* rb, uint8_t* dst, size_t len, int timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_nsec += timeout_ms * 1000000L;
    if (ts.tv_nsec >= 1000000000L) {
        ts.tv_sec += ts.tv_nsec / 1000000000L;
        ts.tv_nsec %= 1000000000L;
    }

    pthread_mutex_lock(&rb->lock);
    while (rb->count < len) {
        int res = pthread_cond_timedwait(&rb->not_empty, &rb->lock, &ts);
        if (res != 0) {
            pthread_mutex_unlock(&rb->lock);
            return false; /* Таймаут вичитування */
        }
    }

    for (size_t i = 0; i < len; ++i) {
        dst[i] = rb->data[rb->tail];
        rb->tail = (rb->tail + 1) % BUFFER_CAPACITY;
    }
    rb->count -= len;

    pthread_cond_signal(&rb->not_full);
    pthread_mutex_unlock(&rb->lock);
    return true;
}

/* Потік виробника (Producer) */
static void* producer_thread(void* arg) {
    TestContext* ctx = (TestContext*)arg;
    uint8_t packet[PACKET_SIZE];

    for (size_t seq = 0; seq < TEST_ITERATIONS && !ctx->stop_flag; ++seq) {
        packet[0] = (uint8_t)(seq & 0xFF);
        packet[1] = (uint8_t)((seq >> 8) & 0xFF);
        for (size_t i = 2; i < PACKET_SIZE - 1; ++i) {
            packet[i] = (uint8_t)(i * 7);
        }
        /* Контрольний байт: XOR сума */
        uint8_t crc = 0;
        for (size_t i = 0; i < PACKET_SIZE - 1; ++i) {
            crc ^= packet[i];
        }
        packet[PACKET_SIZE - 1] = crc;

        if (!ring_buffer_push(ctx->rb, packet, PACKET_SIZE)) {
            ctx->dropped_packets++;
        }

        if (seq % 50 == 0) {
            sched_yield(); /* Спровокувати перемикання контексту */
        }
    }
    return NULL;
}

/* Потік споживача (Consumer) */
static void* consumer_thread(void* arg) {
    TestContext* ctx = (TestContext*)arg;
    uint8_t packet[PACKET_SIZE];
    size_t received = 0;

    while (received < TEST_ITERATIONS && !ctx->stop_flag) {
        if (!ring_buffer_pop(ctx->rb, packet, PACKET_SIZE, 50)) {
            /* Таймаут зчитування через джитер */
            break;
        }

        uint8_t crc = 0;
        for (size_t i = 0; i < PACKET_SIZE - 1; ++i) {
            crc ^= packet[i];
        }

        if (packet[PACKET_SIZE - 1] != crc) {
            ctx->errors_detected++;
        }
        received++;
    }
    return NULL;
}

int main(void) {
    RingBuffer rb;
    TestContext ctx;
    pthread_t prod, cons;

    printf("=== Запуск стрес-тесту буфера на 10000 ітерацій ===\n");

    /* Тест 1: Режим зі штучною нестабільністю (симуляція джитеру) */
    ring_buffer_init(&rb, true);
    ctx.rb = &rb;
    ctx.errors_detected = 0;
    ctx.dropped_packets = 0;
    ctx.stop_flag = false;

    pthread_create(&prod, NULL, producer_thread, &ctx);
    pthread_create(&cons, NULL, consumer_thread, &ctx);

    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    ring_buffer_destroy(&rb);

    printf("Результати нестабільного режиму:\n");
    printf("  - Втрачено пакетів: %zu\n", ctx.dropped_packets);
    printf("  - Помилок контрольної суми: %zu\n", ctx.errors_detected);

    /* Тест 2: Захищений детермінований режим */
    ring_buffer_init(&rb, false);
    ctx.errors_detected = 0;
    ctx.dropped_packets = 0;

    pthread_create(&prod, NULL, producer_thread, &ctx);
    pthread_create(&cons, NULL, consumer_thread, &ctx);

    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    ring_buffer_destroy(&rb);

    printf("Результати захищеного детермінованого режиму:\n");
    printf("  - Втрачено пакетів: %zu\n", ctx.dropped_packets);
    printf("  - Помилок контрольної суми: %zu\n", ctx.errors_detected);

    if (ctx.errors_detected == 0 && ctx.dropped_packets == 0) {
        printf("СТАТУС: ТЕСТ УСПІШНО ПРОЙДЕНО (100%% ДЕТЕРМІНІЗМ)\n");
        return 0;
    }
    return 1;
}
