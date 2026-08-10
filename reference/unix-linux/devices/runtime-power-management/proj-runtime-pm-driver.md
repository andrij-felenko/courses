# ⚙️ Лабораторія автосну: модуль, у якому лічильник видно наживо

Півтори сотні рядків мовою C заводять у системі пристрій, у якому немає нічого, крім обліку живлення: три зворотні виклики замість вимикання напруги пишуть у журнал і чесно сплять кілька десятків мілісекунд, а один файл у sysfs дозволяє «звернутися до пристрою» на задану кількість мілісекунд. Далі — два вікна термінала, у яких видно, як лічильник падає до нуля, як витримка з'їдає короткі паузи й у яких саме місцях драйвер ламає собі облік.

## Завдання

Судити про керування живленням із чужого драйвера важко: усе цікаве ховається за реальним залізом, а ознака правильної роботи — кілька зекономлених міліватт, яких ніде не видно. Тож зробимо навпаки: заберемо залізо й лишимо саму бухгалтерію.

Потрібен модуль, який заводить пристрій із трьома зворотними викликами `runtime_suspend`, `runtime_resume`, `runtime_idle` і одним атрибутом `poke`. Запис числа в `poke` означає «попрацюй із пристроєм стільки мілісекунд». Усе інше — вмикання обліку в `probe`, симетричне вимикання у відв'язці й збалансовані лічильники на гілках помилок.

## Ідея

Три рішення роблять із цього робочу лабораторію.

**Пристрій без шини.** Наше залізо ніде не оголошене: його не знайде ні PCI, ні USB, ні [дерево пристроїв](book:unix-linux/device-tree). Для такого випадку в ядрі є платформна шина — місце для вузлів, про які просто хтось сказав, що вони існують. `platform_device_register_simple("pmlab", 0, NULL, 0)` створює екземпляр, `platform_driver_register()` реєструє драйвер, ядро зводить їх за іменем і кличе `probe`.

**Затримка замість вимикання.** Зворотні виклики нічого не вимикають, зате сплять: 40 мс на пробудження, 10 мс на присипляння. Це не декорація. Саме тривалість переходу робить присипляння платною операцією, і без неї всі досліди виглядали б однаково — миттєвими.

**Робота, яку видно.** `poke` бере число, будить пристрій, спить задану кількість мілісекунд і відпускає. Змінюючи паузи між записами, ви керуєте єдиною величиною, від якої залежить рішення ядра, — тривалістю простою між зверненнями.

## Код

Модуль цілком. Він розрахований на ядра, у яких `remove` платформного драйвера повертає `void`, а `RUNTIME_PM_OPS()` уже є; якщо збірка лається на тип `remove`, дерево старіше й поле зветься `remove_new`.

