/* драйвер: задача чекає на завершення обміну, будить її переривання */
struct my_dev {
    struct completion done;
    u32 result;
};

static ssize_t dev_read(struct file *f, char __user *buf, size_t n, loff_t *off)
{
    struct my_dev *d = f->private_data;

    start_transfer(d);                              /* смикнули пристрій */
    if (wait_for_completion_interruptible(&d->done)) /* заснули: ми задача, нам можна */
        return -ERESTARTSYS;

    return copy_result(d, buf, n);
}

static irqreturn_t dev_irq(int irq, void *arg)
{
    struct my_dev *d = arg;

    d->result = read_status(d);
    complete(&d->done);       /* будити з переривання можна: це не взяття замка */
    return IRQ_HANDLED;
}
