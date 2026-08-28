#include <pthread.h>
#include <stdio.h>

int init_writer_preferring_rwlock(pthread_rwlock_t *rwlock) {
    pthread_rwlockattr_t attr;
    if (pthread_rwlockattr_init(&attr) != 0) {
        return -1;
    }

    // Встановлення пріоритету письменників без рекурсивного захоплення читачами
    pthread_rwlockattr_setkind_np(&attr, PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP);

    int res = pthread_rwlock_init(rwlock, &attr);
    pthread_rwlockattr_destroy(&attr);
    return res;
}
