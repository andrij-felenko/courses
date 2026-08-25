# ⚙️ Розробка модуля ядра з власним файлом debugfs та користувацькою програмою спостереження

Практичний проект демонструє створення модуля ядра Linux, який експортує кільцевий буфер подій та лічильники через debugfs з використанням seq_file та атомарних операцій, а також розробку ідіоматичних клієнтів простору користувача мовами C та C++ для моніторингу цих даних.

## 1. Постановка задачі та архітектура рішення

При розробці системних драйверів та підсистем ядра Linux виникає критична потреба збирати діагностичну статистику подій та надавати інженеру можливість динамічно змінювати режими роботи модуля безпосередньо під час виконання, не вдаючись до перезбирання коду чи перезавантаження операційної системи. 

У цьому практичному проекті ми спроектуємо та реалізуємо повноцінний модуль ядра під назвою `kdebug_inspector`. При завантаженні цей модуль створює власну ієрархію каталогів усередині віртуальної файлової системи debugfs за шляхом `/sys/kernel/debug/inspector_demo/`.

```
+--------------------------------------------------------------------------+
|                          АРХІТЕКТУРА ПРОЄКТУ                             |
+--------------------------------------------------------------------------+
|  User Space (Простір користувача):                                       |
|   - Команди утиліт: cat, echo, sudo                                      |
|   - Клієнти моніторингу: C (POSIX APIs) та C++ (std::filesystem, RAII)    |
+--------------------------------------------------------------------------+
                                    |
                                    |  системні виклики: open(), read(), write()
                                    v
+--------------------------------------------------------------------------+
|  Kernel Space (debugfs VFS & kdebug_inspector.ko):                       |
|                                                                          |
|   /sys/kernel/debug/inspector_demo/                                      |
|    |-- event_count  <-- debugfs_create_atomic_t (атомарний лічильник)    |
|    |-- control      <-- debugfs_create_file (запис "1"/"0" у прапорець)   |
|    `-- events_log   <-- debugfs_create_file (seq_file кільцевого буфера)|
+--------------------------------------------------------------------------+
```

Для демонстрації різноманітних типів взаємодії наш модуль реалізує три незалежні точки доступу:
1. **`event_count`** (атомарний лічильник): використовує C API `debugfs_create_atomic_t` для беззамоквого оновлення та зчитання загальної кількості зареєстрованих подій ядра.
2. **`control`** (файл читання та запису): реалізує власну структуру `file_operations` для зчитування поточного стану журналювання та запису прапорця вмикання чи вимикання генерації подій через текстові команди `"1"` або `"0"`.
3. **`events_log`** (послідовний файл `seq_file`): форматований журнал останніх подій ядра, збережених у кільцевому буфері пам'яті під захистом потокового м'ютекса (`struct mutex`).

Після реалізації та завантаження модуля ядра ми розробляємо дві незалежні утиліти моніторингу простору користувача мовами **C** та **C++**.

---

## 2. Механізми передачі даних та безпека межі "ядро — простір користувача"

Взаємодія між програмою простору користувача та модулем ядра через файли debugfs спирається на стандартні системні виклики VFS (`open`, `read`, `write`, `close`). Однак передача даних через межу привілейованого режиму виконання вимагає дотримання суворих правил безпеки пам'яті.

### Безпечне копіювання через межу MMU

Коли програма користувача надсилає команду запису у файл `/sys/kernel/debug/inspector_demo/control` через системний виклик `write(fd, "1", 1)`, вказівник на буфер пам'яті належить віртуальному адресному простору користувацького процесу. Ядро Linux не має права прямо dereferencing цей вказівник у своєму контексті, оскільки користувацький процес може передати невалідну адресу, зняту з мапування сторінку пам'яті або свідомо підроблений вказівник на структури ядра.

Для безпечного перенесення даних використовується функція ядра `copy_from_user()`:

```c
if (copy_from_user(buf, user_buf, buf_size))
    return -EFAULT;
