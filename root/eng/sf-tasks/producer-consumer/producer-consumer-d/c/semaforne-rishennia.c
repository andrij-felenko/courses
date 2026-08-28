#include <semaphore.h>
#include <pthread.h>

sem_t empty_slots; // Початкове значення = N (місткість)
sem_t full_slots;  // Початкове значення = 0
pthread_mutex_t mtx; // Початкове значення = 1

void producer(void* item) {
    sem_wait(&empty_slots); // P(empty_slots): чекаємо вільного місця
    pthread_mutex_lock(&mtx);

    // Критична секція: запис у буфер
    enqueue(item);

    pthread_mutex_unlock(&mtx);
    sem_post(&full_slots);  // V(full_slots): сповіщаємо про новий елемент
}

void* consumer(void) {
    sem_wait(&full_slots);  // P(full_slots): чекаємо появи даних
    pthread_mutex_lock(&mtx);

    // Критична секція: вилучення з буфера
    void* item = dequeue();

    pthread_mutex_unlock(&mtx);
    sem_post(&empty_slots); // V(empty_slots): сповіщаємо про звільнення місця
    return item;
}
