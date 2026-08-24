# ⚙️ Постачальник доменів своїми руками: батько, піддомен і споживач на ньому

Дві з половиною сотні рядків мовою C заводять у системі два домени живлення, у яких увесь «вимикач» — це одна булева змінна й рядок у журналі. Решта — справжня: той самий `pm_genpd_init()`, той самий губернатор, той самий порядок викликів, що й на кристалі. Тому в `dmesg` видно рівно те, чого на реальній платі не спіймаєш: мить, коли останній пристрій заснув, і два вимикачі відкриваються один за одним — спершу піддомен, потім батько.

Мова тут не обговорюється: це код ядра, а ядро пишуть на C.

## Завдання

На справжньому кристалі постачальник доменів захований усередині драйвера контролера живлення на кілька тисяч рядків, де genpd — сотня рядків із них, а решта — послідовності вмикання, скидання, обхідні шляхи для помилок кремнію. Вирізати з цього механізм неможливо: щоб побачити, як домен ухвалює рішення, доводиться вірити чужому коду.

Зберемо натомість скелет. Два домени: `pd-media` — батьківський, `pd-display` — його піддомен. Один пристрій-споживач, повішений на піддомен через властивість `power-domains` у [дереві пристроїв](topic:unix-linux/device-tree) — тому самому місці, звідки ядро дізнається про залізо, якого не можна знайти опитуванням шини. Ознака успіху проста: `pm_genpd_summary` показує вкладеність, а один запис у файл `power/control` споживача змушує обидва вимикачі відкритися в журналі — знизу вгору.

## Ідея

Три рішення роблять із цього робочу лабораторію.

**Вимикач — це прапорець.** У справжньому постачальнику `power_on`/`power_off` — єдине місце, де хтось торкається регістра контролера живлення. Заміняємо їх на `pr_info()` і `bool powered`; усе інше — лічильники, черга викликів, губернатор — лишається чинним кодом ядра. Обман рівно один, і він на самому краю.

**Два платформні драйвери в одному модулі.** Постачальник прив'язується до вузла контролера живлення, споживач — до свого. Це відтворює справжній розкол: два незалежні драйвери, які знаходять одне одного через [шину platform](topic:unix-linux/platform-bus) — дім для вбудованих у кристал блоків, що не вміють оголосити себе самі.

**Керуємо штатним файлом.** Власного атрибута для дослідів не треба: [runtime PM](topic:unix-linux/runtime-power-management), який рахує заявників на пристрій і присипляє його на нулі, уже дає `power/control`. Запис `on` тримає споживача активним, `auto` відпускає. Увесь дослід — два `echo`.

## Постачальник: два домени й ребро між ними

