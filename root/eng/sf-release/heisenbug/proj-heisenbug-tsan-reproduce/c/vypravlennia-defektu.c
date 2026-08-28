#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdatomic.h>

typedef struct {
    int user_id;
    _Atomic long long hits;
    const char *session_tag;
} UserStats;

static _Atomic(UserStats *) g_stats = NULL;
static pthread_mutex_t g_alloc_lock = PTHREAD_MUTEX_INITIALIZER;

void *worker_updater_safe(void *arg) {
    (void)arg;
    for (int i = 0; i < 100000; ++i) {
        // Безпечне читання атомарного покажчика
        UserStats *s = atomic_load_explicit(&g_stats, memory_order_acquire);
        if (s != NULL) {
            atomic_fetch_add_explicit(&s->hits, 1, memory_order_relaxed);
        }
    }
    return NULL;
}

void *worker_allocator_safe(void *arg) {
    (void)arg;
    for (int i = 0; i < 100000; ++i) {
        UserStats *fresh = (UserStats *)malloc(sizeof(UserStats));
        fresh->user_id = 42;
        atomic_init(&fresh->hits, 0);
        fresh->session_tag = "session_init";

        pthread_mutex_lock(&g_alloc_lock);
        UserStats *old = atomic_exchange_explicit(&g_stats, fresh, memory_order_acq_rel);
        pthread_mutex_unlock(&g_alloc_lock);

        // У реальних системах для безпечного звільнення використовують RCU
        // або епохи пам'яті (hazard pointers) замість негайного free
        (void)old;
    }
    return NULL;
}
