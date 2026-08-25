# ⚙️ Модуль ядра для перехоплення системних подій через notifier chains

Створення завантажуваного модуля ядра (Loadable Kernel Module, LKM) — найбільш наочний та практичний спосіб розібратися у внутрішній механіці ланцюжків сповіщень. Замість абстрактного аналізу вихідного коду розробник може підключитися до живого глобального ланцюжка ядра, перехопити події створення та зміни конфігурації апаратних пристроїв, витягти службові метадані та перевірити роботу механізмів синхронізації в реальному часі.

У цьому практичному проекті ми розглянемо три взаємодоповнюючі сценарії:
1. Підписка на події життєвого циклу мережевих інтерфейсів через глобальний ланцюжок `netdev_chain` за допомогою стандартного API `register_netdevice_notifier()`.
2. Оголошення та експорт власного ланцюжка сповіщень всередині драйвера, що дозволяє іншим стороннім модулям підписуватися на події нашої підсистеми.
3. Точкова підписка на події конкретного екземпляра пристрою через механізм `register_netdevice_notifier_dev()`.

### Архітектура та логіка роботи модуля

Підсистема мережевих пристроїв Linux використовує ланцюжок типу SRCU (`srcu_notifier_head`). Це означає, що функція зворотного виклику нашого модуля виконуватиметься в контексті процесу ядра, що генерує зміну стану (наприклад, процесу утиліти `ip` під час виконання системного виклику Netlink). Читання списку обробників виконується без блокування, проте декілька подій для різних інтерфейсів можуть оброблятися паралельно на різних процесорних ядрах. Тому код нашого обробника має бути повністю реентерабельним (reentrant) і потокобезпечним.

Життєвий цикл модуля складається з трьох послідовних кроків:
1. **Ініціалізація та реєстрація:** під час завантаження через `insmod` функція `module_init()` ініціалізує статичний екземпляр `struct notifier_block`, вказує адресу функції зворотного виклику, задає пріоритет обробника та викликає `register_netdevice_notifier()`.
2. **Обробка подій та розбір метаданих:** при зміні стану будь-якого мережевого інтерфейсу ядро викликає функцію `my_netdev_event_handler()`. Вона перетворює безтиповий вказівник `data` на структуру метаданих `struct netdev_notifier_info`, витягує покажчик на `struct net_device`, перевіряє ім'я інтерфейсу та його параметри (MTU, прапорці стану), після чого повертає статус `NOTIFY_OK` або `NOTIFY_DONE`.
3. **Безпечне вивантаження:** під час виконання команди `rmmod` функція `module_exit()` викликає `unregister_netdevice_notifier()`. Завдяки внутрішній синхронізації SRCU ядро гарантує, що пам'ять модуля не буде звільнена, доки всі паралельні обробники подій на інших ядрах CPU повністю не завершать свою роботу.

### Вихідний код модуля ядра

Нижче наведено повний вихідний код модуля `my_netdev_notifier.c` з детальними коментарями до кожного рядка:

```c
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
```

---

### Створення власного ланцюжка сповіщень у власному драйвері

