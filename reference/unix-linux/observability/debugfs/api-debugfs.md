# 📋 Інтерфейси та функції kernel API для debugfs

Цей довідник містить повну специфікацію C API ядра Linux для створення, керування та безпечного вилучення файлів і каталогів у debugfs, включаючи виклики для базових типів, масивів, регістрів, послідовних файлів seq_file та параметрів boot-команд ядра.

## 1. Заголовочні файли, конфігурація та концепція безпечних заглушок

Для використання C API debugfs у модулі чи підсистемі ядра необхідні такі базові заголовочні файли:

```c
#include <linux/debugfs.h>
#include <linux/seq_file.h> /* Якщо використовуються seq_file генератори */
```

Файлова система debugfs керується конфігураційним прапорцем ядра `CONFIG_DEBUG_FS`. Якщо цей параметр вимкнений при збірці ядра (`CONFIG_DEBUG_FS=n`), уся функціональність підсистеми деактивується. Однак, на відміну від багатьох інших підсистем, це не вимагає від розробника огортати кожен виклик `debugfs_create_*` директивами препроцесора `#ifdef CONFIG_DEBUG_FS`.

Заголовочний файл `<linux/debugfs.h>` розроблений таким чином, що при `CONFIG_DEBUG_FS=n` всі макроси та функції компілюються у вбудовані порожні заглушки (`static inline stubs`), які негайно повертають `ERR_PTR(-ENODEV)` або `NULL`. При цьому решта коду драйвера продовжує компілюватися без жодних змін та помилок.

Важливе застереження для розробника: розробник **не повинен** перевіряти повернутий вказівник `struct dentry *` на помилку (наприклад, через `IS_ERR()`) перед передачею його у наступні виклики `debugfs_create_file()`. Всі функції створення у debugfs свідомо розраховані на те, що параметр `parent` може бути вказівником на помилку `ERR_PTR`. Якщо передати `ERR_PTR` як батьківський каталог, функція створення просто тихесенько поверне той самий `ERR_PTR` далі по ланцюжку. Це дозволяє створювати десятки файлів усередині кастомного каталогу без єдиного розгалуження `if (IS_ERR(dir))`.

---

## 2. Створення та рекурсивне вилучення каталогів

Каталоги у debugfs використовуються для групування відлагоджувальних файлів конкретного драйвера, шини чи підсистеми ядра.

### `debugfs_create_dir`

Створює новий каталог усередині дерева debugfs.

```c
struct dentry *debugfs_create_dir(const char *name, struct dentry *parent);
```

Розбір параметрів та механізму виконання:
- `name`: нуль-термінований рядок з іменем нового каталогу (наприклад, `"my_driver"`).
- `parent`: вказівник на батьківський каталог `struct dentry *`. Якщо передано `NULL`, новий каталог буде створений безпосередньо у корені файлової системи debugfs (зазвичай `/sys/kernel/debug/name`).
- **Повертає:** вказівник на створений об'єкт `struct dentry`. У разі виникнення помилки створення або якщо debugfs деактивовано у конфігурації ядра, повертає `ERR_PTR(-errno)`.

Під капотом `debugfs_create_dir` захоплює м'ютекс батьківського каталогу (`inode->i_rwsem`), перевіряє унікальність імені за допомогою VFS-хелпера `lookup_one_len()`, виділяє пам'ять під новий `dentry` та прив'язує до нього `inode` з операціями каталогів `simple_dir_inode_operations`.

### `debugfs_remove` та `debugfs_remove_recursive`

Вилучають файли або цілі ієрархічні дерева каталогів з debugfs.

```c
void debugfs_remove(struct dentry *dentry);
void debugfs_remove_recursive(struct dentry *dentry);
```

Деталізація поведінки та контракту:
- `debugfs_remove`: призначений для вилучення одного конкретного файла або порожнього каталогу. Якщо переданий параметр `dentry` дорівнює `NULL` або є вказівником на помилку `ERR_PTR`, функція безпечно ігнорує виклик і негайно повертає керування (no-op).
- `debugfs_remove_recursive`: рекурсивно вилучає каталог разом з усіма його вкладеними підкаталогами та файлами на будь-яку глибину. 

Практичний контракт використання: розробнику модуля ядра достатньо зберегти у глобальній змінній чи структурі пристрою лише один вказівник на свій головний каталог `struct dentry *my_debug_dir`. При вивантаженні модуля у функційній точці `module_exit` виконується єдиний виклик `debugfs_remove_recursive(my_debug_dir)`. Всі вкладені файли, масиви, регулятори та підкаталоги будуть безпечно очищені з пам'яті VFS без залишку.

---

## 3. Створення універсальних та захищених файлів

Для створення файлів із власною логікою читання та запису використовується функція `debugfs_create_file`.

### `debugfs_create_file`

Універсальний виклик для створення відлагоджувального файла з власною структурою `file_operations`.

