struct my_device *find_device_rcu(int id)
{
    struct my_device *dev;

    rcu_read_lock();
    list_for_each_entry_rcu(dev, &device_list_rcu, rcu_node) {
        if (dev->dev_id == id) {
            // Намагаємося збільшити лічильник ТІЛЬКИ якщо він не дорівнює нулю
            if (refcount_inc_not_zero(&dev->kref.refcount)) {
                rcu_read_unlock();
                return dev; // Успішно захопили живий об'єкт
            }
            // Лічильник уже 0: об'єкт у процесі видалення, пропускаємо його
            break;
        }
    }
    rcu_read_unlock();
    return NULL;
}
