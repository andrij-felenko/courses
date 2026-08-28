/* Отримання з'єднання з пулу з контролем дедлайну */
int acquire_connection_with_deadline(pthread_mutex_t *pool_lock,
                                     pthread_cond_t *pool_cond,
                                     int *pool_slots_available,
                                     const deadline_context_t *ctx) {
    pthread_mutex_lock(pool_lock);

    while (*pool_slots_available <= 0) {
        int64_t remain_ms = context_remaining_ms(ctx);
        if (remain_ms <= 0) {
            pthread_mutex_unlock(pool_lock);
            errno = ETIMEDOUT;
            return -1; /* Час у черзі пулу вичерпано */
        }

        /* Переведення залишку мілісекунд в абсолютний таймспек на CLOCK_REALTIME */
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += remain_ms / 1000;
        ts.tv_nsec += (remain_ms % 1000) * 1000000;
        if (ts.tv_nsec >= 1000000000) {
            ts.tv_sec += 1;
            ts.tv_nsec -= 1000000000;
        }

        int ret = pthread_cond_timedwait(pool_cond, pool_lock, &ts);
        if (ret == ETIMEDOUT) {
            pthread_mutex_unlock(pool_lock);
            errno = ETIMEDOUT;
            return -1;
        }
    }

    (*pool_slots_available)--;
    pthread_mutex_unlock(pool_lock);
    return 0; /* З'єднання успішно виділено */
}
