static ssize_t wqdemo_write(struct file *f, const char __user *buf, size_t len, loff_t *off)
{
    struct wqdemo *d = f->private_data;
    char kbuf[CHUNK];
    unsigned long flags;
    unsigned int n;
    int ret;

    if (len > sizeof(kbuf))
        len = sizeof(kbuf);
    if (!len)
        return 0;                            /* нульовий запис не чекає на місце */
    if (copy_from_user(kbuf, buf, len))      /* замка ще немає — спати МОЖНА */
        return -EFAULT;

    for (;;) {
        spin_lock_irqsave(&d->lock, flags);
        n = ring_put(d, kbuf, len);
        spin_unlock_irqrestore(&d->lock, flags);

        if (n)
            break;
        if (f->f_flags & O_NONBLOCK)
            return -EAGAIN;

        ret = wait_event_interruptible(d->writeq, ring_has_space(d));
        if (ret)
            return ret;
    }

    if (wq_has_sleeper(&d->readq))
        wake_up_interruptible(&d->readq);

    return n;
}

static void wqdemo_tick(struct timer_list *t)
{
    struct wqdemo *d = container_of(t, struct wqdemo, tick);
    char msg[24];
    unsigned int n;

    n = scnprintf(msg, sizeof(msg), "tick %lu\n", ++d->seq);

    spin_lock(&d->lock);                     /* м'який контекст: irqsave не потрібен */
    ring_put(d, msg, n);
    spin_unlock(&d->lock);

    if (wq_has_sleeper(&d->readq))
        wake_up_interruptible(&d->readq);

    if (READ_ONCE(period_ms))
        mod_timer(&d->tick, jiffies + msecs_to_jiffies(READ_ONCE(period_ms)));
}
