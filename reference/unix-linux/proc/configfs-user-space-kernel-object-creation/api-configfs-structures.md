# 📋 Контракт API: структури, зворотновикликальні методи та прапори configfs

Цей довідник містить точний опис C-структур, сигнатур системних функцій та таблиць методів підсистеми `configfs` у ядрі Linux, необхідних для розробки нових модулів ядра та створення динамічних конфігураційних об'єктів із простору користувача.

## Базові атомні структури: `config_item` та `config_group`

Структура `struct config_item` є фундаментальним абстрактним елементом у `configfs`. Вона відображається у файловій системі як каталог або контейнер атрибутів і зазвичай вбудовується всередину специфічної структури даних драйвера.

```c
struct config_item {
    char                    *ci_name;
    char                    ci_namebuf[CONFIGFS_ITEM_NAME_LEN];
    struct kref             ci_kref;
    struct list_head        ci_entry;
    struct config_item      *ci_parent;
    struct config_group     *ci_group;
    const struct config_item_type *ci_type;
    struct dentry           *ci_dentry;
};
```

Поля структури `config_item`:
- **`ci_name`**: текстове ім'я елемента, яке стає назвою каталогу у файловій системі `/sys/kernel/config/`. Ім'я, коротше за `CONFIGFS_ITEM_NAME_LEN` (20), лягає у вбудований масив `ci_namebuf`; від двадцяти символів `config_item_set_name()` виділяє окремий буфер у купі, і `ci_name` показує вже на нього.
- **`ci_kref`**: атомарний лічильник посилань (`struct kref`). Визначає час життя структури у пам'яті ядра.
- **`ci_entry`**: член двозв'язного списку для включення об'єкта до батьківської групи `cg_children`.
- **`ci_parent`**: вказівник на батьківський `config_item`.
- **`ci_group`**: вказівник на групу `config_group`, якій належить даний елемент.
- **`ci_type`**: вказівник на таблицю типів `config_item_type`, яка описує операції та набір атрибутів.
- **`ci_dentry`**: вказівник на вузол `dentry` у дереві VFS. `configfs` не побудована на шарі `kernfs` (його вживають `sysfs` і `cgroupfs`), а веде власне службове дерево `struct configfs_dirent` поверх звичайних `dentry` та `inode`.

Для маніпуляції лічильником посилань застосовуються такі функції:
- `struct config_item *config_item_get(struct config_item *item)`: збільшує лічильник `ci_kref` на 1 і повертає вказівник на елемент.
- `void config_item_put(struct config_item *item)`: зменшує лічильник `ci_kref`. Якщо лічильник досягає 0, викликається зворотний метод `release()` з відповідного `config_item_type`.
- `void config_item_init_type_name(struct config_item *item, const char *name, const struct config_item_type *type)`: ініціалізує структуру `item`, копіює ім'я `name`, призначає тип `type` та встановлює початкове значення `ci_kref = 1`.

Структура `struct config_group` розширює `config_item` і дає можливість містити дочірні елементи або інші групи:

```c
struct config_group {
    struct config_item              cg_item;
    struct list_head                cg_children;
    struct configfs_subsystem       *cg_subsys;
    struct list_head                default_groups;
    struct list_head                group_entry;
};
```

Поля структури `config_group`:
- **`cg_item`**: вкладений базовий `config_item`. Дозволяє самій групі відображатися як каталог VFS.
- **`cg_children`**: голова двозв'язного списку дочірніх елементів `config_item`.
- **`cg_subsys`**: вказівник на підсистему верхнього рівня, до якої належить група.
- **`default_groups`**: голова списку дочірніх груп, які створюються автоматично разом із батьківською. Додають їх викликом `configfs_add_default_group()`.
- **`group_entry`**: член списку `default_groups` батьківської групи.

Окремого поля з таблицею операцій у групі **немає**: методи фабрики лежать у таблиці типів вкладеного елемента, за вказівником `cg_item.ci_type->ct_group_ops`. Це поширена помилка — шукати у групі поле на кшталт `cg_ops`.

Функції ініціалізації груп:
- `void config_group_init(struct config_group *group)`: ініціалізує вкладений `cg_item` та списки групи.
- `void config_group_init_type_name(struct config_group *group, const char *name, const struct config_item_type *type)`: ініціалізує вкладений `cg_item` та готує групу до прийому дочірніх вузлів.

## Типізація та таблиці операцій: `config_item_type`

Поведінка будь-якого елемента у `configfs` описується структурою `struct config_item_type`:

```c
struct config_item_type {
    struct module                       *ct_owner;
    const struct configfs_item_operations  *ct_item_ops;
    const struct configfs_group_operations *ct_group_ops;
    struct configfs_attribute           **ct_attrs;
    struct configfs_bin_attribute       **ct_bin_attrs;
};
```

