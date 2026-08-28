static enum cpuhp_state hp_state;

static int mycache_cpu_online(unsigned int cpu)
{
        struct mycache *c = per_cpu_ptr(&mycache, cpu);

        c->head = NULL;
        c->count = 0;
        return 0;
}

static int mycache_cpu_dying(unsigned int cpu)
{
        struct mycache *c = per_cpu_ptr(&mycache, cpu);

        mycache_drain(c);       /* віддати запас у спільний пул */
        return 0;
}

static int __init mycache_init(void)
{
        int ret = cpuhp_setup_state(CPUHP_AP_ONLINE_DYN, "mycache:online",
                                    mycache_cpu_online, mycache_cpu_dying);
        if (ret < 0)
                return ret;

        hp_state = ret;
        return 0;
}
