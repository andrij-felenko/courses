# 📋 Довідка: контракт runtime PM

Тут зібрано все, що підсистема runtime PM показує назовні: помічники, які кличе драйвер, три зворотні виклики, які він мусить написати, коди повернення в обидва боки й файли, якими цим керують із простору користувача. Оголошення наведено за ядром 6.12 (`include/linux/pm_runtime.h`, `include/linux/pm.h`, `Documentation/ABI/testing/sysfs-devices-power`); де свіжіші ядра змінили контракт, це позначено окремо — для ядра питання «а в якій версії?» доречне майже завжди.

## Помічники

Ключ до всієї таблиці — поле `power.usage_count`: [лічильник живих користувачів](topic:sf-lang/reference-counting) пристрою, доки він не нуль, присипляння навіть не розглядають. Суфікс `_sync` означає «зробити тут-таки й дочекатися», його відсутність у парі з `pm_request_*` — «поставити заявку в чергу `pm_wq` і повернутися негайно».

```c
#include <linux/pm_runtime.h>

/* увімкнення механізму для пристрою */
void pm_runtime_enable(struct device *dev);       /* −1 до power.disable_depth */
void pm_runtime_disable(struct device *dev);      /* +1; дочекатися й скасувати незавершене */
int  pm_runtime_barrier(struct device *dev);      /* тільки дочекатися й скасувати заявки */

/* заявити потребу: +1 до лічильника */
int  pm_runtime_get_sync(struct device *dev);            /* +1, розбудити, дочекатися */
int  pm_runtime_resume_and_get(struct device *dev);      /* те саме, але −1 назад на помилці */
int  pm_runtime_get(struct device *dev);                 /* +1, пробудження — заявкою */
void pm_runtime_get_noresume(struct device *dev);        /* лише +1, заліза не чіпає */
int  pm_request_resume(struct device *dev);              /* заявка на пробудження, лічильника не чіпає */
int  pm_runtime_get_if_active(struct device *dev);       /* +1 лише якщо статус уже active */
int  pm_runtime_get_if_in_use(struct device *dev);       /* +1 лише якщо лічильник уже ≠ 0 */

/* відпустити: −1 */
int  pm_runtime_put(struct device *dev);                 /* на нулі — заявка на idle */
int  pm_runtime_put_autosuspend(struct device *dev);     /* на нулі — заявка з витримкою */
int  pm_runtime_put_sync(struct device *dev);            /* на нулі — idle тут-таки */
int  pm_runtime_put_sync_suspend(struct device *dev);    /* на нулі — suspend тут-таки */
int  pm_runtime_put_sync_autosuspend(struct device *dev);
void pm_runtime_put_noidle(struct device *dev);          /* лише −1; нижче нуля не піде */

/* прямі дії, лічильника не торкаються */
int  pm_runtime_idle(struct device *dev);
int  pm_runtime_suspend(struct device *dev);
int  pm_runtime_autosuspend(struct device *dev);         /* suspend із урахуванням витримки */
int  pm_runtime_resume(struct device *dev);
int  pm_request_idle(struct device *dev);
int  pm_request_autosuspend(struct device *dev);
int  pm_schedule_suspend(struct device *dev, unsigned int delay_ms);

/* оголосити стан заліза — лише поки механізм вимкнено або після фатальної помилки */
int  pm_runtime_set_active(struct device *dev);
int  pm_runtime_set_suspended(struct device *dev);
bool pm_runtime_status_suspended(struct device *dev);    /* статус саме suspended */
bool pm_runtime_active(struct device *dev);              /* active або механізм вимкнено */
bool pm_runtime_suspended(struct device *dev);           /* suspended і механізм увімкнено */

/* політика */
void pm_runtime_use_autosuspend(struct device *dev);
void pm_runtime_dont_use_autosuspend(struct device *dev);
void pm_runtime_set_autosuspend_delay(struct device *dev, int delay_ms); /* <0 — ніколи */
void pm_runtime_mark_last_busy(struct device *dev);
void pm_runtime_forbid(struct device *dev);   /* +1 і тримати: те саме, що power/control = on */
void pm_runtime_allow(struct device *dev);    /* повернути це −1: power/control = auto */
void pm_runtime_irq_safe(struct device *dev);
void pm_suspend_ignore_children(struct device *dev, bool enable);
void pm_runtime_no_callbacks(struct device *dev);  /* + прибрати атрибути з sysfs */
```

