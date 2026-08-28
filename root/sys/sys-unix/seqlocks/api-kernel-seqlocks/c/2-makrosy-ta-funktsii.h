/* Статичне оголошення та ініціалізація автономного seqlock_t */
DEFINE_SEQLOCK(my_seqlock);

/* Статичне оголошення та ініціалізація голого seqcount_t */
seqcount_t my_seqcount = SEQCNT_ZERO(my_seqcount);

/* Динамічна ініціалізація seqlock_t у виділеній пам'яті */
void seqlock_init(seqlock_t *sl);

/* Динамічна ініціалізація голого seqcount_t */
void seqcount_init(seqcount_t *s);

/* Явна динамічна прив'язка seqcount до зовнішнього спін-замка для Lockdep */
void seqcount_spinlock_init(seqcount_spinlock_t *s, spinlock_t *lock);

/* Динамічна прив'язка seqcount до зовнішнього м'ютекса */
void seqcount_mutex_init(seqcount_mutex_t *s, struct mutex *lock);
