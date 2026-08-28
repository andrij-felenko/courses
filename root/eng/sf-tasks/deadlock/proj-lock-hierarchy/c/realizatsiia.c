#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <stdbool.h>

// Для мови C змінна рангу потоку оголошується через специфікатор _Thread_local (C11)
static _Thread_local uint64_t current_thread_hierarchy = UINT64_MAX;

typedef struct {
    pthread_mutex_t mtx;
    uint64_t level;
    uint64_t prev_level;
} hier_mutex_t;

int hier_mutex_init(hier_mutex_t *h, uint64_t level) {
    h->level = level;
    h->prev_level = 0;
    return pthread_mutex_init(&h->mtx, NULL);
}

void hier_mutex_destroy(hier_mutex_t *h) {
    pthread_mutex_destroy(&h->mtx);
}

void hier_mutex_lock(hier_mutex_t *h) {
    if (current_thread_hierarchy <= h->level) {
        fprintf(stderr, "КРИТИЧНА ПОМИЛКА: порушення ієрархії замків! "
                        "Поточний ранг потоку %llu <= ранг замка %llu\n",
                (unsigned long long)current_thread_hierarchy,
                (unsigned long long)h->level);
        abort(); // Негайне аварійне завершення для виявлення дефекту на етапі тестування
    }

    pthread_mutex_lock(&h->mtx);
    h->prev_level = current_thread_hierarchy;
    current_thread_hierarchy = h->level;
}

void hier_mutex_unlock(hier_mutex_t *h) {
    if (current_thread_hierarchy != h->level) {
        fprintf(stderr, "КРИТИЧНА ПОМИЛКА: спроба звільнити замок поза чергою!\n");
        abort();
    }
    current_thread_hierarchy = h->prev_level;
    pthread_mutex_unlock(&h->mtx);
}