**Що змінилося у свіжіших ядрах.** Від 6.17 позначку «щойно був зайнятий» роблять самі `pm_runtime_put_autosuspend()`, `pm_runtime_put_sync_autosuspend()`, `pm_runtime_autosuspend()` і `pm_request_autosuspend()` — окремий `pm_runtime_mark_last_busy()` поряд із ними став зайвим. Там-таки `pm_runtime_put()` оголошено `void`: його результат ні про що корисне не казав. `pm_runtime_resume_and_get()` перетворився на обгортку спільного `pm_runtime_get_active(dev, rpmflags)`, поведінки це не змінило.

## Звідки що можна кликати

Пробудження — це підйом напруги й очікування готовності, тож синхронні помічники **сплять** і в [обробнику переривання](topic:sys-unix/interrupts-bottom-halves) їм не місце.

| не спить — можна звідусіль | може заснути — лише процесний контекст |
|---|---|
| `pm_runtime_get_noresume()`, `pm_runtime_put_noidle()`, `pm_runtime_mark_last_busy()`, `pm_runtime_get()`, `pm_runtime_put()`, `pm_runtime_put_autosuspend()`, `pm_request_idle()`, `pm_request_resume()`, `pm_request_autosuspend()`, `pm_schedule_suspend()`, `pm_runtime_status_suspended()`, `pm_runtime_enable()` | усі `_sync`-варіанти, `pm_runtime_resume_and_get()`, `pm_runtime_idle()`, `pm_runtime_suspend()`, `pm_runtime_autosuspend()`, `pm_runtime_resume()`, `pm_runtime_barrier()`, `pm_runtime_disable()`, `pm_runtime_forbid()`, `pm_runtime_allow()`, `pm_runtime_use_autosuspend()`, `pm_runtime_dont_use_autosuspend()`, `pm_runtime_set_autosuspend_delay()`, `pm_runtime_set_active()` |

Праву колонку відмикає `pm_runtime_irq_safe()`: після нього зворотні виклики біжать із вимкненими перериваннями, і синхронні помічники стають дозволеними в атомарному контексті. Ціна — виклик назавжди піднімає лічильник батька, тобто батько більше ніколи не засне.

## Коди повернення помічників

| код | що означає |
|---|---|
| `0` | зроблено |
| `1` | робити не довелося: пробудження застало пристрій уже активним, присипляння — уже приспаним. Лічильник, якщо його підіймали, підвищено. `pm_runtime_resume_and_get()` цю одиницю зводить до `0` |
| `−EAGAIN` | присипляти зараз недоречно: лічильник ≠ 0 або вже стоїть зустрічна заявка на пробудження. Не помилка. Також відповідь `pm_runtime_set_active()`/`set_suspended()`, покликаних при ввімкненому механізмі й без помилки — оголошувати стан тоді не можна |
| `−EBUSY` | у пристрою є активні діти (`child_count ≠ 0` і `ignore_children` не виставлено). Не помилка. Ще так відповідає `pm_runtime_set_active()`, коли батько не активний |
| `−EACCES` | механізм для цього пристрою вимкнено: `power.disable_depth > 0` |
| `−EINVAL` | пристрій у стані помилки; доки її не знято, помічники не роблять нічого. Так само відповідають `pm_runtime_get_if_active()`/`get_if_in_use()` при вимкненому механізмі |
| `−EPERM` | обмеження затримки пробудження PM QoS не дозволяє приспати цей пристрій узагалі (`power/pm_qos_resume_latency_us` показує `n/a`) |
| `−EINPROGRESS` | від `pm_runtime_idle()`: `->runtime_idle` уже виконується |

`pm_runtime_get_if_active()` і `pm_runtime_get_if_in_use()` віддають `1`, якщо лічильник підвищено, і `0`, якщо умови не справдилися й нічого не змінилося.

## Зворотні виклики

