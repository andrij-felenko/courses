# 📋 Інтерфейс livepatch: структури, файли, виклики

У живого латання немає ні власного системного виклику, ні утиліти керування: увесь контракт — це три структури, які модуль-латка заповнює, один виклик, яким він себе вмикає, і кілька файлів, через які за ним потім спостерігають. Довідка збирає цей контракт дослівно: підписи, поля, значення й коди помилок.

## Заголовок і умови

```c
#include <linux/livepatch.h>
```

Оголошення живуть у цьому одному заголовку й існують лише тоді, коли ядро зібране з `CONFIG_LIVEPATCH=y`; без нього замість функцій підставляються заглушки. `klp_enable_patch()` експортовано як `EXPORT_SYMBOL_GPL`, тож модуль-латка мусить мати сумісну з GPL ліцензію — інакше він просто не злінкується з ядром.

## Три структури опису

Автор заповнює лише перші поля кожної структури; решту веде ядро й читати їх зсередини латки не треба. Масиви `funcs` і `objs` закінчуються **порожнім елементом** `{ }` — довжини ніде не передають.

```c
struct klp_func {
        const char *old_name;      /* заповнює автор */
        void *new_func;            /* заповнює автор */
        unsigned long old_sympos;  /* заповнює автор, необов'язково */
        /* далі — службові: old_func, kobj, node, stack_node,
           old_size, new_size, nop, patched, transition */
};

struct klp_object {
        const char *name;
        struct klp_func *funcs;
        struct klp_callbacks callbacks;
        /* службові: kobj, func_list, node, mod, dynamic, patched */
};

struct klp_patch {
        struct module *mod;
        struct klp_object *objs;
        struct klp_state *states;
        bool replace;
        /* службові: list, kobj, obj_list, enabled, forced, free_work, finish */
};
```

| Поле `klp_func` | Тип | Значення |
| --- | --- | --- |
| `old_name` | `const char *` | ім'я функції, яку заступають, як воно записане в таблиці символів ядра |
| `new_func` | `void *` | адреса нової функції в модулі-латці |
| `old_sympos` | `unsigned long` | `0` — ім'я вважається унікальним, і якщо це не так, латка не встане; інакше номер потрібного входження цього імені серед символів даного об'єкта |

| Поле `klp_object` | Тип | Значення |
| --- | --- | --- |
| `name` | `const char *` | `NULL` — латаємо саме ядро (`vmlinux`); рядок — ім'я [модуля](root:sys-unix/kernel-modules) |
| `funcs` | `struct klp_func *` | масив функцій цього об'єкта, закінчений `{ }` |
| `callbacks` | `struct klp_callbacks` | зачіпки саме для цього об'єкта |

Об'єкт із іменем модуля, якого зараз немає в пам'яті, не заважає: латка вмикається без нього й чекає. Коли модуль завантажать, ядро долатає його на місці — і саме тоді викличе його зачіпки.

| Поле `klp_patch` | Тип | Значення |
| --- | --- | --- |
| `mod` | `struct module *` | зазвичай `THIS_MODULE` |
| `objs` | `struct klp_object *` | масив об'єктів, закінчений `{ }` |
| `replace` | `bool` | `true` — накопичувальна латка: одним переходом заступає всі раніше застосовані |
| `states` | `struct klp_state *` | необов'язковий опис змін, що їх латка вносить у стан системи |

`struct klp_state` — це трійка `{ unsigned long id; unsigned int version; void *data; }`, а дістають її двома викликами:

```c
struct klp_state *klp_get_state(struct klp_patch *patch, unsigned long id);
struct klp_state *klp_get_prev_state(unsigned long id);
```

Перший знаходить запис у своїй латці, другий — однойменний запис у тій, яку ця латка заступає. Це потрібно, коли нова накопичувальна латка має підхопити ремонт стану, зроблений попередницею, а не робити його вдруге.

## Увімкнення

```c
int klp_enable_patch(struct klp_patch *patch);
```

Кличеться **тільки** з `module_init()`. Парного виклику для вимкнення в інтерфейсі немає — латку вимикають лише через sysfs.

| Повертає | Коли |
| --- | --- |
| `0` | латку прийнято, перехід почався |
| `-EINVAL` | немає `patch`, `mod` чи `objs`; є об'єкт без функцій; модуль не позначений `MODULE_INFO(livepatch, "Y")` |
| `-ENODEV` | ядро livepatch не ініціалізоване, або не вдалося взяти посилання на модуль |
| інший `-ERRNO` | не розв'язався символ, не зареєструвався гачок, або відмовила зачіпка `pre_patch` |