```c
// pmlab.c — пристрій, у якому немає нічого, крім обліку живлення
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/pm_runtime.h>
#include <linux/delay.h>
#include <linux/kstrtox.h>

#define PMLAB_RESUME_MS       40   /* «підняти напругу й відновити регістри» */
#define PMLAB_SUSPEND_MS      10   /* «зберегти контекст і зняти напругу»    */
#define PMLAB_AUTOSUSPEND_MS 500   /* витримка перед сном                    */

/* ── три зворотні виклики: замість заліза — журнал і чесна затримка ─────── */

static int pmlab_runtime_suspend(struct device *dev)
{
	dev_info(dev, "suspend: гашу живлення\n");
	msleep(PMLAB_SUSPEND_MS);
	return 0;
}

static int pmlab_runtime_resume(struct device *dev)
{
	dev_info(dev, "resume: подаю живлення\n");
	msleep(PMLAB_RESUME_MS);          /* тут живе ціна пробудження */
	return 0;
}

static int pmlab_runtime_idle(struct device *dev)
{
	dev_info(dev, "idle: лічильник щойно впав до нуля\n");
	return 0;                         /* 0 → ядро саме попросить присипляння */
}

static const struct dev_pm_ops pmlab_pm_ops = {
	RUNTIME_PM_OPS(pmlab_runtime_suspend, pmlab_runtime_resume,
		       pmlab_runtime_idle)
};

/* ── атрибут: запис числа = звернення до пристрою на стільки мілісекунд ─── */

static ssize_t poke_store(struct device *dev, struct device_attribute *attr,
			  const char *buf, size_t count)
{
	unsigned int ms;
	int ret;

	ret = kstrtouint(buf, 10, &ms);
	if (ret)
		return ret;
	if (ms > 2000)
		return -ERANGE;

	ret = pm_runtime_resume_and_get(dev);  /* +1; на невдачі не лишить +1 */
	if (ret)
		return ret;

	msleep(ms);                            /* «робота» з пристроєм */
	dev_info(dev, "poke: попрацював %u мс\n", ms);

	pm_runtime_put_autosuspend(dev);       /* −1 і, якщо нуль, — відлік */
	return count;
}
static DEVICE_ATTR_WO(poke);               /* права 0200: пише лише root */

static struct attribute *pmlab_attrs[] = {
	&dev_attr_poke.attr,
	NULL,
};
ATTRIBUTE_GROUPS(pmlab);

/* ── вмикання й вимикання обліку ────────────────────────────────────────── */

static int pmlab_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int ret;

	pm_runtime_set_active(dev);            /* правда: живлення вже подано */
	pm_runtime_set_autosuspend_delay(dev, PMLAB_AUTOSUSPEND_MS);
	pm_runtime_use_autosuspend(dev);
	pm_runtime_enable(dev);                /* відтепер помічники діють */

	ret = pm_runtime_resume_and_get(dev);  /* +1 на час ініціалізації */
	if (ret)
		goto err_disable;

	dev_info(dev, "готовий; затримка автосну %d мс\n", PMLAB_AUTOSUSPEND_MS);

	pm_runtime_put_autosuspend(dev);       /* −1: далі вирішує лічильник */
	return 0;

err_disable:                                   /* дзеркало до чотирьох рядків вище */
	pm_runtime_disable(dev);
	pm_runtime_dont_use_autosuspend(dev);
	pm_runtime_set_suspended(dev);
	return ret;
}

static void pmlab_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	pm_runtime_get_sync(dev);              /* розбудити, щоб гасити свідомо */
	pm_runtime_disable(dev);               /* помічники більше не діють */
	pm_runtime_dont_use_autosuspend(dev);
	pm_runtime_set_suspended(dev);         /* облік лишаємо в стані «спить» */
	pm_runtime_put_noidle(dev);            /* −1 без спроби щось присипляти */
}

static struct platform_driver pmlab_driver = {
	.probe	= pmlab_probe,
	.remove	= pmlab_remove,
	.driver	= {
		.name		= "pmlab",
		.pm		= pm_ptr(&pmlab_pm_ops),
		.dev_groups	= pmlab_groups,  /* файл з'явиться при прив'язці */
	},
};

static struct platform_device *pmlab_pdev;

static int __init pmlab_init(void)
{
	int ret;

	ret = platform_driver_register(&pmlab_driver);
	if (ret)
		return ret;

	pmlab_pdev = platform_device_register_simple("pmlab", 0, NULL, 0);
	if (IS_ERR(pmlab_pdev)) {
		platform_driver_unregister(&pmlab_driver);
		return PTR_ERR(pmlab_pdev);
	}
	return 0;
}

static void __exit pmlab_exit(void)
{
	platform_device_unregister(pmlab_pdev);   /* → pmlab_remove */
	platform_driver_unregister(&pmlab_driver);
}

module_init(pmlab_init);
module_exit(pmlab_exit);

MODULE_DESCRIPTION("Runtime PM playground: a device made of accounting only");
MODULE_LICENSE("GPL");
```

Кілька місць варті окремого погляду.

