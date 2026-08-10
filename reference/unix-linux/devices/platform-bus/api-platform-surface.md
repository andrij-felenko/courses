# 📋 Поверхня платформної шини: поля, виклики й файли

Точний перелік того, з чого складається платформний пристрій, що драйвер має право в нього питати і що з усього цього видно ззовні. Імена й поведінку звірено з деревом mainline; там, де від версії до версії щось мінялося, версію названо — для довідника це частина відповіді.

## `struct platform_device`

| Поле | Тип | Що це |
|---|---|---|
| `name` | `const char *` | базове ім'я; воно ж запасний ключ збігу |
| `id` | `int` | номер примірника. `PLATFORM_DEVID_NONE` (−1) — ім'я об'єкта без суфікса; `PLATFORM_DEVID_AUTO` (−2) — номер видасть ядро зі свого лічильника |
| `id_auto` | `bool` | ставиться ядром, коли номер видано автоматично: щоб при знищенні його повернути |
| `dev` | `struct device` | вкладений об'єкт моделі — саме він потрапляє в дерево, у `/sys` і в черги засинання |
| `num_resources` | `u32` | скільки елементів у масиві нижче |
| `resource` | `struct resource *` | масив ресурсів: адреси регістрів, лінії переривань, канали |
| `id_entry` | `const struct platform_device_id *` | заповнюється шиною, коли пара зійшлася за `id_table`; читається макросом `platform_get_device_id(pdev)` |
| `platform_dma_mask`, `dma_parms` | `u64`, `struct device_dma_parameters` | сховище під маску DMA: у `struct device` лежить сам лише вказівник `dma_mask`, а значенню треба десь бути — воно тут |
| `mfd_cell` | `struct mfd_cell *` | посилання на комірку багатофункційної мікросхеми, коли пристрій завела вона |

Ім'я об'єкта складається при додаванні: `"%s.%d"` з `name` і `id`, а при `PLATFORM_DEVID_NONE` — просто `"%s"`.

Три речі, потрібні щодня, лежать не в самій структурі, а у вкладеному `dev`:

| Звертання | Що дає |
|---|---|
| `dev_get_platdata(&pdev->dev)` | вказівник на `dev.platform_data` — структуру параметрів, покладену тим, хто заводив пристрій із коду |
| `pdev->dev.of_node` | вузол [дерева пристроїв](book:unix-linux/device-tree), з якого пристрій зроблено (`NULL`, якщо не з нього) |
| `pdev->dev.fwnode` | той самий вузол у загальному вигляді — дерево, ACPI або програмний вузол. Читати властивості слід через нього: `device_property_read_u32(&pdev->dev, …)` працює однаково для всіх трьох джерел |

Поле `driver_override` колись жило в `platform_device`, а тепер — у `struct device`; шина лише вмикає для своїх пристроїв відповідний атрибут.

## Ресурс

```c
struct resource {
        resource_size_t start;
        resource_size_t end;      /* включно! розмір = end − start + 1 */
        const char     *name;     /* з reg-names / interrupt-names */
        unsigned long   flags;
};
```

| Прапорець типу | Що описує |
|---|---|
| `IORESOURCE_MEM` | діапазон фізичних адрес, за якими видно регістри |
| `IORESOURCE_IO` | діапазон портів вводу-виводу (окремий адресний простір, x86) |
| `IORESOURCE_REG` | зсуви регістрів усередині чужого відображення — так адресують блоки багатофункційної мікросхеми |
| `IORESOURCE_IRQ` | лінія переривання |
| `IORESOURCE_DMA` | номер каналу прямого доступу до пам'яті |

Розмір беруть через `resource_size(res)`, а не відніманням «на око»: `end` — остання **зайнята** адреса, а не перша вільна.

⚠️ Пристрої, створені з дерева пристроїв, ресурсів типу `IRQ` більше не мають взагалі: `of_device_alloc()` заповнює масив лише з `reg`. Тому `platform_get_resource(pdev, IORESOURCE_IRQ, 0)` на такій машині поверне `NULL` — переривання беруть тільки функціями нижче.

## `struct platform_driver`

```c
struct platform_driver {
        int  (*probe)(struct platform_device *);
        void (*remove)(struct platform_device *);
        void (*shutdown)(struct platform_device *);
        int  (*suspend)(struct platform_device *, pm_message_t state);
        int  (*resume)(struct platform_device *);
        struct device_driver driver;
        const struct platform_device_id *id_table;
        bool prevent_deferred_probe;
        bool driver_managed_dma;
};
```

`remove` повертає `void` починаючи з ядра 6.11. Доти він повертав `int`, який ядро однаково відкидало: від'єднання пристрою вже не скасувати, тож відмовляти нема від чого. Заради переходу поруч якийсь час стояв другий покажчик `remove_new` із правильним типом; у 6.11 обидва імені звели в `union`, а згодом лишилося одне.

Усередині вкладеного `driver` живуть поля, без яких драйвер не працює:

