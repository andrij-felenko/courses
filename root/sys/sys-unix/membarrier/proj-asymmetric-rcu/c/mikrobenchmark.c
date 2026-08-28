static double loop(int fenced)
{
    struct timespec a, b;
    const long N = 50L * 1000 * 1000;
    volatile unsigned long sink = 0;

    clock_gettime(CLOCK_MONOTONIC, &a);
    for (long i = 0; i < N; i++) {
        rcu_read_lock();
        if (fenced)
            __atomic_thread_fence(__ATOMIC_SEQ_CST);   /* те, що ми прибрали */
        sink += rcu_dereference(table) != NULL;
        rcu_read_unlock();
    }
    clock_gettime(CLOCK_MONOTONIC, &b);
    return ((b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec)) / (double)N;
}
