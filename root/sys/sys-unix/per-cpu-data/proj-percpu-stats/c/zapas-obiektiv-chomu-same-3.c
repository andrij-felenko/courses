static int depot_refill(void)
{
    struct pcstat_obj *o = kmalloc(sizeof(*o), GFP_KERNEL);   /* може заснути */

    if (!o)
        return -ENOMEM;

    o->payload = 0;
    depot_push(o);                    /* а вже тут — під замком, без сну */
    this_cpu_inc(pcstat_cnt.refills);
    return 0;
}
