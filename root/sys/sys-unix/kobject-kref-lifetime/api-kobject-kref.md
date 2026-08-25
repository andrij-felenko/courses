# 📋 Довідник API: структури та функції kobject, kref і kset

Підсистема об'єктної моделі ядра Linux надає строго типізовані інтерфейси для побудови ієрархій об'єктів, інтеграції з віртуальною файловою системою `sysfs` та гарантованого керування життєвим циклом динамічної пам'яті через атомарний підрахунок посилань.

## Базові структури даних

### `struct kref` (`<linux/kref.h>`)

Легковагова обгортка над захищеним лічильником посилань ядра (`refcount_t`), яка забезпечує атомарний трекінг часу життя структури без накладних витрат на додаткові поля чи файлову систему.

```c
struct kref {
    refcount_t refcount;
};
```

| Поле | Тип | Призначення |
| :--- | :--- | :--- |
| `refcount` | `refcount_t` | Атомарний лічильник посилань із захистом від переповнення та операцій над нульовим значенням. Займає 4 байти в оперативній пам'яті. |

Внутрішня реалізація `refcount_t` захищає систему від двох класичних векторів атак та багів багатопотоковості:
1. **Насичення (Saturation)**: при спробі інкрементувати лічильник понад `REFCOUNT_MAX` (значення `0xc0000000`) він переходить у стан `REFCOUNT_SATURATED` і блокує будь-які подальші зміни, запобігаючи переповненню та переходу у від'ємні числа.
2. **Захист від воскресіння**: якщо лічильник уже досяг `0`, виклик `kref_get()` блокується інструкцією `refcount_inc_not_zero()`, генеруючи трасування стека в системний журнал `dmesg`.

---

### `struct kobject` (`<linux/kobject.h>`)

Центральний атом об'єктної моделі ядра. Призначений для вбудовування у структури вищого рівня (`struct device`, `struct module`, `struct cdev` тощо) для надання їм імені, батьківського зв'язку, лічильника посилань та каталогу в sysfs.

```c
struct kobject {
    const char          *name;
    struct list_head    entry;
    struct kobject      *parent;
    struct kset         *kset;
    const struct kobj_type *ktype;
    struct kernfs_node  *sd;
    struct kref         kref;
    unsigned int state_initialized:1;
    unsigned int state_in_sysfs:1;
    unsigned int state_add_uevent_sent:1;
    unsigned int state_remove_uevent_sent:1;
    unsigned int uevent_suppress:1;
};
```

| Поле | Тип | Опис та інваріанти |
| :--- | :--- | :--- |
| `name` | `const char *` | Рядкове ім'я об'єкта, що визначає назву його каталогу в sysfs. Виділяється динамічно або посилається на константний рядок. |
| `entry` | `struct list_head` | Елемент двозв'язного списку для включення об'єкта до батьківського контейнера `kset`. |
| `parent` | `struct kobject *` | Вказівник на батьківський об'єкт в ієрархії (визначає батьківський каталог у sysfs). При реєстрації ядро автоматично інкрементує лічильник батька. |
| `kset` | `struct kset *` | Вказівник на множину (підсистему), до якої належить об'єкт. Може замінювати поле `ktype`, якщо власне `ktype` не вказано. |
| `ktype` | `const struct kobj_type *` | Вказівник на таблицю операцій, деструктор `release` та атрибути за замовчуванням. |
| `sd` | `struct kernfs_node *` | Вказівник на вузол віртуальної файлової системи `kernfs`/`sysfs`. Керує активними посиланнями VFS. |
| `kref` | `struct kref` | Вбудований лічильник посилань життєвого циклу пам'яті контейнера. |
| `state_initialized` | `unsigned int : 1` | Бітовий прапорець успішного проходження первинної ініціалізації (`kobject_init`). |
| `state_in_sysfs` | `unsigned int : 1` | Прапорець наявності активного зареєстрованого каталогу у файловій системі sysfs. |
| `state_add_uevent_sent` | `unsigned int : 1` | Прапорець успішного відправлення події додавання `KOBJ_ADD` підсистемі `udev`. |
| `state_remove_uevent_sent` | `unsigned int : 1` | Прапорець відправлення події видалення `KOBJ_REMOVE`. Запобігає дублюванню сигналів. |
| `uevent_suppress` | `unsigned int : 1` | Дозволяє тимчасово замаскувати генерацію подій під час масового створення об'єктів. |

---

### `struct kobj_type` (`<linux/kobject.h>`)