Порядок у `probe` не довільний. `pm_runtime_set_active()` стоїть **перед** `pm_runtime_enable()`, бо каже правду про поточний стан заліза, а не міняє його: за замовчуванням ядро вважає новий пристрій приспаним, і якщо мовчки ввімкнути облік, перше ж звернення спробує «розбудити» те, що вже не спить. Затримку теж задають до вмикання — інакше між `enable` і `set_autosuspend_delay` є вікно, у якому чинна затримка нульова.

Гілка `err_disable` — дзеркало вмикання, і саме її найлегше забути. `pm_runtime_disable()` знімає дію помічників, `dont_use_autosuspend` вимикає відлік, `set_suspended` повертає облік у стан, з якого ми зайшли. Без цих трьох рядків невдалий `probe` лишає по собі пристрій із увімкненим обліком і без драйвера.

`pm_ptr(&pmlab_pm_ops)` перетворюється на `NULL`, коли ядро зібране без `CONFIG_PM`. Тоді ж лінкувальник викидає й самі зворотні виклики: посилань на них не лишається.

`pm_runtime_put_noidle()` у `pmlab_remove()` — єдиний з-поміж помічників `put`, який тільки зменшує лічильник і не робить більше нічого. На виході потрібен саме він: облік уже вимкнено, статус уже виставлено руками, і будь-яка спроба ядра ще раз подумати про присипляння була б роботою над пристроєм, від якого драйвер відв'язується просто зараз.

`dev_groups` у драйвері, а не в пристрої, — щоб файл `poke` з'явився при прив'язці разом із рештою каталогу, а не окремим рухом пізніше. Це та сама обережність, з якою [модель пристроїв](book:unix-linux/sysfs-device-model) вимагає описувати атрибути наперед.

## Збірка й запуск

```make
obj-m := pmlab.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules
clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
```

Складання, завантаження й вивантаження модуля поза деревом ядра — [окрема тема](book:unix-linux/kernel-modules); тут важить лише два пункти [конфігурації](book:unix-linux/kernel-config-and-build): `CONFIG_PM` мусить бути ввімкнений, інакше вся лабораторія перетвориться на порожню оболонку, а `CONFIG_PM_ADVANCED_DEBUG` дає файл `power/runtime_usage` — без нього лічильник назовні не видно взагалі.

```
$ sudo insmod pmlab.ko
$ dmesg | tail -2
[  918.204137] pmlab pmlab.0: готовий; затримка автосну 500 мс
[  918.707412] pmlab pmlab.0: suspend: гашу живлення

$ cd /sys/devices/platform/pmlab.0/power
$ cat runtime_status control autosuspend_delay_ms
suspended
auto
500
```

Пристрій заснув сам, за півсекунди після завантаження модуля, і ніхто його про це не просив.

## Що видно в циклі

Тепер найцікавіше: два вікна. У першому — нескінченне читання трьох файлів, у другому — звернення до пристрою.

```sh
$ while :; do
>     printf '%-10s susp=%-6s use=%s\n' "$(cat runtime_status)" \
>            "$(cat runtime_suspended_time)" "$(cat runtime_usage)"
>     sleep 0.1
> done
```

```
suspended  susp=12403  use=0
suspended  susp=12503  use=0
resuming   susp=12550  use=1     # у другому вікні: echo 20 > poke
active     susp=12550  use=1     # 40 мс «заліза» минуло
active     susp=12550  use=0     # put_autosuspend: −1, пішов відлік
active     susp=12550  use=0
active     susp=12550  use=0
active     susp=12550  use=0
active     susp=12550  use=0
suspending susp=12550  use=0     # 500 мс минуло, іде зворотний виклик
suspended  susp=12556  use=0
suspended  susp=12656  use=0
```