```c
// demo-genpd.c — два домени живлення, піддомен і споживач на ньому
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/pm_domain.h>
#include <linux/pm_runtime.h>
#include <linux/pm_qos.h>
#include <linux/delay.h>
#include <linux/of.h>

/* ── «залізо»: кожен вимикач — це один прапорець ─────────────────────────── */

struct demo_domain {
	struct generic_pm_domain genpd;      /* мусить бути першим полем */
	bool			 powered;    /* замість біта в регістрі PMU */
};

enum { DEMO_PD_MEDIA, DEMO_PD_DISPLAY, DEMO_PD_COUNT };

static int demo_power_on(struct generic_pm_domain *genpd)
{
	struct demo_domain *d = container_of(genpd, struct demo_domain, genpd);

	usleep_range(800, 1200);             /* напруга усталюється */
	d->powered = true;
	pr_info("%s: power_on\n", genpd->name);
	return 0;
}

static int demo_power_off(struct generic_pm_domain *genpd)
{
	struct demo_domain *d = container_of(genpd, struct demo_domain, genpd);

	d->powered = false;
	pr_info("%s: power_off (стан %u)\n", genpd->name, genpd->state_idx);
	return 0;
}

#define DEMO_DOMAIN(nm) {					\
	.genpd = {						\
		.name	   = nm,				\
		.power_on  = demo_power_on,			\
		.power_off = demo_power_off,			\
	},							\
}

static struct demo_domain demo_domains[DEMO_PD_COUNT] = {
	[DEMO_PD_MEDIA]	  = DEMO_DOMAIN("pd-media"),
	[DEMO_PD_DISPLAY] = DEMO_DOMAIN("pd-display"),
};

static struct generic_pm_domain *demo_domain_ptrs[DEMO_PD_COUNT];

static struct genpd_onecell_data demo_onecell = {
	.domains     = demo_domain_ptrs,
	.num_domains = DEMO_PD_COUNT,
};

/* ── реєстрація: ініціалізувати → вкласти → аж тоді віддати назовні ──────── */

static int demo_pd_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int i, ret;

	for (i = 0; i < DEMO_PD_COUNT; i++) {
		demo_domain_ptrs[i] = &demo_domains[i].genpd;

		/* is_off = true — обіцянка про залізо: воно справді знеструмлене.
		   Заразом це знімає «тримати ввімкненим до ->sync_state».      */
		ret = pm_genpd_init(&demo_domains[i].genpd,
				    &simple_qos_governor, true);
		if (ret)
			goto err_undo;
	}

	ret = pm_genpd_add_subdomain(&demo_domains[DEMO_PD_MEDIA].genpd,
				     &demo_domains[DEMO_PD_DISPLAY].genpd);
	if (ret)
		goto err_undo;

	/* вкладеність зібрана — тепер споживач не застане півготового дерева */
	ret = of_genpd_add_provider_onecell(dev->of_node, &demo_onecell);
	if (ret)
		goto err_subdomain;

	dev_info(dev, "домени зареєстровано: pd-media ⊃ pd-display\n");
	return 0;

err_subdomain:
	pm_genpd_remove_subdomain(&demo_domains[DEMO_PD_MEDIA].genpd,
				  &demo_domains[DEMO_PD_DISPLAY].genpd);
err_undo:
	while (--i >= 0)
		pm_genpd_remove(&demo_domains[i].genpd);
	return ret;
}

static void demo_pd_remove(struct platform_device *pdev)
{
	int i;

	of_genpd_del_provider(pdev->dev.of_node);
	pm_genpd_remove_subdomain(&demo_domains[DEMO_PD_MEDIA].genpd,
				  &demo_domains[DEMO_PD_DISPLAY].genpd);
	for (i = 0; i < DEMO_PD_COUNT; i++)
		pm_genpd_remove(&demo_domains[i].genpd);
}

static const struct of_device_id demo_pd_match[] = {
	{ .compatible = "demo,pd-controller" },
	{ }
};
MODULE_DEVICE_TABLE(of, demo_pd_match);

static struct platform_driver demo_pd_driver = {
	.probe	= demo_pd_probe,
	.remove	= demo_pd_remove,
	.driver	= {
		.name		= "demo-pd-controller",
		.of_match_table	= demo_pd_match,
	},
};
```

Порядок трьох дій у `probe` жорсткий, і кожна межа має причину. `pm_genpd_init()` мусить пройти на обох доменах раніше за `pm_genpd_add_subdomain()` — ребро проводиться між уже готовими вершинами. А `of_genpd_add_provider_onecell()` стоїть останнім, бо саме він робить домени видимими ззовні: щойно постачальник зареєстрований, будь-який споживач може прив'язатися просто зараз, і застати недобудоване дерево вкладеності — питання секунд.

Два дрібніші рішення в цьому коді варті окремого рядка. `genpd.name` — вказівник, який `pm_genpd_init()` **не копіює**: він лише робить `dev_set_name()` по ньому. Літерал у статичній структурі живе, доки живе модуль, а от ім'я з локального буфера перетвориться на сміття, щойно `probe` завершиться. І `state_count` ми лишили нулем — тоді genpd заводить один типовий стан із нульовими затримками, а губернатор, який рахує бюджет, у такій арифметиці ніколи не відмовляє. Щоб побачити відмову, треба або заповнити масив `states`, або притиснути споживача обмеженням — це буде нижче.

## Споживач: драйвер, який про домени не знає

