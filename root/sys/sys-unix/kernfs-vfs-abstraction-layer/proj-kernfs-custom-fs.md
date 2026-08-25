# ⚙️ Практичний проєкт: модуль ядра з власною файловою системою на kernfs

Практичний проєкт демонструє розробку повноцінної віртуальної файлової системи у просторі ядра Linux за допомогою шару абстракції `kernfs`. У рамках цього проєкту ми побудуємо автономний драйвер ядра, який реєструє власну файлову систему, створює динамічне дерево каталогів та файлів атрибутів у пам'яті, обробляє операції читання й запису з гарантією атомарності та забезпечує безпечне розвантаження модуля — без «сирітських» об'єктів і без гонитви, що дає Use-After-Free.

## Архітектурна ціль та мета проєкту

Традиційний підхід до розробки віртуальних файлових систем ядра вимагає від системного інженера глибокого ручного інтегрування з VFS: реалізації методів `file_system_type->mount`, `super_operations` (`alloc_inode`, `destroy_inode`, `statfs`), `inode_operations` (`lookup`, `mkdir`, `rmdir`) та `file_operations` (`read`, `write`, `iterate_shared`). Це рутинний код (англ. *boilerplate code*), який не має жодного стосунку до самих атрибутів: він лише годує кеш `dcache` та вручну розводить блокування.

Шар `kernfs` знімає з драйвера рівно цю рутину. Нижче її не буде взагалі: жодного `super_operations`, жодного `inode_operations`, жодного власного лічильника «нас саме зараз читають». Драйвер делегує `kernfs` усю роботу з керування деревом вузлів, обходу каталогів та синхронізації, лишаючи собі саму лише логіку обробки атрибутів — у нашому випадку це три короткі зворотні виклики.

Ми створимо віртуальну файлову систему з назвою `demo_kernfs`, яку можна змонтувати у довільну точку файлової системи (наприклад, `/mnt/demo_fs`).

Ієрархічне дерево об'єктів у пам'яті матиме такий вигляд:
```
/mnt/demo_fs/
├── info       (0444, текстовий файл з інформацією про стан модуля)
└── control/   (каталог керування підсистемою)
    └── status (0644, читання/запис лічильника або стану)
```

Двошарова архітектура проєкту:
1. **Код ядра (C)**: Драйвер-модуль, який ініціалізує `kernfs_root`, створює вузли `kernfs_node`, визначає таблицю операцій `kernfs_ops` та реєструє `file_system_type`.
2. **Утиліта користувача (C / C++)**: Програма простору користувача для тестування читання та атомарного запису атрибутів.

---

## 1. Повна реалізація модуля ядра Linux (C)

Створіть файл `demo_kernfs_module.c`. Модуль зібраний під ядра **3.14 – 5.0** — верхню межу ставить монтування. У 5.1 `kernfs` перевели на `fs_context`, і `kernfs_mount()` разом із `kernfs_mount_ns()` просто зникли з заголовка: від 5.1 замість `.mount = demo_mount` у `file_system_type` треба ставити `.init_fs_context`, класти в `struct kernfs_fs_context` поля `root` і `magic` та кликати `kernfs_get_tree(fc)`. Створення вузлів переносити не доведеться: пара `uid`/`gid`, що з'явилася у 4.19, лягла на `kernfs_create_dir_ns()` / `kernfs_create_file_ns()`, а вбудовані обгортки без `_ns`, які ми й кличемо, підставляють `GLOBAL_ROOT_UID` / `GLOBAL_ROOT_GID` самі. Решта коду — вузли, `kernfs_ops`, `kernfs_destroy_root()` — лишається без змін.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/kernfs.h>
#include <linux/seq_file.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/utsname.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Architecture Course");
MODULE_DESCRIPTION("Autonomous kernfs-based pseudo filesystem demo");
MODULE_VERSION("1.0");

#define DEMO_FS_MAGIC 0x5053464B /* байти "KFSP" у порядку little-endian */

static struct kernfs_root *demo_root;
static struct kernfs_node *control_dir;
static struct kernfs_node *info_node;
static struct kernfs_node *status_node;

/* Атомарний лічильник для демонстрації безпечної роботи з даними */
static atomic_t global_counter = ATOMIC_INIT(100);

/* --- Метод 1: seq_show для файла /info --- */
static int demo_info_show(struct seq_file *sf, void *v)
{
    seq_printf(sf, "=== Demo Kernfs Subsystem ===\n");
    seq_printf(sf, "Status: ACTIVE\n");
    seq_printf(sf, "Global Counter Value: %d\n", atomic_read(&global_counter));
    seq_printf(sf, "Kernel Release: %s\n", init_utsname()->release);
    seq_printf(sf, "Architecture Footprint: kernfs_node size = %zu B\n",
               sizeof(struct kernfs_node));
    return 0;
}

