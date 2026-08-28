/* Початок запису: перевірка Lockdep + seq++ (стає непарним) + smp_wmb() */
void write_seqcount_begin(seqcount_t *s);

/* Завершення запису: smp_wmb() + seq++ (стає парним) */
void write_seqcount_end(seqcount_t *s);

/* Сирий варіант без перевірок Lockdep (використовується рідко у критичних місцях) */
void raw_write_seqcount_begin(seqcount_t *s);
void raw_write_seqcount_end(seqcount_t *s);

/* Примусова інвалідація лічильника без виконання модифікації полів */
void write_seqcount_invalidate(seqcount_t *s);
