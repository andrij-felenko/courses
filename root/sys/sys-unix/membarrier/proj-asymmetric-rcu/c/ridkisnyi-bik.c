static void barrier_all(void);         /* membarrier або запасний шлях */

static void synchronize_rcu(void)      /* викликається під замком письменників */
{
    struct reader *r;
    unsigned long now;

    barrier_all();                     /* (1) публікацію бачать усі читачі */
    now = __atomic_add_fetch(&gp, GEN_STEP, __ATOMIC_RELAXED);
    barrier_all();                     /* (2) нове покоління видиме; чужі слова читабельні */

    for (r = registry; r; r = r->next)
        for (;;) {
            unsigned long v = __atomic_load_n(&r->ctr, __ATOMIC_RELAXED);
            if ((v & NEST_MASK) == 0)          /* не в секції */
                break;
            if ((v & ~NEST_MASK) == (now & ~NEST_MASK))
                break;                         /* зайшов уже після (2) */
            usleep(20);
        }
}

void update_table(struct route *fresh)
{
    struct route *old = __atomic_exchange_n(&table, fresh, __ATOMIC_RELEASE);
    synchronize_rcu();
    free_table(old);
}
