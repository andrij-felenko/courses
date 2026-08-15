# 📋 API обробників sysctl та реєстрація ctl_table в ядрі Linux

Параметри ядра, що експортуються через віртуальну файлову систему `/proc/sys`, реєструються підсистемами та модулями ядра за допомогою структури `struct ctl_table`. Ця структура пов'язує ім'я файлу в піддереві `/proc/sys`, відповідну змінну в пам'яті ядра та обробник (*handler*), який виконується під час читання чи запису файлу з простору користувача.

У цьому довіднику наведено внутрішній контракт обробників sysctl у коді ядра Linux, опис стандартних helper-функцій ядра, механізми захисту пам'яті та порядок реєстрації таблиць параметрів.

## Основні структури даних ядра

Головним будівельним блоком підсистеми sysctl є структура `ctl_table`, визначена у заголовковому файлі ядра `<linux/sysctl.h>`:

```c
struct ctl_table {
    const char *procname;         /* Ім'я файлу або каталогу в /proc/sys */
    void *data;                   /* Указник на змінну в пам'яті ядра */
    int maxlen;                   /* Максимальний розмір даних у байтах */
    umode_t mode;                 /* Права доступу VFS (наприклад, 0644 або 0444) */
    proc_handler *proc_handler;   /* Обробник читання/запису */
    struct ctl_table_poll *poll;  /* Опціональна підтримка poll/epoll */
    void *extra1;                 /* Додатковий параметр (наприклад, мінімальне значення) */
    void *extra2;                 /* Додатковий параметр (наприклад, максимальне значення) */
};
```

Детальний аналіз полів структури `ctl_table`:

- `procname`: Рядкове ім'я файла у віртуальній файловій системі. Якщо обробник відсутній, але присутнє піддерево, це ім'я стає назвою каталогу.
- `data`: Прямий вказівник на глобальну або статичну змінну ядра у секції даних (`.data` або `.bss`).
- `maxlen`: Обмеження обсягу пам'яті у байтах. Для цілих чисел `int` дорівнює `sizeof(int)`, для масивів — `N * sizeof(int)`, для рядків — розмір текстового буфера.
- `mode`: Права доступу у форматі маски VFS. Типові значення: `0644` (читання для всіх, запис для root), `0444` (лише читання для всіх), `0600` (читання й запис лише для root).
- `proc_handler`: Указник на функцію ядра, яка викликається при читанні або записі файлу.
- `extra1` та `extra2`: Допоміжні вказівники для передачі нижньої та верхньої меж діапазону у перевірочних обробниках `proc_dointvec_minmax`.

Для управління групою параметрів та їх реєстрації у дереві VFS ядро використовує обгортку `ctl_table_header`, яка повертається під час реєстрації:

```c
struct ctl_table_header *register_sysctl(const char *path, struct ctl_table *table);
void unregister_sysctl_table(struct ctl_table_header *header);
```

Аргумент `path` задає відносний шлях у дереві `/proc/sys` (наприклад, `"net/ipv4"` або `"kernel"`).

## Сигнатура обробника proc_handler

Кожен файл у `/proc/sys` має свій обробник читання та запису. Прототип функції `proc_handler` визначено у ядрі наступним чином:

```c
typedef int proc_handler(struct ctl_table *table, int write,
                         void *buffer, size_t *lenp, loff_t *ppos);
```

Параметри обробника:
- `table` — указник на елемент `struct ctl_table`, до якого звертається користувач.
- `write` — прапорець напрямку операції: `0` для читання (`read`), `1` для запису (`write`).
- `buffer` — указник на буфер із даними. Від Linux 5.8 (набір патчів Крістофа Гельвіга «pass kernel pointers to ->proc_handler») це вже **ядерна** пам'ять: спільний код `proc_sys_call_handler()` сам копіює дані користувача й завершує рядок нулем, тому анотація `__user` із сигнатури зникла, а обробникам більше не потрібні `copy_from_user()`/`copy_to_user()`.
- `lenp` — указник на розмір буфера (вхідний параметр — запитаний розмір користувача, вихідний — фактично оброблена кількість байтів).
- `ppos` — поточний зсув позиції у файлі (*file position offset*).