```c
struct dev_pm_ops {
        ...
        int (*runtime_suspend)(struct device *dev);
        int (*runtime_resume)(struct device *dev);
        int (*runtime_idle)(struct device *dev);
};
```

| виклик | коли ядро його кличе | статус під час виклику | що мусить зробити |
|---|---|---|---|
| `runtime_suspend` | лічильник нуль, активних дітей немає, витримка автосну добігла | `suspending` | зберегти контекст, який зникне без живлення, і поскидати такти й регулятори |
| `runtime_resume` | хтось заявив потребу, а пристрій спить; або ядро підіймає батька перед дитиною | `resuming` | подати живлення й такти, відновити контекст, лишити пристрій цілком робочим |
| `runtime_idle` | лічильник щойно впав до нуля | лишається `active` | вирішити, чи справді час присипляти |

Що ядро робить із поверненим кодом:

| від кого | код | наслідок |
|---|---|---|
| `runtime_suspend` | `0` | статус `suspended`, `child_count` батька −1, батькові йде сповіщення про простій |
| `runtime_suspend` | `−EBUSY`, `−EAGAIN` | статус вертається в `active`, помилки немає; якщо це була спроба автосну і зворотний виклик устиг оновити позначку «щойно зайнятий», ядро саме перепризначить наступну спробу |
| `runtime_suspend` | будь-який інший | **фатально**: виставлено `power.runtime_error`, `runtime_status` показує `error`, помічники віддають `−EINVAL`, доки стан не оголосять руками |
| `runtime_resume` | `0` | статус `active` |
| `runtime_resume` | будь-яка помилка | **фатально**, наслідки ті самі |
| `runtime_idle` | `0` або зворотного виклику немає | ядро йде далі й робить `pm_runtime_autosuspend()` |
| `runtime_idle` | будь-яке ненульове | нічого не стається, пристрій лишається активним |

Вийти зі стану помилки можна лише руками: `pm_runtime_set_active()` або `pm_runtime_set_suspended()` скидають `power.runtime_error` і оголошують, у якому стані залізо насправді.

Важлива тонкість про адресата: ядро бере зворотний виклик у першої зі структур, що його має, — `dev->pm_domain->ops`, далі `dev->type->pm`, `dev->class->pm`, `dev->bus->pm`; поле `dev->driver->pm` беруть, **лише якщо жодна з них цього виклику не оголосила**. Тому на шинах на кшталт PCI чи USB драйверів `runtime_suspend` кличе не ядро, а зворотний виклик шини, і саме шина вирішує, що зробити з поверненим кодом до того, як віддати його вище.

## Макроси оголошення

```c
/* поля всередині вже наявної struct dev_pm_ops */
#define RUNTIME_PM_OPS(suspend_fn, resume_fn, idle_fn) \
        .runtime_suspend = suspend_fn, \
        .runtime_resume  = resume_fn,  \
        .runtime_idle    = idle_fn,

/* уся структура одним рядком */
#define DEFINE_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn) \
        _DEFINE_DEV_PM_OPS(name, pm_runtime_force_suspend, pm_runtime_force_resume, \
                           suspend_fn, resume_fn, idle_fn)

/* те саме, коли структуру мусить бачити інший модуль */
EXPORT_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn)
EXPORT_GPL_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn)
EXPORT_NS_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn, ns)
```

`SET_RUNTIME_PM_OPS()` — старіша назва `RUNTIME_PM_OPS()`, у сучасних ядрах це просто синонім.

Три відмінності, на яких помиляються. Перша: `DEFINE_RUNTIME_DEV_PM_OPS` **не ставить `static` сам** — його пишуть перед макросом (`static DEFINE_RUNTIME_DEV_PM_OPS(mydev_pm_ops, …)`), а от варіанти `EXPORT_*` статичними бути не можуть, бо саме експортують символ. Друга: `DEFINE_RUNTIME_DEV_PM_OPS` заразом заповнює й гілку [загальносистемного сну](topic:sf-os/suspend-and-resume) готовими `pm_runtime_force_suspend`/`pm_runtime_force_resume` — вони зводять системний перехід до тих самих двох зворотних викликів; `EXPORT_RUNTIME_DEV_PM_OPS` заповнює тільки runtime-гілку. Третя: у полі драйвера структуру підставляють через `pm_ptr(&mydev_pm_ops)` — без `CONFIG_PM` вираз стає `NULL`, і компонувальник викидає всю структуру разом із зворотними викликами.

