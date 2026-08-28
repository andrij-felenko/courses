struct my_device *get_device_by_id_safe(int id)
{
    struct my_device *dev, *target = NULL;

    spin_lock(&list_lock);
    list_for_each_entry(dev, &device_list, entry) {
        if (dev->dev_id == id) {
            // Збільшуємо лічильник ПІД захистом блокування
            kref_get(&dev->kref);
            target = dev;
            break;
        }
    }
    spin_unlock(&list_lock);
    return target;
}