```

Функція `copy_from_user()` перевіряє права доступу до сторінки пам'яті в таблицях сторінок MMU (Memory Management Unit). Якщо користувацький буфер є невалідним, функція перехоплює сторінковий зсув (Page Fault) і повертає кількість некопійованих байтів, запобігаючи падінню ядра (Kernel Panic). У разі помилки обробник запису повертає від'ємний код помилки `-EFAULT`, який системний виклик VFS транслює у користувацьку змінну `errno`.

Для зчитування даних із буфера ядра у користувацький буфер у файлі `control` використовується хелпер `simple_read_from_buffer()`. Він автоматично обробляє поточне зміщення каретки читання (`loff_t *ppos`), гарантуючи, що повторні виклики `read()` не будуть зациклюватися, а повернуть `0` (EOF — End of File), коли весь текстовий рядок буде зчитано.

### Захист кільцевого буфера та математика циклічного індексу

Кільцевий буфер подій у нашому модулі зберігає масив із `LOG_MAX_ENTRIES` (10) елементів `struct log_entry`. Кожен елемент містить часову мітку наносекундної точності `ktime_get_real_ns()` та текстове повідомлення.

Для додавання нових подій використовується циклічне оновлення індексу верхівки буфера:

```
ring_head = (ring_head + 1) % LOG_MAX_ENTRIES
```

Ця математика гарантує, що при досягненні кінця масиву нові записи починають перезаписувати найстаріші події, утворюючи фіксоване за розміром вікно останніх подій без ризику виходу за межі виділеної пам'яті (Buffer Overflow).

Оскільки до файлу debugfs можуть одночасно звертатися декілька процесів простору користувача або декілька ядерних потоків, оновлення індексів `ring_head`, `ring_count` та читання буфера у `seq_file` захищені потоковим м'ютексом `ring_lock` (`mutex_lock(&ring_lock)` / `mutex_unlock(&ring_lock)`). Це унеможливлює стан гонки (Race Condition) та пошкодження даних у пам'яті ядра.

---

## 3. Повний сирцевий код модуля ядра (`kdebug_inspector.c`)

Нижче наведено повний сирцевий код модуля ядра `kdebug_inspector.c`, що реалізує описану архітектуру.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/mutex.h>
#include <linux/uaccess.h>
#include <linux/atomic.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Developer");
MODULE_DESCRIPTION("Demo Kernel Module with Custom debugfs Interface");
MODULE_VERSION("1.0");

#define LOG_MAX_ENTRIES 10
#define LOG_ENTRY_LEN 128

struct log_entry {
    u64 timestamp_ns;
    char message[LOG_ENTRY_LEN];
};

static struct dentry *demo_dir;
static atomic_t event_count = ATOMIC_INIT(0);
static bool logging_enabled = true;

static struct log_entry ring_buffer[LOG_MAX_ENTRIES];
static size_t ring_head = 0;
static size_t ring_count = 0;
static DEFINE_MUTEX(ring_lock);

/* Додавання нового запису до кільцевого буфера ядра */
static void add_event_log(const char *msg)
{
    if (!logging_enabled)
        return;

    mutex_lock(&ring_lock);
    
    ring_buffer[ring_head].timestamp_ns = ktime_get_real_ns();
    snprintf(ring_buffer[ring_head].message, LOG_ENTRY_LEN, "%s", msg);
    
    ring_head = (ring_head + 1) % LOG_MAX_ENTRIES;
    if (ring_count < LOG_MAX_ENTRIES)
        ring_count++;

    mutex_unlock(&ring_lock);
    atomic_inc(&event_count);
}

/* === Послідовний вивід seq_file для events_log === */
static int events_seq_show(struct seq_file *s, void *v)
{
    size_t i, idx;
    u64 sec, nsec;

    mutex_lock(&ring_lock);
    seq_printf(s, "=== INSPECTOR DEMO LOG (Total Events: %d) ===\n", atomic_read(&event_count));
    seq_printf(s, "%-20s | %s\n", "Timestamp (s.ns)", "Event Message");
    seq_printf(s, "-----------------------------------------------------\n");

    for (i = 0; i < ring_count; i++) {
        /* Обчислюємо індекс для зчитування від найстарішого запису до найновішого */
        if (ring_count < LOG_MAX_ENTRIES) {
            idx = i;
        } else {
            idx = (ring_head + i) % LOG_MAX_ENTRIES;
        }

        sec = ring_buffer[idx].timestamp_ns / 1000000000ULL;
        nsec = ring_buffer[idx].timestamp_ns % 1000000000ULL;

        seq_printf(s, "%llu.%09llu | %s\n", sec, nsec, ring_buffer[idx].message);
    }

    mutex_unlock(&ring_lock);
    return 0;
}

static int events_seq_open(struct inode *inode, struct file *file)
{
    return single_open(file, events_seq_show, NULL);
}

static const struct file_operations events_fops = {
    .owner   = THIS_MODULE,
    .open    = events_seq_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};

/* === Обробник читання та запису для control === */
static ssize_t control_write(struct file *file, const char __user *user_buf,
                             size_t count, loff_t *ppos)
{
    char buf[16];
    size_t buf_size = min(count, sizeof(buf) - 1);

    if (copy_from_user(buf, user_buf, buf_size))
        return -EFAULT;

    buf[buf_size] = '\0';

    if (buf[0] == '1') {
        logging_enabled = true;
        add_event_log("Logging manually ENABLED via control file");
    } else if (buf[0] == '0') {
        add_event_log("Logging manually DISABLED via control file");
        logging_enabled = false;
    }

    return count;
}

static ssize_t control_read(struct file *file, char __user *user_buf,
                            size_t count, loff_t *ppos)
{
    char status_str[32];
    int len = snprintf(status_str, sizeof(status_str), "Enabled: %d\n", logging_enabled);
    return simple_read_from_buffer(user_buf, count, ppos, status_str, len);
}

static const struct file_operations control_fops = {
    .owner = THIS_MODULE,
    .read  = control_read,
    .write = control_write,
};

/* === Ініціалізація та вивантаження модуля === */
static int __init inspector_init(void)
{
    demo_dir = debugfs_create_dir("inspector_demo", NULL);
    if (IS_ERR(demo_dir)) {
        pr_err("kdebug_inspector: Failed to create debugfs directory\n");
        return PTR_ERR(demo_dir);
    }

    /* 1. Створюємо атомарний файл лічильника */
    debugfs_create_atomic_t("event_count", 0644, demo_dir, &event_count);

    /* 2. Створюємо файл керування */
    debugfs_create_file("control", 0644, demo_dir, NULL, &control_fops);

    /* 3. Створюємо seq_file журнал подій */
    debugfs_create_file("events_log", 0444, demo_dir, NULL, &events_fops);

    add_event_log("Module loaded successfully");
    pr_info("kdebug_inspector: Module initialized at /sys/kernel/debug/inspector_demo\n");
    return 0;
}

static void __exit inspector_exit(void)
{
    /* Рекурсивно вилучаємо каталог і всі вкладені файли */
    debugfs_remove_recursive(demo_dir);
    pr_info("kdebug_inspector: Module unloaded\n");
}

module_init(inspector_init);
module_exit(inspector_exit);
```

