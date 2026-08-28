/* Оголошуємо та ініціалізуємо блокуючий ланцюжок для нашого драйвера */
static BLOCKING_NOTIFIER_HEAD(sensor_event_chain);

/* Коди подій нашого датчика */
#define SENSOR_EVENT_TEMP_HIGH    0x0001
#define SENSOR_EVENT_BATTERY_LOW  0x0002
#define SENSOR_EVENT_DISCONNECTED 0x0003

/* Експортуємо функцію реєстрації для інших модулів */
int register_sensor_notifier(struct notifier_block *nb)
{
    return blocking_notifier_chain_register(&sensor_event_chain, nb);
}
EXPORT_SYMBOL_GPL(register_sensor_notifier);

/* Експортуємо функцію відписки */
int unregister_sensor_notifier(struct notifier_block *nb)
{
    return blocking_notifier_chain_unregister(&sensor_event_chain, nb);
}
EXPORT_SYMBOL_GPL(unregister_sensor_notifier);

/* Внутрішня функція драйвера, яка генерує сповіщення при спрацьовуванні сенсора */
void notify_sensor_event(unsigned long event_type, void *sensor_data)
{
    pr_info("[sensor_core] Генерація події 0x%lx для зареєстрованих передплатників...\n",
            event_type);

    /* Викликаємо всіх передплатників у контексті процесу під захистом rwsem */
    blocking_notifier_call_chain(&sensor_event_chain, event_type, sensor_data);
}
