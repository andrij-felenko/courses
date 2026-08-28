#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

pthread_mutex_t mutex_a = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mutex_b = PTHREAD_MUTEX_INITIALIZER;

void* worker_1(void* arg) {
    (void)arg;
    pthread_mutex_lock(&mutex_a);
    sleep(1); // Симуляція проміжної роботи
    pthread_mutex_lock(&mutex_b); // Зависає в очікуванні mutex_b

    pthread_mutex_unlock(&mutex_b);
    pthread_mutex_unlock(&mutex_a);
    return NULL;
}

void* worker_2(void* arg) {
    (void)arg;
    pthread_mutex_lock(&mutex_b);
    sleep(1); // Симуляція проміжної роботи
    pthread_mutex_lock(&mutex_a); // Зависає в очікуванні mutex_a

    pthread_mutex_unlock(&mutex_a);
    pthread_mutex_unlock(&mutex_b);
    return NULL;
}
