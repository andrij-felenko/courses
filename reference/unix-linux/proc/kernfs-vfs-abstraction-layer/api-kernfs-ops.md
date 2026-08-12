# 📋 Контракт API: структури, методи та функції kernfs

Довідник системного контракту підсистеми `kernfs` описує ключові структури даних, функції створення й вилучення вузлів, механізми активного підрахунку посилань, інваріанти синхронізації та таблицю операцій `kernfs_ops`, необхідні розробникам модулів ядра для побудови власних віртуальних файлових систем або інтеграції атрибутів підсистем.

---

## 1. Головні структури даних

### `struct kernfs_node`
Фундаментальний вузол дерева `kernfs`. Представляє каталог, звичайний файл або символічне посилання в пам'яті ядра.

```c
struct kernfs_node {
    atomic_t            count;
    atomic_t            active;
    struct kernfs_node  *parent;
    const char          *name;
    struct rb_node      rb;
    const void          *ns;
    unsigned int        hash;
    union {
        struct kernfs_elem_dir  dir;
        struct kernfs_elem_file file;
        struct kernfs_elem_symlink symlink;
    } u;
    void                *priv;
    unsigned short      flags;
    umode_t             mode;
    struct kernfs_iattr *iattr;
};
```

#### Поля структури та їхній системний контракт:
- **`count`**: Атомарний лічильник посилань (`atomic_t`) для керування життєвим циклом пам'яті самої структури `kernfs_node`. Пам'ять виділяється зі спеціалізованого кешу SLAB `kernfs_node_cache` і звільняється лише тоді, коли `count` досягає `0`.
- **`active`**: Атомарний лічильник активних файлових операцій (`atomic_t`). Використовується для гарантії безпеки при вилученні вузла (гаряче відключення). Верхній біт прапора `KERNFS_DRAIN_PTR` сигналізує про процес деактивації та блокує виклики нових операцій.
- **`parent`**: Вказівник на батьківський `kernfs_node` (для кореневого вузла дорівнює `NULL`). Зв'язки `parent` утворюють точне дерево ієрархії каталогів.
- **`name`**: Рядок із ім'ям вузла у файловій системі (ASCIIZ). Виділяється динамічно або посилається на константну назву атрибута.
- **`rb`**: Вузли червоно-чорного дерева (`struct rb_node`) для швидкого пошуку сиблінгів за іменем у батьківському каталозі (`O(log N)`).
- **`ns`**: Вказівник на тег простору імен (наприклад, `struct net *` для мережевих просторів імен netns). Дозволяє прозоро ізолювати віртуальні файли у контейнерах.
- **`priv`**: Довільний вказівник на дані підсистеми (наприклад, `struct kobject *` для sysfs або `struct cgroup *` для cgroup v2).
- **`flags`**: Бітові прапори стану вузла (`KERNFS_HAS_SEQ_SHOW`, `KERNFS_HAS_MMAP`, `KERNFS_LOCKDEP` тощо).
- **`mode`**: Права доступу файлової системи (`S_IRUGO`, `S_IWUSR` тощо).
- **`iattr`**: Вказівник на структуру `struct kernfs_iattr`. Виділяється динамічно лише у разі виклику `chmod`, `chown` або оновлення часу доступу.

---

### `struct kernfs_iattr`
Структура метаданих файлової системи, яка виділяється на вимогу (ліниве виділення):

```c
struct kernfs_iattr {
    struct iattr        ia_iattr;
    void                *ia_secdata;
    u32                 ia_secdata_len;
    struct simple_xattrs xattrs;
};
```

Поки процес користувача не змінює права чи власника файла за допомогою викликів `chmod()` або `chown()`, `kn->iattr` залишається `NULL`. Це заощаджує 48 байтів пам'яті для кожного з сотень тисяч вузлів у системі.

---

### `struct kernfs_ops`
Таблиця зворотних викликів (англ. *callbacks*), які реалізує драйвер чи підсистема для обробки читання, запису та керування файлами.

```c
struct kernfs_ops {
    int (*seq_show)(struct seq_file *sf, void *v);
    ssize_t (*read)(struct kernfs_open_file *of, char *buf,
                    size_t count, loff_t off);
    ssize_t (*write)(struct kernfs_open_file *of, char *buf,
                     size_t count, loff_t off);
    int (*mmap)(struct kernfs_open_file *of, struct vm_area_struct *vma);
    __poll_t (*poll)(struct kernfs_open_file *of,
                     struct poll_table_struct *pt);
    void (*open)(struct kernfs_open_file *of);
    void (*release)(struct kernfs_open_file *of);
};
```

