static struct timer_list pcstat_timer;
static unsigned int period_ms = 10;

static void pcstat_tick(struct timer_list *t)
{
    struct pcstat_obj *o;

    this_cpu_inc(pcstat_cnt.events);

    o = depot_pop();                 /* спати не можна — беремо лише те, що вже є */
    if (o) {
        o->payload = (u32)jiffies;
        this_cpu_add(pcstat_cnt.bytes, sizeof(*o));
        depot_push(o);
    } else {
        this_cpu_inc(pcstat_cnt.misses);
    }

    mod_timer(t, jiffies + msecs_to_jiffies(READ_ONCE(period_ms)));
}