```c
struct dentry *debugfs_create_file(const char *name, umode_t mode,
                                   struct dentry *parent, void *data,
                                   const struct file_operations *fops);
```

Параметри та специфікація використання:
- `name`: назва нового файла у каталозі debugfs (наприклад, `"status"` або `"registers"`).
- `mode`: маска прав доступу POSIX (наприклад, `0644` для читання та запису володарем, `0400` лише для читання суперкористувачем). Символічні макроси `S_IRUGO`, `S_IWUSR` також підтримуються.
- `parent`: вказівник на батьківський каталог `struct dentry *`. Якщо `NULL`, файл створюється у корені debugfs.
- `data`: довільний вказівник пам'яті (`void *`), який зберігається у полі `inode->i_private`. У функціях-обробниках `read`/`write` цей вказівник витягується через `file->private_data` або `inode->i_private`, дозволяючи ідентифікувати конкретний екземпляр пристрою.
- `fops`: вказівник на структуру `struct file_operations`, що містить функції-обробники `read`, `write`, `open`, `release`, `llseek`.

### `debugfs_create_file_unsafe`

Незахищена версія створення файла для обходу накладних витрат підсистеми безпечного вилучення.

```c
struct dentry *debugfs_create_file_unsafe(const char *name, umode_t mode,
                                          struct dentry *parent, void *data,
                                          const struct file_operations *fops);
```

Архітектурні особливості та застереження:
За замовчуванням `debugfs_create_file` огортає всі операції файлу внутрішнім механізмом синхронізації SRCU (`debugfs_file_get` / `debugfs_file_put`). Це гарантує, що якщо файл вилучається під час виконання читання, ядро зачекає завершення обробника і не впаде у Use-After-Free.