Визначає спільну поведінку, правила відображення у sysfs та деструктор для групи споріднених об'єктів `kobject`.

```c
struct kobj_type {
    void (*release)(struct kobject *kobj);
    const struct sysfs_ops *sysfs_ops;
    const struct attribute_group **default_groups;
    const struct kobj_ns_type_operations *(*child_ns_type)(const struct kobject *kobj);
    const void *(*namespace)(const struct kobject *kobj);
    void (*get_ownership)(const struct kobject *kobj, kuid_t *uid, kgid_t *gid);
};
```

| Метод / Поле | Сигнатура / Тип | Опис |
| :--- | :--- | :--- |
| `release` | `void (*)(struct kobject *kobj)` | **Обов'язковий деструктор.** Викликається ядром, коли `kref` досягає нуля. Звільняє пам'ять батьківського контейнера через `container_of()`. |
| `sysfs_ops` | `const struct sysfs_ops *` | Таблиця методів читання (`show`) та запису (`store`) атрибутів у sysfs. |
| `default_groups` | `const struct attribute_group **` | Масив груп атрибутів, які автоматично створюються при додаванні об'єкта до sysfs. |
| `namespace` | `const void *(*)(...)` | Повертає вказівник на простір імен мережі чи пристроїв для ізольованих контейнерів. |
| `get_ownership` | `void (*)(...)` | Дозволяє призначити нестандартні права володіння (UID/GID) для файлів у sysfs всередині user namespaces. |

---

### `struct sysfs_ops` (`<linux/sysfs.h>`)

Таблиця перехоплення операцій VFS над файлами атрибутів у sysfs.

```c
struct sysfs_ops {
    ssize_t (*show)(struct kobject *kobj, struct attribute *attr, char *buf);
    ssize_t (*store)(struct kobject *kobj, struct attribute *attr, const char *buf, size_t count);
};
```

| Метод | Контекст виконання | Призначення та обмеження |
| :--- | :--- | :--- |
| `show` | Процесний (може блокуватися) | Форматує стан атрибута у буфер розміром до `PAGE_SIZE` (4096 байтів). Повертає кількість записаних байтів. Заборонено писати більше за одну сторінку. |
| `store` | Процесний (може блокуватися) | Зчитує дані користувача з буфера `buf` довжиною `count`, оновлює стан драйвера. Повертає кількість оброблених байтів або від'ємний код помилки (`-EINVAL`, `-EIO`). |

---

### `struct attribute` та `struct bin_attribute` (`<linux/sysfs.h>`)

Дескриптори файлів-атрибутів, які драйвер експортує у каталог об'єкта в sysfs.

```c
struct attribute {
    const char *name;
    umode_t mode;
};

struct bin_attribute {
    struct attribute attr;
    size_t size;
    void *private;
    struct address_space *(*f_mapping)(void);
    ssize_t (*read)(struct file *, struct kobject *, struct bin_attribute *, char *, loff_t, size_t);
    ssize_t (*write)(struct file *, struct kobject *, struct bin_attribute *, char *, loff_t, size_t);
    int (*mmap)(struct file *, struct kobject *, struct bin_attribute *attr, struct vm_area_struct *vma);
};
```

- `struct attribute`: базовий текстовий атрибут. Поле `mode` визначає права доступу у восьмеричному форматі POSIX (наприклад, `0644` для читання всіма і запису власником, `0444` для тільки-читання).
- `struct bin_attribute`: двійковий атрибут для передачі неструктурованих потоків даних (дампи EEPROM, прошивки мікроконтролерів, доступ до регістрів PCI MMIO). Підтримує операції довільного позиціонування (`loff_t`) та пряме відображення пам'яті (`mmap`).

---

### `struct kset` (`<linux/kobject.h>`)

Колекція об'єктів `kobject`, що утворює самостійну підсистему та слугує центром маршрутизації подій гарячого підключення (uevents).

```c
struct kset {
    struct list_head list;
    spinlock_t list_lock;
    struct kobject kobj;
    const struct kset_uevent_ops *uevent_ops;
};
```

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| `list` | `struct list_head` | Голова двозв'язного списку всіх дочірніх об'єктів `kobject`, включених до цієї множини. |
| `list_lock` | `spinlock_t` | Спінлок захисту списку `list` від паралельних змін у багатоядерному середовищі. |
| `kobj` | `struct kobject` | Власний вбудований `kobject`, завдяки якому `kset` відображається у sysfs як каталог. |
| `uevent_ops` | `const struct kset_uevent_ops *` | Таблиця фільтрації подій та генерації змінних середовища для демона `udevd`. |