---

## 4. Розробка та порівняльний розбір клієнтів простору користувача (C та C++)

Для взаємодії з вищеописаним модулем ядра з простору користувача розробляються два незалежні варіанти клієнтської програми.

### Порівняння підходів C та C++

1. **Низькорівневий підхід у C (POSIX APIs):**
   Використовує процедурні системні виклики `open()`, `read()`, `write()`, `close()`. Розробник зобов'язаний вручну керувати файловими дескрипторами (`int fd`), виділяти фіксовані текстові буфери `char buffer[]`, обробляти коди помилок через глобальну змінну `errno` та виводити деталі збоїв за допомогою `strerror()`. Ручне закриття файлів вимагає уважності при виході з функцій за кількома гілками умов.

2. **Ідіоматичний підхід у C++20 (RAII & `std::filesystem`):**
   Використовує концепцію RAII (Resource Acquisition Is Initialization). Файлові потоки `std::ifstream` та `std::ofstream` автоматично закривають файлові дескриптори у своїх деструкторах при виході об'єкта із зони видимості (Scope). Для перевірки наявності точки монтування використовується кросплатформовий модуль `std::filesystem::exists()`. Обробка помилок виконується без використання сирих буферів пам'яті через безпечні рядкові потоки `std::string`.

Ніжче наведено код обох клієнтів у паралельних вкладках.

