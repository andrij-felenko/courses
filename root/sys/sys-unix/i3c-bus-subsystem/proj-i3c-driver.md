# ⚙️ Реалізація драйвера I3C-пристрою з обробкою IBI та sysfs

Практична розробка драйвера периферійного пристрою шини I3C у ядрі Linux полягає у створенні модуля ядра, який декларує таблицю ідентифікаторів пристроїв, обробляє події призначення динамічної адреси, виконує обмін даними через приватні транзакції та налаштовує обробку внутрішньосмугових переривань (In-Band Interrupts — IBI).

У цій вставці наведено повну реалізацію драйвера ядра для вбудованого периферійного сенсора освітленості та температури (`i3c_demo_sensor`), а також розширене пояснення ключових системних викликів, моделей синхронізації та етапів розробки.

## 1. Архітектура та життєвий цикл драйвера I3C

Драйвер периферійного пристрою спирається на структуру `struct i3c_driver`, яка реєструється у підсистемі за допомогою макросу `module_i3c_driver()`. Підсистема ядра `i3c-core` порівнює атрибути виявленого на шині пристрою (його 48-бітний Provisional ID, BCR та DCR) із таблицею ідентифікаторів `id_table`. Якщо виявлено збіг, ядро викликає точку входу `probe()`.

### 1.1. Етапи виконання функції `probe()`

Під час виконання функції `probe()` драйвер виконує такі послідовні кроки:

1. **Виділення приватної структури даних (`devm_kzalloc`):** Створення екземпляра структури `struct i3c_demo_sensor_priv` у пам'яті ядра з автоматичним управлінням життєвим циклом (Devres framework). Структура зберігає вказівник на `struct i3c_device`, поточні виміряні значення та об'єкт робочої черги. Записування вказівника на приватні дані здійснюється через `i3cdev_set_drvdata()`.
2. **Перевірка апаратного ідентифікатора:** Виконання першої приватної транзакції `i3c_device_do_priv_xfers()` для зчитування внутрішнього регістра Chip ID пристрою та перевірки відповідності фізичної мікросхеми заявленій специфікації.
3. **Налаштування робочої черги:** Ініціалізація структури `struct work_struct` за допомогою макросу `INIT_WORK()` для обробки подій переривань у відкладеному контексті.
4. **Конфігурування IBI (In-Band Interrupts):** Заповнення структури `struct i3c_ibi_setup`, запит ресурсів переривання через `i3c_device_request_ibi()` та подальша активація через `i3c_device_enable_ibi()`.
5. **Створення атрибутів sysfs:** Експорт атрибутів (наприклад, поточного значення температури) у віртуальну файлову систему для доступності простору користувача за допомогою системних макросів `DEVICE_ATTR_RO()` та `ATTRIBUTE_GROUPS()`.

## 2. Повний вихідний код модуля ядра Linux

Нижче наведено вихідний код автономного драйвера для ядра Linux. Код написано мовою C відповідно до винятку §5 канону для коду ядра Linux. Драйвер містить повний цикл ініціалізації, перевірки ID, обробки IBI та створення файлів sysfs.