---

## Інтерфейс підрахунку посилань `kref`

Всі функції модуля `<linux/kref.h>` працюють з атомарними апаратними гарантіями та встановлюють суворі бар'єри пам'яті (англ. *memory barriers*) для процесорів із позачерговим виконанням інструкцій (англ. *out-of-order execution*).

```c
#include <linux/kref.h>
```

### `kref_init`

```c
void kref_init(struct kref *kref);
```
- **Призначення:** Ініціалізує лічильник посилань значенням `1`.
- **Контекст:** Будь-який (зазвичай під час виділення пам'яті структури через `kmalloc`/`kzalloc`).
- **Правило безпеки:** Викликається рівно один раз перед тим, як вказівник на структуру буде опубліковано для доступу іншим потокам або підсистемам.

### `kref_get`

```c
void kref_get(struct kref *kref);
```
- **Призначення:** Атомарно збільшує лічильник посилань на одиницю.
- **Контекст:** Будь-який (атомарний або процесний).
- **Попередження безпеки:** Функцію дозволено викликати лише тоді, коли поточний потік уже утримує гарантовано валідне посилання. Якщо лічильник дорівнює нулю, виклик свідчить про наявність стану гонитви та спробу повторного використання мертвої структури. Ядро виводить аварійне попередження `refcount_t: addition on 0; use-after-free` і блокує подальші зміни лічильника.

### `kref_put`

```c
int kref_put(struct kref *kref, void (*release)(struct kref *kref));
```
- **Призначення:** Атомарно зменшує лічильник посилань на одиницю із застосуванням бар'єра пам'яті звільнення (англ. *release barrier*). Якщо лічильник досягає нуля, виконує бар'єр отримання (англ. *acquire barrier*) та викликає передану функцію-деструктор `release`.
- **Значення, що повертається:** `1`, якщо було викликано функцію `release`; `0` — якщо об'єкт все ще утримується іншими активними посиланнями.
- **Контекст:** Будь-який, проте якщо функція `release` виконує операції, що можуть засинати (`mutex_lock`, `msleep`, `kfree` великих буферів), `kref_put` має викликатися виключно у процесному контексті.

### `kref_put_lock`

```c
int kref_put_lock(struct kref *kref, void (*release)(struct kref *kref), spinlock_t *lock);
```
- **Призначення:** Забезпечує безпечне видалення структури з глобального списку або хеш-таблиці. Якщо поточний лічильник дорівнює `1`, функція спочатку захоплює наданий спінлок `lock`, після чого атомарно зменшує лічильник до нуля і викликає деструктор `release` під захистом цього блокування.
- **Мета застосування:** Повне усунення вікна гонитви між зменшенням лічильника до нуля на одному CPU та паралельним пошуком об'єкта у списку на іншому CPU.

### `kref_read`

```c
unsigned int kref_read(const struct kref *kref);
```
- **Призначення:** Повертає поточне числове значення лічильника посилань.
- **Застереження:** Використовується виключно для діагностичного виводу в `pr_debug()` або перевірок `WARN_ON()`. Заборонено використовувати результат `kref_read()` для ухвалення логічних рішень про життєвий цикл об'єкта, оскільки на багатоядерній системі значення лічильника може змінитися іншим ядром одразу після повернення з функції.

---

## Інтерфейс об'єктної моделі `kobject`

```c
#include <linux/kobject.h>
```

### `kobject_init`

```c
void kobject_init(struct kobject *kobj, const struct kobj_type *ktype);
```
- **Призначення:** Обнуляє внутрішні поля структури `kobject`, призначає дескриптор поведінки `ktype`, ініціалізує лічильник `kref` значенням `1` та встановлює прапорець `state_initialized = 1`.
- **Вимоги:** Пам'ять об'єкта перед викликом має бути попередньо виділена та очищена нулями.

### `kobject_add`

```c
int __must_check kobject_add(struct kobject *kobj, struct kobject *parent, const char *fmt, ...);
```
- **Призначення:** Формує ім'я об'єкта за шаблоном `fmt`, встановлює зв'язок з батьківським об'єктом `parent` (автоматично захоплюючи на ньому `kobject_get()`) і створює каталог у sysfs разом з усіма групами атрибутів за замовчуванням.
- **Повертає:** `0` у разі успішної реєстрації; від'ємний код помилки (`-ENOMEM`, `-EEXIST`) у разі збою виділення пам'яті або виявлення дублювання імені в одному каталозі.
- **Критичне правило:** Якщо `kobject_add()` завершився з помилкою, розробник зобов'язаний викликати `kobject_put(kobj)`, щоб коректно звільнити виділені внутрішні ресурси через деструктор `release`. Прямий виклик `kfree()` у цій точці заборонено.

### `kobject_init_and_add`

```c
int __must_check kobject_init_and_add(struct kobject *kobj, const struct kobj_type *ktype,
                                      struct kobject *parent, const char *fmt, ...);
```
- **Призначення:** Об'єднує послідовне виконання `kobject_init()` та `kobject_add()` в один виклик. Найпоширеніший спосіб ініціалізації вбудованих об'єктів ядра.

### `kobject_create_and_add`

```c
struct kobject *kobject_create_and_add(const char *name, struct kobject *parent);
```
- **Призначення:** Виділяє пам'ять під автономний `kobject` зі стандартним типом `dynamic_kobj_ktype` (який викликає `kfree(kobj)` у своєму методі `release`) та створює каталог у sysfs.
- **Сфера застосування:** Швидке створення простих ізольованих каталогів у `/sys/kernel/` без необхідності опису власної складної структури пристрою.

### `kobject_get`

```c
struct kobject *kobject_get(struct kobject *kobj);
```
- **Призначення:** Атомарно збільшує лічильник посилань `kref` на одиницю і повертає той самий вказівник `kobj`. Якщо передано `NULL`, функція безпечно повертає `NULL`.

### `kobject_put`

```c
void kobject_put(struct kobject *kobj);
```
- **Призначення:** Атомарно зменшує лічильник `kref`. Якщо лічильник досягає нуля, функція викликає деструктор `kobj->ktype->release(kobj)`.
- **Правило архітектури:** Це єдиний дозволений у ядрі спосіб ініціювати завершення життєвого циклу структури, що містить `kobject`.

### `kobject_del`

```c
void kobject_del(struct kobject *kobj);
```
- **Призначення:** Видаляє каталог об'єкта та всі його атрибути з файлової системи sysfs, від'єднує його від батьківського об'єкта (`kobject_put(kobj->parent)`) та вилучає зі списку `kset`.
- **Важливе розмежування:** `kobject_del()` **НЕ звільняє оперативну пам'ять структури**. Вона лише прибирає інтерфейси взаємодії з VFS. Після виклику `kobject_del()` драйвер обов'язково повинен викликати `kobject_put()`, щоб скинути власне посилання та запустити деструктор `release`.

---

## Інтерфейс множин `kset`

```c
#include <linux/kobject.h>
```

| Функція | Сигнатура | Опис та правила блокування |
| :--- | :--- | :--- |
| `kset_create_and_add` | `struct kset *kset_create_and_add(const char *name, const struct kset_uevent_ops *u, struct kobject *parent_kobj)` | Динамічно виділяє пам'ять під множину `kset`, ініціалізує її вбудований `kobject`, призначає таблицю подій `uevent_ops` та створює каталог у sysfs. |
| `kset_register` | `int kset_register(struct kset *k)` | Реєструє попередньо налаштований екземпляр `struct kset` у системі. |
| `kset_unregister` | `void kset_unregister(struct kset *k)` | Видаляє каталог множини з sysfs та викликає фінальний `kobject_put(&k->kobj)`. |
| `kset_find_obj` | `struct kobject *kset_find_obj(struct kset *kset, const char *name)` | Шукає об'єкт з ім'ям `name` у списку множини `kset`, атомарно захоплює на ньому `kobject_get()` під захистом внутрішнього спінлока `kset->list_lock` і повертає вказівник на знайдений екземпляр. |

---

## Допоміжний макрос навігації по пам'яті `container_of`

### `container_of` (`<linux/container_of.h>`)

```c
#define container_of(ptr, type, member) ({                      \
    void *__mptr = (void *)(ptr);                               \
    static_assert(__same_type(*(ptr), ((type *)0)->member) ||   \
                  __same_type(*(ptr), void),                    \
                  "pointer type mismatch in container_of()");   \
    ((type *)(__mptr - offsetof(type, member))); })
```
- **Призначення:** За адресою внутрішнього поля `member` обчислює базову адресу зовнішнього контейнера типу `type`.
- **Механізм перевірки:** Макрос містить вбудоване компіляторне твердження `static_assert`, яке блокує збирання модуля у випадку передачі несумісного типу вказівника, захищаючи ядро від помилок адресації на етапі компіляції.
