static struct dentry *pcstat_dir;
static int pcstat_hp_state = -1;

static int __init pcstat_init(void)
{
    int cpu, ret;

    for_each_possible_cpu(cpu) {
        struct pcstat_depot *d = per_cpu_ptr(&pcstat_depot, cpu);

        INIT_LIST_HEAD(&d->free);   /* статично цього зробити НЕ можна — пастка 4 */
        d->count = 0;
    }

    pcstat_dir = debugfs_create_dir("pcstat", NULL);
    debugfs_create_file("stats",  0444, pcstat_dir, NULL, &pcstat_stats_fops);
    debugfs_create_file("refill", 0200, pcstat_dir, NULL, &pcstat_refill_fops);
    debugfs_create_file("bench",  0200, pcstat_dir, NULL, &pcstat_bench_fops);
    debugfs_create_u32("period_ms", 0644, pcstat_dir, &period_ms);

    ret = cpuhp_setup_state(CPUHP_AP_ONLINE_DYN, "pcstat:online",
                            pcstat_cpu_online, pcstat_cpu_offline);
    if (ret < 0) {
        debugfs_remove_recursive(pcstat_dir);
        return ret;
    }
    pcstat_hp_state = ret;

    timer_setup(&pcstat_timer, pcstat_tick, 0);
    mod_timer(&pcstat_timer, jiffies + msecs_to_jiffies(period_ms));

    pr_info("завантажено; possible=%u online=%u\n",
            num_possible_cpus(), num_online_cpus());
    return 0;
}

static void __exit pcstat_exit(void)
{
    struct pcstat_obj *o, *tmp;
    int cpu;

    timer_shutdown_sync(&pcstat_timer);    /* 1. більше не вистрелить і не переозброїться */
    debugfs_remove_recursive(pcstat_dir);  /* 2. зовнішній вхід зачинено                  */
    cpuhp_remove_state(pcstat_hp_state);   /* 3. кличе гак на КОЖНОМУ ввімкненому ядрі    */

    /* 4. тепер не біжить ніхто — замки вже не потрібні */
    for_each_possible_cpu(cpu) {
        struct pcstat_depot *d = per_cpu_ptr(&pcstat_depot, cpu);

        list_for_each_entry_safe(o, tmp, &d->free, node) {
            list_del(&o->node);
            kfree(o);
        }
    }
    list_for_each_entry_safe(o, tmp, &pcstat_attic, node) {
        list_del(&o->node);
        kfree(o);
    }
    pr_info("вивантажено\n");
}

module_init(pcstat_init);
module_exit(pcstat_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Статистика per-CPU: this_cpu_*, local_lock, гак cpuhp");
