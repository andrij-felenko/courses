# ⚙️ Практика: розробка платформеного драйвера з devm_add_action_or_reset та групами ресурсів

Під час розробки драйверів ядра Linux сучасний стандарт вимагає максимального використання керованих ресурсів. Це не лише виключає помилки витоку пам'яті та завислих переривань, але й робить код компактним та стійким до відкладеної ініціалізації (`-EPROBE_DEFER`).

Нижче наведено повний зразок реалізації платформеного драйвера для апаратного датчика температури й тиску `acme_sensor`. Приклад демонструє типовий життєвий цикл: отримання системних ресурсів, реєстрацію власної функції апаратного вимкнення за допомогою `devm_add_action_or_reset()`, безпечну інтеграцію з робочою чергою (`workqueue`), динамічну групу калібрування та реєстрацію в підсистемі HWMON.

## Повний вихідний код модуля драйвера

```c
// SPDX-License-Identifier: GPL-2.0
/*
 * acme_sensor.c — Драйвер датчика з повним керуванням ресурсами devres
 */

#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/io.h>
#include <linux/clk.h>
#include <linux/interrupt.h>
#include <linux/hwmon.h>
#include <linux/workqueue.h>
#include <linux/delay.h>
#include <linux/slab.h>

#define ACME_REG_CTRL       0x00
#define ACME_REG_STATUS     0x04
#define ACME_REG_DATA       0x08
#define ACME_CTRL_ENABLE    BIT(0)
#define ACME_CTRL_RESET     BIT(1)
#define ACME_STATUS_READY   BIT(0)

struct acme_sensor_priv {
	struct device *dev;
	void __iomem *regs;
	struct clk *clk;
	int irq;
	struct delayed_work poll_work;
	struct mutex lock;
	u32 cached_sample;
};

/* Власна дія: переведення заліза в стан низького споживання */
static void acme_hw_disable_action(void *data)
{
	struct acme_sensor_priv *priv = data;
	u32 val;

	/* Записуємо нуль у регістр контролю для зупинки вимірювань */
	val = readl(priv->regs + ACME_REG_CTRL);
	val &= ~ACME_CTRL_ENABLE;
	writel(val, priv->regs + ACME_REG_CTRL);

	dev_dbg(priv->dev, "Апаратну частину датчика вимкнено через devm-action\n");
}

/* Власна дія: зупинка та синхронізація робочої черги */
static void acme_cancel_work_action(void *data)
{
	struct acme_sensor_priv *priv = data;

	/* Гарантує, що жоден фоновий потік більше не звернеться до priv */
	cancel_delayed_work_sync(&priv->poll_work);
}

static void acme_poll_worker(struct work_struct *work)
{
	struct acme_sensor_priv *priv =
		container_of(work, struct acme_sensor_priv, poll_work.work);

	mutex_lock(&priv->lock);
	if (readl(priv->regs + ACME_REG_STATUS) & ACME_STATUS_READY)
		priv->cached_sample = readl(priv->regs + ACME_REG_DATA);
	mutex_unlock(&priv->lock);

	schedule_delayed_work(&priv->poll_work, msecs_to_jiffies(1000));
}

static irqreturn_t acme_irq_handler(int irq, void *dev_id)
{
	struct acme_sensor_priv *priv = dev_id;

	/* Швидка реакція на переривання готовності даних */
	schedule_delayed_work(&priv->poll_work, 0);
	return IRQ_HANDLED;
}

/* Динамічна фаза калібрування з використанням devres groups */
static int acme_calibrate_sensor(struct acme_sensor_priv *priv)
{
	struct device *dev = priv->dev;
	void *group_id;
	u32 *calib_buf;
	int ret = 0;

	/* Відкриваємо ізольовану групу ресурсів під тимчасові дані калібрування */
	group_id = devres_open_group(dev, NULL, GFP_KERNEL);
	if (!group_id)
		return -ENOMEM;

	calib_buf = devm_kmalloc(dev, 1024, GFP_KERNEL);
	if (!calib_buf) {
		devres_release_group(dev, group_id);
		return -ENOMEM;
	}

	/* Імітація читання калібрувальної таблиці з чіпа */
	calib_buf[0] = readl(priv->regs + ACME_REG_DATA);

	/* Якщо дані некоректні — відкочуємо групу */
	if (calib_buf[0] == 0xFFFFFFFF) {
		dev_err(dev, "Помилка калібрування датчика\n");
		ret = -EIO;
		devres_release_group(dev, group_id);
		return ret;
	}

	/* Якщо все добре — закриваємо групу або видаляємо тимчасовий буфер */
	devres_release_group(dev, group_id);
	return 0;
}

/* HWMON-інтерфейс читання температури */
static umode_t acme_hwmon_is_visible(const void *drvdata,
                                     enum hwmon_sensor_types type,
                                     u32 attr, int channel)
{
	return 0444;
}

static int acme_hwmon_read(struct device *dev, enum hwmon_sensor_types type,
                           u32 attr, int channel, long *val)
{
	struct acme_sensor_priv *priv = dev_get_drvdata(dev);

	mutex_lock(&priv->lock);
	*val = (long)priv->cached_sample * 1000;
	mutex_unlock(&priv->lock);

	return 0;
}

static const struct hwmon_channel_info *acme_hwmon_info[] = {
	HWMON_CHANNEL_INFO(temp, HWMON_T_INPUT),
	NULL
};

static const struct hwmon_ops acme_hwmon_ops = {
	.is_visible = acme_hwmon_is_visible,
	.read = acme_hwmon_read,
};

static const struct hwmon_chip_info acme_chip_info = {
	.ops = &acme_hwmon_ops,
	.info = acme_hwmon_info,
};

static int acme_sensor_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct acme_sensor_priv *priv;
	struct device *hwmon_dev;
	int ret;

	/* 1. Виділення пам'яті для приватного стану */
	priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = dev;
	mutex_init(&priv->lock);
	INIT_DELAYED_WORK(&priv->poll_work, acme_poll_worker);
	platform_set_drvdata(pdev, priv);

	/* 2. Отримання та відображення діапазону регістрів MMIO */
	priv->regs = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(priv->regs))
		return PTR_ERR(priv->regs);

	/* 3. Отримання та ввімкнення тактового сигналу */
	priv->clk = devm_clk_get_enabled(dev, "sensor_clk");
	if (IS_ERR(priv->clk))
		return dev_err_probe(dev, PTR_ERR(priv->clk),
		                      "Не вдалося ввімкнути тактування\n");

	/* 4. Апаратне скидання та активація чіпа */
	writel(ACME_CTRL_RESET, priv->regs + ACME_REG_CTRL);
	usleep_range(1000, 2000);
	writel(ACME_CTRL_ENABLE, priv->regs + ACME_REG_CTRL);

	/* 5. Реєструємо дію зупинки апаратного модуля */
	ret = devm_add_action_or_reset(dev, acme_hw_disable_action, priv);
	if (ret)
		return ret;

	/* 6. Реєструємо дію зупинки фонової робочої черги */
	ret = devm_add_action_or_reset(dev, acme_cancel_work_action, priv);
	if (ret)
		return ret;

	/* 7. Виконання калібрування з локальною devres-групою */
	ret = acme_calibrate_sensor(priv);
	if (ret)
		return ret;

	/* 8. Отримання лінії переривання та реєстрація обробника */
	priv->irq = platform_get_irq(pdev, 0);
	if (priv->irq < 0)
		return priv->irq;

	ret = devm_request_irq(dev, priv->irq, acme_irq_handler,
	                       IRQF_TRIGGER_RISING, "acme_sensor", priv);
	if (ret)
		return dev_err_probe(dev, ret, "Не вдалося отримати IRQ %d\n", priv->irq);

	/* 9. Реєстрація пристрою в підсистемі HWMON */
	hwmon_dev = devm_hwmon_device_register_with_info(dev, "acme_sensor",
	                                                 priv, &acme_chip_info,
	                                                 NULL);
	if (IS_ERR(hwmon_dev))
		return PTR_ERR(hwmon_dev);

	/* Запуск фонового опитування */
	schedule_delayed_work(&priv->poll_work, msecs_to_jiffies(100));

	dev_info(dev, "Датчик acme_sensor успішно ініціалізовано\n");
	return 0;
}

static const struct of_device_id acme_sensor_of_match[] = {
	{ .compatible = "acme,temp-sensor-v1" },
	{ /* кінець таблиці */ }
};
MODULE_DEVICE_TABLE(of, acme_sensor_of_match);

static struct platform_driver acme_sensor_driver = {
	.probe = acme_sensor_probe,
	.driver = {
		.name = "acme-sensor",
		.of_match_table = acme_sensor_of_match,
	},
	/* Функція .remove відсутня: devres автоматично виконає повне очищення */
};
module_platform_driver(acme_sensor_driver);

MODULE_AUTHOR("Linux Driver Engineer");
MODULE_DESCRIPTION("Acme Hardware Sensor Driver with Full Devres Support");
MODULE_LICENSE("GPL");
```

