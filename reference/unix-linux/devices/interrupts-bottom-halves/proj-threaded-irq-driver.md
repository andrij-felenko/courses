# ⚙️ Драйвер, у якому працюють усі три нижні половини

Зберемо модуль для давача на шині I²C, де відкладену роботу розкладено на всі три маршрути одразу: потік переривання розмовляє з шиною, BH-робота розкодовує вибірки просто в softirq, а звичайна робоча черга зводить статистику під м'ютексом. Драйвер невеликий — але саме на такому розмірі видно те, чого не показує підручниковий «привіт, світе»: межа між контекстами — це межа, через яку дані передають чергою, а не змінною.

## Задача

Давач сидить на [шині I²C](topic:communications/i2c-bus) і має власну лінію переривання. Усередині в нього невеликий апаратний накопичувач: набралося вісім вибірок — він піднімає лінію й тримає її піднятою, доки накопичувач не прочитають. Від драйвера потрібно:

- `/dev/davach`, з якого читають по рядку «мітка часу, значення»; порожньо — читач засинає на [черзі очікування](topic:unix-linux/kernel-wait-queues), а не крутиться в циклі;
- мітка часу мусить бути знята **в мить переривання**, а не тоді, коли до неї дійдуть руки: інакше в ній записана не подія, а завантаженість машини;
- `stats` у sysfs: скільки вибірок пройшло, скільки викинуто, які межі;
- вивантаження драйвера не лишає позаду ні черг, ні потоків, які згодом стрибнуть у звільнену пам'ять.

## Ідея: чотири виконавці й одна течія

Кожна ланка робить рівно те, на що має право у своєму контексті, — і саме право, а не обсяг роботи, вирішує, де вона стоїть.

**Верхня половина** не може дізнатися про давач нічого: усі його регістри лежать за шиною, а обмін на шині — це сон. Тому робити їй лишається одне: зняти мітку [монотонного годинника](topic:unix-linux/kernel-timekeeping) й розбудити потік.

**Потік переривання** проводить обмін — вісім вибірок по два байти одним блоковим читанням. Це і є те, заради чого потрібен саме потік: сотні мікросекунд, які комусь треба проспати. Читання накопичувача заразом знімає запит із лінії, і поки воно не сталося, лінія піднята, — тому маскувати її доводиться аж до кінця потоку, і саме це робить `IRQF_ONESHOT`.

**BH-робота** розкодовує сирі байти й кладе вибірки в кільце. Чому не в потоці, який їх щойно привіз? Бо доки потік не повернувся, лінія замаскована й давач мовчить, хоч і накопичує далі. Усе, що не потребує шини, варто винести за межу маскування — тоді вікно мовчання дорівнює рівно тривалості обміну. Друга вигода прихована в `queue_work()`: повторна постановка вже поставленої роботи нічого не робить, тож на сплеск із чотирьох переривань поспіль припаде один прохід BH-роботи й **одне** пробудження читачів замість чотирьох — а пробудження задачі на іншому ядрі коштує [міжпроцесорного переривання](topic:unix-linux/inter-processor-interrupts).

**Робоча черга** зводить статистику. Вона тут не тому, що роботи багато, а тому, що зведення живе під м'ютексом: його читає [sysfs](topic:unix-linux/sysfs-device-model), а показ у sysfs — це форматування в буфер і копіювання назовні, тобто контекст, який має право спати. М'ютекса не візьмеш ні в softirq, ні у верхній половині — отже, між кільцем і зведенням мусить стояти хтось, кому спати вільно.

Звідси й розкладка замків, і вона важливіша за самі механізми. До кільця, до черги сирих блоків і до «пакета» — того, що назбиралося від останнього зведення, — дотягується softirq — значить, це спін-замок, і всі, хто бере його **не** з softirq, беруть варіант `_bh`, інакше нижня половина на тому самому ядрі спробує взяти вже зайнятий замок і зависне на ньому назавжди. До зведеної статистики дотягується лише контекст задачі — значить, м'ютекс. Варіант замка обирають за тим, **хто ще торкається цих даних**, а не за звичкою; про саму межу — [замки в ядрі й атомарний контекст](topic:unix-linux/kernel-locking).

