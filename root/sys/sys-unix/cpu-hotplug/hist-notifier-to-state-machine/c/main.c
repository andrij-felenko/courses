static int foo_cpu_notify(struct notifier_block *nb,
                          unsigned long action, void *hcpu)
{
        unsigned int cpu = (unsigned long)hcpu;

        switch (action & ~CPU_TASKS_FROZEN) {
        case CPU_UP_PREPARE:
                return foo_alloc(cpu) ? NOTIFY_BAD : NOTIFY_OK;
        case CPU_ONLINE:
                foo_start(cpu);
                break;
        case CPU_DOWN_PREPARE:
                foo_stop(cpu);
                break;
        case CPU_DEAD:
                foo_free(cpu);
                break;
        }
        return NOTIFY_OK;
}

static struct notifier_block foo_nb = {
        .notifier_call = foo_cpu_notify,
        .priority      = 10,   /* єдиний важіль порядку */
};

register_cpu_notifier(&foo_nb);