## Зачіпки

```c
struct klp_callbacks {
        int  (*pre_patch)(struct klp_object *obj);
        void (*post_patch)(struct klp_object *obj);
        void (*pre_unpatch)(struct klp_object *obj);
        void (*post_unpatch)(struct klp_object *obj);
        bool post_unpatch_enabled;   /* веде ядро */
};
```

| Зачіпка | Момент виклику | Наслідок |
| --- | --- | --- |
| `pre_patch` | перед тим, як об'єкт починають латати | `0` — далі; `-ERRNO` — латання скасовано, і завантаження модуля (латки або цільового) провалюється |
| `post_patch` | після того, як об'єкт залатано **і перехід завершився на всіх задачах** | — |
| `pre_unpatch` | перед відлатуванням об'єкта | прибирає зроблене в `post_patch` |
| `post_unpatch` | після того, як зворотний перехід завершився | прибирає зроблене в `pre_patch` |

Пари симетричні: `pre_patch` ↔ `post_unpatch` і `post_patch` ↔ `pre_unpatch`. Зачіпку зняття кличуть лише тоді, коли відпрацювала її пара, — саме для цього ядро й веде прапорець `post_unpatch_enabled`.

Оскільки зачіпки належать об'єктові, для `name = NULL` вони спрацьовують на ввімкненні й вимкненні самої латки, а для об'єкта-модуля — ще й на кожному завантаженні та вивантаженні того модуля.

## Дерево `/sys/kernel/livepatch`

```
/sys/kernel/livepatch/
└── <ім'я модуля-латки>/
    ├── enabled            0/1, запис 0 вимикає; запис 1 лише розвертає зворотний перехід
    ├── transition         1, поки триває перехід
    ├── force              запис 1 знімає прапорець очікування з усіх задач
    ├── replace            1, якщо латка накопичувальна
    ├── stack_order        місце в стосі латок; чинна — з найбільшим числом
    └── <vmlinux | ім'я модуля>/
        ├── patched        1, якщо цей об'єкт зараз залатаний
        └── <функція,sympos>/
```

| Файл | З ядра | Права |
| --- | --- | --- |
| `enabled` | 4.0 | читання й запис |
| `transition` | 4.12 | читання |
| `force` | 4.15 | запис |
| `patched` | 6.1 | читання |
| `replace` | 6.11 | читання |
| `stack_order` | 6.14 | читання |

Ім'я теки функції — це ім'я плюс номер входження через кому, той самий `sympos`, тому для унікального символу тека зветься `cmdline_proc_show,0`.

`force` — незворотний. Ядро тримає посилання на модуль-латку весь час, поки та ввімкнена, і віддає його наприкінці зворотного переходу; після `force` воно посилання не віддає взагалі, бо більше не знає, чи хтось усе ще виконує стару версію. Отже, вивантажити такий модуль уже не вийде ніколи.

## `/proc/<pid>/patch_state`

| Значення | Що означає |
| --- | --- |
| `-1` | зараз жодного переходу немає |
| `0` | задача бачить старий набір функцій |
| `1` | задача бачить новий набір функцій |

Поки `transition` показує одиницю, `grep -l 0 /proc/*/patch_state` дає перелік задач, які ще не перемкнулися.

Уся спостережна частина контракту читається кількома рядками — окремої утиліти для цього немає й не потрібно:

```sh
# які латки стоять і в якому вони стані
for p in /sys/kernel/livepatch/*/; do
        printf '%s enabled=%s transition=%s\n' \
                "$(basename "$p")" "$(cat "$p/enabled")" "$(cat "$p/transition")"
done

# що саме залатано у верхній латці
find /sys/kernel/livepatch/<латка> -mindepth 2 -maxdepth 2 -type d

# хто ще не перемкнувся, з іменами
for f in $(grep -l '^0$' /proc/[0-9]*/patch_state); do
        pid=${f%/patch_state}; printf '%s %s\n' "${pid#/proc/}" "$(cat "$pid/comm")"
done
```

## Тіньові змінні

