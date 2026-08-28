static DEFINE_PER_CPU(call_single_data_t, poke_csd);

static int __init poke_init(void)
{
        int cpu;

        for_each_possible_cpu(cpu)
                INIT_CSD(per_cpu_ptr(&poke_csd, cpu), say_where, NULL);
        return 0;
}

/* кличеться звідки завгодно, зокрема з вимкненими перериваннями */
static void poke_async(int cpu)
{
        int err = smp_call_function_single_async(cpu, per_cpu_ptr(&poke_csd, cpu));

        /* -EBUSY: дзвінок уже в дорозі, другий зайвий; -ENXIO: ядра немає */
        if (err && err != -EBUSY)
                pr_warn("ядро %d недосяжне: %d\n", cpu, err);
}