| Поле | Роль |
|---|---|
| `driver.name` | ім'я каталогу в `/sys/bus/platform/drivers/`, ключ для `driver_override` і остання сходинка збігу |
| `driver.of_match_table` | масив `struct of_device_id` — збіг за `compatible` |
| `driver.acpi_match_table` | масив `struct acpi_device_id` — збіг за ідентифікатором ACPI |
| `driver.owner` | модуль-власник; макроси реєстрації підставляють його самі |
| `driver.suppress_bind_attrs` | прибирає `bind`/`unbind` із `/sys` — для драйверів, від'єднання яких небезпечне |
| `id_table` | масив `struct platform_device_id` — збіг за іменами, з довільним `driver_data` на кожен рядок |

## Помічники доступу

| Виклик | Повертає | Тонкість |
|---|---|---|
| `platform_get_resource(pdev, type, idx)` | `struct resource *` або `NULL` | `idx` — номер **серед ресурсів цього типу**, не в усьому масиві |
| `platform_get_resource_byname(pdev, type, name)` | те саме | безіменні ресурси пропускає мовчки |
| `platform_get_mem_or_io(pdev, idx)` | перший ресурс типу `MEM` **або** `IO` | для блоків, які на одній машині відображені в пам'ять, а на іншій — у порти |
| `platform_get_irq(pdev, idx)` | номер лінії (> 0) або від'ємний код | не читає поле, а **перетворює** номер входу контролера в лінійний номер Linux; звідси й `-EPROBE_DEFER` |
| `platform_get_irq_optional(pdev, idx)` | те саме | те саме, але мовчки: без повідомлення в журнал |
| `platform_get_irq_byname(pdev, "rx")` | те саме | ім'я з `interrupt-names` вузла |
| `platform_get_irq_byname_optional(pdev, "rx")` | те саме | мовчазний варіант |
| `devm_platform_ioremap_resource(pdev, idx)` | `void __iomem *`, помилка через `IS_ERR()` | ресурс типу `MEM` за номером + захоплення діапазону + [відображення регістрів](book:unix-linux/mmio-and-ioremap) одним рухом |
| `devm_platform_ioremap_resource_byname(pdev, "cfg")` | те саме | ім'я з `reg-names` |
| `devm_platform_get_and_ioremap_resource(pdev, idx, &res)` | те саме, плюс сам ресурс | коли крім вказівника потрібен ще й розмір |
| `platform_set_drvdata(pdev, p)` / `platform_get_drvdata(pdev)` | — / `void *` | обгортки над `dev_set_drvdata()`: як `remove()` знаходить те, що завів `probe()` |

Різниця між `platform_get_irq()` і його мовчазним двійником — рівно в одному рядку журналу. До того ж про `-EPROBE_DEFER` гучний варіант теж не кричить: цей код він відкладає в налагоджувальний рівень, бо відкладена спроба — не помилка. Тому «optional» беруть там, де переривання справді може бути відсутнє за задумом, а не там, де просто хочеться тиші.

**Мінімальний повний виклик** — драйвер, що бере іменовані ресурси:

```c
static int acme_probe(struct platform_device *pdev)
{
        struct acme *a;
        int irq, ret;

        a = devm_kzalloc(&pdev->dev, sizeof(*a), GFP_KERNEL);
        if (!a)
                return -ENOMEM;

        a->regs = devm_platform_ioremap_resource_byname(pdev, "cfg");
        if (IS_ERR(a->regs))
                return PTR_ERR(a->regs);

        irq = platform_get_irq_byname(pdev, "rx");
        if (irq < 0)
                return irq;

        ret = devm_request_irq(&pdev->dev, irq, acme_isr, 0,
                               dev_name(&pdev->dev), a);
        if (ret)
                return ret;

        platform_set_drvdata(pdev, a);
        return 0;
}
```

Жодного шляху виходу зі звільненням тут нема, бо все взято з префіксом `devm_` — такі захоплення [ядро скасовує саме](book:unix-linux/devres-managed-resources), коли пристрій зникає.

## Заведення пристрою

| Виклик | Коли беруть |
|---|---|
| `platform_device_register(pdev)` | готова статична структура — ініціалізувати й додати |
| `platform_device_register_simple(name, id, res, num)` | ім'я плюс масив ресурсів, більше нічого не треба |
| `platform_device_register_data(parent, name, id, data, size)` | ім'я плюс структура параметрів |
| `platform_device_register_full(&info)` | усе разом: батько, `fwnode`, ресурси, параметри, маска DMA, програмний вузол або перелік властивостей |
| `platform_device_alloc()` → `platform_device_add_resources()` → `platform_device_add_data()` → `platform_device_add()` | коли склад пристрою збирається по шматках |
| `platform_device_unregister(pdev)` | зняти й відпустити |

Два правила, порушення яких дає підступні падіння. `add_resources()` і `add_data()` **копіюють** передане, тож віддавати їм тимчасові масиви можна. А от сам об'єкт `kfree()` не звільняють ніколи: він на лічильнику посилань, тож після невдалого `platform_device_add()` кличуть `platform_device_put()`, і пам'ять поверне вже функція звільнення.

## Заведення драйвера

