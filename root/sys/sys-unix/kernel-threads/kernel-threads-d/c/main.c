static int flusher(void *data)
{
    struct my_dev *dev = data;

    while (!kthread_should_stop()) {
        wait_event_interruptible(dev->waitq,
                                 dev->has_work || kthread_should_stop());
        if (kthread_should_stop())
            break;

        flush_pending(dev);
    }
    return 0;
}

/* запуск: ім'я задачі задають одразу, воно й буде видно в ps */
dev->task = kthread_run(flusher, dev, "myflush/%d", dev->id);

/* зупинка з боку того, хто створив */
kthread_stop(dev->task);
