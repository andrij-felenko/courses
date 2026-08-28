static __poll_t wqdemo_poll(struct file *f, struct poll_table_struct *pt)
{
    struct wqdemo *d = f->private_data;
    __poll_t mask = 0;

    poll_wait(f, &d->readq, pt);             /* безумовно й ДО перевірки умови */
    poll_wait(f, &d->writeq, pt);

    if (ring_has_data(d))
        mask |= EPOLLIN | EPOLLRDNORM;
    if (ring_has_space(d))
        mask |= EPOLLOUT | EPOLLWRNORM;

    return mask;
}
