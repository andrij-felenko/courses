static int wqdemo_open(struct inode *i, struct file *f)
{
    f->private_data = container_of(i->i_cdev, struct wqdemo, cdev);
    return stream_open(i, f);      /* позиції немає; read і write можуть іти разом */
}

static const struct file_operations wqdemo_fops = {
    .owner = THIS_MODULE,
    .open  = wqdemo_open,
    .read  = wqdemo_read,
    .write = wqdemo_write,
    .poll  = wqdemo_poll,
};

static int __init wqdemo_init(void)
{
    struct device *device;
    int ret;

    dev = kzalloc(sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;

    dev->ring = kmalloc(RING_SIZE, GFP_KERNEL);
    if (!dev->ring) { ret = -ENOMEM; goto err_dev; }

    spin_lock_init(&dev->lock);
    init_waitqueue_head(&dev->readq);
    init_waitqueue_head(&dev->writeq);
    timer_setup(&dev->tick, wqdemo_tick, 0);

    ret = alloc_chrdev_region(&devt, 0, 1, "wqdemo");
    if (ret) goto err_ring;

    cdev_init(&dev->cdev, &wqdemo_fops);
    dev->cdev.owner = THIS_MODULE;
    ret = cdev_add(&dev->cdev, devt, 1);
    if (ret) goto err_region;

    cls = class_create("wqdemo");            /* ядро < 6.4: class_create(THIS_MODULE, "wqdemo") */
    if (IS_ERR(cls)) { ret = PTR_ERR(cls); goto err_cdev; }

    device = device_create(cls, NULL, devt, NULL, "wqdemo");
    if (IS_ERR(device)) { ret = PTR_ERR(device); goto err_class; }

    if (period_ms)
        mod_timer(&dev->tick, jiffies + msecs_to_jiffies(period_ms));

    pr_info("/dev/wqdemo готовий: major=%d minor=%d\n", MAJOR(devt), MINOR(devt));
    return 0;

err_class:  class_destroy(cls);
err_cdev:   cdev_del(&dev->cdev);
err_region: unregister_chrdev_region(devt, 1);
err_ring:   kfree(dev->ring);
err_dev:    kfree(dev);
    return ret;
}

static void __exit wqdemo_exit(void)
{
    timer_shutdown_sync(&dev->tick);   /* більше не спрацює й не перезаведеться */
    device_destroy(cls, devt);
    class_destroy(cls);
    cdev_del(&dev->cdev);
    unregister_chrdev_region(devt, 1);
    kfree(dev->ring);
    kfree(dev);
}

module_init(wqdemo_init);
module_exit(wqdemo_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Символьний пристрій із чергою очікування");
