struct depot {
    local_lock_t     lock;
    struct list_head free;
    unsigned int     count;
};

static DEFINE_PER_CPU(struct depot, depot) = {
    .lock = INIT_LOCAL_LOCK(lock),
};

static struct obj *depot_pop(void)
{
    struct depot *d;
    struct obj *o = NULL;

    local_lock(&depot.lock);        /* саме ця структура, саме цей захист */
    d = this_cpu_ptr(&depot);
    if (d->count) {
        o = list_first_entry(&d->free, struct obj, node);
        list_del(&o->node);
        d->count--;
    }
    local_unlock(&depot.lock);
    return o;
}
