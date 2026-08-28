static ssize_t pcstat_bench_write(struct file *f, const char __user *ubuf,
                                  size_t len, loff_t *ppos)
{
    unsigned int n = 0;
    u64 ops_a, ops_p, ns;

    ops_a = bench_run(true,  &n);
    ops_p = bench_run(false, &n);
    if (!n || !ops_a || !ops_p)
        return -EAGAIN;

    ns = (u64)bench_ms * NSEC_PER_MSEC;          /* тривалість одного проходу */

    pr_info("замір: ядер %u, по %u мс на прохід\n", n, bench_ms);
    pr_info("atomic64_inc: %12llu приростів, %8llu тис/с, %8llu пс на приріст\n",
            ops_a, div64_u64(ops_a, bench_ms), div64_u64(ns * n * 1000, ops_a));
    pr_info("this_cpu_inc: %12llu приростів, %8llu тис/с, %8llu пс на приріст\n",
            ops_p, div64_u64(ops_p, bench_ms), div64_u64(ns * n * 1000, ops_p));
    pr_info("перевага this_cpu_inc — у %llu разів\n", div64_u64(ops_p, ops_a));
    return len;
}

static const struct file_operations pcstat_bench_fops = {
    .owner  = THIS_MODULE,
    .write  = pcstat_bench_write,
    .llseek = noop_llseek,
};
