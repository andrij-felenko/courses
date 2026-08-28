#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>

// Опис елемента черги
typedef struct {
    void (*function)(void *arg);
    void *arg;
} task_t;

// Структура пулу потоків
typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    pthread_t *threads;
    task_t *queue;
    size_t capacity;
    size_t count;
    size_t head;
    size_t tail;
    size_t num_threads;
    bool shutdown;
} thread_pool_t;

// Робочий цикл кожного потоку в пулі
static void *worker_thread(void *pool_ptr) {
    thread_pool_t *pool = (thread_pool_t *)pool_ptr;

    while (true) {
        pthread_mutex_lock(&pool->lock);

        // Очікуємо появи задачі або команди завершення
        while (pool->count == 0 && !pool->shutdown) {
            pthread_cond_wait(&pool->not_empty, &pool->lock);
        }

        // Якщо пул зупиняється і черга порожня — виходимо
        if (pool->shutdown && pool->count == 0) {
            pthread_mutex_unlock(&pool->lock);
            break;
        }

        // Витягуємо завдання з кільцевого буфера
        task_t task = pool->queue[pool->head];
        pool->head = (pool->head + 1) % pool->capacity;
        pool->count--;

        // Сповіщаємо тих, хто чекав вільного місця в черзі
        pthread_cond_signal(&pool->not_full);
        pthread_mutex_unlock(&pool->lock);

        // Виконуємо задачу поза замком, щоб не блокувати чергу
        task.function(task.arg);
    }
    return NULL;
}

// Створення пулу потоків
thread_pool_t *thread_pool_create(size_t num_threads, size_t queue_capacity) {
    if (num_threads == 0 || queue_capacity == 0) return NULL;

    thread_pool_t *pool = (thread_pool_t *)malloc(sizeof(thread_pool_t));
    if (!pool) return NULL;

    pool->num_threads = num_threads;
    pool->capacity = queue_capacity;
    pool->count = 0;
    pool->head = 0;
    pool->tail = 0;
    pool->shutdown = false;

    pool->queue = (task_t *)malloc(sizeof(task_t) * queue_capacity);
    pool->threads = (pthread_t *)malloc(sizeof(pthread_t) * num_threads);

    pthread_mutex_init(&pool->lock, NULL);
    pthread_cond_init(&pool->not_empty, NULL);
    pthread_cond_init(&pool->not_full, NULL);

    for (size_t i = 0; i < num_threads; i++) {
        pthread_create(&pool->threads[i], NULL, worker_thread, pool);
    }
    return pool;
}

// Додавання завдання до пулу (блокуюче при заповненій черзі)
bool thread_pool_submit(thread_pool_t *pool, void (*function)(void*), void *arg) {
    if (!pool || !function) return false;

    pthread_mutex_lock(&pool->lock);

    while (pool->count == pool->capacity && !pool->shutdown) {
        pthread_cond_wait(&pool->not_full, &pool->lock);
    }

    if (pool->shutdown) {
        pthread_mutex_unlock(&pool->lock);
        return false;
    }

    pool->queue[pool->tail].function = function;
    pool->queue[pool->tail].arg = arg;
    pool->tail = (pool->tail + 1) % pool->capacity;
    pool->count++;

    pthread_cond_signal(&pool->not_empty);
    pthread_mutex_unlock(&pool->lock);
    return true;
}

// Коректне завершення роботи та звільнення пам'яті
void thread_pool_destroy(thread_pool_t *pool) {
    if (!pool) return;

    pthread_mutex_lock(&pool->lock);
    pool->shutdown = true;
    // Будимо всіх робітників, щоб вони завершили залишок черги та вийшли
    pthread_cond_broadcast(&pool->not_empty);
    pthread_cond_broadcast(&pool->not_full);
    pthread_mutex_unlock(&pool->lock);

    for (size_t i = 0; i < pool->num_threads; i++) {
        pthread_join(pool->threads[i], NULL);
    }

    pthread_mutex_destroy(&pool->lock);
    pthread_cond_destroy(&pool->not_empty);
    pthread_cond_destroy(&pool->not_full);

    free(pool->threads);
    free(pool->queue);
    free(pool);
}