```c
/*
 * i3c_demo_sensor.c - Драйвер I3C сенсора з підтримкою IBI та sysfs
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/workqueue.h>
#include <linux/sysfs.h>
#include <linux/i3c/device.h>

#define SENSOR_REG_CHIP_ID   0x00
#define SENSOR_REG_TEMP_DATA 0x02
#define SENSOR_REG_CTRL      0x10

struct i3c_demo_sensor_priv {
	struct i3c_device *i3cdev;
	struct work_struct ibi_work;
	u16 last_temp;
	u8 chip_id;
};

/* Обробник нижньої половини IBI переривання */
static void i3c_demo_ibi_work_handler(struct work_struct *work)
{
	struct i3c_demo_sensor_priv *priv =
		container_of(work, struct i3c_demo_sensor_priv, ibi_work);
	struct i3c_priv_xfer xfers[2];
	u8 reg_addr = SENSOR_REG_TEMP_DATA;
	u8 raw_data[2] = {0};
	int ret;

	/* Читання регістра температури після отримання IBI сигналізації */
	xfers[0].rnw = false;
	xfers[0].len = 1;
	xfers[0].data.out = &reg_addr;

	xfers[1].rnw = true;
	xfers[1].len = 2;
	xfers[1].data.in = raw_data;

	ret = i3c_device_do_priv_xfers(priv->i3cdev, xfers, 2);
	if (ret == 0) {
		priv->last_temp = (raw_data[0] << 8) | raw_data[1];
		dev_info(&priv->i3cdev->dev,
			 "IBI оброблено: нова температура = %u\n", priv->last_temp);
	} else {
		dev_err(&priv->i3cdev->dev, "Помилка читання регістра температури через I3C\n");
	}
}

/* Callback переривання верхньої половини IBI (атомарний контекст) */
static void i3c_demo_ibi_handler(struct i3c_device *i3cdev,
				 const struct i3c_ibi_payload *payload)
{
	struct i3c_demo_sensor_priv *priv = i3cdev_get_drvdata(i3cdev);

	if (payload->len > 0) {
		u8 mdb = ((u8 *)payload->data)[0];
		dev_dbg(&i3cdev->dev, "Отримано MDB байт IBI: 0x%02x\n", mdb);
	}

	/* Передаємо обробку у робочу чергу */
	schedule_work(&priv->ibi_work);
}

/* Sysfs атрибут для зчитування температури з простору користувача */
static ssize_t temperature_show(struct device *dev,
				struct device_attribute *attr, char *buf)
{
	struct i3c_device *i3cdev = dev_to_i3cdev(dev);
	struct i3c_demo_sensor_priv *priv = i3cdev_get_drvdata(i3cdev);

	return sysfs_emit(buf, "%u\n", priv->last_temp);
}
static DEVICE_ATTR_RO(temperature);

static struct attribute *i3c_demo_attrs[] = {
	&dev_attr_temperature.attr,
	NULL,
};
ATTRIBUTE_GROUPS(i3c_demo);

static int i3c_demo_probe(struct i3c_device *i3cdev)
{
	struct i3c_demo_sensor_priv *priv;
	struct i3c_ibi_setup ibi_req = {0};
	struct i3c_priv_xfer xfers[2];
	u8 reg_addr = SENSOR_REG_CHIP_ID;
	int ret;

	priv = devm_kzalloc(&i3cdev->dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->i3cdev = i3cdev;
	i3cdev_set_drvdata(i3cdev, priv);
	INIT_WORK(&priv->ibi_work, i3c_demo_ibi_work_handler);

	/* Перевірка Chip ID пристрою */
	xfers[0].rnw = false;
	xfers[0].len = 1;
	xfers[0].data.out = &reg_addr;

	xfers[1].rnw = true;
	xfers[1].len = 1;
	xfers[1].data.in = &priv->chip_id;

	ret = i3c_device_do_priv_xfers(i3cdev, xfers, 2);
	if (ret) {
		dev_err(&i3cdev->dev, "Не вдалося зчитати Chip ID через I3C\n");
		return ret;
	}

	dev_info(&i3cdev->dev, "Успішно знайдено I3C сенсор Chip ID: 0x%02x\n", priv->chip_id);

	/* Налаштування та активація внутрішньосмугових переривань (IBI) */
	ibi_req.max_payload_len = 1;
	ibi_req.num_slots = 2;
	ibi_req.handler = i3c_demo_ibi_handler;

	ret = i3c_device_request_ibi(i3cdev, &ibi_req);
	if (ret == 0) {
		ret = i3c_device_enable_ibi(i3cdev);
		if (ret) {
			dev_warn(&i3cdev->dev, "Не вдалося увімкнути IBI переривання\n");
			i3c_device_free_ibi(i3cdev);
		} else {
			dev_info(&i3cdev->dev, "IBI переривання успішно активовано\n");
		}
	}

	return 0;
}

static void i3c_demo_remove(struct i3c_device *i3cdev)
{
	struct i3c_demo_sensor_priv *priv = i3cdev_get_drvdata(i3cdev);

	i3c_device_disable_ibi(i3cdev);
	i3c_device_free_ibi(i3cdev);
	cancel_work_sync(&priv->ibi_work);

	dev_info(&i3cdev->dev, "Драйвер I3C сенсора вивантажено\n");
}

/* Таблиця зіставлення за 48-бітним Provisional ID (PID) */
static const struct i3c_device_id i3c_demo_ids[] = {
	/* Виробник (MIPI Manuf ID), Part ID */
	I3C_DEVICE(0x01B0, 0x0042, NULL),
	{ /* Термінатор */ }
};
MODULE_DEVICE_TABLE(i3c, i3c_demo_ids);

static struct i3c_driver i3c_demo_driver = {
	.driver = {
		.name = "i3c_demo_sensor",
		.dev_groups = i3c_demo_groups,
	},
	.probe = i3c_demo_probe,
	.remove = i3c_demo_remove,
	.id_table = i3c_demo_ids,
};

module_i3c_driver(i3c_demo_driver);

MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("Демонстраційний драйвер I3C-сенсора для ядра Linux");
MODULE_LICENSE("GPL");
```

