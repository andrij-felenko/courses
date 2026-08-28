DEFINE_WAIT_FUNC(wait, woken_wake_function);
long timeo = msecs_to_jiffies(2000);

add_wait_queue(&dev->readq, &wait);
while (!poll_device_over_slow_bus(dev)) {   /* довга перевірка */
    timeo = wait_woken(&wait, TASK_INTERRUPTIBLE, timeo);
    if (!timeo || signal_pending(current))
        break;
}
remove_wait_queue(&dev->readq, &wait);