Читати цей стовпчик варто справа наліво. `use` стрибнув до одиниці ще до того, як статус став `active`, — заявку зареєстровано раніше, ніж залізо встигло прокинутися. `susp` завмер рівно на час неспання й побіг далі після присипляння: це не оцінка, а виміряні мілісекунди, накопичені ядром. І між нулем у `use` та статусом `suspending` пройшло рівно п'ять рядків по 100 мс — та сама витримка.

> 🔧 **Навіщо це.** `runtime_suspended_time` — єдиний чесний доказ, що пристрій справді спить. З коду драйвера цього не видно ніколи: наявність зворотних викликів каже лише, що драйвер **уміє** засинати. Візьміть два зрізи цього файлу з проміжком у хвилину — і різниця скаже, скільки з тих шістдесяти секунд пристрій був без живлення. Саме так знаходять вузол, який тримає ноутбук у неспанні: не читанням коду, а порівнянням двох чисел.

Спробуйте тепер звернутися до пристрою кілька разів поспіль, з паузами, коротшими за витримку.

```
$ for i in 1 2 3 4; do echo 5 | sudo tee poke >/dev/null; sleep 0.3; done
$ dmesg | tail -6
[ 1042.113904] pmlab pmlab.0: resume: подаю живлення
[ 1042.154611] pmlab pmlab.0: poke: попрацював 5 мс
[ 1042.461238] pmlab pmlab.0: poke: попрацював 5 мс
[ 1042.767902] pmlab pmlab.0: poke: попрацював 5 мс
[ 1043.074577] pmlab pmlab.0: poke: попрацював 5 мс
[ 1043.580115] pmlab pmlab.0: suspend: гашу живлення
```

Чотири звернення — одне пробудження. Кожен `put_autosuspend` перезапускав відлік, і жодна з трьохсотмілісекундних пауз не дожила до кінця.

**Скільки коштували б ці чотири звернення без витримки:**

```
затримка автосну         500 мс
пауза між зверненнями    300 мс  → відлік щоразу скидається

із витримкою:   1 пробудження + 1 присипляння = 40 + 10        =  50 мс
без витримки:   4 пробудження + 4 присипляння = 4 · (40 + 10)  = 200 мс
```

Замініть `sleep 0.3` на `sleep 0.7` — і в журналі з'являться чотири повні цикли: пауза, довша за витримку, доводить відлік до кінця щоразу.

Помітьте, чого в журналі немає жодного разу: рядка `idle`. Зворотний виклик `runtime_idle` спрацьовує на шляху `pm_runtime_put()`, який просить ядро подумати про простій; `pm_runtime_put_autosuspend()` іде іншою дорогою — одразу замовляє присипляння з витримкою, повз повідомлення про простій. Замініть у `poke_store` один виклик на інший — і `idle` з'явиться перед кожним `suspend`.

Лишилося два вимикачі, обидва в `power/`.

```
$ echo on | sudo tee control >/dev/null
$ cat runtime_status runtime_usage
active
1
$ sleep 3; cat runtime_status
active

$ echo auto | sudo tee control >/dev/null
$ cat runtime_usage; sleep 1; cat runtime_status
0
suspended
```

Одиниця в `runtime_usage` при повній бездіяльності драйвера — найкраще пояснення того, що робить `control`: простір користувача просто взяв заявку на потребу й тримає її. Окремого механізму блокування немає.

Поряд лежить `runtime_active_time` — накопичені мілісекунди в усіх інших станах. Разом ці два числа дають час, що минув від вмикання обліку, і в цьому їхня друга користь: помітна нестача в сумі означає, що частину часу облік для пристрою був просто вимкнений — хтось кликав на нього `pm_runtime_disable()`. Пристрій, який «не спить», варто спершу перевірити саме цим відніманням, бо вимкнений облік і активний пристрій виглядають назовні майже однаково.

```
$ echo -1 | sudo tee autosuspend_delay_ms >/dev/null
$ echo 5 | sudo tee poke >/dev/null
$ sleep 3; cat runtime_status
active
```

