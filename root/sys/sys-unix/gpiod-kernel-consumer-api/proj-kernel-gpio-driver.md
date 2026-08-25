# ⚙️ Практична реалізація драйвера ядра Linux із використанням gpiod API

Ця практична вставка містить вичерпний розбір та повний сирцевий код навчального драйвера ядра Linux для символьного пристрою, який демонструє безпечне отримання дескрипторів GPIO через `devm_gpiod_get()`, керування полярністю, обробку відкладеної ініціалізації (`-EPROBE_DEFER`), інтеграцію з підсистемою переривань (IRQ) та безпечне керування ресурсами пристрою.

---

## 1. Архітектура та задачі прикладного драйвера

Розроблюваний драйвер описує периферійний модуль (умовний цифровий датчик `acme-sensor`), який підключається до системної шини та використовує три лінії GPIO для зв'язку з процесором:

1. **`reset` (Reset pin)**: Обов'язкова вихідна лінія керування апаратним скиданням датчика. У файлі Дерева пристроїв (Device Tree) вона позначена як `GPIO_ACTIVE_LOW`. Драйвер повинен сформувати короткий імпульс скидання при завантаженні.
2. **`enable` (Enable pin)**: Опціональна вихідна лінія керування живленням та внутрішнім регулятором напруги модуля (`GPIO_ACTIVE_HIGH`). Якщо плата не підтримує програмне відключення живлення, ця лінія відсутня у Device Tree, і драйвер повинен коректно продовжити роботу.
3. **`irq` (Interrupt pin)**: Вхідна лінія сигналу готовності даних (`GPIO_ACTIVE_HIGH`), яка викликає апаратне переривання процесора при кожному вимірюванні датчика.

---

## 2. Повний сирцевий код драйвера (`acme_sensor.c`)

Оскільки код призначений для роботи у просторі ядра (Kernel Space), де відсутня стандартна бібліотека C++ та механізм винятків, приклад реалізовано мовою C з дотриманням усіх правил та конвенцій ядра Linux.

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>
#include <linux/delay.h>
#include <linux/slab.h>

#define DRIVER_NAME "acme_sensor_driver"

/* Приватна структура стану пристрою */
struct acme_sensor_dev {
    struct device *dev;
    struct gpio_desc *reset_gpio;
    struct gpio_desc *enable_gpio;
    struct gpio_desc *irq_gpio;
    int irq_num;
};

/* Обробник переривання лінії IRQ GPIO */
static irqreturn_t acme_sensor_irq_handler(int irq, void *dev_id)
{
    struct acme_sensor_dev *priv = dev_id;

    dev_info(priv->dev, "IRQ triggered on GPIO line! Sensor data ready.\n");
    return IRQ_HANDLED;
}

/* Функція ініціалізації пристрою (Probe) */
static int acme_sensor_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct acme_sensor_dev *priv;
    int ret;

    dev_info(dev, "Probing ACME Sensor Device...\n");

    /* 1. Виділення пам'яті під приватну структуру пристрою через Devres */
    priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    priv->dev = dev;

    /* 2. Отримання обов'язкової лінії Reset (встановлюємо логічний 0 = неактивний) */
    priv->reset_gpio = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
    if (IS_ERR(priv->reset_gpio)) {
        ret = PTR_ERR(priv->reset_gpio);
        if (ret != -EPROBE_DEFER)
            dev_err(dev, "Failed to get 'reset' GPIO: %d\n", ret);
        return ret;
    }

    /* 3. Отримання опціональної лінії Enable */
    priv->enable_gpio = devm_gpiod_get_optional(dev, "enable", GPIOD_OUT_HIGH);
    if (IS_ERR(priv->enable_gpio)) {
        ret = PTR_ERR(priv->enable_gpio);
        if (ret != -EPROBE_DEFER)
            dev_err(dev, "Failed to get optional 'enable' GPIO: %d\n", ret);
        return ret;
    }

    /* 4. Отримання вхідної лінії переривання IRQ */
    priv->irq_gpio = devm_gpiod_get(dev, "irq", GPIOD_IN);
    if (IS_ERR(priv->irq_gpio)) {
        ret = PTR_ERR(priv->irq_gpio);
        if (ret != -EPROBE_DEFER)
            dev_err(dev, "Failed to get 'irq' GPIO: %d\n", ret);
        return ret;
    }

    /* 5. Перетворення дескриптора GPIO у номер системного переривання */
    priv->irq_num = gpiod_to_irq(priv->irq_gpio);
    if (priv->irq_num < 0) {
        dev_err(dev, "Failed to map IRQ GPIO to system IRQ: %d\n", priv->irq_num);
        return priv->irq_num;
    }

    /* 6. Реєстрація потокового обробника переривання через Devres */
    ret = devm_request_threaded_irq(dev, priv->irq_num, NULL,
                                   acme_sensor_irq_handler,
                                   IRQF_TRIGGER_RISING | IRQF_ONESHOT,
                                   "acme_sensor_irq", priv);
    if (ret) {
        dev_err(dev, "Failed to request IRQ %d: %d\n", priv->irq_num, ret);
        return ret;
    }

    /* 7. Виконання апаратного скидання датчика (Pulse Reset) */
    dev_info(dev, "Asserting hardware Reset (Logical 1)...\n");
    gpiod_set_value(priv->reset_gpio, 1); /* Активація скидання */
    msleep(20);                           /* Тимчасова затримка 20 мс */
    
    dev_info(dev, "Deasserting hardware Reset (Logical 0)...\n");
    gpiod_set_value(priv->reset_gpio, 0); /* Зняття скидання */

    platform_set_drvdata(pdev, priv);
    dev_info(dev, "ACME Sensor probed successfully! Assigned IRQ: %d\n", priv->irq_num);

    return 0;
}

