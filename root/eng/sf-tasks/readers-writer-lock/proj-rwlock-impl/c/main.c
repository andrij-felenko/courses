#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t  cond_readers;
    pthread_cond_t  cond_writers;
    int             readers;
    int             writers_waiting;
    bool            writer_active;
} custom_rwlock_t;

int custom_rwlock_init(custom_rwlock_t *rw) {
    if (!rw) return -1;
    rw->readers = 0;
    rw->writers_waiting = 0;
    rw->writer_active = false;
    if (pthread_mutex_init(&rw->mutex, NULL) != 0) return -1;
    if (pthread_cond_init(&rw->cond_readers, NULL) != 0) {
        pthread_mutex_destroy(&rw->mutex);
        return -1;
    }
    if (pthread_cond_init(&rw->cond_writers, NULL) != 0) {
        pthread_cond_destroy(&rw->cond_readers);
        pthread_mutex_destroy(&rw->mutex);
        return -1;
    }
    return 0;
}

void custom_rwlock_destroy(custom_rwlock_t *rw) {
    if (!rw) return;
    pthread_mutex_destroy(&rw->mutex);
    pthread_cond_destroy(&rw->cond_readers);
    pthread_cond_destroy(&rw->cond_writers);
}

void custom_rwlock_rdlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    while (rw->writer_active || rw->writers_waiting > 0) {
        pthread_cond_wait(&rw->cond_readers, &rw->mutex);
    }
    rw->readers++;
    pthread_mutex_unlock(&rw->mutex);
}

void custom_rwlock_rdunlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    rw->readers--;
    if (rw->readers == 0 && rw->writers_waiting > 0) {
        pthread_cond_signal(&rw->cond_writers);
    }
    pthread_mutex_unlock(&rw->mutex);
}

void custom_rwlock_wrlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    rw->writers_waiting++;
    while (rw->writer_active || rw->readers > 0) {
        pthread_cond_wait(&rw->cond_writers, &rw->mutex);
    }
    rw->writers_waiting--;
    rw->writer_active = true;
    pthread_mutex_unlock(&rw->mutex);
}

void custom_rwlock_wrunlock(custom_rwlock_t *rw) {
    pthread_mutex_lock(&rw->mutex);
    rw->writer_active = false;
    if (rw->writers_waiting > 0) {
        pthread_cond_signal(&rw->cond_writers);
    } else {
        pthread_cond_broadcast(&rw->cond_readers);
    }
    pthread_mutex_unlock(&rw->mutex);
}

// Тестовий спільний стан
static custom_rwlock_t g_lock;
static long            g_shared_value = 0;

void* reader_thread(void *arg) {
    long id = (long)arg;
    for (int i = 0; i < 5; ++i) {
        custom_rwlock_rdlock(&g_lock);
        // Безпечне читання спільного ресурсу
        long val = g_shared_value;
        usleep(1000); // Імітація роботи
        custom_rwlock_rdunlock(&g_lock);
    }
    return NULL;
}

void* writer_thread(void *arg) {
    long id = (long)arg;
    for (int i = 0; i < 3; ++i) {
        custom_rwlock_wrlock(&g_lock);
        // Монопольний запис у спільний ресурс
        g_shared_value += 10;
        usleep(2000); // Імітація запису
        custom_rwlock_wrunlock(&g_lock);
    }
    return NULL;
}
