/* заснути так, як просить параметр модуля */
static int wqdemo_wait_data(struct wqdemo *d)
{
    if (READ_ONCE(exclusive))
        return wait_event_interruptible_exclusive(d->readq, ring_has_data(d));

    return wait_event_interruptible(d->readq, ring_has_data(d));
}

static ssize_t wqdemo_read(struct file *f, char __user *buf, size_t len, loff_t *off)
{
    struct wqdemo *d = f->private_data;
    char kbuf[CHUNK];
    unsigned long flags;
    unsigned int n;
    int ret;

    if (len > sizeof(kbuf))
        len = sizeof(kbuf);
    if (!len)
        return 0;                            /* read(fd, buf, 0) не має чекати */

    for (;;) {
        spin_lock_irqsave(&d->lock, flags);
        n = ring_get(d, kbuf, len);          /* істину беремо під замком */
        spin_unlock_irqrestore(&d->lock, flags);

        if (n)
            break;
        if (f->f_flags & O_NONBLOCK)
            return -EAGAIN;

        ret = wqdemo_wait_data(d);           /* ось тут задача засинає */
        if (ret)
            return ret;                      /* -ERESTARTSYS: прилетів сигнал */
    }

    if (copy_to_user(buf, kbuf, n))          /* замка вже немає — тут спати МОЖНА */
        return -EFAULT;

    if (wq_has_sleeper(&d->writeq))          /* у кільці звільнилося місце */
        wake_up_interruptible(&d->writeq);

    return n;
}
