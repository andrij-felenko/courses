DEFINE_STATIC_KEY_FALSE(sched_numa_balancing);

static void task_tick_fair(struct rq *rq, struct task_struct *curr)
{
        if (static_branch_unlikely(&sched_numa_balancing))
                task_tick_numa(rq, curr);

        update_misfit_status(curr, rq);
}

/* десь у налаштуванні підсистеми, дуже рідко: */
static_branch_enable(&sched_numa_balancing);
