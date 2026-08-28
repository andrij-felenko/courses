DEFINE_SPINLOCK(name);                 /* статично */
spin_lock_init(&lock);                 /* динамічно, обов'язково до першого взяття */

void spin_lock(spinlock_t *lock);
void spin_lock_bh(spinlock_t *lock);           /* + заборона нижніх половин */
void spin_lock_irq(spinlock_t *lock);          /* + закриття переривань, беззастережне */
void spin_lock_irqsave(spinlock_t *lock, unsigned long flags);   /* макрос: flags — вихідний */

void spin_unlock(spinlock_t *lock);
void spin_unlock_bh(spinlock_t *lock);
void spin_unlock_irq(spinlock_t *lock);
void spin_unlock_irqrestore(spinlock_t *lock, unsigned long flags);

int  spin_trylock(spinlock_t *lock);           /* 1 — узяли, 0 — зайнято */
int  spin_trylock_bh(spinlock_t *lock);
int  spin_trylock_irqsave(spinlock_t *lock, unsigned long flags);

void spin_lock_nested(spinlock_t *lock, int subclass);  /* два замки одного класу — для lockdep */
int  spin_is_locked(spinlock_t *lock);         /* лише для налагодження */
void assert_spin_locked(spinlock_t *lock);
