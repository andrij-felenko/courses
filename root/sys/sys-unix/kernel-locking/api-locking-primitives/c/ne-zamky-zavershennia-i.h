atomic_t counter = ATOMIC_INIT(0);

int  atomic_read(const atomic_t *v);            /* READ_ONCE — упорядкування НЕ дає  */
void atomic_set(atomic_t *v, int i);            /* WRITE_ONCE — так само             */

void atomic_inc(atomic_t *v);                   /* без повернення → НЕвпорядковані   */
void atomic_add(int i, atomic_t *v);
bool atomic_dec_and_test(atomic_t *v);          /* 1, якщо стало нулем               */
bool atomic_add_unless(atomic_t *v, int a, int u);

int  atomic_inc_return(atomic_t *v);            /* із поверненням → ПОВНІ бар'єри    */
int  atomic_fetch_add(int i, atomic_t *v);
int  atomic_cmpxchg(atomic_t *v, int old, int new);
bool atomic_try_cmpxchg(atomic_t *v, int *old, int new);

/* послаблені різновиди тих самих операцій */
atomic_inc_return_relaxed(v);  atomic_fetch_add_acquire(i, v);  atomic_fetch_add_release(i, v);
smp_mb__before_atomic();  smp_mb__after_atomic();   /* добудувати бар'єр до невпорядкованої */
