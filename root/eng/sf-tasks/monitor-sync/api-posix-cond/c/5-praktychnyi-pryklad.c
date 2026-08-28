#include <pthread.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>

typedef struct {
    pthread_mutex_t mtx;
    pthread_cond_t cv;
    bool ready;
} event_flag_t;

int event_flag_init(event_flag_t *e) {
    e->ready = false;
    pthread_mutex_init(&e->mtx, NULL);

    pthread_condattr_t attr;
    pthread_condattr_init(&attr);
    pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
    pthread_cond_init(&e->cv, &attr);
    pthread_condattr_destroy(&attr);
    return 0;
}

bool event_flag_wait(event_flag_t *e, long timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    pthread_mutex_lock(&e->mtx);
    while (!e->ready) {
        int rc = pthread_cond_timedwait(&e->cv, &e->mtx, &ts);
        if (rc == ETIMEDOUT) {
            break;
        }
    }
    bool status = e->ready;
    pthread_mutex_unlock(&e->mtx);
    return status;
}

void event_flag_set(event_flag_t *e) {
    pthread_mutex_lock(&e->mtx);
    e->ready = true;
    pthread_cond_broadcast(&e->cv);
    pthread_mutex_unlock(&e->mtx);
}

void event_flag_destroy(event_flag_t *e) {
    pthread_mutex_destroy(&e->mtx);
    pthread_cond_destroy(&e->cv);
}
