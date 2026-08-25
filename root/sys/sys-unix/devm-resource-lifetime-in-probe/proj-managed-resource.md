# ⚙️ Власний керований ресурс: збираємо вузол devres руками й дивимось, як він розкручується

Один модуль ядра на півтори сотні рядків, який заводить власний тип керованого ресурсу двома способами — довгим (`devres_alloc()` плюс своя функція звільнення) і коротким (`devm_add_action_or_reset()`), — і при відв'язці друкує в журнал те, чого зазвичай не видно: точний порядок звільнення й точний момент, коли він настає.

## Задача

Порядок звільнення в керованих ресурсах — річ, яку всі переказують («зворотний до захоплення»), але майже ніхто не бачив. Стенд має зробити його спостережним: кожен вузол при звільненні друкує свій рядок, і послідовність рядків у `dmesg` виявляється єдиним доказом.

Далі — три речі, які з цього порядку випливають. Зняти один вузол достроково й переконатися, що при відв'язці його вже немає. Побачити, що тіло `remove()` виконується **до** першого звільнення, і зловити на цьому справжнє звернення до звільненої пам'яті. І наприкінці — увімкнути власний журнал механізму й прочитати той самий прогін очима самого ядра.

## Ідея: як зробити невидиме спостережним

Перешкода одна: на настільній машині немає пристрою, до якого можна писати драйвер. Тому пристрій ми вигадаємо — `platform_device_register_simple()` заводить на [шині platform](topic:sys-unix/platform-bus) (пристрої, які не можна знайти опитуванням, реєструють кодом) порожній пристрій з одним лише іменем. Драйвер до нього — у тому самому модулі.

Далі суттєве. Керовані обгортки на кшталт `devm_ioremap()` звільняють щось справжнє, і побачити цю мить збоку неможливо. Тому наш ресурс не робитиме нічого, крім друку: «канал», у якого корисних даних — один номер, а вся функція звільнення — один `dev_info()`. Ресурс від цього не стає іграшковим: у списку пристрою його вузол нічим не відрізняється від вузла `devm_request_irq()`, і проходить його ядро за тими самими правилами.

Одну справжню необоротну дію ми все-таки заведемо — відкладену роботу, яка сама себе перезапускає й пише в буфер. Такої дії немає в готовому вигляді ні в кого, і саме на ній видно, навіщо потрібен `devm_add_action_or_reset()`. Вона ж дасть нам постріл у пастці порядку: [відкладена робота](topic:sys-unix/interrupts-bottom-halves) виконується асинхронно й нічого не знає про те, що драйвер уже відв'язують.

## Код

Мова тут не обговорюється: модуль ядра — це C.

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/delay.h>
#include <linux/device.h>
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include <linux/workqueue.h>

static bool zlamaty;
module_param(zlamaty, bool, 0444);
MODULE_PARM_DESC(zlamaty, "звільняти буфер руками в remove() — відтворити пастку");

/* ── власний ресурс довгим шляхом ──────────────────────────────────────── */

struct kanal {
	int nomer;              /* усе, що потрібне функції звільнення */
};

/* res — вказівник на ДАНІ вузла, не на його шапку. */
static void kanal_release(struct device *dev, void *res)
{
	struct kanal *k = res;

	dev_info(dev, "   <- закрив канал %d\n", k->nomer);
}

/* Ознака, за якою вузол шукають серед вузлів із тим самим release. */
static int kanal_match(struct device *dev, void *res, void *dani)
{
	struct kanal *k = res;

	return k->nomer == *(int *)dani;
}

static int kanal_vidkryty(struct device *dev, int nomer)
{
	struct kanal *k;

	k = devres_alloc(kanal_release, sizeof(*k), GFP_KERNEL);
	if (!k)
		return -ENOMEM;
	k->nomer = nomer;
	devres_add(dev, k);     /* аж ТУТ вузол лягає у список пристрою */

	dev_info(dev, "-> відкрив канал %d\n", nomer);
	return 0;
}

/* ── необоротна дія коротким шляхом ────────────────────────────────────── */

struct stend {
	struct device      *dev;
	struct delayed_work robota;
	u32                *bufer;
	unsigned long       obertiv;
};

