#include <pthread.h>
#include <stdio.h>
#include <string.h>

void rwlock_cleanup_handler(void *arg) {
    pthread_rwlock_t *rwlock = (pthread_rwlock_t *)arg;
    pthread_rwlock_unlock(rwlock);
}

void safe_cancellation_read(pthread_rwlock_t *rwlock, char *shared_data, char *out_buf, size_t len) {
    pthread_rwlock_rdlock(rwlock);
    pthread_cleanup_push(rwlock_cleanup_handler, (void *)rwlock);

    // Критична секція читання з потенційними точками скасування (наприклад, операції вводу-виводу)
    strncpy(out_buf, shared_data, len - 1);
    out_buf[len - 1] = '\0';

    // 0 означає не викликати обробник зараз, але безпечно зняти його зі стека
    pthread_cleanup_pop(0);
    pthread_rwlock_unlock(rwlock);
}
