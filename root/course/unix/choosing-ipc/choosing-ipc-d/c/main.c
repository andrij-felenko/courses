/* Налаштування робастного м'ютекса у спільній пам'яті */
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
pthread_mutexattr_setrobust(&attr, PTHREAD_MUTEX_ROBUST);

pthread_mutex_t *mutex = (pthread_mutex_t*)shm_ptr;
pthread_mutex_init(mutex, &attr);
pthread_mutexattr_destroy(&attr);

/* Захоплення з обробкою аварії партнера */
int rc = pthread_mutex_lock(mutex);
if (rc == EOWNERDEAD) {
    /* Попередній власник загинув усередині критичної секції! */
    /* 1. Відновлюємо інваріанти даних (наприклад, очищаємо напівзаписаний елемент) */
    repair_inconsistent_data(shm_ptr);
    
    /* 2. Фіксуємо узгодженість м'ютекса */
    pthread_mutex_consistent(mutex);
}
/* Продовжуємо роботу у критичній секції */
do_critical_work(shm_ptr);
pthread_mutex_unlock(mutex);
