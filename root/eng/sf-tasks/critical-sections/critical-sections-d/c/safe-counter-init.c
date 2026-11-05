#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define NUM_THREADS 4
#define ITERATIONS 1000000

typedef struct {
    long counter;
    pthread_mutex_t lock;
} SafeCounter;

void safe_counter_init(SafeCounter* sc) {
    sc->counter = 0;
    pthread_mutex_init(&sc->lock, NULL);
}

void safe_counter_destroy(SafeCounter* sc) {
    pthread_mutex_destroy(&sc->lock);
}

void* safe_increment(void* arg) {
    SafeCounter* sc = (SafeCounter*)arg;
    for (int i = 0; i < ITERATIONS; i++) {
        /* Вхід у критичну секцію (встановлення просторової межі) */
        pthread_mutex_lock(&sc->lock);

        /* Критична секція: неподільна операція RMW */
        sc->counter++;

        /* Вихід з критичної секції */
        pthread_mutex_unlock(&sc->lock);
    }
    return NULL;
}

int main(void) {
    pthread_t threads[NUM_THREADS];
    SafeCounter counter;
    safe_counter_init(&counter);

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, safe_increment, &counter);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Результат захищеної критичної секції: %ld (Очікувалось: %d)\n",
           counter.counter, NUM_THREADS * ITERATIONS);

    safe_counter_destroy(&counter);
    return 0;
}