Таблиця операцій елемента `struct configfs_item_operations`:

```c
struct configfs_item_operations {
    void (*release)(struct config_item *item);
    int (*allow_link)(struct config_item *src, struct config_item *target);
    void (*drop_link)(struct config_item *src, struct config_item *target);
};
```

Опис методів `ct_item_ops`:
- **`release(item)`**: деструктор. Викликається ядром, коли лічильник посилань `ci_kref` падає до нуля. Формально поле необов'язкове — `config_item_cleanup()` перевіряє його наявність, — але драйвер, який виділяв пам'ять під елемент, зобов'язаний його дати: без `release()` цю пам'ять не поверне вже ніхто. У цьому методі драйвер виконує деініціалізацію та виклики `kfree()` для зовнішніх структур пам'яті. **Прямий виклик `kfree()` поза цим методом суворо заборонений.**
- **`allow_link(src, target)`**: викликається при створенні символічного посилання `ln -s target src/link_name`; береться з таблиці типів **батьківського** елемента `src`, тобто того каталогу, у якому народжується посилання. Перевіряє сумісність об'єктів `src` та `target`. Повернений `0` — дозвіл: далі `configfs` сам бере посилання на службовий вузол цілі й піднімає її лічильник симлінків `s_links`. Якщо `allow_link` у таблиці немає, `symlink()` завершується `-EPERM`.
- **`drop_link(src, target)`**: викликається при видаленні символічного посилання `rm src/link_name`. Драйвер розриває власний зв'язок; лічильники — не його клопіт: `s_links` цілі `configfs` зменшує й своє посилання віддає вже **після** повернення з `drop_link()`. Порядок навмисний — інакше `drop_link(this, target)` міг би відпрацювати після `drop_item(target)`.

Таблиця операцій групи `struct configfs_group_operations`:

```c
struct configfs_group_operations {
    struct config_item *(*make_item)(struct config_group *group, const char *name);
    struct config_group *(*make_group)(struct config_group *group, const char *name);
    void (*disconnect_notify)(struct config_group *group, struct config_item *item);
    void (*drop_item)(struct config_group *group, struct config_item *item);
    bool (*is_visible)(struct config_item *item, struct configfs_attribute *attr, int n);
    bool (*is_bin_visible)(struct config_item *item, struct configfs_bin_attribute *attr, int n);
};
```

Опис методів `ct_group_ops`:
- **`make_item(group, name)`**: викликається при виконанні утилітою у просторі користувача виклику `mkdir name`. Драйвер повинен виділити пам'ять під власну структуру, що містить `config_item`, виконати `config_item_init_type_name()` і повернути вказівник на новий `config_item`. Якщо повертається `ERR_PTR(-errno)`, VFS скасовує створення каталогу.
- **`make_group(group, name)`**: аналог `make_item()`, але використовується, коли створювана дочірня сутність сама є групою `config_group` і може містити подальші підкаталоги.
- **`drop_item(group, item)`**: викликається при виконанні `rmdir name`. Драйвер повинен виключити елемент із внутрішніх робочих списків **і сам віддати посилання**, установлене при створенні, — `config_item_put(item)`. Коментар у `client_drop_item()` формулює це прямо: «якщо `->drop_item()` існує, він відповідає за `config_item_put()`». Метод необов'язковий: коли драйверові нічого прибирати, `drop_item` не оголошують узагалі, і `config_item_put()` викликає `configfs`. Оголосити `drop_item` і не покласти в нього `config_item_put()` — витік пам'яті, який нічим не проявиться, крім того, що `release()` ніколи не спрацює.
- **`disconnect_notify(group, item)`**: необов'язкове сповіщення на шляху `rmdir`. Викликається після того, як `configfs` прибрав елемент із файлової картини, але **до** того, як елемент від'єднано від батьківської групи, і до `drop_item()`. Лічильника посилань не змінює.
- **`is_visible(item, attr, n)`** та **`is_bin_visible(item, bin_attr, n)`**: необов'язкові фільтри видимості. `configfs` питає їх під час створення каталогу для кожного атрибута з `ct_attrs`/`ct_bin_attrs`; повернене `false` означає, що файл атрибута у каталозі не з'явиться. Так одна таблиця типів обслуговує кілька різновидів об'єкта.

## Атрибути та файловий інтерфейс: `configfs_attribute` та `configfs_bin_attribute`

Файли у каталогах `configfs` створюються на основі масиву вказівників `ct_attrs`, який посилається на структури `struct configfs_attribute`:

