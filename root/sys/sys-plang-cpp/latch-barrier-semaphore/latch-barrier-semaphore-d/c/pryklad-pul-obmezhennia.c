#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

/* У чистому C під POSIX використовується sem_t із <semaphore.h> */
sem_t g_posix_sem;

void* client_task(void* arg) {
    long id = (long)arg;
    
    // sem_wait() еквівалентний acquire()
    sem_wait(&g_posix_sem);
    
    printf("[POSIX Client %ld] Отримав з'єднання...\n", id);
    usleep(50000); // 50 мс
    printf("[POSIX Client %ld] Завершив роботу.\n", id);
    
    // sem_post() еквівалентний release()
    sem_post(&g_posix_sem);
    return NULL;
}
