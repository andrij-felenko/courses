static atomic64_t bench_shared = ATOMIC64_INIT(0);
static DEFINE_PER_CPU(u64, bench_own);
static DEFINE_PER_CPU(u64, bench_ops);

static unsigned int bench_ms = 200;
static bool bench_atomic;

#define BENCH_CHUNK 4096

struct bench_ctl { atomic_t ready, go; };

static int bench_worker(void *arg)
{
    struct bench_ctl *c = arg;
    u64 t0, now, deadline, ops = 0;
    int i;

    atomic_inc(&c->ready);
    while (!atomic_read(&c->go))
        cpu_relax();

    t0 = ktime_get_ns();
    deadline = t0 + (u64)bench_ms * NSEC_PER_MSEC;
    do {
        if (bench_atomic)
            for (i = 0; i < BENCH_CHUNK; i++)
                atomic64_inc(&bench_shared);
        else
            for (i = 0; i < BENCH_CHUNK; i++)
                this_cpu_inc(bench_own);
        ops += BENCH_CHUNK;
        now = ktime_get_ns();
        cond_resched();
    } while (now < deadline);

    this_cpu_write(bench_ops, ops);

    /* Самі не виходимо: на нас чекатиме kthread_stop() */
    while (!kthread_should_stop()) {
        set_current_state(TASK_IDLE);
        if (kthread_should_stop())
            break;
        schedule();
    }
    __set_current_state(TASK_RUNNING);
    return 0;
}

static u64 bench_run(bool use_atomic, unsigned int *nr_out)
{
    struct bench_ctl c = { .ready = ATOMIC_INIT(0), .go = ATOMIC_INIT(0) };
    struct task_struct **t;
    unsigned int n, i = 0;
    u64 total = 0;
    int cpu;

    cpus_read_lock();                     /* поки міряємо, ядра нікуди не дінуться */
    n = num_online_cpus();
    t = kcalloc(n, sizeof(*t), GFP_KERNEL);
    if (!t) {
        cpus_read_unlock();
        return 0;
    }

    bench_atomic = use_atomic;
    for_each_online_cpu(cpu) {
        per_cpu(bench_ops, cpu) = 0;
        t[i] = kthread_create(bench_worker, &c, "pcbench/%d", cpu);
        if (IS_ERR(t[i]))
            break;
        kthread_bind(t[i], cpu);          /* лише доки задача ще не бігала */
        wake_up_process(t[i]);
        i++;
    }
    n = i;

    while (atomic_read(&c.ready) < n)
        schedule_timeout_uninterruptible(1);
    atomic_set(&c.go, 1);

    for (i = 0; i < n; i++)
        kthread_stop(t[i]);               /* чекає, доки потік договорить */

    for_each_online_cpu(cpu)
        total += per_cpu(bench_ops, cpu);

    kfree(t);
    cpus_read_unlock();
    *nr_out = n;
    return total;
}
