static void my_device_kref_release(struct kref *kref)
{
    struct my_device *dev = container_of(kref, struct my_device, kref);
    // Спінлок list_lock ВЖЕ захоплено функцією kref_put_lock!
    list_del(&dev->entry);
    spin_unlock(&list_lock);

    kfree(dev);
}

void put_my_device(struct my_device *dev)
{
    // Безпечне зменшення лічильника з автоблокуванням при нулі
    kref_put_lock(&dev->kref, my_device_kref_release, &list_lock);
}
