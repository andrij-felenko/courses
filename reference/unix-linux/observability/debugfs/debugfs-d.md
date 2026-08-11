# debugfs: службове вікно в нутрощі ядра

<preknowlist>
- [Концепції ядра Linux](book:unix-linux/kernel-and-userspace) — базові поняття системних викликів та VFS.
</preknowlist>

У світі Linux-ядра існує декілька віртуальних файлових систем, кожна з яких має своє чітке призначення. `/proc` (procfs) використовується для відображення інформації про процеси та деяких загальних параметрів системи. `/sys` (sysfs) надає структурований погляд на дерево пристроїв (device model) та дозволяє керувати обладнанням. Обидві ці файлові системи мають дуже суворі правила: їхні інтерфейси (ABI) є стабільними, і зміна формату виводу у файлах всередині `/proc` чи `/sys` може зламати користувацький простір (userspace), що категорично заборонено головним правилом Лінуса Торвальдса: "Never break userspace".

Але що робити розробнику ядра, якщо йому потрібно вивести багато відлагоджувальної інформації, яка може часто змінювати свій формат, бути нестабільною, специфічною для конкретного драйвера і абсолютно не потрібною звичайним користувачам? Для цього і була створена **debugfs**.

## Що таке debugfs?

**debugfs** — це віртуальна файлова система (ram-based), яка зазвичай монтується у `/sys/kernel/debug`. Вона була створена Грегом Кроа-Хартманом (Greg Kroah-Hartman) як просте і нерегульоване місце для розміщення відлагоджувальної інформації.

Головне правило debugfs полягає в тому, що **правил немає**.

### Відмінності від procfs та sysfs

1. **Відсутність стабільності ABI (No ABI stability).** Формат файлів у debugfs може змінюватися від версії до версії ядра без будь-яких попереджень. Користувацькі скрипти чи програми не повинні покладатися на стабільність файлів у `/sys/kernel/debug`. Це дозволяє розробникам ядра вільно додавати, змінювати або видаляти інформацію за потреби.
2. **Простота API.** Створення файлу в sysfs або procfs вимагає значних зусиль (особливо в sysfs, де потрібно правильно вбудувати об'єкт у kobject ієрархію). У debugfs виклик зводиться до одного-двох рядків C-коду.
3. **Лише для root.** За замовчуванням доступ до `/sys/kernel/debug` має лише користувач `root`. Це гарантує, що небезпечна або надмірно деталізована інформація не потрапить до непривілейованих процесів.

![Порівняння procfs, sysfs та debugfs](/reference/unix-linux/observability/debugfs/img/fig-debugfs-comparison.svg)

*Рис. 1. debugfs порівняно з procfs та sysfs.*

## Використання debugfs у ядрі (C API)

Щоб використовувати debugfs у своєму модулі ядра, необхідно включити заголовочний файл `<linux/debugfs.h>`.

### Створення директорії

Зазвичай драйвери чи підсистеми створюють власну директорію в корені debugfs. Для цього використовується функція:

```c
struct dentry *debugfs_create_dir(const char *name, struct dentry *parent);
```

- `name` — ім'я нової директорії.
- `parent` — вказівник на батьківську директорію. Якщо передати `NULL`, директорія буде створена в корені `/sys/kernel/debug`.

Функція повертає вказівник на `struct dentry` (об'єкт директорії), який потім можна використовувати як батьківський для файлів.

### Створення файлів

Для створення файлів використовується функція `debugfs_create_file`:

```c
struct dentry *debugfs_create_file(const char *name, umode_t mode,
                                   struct dentry *parent, void *data,
                                   const struct file_operations *fops);
```

- `name` — ім'я файлу.
- `mode` — права доступу (наприклад, `0644` або символічно `S_IRUGO | S_IWUSR`).
- `parent` — вказівник на директорію, де створюється файл.
- `data` — вказівник на приватні дані, які будуть передані у функції з `fops`.
- `fops` — вказівник на `struct file_operations`, який визначає функції для читання/запису.

У багатьох випадках писати повний `struct file_operations` занадто довго. Тому ядро надає допоміжні функції для простих типів даних. Наприклад, щоб створити файл для читання або запису цілого числа (`u32`), можна використати:

```c
void debugfs_create_u32(const char *name, umode_t mode,
                        struct dentry *parent, u32 *value);
```

Коли користувач читає цей файл, він отримає значення змінної `value`. Коли записує — змінить її. Існують також функції `debugfs_create_u8`, `debugfs_create_u16`, `debugfs_create_u64`, `debugfs_create_bool` та інші.

### Видалення

Важливо не забувати прибирати за собою при вивантаженні модуля. Оскільки всі файли та директорії в debugfs представлені як `dentry`, їх можна видалити функцією:

```c
void debugfs_remove(struct dentry *dentry);
```

Але ще простіше видалити відразу цілу директорію зі всіма її дочірніми файлами за допомогою:

```c
void debugfs_remove_recursive(struct dentry *dentry);
```

Це дозволяє модулю просто зберегти вказівник на свою головну директорію, і при вивантаженні (`module_exit`) викликати `debugfs_remove_recursive()`.

## Приклад: Простий модуль ядра з debugfs

Розглянемо невеликий приклад модуля ядра, який експортує змінну та власний файл у debugfs.

```c
#include <linux/module.h>
#include <linux/debugfs.h>
#include <linux/uaccess.h>

static struct dentry *my_debugfs_root;
static u32 my_var = 42;

static ssize_t my_read(struct file *file, char __user *user_buf,
                       size_t count, loff_t *ppos)
{
    char buf[64];
    int len;

    len = snprintf(buf, sizeof(buf), "Hello from debugfs! Var is %u\n", my_var);
    return simple_read_from_buffer(user_buf, count, ppos, buf, len);
}

static const struct file_operations my_fops = {
    .read = my_read,
    .open = simple_open,
    .llseek = default_llseek,
};

static int __init my_module_init(void)
{
    /* Створюємо директорію /sys/kernel/debug/my_module */
    my_debugfs_root = debugfs_create_dir("my_module", NULL);
    if (!my_debugfs_root) {
        pr_err("Failed to create debugfs directory\n");
        return -ENOMEM;
    }

    /* Створюємо файл, що використовує нашу структуру file_operations */
    debugfs_create_file("hello", 0444, my_debugfs_root, NULL, &my_fops);

    /* Створюємо файл для керування змінною типу u32 */
    debugfs_create_u32("my_var", 0644, my_debugfs_root, &my_var);

    pr_info("my_module loaded\n");
    return 0;
}

static void __exit my_module_exit(void)
{
    /* Видаляємо директорію та всі її файли */
    debugfs_remove_recursive(my_debugfs_root);
    pr_info("my_module unloaded\n");
}

module_init(my_module_init);
module_exit(my_module_exit);
MODULE_LICENSE("GPL");
```

Після завантаження цього модуля в директорії `/sys/kernel/debug/my_module/` з'являться два файли:
- `hello` (лише для читання)
- `my_var` (для читання та запису)

Користувач (root) зможе взаємодіяти з ними через звичайні утиліти `cat` та `echo`.

## Висновок

`debugfs` є потужним інструментом в арсеналі розробника ядра Linux. Її простота та відсутність жорстких правил дозволяють дуже швидко виводити потрібну діагностичну інформацію з надр ядра до простору користувача. Головне пам'ятати, що ця гнучкість приходить ціною відсутності стабільності (ABI), тому розробляти користувацькі програми, що залежать від файлів у `debugfs`, вкрай не рекомендується.