![Ланцюжок із чотирьох виконавців: верхня половина знімає мітку часу, потік читає блок вибірок по шині (весь цей час лінія замаскована ONESHOT), BH-робота в softirq розкодовує й кладе вибірки в кільце під спін-замком, kworker зводить статистику під м'ютексом; read() бере з кільця по одній вибірці, а розбирання драйвера йде проти течії](img/driver-chain.svg)

*Одна подія проходить чотири контексти. Дані між ними йдуть чергами — крім однієї-єдиної комірки, і за неї платить `IRQF_ONESHOT`.*

## Код

Вузол у `/dev` заводимо через `miscdevice` — це три поля замість двох пар реєстрацій; як влаштована довша дорога через `cdev` і клас, показано в [найпростішому символьному драйвері](topic:unix-linux/device-file-model/proj-char-driver.md).

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/devm-helpers.h>
#include <linux/fs.h>
#include <linux/i2c.h>
#include <linux/interrupt.h>
#include <linux/ktime.h>
#include <linux/math64.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/uaccess.h>
#include <linux/wait.h>
#include <linux/workqueue.h>

#define DVCH_REG_FIFO   0x02
#define DVCH_BURST      8     /* вибірок за одне переривання */
#define DVCH_SLOTS      4u    /* черга «потік → BH-робота» */
#define DVCH_RING       64u   /* степінь двійки: залишок замість ділення */
#define DVCH_LINE       48

struct dvch_sample {
	u64 ts;      /* наносекунди, зняті у верхній половині */
	s32 milli;   /* значення в тисячних */
};

struct dvch_raw {
	u64 ts;
	u8  b[DVCH_BURST * 2];
};

struct dvch {
	struct i2c_client *client;
	struct miscdevice  misc;

	/* Верхня половина → потік. Єдина передача в драйвері, що не є чергою:
	   ONESHOT не пускає другу верхню половину, доки потік не скінчився. */
	u64 stamp;

	struct work_struct bh_work;      /* softirq: розкодувати й опублікувати */
	struct work_struct stats_work;   /* kworker: звести під м'ютексом */

	/* Під спін-замком: сюди дотягується softirq. */
	spinlock_t         lock;
	struct dvch_raw    raw[DVCH_SLOTS];
	unsigned int       rhead, rtail;
	struct dvch_sample ring[DVCH_RING];
	unsigned int       head, tail;
	unsigned int       pack_n, pack_lost;
	s32                pack_min, pack_max;

	wait_queue_head_t  readers;

	/* Під м'ютексом: сюди дотягується лише контекст задачі. */
	struct mutex stats_lock;
	u64 total, lost;
	s32 all_min, all_max;
};

/* ─── верхня половина: апаратний контекст, сотні наносекунд ─────────────── */
static irqreturn_t dvch_hardirq(int irq, void *data)
{
	struct dvch *s = data;

	/* Спитати «чи наше це переривання» нема в кого: регістр стану лежить
	   за шиною. Тому лінія в цього давача мусить бути лише його.      */
	s->stamp = ktime_get_ns();
	return IRQ_WAKE_THREAD;
}

/* ─── потік переривання: контекст задачі, спати можна ───────────────────── */
static irqreturn_t dvch_thread(int irq, void *data)
{
	struct dvch *s = data;
	struct dvch_raw *slot;
	u8 buf[DVCH_BURST * 2];
	int ret;

	/* Саме це читання знімає запит із лінії — більше ніщо його не зніме. */
	ret = i2c_smbus_read_i2c_block_data(s->client, DVCH_REG_FIFO,
					    sizeof(buf), buf);
	if (ret != sizeof(buf)) {
		dev_warn_ratelimited(&s->client->dev, "шина відповіла %d\n", ret);
		return IRQ_HANDLED;   /* лінію однаково треба розмаскувати */
	}

	spin_lock_bh(&s->lock);       /* «_bh»: цей замок бере й BH-робота */
	if (s->rhead - s->rtail == DVCH_SLOTS) {
		s->rtail++;
		s->pack_lost += DVCH_BURST;
	}
	slot = &s->raw[s->rhead++ % DVCH_SLOTS];
	slot->ts = s->stamp;
	memcpy(slot->b, buf, sizeof(buf));
	spin_unlock_bh(&s->lock);

	queue_work(system_bh_wq, &s->bh_work);
	return IRQ_HANDLED;           /* звідси ядро розмаскує лінію */
}

/* ─── BH-робота: softirq; те, що колись було тасклетом ──────────────────── */
static void dvch_bh(struct work_struct *w)
{
	struct dvch *s = container_of(w, struct dvch, bh_work);
	bool published = false;

	/* Ми вже в softirq: тут беруть простий spin_lock — глушити нижні
	   половини нема від кого, вони і є ми.                          */
	spin_lock(&s->lock);
	while (s->rhead != s->rtail) {
		struct dvch_raw *slot = &s->raw[s->rtail++ % DVCH_SLOTS];
		int i;

		for (i = 0; i < DVCH_BURST; i++) {
			s16 code = (s16)(((u16)slot->b[2 * i] << 8) |
					 slot->b[2 * i + 1]);
			struct dvch_sample smp = {
				.ts    = slot->ts + i * 1000000ull,  /* 1 кГц */
				.milli = code * 1000 / 32,
			};

			if (s->head - s->tail == DVCH_RING) {
				s->tail++;      /* свіже цінніше за старе */
				s->pack_lost++;
			}
			s->ring[s->head++ % DVCH_RING] = smp;

			if (!s->pack_n || smp.milli < s->pack_min)
				s->pack_min = smp.milli;
			if (!s->pack_n || smp.milli > s->pack_max)
				s->pack_max = smp.milli;
			s->pack_n++;
		}
		published = true;
	}
	spin_unlock(&s->lock);

	if (published) {
		wake_up_interruptible(&s->readers);
		schedule_work(&s->stats_work);
	}
}

/* ─── робоча черга: kworker, спати можна ────────────────────────────────── */
static void dvch_stats(struct work_struct *w)
{
	struct dvch *s = container_of(w, struct dvch, stats_work);
	unsigned int n, lost;
	s32 lo, hi;

	spin_lock_bh(&s->lock);
	n = s->pack_n;      lost = s->pack_lost;
	lo = s->pack_min;   hi = s->pack_max;
	s->pack_n = 0;      s->pack_lost = 0;
	spin_unlock_bh(&s->lock);

	if (!n && !lost)
		return;

	mutex_lock(&s->stats_lock);
	if (n) {
		if (!s->total || lo < s->all_min)
			s->all_min = lo;
		if (!s->total || hi > s->all_max)
			s->all_max = hi;
		s->total += n;
	}
	s->lost += lost;
	mutex_unlock(&s->stats_lock);
}

/* ─── символьний пристрій ───────────────────────────────────────────────── */
static bool dvch_pop(struct dvch *s, struct dvch_sample *out)
{
	bool got = false;

	spin_lock_bh(&s->lock);
	if (s->head != s->tail) {
		*out = s->ring[s->tail++ % DVCH_RING];
		got = true;
	}
	spin_unlock_bh(&s->lock);
	return got;
}

static ssize_t dvch_read(struct file *f, char __user *ubuf,
			 size_t count, loff_t *ppos)
{
	struct dvch *s = container_of(f->private_data, struct dvch, misc);
	struct dvch_sample smp;
	char line[DVCH_LINE];
	u64 sec;
	u32 nsec;
	int len, ret;

	if (count < DVCH_LINE)
		return -EINVAL;        /* рядок цілий або жодного */

	if (!dvch_pop(s, &smp)) {
		if (f->f_flags & O_NONBLOCK)
			return -EAGAIN;
		ret = wait_event_interruptible(s->readers, dvch_pop(s, &smp));
		if (ret)
			return ret;    /* -ERESTARTSYS: прийшов сигнал */
	}

	sec = div_u64_rem(smp.ts, NSEC_PER_SEC, &nsec);
	len = scnprintf(line, sizeof line, "%llu.%09u %d\n", sec, nsec, smp.milli);
	if (copy_to_user(ubuf, line, len))
		return -EFAULT;
	return len;
}

static int dvch_open(struct inode *ino, struct file *f)
{
	return stream_open(ino, f);    /* позиції в потоці немає */
}

static const struct file_operations dvch_fops = {
	.owner = THIS_MODULE,
	.open  = dvch_open,
	.read  = dvch_read,
};

static ssize_t stats_show(struct device *dev, struct device_attribute *a,
			  char *buf)
{
	struct dvch *s = i2c_get_clientdata(to_i2c_client(dev));
	ssize_t n;

	mutex_lock(&s->stats_lock);
	n = sysfs_emit(buf, "усього %llu, викинуто %llu, від %d до %d\n",
		       s->total, s->lost, s->all_min, s->all_max);
	mutex_unlock(&s->stats_lock);
	return n;
}
static DEVICE_ATTR_RO(stats);

static struct attribute *dvch_attrs[] = { &dev_attr_stats.attr, NULL };
ATTRIBUTE_GROUPS(dvch);

/* ─── прив'язка й відв'язка ─────────────────────────────────────────────── */
static int dvch_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct dvch *s;
	int ret;

	if (client->irq <= 0)
		return dev_err_probe(dev, -EINVAL, "потрібна лінія переривання\n");

	s = devm_kzalloc(dev, sizeof(*s), GFP_KERNEL);
	if (!s)
		return -ENOMEM;

	s->client = client;
	spin_lock_init(&s->lock);
	mutex_init(&s->stats_lock);
	init_waitqueue_head(&s->readers);
	i2c_set_clientdata(client, s);

	/* devm розбирає в ЗВОРОТНОМУ порядку — отже, реєструємо ланцюжок
	   з хвоста до голови: скасувати споживача раніше за постачальника
	   означає дати постачальникові поставити роботу після скасування. */
	ret = devm_work_autocancel(dev, &s->stats_work, dvch_stats);
	if (ret)
		return ret;
	ret = devm_work_autocancel(dev, &s->bh_work, dvch_bh);
	if (ret)
		return ret;

	ret = devm_request_threaded_irq(dev, client->irq,
					dvch_hardirq, dvch_thread,
					IRQF_ONESHOT, "davach", s);
	if (ret)
		return dev_err_probe(dev, ret, "переривання %d зайняте\n",
				     client->irq);

	s->misc.minor  = MISC_DYNAMIC_MINOR;
	s->misc.name   = "davach";
	s->misc.fops   = &dvch_fops;
	s->misc.parent = dev;

	return misc_register(&s->misc);   /* останній рядок: тепер нас видно */
}