Від'ємна витримка означає «ніколи не присипляти автоматично». Пристрій прокинувся й лишився активним назавжди — доки хтось не поверне туди додатне число.

## Чотири пастки, які легко відтворити просто тут

**Незбалансований `put`.** Приберіть із `poke_store` рядок `pm_runtime_put_autosuspend(dev)` і перезберіть модуль. Пристрій прокинеться при першому ж зверненні й більше не засне ніколи, а `runtime_usage` після чотирьох звернень покаже `4`. У справжньому драйвері симптом виглядає як «пристрій чомусь не економить», і шукати його в коді можна довго: усе працює правильно, просто заявки ніхто не знімає. Дзеркальна помилка — зайвий `put` — ловиться одразу: ядро повертає лічильник назад у нуль, віддає `-EINVAL` і пише в журнал `Runtime PM usage count underflow!`.

**`get_sync` на гілці помилки.** `pm_runtime_get_sync()` піднімає лічильник **до** спроби пробудження й не опускає його, якщо пробудження не вдалося. Тому наївний код

```c
	ret = pm_runtime_get_sync(dev);
	if (ret < 0)
		return ret;              /* ← +1 лишився назавжди */
```

лишає по собі вічну заявку саме тоді, коли з пристроєм і так уже щось не гаразд. Правильних варіантів два: `pm_runtime_resume_and_get()`, який прибирає за собою сам, або той самий `get_sync` із `pm_runtime_put_noidle(dev)` перед виходом.

Друга половина цієї пастки — сам код повернення. `pm_runtime_resume()` віддає `1`, коли пристрій уже був активним, а `pm_runtime_get_sync()` чесно передає цю одиницю далі. Тому перевірка `if (ret)` після `get_sync` оголошує помилкою найзвичайніший випадок з усіх — звернення до пристрою, який і так не спав; єдина правильна перевірка там `if (ret < 0)`. У `resume_and_get()` цієї двозначності немає: на успіх він повертає рівно нуль, і саме тому в `poke_store` вище стоїть коротке `if (ret)`.

**Синхронний помічник із обробника переривання.** Усередині `pm_runtime_get_sync()` стоїть `might_sleep_if(!(rpmflags & RPM_ASYNC) && !dev->power.irq_safe)` — і це не випадковість: виклик чекає, поки закінчиться `runtime_resume`, тобто в нашому модулі спить сорок мілісекунд. З увімкненим `CONFIG_DEBUG_ATOMIC_SLEEP` ядро скаже про це прямо («sleeping function called from invalid context»); без нього ви отримаєте зависання без пояснень. У [верхньому обробнику переривання](book:unix-linux/interrupts-bottom-halves) є лише два законні шляхи: `pm_runtime_get_noresume()` разом із `pm_request_resume()` або обіцянка `pm_runtime_irq_safe()`, яка зобов'язує тримати активним ще й батьківський пристрій.

**Довільний код помилки з `runtime_suspend`.** Поверніть із `pmlab_runtime_suspend()` не нуль, а `-EIO`, і пристрій зламається назавжди:

```
$ cat runtime_status
error
$ echo 5 | sudo tee poke
tee: poke: Invalid argument
```

Ядро розрізняє два роди відмов. `-EBUSY` і `-EAGAIN` означають «зараз незручно, спробуйте потім»: статус лишається `active`, життя триває. Будь-який інший код осідає в полі `runtime_error`, і після цього кожна перевірка перед сном чи пробудженням повертає `-EINVAL` — саме воно й дійшло до `tee` як `Invalid argument`. Вийти з цього стану ззовні неможливо: `runtime_status` у sysfs доступний лише для читання, тож статус мусить виставити сам драйвер викликом `pm_runtime_set_active()` або `pm_runtime_set_suspended()`. На практиці це означає вивантажити модуль і завантажити знову — і саме тому «повернути помилку» зі зворотного виклику присипляння варто рівно двома кодами з трьох.