## Файли в каталозі `power/`

Кожен пристрій у [моделі пристроїв sysfs](topic:sys-unix/sysfs-device-model) — це каталог із файлами-атрибутами; підкаталог `power/` містить оце.

| файл | режим | значення |
|---|---|---|
| `control` | rw | `auto` — рішення за ядром; `on` — тримати активним завжди (це буквально `pm_runtime_forbid()`, тобто нескінченний `+1`). Файла немає, якщо драйвер покликав `pm_runtime_no_callbacks()` |
| `runtime_status` | ro | `active`, `suspended`, перехідні `suspending` і `resuming`, `error` після фатальної помилки, `unsupported` — драйвер runtime PM не підтримує |
| `runtime_active_time` | ro | накопичені мілісекунди в активному стані |
| `runtime_suspended_time` | ro | накопичені мілісекунди у сні |
| `autosuspend_delay_ms` | rw | витримка перед автосном; **від'ємне значення означає «не присипляти ніколи»**. Значення від 1000 округлюють до цілих секунд. Файл є, лише якщо драйвер покликав `pm_runtime_use_autosuspend()` |
| `wakeup` | rw | `enabled` / `disabled` — чи дозволено пристрою будити. Файл є, лише якщо пристрій узагалі на це здатен |
| `wakeup_count`, `wakeup_active_count`, `wakeup_abort_count`, `wakeup_expire_count` | ro | скільки подій пробудження надійшло, скільки оброблено до кінця, скільки могли зірвати перехід системи, скільки згасло за таймаутом |
| `wakeup_active` | ro | `1`, якщо подію пробудження обробляють просто зараз |
| `wakeup_total_time_ms`, `wakeup_max_time_ms`, `wakeup_last_time_ms` | ro | сумарний і найдовший час обробки, а також мить останньої події за монотонним годинником |
| `pm_qos_resume_latency_us` | rw | стеля затримки пробудження; `0` — обмеження немає, `n/a` — жодної затримки не приймають, і присипляння забороняється зовсім |
| `async` | rw | стосується лише загальносистемного сну, до runtime PM відношення не має |

Під `CONFIG_PM_ADVANCED_DEBUG` додаються три файли лише для читання — саме ними ловлять розбалансовані `get`/`put`:

| файл | що показує |
|---|---|
| `runtime_usage` | поточний `usage_count` — скільки заявників зараз тримають пристрій |
| `runtime_active_kids` | `child_count`, або `0`, якщо дітей ігнорують |
| `runtime_enabled` | `enabled`, `disabled` (`disable_depth > 0`), `forbidden` (у `control` стоїть `on`) або `disabled & forbidden` |

## Мінімальний робочий каркас

```c
/* прив'язка: пристрій приходить із disable_depth = 1, тобто механізм вимкнено */
pm_runtime_set_autosuspend_delay(dev, 100);   /* мс */
pm_runtime_use_autosuspend(dev);
pm_runtime_set_active(dev);                   /* прошивка лишила залізо ввімкненим */
pm_runtime_enable(dev);                       /* аж тепер механізм живий */

/* робота */
ret = pm_runtime_resume_and_get(dev);
if (ret < 0)
        return ret;                           /* лічильник уже опущено назад */
... звертання до заліза ...
pm_runtime_put_autosuspend(dev);

/* відв'язка */
pm_runtime_dont_use_autosuspend(dev);
pm_runtime_disable(dev);
pm_runtime_set_suspended(dev);                /* законно саме тому, що механізм уже вимкнено */
```

Порядок у прив'язці не довільний: `pm_runtime_set_active()` мусить стояти **до** `pm_runtime_enable()`, бо оголошувати стан вільно лише поки механізм вимкнено. Пропустити його можна тільки тоді, коли залізо справді приспане, — саме це ядро припускає за замовчуванням.