static struct kernfs_ops info_ops = {
    .seq_show = demo_info_show,
};

/* --- Метод 2: read/write для файла /control/status --- */
static int demo_status_show(struct seq_file *sf, void *v)
{
    seq_printf(sf, "%d\n", atomic_read(&global_counter));
    return 0;
}

static ssize_t demo_status_write(struct kernfs_open_file *of,
                                 char *buf, size_t count, loff_t off)
{
    int val, err;

    /* Шар kernfs гарантує, що buf завершується нуль-термінатором '\0' */
    err = kstrtoint(strstrip(buf), 10, &val);
    if (err) {
        pr_warn("demo_kernfs: Invalid integer format: %s\n", buf);
        return err;
    }

    if (val < 0 || val > 1000000) {
        pr_warn("demo_kernfs: Counter value out of range (0..1000000): %d\n", val);
        return -EINVAL;
    }

    atomic_set(&global_counter, val);
    pr_info("demo_kernfs: global_counter successfully updated to %d\n", val);

    return count;
}

static struct kernfs_ops status_ops = {
    .seq_show = demo_status_show,
    .write    = demo_status_write,
};

/* --- Монтування та ініціалізація суперблоку VFS --- */
static struct dentry *demo_mount(struct file_system_type *fs_type,
                                 int flags, const char *dev_name, void *data)
{
    /* kernfs_mount автоматично зв'язує VFS superblock із нашим kernfs_root */
    return kernfs_mount(fs_type, flags, demo_root, DEMO_FS_MAGIC, NULL);
}

static void demo_kill_sb(struct super_block *sb)
{
    /* Автоматична деінсталяція VFS dentry та inode при розмонтуванні */
    kernfs_kill_sb(sb);
}

static struct file_system_type demo_fs_type = {
    .name     = "demo_kernfs",
    .mount    = demo_mount,
    .kill_sb  = demo_kill_sb,
    .owner    = THIS_MODULE,
};

/* --- Ініціалізація модуля ядра --- */
static int __init demo_kernfs_init(void)
{
    int ret;

    pr_info("demo_kernfs: Initializing custom kernfs demonstration module...\n");

    /* 1. Створюємо корінь деревного графа kernfs */
    demo_root = kernfs_create_root(NULL, 0, NULL);
    if (IS_ERR(demo_root)) {
        pr_err("demo_kernfs: Failed to create kernfs root structure\n");
        return PTR_ERR(demo_root);
    }

    /* 2. Створюємо файл /info у корені з правами читання 0444 */
    info_node = kernfs_create_file(demo_root->kn, "info", 0444, 0,
                                   &info_ops, NULL);
    if (IS_ERR(info_node)) {
        ret = PTR_ERR(info_node);
        pr_err("demo_kernfs: Failed to create /info node (err=%d)\n", ret);
        goto err_destroy_root;
    }

    /* 3. Створюємо каталог /control з правами 0755 */
    control_dir = kernfs_create_dir(demo_root->kn, "control", 0755, NULL);
    if (IS_ERR(control_dir)) {
        ret = PTR_ERR(control_dir);
        pr_err("demo_kernfs: Failed to create /control directory (err=%d)\n", ret);
        goto err_destroy_root;
    }

    /* 4. Створюємо файл /control/status з правами читання/запису 0644 */
    status_node = kernfs_create_file(control_dir, "status", 0644, 0,
                                     &status_ops, NULL);
    if (IS_ERR(status_node)) {
        ret = PTR_ERR(status_node);
        pr_err("demo_kernfs: Failed to create /control/status node (err=%d)\n", ret);
        goto err_destroy_root;
    }

    /* 5. Реєструємо тип ФС у глобальному реєстрі VFS */
    ret = register_filesystem(&demo_fs_type);
    if (ret) {
        pr_err("demo_kernfs: Failed to register demo_kernfs filesystem type\n");
        goto err_destroy_root;
    }

    pr_info("demo_kernfs: Subsystem initialized cleanly. Mount using: mount -t demo_kernfs none /mnt/demo_fs\n");
    return 0;

err_destroy_root:
    /* При виникненні помилок рекурсивно очищаємо виділені вузли */
    kernfs_destroy_root(demo_root);
    return ret;
}

