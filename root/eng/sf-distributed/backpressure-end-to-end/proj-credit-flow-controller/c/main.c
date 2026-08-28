#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_CAPACITY 100
#define HIGH_WATERMARK  80
#define LOW_WATERMARK   30

typedef struct {
    int id;
    int payload_size;
} message_t;

typedef struct {
    message_t ring_buffer[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;

    int32_t active_credits;
    bool is_socket_paused;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} flow_controller_t;

void flow_controller_init(flow_controller_t *fc) {
    fc->head = 0;
    fc->tail = 0;
    fc->count = 0;
    fc->active_credits = 0;
    fc->is_socket_paused = false;

    pthread_mutex_init(&fc->lock, NULL);
    pthread_cond_init(&fc->not_empty, NULL);
    pthread_cond_init(&fc->not_full, NULL);
}

void flow_controller_destroy(flow_controller_t *fc) {
    pthread_mutex_destroy(&fc->lock);
    pthread_cond_destroy(&fc->not_empty);
    pthread_cond_destroy(&fc->not_full);
}

// Емуляція системного виклику керування сокетом (epoll_ctl EPOLLIN)
static void update_socket_epoll_state(bool enable_read) {
    if (enable_read) {
        printf("[SOCKET] Відновлено читання: EPOLL_CTL_MOD (EPOLLIN увімкнено) -> TCP Window > 0\n");
    } else {
        printf("[SOCKET] Пауза читання: EPOLL_CTL_MOD (EPOLLIN вимкнено) -> TCP ZeroWindow\n");
    }
}

// Додавання повідомлення, що надійшло з мережі
bool flow_controller_push_ingress(flow_controller_t *fc, message_t msg) {
    pthread_mutex_lock(&fc->lock);

    if (fc->count >= BUFFER_CAPACITY) {
        // Буфер переповнено через ігнорування протоколу відправником
        pthread_mutex_unlock(&fc->lock);
        return false;
    }

    fc->ring_buffer[fc->tail] = msg;
    fc->tail = (fc->tail + 1) % BUFFER_CAPACITY;
    fc->count++;

    if (fc->active_credits > 0) {
        fc->active_credits--;
    }

    // Перевірка досягнення High Watermark
    if (fc->count >= HIGH_WATERMARK && !fc->is_socket_paused) {
        fc->is_socket_paused = true;
        update_socket_epoll_state(false);
    }

    pthread_cond_signal(&fc->not_empty);
    pthread_mutex_unlock(&fc->lock);
    return true;
}

// Вибірка повідомлення робочим потоком бізнес-логіки
message_t flow_controller_pop_worker(flow_controller_t *fc) {
    pthread_mutex_lock(&fc->lock);

    while (fc->count == 0) {
        pthread_cond_wait(&fc->not_empty, &fc->lock);
    }

    message_t msg = fc->ring_buffer[fc->head];
    fc->head = (fc->head + 1) % BUFFER_CAPACITY;
    fc->count--;

    // Перевірка падіння черги нижче Low Watermark
    if (fc->count <= LOW_WATERMARK && fc->is_socket_paused) {
        fc->is_socket_paused = false;
        update_socket_epoll_state(true);

        // Поповнення кредитів відправника
        int32_t grant = (int32_t)(BUFFER_CAPACITY - fc->count);
        fc->active_credits += grant;
        printf("[CREDIT] Надіслано кадр REQUEST_N: +%d кредитів (доступно: %d)\n",
               grant, fc->active_credits);
    }

    pthread_cond_signal(&fc->not_full);
    pthread_mutex_unlock(&fc->lock);
    return msg;
}
