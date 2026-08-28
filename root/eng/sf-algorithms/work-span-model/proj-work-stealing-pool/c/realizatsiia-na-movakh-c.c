#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define DEQUE_CAPACITY 1024

typedef struct Task {
    void (*func)(void*);
    void *arg;
} Task;

typedef struct Deque {
    Task buffer[DEQUE_CAPACITY];
    int top;
    int bottom;
    pthread_mutex_t lock;
} Deque;

typedef struct ThreadPool {
    int num_threads;
    pthread_t *threads;
    Deque *deques;
    volatile bool running;
} ThreadPool;

typedef struct WorkerArgs {
    ThreadPool *pool;
    int worker_id;
} WorkerArgs;

static void deque_init(Deque *q) {
    q->top = 0;
    q->bottom = 0;
    pthread_mutex_init(&q->lock, NULL);
}

static void deque_destroy(Deque *q) {
    pthread_mutex_destroy(&q->lock);
}

static bool deque_push_bottom(Deque *q, Task task) {
    pthread_mutex_lock(&q->lock);
    if (q->bottom - q->top >= DEQUE_CAPACITY) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    q->buffer[q->bottom % DEQUE_CAPACITY] = task;
    q->bottom++;
    pthread_mutex_unlock(&q->lock);
    return true;
}

static bool deque_pop_bottom(Deque *q, Task *out_task) {
    pthread_mutex_lock(&q->lock);
    if (q->bottom <= q->top) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    q->bottom--;
    *out_task = q->buffer[q->bottom % DEQUE_CAPACITY];
    pthread_mutex_unlock(&q->lock);
    return true;
}

static bool deque_steal_top(Deque *q, Task *out_task) {
    if (pthread_mutex_trylock(&q->lock) != 0) {
        return false;
    }
    if (q->top >= q->bottom) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_task = q->buffer[q->top % DEQUE_CAPACITY];
    q->top++;
    pthread_mutex_unlock(&q->lock);
    return true;
}

static void* worker_loop(void *arg) {
    WorkerArgs *wargs = (WorkerArgs*)arg;
    ThreadPool *pool = wargs->pool;
    int id = wargs->worker_id;
    Deque *my_q = &pool->deques[id];

    unsigned int seed = (unsigned int)(id + 100);

    while (pool->running) {
        Task task;
        if (deque_pop_bottom(my_q, &task)) {
            task.func(task.arg);
            continue;
        }

        // Крадіжка роботи у випадково обраного сусіда
        bool stolen = false;
        if (pool->num_threads > 1) {
            int victim = rand_r(&seed) % pool->num_threads;
            if (victim != id) {
                if (deque_steal_top(&pool->deques[victim], &task)) {
                    task.func(task.arg);
                    stolen = true;
                }
            }
        }

        if (!stolen) {
            usleep(50); // Коротке очікування появи задач
        }
    }
    return NULL;
}

ThreadPool* pool_create(int num_threads) {
    ThreadPool *pool = (ThreadPool*)malloc(sizeof(ThreadPool));
    pool->num_threads = num_threads;
    pool->running = true;
    pool->threads = (pthread_t*)malloc(sizeof(pthread_t) * num_threads);
    pool->deques = (Deque*)malloc(sizeof(Deque) * num_threads);

    for (int i = 0; i < num_threads; ++i) {
        deque_init(&pool->deques[i]);
    }

    for (int i = 0; i < num_threads; ++i) {
        WorkerArgs *args = (WorkerArgs*)malloc(sizeof(WorkerArgs));
        args->pool = pool;
        args->worker_id = i;
        pthread_create(&pool->threads[i], NULL, worker_loop, args);
    }
    return pool;
}

void pool_destroy(ThreadPool *pool) {
    pool->running = false;
    for (int i = 0; i < pool->num_threads; ++i) {
        pthread_join(pool->threads[i], NULL);
        deque_destroy(&pool->deques[i]);
    }
    free(pool->threads);
    free(pool->deques);
    free(pool);
}
