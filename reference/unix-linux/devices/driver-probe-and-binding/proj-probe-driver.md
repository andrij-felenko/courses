# ⚙️ Стенд прив'язки: збираємо драйвер і навмисно ламаємо йому probe

Три крихітні модулі — «плата», що вигадує пристрої, драйвер до одного з них і «джерело», якого спершу немає, — показують на звичайній машині, без жодного заліза, усі стани прив'язки по черзі: відкладену спробу з рядком у `devices_deferred`, автоматичний повтор після появи постачальника, пару посилань у `/sys` і ручну відв'язку.

## Задача

Стенд має відтворити ту саму сцену, з якої починається більшість розслідувань: модуль завантажено, пристрій у системі є, роботи немає, у журналі тиша. Далі — знайти причину однією командою, усунути її й побачити, як ядро повертається до відкладеного пристрою вже без нашої участі.

Наприкінці той самий пристрій треба відв'язати руками, спробувати прив'язати назад через важіль ручного керування й зрозуміти, чому одна зі спроб дає `No such device` на цілком справному драйвері.

## Ідея: чого бракує на звичайному комп'ютері

Перша перешкода: на настільній машині немає пристрою, до якого можна написати свій драйвер. Тому пристрій ми вигадаємо. Виклик `platform_device_register_simple()` створює на [шині platform](topic:unix-linux/platform-bus) пристрій, у якого немає нічого, крім імені, — рівно так залізо колись реєстрували файли опису плат. Це і є найчесніший стенд: шина platform існує саме для заліза, якого не можна знайти опитуванням.

Друга перешкода — звідки взяти справжнє відкладення. У житті драйвер не вигадує `-EPROBE_DEFER` сам: цей код йому віддають функції доступу до ресурсу (`devm_clk_get`, `devm_regulator_get`, `devm_gpiod_get`), які самі шукають постачальника й самі бачать, що його ще немає. На стенді таких постачальників не існує, тож той самий пошук ми напишемо власноруч: шукаємо на шині пристрій із заданим іменем і перевіряємо, чи він **уже прив'язаний**. Форма виходить та сама — «потрібне в системі описане, але ще не працює».

Третя умова — і найважливіша. Модуль-джерело ми завантажимо **після** драйвера й більше не торкнемося ні його, ні `termo.ko`. Повторну спробу має влаштувати саме ядро, і єдиним поштовхом до неї буде успішний `probe` зовсім іншого драйвера.

## Код

Мова тут не обговорюється: модуль ядра — це C, іншого способу немає. Три файли, кожен у своїй ролі.

**Плата.** Реєструє два порожні пристрої й на цьому все:

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>

static struct platform_device *datchyk, *dzherelo;

static int __init plata_init(void)
{
	datchyk = platform_device_register_simple("termodatchyk",
						  PLATFORM_DEVID_NONE, NULL, 0);
	if (IS_ERR(datchyk))
		return PTR_ERR(datchyk);

	dzherelo = platform_device_register_simple("dzherelo",
						   PLATFORM_DEVID_NONE, NULL, 0);
	if (IS_ERR(dzherelo)) {
		platform_device_unregister(datchyk);
		return PTR_ERR(dzherelo);
	}
	return 0;
}

static void __exit plata_exit(void)
{
	platform_device_unregister(dzherelo);
	platform_device_unregister(datchyk);
}