:::tabs
```c
/* Userspace Client in C (POSIX File I/O) */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

#define PATH_EVENT_COUNT "/sys/kernel/debug/inspector_demo/event_count"
#define PATH_CONTROL     "/sys/kernel/debug/inspector_demo/control"
#define PATH_EVENTS_LOG  "/sys/kernel/debug/inspector_demo/events_log"

static void read_and_print_file(const char *path, const char *title) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Error opening %s: %s\n", path, strerror(errno));
        return;
    }

    printf("=== %s ===\n", title);
    char buffer[512];
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[bytes_read] = '\0';
        fputs(buffer, stdout);
    }
    close(fd);
    printf("\n");
}

static void write_control(const char *val) {
    int fd = open(PATH_CONTROL, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Error opening control file: %s\n", strerror(errno));
        return;
    }
    ssize_t written = write(fd, val, strlen(val));
    if (written < 0) {
        fprintf(stderr, "Failed write to control: %s\n", strerror(errno));
    } else {
        printf("Written '%s' to control file.\n", val);
    }
    close(fd);
}

int main(void) {
    if (access("/sys/kernel/debug/inspector_demo", F_OK) != 0) {
        fprintf(stderr, "Error: debugfs node not found. Are you root?\n");
        return EXIT_FAILURE;
    }

    read_and_print_file(PATH_EVENT_COUNT, "Current Event Count");
    write_control("1");
    read_and_print_file(PATH_EVENTS_LOG, "Kernel Event Log");

    return EXIT_SUCCESS;
}
```
```cpp
// Modern Userspace Client in C++20 (RAII & std::filesystem)
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

class DebugfsInspector {
public:
    static constexpr std::string_view base_path = "/sys/kernel/debug/inspector_demo";

    bool is_available() const noexcept {
        std::error_code ec;
        return fs::exists(base_path, ec);
    }

    void print_file(const fs::path& rel_path, std::string_view title) const {
        fs::path full_path = fs::path(base_path) / rel_path;
        std::ifstream file(full_path);
        
        if (!file.is_open()) {
            std::cerr << "Failed to open debugfs file: " << full_path << '\n';
            return;
        }

        std::cout << "=== " << title << " ===\n";
        std::string line;
        while (std::getline(file, line)) {
            std::cout << line << '\n';
        }
        std::cout << '\n';
    }

    void set_control(std::string_view value) const {
        fs::path control_path = fs::path(base_path) / "control";
        std::ofstream file(control_path);

        if (!file.is_open()) {
            std::cerr << "Failed to open control file for writing: " << control_path << '\n';
            return;
        }

        file << value;
        std::cout << "Successfully updated control state to: " << value << '\n';
    }
};

int main() {
    DebugfsInspector inspector;

    if (!inspector.is_available()) {
        std::cerr << "Error: /sys/kernel/debug/inspector_demo is inaccessible.\n"
                  << "Ensure the module is loaded and program runs with root privileges.\n";
        return 1;
    }

    inspector.print_file("event_count", "Current Event Count");
    inspector.set_control("1");
    inspector.print_file("events_log", "Kernel Events Log");

    return 0;
}
```
:::

---

## 5. Збирання, завантаження, випробування та обробка крайових випадків

Для збирання модуля ядра використовується стандартний `Makefile`, який звертається до підсистеми збірки ядра Kbuild.

```makefile
obj-m += kdebug_inspector.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

### Покроковий сценарій розгортання та перевірки

1. **Компіляція та завантаження модуля ядра:**
   ```bash
   make
   sudo insmod kdebug_inspector.ko
   ```

2. **Перевірка системних журналів ядра `dmesg`:**
   ```bash
   dmesg | tail -n 5
   ```
   *Очікуваний вивід:*
   `kdebug_inspector: Module initialized at /sys/kernel/debug/inspector_demo`

3. **Перевірка наявності та прав доступу до файлів:**
   ```bash
   sudo ls -la /sys/kernel/debug/inspector_demo
   ```
   *Вивід у терміналі:*
   ```text
   -rw-r--r-- 1 root root 0 Aug 14 12:00 control
   -rw-r--r-- 1 root root 0 Aug 14 12:00 event_count
   -r--r--r-- 1 root root 0 Aug 14 12:00 events_log
   ```

4. **Зчитування даних за допомогою стандартних системних утиліт:**
   ```bash
   sudo cat /sys/kernel/debug/inspector_demo/event_count
   sudo cat /sys/kernel/debug/inspector_demo/events_log
   ```

5. **Зміна режимів робота ядра через запис у `control`:**
   ```bash
   echo "0" | sudo tee /sys/kernel/debug/inspector_demo/control
   sudo cat /sys/kernel/debug/inspector_demo/control
   ```

6. **Компіляція та запуск C++ клієнта спостереження:**
   ```bash
   g++ -std=c++20 -O2 monitor_client.cpp -o monitor_client
   sudo ./monitor_client
   ```

7. **Безпечне вивантаження модуля:**
   ```bash
   sudo rmmod kdebug_inspector
   ```

### Крайові випадки та поведінка системи

- **Спроба запуску без прав `root`:** якщо користувач запускає клієнтську програму без привілей суперкористувача (`sudo`), виклик `access()` або `open()` поверне помилку `EACCES` (Permission denied). Це зумовлено тим, що точка монтування `/sys/kernel/debug` за замовчуванням має права `0700` (`drwx------`).
- **Спроба зчитування під час вивантаження модуля:** завдяки підсистемі SRCU (`debugfs_file_get` / `debugfs_file_put`), якщо юзерспейс-процес виконує тривале зчитування `events_log` у момент виконання `rmmod`, функція `debugfs_remove_recursive()` зачекає завершення читання і не викличе Use-After-Free чи Kernel Panic.
