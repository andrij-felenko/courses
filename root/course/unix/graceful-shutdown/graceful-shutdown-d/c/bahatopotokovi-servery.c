#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <unistd.h>
#include <stdio.h>

typedef struct {
    pthread_t thread;
    atomic_bool running;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
} worker_t;

void* worker_func(void *arg) {
    worker_t *w = (worker_t*)arg;
    while (atomic_load(&w->running)) {
        pthread_mutex_lock(&w->mutex);
        /* Очікування задачі з можливістю пробудження при зупинці */
        pthread_cond_wait(&w->cond, &w->mutex);
        pthread_mutex_unlock(&w->mutex);

        if (!atomic_load(&w->running)) break;
        /* Виконання задачі */
    }
    printf("[WORKER] Потік завершив роботу коректно\n");
    return NULL;
}

void stop_worker(worker_t *w) {
    atomic_store(&w->running, false);
    pthread_mutex_lock(&w->mutex);
    pthread_cond_broadcast(&w->cond); /* Пробудження потоку для виходу */
    pthread_mutex_unlock(&w->mutex);
    pthread_join(w->thread, NULL);     /* Очікування завершення */
}
