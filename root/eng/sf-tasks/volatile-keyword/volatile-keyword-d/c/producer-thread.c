#include <stdio.h>
#include <stdbool.h>
#include <pthread.h>
#include <stdatomic.h>

/* Використання volatile забороняє оптимізації компілятора, але не апаратні перевпорядкування */
volatile int payload = 0;
volatile bool ready = false;

void* producer_thread(void* arg) {
    (void)arg;
    payload = 42; /* Крок 1: Підготовка даних */

    /* Апаратний бар'єр пам'яті примусово скидає буфери запису до оновлення ready */
    atomic_thread_fence(memory_order_release);

    ready = true; /* Крок 2: Публікація прапорця */
    return NULL;
}

void* consumer_thread(void* arg) {
    (void)arg;
    while (!ready) {
        /* Очікування прапорця */
    }

    /* Апаратний бар'єр гарантує впорядковане читання payload після прапорця ready */
    atomic_thread_fence(memory_order_acquire);

    printf("[Споживач]: Отримано payload = %d\n", payload);
    return NULL;
}

int main(void) {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, producer_thread, NULL);
    pthread_create(&t2, NULL, consumer_thread, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
