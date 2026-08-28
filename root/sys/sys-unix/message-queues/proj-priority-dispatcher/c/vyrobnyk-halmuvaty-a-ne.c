/* виробник відкрив чергу БЕЗ O_NONBLOCK: mq_timedsend має право почекати */
static int send_order(mqd_t q, const char *body, size_t len, unsigned prio)
{
    struct timespec deadline;
    clock_gettime(CLOCK_REALTIME, &deadline);   /* саме REALTIME: так вимагає POSIX */
    deadline.tv_sec += 2;

    for (;;) {
        if (mq_timedsend(q, body, len, prio, &deadline) == 0) return 0;
        if (errno == EINTR)     continue;       /* сигнал — просто повторюємо */
        if (errno == ETIMEDOUT) return -1;      /* приймач стоїть: це тривога, не тиша */
        return -1;                              /* EMSGSIZE — помилка нашого формату */
    }
}