Однак виклик `debugfs_file_get()` створює додаткові накладні витрати на кожній операції I/O. Якщо розробник створює файл у критичному за швидкодією підсистемному модулі, який **ніколи** не вивантажується під час роботи ядра (наприклад, ядровий плановик чи підсистема керування пам'яттю), він може використати `debugfs_create_file_unsafe()`. Це усуває SRCU-захист і забезпечує максимальну продуктивність системних викликів.

---

## 4. Готові хелпери для примітивних типів та логічних змінних

Щоб розробники не писали повторювальний boilerplate-код для експорту звичайних числових змінних, debugfs пропонує багатий набір готових функцій для примітивних типів.

### Цілі числа в десятковому та шістнадцятковому форматах

```c
void debugfs_create_u8(const char *name, umode_t mode, struct dentry *parent, u8 *value);
void debugfs_create_u16(const char *name, umode_t mode, struct dentry *parent, u16 *value);
void debugfs_create_u32(const char *name, umode_t mode, struct dentry *parent, u32 *value);
void debugfs_create_u64(const char *name, umode_t mode, struct dentry *parent, u64 *value);

void debugfs_create_x8(const char *name, umode_t mode, struct dentry *parent, u8 *value);
void debugfs_create_x16(const char *name, umode_t mode, struct dentry *parent, u16 *value);
void debugfs_create_x32(const char *name, umode_t mode, struct dentry *parent, u32 *value);
void debugfs_create_x64(const char *name, umode_t mode, struct dentry *parent, u64 *value);
```

Семантика роботи:
- Префікс **`u`**: при зчитуванні файла користувач отримує десятковий ASCII-рядок (наприклад, `"42\n"`). При записі (якщо у `mode` дозволено запис) ядро парсить десяткове число з користувацького буфера і перезаписує змішану змінну `value`.
- Префікс **`x`**: при зчитуванні значення форматується як шістнадцятковий рядок з префіксом `0x` (наприклад, `"0x0000002a\n"`).

### Логічні прапорці, розміри та атомарні лічильники

```c
void debugfs_create_bool(const char *name, umode_t mode, struct dentry *parent, bool *value);
void debugfs_create_size_t(const char *name, umode_t mode, struct dentry *parent, size_t *value);
void debugfs_create_atomic_t(const char *name, umode_t mode, struct dentry *parent, atomic_t *value);
```

Деталі форматизації:
- **`debugfs_create_bool`**: при зчитуванні виводить символ `Y\n` (якщо змінна `true`) або `N\n` (якщо `false`). При записі приймає значення `Y`/`N`, `1`/`0`, `y`/`n`, `on`/`off`.
- **`debugfs_create_atomic_t`**: забезпечує безпечну роботу з атомарними змінними `atomic_t`. Зчитування виконується через `atomic_read()`, а запис атомарно оновлює значення через `atomic_set()`.

---

## 5. Масиви, рядки та сирі двійкові блоби

Коли виникає потреба експортувати не одну змінну, а цілу структуру чи бінарний масив даних, використовуються спеціалізовані контейнерні виклики.

### `debugfs_create_u32_array`

Експортує масив 32-бітних unsigned цілих чисел для перегляду з простору користувача.

```c
void debugfs_create_u32_array(const char *name, umode_t mode,
                              struct dentry *parent,
                              u32 *array, u32 elements);
```

- При зчитуванні ядро виводить усі `elements` масиву `array` у вигляді текстової послідовності числових значень, розділених символом нової лінії.

### `debugfs_create_str` та `debugfs_create_blob`

Експорт динамічних текстових рядків та сирих блоків оперативної пам'яті ядра.

```c
void debugfs_create_str(const char *name, umode_t mode,
                        struct dentry *parent, char **str);

struct debugfs_blob_wrapper {
    void *data;
    unsigned long size;
};

void debugfs_create_blob(const char *name, umode_t mode,
                         struct dentry *parent,
                         struct debugfs_blob_wrapper *blob);
```

Механіка роботи:
- **`debugfs_create_str`**: зв'язується з вказівником на рядок `char **str`. Дозволяє не лише читати поточний рядок, але й безпечно перезаписувати його з простору користувача. При записі ядро автоматично виділяє новий буфер пам'яті через `kstrdup()` і звільняє старий.
- **`debugfs_create_blob`**: використовується для зняття бінарних дампів пам'яті. Розробник заповнює структуру `debugfs_blob_wrapper`, вказуючи вказівник на область пам'яті `data` та її розмір у байтах `size`. Зчитування файла повертає сирі двійкові байти (без текстового форматування).

---

## 6. Інтерфейс дампів регістрів MMIO: `debugfs_regset32`

Для спрощення діагностики апаратних контролерів, чиї регістри відображені в адресний простір пам'яті (Memory-Mapped I/O, MMIO), debugfs містить готовий інфраструктурний хелпер.

```c
struct debugfs_reg32 {
    char *name;
    unsigned long offset;
};

struct debugfs_regset32 {
    const struct debugfs_reg32 *regs;
    int nregs;
    void __iomem *base;
    struct device *dev;
};

void debugfs_create_regset32(const char *name, umode_t mode,
                            struct dentry *parent,
                            struct debugfs_regset32 *regset);
```

Опис механізму:
1. Розробник створює масив системних регістрів `struct debugfs_reg32`, вказуючи текстове ім'я кожного регістру та його байтовий зсув (`offset`) відносно базової адреси.
2. Розробник ініціалізує обгортку `struct debugfs_regset32`, вказуючи базову адресу MMIO (`base`), отриману після виклику `ioremap()`, та кількість регістрів `nregs`.
3. При зчитуванні файла `name` через `cat` ядро проходить по всіх записах масиву, безпечно зчитує 32-бітний регістр через системний виклик `ioread32(base + offset)` та виводить списочний дамп у форматі `NAME = 0xVALUE\n`.

---

## 7. Послідовний файл `seq_file` та допоміжні виклики

Для генерації обсяжних текстових дампів, що перевищують 4096 байтів, стандартний `file_operations.read` є незручним. У такому разі використовується зв'язка з двигуном `seq_file`.

```c
/* Створення прочитального seq_file з прив'язкою до системного пристрою */
void debugfs_create_devm_seqfile(struct device *dev, const char *name,
                                 struct dentry *parent,
                                 int (*read_fn)(struct seq_file *s, void *data));
```

Параметри та функціонал:
- `dev`: вказівник на об'єкт пристрою `struct device *`. Використовує менеджер ресурсів `devres` для автоматичного очищення пам'яті.
- `read_fn`: функція зворотного виклику (callback), яка отримує вказівник на `struct seq_file *s`. Усередині цієї функції розробник викликає `seq_printf()`, `seq_puts()` або `seq_putc()`. `seq_file` автоматично обробляє виділення сторінок пам'яті, зсув `ppos` та часткове читання з простору користувача.

---

## 8. Пошук вузлів та параметри командного рядка ядра

### `debugfs_lookup`

Знаходить існуючу `dentry` у дереві debugfs за її іменем та батьківським каталогом.

```c
struct dentry *debugfs_lookup(const char *name, struct dentry *parent);
```

- Використовується для перевірки того, чи був каталог чи файл вже створений іншою частиною драйвера. Повертає `struct dentry *` або `NULL`, якщо об'єкт не знайдено.

### Завантажувальні параметри ядра (`debugfs=`)

Налаштування доступності debugfs передаються ядру при завантаженні через параметр командного рядка boot-завантажника (`grub` чи `systemd-boot`):

| Параметр `debugfs=` | Опис поведінки ядра |
| :--- | :--- |
| `debugfs=on` | Стандартний режим роботи. debugfs дозволено реєструвати та монтувати. |
| `debugfs=off` | Повне вимкнення debugfs. Усі виклики створення повертають помилку, монтування заблоковано. |
| `debugfs=no-mount` | Забороняє монтування debugfs у простір користувача, але зберігає її роботу для `tracefs`. |
