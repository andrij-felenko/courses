#define NEST_MASK  0x7fUL              /* сім молодших бітів — глибина */
#define GEN_STEP   0x80UL              /* крок покоління — перший біт над нею */

struct reader {
    _Alignas(64) unsigned long ctr;    /* покоління | глибина */
    struct reader *next;
};

static unsigned long gp;               /* покоління; піднімає лише письменник */
static struct reader *registry;
static __thread struct reader *self;

static inline void rcu_read_lock(void)
{
    unsigned long v = self->ctr;                       /* слово своє — гонок нема */
    if ((v & NEST_MASK) == 0)
        v = __atomic_load_n(&gp, __ATOMIC_RELAXED) | 1;  /* зовнішній вхід */
    else
        v = v + 1;                                     /* вкладений — лише глибина */
    __atomic_store_n(&self->ctr, v, __ATOMIC_RELAXED);
    __atomic_signal_fence(__ATOMIC_SEQ_CST);           /* бар'єр компілятора */
}

static inline void rcu_read_unlock(void)
{
    unsigned long v = __atomic_load_n(&self->ctr, __ATOMIC_RELAXED);
    __atomic_signal_fence(__ATOMIC_SEQ_CST);
    __atomic_store_n(&self->ctr, v - 1, __ATOMIC_RELAXED);
}

#define rcu_dereference(p) __atomic_load_n(&(p), __ATOMIC_RELAXED)