## 3. Опис механізму роботи з перериваннями IBI у розробці

Робота з внутрішньосмуговими перериваннями IBI вимагає поділу обробки на два рівні:

1. **Верхня половина (`i3c_demo_ibi_handler`):** Викликається перериванням апаратного контролера у жорсткому атомарному контексті. Тут заборонено виконувати синхронні виклики, які можуть заснути (наприклад, `i3c_device_do_priv_xfers()`, `msleep()`, виділення пам'яті `GFP_KERNEL`). Функція лишь зчитує MDB байт із корисного навантаження та ставить задачу `schedule_work()` у робочу чергу ядра.
2. **Нижня половина (`i3c_demo_ibi_work_handler`):** Виконується у контексті потоку ядра `kworker`. Тут дозволено синхронне читання регістрів через I3C-транзакції, обробку даних сенсора та виклики блокувальних функцій.

## 4. Опис прив'язки Device Tree та деструкція ресурсів

Для опису пристрою у дереві пристроїв (Device Tree) вузол I3C-сенсора розташовується як дочірній елемент вузла контролера шини I3C:

```dts
&i3c_master {
	status = "okay";

	demo_sensor: sensor@1,1b000420000 {
		reg = <1 0x01b0 0x0042>;
		assigned-address = <0x08>;
	};
};
```

Значення поля `reg` описує три параметри: номер екземпляра пристрою (`1`), MIPI Manufacturer ID (`0x01B0`) та Part ID (`0x0042`). Властивість `assigned-address` дозволяє статично зарезервувати бажану динамічну адресу (наприклад, `0x08`), яку майстер спробує призначити даному пристрою під час процедури DAA.

Під час вивантаження модуля функція `i3c_demo_remove()` виконує коректне деактивування ресурсів:
- `i3c_device_disable_ibi()` надсилає CCC команду `DISEC` для заборони генерації сигналів переривань на периферійному пристрої;
- `i3c_device_free_ibi()` звільняє виділені буфери слотів переривань у контролері;
- `cancel_work_sync(&priv->ibi_work)` гарантує, що всі завершальні фонові задачі зчитування даних дочекаються завершення виконання до того, як приватна структура пам'яті буде звільнена.

## 5. Обробка помилок та процедури відновлення

У реальних вбудованих системах периферійний I3C пристрій може втратити динамічну адресу внаслідок короткочасного просідання напруги живлення (Power Dip) або перезавантаження внутрішнього контролера сенсора.

Коли драйвер виконує транзакцію `i3c_device_do_priv_xfers()` і отримує код помилки `-ENXIO` (NACK на рівні адресації), підсистема `i3c-core` запускає механізм реінтеграції пристрою:

1. Драйвер пристрою повертає помилку у підсистему або надсилає запит на скидання.
2. Ядро шини ініціює повторний цикл `do_daa()` або відправляє адресу ССС команди `RSTDAA` з наступною повторною видачею динамічної адреси через `reattach_i3c_dev()`.
3. Після успішного відновлення адреси ядро оновлює внутрішню таблицю `bus->addrslots` та повертає пристрій у працездатний стан без вивантаження модуля драйвера.

## 6. Динамічне налагодження та відстеження трасувальних подій

Для перевірки працездатності розробленого драйвера інженери використовують механізм динамічного налагодження ядра Dynamic Debug та точки трасування tracepoints.

Увімкнення виводу налагоджувальних повідомлень для нашого модуля здійснюється через файлову систему `debugfs`:

```bash
echo "file i3c_demo_sensor.c +p" > /sys/kernel/debug/dynamic_debug/control
```

Після цього всі виклики `dev_dbg()` починають виводити детальні дампи MDB байтів у системний журнал `dmesg`.

Для перевірки результуючих транзакцій на шині без осцилографа можна скористатися точками трасування `tracefs`:

```bash
cd /sys/kernel/tracing
echo 1 > events/i3c/i3c_priv_xfer/enable
echo 1 > events/i3c/i3c_ibi/enable
cat trace_pipe
```

У журналі трасування з'являються записи з точними часовими мітками виконання кожної транзакції читання температури, що дозволяє оцінити затримку між надходженням апаратного сигналу IBI та реальним зчитуванням регістра сенсора робочою чергою.