module_init(plata_init);
module_exit(plata_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Стенд: два вигадані пристрої на шині platform");
```

**Драйвер.** Таблиця ознак, `MODULE_DEVICE_TABLE`, перевірка постачальника, стан на `devm_` і реєстрація в підсистемі `hwmon` — останньою дією:

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/hwmon.h>
#include <linux/mod_devicetable.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/platform_device.h>

#define DZHERELO "dzherelo"

struct termo {
	struct mutex lock;
	long         mk;      /* показ у мілліградусах Цельсія */
};

static umode_t termo_visible(const void *drvdata, enum hwmon_sensor_types type,
			     u32 attr, int channel)
{
	return 0444;
}

static int termo_read(struct device *dev, enum hwmon_sensor_types type,
		      u32 attr, int channel, long *val)
{
	struct termo *st = dev_get_drvdata(dev);

	mutex_lock(&st->lock);
	st->mk += 100;        /* заліза немає — показ вигадуємо */
	*val = st->mk;
	mutex_unlock(&st->lock);
	return 0;
}

static const struct hwmon_channel_info * const termo_info[] = {
	HWMON_CHANNEL_INFO(temp, HWMON_T_INPUT),
	NULL
};

static const struct hwmon_ops termo_hwmon_ops = {
	.is_visible = termo_visible,
	.read       = termo_read,
};

static const struct hwmon_chip_info termo_chip = {
	.ops  = &termo_hwmon_ops,
	.info = termo_info,
};

/* Ознаки, за якими шина зводить нас із пристроєм. Останній рядок обнулений:
   довжини таблиця не несе, і перебір спиняється саме на порожньому імені. */
static const struct platform_device_id termo_ids[] = {
	{ "termodatchyk",    30000 },
	{ "termodatchyk-v2", 25000 },
	{ }
};
MODULE_DEVICE_TABLE(platform, termo_ids);

static int termo_probe(struct platform_device *pdev)
{
	const struct platform_device_id *id = pdev->id_entry;
	struct device *dev = &pdev->dev;
	struct device *sup, *hwmon;
	struct termo *st;

	/* 1. Чи є постачальник — і чи він уже працює. Гонку тут ми свідомо
	      не закриваємо: найгірше, що буде, — один зайвий оберт черги. */
	sup = bus_find_device_by_name(&platform_bus_type, NULL, DZHERELO);
	if (!sup || !sup->driver) {
		put_device(sup);
		return dev_err_probe(dev, -EPROBE_DEFER,
				     "джерела «%s» ще немає\n", DZHERELO);
	}
	put_device(sup);

	/* 2. Свій стан. Усе через devm_ — драбинки прибирання не буде. */
	st = devm_kzalloc(dev, sizeof(*st), GFP_KERNEL);
	if (!st)
		return -ENOMEM;
	mutex_init(&st->lock);
	st->mk = id ? id->driver_data : 30000;   /* про NULL — у пастках */

	/* 3. І аж тепер назовні. Реєстрація остання не для краси: devm_
	      розмотує список у зворотному порядку, тож при відв'язці ми
	      відпишемося з підсистеми ПЕРШИМИ — раніше, ніж помре st. */
	hwmon = devm_hwmon_device_register_with_info(dev, "termodatchyk",
						     st, &termo_chip, NULL);
	if (IS_ERR(hwmon))
		return PTR_ERR(hwmon);

	dev_info(dev, "прив'язано, початок %ld мК\n", st->mk);
	return 0;
}

static struct platform_driver termo_driver = {
	.driver   = { .name = "termo" },   /* це ім'я з'явиться в drivers/ */
	.id_table = termo_ids,
	.probe    = termo_probe,
};
module_platform_driver(termo_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Вигаданий термодатчик на шині platform");
```

Функції `remove` немає взагалі — і це не забудькуватість. Усе, що драйвер узяв, узято через [керовані ресурси](topic:unix-linux/devres-managed-resources), а їх ядро звільняє само й при невдалому `probe`, і при відв'язці.

**Джерело.** Драйвер без таблиці — збіг піде за іменем:

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>

static int dzherelo_probe(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "джерело готове\n");
	return 0;
}