| Макрос або виклик | Що робить |
|---|---|
| `platform_driver_register()` / `platform_driver_unregister()` | явна пара |
| `module_platform_driver(drv)` | розгортається в `module_init`/`module_exit` — звичайний вибір для модуля |
| `builtin_platform_driver(drv)` | те саме для драйвера, вшитого в ядро назавжди |
| `platform_driver_probe(drv, probe)` | реєстрація з розрахунком на одну-єдину спробу |
| `module_platform_driver_probe()`, `builtin_platform_driver_probe()` | обгортки над попереднім |

Останні два рядки варто розібрати, бо пастка в переліку одна — і вона там. Сенс `platform_driver_probe()` — дозволити покласти саму функцію `probe()` в секцію `__init`, пам'ять якої ядро віддає назад одразу після старту. Раз функції потім просто не існує, викликати її вдруге не можна ніколи. Тому реєстрація вимикає все, що могло б покликати її ще раз: ставить `prevent_deferred_probe = true`, тож `-EPROBE_DEFER` від такого драйвера відкидається; ставить `suppress_bind_attrs = true`, тож у `/sys` не з'являються `bind` і `unbind`; після реєстрації підміняє вказівник `probe` на заглушку, яка відмовляє всім пристроям, що прийдуть згодом; і повертає `-ENODEV`, знявши драйвер, якщо жодного пристрою так і не знайшлося. Звідси й межа застосування: тільки залізо, яке напевно вже зареєстроване й точно не з'явиться пізніше. Усе інше — `module_platform_driver()` і звичайна [відкладена спроба](book:unix-linux/driver-probe-and-binding).

## Порядок збігу в `platform_match()`

Сходинки перебираються згори вниз, перша ж, що спрацювала, зупиняє перебір:

1. `dev.driver_override` — якщо поле заповнене, відповідь дає лише порівняння з ним, і решта сходинок не розглядається взагалі.
2. `of_driver_match_device()` — `compatible` вузла проти `driver.of_match_table`.
3. `acpi_driver_match_device()` — ідентифікатори ACPI проти `driver.acpi_match_table`. Драйвер зовсім без цієї таблиці теж може зійтися: коли прошивка оголосила вузол через `PRP0001`, порівняння піде по `of_match_table`.
4. `id_table` — імена, з побічним ефектом: на збігу заповнюється `pdev->id_entry`.
5. `pdev->name` проти `driver.name` — простий `strcmp`.

Пастка на четвертій сходинці: **якщо `id_table` у драйвера є, п'ятої сходинки не буде**. Порівняння повертає результат таблиці, і невдача в ній — це остаточна невдача. Драйвер із таблицею на два імені не прив'яжеться до пристрою з третім, хай навіть той збігається з `driver.name` буква в букву.

## Файли в `/sys`

| Шлях | Що з ним роблять |
|---|---|
| `/sys/bus/platform/devices/` | посилання на всі заведені пристрої — перелік того, що ядру розповіли |
| `/sys/bus/platform/drivers/` | по каталогу на кожен зареєстрований драйвер |
| `/sys/bus/platform/drivers_autoprobe` | `0` вимикає автоматичну спробу для нових пристроїв |
| `/sys/bus/platform/drivers_probe` | записати ім'я пристрою → змусити шину спробувати підібрати йому драйвер |
| `…/drivers/<ім'я>/bind`, `…/unbind` | записати ім'я пристрою → приєднати чи від'єднати руками (нема, якщо `suppress_bind_attrs`) |
| `…/devices/<ім'я>/driver_override` | записати ім'я драйвера → прив'язка тільки до нього; порожній рядок скасовує |
| `…/devices/<ім'я>/modalias` | рядок, за яким `udev` шукає модуль |
| `…/devices/<ім'я>/of_node` | посилання на вузол у `/sys/firmware/devicetree`, коли пристрій звідти |
| `/sys/kernel/debug/devices_deferred` | хто саме зараз чекає повторної спроби і чого йому бракує |

## Формати `modalias`

Рядок береться з першого джерела, яке в пристрою є: спершу дерево пристроїв, потім ACPI, і аж тоді — ім'я.

```
of:N<ім'я вузла>T<device_type>C<compatible>C<compatible>…
acpi:<HID>:<CID>:…:
platform:<name>
```

Дві дрібниці, на яких спотикаються. У формі `of:` при відсутньому `device_type` друкується `(null)` — саме так `vsnprintf` показує рядок, якого нема, — тож у реальному `/sys` видно `of:NserialT(null)Cacme,myuart-r1p2`. І псевдоніми, які [`udev`](book:unix-linux/udev-rules) шукає в модулі, виглядають інакше: `MODULE_DEVICE_TABLE(of, …)` кладе в модуль пару `of:N*T*C<compatible>` і `of:N*T*C<compatible>C*` — зірочки замість імені вузла й типу, а хвостове `C*` потрібне тому, що пристрій цілком може оголосити ще кілька `compatible` після потрібного. Псевдонім ACPI так само із зірочками: `acpi*:<ID>:*`.