Часто перед розробником постає зворотне завдання: створити підсистему або складний драйвер апаратного пристрою, який сам генерує події (наприклад, стан заряджання батареї, перевищення температурного порогу або перемикання каналу зв'язку) та надає іншим стороннім модулям можливість підписатися на ці повідомлення.

Для цього драйвер оголошує власну голову ланцюжка, експортує публічні реєстраційні функції через `EXPORT_SYMBOL_GPL` та ініціює виклик подій через `*_notifier_call_chain`.

Розглянемо реалізацію власного блокуючого ланцюжка:

```c
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
```

Такий підхід забезпечує ідеальну модульність: сторонній драйвер охолодження вентилятора може підписатися на `register_sensor_notifier` і вмикати додаткове охолодження при отриманні `SENSOR_EVENT_TEMP_HIGH`, не маючи прямої компіляційної залежності від внутрішньої реалізації сенсорного чіпа.

---

### Точкова фільтрація подій: `register_netdevice_notifier_dev`

Коли драйвер або мережевий фільтр обслуговує лише один конкретний інтерфейс (наприклад, віртуальний тунель або один порт комутатора), прослуховування глобального `netdev_chain` створює зайві накладні витрати, адже обробник викликається на події всіх інтерфейсів системи (loopback, фізичні карти, віртуальні мости).

Для таких випадків ядро надає функцію `register_netdevice_notifier_dev(struct net_device *dev, struct notifier_block *nb)`. Вона дозволяє прив'язати обробник безпосередньо до черги подій зазначеного адаптера `dev`. Диспетчер ядра автоматично фільтрує повідомлення, викликаючи функцію зворотного виклику лише тоді, коли подія сталася на вказаному пристрої.

---

### Відновлення контексту драйвера через макрос container_of

У реальних драйверах екземпляр `struct notifier_block` рідко буває глобальною статичною змінною. Зазвичай він динамічно розміщується всередині приватної структури екземпляра пристрою (`struct my_device_priv`).

Щоб обробник сповіщення міг отримати доступ до полів свого пристрою, використовується фундаментальний макрос ядра `container_of()`:

```c
struct my_device_priv {
    int device_id;
    void __iomem *io_base;
    struct mutex lock;
    struct notifier_block reboot_nb;    /* Вбудований блок сповіщення */
};

static int my_reboot_callback(struct notifier_block *nb,
                              unsigned long action,
                              void *data)
{
    /*
     * Отримуємо вказівник на структуру пристрою за адресою її внутрішнього поля reboot_nb.
     * Макрос обчислює зміщення поля reboot_nb відносно початку struct my_device_priv
     * і повертає коректну базову адресу об'єкта.
     */
    struct my_device_priv *priv = container_of(nb, struct my_device_priv, reboot_nb);

    pr_info("[my_device_%d] Зупинка пристрою перед вимкненням системи...\n",
            priv->device_id);

    /* Виконуємо операції з апаратурою */
    iowrite32(0, priv->io_base + 0x04);

    return NOTIFY_OK;
}
```

---

### Складання модуля через Kbuild

Для компіляції модуля під поточне запущене ядро використовується стандартний файл `Makefile`, який звертається до складальної інфраструктури заголовків ядра:

```makefile
obj-m += my_netdev_notifier.o

# Шлях до каталогів заголовків і конфігурації поточного ядра
KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

---

### Практичне тестування та перевірка журналів

Для безпечного тестування модуля без впливу на реальне мережеве з'єднання найкраще використовувати віртуальні інтерфейси типу `dummy`.

Послідовність команд для перевірки:

```bash
# 1. Компільовано модуль ядра
make

# 2. Завантажуємо зібраний бінарний файл .ko у ядро
sudo insmod my_netdev_notifier.ko

# 3. Створюємо новий віртуальний мережевий адаптер test_dummy0
sudo ip link add name test_dummy0 type dummy

# 4. Змінюємо розмір MTU інтерфейсу
sudo ip link set test_dummy0 mtu 1400

# 5. Піднімаємо інтерфейс (генерує NETDEV_UP)
sudo ip link set test_dummy0 up

# 6. Опускаємо інтерфейс (генерує NETDEV_GOING_DOWN та NETDEV_DOWN)
sudo ip link set test_dummy0 down

# 7. Видаляємо віртуальний інтерфейс із системи
sudo ip link delete test_dummy0

# 8. Вивантажуємо модуль сповіщень
sudo rmmod my_netdev_notifier
```

Після виконання цих операцій перевіримо журнал буфера повідомлень ядра командою `dmesg -T` або `journalctl -k`:

```text
[Thu Aug 20 20:15:01 2026] [netdev_probe] Завантаження модуля: підписка на netdev_chain...
[Thu Aug 20 20:15:01 2026] [netdev_probe] Успішно зареєстровано в netdev_chain (priority: 0)
[Thu Aug 20 20:15:10 2026] [netdev_probe] Зареєстровано новий пристрій: test_dummy0 (тип: 1)
[Thu Aug 20 20:15:15 2026] [netdev_probe] Інтерфейс test_dummy0 ЗМІНИВ MTU: нове значення 1400 (мін: 0, макс: 65535)
[Thu Aug 20 20:15:20 2026] [netdev_probe] Інтерфейс test_dummy0 ПІДНЯТО (UP), поточний MTU: 1400, MAC: 52:54:00:12:34:56
[Thu Aug 20 20:15:25 2026] [netdev_probe] Інтерфейс test_dummy0 ПОЧИНАЄ ВИМИКАННЯ (GOING_DOWN)
[Thu Aug 20 20:15:25 2026] [netdev_probe] Інтерфейс test_dummy0 ОПУЩЕНО (DOWN)
[Thu Aug 20 20:15:30 2026] [netdev_probe] Дереєстрація та видалення інтерфейсу: test_dummy0
[Thu Aug 20 20:15:35 2026] [netdev_probe] Вивантаження модуля: відписка від netdev_chain...
[Thu Aug 20 20:15:35 2026] [netdev_probe] Модуль успішно вивантажено з ядра
```

---

### Аналіз типових помилок та правил безпеки

Розробка обробників сповіщень вимагає врахування таких інженерних нюансів:

1. **Строгий контроль життєвого циклу пам'яті:** об'єкт `struct notifier_block` та скомпільований код функції `my_netdev_event_handler` знаходяться у віртуальній пам'яті, виділеній під модуль. Якщо модуль вивантажити через `rmmod`, але пропустити виклик `unregister_netdevice_notifier()`, голова ланцюжка ядра збереже вказівник на звільнену пам'ять. Перша ж наступна мережева дія в системі викличе виконання інструкцій за мертвою адресою, спричинивши Kernel Oops або паніку ядра.
2. **Робота з контекстом даних (`data`):** ніколи не розіменовуйте вказівник `data` безпосередньо як структуру пристрою. У різних підсистемах ядра тип об'єкта, переданого через `void *data`, відрізняється. Для мережевого стека обов'язково слід використовувати офіційні макроси ядра, такі як `netdev_notifier_info_to_dev(data)`.
3. **Заборона важких операцій у швидких шляхах:** хоча ланцюжок `netdev_chain` допускає перехід у стан сну, функція зворотного виклику не повинна виконувати тривалих синхронних операцій (наприклад, надсилати HTTP-запити чи чекати на відповідь віддалених серверів). Якщо реакція на подію вимагає складної обробки, правильний патерн проектування — скопіювати потрібні метадані в локальний буфер, поставити завдання у чергу робіт ядра (`schedule_work`) і негайно повернути керування через `NOTIFY_OK`.