/* --- Очищення ресурсів при розвантаженні модуля --- */
static void __exit demo_kernfs_exit(void)
{
    pr_info("demo_kernfs: Unregistering filesystem from VFS...\n");
    unregister_filesystem(&demo_fs_type);

    /*
     * kernfs_destroy_root рекурсивно проходить по всіх вузлах,
     * викликає kernfs_drain() для кожного з них, очікує завершення
     * активних файлових операцій read/write та звільняє пам'ять.
     */
    kernfs_destroy_root(demo_root);
    pr_info("demo_kernfs: Module unloaded with 100%% active reference drain safety.\n");
}

module_init(demo_kernfs_init);
module_exit(demo_kernfs_exit);
```

---

## 2. Детальний аналіз механізмів коду ядра

Для того щоб зрозуміти, як написаний модуль забезпечує високу продуктивність та надійність, проаналізуємо ключові етапи його роботи:

### 1. Ініціалізація `kernfs_root` та утворення ієрархії
Під час виконання `kernfs_create_root(NULL, 0, NULL)` шар `kernfs` виділяє корінь файлової системи `struct kernfs_root` та автоматично створює перший кореневий вузол `kernfs_node` типу `KERNFS_DIR`. Посилання на цей кореневий вузол доступне через `demo_root->kn`.

Далі виклики `kernfs_create_dir` та `kernfs_create_file` додають дочірні вузли. Кожен виклик виконує такі атомарні кроки:
- Виділяє пам'ять під новий `struct kernfs_node` зі SLAB-кешу `kernfs_node_cache`.
- Призначає ім'я та обчислює його 32-бітний хеш `kernfs_name_hash(name, ns)`.
- Вставляє вузол у червоно-чорне дерево `parent->dir.children` за логарифмічний час `O(log N)`.
- Призначає вказівник на таблицю операцій `ops`. Народжується вузол деактивованим (`active == KN_DEACTIVATED_BIAS`) і активується вже під час додавання в дерево — тоді `active` стає `0`, і файл починає приймати операції.

### 2. Безпека запису та парсинг рядків
У методі `demo_status_write` ядро отримує буфер `buf`, переданий із простору користувача. Оскільки `kernfs` автоматично дописує нульовий термінатор `\0` в кінець буфера `buf`, розробник ядра може безпечно використовувати допоміжні функції `strstrip()` (для вилучення символів переведення рядка `\n`) та `kstrtoint()` (для перетворення рядка в ціле число з перевіркою переповнення). Це упереджує вразливості типу «переповнення буфера у стеку ядра».

### 3. Очищення ресурсів та функціонал `kernfs_destroy_root()`
Найважливішою перевагою використання `kernfs` у драйвері є виклик `kernfs_destroy_root(demo_root)` у деструкторі `demo_kernfs_exit`. 

При виконанні цієї функції відбувається рекурсивний обхід дерева вузлів:
1. Для кожного вузла викликається `kernfs_drain()`, що унеможливлює виникнення нових системних викликів.
2. Якщо у цей момент процес користувача виконує читання `/mnt/demo_fs/info`, потік розвантаження модуля ядра блокується на черзі очікування `deactivate_waitq`.
3. Лише після того, як останнє активне посилання буде повернуто і `active` впаде назад до `KN_DEACTIVATED_BIAS`, ядро вивільняє пам'ять вузла і повертає керування з `rmmod`.

---

## 3. Детальний потік виконання системних викликів у ядрі

Щоб краще зрозуміти взаємодію між VFS, `kernfs` та кодом нашого модуля, розберемо послідовність викликів під час виконання стандартних команд Linux у терміналі.

### Сценарій А: Зчитання файлу `cat /mnt/demo_fs/info`

1. **Системний виклик `open()`**:
   - Процес у просторі користувача викликає `open("/mnt/demo_fs/info", O_RDONLY)`.
   - VFS шукає шлях у кеші `dcache`. При першому зверненні `dentry` відсутній.
   - VFS звертається до `kernfs_iop_lookup()`, який проводить пошук вузла "info" у червоно-чорному дереві `demo_root->kn` за ім'ям та хешем.
   - Знайшовши `kernfs_node` для "info", ядро викликає `kernfs_get_inode()`, створює тимчасову структуру `struct inode` у кеші `icache` та призначає таблицю операцій `kernfs_file_fops`.
   - У `kernfs_fop_open()` виділяється структура `struct kernfs_open_file` і підключається механізм `seq_file` (сам `seq_file` осідає в полі `of->seq_file`).

2. **Системний виклик `read()`**:
   - Процес викликає `read(fd, buf, 512)`.
   - Перехоплювач `kernfs_fop_read()` першим ділом викликає `kernfs_get_active(info_node)`. Лічильник `info_node->active` атомарно збільшується.
   - `kernfs` спрямовує виклик у `seq_read()`, який викликає наш метод `demo_info_show()`.
   - Функція `seq_printf()` форматує текст ("=== Demo Kernfs Subsystem ===", статус, значення лічильника) у внутрішній сторінковий буфер `seq_file`.
   - Дані копіюються у простір користувача через `copy_to_user()`.
   - `kernfs` викликає `kernfs_put_active(info_node)`, зменшуючи лічильник активних операцій.

3. **Системний виклик `close()`**:
   - Процес закриває файловий дескриптор.
   - `kernfs_fop_release()` звільняє контекст `kernfs_open_file`. Якщо інших відкритих дескрипторів немає, VFS shrinker може у будь-який момент вилучити тимчасові `dentry` та `inode`, але `kernfs_node` залишається жити у пам'яті модуля.

---

### Сценарій Б: Запис значення `echo "500" > /mnt/demo_fs/control/status`

1. **Системний виклик `write()`**:
   - VFS перехоплює запит і викликає `kernfs_fop_write()`.
   - Перевірка `kernfs_get_active(status_node)` гарантує, що файл не перебуває у стані вилучення.
   - Шар `kernfs` захоплює мутекс `of->mutex` для забезпечення послідовного запису при паралельних викликах з різних потоків.
   - `kernfs` копіює рядок з простору користувача у тимчасовий ядерний буфер і гарантовано ставить нуль-термінатор `\0` в кінець.
   - Керування передається у наш метод `demo_status_write()`.
   - Функція `strstrip()` вилучає символ `\n`, а `kstrtoint()` перетворює "500" у ціле число `500`.
   - Атомарна функція `atomic_set(&global_counter, 500)` оновлює значення у RAM.
   - Мутекс розблоковується, `kernfs_put_active()` зменшує лічильник, і виклик `write()` повертає кількість записаних байтів.

---

## 4. Обробка крайніх випадків та інваріанти синхронізації

Під час розробки модулів на базі `kernfs` необхідно дотримуватися кількох суворих інженерних правил:

1. **Захист від некоректного вводу**:
   У методі `demo_status_write` ми перевіряємо не лише факт успішного конвертування рядка в число через `kstrtoint()`, але й валідуємо діапазон допустимих значень (`val < 0 || val > 1000000`). Якщо користувач передасть від'ємне число або нечисловий рядок (наприклад, `echo "abc" > status`), драйвер поверне `-EINVAL`; на числі, що не влазить у `int`, `kstrtoint()` віддасть `-ERANGE`. І те, і те запобігає пошкодженню внутрішніх даних модуля.

2. **Захист від умов гонитви при паралельному записі**:
   Завдяки тому, що `kernfs` захищає виклик `.write` мутексом `of->mutex`, два паралельних потоки, які одночасно виконують `write()` у той самий файл `status`, будуть послідовно впорядковані. Перший потік викличе `demo_status_write`, оновлюючи атомарний лічильник, і лише після його виходу керування отримає другий потік.

3. **Обробка помилок ієрархічної ініціалізації**:
   У функції `demo_kernfs_init()` кожен виклик створення вузла перевіряється за допомогою макросу `IS_ERR()`. Якщо виділення пам'яті для `/control/status` зазнає невдачі (наприклад, при екстремальному дефіциті RAM), виконання передається на мітку `err_destroy_root`. Виклик `kernfs_destroy_root(demo_root)` рекурсивно вилучить уже успішно створені вузли `/info` та `/control`, запобігаючи витоку SLAB-пам'яті.

---

## 5. Збірка модуля через Makefile

Створіть файл `Makefile` у тій самій теці:

```makefile
obj-m += demo_kernfs_module.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