## Покроковий розбір архітектури та послідовності LIFO

Головною відмінністю наведеного драйвера від застарілих реалізацій є повна відсутність міток `goto err_*` у функції `acme_sensor_probe()` та відсутність функції `.remove` у структурі `platform_driver`. Весь життєвий цикл опирається на внутрішній стек ядра `devres`.

### 1. Формування стека керованих ресурсів

Під час послідовного виконання `acme_sensor_probe()` ядро реєструє об'єкти у голові зв'язаного списку `dev->devres_head`. У результаті утворюється впорядкований стек, де кожен новий елемент лягає поверх попередніх:

1. `devm_kzalloc()`: пам'ять для `struct acme_sensor_priv` опиняється в самому низу списку (буде звільнена останньою).
2. `devm_platform_ioremap_resource()`: діапазон фізичних регістрів MMIO перевіряється, резервується в кореневому дереві ресурсів і відображається у віртуальний простір ядра.
3. `devm_clk_get_enabled()`: тактовий генератор готується та вмикається. Якщо тактування не вдалося ввімкнути, відображення MMIO та виділена пам'ять `priv` автоматично звільняються без додаткового коду.
4. `devm_add_action_or_reset(..., acme_hw_disable_action)`: реєструє виклик зупинки апаратної генерації даних. Важливо, що дія реєструється **після** увімкнення тактування та запису в регістри. Якщо реєстрація дії зазнає невдачі через брак пам'яті під вузол `devres`, суфікс `_or_reset` негайно викличе саму функцію `acme_hw_disable_action()`, запобігаючи неконтрольованій роботі чіпа.
5. `devm_add_action_or_reset(..., acme_cancel_work_action)`: реєструє синхронне скасування таймерів та фонових потоків ядра (`cancel_delayed_work_sync`).
6. `devm_request_irq()`: прив'язує апаратне переривання до обробника.
7. `devm_hwmon_device_register_with_info()`: експортує атрибути датчика у простір користувача через підсистему апаратного моніторингу HWMON.

