#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netdevice.h>
#include <linux/notifier.h>
#include <linux/rtnetlink.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Systems Engineer");
MODULE_DESCRIPTION("Модуль перехоплення подій мережевих інтерфейсів через netdev_chain");
MODULE_VERSION("1.0");

/*
 * Функція зворотного виклику, що спрацьовує при зміні стану
 * будь-якого мережевого адаптера в операційній системі.
 */
static int my_netdev_event_handler(struct notifier_block *nb,
                                   unsigned long action,
                                   void *data)
{
    /*
     * У ланцюжку netdev_chain параметр data вказує на struct netdev_notifier_info.
     * Спеціальний макрос netdev_notifier_info_to_dev безпечно дістає з нього
     * вказівник на цільовий мережевий пристрій struct net_device.
     */
    struct net_device *dev = netdev_notifier_info_to_dev(data);

    /* Захист від некоректних або порожніх подій */
    if (!dev)
        return NOTIFY_DONE;

    /*
     * Фільтруємо події за типом дії (action).
     * Якщо подія нас цікавить — виводимо інформацію в системний журнал ядра.
     */
    switch (action) {
    case NETDEV_REGISTER:
        pr_info("[netdev_probe] Зареєстровано новий пристрій: %s (тип: %u)\n",
                dev->name, dev->type);
        break;

    case NETDEV_UP:
        pr_info("[netdev_probe] Інтерфейс %s ПІДНЯТО (UP), поточний MTU: %u, MAC: %pM\n",
                dev->name, dev->mtu, dev->dev_addr);
        break;

    case NETDEV_GOING_DOWN:
        pr_info("[netdev_probe] Інтерфейс %s ПОЧИНАЄ ВИМИКАННЯ (GOING_DOWN)\n",
                dev->name);
        break;

    case NETDEV_DOWN:
        pr_info("[netdev_probe] Інтерфейс %s ОПУЩЕНО (DOWN)\n",
                dev->name);
        break;

    case NETDEV_CHANGEMTU:
        pr_info("[netdev_probe] Інтерфейс %s ЗМІНИВ MTU: нове значення %u (мін: %u, макс: %u)\n",
                dev->name, dev->mtu, dev->min_mtu, dev->max_mtu);
        break;

    case NETDEV_CHANGENAME:
        pr_info("[netdev_probe] Інтерфейс ПЕРЕЙМЕНОВАНО на: %s\n",
                dev->name);
        break;

    case NETDEV_UNREGISTER:
        pr_info("[netdev_probe] Дереєстрація та видалення інтерфейсу: %s\n",
                dev->name);
        break;

    default:
        /*
         * Невідома або нецікава для нас подія (наприклад, зміна черг tx).
         * Повертаємо NOTIFY_DONE, що дозволяє ядру безперешкодно продовжити обхід.
         */
        return NOTIFY_DONE;
    }

    /* Сповіщення успішно оброблено */
    return NOTIFY_OK;
}

/*
 * Статичне оголошення блоку сповіщення.
 * priority = 0 означає стандартний нейтральний пріоритет.
 */
static struct notifier_block my_netdev_nb = {
    .notifier_call = my_netdev_event_handler,
    .priority = 0,
};

/*
 * Функція ініціалізації модуля.
 * Виконується при завантаженні через insmod / modprobe.
 */
static int __init my_notifier_init(void)
{
    int ret;

    pr_info("[netdev_probe] Завантаження модуля: підписка на netdev_chain...\n");

    /*
     * Реєструємо наш блок у глобальному ланцюжку сповіщень.
     * Функція автоматично додасть my_netdev_nb у список ядра.
     */
    ret = register_netdevice_notifier(&my_netdev_nb);
    if (ret) {
        pr_err("[netdev_probe] Помилка реєстрації обробника: %d\n", ret);
        return ret;
    }

    pr_info("[netdev_probe] Успішно зареєстровано в netdev_chain (priority: %d)\n",
            my_netdev_nb.priority);
    return 0;
}

/*
 * Функція очищення модуля.
 * Виконується при вивантаженні через rmmod.
 */
static void __exit my_notifier_exit(void)
{
    pr_info("[netdev_probe] Вивантаження модуля: відписка від netdev_chain...\n");

    /*
     * КРИТИЧНО ВАЖЛИВО: видаляємо блок зі списку ядра!
     * unregister_netdevice_notifier очікує завершення всіх активних обробників (SRCU sync),
     * перш ніж повернути керування.
     */
    unregister_netdevice_notifier(&my_netdev_nb);

    pr_info("[netdev_probe] Модуль успішно вивантажено з ядра\n");
}

module_init(my_notifier_init);
module_exit(my_notifier_exit);