```c
/* ── споживач ────────────────────────────────────────────────────────────── */

static int demo_consumer_runtime_suspend(struct device *dev)
{
	dev_info(dev, "runtime_suspend: контекст збережено\n");
	return 0;
}

static int demo_consumer_runtime_resume(struct device *dev)
{
	dev_info(dev, "runtime_resume: живлення вже є, відновлюю регістри\n");
	return 0;
}

static const struct dev_pm_ops demo_consumer_pm_ops = {
	RUNTIME_PM_OPS(demo_consumer_runtime_suspend,
		       demo_consumer_runtime_resume, NULL)
};

/* НАВМИСНО неправильно: «читання регістра» без заявки на живлення */
static ssize_t raw_read_show(struct device *dev,
			     struct device_attribute *attr, char *buf)
{
	bool live = demo_domains[DEMO_PD_DISPLAY].powered;

	return sysfs_emit(buf, "регіон %s: читання %s\n",
			  live ? "живий" : "знеструмлений",
			  live ? "пройшло б" : "підвісило б шину");
}
static DEVICE_ATTR_RO(raw_read);

static struct attribute *demo_consumer_attrs[] = {
	&dev_attr_raw_read.attr,
	NULL,
};
ATTRIBUTE_GROUPS(demo_consumer);

static int demo_consumer_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int ret;

	pm_runtime_set_autosuspend_delay(dev, 500);
	pm_runtime_use_autosuspend(dev);
	pm_runtime_enable(dev);

	ret = pm_runtime_resume_and_get(dev);   /* тільки після цього рядка
						   можна чіпати залізо */
	if (ret)
		goto err_disable;

	dev_info(dev, "ініціалізація заліза\n");

	/* завести файл power/pm_qos_resume_latency_us; поки без обмеження */
	dev_pm_qos_expose_latency_limit(dev, PM_QOS_RESUME_LATENCY_NO_CONSTRAINT);

	pm_runtime_put_autosuspend(dev);
	return 0;

err_disable:
	pm_runtime_disable(dev);
	pm_runtime_dont_use_autosuspend(dev);
	return ret;
}

static void demo_consumer_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	dev_pm_qos_hide_latency_limit(dev);
	pm_runtime_get_sync(dev);               /* розбудити, поки облік діє */
	pm_runtime_disable(dev);
	pm_runtime_dont_use_autosuspend(dev);
	pm_runtime_put_noidle(dev);
}

static const struct of_device_id demo_consumer_match[] = {
	{ .compatible = "demo,pd-consumer" },
	{ }
};
MODULE_DEVICE_TABLE(of, demo_consumer_match);

static struct platform_driver demo_consumer_driver = {
	.probe	= demo_consumer_probe,
	.remove	= demo_consumer_remove,
	.driver	= {
		.name		= "demo-pd-consumer",
		.of_match_table	= demo_consumer_match,
		.pm		= pm_ptr(&demo_consumer_pm_ops),
		.dev_groups	= demo_consumer_groups,
	},
};

/* ── постачальник реєструється першим ────────────────────────────────────── */

static int __init demo_genpd_init(void)
{
	int ret;

	ret = platform_driver_register(&demo_pd_driver);
	if (ret)
		return ret;

	ret = platform_driver_register(&demo_consumer_driver);
	if (ret)
		platform_driver_unregister(&demo_pd_driver);
	return ret;
}

static void __exit demo_genpd_exit(void)
{
	platform_driver_unregister(&demo_consumer_driver);
	platform_driver_unregister(&demo_pd_driver);
}

module_init(demo_genpd_init);
module_exit(demo_genpd_exit);

MODULE_DESCRIPTION("Two genpd domains, a subdomain and a consumer on it");
MODULE_LICENSE("GPL");
```

Найважливіше в цьому шматку — те, чого в ньому немає. Слово «домен» не трапляється в споживачі жодного разу: ні пошуку постачальника, ні вмикання, ні перевірки. Шина platform сама викликає `dev_pm_domain_attach()` **до** `probe`, і саме тому драйвер контролера дисплея однаково працює на кристалі зі спільним регіоном і на кристалі, де в нього регіон власний.

