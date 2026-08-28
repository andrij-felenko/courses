static struct pcstat_obj *depot_pop(void)
{
    struct pcstat_depot *d;
    struct pcstat_obj *o = NULL;
    unsigned long flags;

    local_lock_irqsave(&pcstat_depot.lock, flags);
    d = this_cpu_ptr(&pcstat_depot);        /* вказівник беремо ВСЕРЕДИНІ ділянки */
    if (d->count) {
        o = list_first_entry(&d->free, struct pcstat_obj, node);
        list_del(&o->node);
        d->count--;
    }
    local_unlock_irqrestore(&pcstat_depot.lock, flags);

    return o;
}

static void depot_push(struct pcstat_obj *o)
{
    struct pcstat_depot *d;
    bool overflow = false;
    unsigned long flags;

    local_lock_irqsave(&pcstat_depot.lock, flags);
    d = this_cpu_ptr(&pcstat_depot);
    if (d->count < DEPOT_HIGH) {
        list_add(&o->node, &d->free);
        d->count++;
    } else {
        overflow = true;
    }
    local_unlock_irqrestore(&pcstat_depot.lock, flags);

    if (overflow)
        kfree(o);            /* звільняємо ПІСЛЯ виходу з ділянки */
}
