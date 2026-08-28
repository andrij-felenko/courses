/* Початок спроби читання. 
   Повертає поточне значення лічильника seq.
   Виконує smp_rmb(). Якщо seq непарне — спінить до парного. */
unsigned read_seqbegin(const seqlock_t *sl);

/* Перевірка цілісності після прочитання даних.
   Виконує smp_rmb().
   Повертає true (1), якщо запис відбувся, вимагаючи повтору циклу. */
unsigned read_seqretry(const seqlock_t *sl, unsigned start_seq);

/* Аналогічні операції для голого seqcount_t */
unsigned read_seqcount_begin(const seqcount_t *s);
unsigned read_seqcount_retry(const seqcount_t *s, unsigned start_seq);