/* Опис відповідності Дерева пристроїв (Device Tree Matching) */
static const struct of_device_id acme_sensor_of_match[] = {
    { .compatible = "acme,sensor" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, acme_sensor_of_match);

static struct platform_driver acme_sensor_driver = {
    .probe = acme_sensor_probe,
    .driver = {
        .name = DRIVER_NAME,
        .of_match_table = acme_sensor_of_match,
    },
};

module_platform_driver(acme_sensor_driver);

MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("Example driver demonstrating Kernel gpiod Consumer API");
```

---

## 3. Відповідний фрагмент Дерева пристроїв (Device Tree)

Для успішного збігу (`matching`) описуваного драйвера з апаратурою у файлі специфікації платформи (`.dts`) створюється відповідний вузол:

```dts
/ {
    /* Вузол без батьківської шини: ядро створює для нього platform_device */
    acme_sensor {
        compatible = "acme,sensor";

        /* reset-gpios: Контролер gpio1, пін 10, активний низький рівень (0V) */
        reset-gpios = <&gpio1 10 GPIO_ACTIVE_LOW>;

        /* enable-gpios: Контролер gpio1, пін 12, активний високий рівень (3.3V) */
        enable-gpios = <&gpio1 12 GPIO_ACTIVE_HIGH>;

        /* irq-gpios: Контролер gpio1, пін 11, активний високий рівень */
        irq-gpios = <&gpio1 11 GPIO_ACTIVE_HIGH>;
    };
};
```

---

## 4. Покроковий детальний розбір механізмів коду

Для того щоб зрозуміти, як реалізований драйвер взаємодіє з підсистемою `gpiolib` та системою керування ресурсами Devres, проаналізуємо кожен етап виконання функції `probe()` від початку до кінця.

### 4.1. Виділення пам'яті через Devres (`devm_kzalloc`)

У самому початку функції `probe()` драйвер створює екземпляр приватної структури `struct acme_sensor_dev`:

```c
priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
```

Використання `devm_kzalloc()` замість стандартного `kzalloc()` забезпечує авто-вивільнення пам'яті. Коли пристрій вилучається з системи (наприклад, при розвантаженні модуля `rmmod`), ядро самостійно викличе `kfree(priv)`. Прапор `GFP_KERNEL` вказує, що виділення пам'яті відбувається у контексті процесу і може піддаватися блокуванню та виходу в сон при браку вільних сторінок RAM.

### 4.2. Отримання обов'язкових та опціональних ліній

Для отримання лінії скидання використовується виклик:

```c
priv->reset_gpio = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
```

При цьому відбуваються наступні кроки:
1. `gpiolib` звертається до вузла Device Tree для пристрою `dev` і знаходить властивість `reset-gpios`.
2. Витягується посилання на контролер `gpio1` та фізичний пін `10`.
3. Витягується прапор `GPIO_ACTIVE_LOW` та зберігається у `reset_gpio->flags`.
4. Лінія конфігурується у режим виходу (`GPIOD_OUT_LOW`), і виставляється початкове логічне значення `0`.

Для опціональної лінії `enable` використовується `devm_gpiod_get_optional()`. Якщо у Device Tree вузол не містить `enable-gpios`, ядро повертає `NULL`. Усі подальші виклики `gpiod_set_value(NULL, val)` є безпечними "пустушками" (No-Op), які не викликають падіння ядра.

### 4.3. Опрацювання відкладеного завантаження (`-EPROBE_DEFER`)

Якщо драйвер GPIO-контролера ще не завершив свій виклик `probe()`, функція `devm_gpiod_get()` поверне вказівник з кодом помилки `-EPROBE_DEFER`.

У коді драйвера ця ситуація обробляється наступним чином:

```c
if (IS_ERR(priv->reset_gpio)) {
    ret = PTR_ERR(priv->reset_gpio);
    if (ret != -EPROBE_DEFER)
        dev_err(dev, "Failed to get 'reset' GPIO: %d\n", ret);
    return ret;
}
```

Перевірка `ret != -EPROBE_DEFER` запобігає засміченню системного логу `dmesg` помилками під час нормального асинхронного завантаження ядра. Повернення від'ємного значення `-EPROBE_DEFER` з функції `probe()` повідомляє драйверну модель ядра, що пристрій слід відкласти та спробувати ініціалізувати пізніше.

### 4.4. Трансляція GPIO у системне переривання (`gpiod_to_irq`)

Для роботи з лінією готовності даних драйвер спочатку отримує дескриптор лінії у режимі входу (`GPIOD_IN`), а потім транслює його у номер переривання:

```c
priv->irq_num = gpiod_to_irq(priv->irq_gpio);
```

Підсистема `gpiolib` звертається до домену переривань (`irq_domain`), прив'язаного до даного GPIO-контролера. Якщо пін апаратно підтримує переривання, ядро повертає позитивний цілочисельний номер системного IRQ (наприклад, `142`).

Далі здійснюється реєстрація потокового обробника через Devres:

```c
ret = devm_request_threaded_irq(dev, priv->irq_num, NULL,
                               acme_sensor_irq_handler,
                               IRQF_TRIGGER_RISING | IRQF_ONESHOT,
                               "acme_sensor_irq", priv);
```

Прапор `IRQF_ONESHOT` гарантує, що лінія переривання залишатиметься заблокованою (маскованою) доти, доки не завершиться виконання потокового обробника переривання.

### 4.5. Апаратний імпульс скидання та логічна інверсія

Після успішної конфігурації всіх ресурсів драйвер подає імпульс скидання на датчик:

```c
gpiod_set_value(priv->reset_gpio, 1); /* Логічна 1 -> Фізичний 0V (RESET Active) */
msleep(20);                           /* Затримка 20 мс */
gpiod_set_value(priv->reset_gpio, 0); /* Логічний 0 -> Фізичний 3.3V (RESET Inactive) */
```

Завдяки тому, що у Device Tree вказано `GPIO_ACTIVE_LOW`, драйвер встановлює логічну одиницю `1`, а підсистема `gpiolib` фізично притягує вивід до землі (`0V`), викликаючи скидання мікросхеми. Через 20 мілісекунд драйвер встановлює логічний `0`, і лінія повертається до високого потенціалу (`3.3V`), виводячи датчик із режиму скидання у робочий стан.

### 4.6. Автоматичне очищення ресурсів при вилученні модуля

Завдяки суцільному використанню функцій з префіксом `devm_` (`devm_kzalloc`, `devm_gpiod_get`, `devm_request_threaded_irq`), драйверу **взагалі не потрібна реалізація функції `remove()`**.

При розвантаженні модуля підсистема Devres автоматично виконує очищення у зворотному порядку (LIFO):
1. Відключає та вивільняє обробник переривання (`devm_free_irq`).
2. Повертає дескриптори GPIO у початковий неактивний стан та вивільняє їх (`devm_gpiod_put`).
3. Звільняє виділену під структуру `priv` оперативну пам'ять (`devm_kfree`).

Це гарантує абсолютну відсутність витоків пам'яті та захищає систему від завислих ліній GPIO при перезавантаженні драйверів.
