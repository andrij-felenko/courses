#include <stdio.h>
#include <pthread.h>

#define NUM_THREADS 4
#define INCREMENTS_PER_THREAD 1000000

// Спільний лічильник без атомарного захисту
long shared_counter = 0;

void* count_unsynchronized(void* arg) {
    for (int i = 0; i < INCREMENTS_PER_THREAD; ++i) {
        // Цикл зчитування-модифікації-запису виконується неконкурентно-безпечно.
        // Інструкції розбиваються на mov, add, mov.
        shared_counter++;
    }
    return NULL;
}

int main(void) {
    pthread_t threads[NUM_THREADS];

    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_create(&threads[i], NULL, count_unsynchronized, NULL);
    }

    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Очікуваний результат: 4,000,000. Реальний результат буде набагато меншим через втрачені оновлення.
    printf("Фактичне значення лічильника: %ld (Очікувалося: %d)\n", 
           shared_counter, NUM_THREADS * INCREMENTS_PER_THREAD);
    return 0;
}