static struct platform_driver dzherelo_driver = {
	.driver = { .name = "dzherelo" },
	.probe  = dzherelo_probe,
};
module_platform_driver(dzherelo_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Порожній постачальник, якого чекає термодатчик");
```

```makefile
obj-m += plata.o termo.o dzherelo.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

## Прогін

Потрібні заголовки ядра (`linux-headers-$(uname -r)` у Debian, `kernel-devel` у Fedora), змонтований `debugfs` і ядро з увімкненими `CONFIG_HWMON` та `CONFIG_DEBUG_FS` — у дистрибутивних [збірках](topic:unix-linux/kernel-config-and-build) обидва ввімкнено типово.

Спершу сама плата — пристрої з'являються, драйверів до них ще немає:

```sh
$ make && sudo insmod plata.ko
$ ls /sys/devices/platform/termodatchyk/
driver_override  modalias  power  subsystem  uevent
$ cat /sys/devices/platform/termodatchyk/modalias
platform:termodatchyk
$ modinfo -F alias termo.ko
platform:termodatchyk
platform:termodatchyk-v2
```

Рядок `modalias` пристрою й аліаси всередині `.ko` збігаються не випадково: обидва зроблено з тієї самої таблиці, і саме за цим збігом [udev](topic:unix-linux/udev-rules) підвантажив би [модуль](topic:unix-linux/kernel-modules) сам, якби той лежав у `/lib/modules`.

Тепер драйвер — і та сама сцена, з якої ми почали:

```sh
$ sudo insmod termo.ko
$ ls /sys/devices/platform/termodatchyk/driver
ls: cannot access '/sys/devices/platform/termodatchyk/driver': No such file or directory
$ dmesg | tail -1
[  731.882194] plata: loading out-of-tree module taints kernel.
$ sudo cat /sys/kernel/debug/devices_deferred
termodatchyk	джерела «dzherelo» ще немає
```

Останній рядок [журналу ядра](topic:unix-linux/kernel-log-printk) лишився тим самим, що й до `insmod`, — попередження про сторонній модуль, видане ще хвилину тому. Про наш пристрій не сказано нічого: `dev_err_probe()` мовчить, коли причина відмови `-EPROBE_DEFER`, інакше довге завантаження перетворилося б на потік однакових скарг. Зате рядок, який ми передали цій функції, стоїть у налагоджувальному файлі поруч з іменем пристрою — і `devices_deferred` тут єдине місце, де взагалі є що читати.

Різницю між «ще зарано» й «це не моє» видно з правки на один рядок. Поставте в тому самому місці `return -ENODEV` — і файл відкладених лишиться порожнім, `insmod` пройде так само тихо, а повторної спроби не буде ніколи, скільки б драйверів після того не прив'язалося. Обидві відмови ззовні виглядають однаково — пристрій без драйвера; але одна ставить пристрій у чергу, а друга закриває питання.

Далі найцікавіше — джерело. Ми завантажуємо його й більше нічого не робимо:

```sh
$ sudo insmod dzherelo.ko
$ dmesg | tail -2
[  894.512700] dzherelo dzherelo: джерело готове
[  894.512884] termo termodatchyk: прив'язано, початок 30000 мК
$ sudo cat /sys/kernel/debug/devices_deferred
$ ls -l /sys/devices/platform/termodatchyk/driver
lrwxrwxrwx 1 root root 0 ... driver -> ../../../bus/platform/drivers/termo
$ ls /sys/bus/platform/drivers/termo/
bind  termodatchyk  uevent  unbind
$ cat /sys/class/hwmon/hwmon4/name
termodatchyk
$ cat /sys/class/hwmon/hwmon4/temp1_input
30100
```

Два повідомлення розділяють мікросекунди, і в цьому вся суть: успішний `probe` джерела перевів чергу відкладених у робочу, і наш пристрій спробували вдруге — без жодної команди з нашого боку, без таймера й без графа залежностей.

Варто витратити хвилину й вивантажити всі три модулі, а потім завантажити їх у зворотному порядку — спершу `termo.ko`, тоді `dzherelo.ko` і аж наприкінці `plata.ko`. Кінцевий стан вийде той самий, із тим самим `hwmon4`. Відкладення станеться й тут, але побачити його вже не вдасться. `plata_init()` реєструє термодатчик першим рядком, і в ту мить джерела ще немає; наступний рядок реєструє джерело, його `probe` вдається — і чергу проходять знову. Усе відкладення живе кілька мікросекунд усередині одного `insmod`. Причому повторний прохід ядро віддає окремому потоку, тож він може статися вже після того, як команда повернулася: ще одне нагадування, що вдалий `insmod` і готовий пристрій — різні події.

![Три знімки /sys уздовж прогону: після завантаження драйвера пристрій без посилання driver і рядок у devices_deferred; після появи джерела — пара посилань в обидва боки, порожній devices_deferred і файл temp1_input у hwmon; після ручної відв'язки — знову жодного посилання, але devices_deferred порожній](img/lab-snapshots.svg)

*У каталозі пристрою перший і третій стовпці не відрізняються нічим; що саме сталося — «чекає постачальника» чи «відв'язали руками» — каже лише `devices_deferred`.*

## Ручні важелі

Відв'язка — один рядок, і разом із нею зникає все, що драйвер видав назовні:

```sh
$ echo termodatchyk | sudo tee /sys/bus/platform/drivers/termo/unbind
$ ls /sys/class/hwmon/
hwmon0  hwmon1  hwmon2  hwmon3
$ sudo cat /sys/kernel/debug/devices_deferred
$ echo termodatchyk | sudo tee /sys/bus/platform/drivers/termo/bind
```

Пристрій `hwmon4` зник — його існування трималося на прив'язці, а не на завантаженому модулі. Файл відкладених при цьому порожній: пристрій нікого не чекає, він просто нічий.

Тепер важіль, який доручає пристрій конкретному драйверові. Туди пишуть ім'я **драйвера**, а не пристрою, і на цьому спотикаються майже всі:

```sh
$ echo termodatchyk | sudo tee /sys/bus/platform/drivers/termo/unbind
$ echo termodatchyk | sudo tee /sys/devices/platform/termodatchyk/driver_override
$ echo termodatchyk | sudo tee /sys/bus/platform/drivers/termo/bind
tee: /sys/bus/platform/drivers/termo/bind: No such device
$ echo termo | sudo tee /sys/devices/platform/termodatchyk/driver_override
$ echo termodatchyk | sudo tee /sys/bus/platform/drivers/termo/bind
$ echo | sudo tee /sys/devices/platform/termodatchyk/driver_override
```

Помилка `No such device` тут не про несправність. Функція збігу шини platform, побачивши непорожній `driver_override`, більше нічого не звіряє — ані таблиці, ані імені: вона просто порівнює записаний рядок з іменем драйвера. Ми записали ім'я пристрою, воно не збіглося з `termo`, і збіг не відбувся. Порожній запис скасовує це правило й повертає звичайний перебір.

## Пастки

**Забутий порожній рядок наприкінці таблиці.** Перебір ознак у шині platform написано як `while (id->name[0])` — його спиняє саме нульовий байт першого символу імені. Без обнуленого рядка перебір іде далі в сусідню пам'ять: у кращому разі ядро негайно падає, у гіршому — драйвер мовчки бере чужий пристрій, і шукати причину доведеться довго. Компілятор не допоможе: масив без термінатора — цілком правильний C.

**`id_entry` порожній саме тоді, коли прив'язку зробила людина.** Покажчик на рядок таблиці ставить лише той код, який по таблиці й пройшов. Прив'язка через `driver_override` до таблиці не доходить, збіг за іменем драйвера — теж, і `pdev->id_entry` лишається `NULL`. Драйвер, який розіменовує його без перевірки, падає рівно на тому шляху, яким користуються руками. Тому в `termo_probe` стоїть `id ? id->driver_data : 30000`, а драйвери в дереві ядра для того самого мають `device_get_match_data()`.

**Реєстрація в підсистемі раніше за готовність стану.** Виклик `devm_hwmon_device_register_with_info()` не «оголошує намір» — після нього файл `temp1_input` уже є в `/sys`, і сусіднє ядро процесора може ту ж мить покликати `termo_read()`. Ініціалізуйте `st->lock` після цього рядка — і перший же `cat` візьме неготовий [замок](topic:unix-linux/kernel-locking). Той самий порядок працює і в зворотний бік: керовані ресурси розмотуються від останнього до першого, тож реєстрація останньою дією означає, що при відв'язці нас найперше відпишуть із підсистеми й лише потім звільнять пам'ять, якою вона користувалася. Поміняйте два рядки місцями — і `unbind` звільнить стан під живим читачем.

**Відв'язка нікого не питає.** Запис у `unbind` виконує повний `remove` незалежно від того, чи є користувачі. Наш `hwmon` це переживає, бо файли атрибутів у `sysfs` тримають власні посилання й не дають зникнути з-під читача. Але інші канали назовні такого захисту не мають: відкритий [вузол у `/dev`](topic:unix-linux/device-file-model), заведений таймер, робота в черзі чи потік ядра переживуть звільнення стану й стрибнуть у порожнечу. Усе, що може покликати драйвер, мусить бути спинене раніше, ніж помре те, чим воно користується, — і саме тому `bind`/`unbind` не варто пропонувати як зручну кнопку на змонтованому диску.
