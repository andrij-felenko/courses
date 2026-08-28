#include <pthread.h>
#include <errno.h>
#include <stdio.h>

int lock_robust_mutex(pthread_mutex_t *mutex, void *shm_state) {
    int rc = pthread_mutex_lock(mutex);
    if (rc == EOWNERDEAD) {
        printf("[Відновлення] Попередній процес загинув! Відновлення цілісності...\n");
        /* Відновлення інваріантів спільного буфера */
        pthread_mutex_consistent(mutex);
        return 0;
    } else if (rc == ENOTRECOVERABLE) {
        fprintf(stderr, "[Помилка] Спільний стан пошкоджено незворотно!\n");
        return -1;
    }
    return rc;
}