```c
struct configfs_attribute {
    const char              *ca_name;
    struct module           *ca_owner;
    umode_t                 ca_mode;
    ssize_t (*show)(struct config_item *item, char *page);
    ssize_t (*store)(struct config_item *item, const char *page, size_t count);
};
```

Поля структури `configfs_attribute`:
- **`ca_name`**: ім'я файла атрибута у каталозі VFS (наприклад, `enabled`, `target_iqn`, `size`).
- **`ca_mode`**: стандартні біти доступу POSIX (наприклад, `0644` для читання/запису, `0444` для читання).
- **`show(item, page)`**: викликається при виконанні `cat attribute_file`. Приймає буфер `page` розміром в одну системну сторінку пам'яті (`PAGE_SIZE`, зазвичай 4096 байтів). Форматує рядок і повертає кількість записаних байтів.
- **`store(item, page, count)`**: викликається при записі даних через `echo "val" > attribute_file`. Приймає буфер `page` довжиною `count` байтів. Валідує вхідні дані, оновлює стан драйвера і повертає кількість оброблених байтів або від'ємний код помилки (наприклад, `-EINVAL`).

Для зчитування або передачі великих бінарних даних (наприклад, дампів прошивок або таблиць ключів) використовується структура `struct configfs_bin_attribute`:

```c
struct configfs_bin_attribute {
    struct configfs_attribute   cb_attr;
    void                        *cb_private;
    size_t                      cb_max_size;
    ssize_t (*read)(struct config_item *item, void *buf, size_t count);
    ssize_t (*write)(struct config_item *item, const void *buf, size_t count);
};
```

Отримати вказівник на структуру драйвера можна за допомогою макросу `container_of`:

```c
struct my_custom_device {
    int                     enabled;
    char                    target_name[64];
    struct config_item      item;
};

struct my_custom_device *dev = container_of(item, struct my_custom_device, item);
```

## Реєстрація підсистеми: `configfs_subsystem`

Вершиною ієрархії конфігураційного дерева є структура `struct configfs_subsystem`:

```c
struct configfs_subsystem {
    struct config_group     su_group;
    struct mutex            su_mutex;
};
```

Поля структури `configfs_subsystem`:
- **`su_group`**: коренева група підсистеми, яка реєструється як каталог у `/sys/kernel/config/`.
- **`su_mutex`**: м'ютекс ядра (`struct mutex`), який забезпечує взаємне виключення при одночасних викликах `mkdir` та `rmdir` з кількох потоків простору користувача.

Функції керування підсистемою:
- `int configfs_register_subsystem(struct configfs_subsystem *subsys)`: реєструє підсистему у ядрі. Ім'я кореневого каталогу береться з `su_group.cg_item` (`ci_name`, а якщо він порожній — `ci_namebuf`), тож підсистему заведено оголошувати статично, з `.ci_namebuf = "…"`. Перед викликом група має бути ініціалізована через `config_group_init()`, а м'ютекс — через `mutex_init()`. Повертає `0` у разі успіху або від'ємний код помилки (насамперед `-ENOMEM`; решта — те, що поверне внутрішній `configfs_attach_group()`).
- `void configfs_unregister_subsystem(struct configfs_subsystem *subsys)`: від'єднує кореневу групу підсистеми від дерева `configfs`. Підсистема на цей момент має бути порожньою — інакше ядро друкує `Tried to unregister non-empty subsystem!`. Саме тому модуль не має шансу зникнути «під» живими об'єктами: доки в підсистемі є елементи, знімати її нема як.

Таблиця стандартних кодів помилок `configfs`:

| Код помилки | Значення POSIX | Причина повернення підсистемою |
| :--- | :--- | :--- |
| `-ENOMEM` | Out of Memory | Неможливо виділити пам'ять під `config_item` у `kzalloc()`. |
| `-EEXIST` | File Exists | Каталог із таким ім'ям вже існує; помилку віддає шар VFS ще до того, як `configfs` дістане `mkdir`. |
| `-EINVAL` | Invalid Argument | Передано некоректне значення атрибута у метод `store()`; також `configfs_mkdir()`, коли не вдався `try_module_get()` на власника типу. |
| `-ENOTEMPTY` | Directory Not Empty | Спроба виконати `rmdir` для групи, яка містить вкладені елементи або власні символічні посилання. |
| `-EBUSY` | Device or Resource Busy | Спроба `rmdir` для об'єкта, на який вказує чуже символічне посилання (ненульовий `s_links`). |
| `-EPERM` | Operation Not Permitted | `mkdir` у каталозі, чия таблиця типів не пропонує ні `make_item()`, ні `make_group()` («це не група-фабрика»); так само `symlink` там, де немає `allow_link()`. |
