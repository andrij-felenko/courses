typedef struct {
    const QuotientFilter *qf;
    size_t curr_slot;
    size_t curr_fq;
} QFIterator;

/* Ініціалізація ітератора на початку таблиці */
void qf_iter_init(QFIterator *iter, const QuotientFilter *qf);

/* Отримання наступного відбитка (повертає false після вичерпання таблиці) */
bool qf_iter_next(QFIterator *iter, uint64_t *out_hash);