Повертане значення: `0` у разі успішного виконання або від'ємний код помилки POSIX (наприклад, `-EINVAL`, `-EPERM`, `-EFAULT`, `-EOVERFLOW`).

## Стандартні системні обробники ядра

Ядро Linux надає набір готових реалізацій `proc_handler` для найпоширеніших типів даних. Вони самі розбирають текстовий вхід користувача, перевіряють типи, конвертують символи та оновлюють змінні ядра.

| Обробник | Опис та застосування | Приклад параметрів `ctl_table` |
| :--- | :--- | :--- |
| `proc_dointvec` | Читання/запис одного або кількох цілих чисел (`int`). | `data = &my_int`, `maxlen = sizeof(int)` |
| `proc_dostring` | Читання/запис текстового рядка символів (`char*`). | `data = my_str`, `maxlen = sizeof(my_str)` |
| `proc_dointvec_minmax` | Читання/запис `int` із перевіркою нижньої та верхньої меж. | `extra1 = &min_val`, `extra2 = &max_val` |
| `proc_doulongvec_minmax` | Читання/запис `unsigned long` з перевіркою меж. | `extra1 = &min_ulong`, `extra2 = &max_ulong` |
| `proc_dointvec_jiffies` | Конвертація часу між jiffies ядра та секундами. | Використовується для системних таймерів. |
| `proc_dointvec_userhz_jiffies` | Конвертація часу між jiffies ядра та одиницями USER_HZ. | Для інтервалів, які простір користувача задає в тиках USER_HZ. |
| `proc_dointvec_ms_jiffies` | Конвертація часу між jiffies ядра та мілісекундами. | Зручний інтерфейс таймерів у мілісекундах. |

### Поведінка обробника proc_dointvec_minmax

Обробник `proc_dointvec_minmax` є найбезпечнішим способом експортувати цілочисельний параметр, оскільки він не пропускає у пам'ять ядра значень поза дозволеним діапазоном.

Приклад визначення меж у коді ядра:

```c
static int val_min = 0;
static int val_max = 100;

static struct ctl_table example_table[] = {
    {
        .procname     = "percent_limit",
        .data         = &my_percentage,
        .maxlen       = sizeof(int),
        .mode         = 0644,
        .proc_handler = proc_dointvec_minmax,
        .extra1       = &val_min,
        .extra2       = &val_max,
    },
    { }
};
```

Якщо користувач намагається записати значення `-5` або `150`, функція `proc_dointvec_minmax` повертає помилку `-EINVAL`, і змінна `my_percentage` залишається незмінною.

## Повний приклад реєстрації таблиці sysctl у модулі ядра

Нижче наведено робочий приклад модуля ядра Linux, який реєструє власне піддерево у `/proc/sys/kernel/custom_tuning`.

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sysctl.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Course");
MODULE_DESCRIPTION("Приклад реєстрації параметрів sysctl");

static int custom_debug_level = 0;
static int min_debug = 0;
static int max_debug = 5;

static char custom_node_name[64] = "linux-node-01";

static struct ctl_table custom_sysctl_table[] = {
    {
        .procname     = "debug_level",
        .data         = &custom_debug_level,
        .maxlen       = sizeof(int),
        .mode         = 0644,
        .proc_handler = proc_dointvec_minmax,
        .extra1       = &min_debug,
        .extra2       = &max_debug,
    },
    {
        .procname     = "node_name",
        .data         = custom_node_name,
        .maxlen       = sizeof(custom_node_name),
        .mode         = 0644,
        .proc_handler = proc_dostring,
    },
    { } /* Порожній термінальний елемент масиву */
};

static struct ctl_table_header *custom_header;

static int __init custom_sysctl_init(void)
{
    /* Реєструємо параметри за шляхом /proc/sys/kernel/custom_tuning */
    custom_header = register_sysctl("kernel/custom_tuning", custom_sysctl_table);
    if (!custom_header) {
        pr_err("sysctl_demo: не вдалося зареєструвати таблицю sysctl\n");
        return -ENOMEM;
    }
    pr_info("sysctl_demo: параметри у /proc/sys/kernel/custom_tuning успішно створено\n");
    return 0;
}

