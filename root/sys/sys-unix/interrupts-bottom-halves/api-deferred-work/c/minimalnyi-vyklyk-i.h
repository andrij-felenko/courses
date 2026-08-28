struct mydev {
    void __iomem *regs;
    struct work_struct work;
    int irq;
};

static irqreturn_t mydev_isr(int irq, void *dev_id)          /* верхня половина */
{
    struct mydev *d = dev_id;

    if (!(readl(d->regs + REG_STATUS) & STATUS_DONE))
        return IRQ_NONE;                                     /* лінія спільна — не наше */

    writel(STATUS_DONE, d->regs + REG_STATUS);               /* зняти запит негайно */
    schedule_work(&d->work);                                 /* решту — колись потім */
    return IRQ_HANDLED;
}

static void mydev_work(struct work_struct *w)                /* тут спати можна */
{
    struct mydev *d = container_of(w, struct mydev, work);
    ...
}

/* під час підключення пристрою */
INIT_WORK(&d->work, mydev_work);
err = request_irq(d->irq, mydev_isr, IRQF_SHARED, "mydev", d);

/* під час від'єднання — саме в такому порядку */
free_irq(d->irq, d);
cancel_work_sync(&d->work);
kfree(d);