Порядок вивантаження в `demo_genpd_exit()` теж не косметика. Спершу знімається драйвер споживача — разом із ним пристрій відв'язується від домену; лише після цього має право піти постачальник. `pm_genpd_remove()` повертає `-EBUSY`, доки в домені лишається хоч один пристрій, піддомен або батько, і зворотний порядок дав би два незнищенні домени в живому ядрі.

## Оверлей: де сказано, хто в чиєму регіоні

```dts
/dts-v1/;
/plugin/;

&{/} {
	demo_pmu: power-controller {
		compatible = "demo,pd-controller";
		#power-domain-cells = <1>;      /* одне число = індекс домену */
	};

	demo-consumer {
		compatible = "demo,pd-consumer";
		power-domains = <&demo_pmu 1>;  /* 1 → DEMO_PD_DISPLAY */
	};
};
```

Одиниця в `<&demo_pmu 1>` — не адреса й не ідентифікатор, а індекс у масиві `demo_onecell.domains`. Тому нумерація доменів у дереві пристроїв і порядок елементів у масиві постачальника — та сама послідовність, і розійтися їм не дасть ніхто, крім вас.

Складається оверлей звичайним `dtc -I dts -O dtb -o demo-genpd.dtbo demo-genpd.dts`. А от застосувати його — питання платформи: у ванільному ядрі немає способу зробити це з простору користувача. Лишається одне з трьох: додати обидва вузли просто в DTS плати й перезібрати образ дерева, віддати `.dtbo` завантажувачу (`fdt apply` в U-Boot), або застосувати з ядра викликом `of_overlay_fdt_apply()`. Без плати під рукою найшвидший шлях — `qemu-system-aarch64 -M virt`: вивантажити дерево через `-machine dumpdtb=`, дописати два вузли, повернути через `-dtb`.

## Що видно наживо

Складання модуля поза деревом ядра — [окрема тема](topic:unix-linux/kernel-modules); тут важить лише, щоб у конфігурації стояли `CONFIG_PM` і `CONFIG_PM_GENERIC_DOMAINS`.

```
$ sudo insmod demo-genpd.ko
$ dmesg | tail -8
demo-pd-controller power-controller: домени зареєстровано: pd-media ⊃ pd-display
pd-media: power_on
pd-display: power_on
demo-pd-consumer demo-consumer: runtime_resume: живлення вже є, відновлюю регістри
demo-pd-consumer demo-consumer: ініціалізація заліза
demo-pd-consumer demo-consumer: runtime_suspend: контекст збережено
pd-display: power_off (стан 0)
pd-media: power_off (стан 0)
```

Вісім рядків, у яких видно весь механізм. Живлення прийшло **згори вниз**: батько раніше за піддомен, бо на знеструмлений регіон нема чого подавати. Пішло **знизу вгору** і не одразу: спершу заснув пристрій, потім погас піддомен, потім батько — кожен наступний крок став можливим лише через попередній. Півсекунди між ініціалізацією й засинанням — це витримка автосну споживача; сам домен таймера не має взагалі.

Зведення показує ту саму картину статично:

```
$ cat /sys/kernel/debug/pm_genpd/pm_genpd_summary
domain                          status          children
    /device                                             runtime status
----------------------------------------------------------------------
pd-media                        off-0           pd-display
pd-display                      off-0
    /devices/platform/demo-consumer                      suspended
```

Тепер візьмемо пристрій за штатну ручку.

```
$ cd /sys/devices/platform/demo-consumer/power
$ cat ../raw_read
регіон знеструмлений: читання підвісило б шину

$ echo on | sudo tee control >/dev/null
$ cat ../raw_read
регіон живий: читання пройшло б

$ echo auto | sudo tee control >/dev/null; sleep 1
$ cat ../raw_read
регіон знеструмлений: читання підвісило б шину
```

`echo on` не вмикає домен — він бере заявку на потребу пристрою; вимикач закривається як наслідок. Далі зсуньте момент: `echo 5000 > autosuspend_delay_ms`, і після `echo auto` регіон проживе ще п'ять секунд. Домен при цьому не змінився ні на біт: чекає не він, а лічильник пристрою.

І остання ручка — та, що дає губернаторові слово:

```
$ echo n/a | sudo tee pm_qos_resume_latency_us >/dev/null
$ echo auto | sudo tee control >/dev/null; sleep 2
$ grep pd-display /sys/kernel/debug/pm_genpd/pm_genpd_summary
pd-display                      on
```

Пристрій спить, а домен горить. `n/a` тут означає «прийнятна затримка пробудження — нуль», тобто вимикати не можна ніколи; повертає все на місце `echo 0`, бо нуль у цьому файлі читається як «обмежень немає». Порядок навпаки, ніж підказує чуття.

> 🔧 **Навіщо це.** Цей файл існує не завжди: він з'являється лише тому, що драйвер покликав `dev_pm_qos_expose_latency_limit()`. Тобто відсутність `pm_qos_resume_latency_us` у каталозі пристрою нічого не каже про обмеження — вона каже, що драйвер не дав вам ручки. Обмеження з боку ядра при цьому цілком може бути виставлене, і побачити його ззовні буде нічим. Це перше, у що впирається спроба з'ясувати, чому чужий домен не гасне.

## Пастки

**`-EPROBE_DEFER`, якого ви не побачите.** Поміняйте місцями два `platform_driver_register()` у `demo_genpd_init()` — і споживач спробує прив'язатися раніше, ніж домени існують. Ваш `probe` при цьому не виконає жодного рядка: `dev_pm_domain_attach()` викликає шина **до** нього й на невдачі повертає `-EPROBE_DEFER` замість входу в драйвер. Тому шукати причину в коді `probe` марно; дивитися треба у `/sys/kernel/debug/devices_deferred`, де перелічені пристрої, що чекають на своїх постачальників. Сама [відкладена спроба](topic:unix-linux/driver-probe-and-binding) — механізм, а не помилка: ядро повторить прив'язку, щойно з'явиться постачальник, і в нашому модулі все зійдеться з другого разу.

**Регістр у `probe` до `pm_runtime_resume_and_get()`.** Тут ця помилка особливо підступна, бо на шині platform вона **не виявляється**: прив'язка до домену йде з прапорцем «увімкнути при приєднанні», тож на час `probe` регіон живий за побудовою. Код проходить рев'ю, працює на стенді й ламається пізніше — у будь-якому шляху, на який ця гарантія не поширюється: обробнику sysfs, `ioctl`, перериванні, поверненні з системного сну. Файл `raw_read` вище — саме така мить: після засинання він чесно каже, що читання пішло б у знеструмлений блок. На кристалі наслідок гірший за помилку — шина всередині кристала не поверне коду, а транзакція просто не завершиться, і машина зависне мовчки.

**Сусід без runtime PM.** Приберіть із `demo_consumer_probe()` рядок `pm_runtime_enable(dev)` і перезберіть модуль: домен не погасне більше ніколи. Причина в тому, що genpd перед вимкненням питає `pm_runtime_suspended()` на кожному своєму пристрої, а ця перевірка вимагає двох умов одночасно — статус `RPM_SUSPENDED` **і** ввімкнений облік. Пристрій із вимкненим обліком не проходить її ніколи, хоч би скільки він насправді байдикував. Діагноз видно прямо у зведенні: у стовпчику стану замість `suspended` стоятиме `unsupported`. Одне це слово й називає винуватця — драйвер, який runtime PM не реалізує, тримає під напругою весь регіон разом із сусідами.

**Домен, який не гасне одразу після реєстрації.** Поставте в `pm_genpd_init()` `is_off = false` — і домен лишиться ввімкненим навіть тоді, коли все всередині нього спить. Це не збій: сучасне ядро навмисно тримає ввімкненим той домен, який на момент реєстрації був живим, доки не спрацює `->sync_state` постачальника, тобто доки не прив'яжуться всі відомі споживачі. Захист від того, щоб не погасити регіон під носом у драйвера, який ще не завантажився. Відмовитися від очікування можна прапорцем `GENPD_FLAG_NO_STAY_ON`; збрехати про стан заліза — не можна ніяк, бо `is_off` не вимикає нічого, а лише повідомляє genpd, з чого починати облік.