### 2. Послідовність демонтажу під час unbind / remove

Коли пристрій вилучається з системи (наприклад, через sysfs за шляхом `/sys/bus/platform/drivers/acme-sensor/unbind` або під час вивантаження модуля командою `rmmod`), ядро викликає функцію `devres_release_all(&pdev->dev)`. Список розмотується у строго зворотній послідовності (LIFO):

- **Крок 1 (HWMON):** ядро вилучає пристрій із каталогу `/sys/class/hwmon/hwmonX`. Простір користувача більше не може ініціювати нові виклики `read()` через sysfs.
- **Крок 2 (IRQ):** деструктор `devm_free_irq()` відключає лінію переривання та очікує завершення будь-яких активних апаратних обробників. Апаратне залізо більше не здатне активувати обробник `acme_irq_handler`.
- **Крок 3 (Workqueue Action):** викликається `acme_cancel_work_action()`. Функція `cancel_delayed_work_sync(&priv->poll_work)` гарантує, що заплановане опитування скасовано, а якщо потік ядра `kworker` уже виконував функцію `acme_poll_worker()`, виконання блокується до повного завершення поточної ітерації.
- **Крок 4 (Hardware Disable Action):** викликається `acme_hw_disable_action()`. Оскільки відображення MMIO та тактування все ще активні, драйвер безпечно скидає біт `ACME_CTRL_ENABLE` у регістрах датчика.
- **Крок 5 (Clock):** деструктор `clk_disable_unprepare()` зупиняє генератор частоти та викликає `clk_put()`.
- **Крок 6 (MMIO):** функція `iounmap()` розриває сторінкові відображення, а шинний регіон повертається ядру.
- **Крок 7 (Пам'ять):** звільняється пам'ять структури `priv` через `kfree()`.

### 3. Ізоляція тимчасових даних через devres groups

У функції `acme_calibrate_sensor()` продемонстровано використання груп ресурсів (`devres groups`). Під час калібрування виділяється тимчасовий буфер `calib_buf` розміром 1 КБ для зчитування сирих коефіцієнтів з чіпа:

- Виклик `devres_open_group(dev, NULL, GFP_KERNEL)` розміщує у списку спеціальний вузол-маркер початку групи.
- Буфер `calib_buf` виділяється через `devm_kmalloc()`, автоматично потрапляючи всередину цієї групи.
- Після завершення калібрування (як у разі успіху, так і в разі апаратної помилки `0xFFFFFFFF`) викликається `devres_release_group(dev, group_id)`. Ядро миттєво знаходить усі ресурси, створені після маркера групи, звільняє пам'ять буфера `calib_buf` і видаляє сам маркер.
- Усі попередні базові ресурси драйвера (пам'ять `priv`, відображення `regs`, тактування `clk`) залишаються абсолютно незайманими.

## Синхронізація блокувань та контекст виконання devres

Під час виклику `devres_add()` або `devres_release_all()` ядро захищає список `devres_head` за допомогою внутрішнього спін-блокування `spinlock_t devres_lock` з маскуванням переривань (`spin_lock_irqsave`). Проте виконання самих деструкторів `dr_release_t` або користувацьких функцій `action(data)` відбувається **після** вилучення вузла зі списку і **після** відпускання блокування (`spin_unlock_irqrestore`).

Це фундаментальне архітектурне рішення означає, що всередині ваших функцій очищення дозволено:
- Використовувати сплячі блокування (м'ютекси `mutex_lock` та семафори).
- Чекати завершення операцій введення-виведення або фонових потоків (`msleep`, `usleep_range`, `wait_for_completion`, `flush_workqueue`).
- Викликати підсистеми, які вимагають контексту процесу (process context).

Єдиним обмеженням є те, що самі виклики `devm_kzalloc()` або `devm_add_action()` не можна виконувати з контексту жорстких переривань (hardirq), оскільки виділення службового вузла `devres_alloc()` потребує виділення пам'яті в SLAB.

## Діагностика та налагодження devres

Для перевірки стану списку керованих ресурсів та пошуку аномалій у ядрі доступні штатні механізми трасування та налагодження:

1. **Динамічний налагоджувальний друк (Dynamic Debug):** якщо ядро зібрано з параметром `CONFIG_DYNAMIC_DEBUG`, можна увімкнути детальний журнал усіх операцій devres для конкретного пристрою:
   ```bash
   echo "file devres.c +p" > /sys/kernel/debug/dynamic_debug/control
   ```
   У системному лозі `dmesg` відображатимуться всі операції додавання, пошуку та вивільнення вузлів разом з адресами та назвами деструкторів.

2. **Трасування ftrace:** підсистема підтримує перевірку стека викликів за допомогою функціонального трасувальника ядра:
   ```bash
   echo devres_add > /sys/kernel/tracing/set_ftrace_filter
   echo devres_release_all >> /sys/kernel/tracing/set_ftrace_filter
   echo function > /sys/kernel/tracing/current_tracer
   ```
   Це дозволяє точно зафіксувати часові інтервали між захопленням та автоматичним звільненням системних ресурсів під час тестування перепідключення пристроїв.
