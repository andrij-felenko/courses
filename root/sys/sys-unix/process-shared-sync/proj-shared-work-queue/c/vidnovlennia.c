static void wq_recover(struct wq *q)
{
    uint32_t op = atomic_load(&q->op);

    if (op == OP_PUSH) {
        uint64_t T = atomic_load(&q->op_index), g = atomic_load(&q->op_gen);
        struct slot *s = &q->ring[T & (WQ_SLOTS - 1)];
        uint64_t now = atomic_load(&s->gen);

        if (now == g) {
            fprintf(stderr, "[віднов] намір був, кільця не торкнулися\n");
        } else if (now == g + 1) {               /* ВІДКІТ: дані рвані */
            atomic_store(&s->gen, g + 2);        /* слот знову «цілий», але порожній */
            fprintf(stderr, "[віднов] слот %llu рваний — відкинуто\n",
                    (unsigned long long)T);      /* tail не рухаємо: запису не було */
        } else if (now == g + 2 && atomic_load(&q->tail) == T) {
            atomic_store(&q->tail, T + 1);       /* ДОКОЧУВАННЯ: запис цілий */
            fprintf(stderr, "[віднов] слот %llu цілий — докочено\n",
                    (unsigned long long)T);
        }
    }
    /* OP_POP: якщо head не зрушив, задача лишається в черзі й буде видана вдруге.
       Свідомий вибір «щонайменше раз»: чи встиг мрець її виконати, знати нізвідки. */
    atomic_store(&q->op, OP_NONE);

    /* Цілісність кільця, незалежна від наміру: непарних поколінь бути не сміє,
       а зайнятих слотів — не більше, ніж їх є. */
    for (uint32_t j = 0; j < WQ_SLOTS; j++)
        CK((atomic_load(&q->ring[j].gen) & 1) == 0);
    CK(atomic_load(&q->tail) - atomic_load(&q->head) <= WQ_SLOTS);

    CK(pthread_mutex_consistent(&q->lock) == 0);   /* без цього замок помре назавжди */
}
