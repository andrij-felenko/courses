struct depot {
        local_lock_t     lock;
        struct list_head free;
        unsigned int     count;
};

static DEFINE_PER_CPU(struct depot, depot) = {
        .lock = INIT_LOCAL_LOCK(lock),
};
static DEFINE_PER_CPU(unsigned long, hits);

static struct obj *depot_pop(void)
{
        struct depot *d;
        struct obj *o = NULL;

        local_lock(&depot.lock);        /* витіснення закрито   */
        d = this_cpu_ptr(&depot);       /* адреса дійсна тут    */
        lockdep_assert_held(this_cpu_ptr(&depot.lock));
        if (d->count) {
                o = list_first_entry(&d->free, struct obj, node);
                list_del(&o->node);
                d->count--;
                __this_cpu_inc(hits);   /* можна без гарантій:  */
        }                               /* витіснення вже нема  */
        local_unlock(&depot.lock);
        return o;
}

static unsigned long depot_hits(void)
{
        unsigned long total = 0;
        int cpu;

        for_each_possible_cpu(cpu)      /* possible, не online  */
                total += per_cpu(hits, cpu);
        return total;                   /* сума з різних митей  */
}
