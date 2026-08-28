/* ✅ ПРАВИЛЬНО: Динамічне виділення та звільнення виключно в release() */
static void my_device_release(struct kobject *kobj)
{
    struct my_device *dev = container_of(kobj, struct my_device, kobj);
    pr_info("my_device: freeing dynamic memory at %p\n", dev);
    kfree(dev);
}

static const struct kobj_type my_ktype = {
    .release   = my_device_release,
    .sysfs_ops = &my_sysfs_ops,
};

static int __init my_module_init(void)
{
    struct my_device *dev = kzalloc(sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;

    kobject_init_and_add(&dev->kobj, &my_ktype, NULL, "my_device");
    return 0;
}

static void __exit my_module_exit(void)
{
    kobject_del(&dev->kobj);
    kobject_put(&dev->kobj); // Фізичне звільнення відбудеться асинхронно в release
}
