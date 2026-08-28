static __poll_t wqdemo_poll(struct file *f, struct poll_table_struct *pt)
{
    struct wqdemo *d = f->private_data;

    if (ring_has_data(d))
        return EPOLLIN | EPOLLRDNORM;        /* ← реєстрації не було */

    poll_wait(f, &d->readq, pt);
    return 0;
}
