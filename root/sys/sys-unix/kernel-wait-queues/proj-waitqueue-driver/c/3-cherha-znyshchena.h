    /* у структурі пристрою */
    bool gone;

    /* у шляху зникнення пристрою */
    WRITE_ONCE(d->gone, true);
    wake_up_interruptible_all(&d->readq);    /* усіх, а не одного! */
    wake_up_interruptible_all(&d->writeq);

    /* і в умові кожного очікування */
    ret = wait_event_interruptible(d->readq,
                                   ring_has_data(d) || READ_ONCE(d->gone));
    if (READ_ONCE(d->gone))
        return -ENODEV;