#### Сигнатури та контракт методів:
- **`seq_show(sf, v)`**: Найпоширеніший метод для відформатованого виводу текстових даних. Використовує підсистему `seq_file`. Дозволяє безпечно записувати дані через `seq_printf(sf, fmt, ...)` без ризику переповнення буфера. Якщо визначено `seq_show`, ядро автоматично встановлює прапор `KERNFS_HAS_SEQ_SHOW`.
- **`read(of, buf, count, off)`**: Низькорівневе зчитування сирих бінарних або текстових даних. Приймає виділений буфер `buf` розміром `count`. Повертає кількість зчитаних байтів або від'ємний код помилки (`-EIO`, `-EINVAL`).
- **`write(of, buf, count, off)`**: Запис даних з простору користувача. Буфер `buf` гарантовано завершується нульовим символом `\0`, а його розмір становить `count`. Виклик виконується під захистом мутекса `of->mutex`.
- **`mmap(of, vma)`**: Пряме відображення внутрішньої пам meті пристрою у простір адресації процесу користувача.
- **`poll(of, pt)`**: Підтримка асинхронного сповіщення процесів через `select()`, `poll()` або `epoll()`. Повертає маску подій (`EPOLLIN`, `EPOLLPRI` тощо).
- **`open(of)` / `release(of)`**: Контекстні виклики при відкритті та закритті файлового дескриптора. Дозволяють драйверу виділяти та звільняти ресурси у полях `of->priv`.

---

### `struct kernfs_open_file`
Контекстний об'єкт, який створюється при відкритті файла `kernfs` і передається в усі методи `kernfs_ops`.

```c
struct kernfs_open_file {
    struct kernfs_node  *kn;
    struct file         *file;
    void                *priv;
    struct mutex        mutex;
    struct mutex        vm_ops_mutex;
    size_t              atomic_write_len;
    bool                mmapped;
};
```

#### Поля контексту:
- **`kn`**: Вказівник на відповідний `kernfs_node`.
- **`file`**: Вказівник на об'єкт файлу VFS (`struct file *`).
- **`priv`**: Приватні дані конкретного відкритого файла (можна призначати у виклику `open`).
- **`mutex`**: Мутекс для синхронізації паралельних операцій читання/запису над цим дескриптором.

---

### `struct kernfs_syscall_ops`
Таблиця обробників системних викликів для віртуальних файлових систем, які дозволяють користувачам створювати каталоги чи перейменовувати файли (наприклад, cgroups v2):

```c
struct kernfs_syscall_ops {
    int (*remount_fs)(struct kernfs_root *root, int *flags, char *data);
    int (*show_options)(struct seq_file *sf, struct kernfs_root *root);
    int (*mkdir)(struct kernfs_node *parent, const char *name, umode_t mode);
    int (*rmdir)(struct kernfs_node *kn);
    int (*rename)(struct kernfs_node *kn, struct kernfs_node *new_parent,
                  const char *new_name);
    int (*show_path)(struct seq_file *sf, struct kernfs_node *kn,
                     struct kernfs_root *root);
};
```

---

## 2. Функції керування життєвим циклом вузлів

### `kernfs_create_root()`
Створює нове коріння дерева `kernfs` для власної віртуальної файлової системи.

```c
struct kernfs_root *kernfs_create_root(
    struct kernfs_syscall_ops *scops,
    unsigned int flags,
    void *priv
);
```
- **`scops`**: Таблиця системних викликів для обробки `mkdir`/`rmdir`/`rename` (може бути `NULL`).
- **`flags`**: Прапорці поведінки (наприклад, `KERNFS_ROOT_HAVESB`, `KERNFS_ROOT_EXTRA_OPEN_PERM`).
- **`priv`**: Приватний вказівник володаря файлової системи.
- **Повертає**: Вказівник на `struct kernfs_root` або `ERR_PTR(-errno)`.

---

### `kernfs_destroy_root()`
Знищує корінь `kernfs` та рекурсивно вилучає всі вкладені вузли з пам meті з гарантією деактивації через `kernfs_drain()`.

```c
void kernfs_destroy_root(struct kernfs_root *root);
```

---

### `kernfs_create_dir_ns()`
Створює новий каталог у дереві `kernfs`.

```c
struct kernfs_node *kernfs_create_dir_ns(
    struct kernfs_node *parent,
    const char *name,
    umode_t mode,
    void *priv,
    const void *ns
);
```
- **`parent`**: Батьківський вузол-каталог.
- **`name`**: Назва нового каталогу.
- **`mode`**: Права доступу (наприклад, `0755`).
- **`priv`**: Вказівник на об'єкт підсистеми.
- **`ns`**: Тег простору імен (`NULL`, якщо простори імен не використовуються).
- **Повертає**: Вказівник на новий `kernfs_node` або `ERR_PTR(-errno)`.

Макрос-спрощення без просторів імен:
```c
#define kernfs_create_dir(parent, name, mode, priv) \
    kernfs_create_dir_ns((parent), (name), (mode), (priv), NULL)
```

---

### `kernfs_create_file_ns()`
Створює звичайний файл атрибута в дереві `kernfs`.

```c
struct kernfs_node *kernfs_create_file_ns(
    struct kernfs_node *parent,
    const char *name,
    umode_t mode,
    loff_t size,
    const struct kernfs_ops *ops,
    void *priv,
    const void *ns
);
```
- **`size`**: Очікуваний розмір файла в байтах (зазвичай `0` для віртуальних файлів).
- **`ops`**: Вказівник на реалізовану таблицю операцій `struct kernfs_ops`.

