// Приклад захисту стану об'єкта під час утримання spinlock
void update_device_flags(struct my_device *dev, unsigned long new_flags) {
    spin_lock(&dev->lock);
    
    /* Перевіряємо, що поки ми під замком, ніхто не намагається писати в dev->flags */
    ASSERT_EXCLUSIVE_WRITER(dev->flags);
    dev->flags = new_flags;
    
    spin_unlock(&dev->lock);
}
