#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    pthread_mutex_t lock;
    uint64_t shared_counter;
} safe_counter_t;

void safe_counter_init(safe_counter_t *counter) {
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    
    /* Налаштування протоколу успадкування пріоритету для запобігання інверсії */
    pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
    pthread_mutex_init(&counter->lock, &attr);
    pthread_mutexattr_destroy(&attr);
    
    counter->shared_counter = 0;
}

void safe_counter_add(safe_counter_t *counter, uint64_t value) {
    pthread_mutex_lock(&counter->lock);
    counter->shared_counter += value;
    pthread_mutex_unlock(&counter->lock);
}