static void stend_robota(struct work_struct *w)
{
	struct stend *s = container_of(to_delayed_work(w), struct stend, robota);

	s->bufer[0] = 0xA11CE;          /* саме цей запис і стане пострілом */
	s->obertiv++;
	schedule_delayed_work(&s->robota, msecs_to_jiffies(20));
}

static void stend_zupynyty(void *dani)
{
	struct stend *s = dani;

	cancel_delayed_work_sync(&s->robota);
	dev_info(s->dev, "   <- спинив роботу після %lu обертів\n", s->obertiv);
}

/* ── прив'язка ─────────────────────────────────────────────────────────── */

static int stend_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int shukanyy = 2;
	struct stend *s;
	struct kanal *k;
	int i, ret;

	s = devm_kzalloc(dev, sizeof(*s), GFP_KERNEL);          /* вузол 1 */
	if (!s)
		return -ENOMEM;
	s->dev = dev;
	platform_set_drvdata(pdev, s);

	for (i = 1; i <= 3; i++) {                              /* вузли 2–4 */
		ret = kanal_vidkryty(dev, i);
		if (ret)
			return ret;
	}

	if (zlamaty)                                            /* вузол 5 */
		s->bufer = kzalloc(64 * sizeof(*s->bufer), GFP_KERNEL);
	else
		s->bufer = devm_kzalloc(dev, 64 * sizeof(*s->bufer), GFP_KERNEL);
	if (!s->bufer)
		return -ENOMEM;

	/* Необоротна дія — і ОДРАЗУ ж її скасування (вузол 6). */
	INIT_DELAYED_WORK(&s->robota, stend_robota);
	schedule_delayed_work(&s->robota, msecs_to_jiffies(20));
	ret = devm_add_action_or_reset(dev, stend_zupynyty, s);
	if (ret)
		return ret;

	/* Дострокове зняття: знайти канал 2 і викинути вузол мовчки. */
	k = devres_find(dev, kanal_release, kanal_match, &shukanyy);
	dev_info(dev, "devres_find(2) -> %s\n", k ? "знайшов" : "нема");
	dev_info(dev, "devres_destroy(2) -> %d\n",
		 devres_destroy(dev, kanal_release, kanal_match, &shukanyy));

	return 0;
}

static void stend_remove(struct platform_device *pdev)
{
	struct stend *s = platform_get_drvdata(pdev);

	dev_info(&pdev->dev, "remove(): почав\n");
	if (zlamaty) {
		kfree(s->bufer);   /* у цей буфер пише робота, яка ще жива */
		msleep(100);       /* даємо їй кілька обертів, щоб не гадати */
	}
	dev_info(&pdev->dev, "remove(): вийшов, devres ще не чіпали\n");
}

static struct platform_driver stend_driver = {
	.driver = { .name = "devres-stend" },
	.probe  = stend_probe,
	.remove = stend_remove,
};

static struct platform_device *stend_pdev;

static int __init stend_init(void)
{
	int ret = platform_driver_register(&stend_driver);

	if (ret)
		return ret;

	stend_pdev = platform_device_register_simple("devres-stend",
						     PLATFORM_DEVID_NONE, NULL, 0);
	if (IS_ERR(stend_pdev)) {
		platform_driver_unregister(&stend_driver);
		return PTR_ERR(stend_pdev);
	}
	return 0;
}

static void __exit stend_exit(void)
{
	platform_device_unregister(stend_pdev);
	platform_driver_unregister(&stend_driver);
}

