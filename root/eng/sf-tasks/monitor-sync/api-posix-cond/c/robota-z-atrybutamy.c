#include <pthread.h>
#include <time.h>
#include <stdio.h>

int init_monotonic_condition(pthread_cond_t *cond) {
    pthread_condattr_t attr;
    int rc;

    rc = pthread_condattr_init(&attr);
    if (rc != 0) return rc;

    /* Встановлюємо монотонний годинник для тайм-аутів */
    rc = pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);
    if (rc != 0) {
        pthread_condattr_destroy(&attr);
        return rc;
    }

    rc = pthread_cond_init(cond, &attr);
    pthread_condattr_destroy(&attr);
    return rc;
}
