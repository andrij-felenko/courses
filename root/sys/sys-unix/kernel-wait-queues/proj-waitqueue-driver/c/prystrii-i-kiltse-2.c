static bool ring_has_data(struct wqdemo *d)
{
    unsigned long flags;
    bool ret;

    spin_lock_irqsave(&d->lock, flags);
    ret = ring_used(d) != 0;
    spin_unlock_irqrestore(&d->lock, flags);
    return ret;
}

static bool ring_has_space(struct wqdemo *d)
{
    unsigned long flags;
    bool ret;

    spin_lock_irqsave(&d->lock, flags);
    ret = ring_free(d) != 0;
    spin_unlock_irqrestore(&d->lock, flags);
    return ret;
}