static void __exit custom_sysctl_exit(void)
{
    if (custom_header) {
        unregister_sysctl_table(custom_header);
        pr_info("sysctl_demo: таблицю sysctl видалено\n");
    }
}

module_init(custom_sysctl_init);
module_exit(custom_sysctl_exit);
```

## Написання власного обробника з побічними ефектами (*Side-Effects*)

Коли зміна параметра вимагає не лише перезапису змінної в пам'яті, а й миттєвого застосування рішень (наприклад, переналаштування апаратного таймера, перебудови таблиць маршрутизації або очищення кешу), розробник пише власний `proc_handler`.

Типовий шаблон власного обробника з побічними ефектами:

1. Викликати стандартний обробник (наприклад, `proc_dointvec`) для зчитування чи запису значення.
2. Перевірити, що це операція запису (`write != 0`) і що стандартний обробник не повернув помилку (`ret == 0`).
3. Виконати додаткову валідацію або запустити побічний ефект у коді ядра.

```c
static int custom_cache_trigger = 0;

static int custom_trigger_handler(struct ctl_table *table, int write,
                                  void *buffer, size_t *lenp, loff_t *ppos)
{
    int old_val = custom_cache_trigger;
    int ret;

    /* 1. Делегуємо базову обробку цілого числа стандартній функції */
    ret = proc_dointvec(table, write, buffer, lenp, ppos);
    if (ret || !write)
        return ret;

    /* 2. Виконуємо реакцію на зміну значення */
    if (custom_cache_trigger != old_val) {
        pr_info("sysctl_demo: значення змінилося з %d на %d\n", old_val, custom_cache_trigger);
        
        if (custom_cache_trigger == 1) {
            pr_info("sysctl_demo: тригер активовано, виконуємо скидання внутрішнього кешу...\n");
            /* Код очищення ресурсів ядра */
            custom_cache_trigger = 0; /* Автоматично скидаємо прапорець */
        }
    }

    return 0;
}
```

## Внутрішній механізм захисту пам'яті та синхронізації

Під час реєстрації таблиць `ctl_table` ядро Linux будує внутрішню ієрархію вузлів `ctl_node`. Для захисту від гонки даних (*data races*) під час одночасного читання та запису з кількох процесів використовуються наступні механізми:

- **Глобальний спінлок `sysctl_lock`:** Пошук вузла в дереві (`lookup_entry()` → `find_entry()`), реєстрація нових таблиць і зміна лічильників виконуються під одним спінлоком, оголошеним у `fs/proc/proc_sysctl.c`. Саме він, а не RCU, серіалізує доступ до дерева каталогів.
- **Підрахунок використання (поле `used` у `ctl_table_header`):** Кожне відкриття файлу в `/proc/sys` тримає посилання на відповідний заголовок (`use_table()` / `unuse_table()`). Виклик `unregister_sysctl_table()` спершу позначає таблицю такою, що знімається з реєстру, і чекає, поки лічильник спорожніє, — лише тоді структура зникає з дерева.
- **Відкладене звільнення через RCU (*Read-Copy-Update*):** Сама пам'ять заголовка звільняється не миттєво, а через `kfree_rcu(head, rcu)` — після завершення поточного грейс-періоду. Так паралельний читач, що вже отримав указник, гарантовано не наткнеться на звільнену пам'ять.

## Ізоляція sysctl у мережевих просторах імен (Network NS)

Для параметрів, які повинні мати окремі значення у кожному контейнері (мережевому просторі імен), ядро надає спеціалізовані функції реєстрації:

```c
struct ctl_table_header *register_net_sysctl(struct net *net,
                                            const char *path,
                                            struct ctl_table *table);
void unregister_net_sysctl_table(struct ctl_table_header *header);
```

У цьому випадку таблиця `ctl_table` реєструється лише для конкретного екземпляра `struct net`. При знищенні мережевого простору імен (наприклад, зупинці контейнера) відповідні файли в `/proc/sys/net/` автоматично вилучаються з VFS без впливу на хостову систему.
