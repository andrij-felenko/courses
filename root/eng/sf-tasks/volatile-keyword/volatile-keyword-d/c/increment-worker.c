#include <stdio.h>
#include <pthread.h>

#define NUM_THREADS 4
#define INCREMENTS_PER_THREAD 100000

/* volatile гарантує прямий доступ до RAM, але не атомарність інкременту */
volatile int shared_counter = 0;

void* increment_worker(void* arg) {
    (void)arg;
    for (int i = 0; i < INCREMENTS_PER_THREAD; i++) {
        /* Операція розбивається на зчитування, інкремент у регістрі та запис */
        shared_counter++;
    }
    return NULL;
}

int main(void) {
    pthread_t threads[NUM_THREADS];

    printf("[Головний потік]: Запуск %d потоків для інкременту лічильника...\n", NUM_THREADS);

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, increment_worker, NULL);
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    int expected = NUM_THREADS * INCREMENTS_PER_THREAD;
    printf("[Результат]: Очікувано = %d, Фактично = %d (втрачено %d оновлень)\n",
           expected, shared_counter, expected - shared_counter);

    return 0;
}
