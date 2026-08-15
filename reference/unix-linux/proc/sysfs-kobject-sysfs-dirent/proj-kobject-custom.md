# ⚙️ Практикум: створення власних kobject та атрибутів у ядрі

Модуль на сотню рядків заводить у системі каталог `/sys/kernel/demo_kobj` із двома файлами, які можна читати й записувати звичайним `cat` та `echo`. Дорогою видно все, на чому спотикаються перші драйвери: `kobject_create_and_add()` і його `NULL`, група атрибутів замість поодиноких файлів, `sysfs_emit()` замість `sprintf()`, і порядок вивантаження, де `sysfs_remove_group()` мусить іти перед `kobject_put()`.

## Архітектура навчального модуля

Створюваний модуль реалізує власну підсистему діагностики ядра. При завантаженні модуль динамічно виділяє каталог у файловій системі за шляхом `/sys/kernel/demo_kobj` та створює у ньому два текстові атрибути:
1. `status` — атрибут тільки для читання (режим доступу `0444`), який повертає поточне значення внутрішнього лічильника звернень і автоматично інкрементує його при кожному зчитуванні.
2. `control` — атрибут для читання й запису (режим доступу `0644`, який ставить макрос `__ATTR_RW`), що дає змогу через консоль зчитувати та змінювати текстову позначку конфігураційного стану драйвера.

Усі файли атрибутів об'єднані у структуру `struct attribute_group`. Такий підхід є стандартом безпечного програмування ядерних модулів: масова реєстрація через групу гарантує атомарність відкриття файлів у sysfs та захищає від витоків пам'яті при часткових помилках ініціалізації. Якщо один із файлів групи не вдасться створити, ядро автоматично видалить усі раніше створені файли даної групи, зберігши цілісність деревоподібної структури.

Внутрішня ініціалізація `demo_kobj` спирається на функцію `kobject_create_and_add()`. Ця функція виконує динамічне виділення пам'яті зі SLUB-кешу ядра, встановлює батьківський вказівник на `kernel_kobj` (що відповідає каталогу `/sys/kernel/`) та підв'язує новий вузол `kernfs_node` у загальну деревоподібну ієрархію `sysfs`. У разі неможливості виділити пам'ять функція повертає `NULL`, що потребує негайного виходу з функції ініціалізації з кодом помилки `-ENOMEM`.

## Сирцевий код модуля ядра (`demo_kobj.c`)

Код написано мовою C для простору ядра (kernel space). Згідно з архітектурою ядра Linux, код модулів та драйверів виконується в привілейованому режимі без наявності стандартної бібліотеки C++ (libstdc++), підтримки винятків або механізмів RAII. Тому драйвери та модулі розробляються виключно мовою C із застосуванням специфічних макросів і ядерних API.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kobject.h>
#include <linux/string.h>
#include <linux/sysfs.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix Reference Course");
MODULE_DESCRIPTION("Demo Kernel Module for kobject and sysfs attributes");
MODULE_VERSION("1.0");

static struct kobject *demo_kobj;
static int counter = 42;
static char control_buffer[64] = "default_state";

/* Обробник читання атрибута status */
static ssize_t status_show(struct kobject *kobj, struct kobj_attribute *attr,
                           char *buf)
{
    return sysfs_emit(buf, "%d\n", counter++);
}

/* Обробник читання атрибута control */
static ssize_t control_show(struct kobject *kobj, struct kobj_attribute *attr,
                            char *buf)
{
    return sysfs_emit(buf, "%s\n", control_buffer);
}

/* Обробник запису атрибута control */
static ssize_t control_store(struct kobject *kobj, struct kobj_attribute *attr,
                             const char *buf, size_t count)
{
    if (count >= sizeof(control_buffer))
        return -EINVAL;

    sscanf(buf, "%63s", control_buffer);
    pr_info("demo_kobj: control state updated to '%s'\n", control_buffer);

    return count;
}

/* Оголошення об'єктів атрибутів через макроси */
static struct kobj_attribute status_attr = __ATTR_RO(status);
static struct kobj_attribute control_attr = __ATTR_RW(control);

/* Масив атрибутів для формування групи */
static struct attribute *demo_attrs[] = {
    &status_attr.attr,
    &control_attr.attr,
    NULL, /* Термінатор масиву */
};

static struct attribute_group demo_attr_group = {
    .attrs = demo_attrs,
};

static int __init demo_init(void)
{
    int retval;

    /* Створення kobject під /sys/kernel/ */
    demo_kobj = kobject_create_and_add("demo_kobj", kernel_kobj);
    if (!demo_kobj)
        return -ENOMEM;

    /* Реєстрація групи атрибутів у sysfs */
    retval = sysfs_create_group(demo_kobj, &demo_attr_group);
    if (retval) {
        kobject_put(demo_kobj);
        return retval;
    }

    pr_info("demo_kobj: module loaded, /sys/kernel/demo_kobj created\n");
    return 0;
}

static void __exit demo_exit(void)
{
    /* Спершу видаляємо атрибути, потім зменшуємо kref */
    sysfs_remove_group(demo_kobj, &demo_attr_group);
    kobject_put(demo_kobj);
    pr_info("demo_kobj: module unloaded\n");
}

