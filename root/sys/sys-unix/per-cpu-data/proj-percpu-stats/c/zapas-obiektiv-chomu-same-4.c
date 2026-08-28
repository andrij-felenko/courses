/* запис числа в /sys/kernel/debug/pcstat/refill — «поклади N об'єктів у запас» */
static ssize_t pcstat_refill_write(struct file *f, const char __user *ubuf,
                                   size_t len, loff_t *ppos)
{
    unsigned int n, i;
    int err;

    err = kstrtouint_from_user(ubuf, len, 10, &n);
    if (err)
        return err;

    for (i = 0; i < min(n, 4096u); i++) {
        err = depot_refill();
        if (err)
            return err;
    }
    return len;
}

static const struct file_operations pcstat_refill_fops = {
    .owner  = THIS_MODULE,
    .write  = pcstat_refill_write,
    .llseek = noop_llseek,
};