```c
typedef int  (*klp_shadow_ctor_t)(void *obj, void *shadow_data, void *ctor_data);
typedef void (*klp_shadow_dtor_t)(void *obj, void *shadow_data);

void *klp_shadow_alloc(void *obj, unsigned long id, size_t size, gfp_t gfp_flags,
                       klp_shadow_ctor_t ctor, void *ctor_data);
void *klp_shadow_get_or_alloc(void *obj, unsigned long id, size_t size, gfp_t gfp_flags,
                              klp_shadow_ctor_t ctor, void *ctor_data);
void *klp_shadow_get(void *obj, unsigned long id);
void  klp_shadow_free(void *obj, unsigned long id, klp_shadow_dtor_t dtor);
void  klp_shadow_free_all(unsigned long id, klp_shadow_dtor_t dtor);
```

Ключ — пара `<obj, id>`. `obj` — адреса батьківської структури; ядро її не розіменовує й нічого про неї не знає, це просто число, за яким хешують. `id` — число, яким автор латки розрізняє свої власні додаткові поля: одному об'єктові можна причепити скільки завгодно тіньових змінних із різними `id`.

| Виклик | Дає | Якщо пара `<obj, id>` вже є |
| --- | --- | --- |
| `klp_shadow_alloc` | адресу нової області розміру `size` | сварка в журнал і `NULL` |
| `klp_shadow_get_or_alloc` | адресу — наявну або щойно створену | повертає наявну, нічого не виділяє |
| `klp_shadow_get` | адресу наявної області | — (без пари повертає `NULL`) |
| `klp_shadow_free` | — | від'єднує саме цю пару, кличучи `dtor` |
| `klp_shadow_free_all` | — | від'єднує **всі** змінні з цим `id`, хоч який `obj` |

`klp_shadow_free_all()` — те, чим латка прибирає за собою: пройти всіх власників поіменно вона не може, а от викинути всі свої поля за номером — може.

`ctor` кличеться під спінлоком таблиці, тож усередині нього **не можна засинати** — ні чекати на м'ютексі, ні виділяти пам'ять із дозволом на сон. Що таке «не можна засинати» під спінлоком і чому — у [блокуваннях ядра](root:sys-unix/kernel-locking). Сам параметр `gfp_flags` — звичайні прапорці ядерного виділювача: `GFP_KERNEL` там, де спати вільно, `GFP_ATOMIC` у контексті, де ні; про них — у [пам'яті ядра й slab](root:sys-unix/kernel-memory-slab).

## Вимоги до модуля-латки

```c
#include <linux/module.h>
#include <linux/seq_file.h>
#include <linux/livepatch.h>

static int lp_cmdline_proc_show(struct seq_file *m, void *v)
{
        seq_printf(m, "%s\n", "залатано");
        return 0;
}

static void lp_post_patch(struct klp_object *obj) { /* ремонт стану */ }

static struct klp_func funcs[] = {
        { .old_name = "cmdline_proc_show", .new_func = lp_cmdline_proc_show },
        { }
};

static struct klp_object objs[] = {
        { .funcs = funcs, .callbacks = { .post_patch = lp_post_patch } },
        { }
};

static struct klp_patch patch = {
        .mod = THIS_MODULE, .objs = objs, .replace = true,
};

static int __init lp_init(void) { return klp_enable_patch(&patch); }
static void __exit lp_exit(void) { }

module_init(lp_init);
module_exit(lp_exit);
MODULE_LICENSE("GPL");
MODULE_INFO(livepatch, "Y");
```

Обов'язкове тут — три рядки в кінці й `module_exit`, що нічого не робить: усе прибирання ядро вже зробило само, коли доводило латку до вимкненого стану.

Мітку `MODULE_INFO(livepatch, "Y")` шукає завантажувач модулів **до** будь-якого коду латки: без неї він не оброблятиме спеціальних перерозміщень `.klp.rela.<об'єкт>.<секція>` і не резолвитиме символів виду `.klp.sym.<об'єкт>.<символ>,<sympos>`, тож `klp_enable_patch()` відмовить із `-EINVAL`. Побачити мітку ззовні можна звичайним `modinfo`.

Порядок вивантаження — рівно три кроки, і жодного не можна пропустити:

| Крок | Дія | Умова переходу далі |
| --- | --- | --- |
| 1 | `echo 0 > /sys/kernel/livepatch/<латка>/enabled` | почався зворотний перехід |
| 2 | чекати, поки `transition` стане `0` | усі задачі повернулися на старий код |
| 3 | `rmmod <латка>` | ядро віддало посилання на модуль |

Поки латка ввімкнена або поки триває перехід, `rmmod` відмовить: посилання на модуль тримає саме ядро.
