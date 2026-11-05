#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#define NUM_THREADS 4
#define ITERATIONS 1000000

/* Спільний змінюваний стан */
volatile long global_counter = 0;

void* unsafe_increment(void* arg) {
    (void)arg;
    for (int i = 0; i < ITERATIONS; i++) {
        /* Незахищена некомутативна операція RMW */
        global_counter++;
    }
    return NULL;
}

int main(void) {
    pthread_t threads[NUM_THREADS];

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, unsafe_increment, NULL);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    /* Очікуваний результат: 4000000. Фактичний результат буде довільним і меншим */
    printf("Фактичний результат: %ld (Очікувалось: %d)\n",
           global_counter, NUM_THREADS * ITERATIONS);
    return 0;
}
