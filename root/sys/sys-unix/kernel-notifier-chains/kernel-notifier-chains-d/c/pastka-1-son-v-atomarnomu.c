/* КАТАСТРОФІЧНА ПОМИЛКА в атомарному ланцюжку (наприклад, die_chain або panic_notifier) */
static int faulty_atomic_handler(struct notifier_block *nb, unsigned long action, void *data)
{
    /* Спроба взяти м'ютекс або виділити пам'ять із GFP_KERNEL */
    mutex_lock(&my_mutex);                      /* BUG: scheduling while atomic! */
    void *buf = kmalloc(1024, GFP_KERNEL);      /* BUG: might_sleep() check fails */
    msleep(10);                                 /* Крах ядра */
    mutex_unlock(&my_mutex);
    return NOTIFY_OK;
}
