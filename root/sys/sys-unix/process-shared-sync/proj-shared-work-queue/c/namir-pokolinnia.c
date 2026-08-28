static int wq_push(struct wq *q, const void *buf, uint32_t len, int die_now)
{
    const uint8_t *p = buf;
    CK(len <= WQ_PAYLOAD);
    struct timespec dl = deadline_ms(2000);

    wq_lock(q);
    while (atomic_load(&q->tail) - atomic_load(&q->head) == WQ_SLOTS) {
        int rc = pthread_cond_timedwait(&q->not_full, &q->lock, &dl);
        if (rc == EOWNERDEAD) { wq_recover(q); continue; }
        if (rc == ETIMEDOUT)  { pthread_mutex_unlock(&q->lock); return -1; }
        CK(rc == 0);
    }

    uint64_t T = atomic_load(&q->tail);
    struct slot *s = &q->ring[T & (WQ_SLOTS - 1)];
    uint64_t g = atomic_load(&s->gen);           /* парне: слот у спокої */

    atomic_store(&q->op_index, T);               /* 1 · намір — ПЕРЕД кільцем */
    atomic_store(&q->op_gen,   g);
    atomic_store(&q->op,       OP_PUSH);

    atomic_store(&s->gen, g + 1);                /* 2 · непарне: слот у роботі */
    s->len = len;                                /* 3 · копіюємо дані           */
    memcpy(s->data, p, len / 2);
    if (die_now) raise(SIGKILL);                 /*    ← те саме, що kill -9 ззовні */
    memcpy(s->data + len / 2, p + len / 2, len - len / 2);
    atomic_store(&s->gen, g + 2);                /* 4 · парне: запис цілий      */

    atomic_store(&q->tail, T + 1);               /* 5 · ПУБЛІКАЦІЯ              */
    atomic_store(&q->op, OP_NONE);               /* 6 · намір знято             */

    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return 0;
}
