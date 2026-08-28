static void wq_recover(struct wq *q);                    /* нижче */

static struct timespec deadline_ms(int ms)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);      /* ТОЙ САМИЙ годинник, що в condattr */
    t.tv_sec += ms / 1000;
    t.tv_nsec += (long)(ms % 1000) * 1000000L;
    if (t.tv_nsec >= 1000000000L) { t.tv_sec++; t.tv_nsec -= 1000000000L; }
    return t;
}

static void wq_lock(struct wq *q)
{
    int rc = pthread_mutex_lock(&q->lock);
    if (rc == EOWNERDEAD) {          /* замок НАШ, але під ним лишився мрець */
        wq_recover(q);               /* усередині — pthread_mutex_consistent */
    } else if (rc == ENOTRECOVERABLE) {
        fprintf(stderr, "черга непоправна — лишається shm_unlink і почати з чистого\n");
        _exit(2);
    } else CK(rc == 0);
}