---

## 6. Утиліта тестування у просторі користувача

Для взаємодії зі змонтованою файловою системою можна використовувати стандартизовані системні виклики POSIX. Нижче наведено ідіоматичні реалізації утиліти читання й модифікації атрибутів мовами C та C++.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define STATUS_PATH "/mnt/demo_fs/control/status"
#define INFO_PATH   "/mnt/demo_fs/info"

static void read_file(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return;
    }

    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    if (n >= 0) {
        buf[n] = '\0';
        printf("--- Вміст %s ---\n%s", path, buf);
    } else {
        fprintf(stderr, "Помилка читання з %s: %s\n", path, strerror(errno));
    }
    close(fd);
}

static void write_status(const char *path, int new_val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття на запис %s: %s\n", path, strerror(errno));
        return;
    }

    char buf[32];
    int len = snprintf(buf, sizeof(buf), "%d\n", new_val);
    ssize_t written = write(fd, buf, len);
    if (written < 0) {
        fprintf(stderr, "Помилка запису у %s: %s\n", path, strerror(errno));
    } else {
        printf("Успішно записано %d у %s\n", new_val, path);
    }
    close(fd);
}

int main(void) {
    printf("1. Читання інформаційного вузла:\n");
    read_file(INFO_PATH);

    printf("\n2. Поточне значення лічильника:\n");
    read_file(STATUS_PATH);

    printf("\n3. Оновлення значення лічильника на 500:\n");
    write_status(STATUS_PATH, 500);

    printf("\n4. Перевірка оновленого значення:\n");
    read_file(STATUS_PATH);

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

static void read_file(const fs::path& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Помилка відкриття файлу: " << filepath << '\n';
        return;
    }

    std::cout << "--- Вміст " << filepath << " ---\n";
    std::string line;
    while (std::getline(file, line)) {
        std::cout << line << '\n';
    }
}