---

### `kernfs_create_link()`
Створює символічне посилання в дереві `kernfs`, яке посилається на інший `kernfs_node`.

```c
struct kernfs_node *kernfs_create_link(
    struct kernfs_node *parent,
    const char *name,
    struct kernfs_node *target
);
```
- **`parent`**: Каталог, у якому створюється посилання.
- **`name`**: Ім'я символічного посилання.
- **`target`**: Вказівник на цільовий вузол `kernfs_node`.
- **Повертає**: Вказівник на створений вузол символічного посилання або `ERR_PTR(-errno)`.

---

### `kernfs_remove()` та `kernfs_remove_by_name()`
Вилучає вузол або ціле піддерево з каталогу з автоматичним викликом `kernfs_drain()`.

```c
void kernfs_remove(struct kernfs_node *kn);
int kernfs_remove_by_name_ns(struct kernfs_node *parent,
                             const char *name,
                             const void *ns);
```
- **Синхронізація**: Функція атомарно деактивує вузол, видаляє його з червоно-чорного дерева батька та БЛОКУЄТЬСЯ доти, доки всі активні операції `read`/`write` над цим вузлом не завершаться.

---

## 3. Навігація та пошук у дереві

### `kernfs_find_and_get_ns()`
Шукає дочірній вузол у каталозі за ім'ям та тегом простору імен і атомарно збільшує лічильник посилань `kn->count`.

```c
struct kernfs_node *kernfs_find_and_get_ns(
    struct kernfs_node *parent,
    const char *name,
    const void *ns
);
```
- **Повертає**: Знайдений `kernfs_node *` із вже збільшеним `count` або `NULL`, якщо вузол відсутній.
- **Обов meязок виклику**: Отриманий вузол після завершення роботи має бути звільнений парним викликом `kernfs_put(kn)`.

---

### `kernfs_walk_and_get()`
Виконує покроковий обхід шляху в дереві `kernfs` від заданого вузла.

```c
struct kernfs_node *kernfs_walk_and_get(
    struct kernfs_node *parent,
    const char *path
);
```
- **`path`**: Відносний шлях у дереві `kernfs` (наприклад, `"control/status"`).

---

## 4. Активний підрахунок посилань та захист від гонитовних умов

```c
bool kernfs_get_active(struct kernfs_node *kn);
void kernfs_put_active(struct kernfs_node *kn);
void kernfs_drain(struct kernfs_node *kn);
```

### Правила використання:
1. `kernfs_get_active(kn)` перевіряє, чи не перебуває вузол у стані вилучення. Якщо вузол активний, атомарний лічильник `kn->active` збільшується на 1, і функція повертає `true`. Якщо вузол деактивовано (`kernfs_remove`), повертає `false`.
2. Кожен успішний виклик `kernfs_get_active()` **ЗБОВ'ЯЗАНИЙ** супроводжуватися викликом `kernfs_put_active()` у парній гілці коду (наприклад, у блоці `finally` чи після завершення VFS-операції).
3. `kernfs_drain(kn)` переводить вузол у стан знеструмлення і чекає на ваіт-черзі (`waitqueue`), доки значення `active` не впаде до нульового рівня.

---

## 5. Блокування та покрокова інваріантність

При роботі з `kernfs` ядро дотримується строгової ієрархії семафорів та мутексів:

| Замок (Lock) | Опис та обсяг захисту |
| :--- | :--- |
| **`kernfs_rwsem`** | Глобальний read/write семафор ядра, який захищає структуру дерев `kernfs_root` та додавання/вилучення вузлів з `rb_node`. |
| **`kernfs_open_file_mutex`** | Захищає глобальний список відкритих файлів `kernfs_open_file`. |
| **`of->mutex`** | Внутрішній мутекс конкретного відкритого файла. Послідовно блокує паралельні виклики `write()` від різних потоків одного процесу. |

### Інваріанти покликів:
- **Заборона спинлоків у `kernfs_ops`**: Методи `seq_show`, `read` та `write` виконуються у контексті процесу з можливістю сну (`might_sleep()`). Заборонено утримувати спинлоки (`spinlock_t`) при викликах методів `kernfs`, які можуть приводити до виділення пам'яті чи сну.
- **Гарантія нульового термінатора**: Буфер `buf`, який передається у метод `write`, завжди містить нуль-термінатор `\0` за індексом `count`, що упереджує виходи за межі масиву при використанні `sscanf()` чи `kstrtoint()`.
- **Контракт повернення кодів помилок**:
  - `-ENODEV`: Пристрій або вузол деактивовано (повертається автоматично при `kernfs_get_active() == false`).
  - `-ENOENT`: Запитаний вузол відсутній у червоно-чорному дереві.
  - `-EEXIST`: Спроба створити вузол із вже наявним ім meм у тому самому каталозі.
  - `-EINVAL`: Некоректні параметри або невалідний формат числа при записі.
