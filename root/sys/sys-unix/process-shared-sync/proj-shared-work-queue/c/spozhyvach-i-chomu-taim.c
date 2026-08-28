static int wq_pop(struct wq *q, void *out, uint32_t *len, int ms)
{
    struct timespec dl = deadline_ms(ms);

    wq_lock(q);
    while (atomic_load(&q->head) == atomic_load(&q->tail)) {
        int rc = pthread_cond_timedwait(&q->not_empty, &q->lock, &dl);
        if (rc == EOWNERDEAD) { wq_recover(q); continue; }   /* замок віддано нам */
        if (rc == ETIMEDOUT)  { pthread_mutex_unlock(&q->lock); return -1; }
        CK(rc == 0);              /* EINTR звідси не буває — лише хибні побудки */
    }

    uint64_t H = atomic_load(&q->head);
    struct slot *s = &q->ring[H & (WQ_SLOTS - 1)];

    atomic_store(&q->op_index, H);
    atomic_store(&q->op_gen, atomic_load(&s->gen));
    atomic_store(&q->op, OP_POP);

    uint32_t n = s->len > WQ_PAYLOAD ? WQ_PAYLOAD : s->len;  /* довжині з чужої */
    memcpy(out, s->data, n); *len = n;                       /* пам'яті не віримо */
    atomic_store(&q->head, H + 1);            /* точка невороття: задачу видано */
    atomic_store(&q->op, OP_NONE);

    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return 0;
}
