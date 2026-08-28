    DEFINE_WAIT(wait);

    for (;;) {
        prepare_to_wait_exclusive(&d->readq, &wait, TASK_INTERRUPTIBLE);
        if (ring_has_data(d))
            break;
        if (signal_pending(current)) { ret = -ERESTARTSYS; break; }   /* ← пастка */
        schedule();
    }
    finish_wait(&d->readq, &wait);