static void dvch_remove(struct i2c_client *client)
{
	struct dvch *s = i2c_get_clientdata(client);

	misc_deregister(&s->misc);
	/* Далі devm сам, проти течії: free_irq (він же дочекається потоку),
	   cancel_work_sync(bh_work), cancel_work_sync(stats_work), kfree(s). */
}

static const struct i2c_device_id dvch_id[] = { { "davach" }, { } };
MODULE_DEVICE_TABLE(i2c, dvch_id);

static const struct of_device_id dvch_of[] = {
	{ .compatible = "kurs,davach" },
	{ }
};
MODULE_DEVICE_TABLE(of, dvch_of);

static struct i2c_driver dvch_driver = {
	.driver = {
		.name           = "davach",
		.of_match_table = dvch_of,
		.dev_groups     = dvch_groups,
	},
	.probe    = dvch_probe,
	.remove   = dvch_remove,
	.id_table = dvch_id,
};
module_i2c_driver(dvch_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Давач I2C із трьома нижніми половинами");
```

`module_i2c_driver()` — це той самий `module_init`/`module_exit`, згорнутий в один рядок: на завантаженні модуля він кличе `i2c_add_driver()`, на вивантаженні — `i2c_del_driver()`. Розгортати його руками сенсу немає: ініціалізація драйвера шини — це реєстрація в шині, і більше нічого.

## Збирання й перевірка

Модуль збирається деревом ядра, тому Makefile — це два рядки й одна змінна:

```makefile
obj-m += davach.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

Прив'язка йде з дерева пристроїв — саме звідти драйвер дістає і адресу на шині, і номер переривання:

```dts
&i2c1 {
	davach@48 {
		compatible = "kurs,davach";
		reg = <0x48>;
		interrupt-parent = <&gpio>;
		interrupts = <17 IRQ_TYPE_LEVEL_LOW>;
	};
};
```

```sh
$ sudo insmod davach.ko
$ sudo cat /dev/davach
174.312004518 -1218
174.313004518 -1187
...
$ grep davach /proc/interrupts
 55:    1042      0      0      0  pinctrl-bcm2835  17 Level  davach
$ ps -eo pid,cls,rtprio,comm | grep irq/55
 312 FF      50 irq/55-davach
$ cat /sys/bus/i2c/devices/1-0048/stats
усього 8336, викинуто 0, від -1904 до 1877
```

Три виконавці видно окремо, і кожен своїм способом. Верхня половина рахується в `/proc/interrupts`. Потік має власний рядок у `ps` — із класом `FF` і пріоритетом 50, тобто реальночасовим; `chrt -f -p 30 312` міняє його на льоту, не чіпаючи коду. А BH-роботу шукають у `/proc/softirqs`: звичайна черга з `WQ_BH` їде на гнізді `TASKLET`, а з додатковим `WQ_HIGHPRI` — на `HI`. Готова черга `system_bh_wq` є в ядрі від версії 6.9; до неї це саме місце займав тасклет, і рядок у `/proc/softirqs` був той самий.

## Пастки

**Спільна лінія й `IRQ_NONE`.** Коли переривання просять із `IRQF_SHARED`, ядро на кожен сигнал обходить **усі** обробники цієї лінії, і кожен мусить чесно відповісти: моє — `IRQ_HANDLED`, не моє — `IRQ_NONE`. Відповісти можна єдиним способом — глянувши в регістр стану свого пристрою. Тепер видно, чому наш давач не має права ділити лінію: його регістр за шиною, а на шині сплять, — у верхній половині цього не зробиш узагалі. Брехня дорога в обидва боки: постійне `IRQ_HANDLED` «про всяк випадок» вимикає діагностику для всіх сусідів по лінії, а `IRQ_NONE` на власному перериванні псує лічильник ядра. Лічильник цей цілком конкретний: коли з останніх 100 000 сигналів понад 99 900 нікого не зацікавили, ядро друкує `irq NN: nobody cared (try booting with the "irqpoll" option)` і глушить лінію назавжди.

**Забутий `ONESHOT` — і машина стоїть.** Лінія в нас рівнева: давач тримає її піднятою, доки накопичувач не прочитано, а читає його потік. Без `IRQF_ONESHOT` ядро розмаскує лінію одразу, щойно верхня половина повернула `IRQ_WAKE_THREAD`, — а вона й далі піднята. І знову верхня половина, знову `IRQ_WAKE_THREAD`, знову розмаскування; потік у цьому штормі не встигає навіть початися. Коментар у `kernel/irq/manage.c` описує це коротко: «rinse and repeat». Один випадок ядро таки ловить: якщо `handler` передали як `NULL` і `IRQF_ONESHOT` не поставили, `request_threaded_irq()` відмовляє з `-EINVAL` і пише в журнал `Threaded irq requested with handler=NULL and !ONESHOT`. Але з непорожньою верхньою половиною — як у нас — ніхто не відмовить: перевірити тип лінії ядро не може, бо прапорці типу підправляє драйвер контролера. Мовчазний шторм лишається на совісті автора.

**Гонка між верхньою половиною й потоком.** `s->stamp` — одна комірка на двох, і на перший погляд це помилка: верхня половина пише, потік читає, ніякого замка немає. Рятує не везіння, а будова: `ONESHOT` тримає лінію замаскованою від входу у верхню половину до виходу з потоку, тож другої верхньої половини в цьому проміжку не буде. Приберіть `ONESHOT` на лінії, що спрацьовує фронтом (там ядро й не заперечить), — і мітку часу затре наступна подія рівно посеред обміну на шині: у вибірки виявиться час чужої події, а помилка ця плаваюча й проявиться лише під навантаженням. Тому передачу **потік → BH-робота** зроблено вже [кільцем](topic:algorithms/ring-buffer), а не коміркою: щойно потік повернув `IRQ_HANDLED`, лінію розмасковано, і наступна подія цілком може прийти раніше, ніж BH-робота торкнеться привезених байтів, — жодного `ONESHOT` над цим проміжком уже немає.

**Скасовувати треба проти течії.** У ланцюжку «переривання → потік → BH-робота → зведення» кожна ланка ставить наступну. Тому знімати їх можна лише з голови: спершу `free_irq()` (він не просто відв'язує обробник, а й чекає, доки добіжить потік), потім `cancel_work_sync(&bh_work)`, потім `cancel_work_sync(&stats_work)`. Порушите порядок — скасована робота повернеться в чергу: `cancel_work_sync()` знімає поточну постановку, але не забороняє наступну (заборона — це `disable_work_sync()` з ядра 6.10). З `devm` порядок виходить сам собою, бо ресурси звільняються у зворотному порядку до реєстрації, — тому в `dvch_probe()` черги заведено з хвоста, а переривання взято останнім. Найдорожча ж помилка тут інша й дуже стара: `INIT_WORK()` поруч із `devm_kzalloc()`. Пам'ять звільнить `devm`, а роботу не скасує ніхто — і `kworker` за мить викличе функцію зі структури, якої вже немає. `devm_work_autocancel()` із `<linux/devm-helpers.h>` існує саме для того, щоб такої пари не траплялося.

**Відкритий дескриптор рятує не від усього.** `.owner = THIS_MODULE` тримає модуль у пам'яті, поки живий бодай один `/dev/davach`, тож `rmmod` під час читання відмовить. Але `echo 1-0048 > /sys/bus/i2c/drivers/davach/unbind` виконає `dvch_remove()` попри всі відкриті дескриптори — і `devm` звільнить `struct dvch` разом із чергою очікування, на якій у цю мить спить читач. Лічильник модуля цього випадку не бачить. Чесний спосіб — не пускати структуру у вільне плавання: тримати її на лічильнику посилань і будити читачів прапорцем «пристрою більше немає», щоб `read()` повернув `-ENODEV`, а не впав.