static void write_status(const fs::path& filepath, int new_val) {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Помилка відкриття для запису: " << filepath << '\n';
        return;
    }

    file << new_val << '\n';
    if (file.good()) {
        std::cout << "Успішно оновлено значення у " << filepath << " на " << new_val << '\n';
    } else {
        std::cerr << "Помилка запису у файл " << filepath << '\n';
    }
}

int main() {
    const fs::path info_path{"/mnt/demo_fs/info"};
    const fs::path status_path{"/mnt/demo_fs/control/status"};

    std::cout << "1. Читання інформаційного вузла:\n";
    read_file(info_path);

    std::cout << "\n2. Поточне значення лічильника:\n";
    read_file(status_path);

    std::cout << "\n3. Оновлення значення лічильника на 750:\n";
    write_status(status_path, 750);

    std::cout << "\n4. Перевірка оновленого значення:\n";
    read_file(status_path);

    return 0;
}
```
:::

---

## 7. Покрокова інструкція зі збірки, монтування та тестування

### Крок 1: Компіляція та завантаження модуля ядра
Використовуйте стандартні консольні інструменти збірки модулів ядра Linux:

```bash
# Компіляція модуля ядра
make

# Завантаження згенерованого .ko модуля
sudo insmod demo_kernfs_module.ko

# Перевірка виводу кільцевого буфера ядра (dmesg)
dmesg | tail -n 5
```

Очікуваний вивід у `dmesg`:
```
demo_kernfs: Initializing custom kernfs demonstration module...
demo_kernfs: Subsystem initialized cleanly. Mount using: mount -t demo_kernfs none /mnt/demo_fs
```

### Крок 2: Створення точки монтування та монтування ФС
```bash
# Створення порожнього каталогу у /mnt
sudo mkdir -p /mnt/demo_fs

# Виконання системного виклику mount для типу demo_kernfs
sudo mount -t demo_kernfs none /mnt/demo_fs

# Перевірка змонтованої ФС серед активних точок монтування
mount | grep demo_kernfs
```

### Крок 3: Тестування через стандартні утиліти Bash
```bash
# Перегляд структури каталогів
ls -la /mnt/demo_fs
ls -la /mnt/demo_fs/control

# Читання статичного текстового атрибута
cat /mnt/demo_fs/info

# Читання поточного значення лічильника
cat /mnt/demo_fs/control/status

# Модифікація значення лічильника через echo
echo "420" | sudo tee /mnt/demo_fs/control/status

# Перевірка оновленого стану
cat /mnt/demo_fs/control/status
```

### Крок 4: Перевірка через програму простору користувача
```bash
# Компіляція C++ тестової утиліти
g++ -std=c++17 test_app.cpp -o test_app

# Запуск тесту під привілейованим користувачем
sudo ./test_app
```

### Крок 5: Безпечне розмонтування та розвантаження
```bash
# Розмонтування віртуальної файлової системи
sudo umount /mnt/demo_fs

# Вилучення модуля з ядра
sudo rmmod demo_kernfs_module

# Перевірка чистого виходу у dmesg
dmesg | tail -n 5
```

Виклик `kernfs_destroy_root()` при розвантаженні модуля автоматично гарантує, що ядро пройде через механізм `kernfs_drain()`, розірве всі зв'язки з VFS та безпечно звільнить оперативну пам'ять без залишення «сирітських» структур.
