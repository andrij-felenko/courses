static void my_device_rcu_free(struct rcu_head *head)
{
    struct my_device *dev = container_of(head, struct my_device, rcu_head);
    kfree(dev);
}

static void my_device_release(struct kobject *kobj)
{
    struct my_device *dev = container_of(kobj, struct my_device, kobj);
    // Видаляємо зі списку з урахуванням RCU-бар'єрів
    list_del_rcu(&dev->rcu_node);
    // Відкладаємо фізичне звільнення до закінчення благодатного періоду (grace period)
    call_rcu(&dev->rcu_head, my_device_rcu_free);
}
