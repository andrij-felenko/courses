#include <stdio.h>
#include <pthread.h>

/* Глобальна потоко-локальна змінна мовою C */
__thread int thread_counter = 0;

void increment_counter(void) {
    thread_counter++;
    printf("Thread %lu: counter = %d\n", (unsigned long)pthread_self(), thread_counter);
}