module_init(demo_init);
module_exit(demo_exit);
```

## Інструкція зі складання та тестування

Для побудови бінарного модуля ядра (`demo_kobj.ko`) використовується система збірки Kbuild ядра Linux через стандартний `Makefile`:

```makefile
obj-m += demo_kobj.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

Послідовне виконання команд складання, інтеграції та тестування у командному інтерфейсі розробника:

```bash
# 1. Збірка модуля у поточному каталозі
make

# 2. Завантаження модуля у ядро
sudo insmod demo_kobj.ko

# 3. Перевірка наявності створеного каталогу та файлів атрибутів у sysfs
ls -la /sys/kernel/demo_kobj/

# 4. Читання атрибута status (кожен новий виклик інкрементує лічильник)
cat /sys/kernel/demo_kobj/status
# Вивід: 42
cat /sys/kernel/demo_kobj/status
# Вивід: 43

# 5. Перевірка читання та запису нового стану в control
cat /sys/kernel/demo_kobj/control
# Вивід: default_state

echo "active_mode" | sudo tee /sys/kernel/demo_kobj/control
cat /sys/kernel/demo_kobj/control
# Вивід: active_mode

# 6. Перевірка ядерних повідомлень через dmesg
dmesg | tail -n 5

# 7. Вивантаження модуля та перевірка видалення каталогу з sysfs
sudo rmmod demo_kobj
```

## Простеження виконання системних викликів

Для аналізу взаємодії простору користувача з ядром при зчитуванні атрибута можна використати утиліту `strace`:

```bash
strace cat /sys/kernel/demo_kobj/status
```

Результат трасування показує стандартний ланцюжок системних викликів VFS:
- `openat(AT_FDCWD, "/sys/kernel/demo_kobj/status", O_RDONLY)` — VFS шукає файл у dcache або створює тимчасовий `dentry` над `kernfs_node`.
- `read(3, "42\n", ...)` — ядро передає виклик операції `kernfs_fop_read_iter()`, яка бере буфер розміром щонайбільше `PAGE_SIZE`, викликає `status_show()`, копіює результат у буфер простору користувача та звільняє буфер. Розмір буфера, який просить `cat`, залежить від версії coreutils, тож у трасуванні там буде або 4096, або більше число — на поведінку sysfs це не впливає.
- `close(3)` — VFS закриває файловий дескриптор. Активне посилання на вузол `kernfs_node` було взяте й віддане ще всередині самого `read()`, тож `close()` тут нічого не звільняє з боку `kobject`: у сучасних ядрах відкритий дескриптор не тримає об'єкт пристрою (це робилося лише до Linux 2.6.22).

## Обробка помилок та крайні випадки при розробці

Під час роботи з атрибутами sysfs розробники драйверів можуть зіштовхнутися з кількома крайніми ситуаціями:

- **Помилки виділення пам'яті**: Якщо під час реєстрації групи атрибутів `sysfs_create_group()` виникає дефіцит оперативної пам'яті, функція повертає код `-ENOMEM`. У цьому випадку драйвер повинен скасувати попередні етапи ініціалізації та обов'язково зменшити лічильник посилань через `kobject_put()`.
- **Спроба повторного створення**: Спроба зареєструвати об'єкт із ім'ям, яке вже існує в даному каталозі sysfs, повертає помилку `-EEXIST`. Ядро захищає дерево sysfs від дублювання імен на рівні вузлів `kernfs_node`.

## Критичні пастки реалізації та системні деталі

При практичній реалізації обробників атрибутів sysfs необхідно дотримуватися кількох суворих інженерних вимог ядра:

1. **Застосування `sysfs_emit` замість `sprintf`**: Починаючи з ядра Linux 5.10, класичні функції `sprintf` та `snprintf` вважаються застарілими для використання в атрибутах sysfs. Нова функція `sysfs_emit(buf, ...)` захищає ядро від виходу за межі виділеного буфера `PAGE_SIZE` (4096 байтів) і повертає точну кількість байтів, необхідну для VFS. Спроба виходу за межі `PAGE_SIZE` у старій функції `sprintf` призводила до пошкодження пам'яті ядра.
2. **Обов'язковий символ `\n`**: Вивід будь-якого текстового атрибута при зчитуванні має закінчуватися символом нового рядка `\n`. Відсутність `\n` ламає конвеєри утиліт командного рядка (`grep`, `sed`, `awk`) та спричиняє некоректне відображення у терміналах.
3. **Строгий порядок очищення у `demo_exit`**: При вивантаженні модуля спочатку викликається `sysfs_remove_group`, що видаляє файли та вузли `kernfs_node` з ієрархії sysfs, і лише після цього здійснюється виклик `kobject_put`. Порушення цієї послідовності призводить до спроби доступу до вже знищеного об'єкта `kobject` під час звернення користувача до файла в `/sys`.
4. **Контекст виконання обробників**: Функції `show` та `store` викликаються в контексті процесів простору користувача, які здійснюють системні виклики `read()` або `write()`. Це означає, що у цих функціях дозволено використовувати блокувальні операції (наприклад, `mutex_lock`), проте неприпустимо затримувати виконання надовго — читач у терміналі просто зависне на `cat`.
5. **Багатопотокова синхронізація**: Якщо обробники `show` та `store` модифікують спільні структури даних ядра, доступ до них має захищатися мутексом (`mutex_lock(&demo_mutex)`), щоб запобігти гонкам при одночасному читанні та записі з різних процесів.
