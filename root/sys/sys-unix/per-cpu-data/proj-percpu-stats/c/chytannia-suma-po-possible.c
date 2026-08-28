static int pcstat_stats_show(struct seq_file *m, void *v)
{
    struct pcstat_counters total = { };
    unsigned int stashed = 0;
    int cpu;

    seq_puts(m, "cpu      events        bytes    misses   refills  depot\n");

    for_each_possible_cpu(cpu) {
        struct pcstat_counters *c = per_cpu_ptr(&pcstat_cnt, cpu);
        struct pcstat_depot *d = per_cpu_ptr(&pcstat_depot, cpu);
        u64 ev = READ_ONCE(c->events);
        unsigned int n = READ_ONCE(d->count);

        total.events  += ev;
        total.bytes   += READ_ONCE(c->bytes);
        total.misses  += READ_ONCE(c->misses);
        total.refills += READ_ONCE(c->refills);
        stashed       += n;

        if (cpu_online(cpu) || ev)
            seq_printf(m, "%-4d %10llu %12llu %9llu %9llu %6u%s\n",
                       cpu, ev, READ_ONCE(c->bytes), READ_ONCE(c->misses),
                       READ_ONCE(c->refills), n,
                       cpu_online(cpu) ? "" : "  (вимкнене)");
    }

    seq_printf(m, "разом %9llu %12llu %9llu %9llu %6u\n",
               total.events, total.bytes, total.misses, total.refills, stashed);
    seq_printf(m, "у смітнику: %u\n", READ_ONCE(pcstat_attic_count));
    seq_printf(m, "possible: %u  online: %u\n",
               num_possible_cpus(), num_online_cpus());
    return 0;
}
DEFINE_SHOW_ATTRIBUTE(pcstat_stats);
