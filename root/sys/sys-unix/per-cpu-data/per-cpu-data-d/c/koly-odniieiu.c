static DEFINE_PER_CPU(struct depot, depot);

static struct obj *depot_pop(void)
{
    unsigned long flags;
    struct depot *d;
    struct obj *o = NULL;

    local_irq_save(flags);          /* заборонити переривання на цьому ядрі процесора */
    d = this_cpu_ptr(&depot);
    if (d->count) {
        o = list_first_entry(&d->free, struct obj, node);
        list_del(&o->node);
        d->count--;
    }
    local_irq_restore(flags);
    return o;
}
