# 📋 Поверхня devres: службовий шар, дії, пам'ять і сімейства `devm_`

Механізм керованих ресурсів має два поверхи, і в драйверах видно майже завжди лише верхній — сотні готових обгорток `devm_`. Тут зібрано обидва за ядром Linux 6.x: точні сигнатури службового шару, яким пишуть власні керовані обгортки; перелік сімейств по підсистемах із тим, що кожне повертає **й як саме в нього перевіряти помилку** (угод тут три, і плутають їх постійно); і два перемикачі, якими весь список стає видно в журналі.

## Службовий шар: два типи вказівників і десяток функцій

Усе, що механізм знає про чужий ресурс, задають два типи з `<linux/device/devres.h>`:

```c
typedef void (*dr_release_t)(struct device *dev, void *res);
typedef int  (*dr_match_t)(struct device *dev, void *res, void *match_data);
```

`release` — те, чим вузол звільняють; `match` — те, чим вузол упізнають серед однотипних. Майже скрізь `match` подають як `NULL`: тоді підходить перший-ліпший вузол із потрібною функцією звільнення, а `match_data` не розглядають узагалі.

| виклик | що робить | повертає |
| --- | --- | --- |
| `devres_alloc(release, size, gfp)` | виділяє вузол із шапкою й місцем на `size` байтів даних; **у список не додає** | вказівник на дані або `NULL` |
| `devres_alloc_node(release, size, gfp, nid)` | те саме на заданому вузлі NUMA | так само |
| `devres_free(res)` | викидає вузол, який **ще не додали** до списку | — |
| `devres_add(dev, res)` | чіпляє готовий вузол у список пристрою | — |
| `devres_find(dev, release, match, match_data)` | шукає вузол, нічого не міняючи | дані або `NULL` |
| `devres_get(dev, new_res, match, match_data)` | знайти такий вузол, а як немає — додати поданий; зайвий звільняє сам | дані: знайдені або свої |
| `devres_remove(dev, release, match, match_data)` | знімає вузол зі списку, **не** звільняючи | дані знятого або `NULL` |
| `devres_destroy(dev, release, match, match_data)` | знімає й звільняє вузол, **не кличучи** `release` | `0` або `-ENOENT` |
| `devres_release(dev, release, match, match_data)` | знімає, кличе `release`, звільняє | `0` або `-ENOENT` |
| `devres_for_each_res(dev, release, match, match_data, fn, data)` | кличе `fn` для кожного відповідного вузла під спінлоком пристрою | — |

Дрібниця, яку видно лише в заголовку: `devres_alloc` — не функція, а макрос над `__devres_alloc_node()`, і зайвим аргументом туди йде дослівний текст `#release`. Саме цей рядок згодом з'являється в налагоджувальному журналі.

Пара `devres_destroy` / `devres_release` різниться рівно одним: чи виконають функцію звільнення. `destroy` — коли драйвер уже віддав ресурс руками й лишилося прибрати запис. `release` — коли ресурс треба віддати **зараз**, не чекаючи відв'язки.

### Мінімальний робочий виклик

Власний керований ресурс — це три рядки: виділити вузол із потрібною функцією звільнення, заповнити дані, додати в список.

```c
struct acme_gate {
	void __iomem	*ctrl;
};

static void acme_gate_release(struct device *dev, void *res)
{
	struct acme_gate *g = res;

	writel(0, g->ctrl);
}

static int acme_gate_open(struct device *dev, void __iomem *ctrl)
{
	struct acme_gate *g;

	g = devres_alloc(acme_gate_release, sizeof(*g), GFP_KERNEL);
	if (!g)
		return -ENOMEM;

	g->ctrl = ctrl;
	writel(ACME_GATE_ON, ctrl);
	devres_add(dev, g);	/* з цієї миті звільнення гарантоване */
	return 0;
}
```

Проміжок між `devres_alloc()` і `devres_add()` — єдине місце, де вузол не належить нікому. Якщо на ньому щось піде не так, звільняти треба саме через `devres_free()`, а не `kfree()`: у шапці лежить службовий заголовок, і `kfree()` за вказівником на `data` цілить не туди.

## Групи: межі всередині списку