module_init(stend_init);
module_exit(stend_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Стенд: власний керований ресурс і порядок його звільнення");
```

```makefile
obj-m += stend.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

Дві дрібниці в цьому тексті варті окремої уваги. `devres_alloc()` — макрос, і він підставляє в шапку вузла рядок з іменем вашої функції звільнення (`"kanal_release"`); те саме роблять макроси `devm_add_action*` з іменем дії. Це знадобиться наприкінці. І `.remove` повертає `void` — так з ядра 6.11; у старших ядрах це поле зветься `.remove_new`, а `.remove` віддає `int`.

## Прогін: порядок, якого ніхто не задавав

Потрібні [заголовки ядра](topic:sys-unix/kernel-config-and-build) (`linux-headers-$(uname -r)` у Debian, `kernel-devel` у Fedora) — більше нічого.

```sh
$ make && sudo insmod stend.ko
$ dmesg | tail -5
devres-stend devres-stend: -> відкрив канал 1
devres-stend devres-stend: -> відкрив канал 2
devres-stend devres-stend: -> відкрив канал 3
devres-stend devres-stend: devres_find(2) -> знайшов
devres-stend devres-stend: devres_destroy(2) -> 0
```

Ключ до вузла — не адреса й не ім'я, а **пара «функція звільнення плюс ознака»**. Тому `devres_find()` шукає лише серед каналів і не спіткнеться об вузол `devm_kzalloc()`, що лежить у тому самому списку. `devres_destroy()` знімає знайдений вузол і звільняє пам'ять під ним, але **не кличе** `kanal_release` — рядка про закриття каналу 2 у виводі немає. Якби ми хотіли, щоб дію було виконано просто зараз, потрібна була б `devres_release()` — та сама операція плюс виклик.

Тепер відв'язка:

```sh
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/unbind
$ dmesg | tail -5
devres-stend devres-stend: remove(): почав
devres-stend devres-stend: remove(): вийшов, devres ще не чіпали
devres-stend devres-stend:    <- спинив роботу після 47 обертів
devres-stend devres-stend:    <- закрив канал 3
devres-stend devres-stend:    <- закрив канал 1
```

Тут одразу три відповіді. Обидва рядки `remove()` стоять **перед** усіма звільненнями — жодного вузла не було чіпано, доки тіло `remove()` не дійшло до кінця. Канали виходять у порядку 3, 1: другого немає, бо ми його зняли, а третій іде раніше за перший — список розкручують з хвоста. І дія, зареєстрована останньою, звільняється першою, хоча всередині вона розіменовує `s`, виділений найпершим викликом `devm_kzalloc()`. Це не щастя: саме зворотний порядок і робить таке розіменування законним.

Другу половину гарантії видно з правки на один рядок. Поверніть із `kanal_vidkryty()` для третього каналу `-EINVAL` — і `probe()` вийде з помилкою, не дійшовши ні до буфера, ні до реєстрації дії:

```sh
$ dmesg | tail -4
devres-stend devres-stend: -> відкрив канал 1
devres-stend devres-stend: -> відкрив канал 2
devres-stend devres-stend:    <- закрив канал 2
devres-stend devres-stend:    <- закрив канал 1
```

Ми не написали для цього ані рядка. `remove()` теж не покликано — його кличуть лише для драйвера, якого встигли прив'язати. Звільнення прийшло з іншого боку: каркас прив'язки, побачивши ненульовий код, сам пройшовся списком. Саме через ці двері щоразу проходить і відкладена спроба, коли драйвер повертає `-EPROBE_DEFER`.

## Пастка порядку

Той самий модуль із `zlamaty=1` бере буфер звичайним `kzalloc()` і звільняє його руками в `remove()` — рівно так, як це роблять драйвери, у яких частина захоплень лишилася ручною:

```sh
$ sudo rmmod stend && sudo insmod stend.ko zlamaty=1
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/unbind
$ dmesg | tail -20
devres-stend devres-stend: remove(): почав
==================================================================
BUG: KASAN: slab-use-after-free in stend_robota+0x44/0xb0 [stend]
Write of size 4 at addr ffff888104c1a800 by task kworker/2:1/58
...
Freed by task 1874:
 kfree+0x...
 stend_remove+0x38/0x70 [stend]
```

Робота ще жива, бо її скасування — керований вузол, а вузли чіпають лише після `remove()`. Вона пише в буфер, якого вже немає, і [санітайзер пам'яті ядра](topic:sys-unix/kasan-kernel-address-sanitizer) показує обидва боки події одразу. Без збірки з KASAN та сама помилка теж помітна, тільки пізніше й глухіше: із `slub_debug=P` у рядку завантаження [шар slab](topic:sys-unix/kernel-memory-slab) поскаржиться на зіпсовану отруту вже при наступному використанні цієї комірки. `msleep(100)` тут лише перетворює рідкісний збіг на певність — приберіть його, і та сама помилка стрілятиме раз на кілька десятків прогонів.

Полагодити можна двома способами, і обидва повертають механізму цілісність: або віддати буфер `devm_kzalloc()` (тоді порядок розставить усе сам), або спинити роботу першим рядком `remove()`, не покладаючись на вузол.

## Журнал самого механізму

Коли список поводиться незрозуміло, у ядра є для цього вбудований лічильник. Він працює лише у збірках із `CONFIG_DEBUG_DEVRES` — у дистрибутивних це майже завжди так:

```sh
$ grep DEBUG_DEVRES /boot/config-$(uname -r)
CONFIG_DEBUG_DEVRES=y
$ sudo rmmod stend && sudo insmod stend.ko      # знову без zlamaty
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/unbind
$ echo 1 | sudo tee /sys/module/devres/parameters/log
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/bind
$ dmesg | grep DEVRES
devres-stend devres-stend: DEVRES ADD ffff888107a4e300 devm_kzalloc_release (112 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e380 kanal_release (4 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e400 kanal_release (4 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e480 kanal_release (4 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e500 devm_kzalloc_release (256 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e580 stend_zupynyty (16 bytes)
devres-stend devres-stend: DEVRES REM ffff888107a4e400 kanal_release (4 bytes)
```

Той самий важіль вмикається й рядком завантаження ядра — `devres.log=1`, коли вузли треба бачити ще до того, як з'явиться `/sys`. У виводі три дієслова: `ADD` — вузол ліг у список, `REM` — вузол зняли (це наш `devres_destroy`), `REL` — вузол звільнено проходом при відв'язці. Розмір `4 bytes` — це `sizeof(struct kanal)`, а `16 bytes` для дії — службова пара «вказівник на функцію плюс дані».

Дві дрібниці, на яких спотикаються. Ім'я `devm_kzalloc_release` стоїть у рядку для **будь-якого** виділення сімейства `devm_kmalloc()` — його там прописано наглухо, і `devm_kmalloc()` не відрізниш від `devm_kzalloc()`. І рядки виходять рівнем `err`, тобто червоним у `journalctl` та крізь будь-який тихий рівень [консолі](topic:sys-unix/kernel-log-printk); тривоги в них рівно нуль.

## Ціна й пастки

Кожен вузол — це шапка плюс вставляння в хвіст списку під спінлоком пристрою: незначуще для десятка захоплень у `probe()` і геть недоречне в гарячому шляху. `devres_find()` та її похідні йдуть списком лінійно, тож дострокове зняття серед сотень вузлів коштує прохід по всіх.

**`devm_` поза `probe()`.** Заведіть у стенді атрибут у `sysfs`, який кличе `devm_kzalloc()` на кожен запис, і подивіться на журнал: `ADD` буде тисяча, `REL` — жодного до самої відв'язки. Це не витік у звичному сенсі — пам'ять таки звільниться, — але пристрій, який працює місяцями, отримає список без стелі.

**`kfree()` замість `devm_kfree()`.** Пам'ять із `devm_kzalloc()` — це корисне навантаження вузла, а не окреме виділення. Просто `kfree()` знищить разом із даними й шапку — а список пристрою залишиться зшитим крізь звільнену область. Правильний виклик `devm_kfree()` знаходить вузол за вказівником на дані й спершу виймає його зі списку. Симетрична помилка теж карається: `devm_kfree()` на пам'яті, взятій не через `devm_`, дає `WARN_ON` — усередині це той самий `devres_destroy()`, який повертає `-ENOENT`.

**`devm_add_action()` без `_or_reset` після необоротної дії.** У стенді роботу вже запущено на рядок раніше за реєстрацію скасування. Замініть виклик на `devm_add_action()` і уявіть, що виділення вузла провалилося: `probe()` поверне помилку, скасовувати роботу буде нікому, а сама вона й далі перезапускатиметься — вже в модулі, який ніхто не тримає.

**`devres_destroy()` там, де потрібна `devres_release()`.** Нашому каналу байдуже: у ньому нема чого віддавати. Але вузол, зроблений навколо `ioremap()`, після `devres_destroy()` зникне разом із єдиним записом про захоплений діапазон — і жодного попередження не буде, бо для механізму це штатна операція.

**Ручне захоплення тягне за собою драбину.** Гілка `zlamaty` бере буфер через `kzalloc()` — і рядком нижче, якщо `devm_add_action_or_reset()` поверне `-ENOMEM`, `probe()` вийде, лишивши цей буфер назавжди. Одне ручне захоплення серед керованих повертає в функцію рівно ту помилку, заради усунення якої писався весь механізм.
