struct mydev {
    struct wait_queue_head readq;
    spinlock_t             lock;
    unsigned int           bytes_ready;
};

/* ініціалізація пристрою */
init_waitqueue_head(&dev->readq);
spin_lock_init(&dev->lock);

/* бік того, хто чекає: read() у контексті процесу */
static ssize_t mydev_read(struct file *f, char __user *buf, size_t n, loff_t *off)
{
    struct mydev *dev = f->private_data;
    int ret;

    if (f->f_flags & O_NONBLOCK) {
        if (!READ_ONCE(dev->bytes_ready))
            return -EAGAIN;
    } else {
        ret = wait_event_interruptible(dev->readq, READ_ONCE(dev->bytes_ready));
        if (ret)
            return ret;              /* -ERESTARTSYS нагору незміненим */
    }
    return copy_ready_bytes(dev, buf, n);
}

/* бік того, хто будить: обробник перервання */
static irqreturn_t mydev_isr(int irq, void *data)
{
    struct mydev *dev = data;

    spin_lock(&dev->lock);
    dev->bytes_ready += drain_fifo(dev);   /* умова стала істинною */
    spin_unlock(&dev->lock);

    if (wq_has_sleeper(&dev->readq))       /* бар'єр + перевірка списку */
        wake_up_interruptible(&dev->readq);
    return IRQ_HANDLED;
}