| виклик | що робить | повертає |
| --- | --- | --- |
| `devres_open_group(dev, id, gfp)` | ставить маркер початку; `id == NULL` → ідентифікатором стає сам повернений вказівник | маркер або `NULL` |
| `devres_close_group(dev, id)` | ставить маркер кінця; `id == NULL` → закриває найсвіжішу відкриту | — |
| `devres_release_group(dev, id)` | звільняє все, що лягло між маркерами | кількість звільнених вузлів |
| `devres_remove_group(dev, id)` | знімає **лише маркери**; уміст лишається в списку пристрою | — |

Остання пара і є суттю груп: після `close` вибір із двох — `release_group()` відкочує шматок, `remove_group()` розчиняє його в загальному списку, тобто затверджує. Групи можна вкладати одна в одну. Відкриття позначене `__must_check` не для форми: маркер — теж вузол, його виділення теж може провалитися, і група, яку не відкрили, мовчки не обмежить нічого.

## Універсальні дії

Гачок для того, чого ядро не роздає й для чого готової обгортки не буде ніколи: зупинити двигун, погасити підсвітку, повернути мікросхему в режим спокою.

```c
int  devm_add_action(struct device *dev, void (*action)(void *), void *data);
int  devm_add_action_or_reset(struct device *dev, void (*action)(void *), void *data);
void devm_release_action(struct device *dev, void (*action)(void *), void *data);
void devm_remove_action(struct device *dev, void (*action)(void *), void *data);
int  devm_remove_action_nowarn(struct device *dev, void (*action)(void *), void *data);
bool devm_is_action_added(struct device *dev, void (*action)(void *), void *data);
```

Обидва `add_` — макроси над `__devm_add_action()`, і зайвим аргументом знову йде дослівна назва функції. Повертають `0` або `-ENOMEM`; варіант `_or_reset` перед поверненням помилки сам кличе `action(data)`, тож необоротну дію можна реєструвати одразу після неї й не боятися розриву.

Тотожність вузла тут — **пара** `(action, data)`, а не сама функція: два виклики з тією самою функцією й різними даними дають два різні вузли, і знімають їх теж окремо. `devm_remove_action()` лається через `WARN_ON`, коли такої пари немає; `devm_remove_action_nowarn()` мовчки повертає `-ENOENT`.

## Пам'ять

Керована пам'ять — найдешевший вузол у списку: корисне навантаження вузла і є та сама пам'ять, окремого `kmalloc()` під неї не роблять. Усе, що знадобиться про [slab та прапорці `GFP_`](book:unix-linux/kernel-memory-slab) — виділення в ядрі буває зі сном і без, і `devm_` цього не міняє: прапорець ви подаєте самі.

| виклик | зауваги |
| --- | --- |
| `void *devm_kmalloc(dev, size, gfp)` | базовий; на невдачі `NULL` |
| `void *devm_kzalloc(dev, size, gfp)` | inline-обгортка, додає `__GFP_ZERO` |
| `void *devm_kmalloc_array(dev, n, size, flags)` | з перевіркою переповнення `n × size` |
| `void *devm_kcalloc(dev, n, size, flags)` | те саме плюс обнулення |
| `void *devm_krealloc(dev, ptr, size, gfp)` | `__must_check`; змінює розмір уже керованої області |
| `void *devm_kmemdup(dev, src, len, gfp)` | копія буфера |
| `void *devm_kmemdup_array(dev, src, n, size, flags)` | копія масиву з перевіркою переповнення |
| `char *devm_kstrdup(dev, s, gfp)` | копія рядка |
| `const char *devm_kstrdup_const(dev, s, gfp)` | якщо `s` лежить у незмінному сегменті — повертає **його ж** і вузла не заводить |
| `char *devm_kasprintf(dev, gfp, fmt, ...)` | форматований рядок; є й `devm_kvasprintf()` зі `va_list` |
| `void devm_kfree(dev, const void *p)` | знаходить вузол за вказівником на дані й виймає його зі списку |
| `unsigned long devm_get_free_pages(dev, gfp_mask, order)` | цілі сторінки; на невдачі **`0`**, а не `NULL` |
| `void devm_free_pages(dev, unsigned long addr)` | дострокове звільнення сторінок |

Усе сімейство сигналізує про невдачу лише відсутністю результату — жодного `ERR_PTR` тут немає й бути не може.

## Три угоди про помилку

