/* Смітник для об'єктів із вимкнених ядер: тут суперник справжній,
   з інших процесорів, — тому й замок справжній. */
static DEFINE_SPINLOCK(pcstat_attic_lock);
static LIST_HEAD(pcstat_attic);
static unsigned int pcstat_attic_count;

static int pcstat_cpu_online(unsigned int cpu)
{
    int i;

    /* Гак ONLINE-секції виконується в потоці cpuhp/N на самому ядрі,
       витіснення й переривання дозволені — тобто ТУТ спати можна. */
    for (i = 0; i < DEPOT_WARM; i++)
        if (depot_refill())
            break;           /* нема пам'яті — гріємо як вийде, вмикання не зриваємо */
    return 0;
}

static int pcstat_cpu_offline(unsigned int cpu)
{
    struct pcstat_depot *d;
    LIST_HEAD(drained);
    unsigned long flags;
    unsigned int n;

    /* cpu == smp_processor_id(): гак біжить на тому ядрі, що йде геть.
       Воно ще онлайн, таймери й переривання на ньому ще працюють. */
    local_lock_irqsave(&pcstat_depot.lock, flags);
    d = this_cpu_ptr(&pcstat_depot);
    list_splice_init(&d->free, &drained);
    n = d->count;
    d->count = 0;
    local_unlock_irqrestore(&pcstat_depot.lock, flags);

    spin_lock(&pcstat_attic_lock);
    list_splice_init(&drained, &pcstat_attic);
    pcstat_attic_count += n;
    spin_unlock(&pcstat_attic_lock);

    pr_info("ядро %u гасне: здано об'єктів — %u\n", cpu, n);
    return 0;
}