Перш ніж дивитися на таблицю підсистем, варто розібрати колонку «перевірка»: у ядрі уживаються три різні способи сказати «не вийшло», і в межах **однієї** підсистеми можуть трапитися два з них.

```
int          →  ret < 0        →  if (ret) return ret;
вказівник    →  IS_ERR(p)      →  if (IS_ERR(p)) return PTR_ERR(p);
вказівник    →  p == NULL      →  if (!p) return -ENOMEM;
```

Пастка тут не теоретична: **`IS_ERR(NULL)` — хибне**. Перевірка `IS_ERR()` на функції, що повертає `NULL`, помилку просто не побачить, і драйвер піде далі з порожнім вказівником — упаде він уже деінде. Взірцева пара — робота з [регістрами в пам'яті](book:unix-linux/mmio-and-ioremap): `devm_ioremap()` віддає `NULL`, а `devm_ioremap_resource()` — `ERR_PTR`, і саме заради коду помилки другу свого часу й додали.

Друга пастка — варіанти з хвостиком `_optional`. Там `NULL` означає не збій, а «в описі плати такого ресурсу немає, працюй без нього»; подальші виклики з таким вказівником нічого не роблять і не падають. Отже, `NULL` треба перевіряти тільки в неоптовому варіанті, а в `_optional` — навпаки, пропускати.

## Сімейства по підсистемах

| підсистема | типові виклики | повертає | перевірка |
| --- | --- | --- | --- |
| тактування | `devm_clk_get(dev, id)`, `devm_clk_get_optional()`, `devm_clk_get_enabled()`, `devm_clk_get_optional_enabled()` | `struct clk *` | `IS_ERR`; в `_optional` `NULL` — норма |
| тактування, гуртом | `devm_clk_bulk_get(dev, num, clks)`, `devm_clk_bulk_get_all()` | `int` | `ret < 0` |
| регулятори | `devm_regulator_get(dev, id)`, `devm_regulator_get_optional()`, `devm_regulator_bulk_get()` | `struct regulator *` / `int` | `IS_ERR` / `ret < 0` |
| регулятори, з умиканням | `devm_regulator_get_enable(dev, id)`, `devm_regulator_get_enable_optional()` | `int` | `ret < 0` |
| GPIO | `devm_gpiod_get(dev, con_id, flags)`, `_index()`, `_optional()`, `devm_gpiod_get_array()` | `struct gpio_desc *` | `IS_ERR` |
| скидання | `devm_reset_control_get_exclusive(dev, id)`, `_optional_exclusive()`, `_shared()`, `devm_reset_control_array_get_exclusive()` | `struct reset_control *` | `IS_ERR` |
| IOMAP | `devm_ioremap(dev, offset, size)`, `devm_ioport_map()` | `void __iomem *` | **`NULL`** |
| IOMAP | `devm_ioremap_resource(dev, res)`, `devm_platform_ioremap_resource(pdev, i)`, `_byname()`, `devm_of_iomap()` | `void __iomem *` | **`IS_ERR`** |
| переривання | `devm_request_irq(dev, irq, handler, flags, name, dev_id)`, `devm_request_threaded_irq(…, thread_fn, …)`, `devm_free_irq()` | `int` | `ret < 0` |
| робочі черги | `devm_alloc_workqueue(dev, fmt, flags, max_active, …)`, `devm_alloc_ordered_workqueue(dev, fmt, flags, …)` | `struct workqueue_struct *` | `NULL` |
| PCI | `pcim_enable_device(pdev)`, `pcim_request_region()`, `pcim_iomap_region()`, `devm_pci_remap_cfgspace()` | `int` / `void __iomem *` | `ret < 0` / `IS_ERR` |
| DMA | `dmam_alloc_coherent()`, `dmam_alloc_attrs()`, `dmam_pool_create()` | вказівник | `NULL` |
| I²C | `devm_i2c_add_adapter(dev, adap)`, `devm_i2c_new_dummy_device(dev, adap, addr)` | `int` / `struct i2c_client *` | `ret < 0` / `IS_ERR` |
| SPI | `devm_spi_register_controller(dev, ctlr)`, `devm_spi_alloc_host()` | `int` / вказівник | `ret < 0` / `NULL` |
| регістрова мапа | `devm_regmap_init_mmio()`, `devm_regmap_init_i2c()`, `devm_regmap_init_spi()` | `struct regmap *` | `IS_ERR` |
| hwmon | `devm_hwmon_device_register_with_info(dev, name, drvdata, chip, groups)` | `struct device *` | `IS_ERR` |
| IIO | `devm_iio_device_alloc(parent, sizeof_priv)`; `devm_iio_device_register()`, `devm_iio_triggered_buffer_setup()` | вказівник / `int` | `NULL` / `ret < 0` |
| input | `devm_input_allocate_device(dev)` | `struct input_dev *` | `NULL` |
| сторожовий таймер | `devm_watchdog_register_device(dev, wdd)` | `int` | `ret < 0` |
| світлодіоди | `devm_led_classdev_register(parent, cdev)`, `_ext()` | `int` | `ret < 0` |
| годинник RTC | `devm_rtc_allocate_device(dev)`; `devm_rtc_register_device(rtc)` | вказівник / `int` | `IS_ERR` / `ret < 0` |

Кілька рядків тут варті окремого слова.

Префікси не завжди `devm_`. PCI має свій, `pcim_`, і поводиться інакше за всіх: `pcim_enable_device()` не захоплює ресурс, а **перемикає пристрій у керований режим**, після чого керованими стають і подальші виклики захоплення діапазонів. Ще одна тонкість — `pcim_iomap_regions()` і `pcim_iomap_table()` позначені застарілими; нове пишуть на `pcim_iomap_region()` та `pcim_request_region()`, по одному діапазону за раз. Робота з DMA має префікс `dmam_` і своє [сімейство відображень](book:unix-linux/dma-and-buffers).

Кероване не завжди означає «звільниться саме воно». `devm_input_allocate_device()` заводить пристрій вводу так, що подальший **звичайний** `input_register_device()` теж скасується автоматично — [підсистема вводу](book:unix-linux/input-evdev) сама зауважує керований спосіб виділення. Схожа асиметрія в IIO та RTC: виділення й реєстрація там окремі виклики, і кожен має свій керований варіант.

Не все з ланцюжка захоплення взагалі має керовану форму. Номер лінії [переривання](book:unix-linux/interrupts-bottom-halves) беруть через `platform_get_irq()` — і в нього немає й не потрібно `devm_`-двійника: номер не займає ресурсу, віддавати нічого. Так само немає керованого варіанта в `clk_prepare_enable()` окремо — його поглинули в `devm_clk_get_enabled()`, бо парне вимикання тепер робить вузол.

## Налагодження: побачити список

Список devres не має власного файла в sysfs — його показує сама збірка ядра.

**`CONFIG_DEBUG_DEVRES`** (у `lib/Kconfig.debug`, «Managed device resources verbose debug messages») дописує в шапку кожного вузла ім'я й розмір. Ім'я — та сама дослівна назва функції, яку макроси `devres_alloc` і `devm_add_action` підхопили на місці виклику, тож у журналі видно не адресу, а `devm_kzalloc_release` чи `acme_engine_stop`.

**`devres.log`** — перемикач самого виводу, оголошений як `module_param_named(log, log_devres, int, S_IRUGO | S_IWUSR)`. Отже, він працює двома шляхами: `devres.log=1` у рядку завантаження ядра або запис у `/sys/module/devres/parameters/log` на ходу — з нього ж значення й читають. Поза `CONFIG_DEBUG_DEVRES` параметра не існує зовсім.

Рядок у [журналі ядра](book:unix-linux/kernel-log-printk) виходить за форматом `"DEVRES %3s %p %s (%zu bytes)"` — операція, адреса вузла, ім'я, розмір:

```
acme fe801000.acme: DEVRES ADD ffff888103d2a800 devm_kzalloc_release (64 bytes)
```

Подія додавання й подія звільнення пишуться однаково, тож у стрічці одразу видно й склад списку, і **порядок** — а він тут майже завжди і є відповіддю на питання «чому впало».

Ті самі події віддає й точка трасування `devres_log`: `devres_log()` кличе `trace_devres_log()` поряд із виводом у журнал. Через [ftrace і точки трасування](book:unix-linux/ftrace-tracepoints) їх можна фільтрувати за пристроєм і не топити журнал — для завантаження, де таких подій тисячі, це єдиний спосіб дивитися прицільно.
