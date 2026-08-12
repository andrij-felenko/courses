# ⚙️ Практика розробки: інтеграція debugfs у модуль ядра та зчитування tracefs

Ця вставка містить покрокове керівництво з практичної реалізації двох системних задач: створення власного модуля ядра Linux із вузлами у `debugfs` на основі безпечного інтерфейсу `seq_file`, а також створення утиліти простору користувача мовами C та C++ для потокового аналізу подій із файлової системи `tracefs`.

---

## 1. Модуль ядра Linux: реєстрація вузлів у debugfs (Kernel Space)

У просторі ядра розробка здійснюється мовою C з використанням спеціалізованого API ядра Linux. Для роботи з `debugfs` та запобігання переповненню буферів пам'яті застосовується підсистема `seq_file` (`<linux/seq_file.h>`).

### Архітектура коду модуля ядра

Головною задачею модуля ядра є експорт внутрішнього стану підсистеми у простір користувача без ризику пошкодження пам'яті ядра. Традиційні операції `read` вимагають від розробника самостійного відстеження поточного зміщення у файлі (`loff_t *ppos`) та викликів `copy_to_user()`. При формуванні складних або багатосторінкових звітів це регулярно призводило до випадкових виходів за межі виділеного буфера та падіння ядра.

Підсистема `seq_file` повністю автоматизує керування буферами пам'яті. Розробник реалізує лише функцію зчитування `show`, яка записує форматований текст у буфер за допомогою безпечної функції `seq_printf()`. Якщо сформований звіт не вміщається у поточний буфер, `seq_file` автоматично подвоює його розмір і повторює виклик функції `show`.

Нижче наведено повний вихідний код модуля ядра `demo_debug_module.c`. Він створює каталог `/sys/kernel/debug/demo_driver`, експортує у ньому скалярний лічильник `u32`, конфігураційний прапорець `bool` та власний вузол `status_report`, який повертає форматований звіт.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/mutex.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Engine");
MODULE_DESCRIPTION("Приклад інтеграції debugfs та seq_file");

/* Структури даних ядра для керування вузлами debugfs */
static struct dentry *demo_dir;
static u32 packet_count = 0;
static bool debug_mode_enabled = false;

/* М'ютекс для захисту змінних стану від паралельного читання/запису */
static DEFINE_MUTEX(state_lock);

/* 
 * Обробник виводу даних через seq_file.
 * Функція викликається ядром для форматування текстового виводу.
 * seq_printf гарантує безпечне виділення пам'яті та усуває ризик
 * переповнення буфера при формуванні великих звітів.
 */
static int demo_seq_show(struct seq_file *m, void *v)
{
    mutex_lock(&state_lock);
    seq_printf(m, "===================================\n");
    seq_printf(m, " СТАТУС ДРАЙВЕРА DEMO_DRIVER       \n");
    seq_printf(m, "===================================\n");
    seq_printf(m, "Опрацьовані пакети : %u\n", packet_count);
    seq_printf(m, "Режим налагодження: %s\n", debug_mode_enabled ? "УВІМКНЕНО" : "ВИМКНЕНО");
    seq_printf(m, "Адреса структур   : %px\n", m->private);
    seq_printf(m, "===================================\n");
    mutex_unlock(&state_lock);
    return 0;
}

/* Обробник відкриття файлу через single_open */
static int demo_seq_open(struct inode *inode, struct file *file)
{
    return single_open(file, demo_seq_show, inode->i_private);
}

/* 
 * Таблиця операцій над файлом debugfs.
 * Використовуються стандартні макроси seq_read, seq_lseek та single_release,
 * що мінімізує кількість написаного коду.
 */
static const struct file_operations demo_fops = {
    .owner   = THIS_MODULE,
    .open    = demo_seq_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};

static int __init demo_debugfs_init(void)
{
    pr_info("demo_driver: Ініціалізація вузлів у debugfs...\n");

    /* Створення каталогу /sys/kernel/debug/demo_driver */
    demo_dir = debugfs_create_dir("demo_driver", NULL);
    if (IS_ERR(demo_dir)) {
        pr_err("demo_driver: Помилка створення каталогу в debugfs (%ld)\n", PTR_ERR(demo_dir));
        return PTR_ERR(demo_dir);
    }

    /* Експорт 32-бітного беззнакового цілого числа (права 0644 — читання/запис) */
    debugfs_create_u32("packet_count", 0644, demo_dir, &packet_count);

    /* Експорт булевого прапорця (права 0644) */
    debugfs_create_bool("debug_enabled", 0644, demo_dir, &debug_mode_enabled);

    /* Експорт користувацького вузла seq_file (права 0444 — лише читання) */
    debugfs_create_file("status_report", 0444, demo_dir, NULL, &demo_fops);

    pr_info("demo_driver: Успішно зареєстровано вузли у /sys/kernel/debug/demo_driver\n");
    return 0;
}

static void __exit demo_debugfs_exit(void)
{
    pr_info("demo_driver: Вилучення вузлів із debugfs...\n");

    /* 
     * Рекурсивне видалення каталогу та всіх його елементів.
     * Запобігає витоку пам'яті та залишенню «сирітських» dentry в ядрі.
     */
    debugfs_remove_recursive(demo_dir);
    pr_info("demo_driver: Модуль вивантажено.\n");
}

module_init(demo_debugfs_init);
module_exit(demo_debugfs_exit);
```

### Покроковий розбір ключових моментів реалізації

1. **Захист стану через м'ютекс:** Функція `demo_seq_show` викликається у контексті процесу простору користувача, який виконує системний виклик `read()`. Оскільки декілька процесів можуть одночасно читати файл `status_report`, виклики `mutex_lock(&state_lock)` та `mutex_unlock(&state_lock)` гарантують узгодженість зчитуваних даних і запобігають станам «перегонів» (data races).
2. **Форматування адреси пам'яті:** Специфікатор `%px` у `seq_printf()` використовується замість звичайного `%p` для друку справжньої нехэшованої фізичної або віртуальної адреси вказівника. З міркувань безпеки звичайний специфікатор `%p` у сучасних ядрах Linux маскує адреси виводом нулів або хеш-рядків.
3. **Обробка помилок `IS_ERR`:** Результат виклику `debugfs_create_dir()` обов'язково перевіряється макросом `IS_ERR()`. Якщо виклик зазнав невдачі, функція повертає маскований код помилки викликом `PTR_ERR()`, зупиняючи завантаження модуля.

### Сценарій збірки та тестування модуля ядра

Для компіляції модуля ядра використовується стандартний `Makefile` підсистеми kbuild:

```makefile
obj-m += demo_debug_module.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
```

Команди для виконання у терміналі під час тестування модуля ядра:

```bash
# 1. Скомпілювати модуль ядра
$ make

# 2. Завантажити модуль у ядро
$ sudo insmod demo_debug_module.ko

# 3. Перевірити вивід системного логу dmesg
$ dmesg | tail -n 5

# 4. Прочитати звіт із debugfs
$ sudo cat /sys/kernel/debug/demo_driver/status_report

# 5. Змінити значення лічильника та прапорця налагодження
$ echo 42 | sudo tee /sys/kernel/debug/demo_driver/packet_count
$ echo Y | sudo tee /sys/kernel/debug/demo_driver/debug_enabled

# 6. Перевірити оновлений звіт
$ sudo cat /sys/kernel/debug/demo_driver/status_report

# 7. Вивантажити модуль з ядра
$ sudo rmmod demo_debug_module
```

---

## 2. Утиліта простору користувача: безперервне читання tracefs

Утиліта простору користувача здійснює моніторинг кільцевого буфера `/sys/kernel/tracing/trace_pipe` у режимі реального часу. На відміну від статичного файла `trace`, читання з `trace_pipe` є потоковим та деструктивним: опрацьований рядок події видаляється з кільцевого буфера ядра.

Системний виклик `read()` на файловому дескрипторі `trace_pipe` переводить викликаючий процес у стан очікування (sleeping/blocking), доки ядро не згенерує нову подію трасування. Це гарантує нульове споживання ресурсів процесора (CPU 0%) у моменти відсутності подій у ядрі.

За принципами розробки, для звичайного простору користувача приклад наводиться двома мовами — C та C++ — у вигляді окремих ідіоматичних вкладок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define TRACE_PIPE_PATH "/sys/kernel/tracing/trace_pipe"
#define BUFFER_SIZE 4096

int main(void)
{
    /* 
     * Відкриття файлу trace_pipe у режимі лише для читання.
     * Потребує привілеїв root або належності до групи tracing.
     */
    int fd = open(TRACE_PIPE_PATH, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", TRACE_PIPE_PATH, strerror(errno));
        fprintf(stderr, "Перевірте права суперкористувача (sudo).\n");
        return EXIT_FAILURE;
    }

    printf("=== Потокове зчитування tracefs (%s) ===\n", TRACE_PIPE_PATH);
    printf("Натисніть Ctrl+C для зупинки.\n\n");

    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;

    /* 
     * Цикл потокового зчитування.
     * Системний виклик read() блокує процес до появи нових подій у ядрі.
     */
    while ((bytes_read = read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[bytes_read] = '\0';
        fputs(buffer, stdout);
        fflush(stdout);
    }

    if (bytes_read < 0) {
        fprintf(stderr, "Помилка читання з файлу: %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <system_error>
#include <filesystem>

namespace fs = std::filesystem;

int main()
{
    const fs::path trace_pipe_path{"/sys/kernel/tracing/trace_pipe"};

    /* 
     * Ідіоматичне відкриття файлового потоку в C++20
     * з використанням RAII для автоматичного закриття дескриптора.
     */
    std::ifstream trace_file{trace_pipe_path};
    if (!trace_file.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити " << trace_pipe_path << '\n';
        std::cerr << "Перевірте права суперкористувача (sudo) або конфігурацію dmesg_restrict.\n";
        return 1;
    }

    std::cout << "=== Потокове зчитування tracefs (" << trace_pipe_path << ") ===\n";
    std::cout << "Натисніть Ctrl+C для зупинки.\n\n";

    std::string line;
    /* 
     * Порядкове зчитування через std::getline.
     * Потік блокується ядром до появи нового рядка події у trace_pipe.
     */
    while (std::getline(trace_file, line)) {
        std::cout << line << '\n';
    }

    if (trace_file.bad()) {
        std::cerr << "Критична помилка потоку при зчитуванні з tracefs\n";
        return 1;
    }

    return 0;
}
```
:::

### Особливості реалізації мовами C та C++

- **Вкладка C:** Використовує низькорівневі системні виклики POSIX `open()` та `read()`. Буфер очищується примусовим скидачем `fflush(stdout)`, що гарантує негайний вивід рядків трасування у консоль без затримок у буфері стандартного виводу C.
- **Вкладка C++:** Застосовує сучасний стандарт C++20 (`std::filesystem::path`) та RAII-обгортку `std::ifstream`. Обробка помилок спирається на перевірку стану потоку `trace_file.bad()`, а закриття дескриптора виконується деструктором при виході з зони видимості.

### Компіляція та запуск утиліти аналізу tracefs

Для тестування утиліти необхідно скомпілювати її та увімкнути будь-яку статичну точку трасування (наприклад, перемикач контексту процесів `sched_switch`):

```bash
# 1. Компіляція утиліти на C та C++
$ gcc -Wall -Wextra trace_reader.c -o trace_reader_c
$ g++ -Wall -Wextra -std=c++20 trace_reader.cpp -o trace_reader_cpp

# 2. Увімкнення статичної точки трасування sched_switch у tracefs
$ echo 1 | sudo tee /sys/kernel/tracing/events/sched/sched_switch/enable

# 3. Запуск C або C++ утиліти моніторингу подій
$ sudo ./trace_reader_cpp

# 4. Після завершення спостереження вимкнути точку трасування
$ echo 0 | sudo tee /sys/kernel/tracing/events/sched/sched_switch/enable
```

---

## 3. Крайові випадки, безпека та розв'язання підводних каменів

Під час експлуатації та розробки ВФС налагодження виникають специфічні ситуації, які вимагають окремого аналізу.

### Запобігання гонитві умов при вивантаженні модуля (Unload Races)

Найпоширенішою помилкою при розробці драйверів з `debugfs` є вивантаження модуля ядра (`rmmod`), у той час як процес у просторі користувача утримує відкритий файловий дескриптор у `/sys/kernel/debug/my_driver/status_report`.

Якщо розробник виконує звичайне видалення структур у `module_exit()`, пам'ять під структури операцій та приватні дані звільняється. Наступний виклик `read()` із користувацької програми спричинить звернення до звільненої пам'яті (Use-After-Free) та Kernel Panic.

Для вирішення цієї проблеми в сучасному ядрі Linux впроваджено автоматичний шар відстеження `debugfs_file_get()` та `debugfs_file_put()`. Коли модуль викликає `debugfs_remove_recursive()`, ядро помічає файл як видалений, але відкладає звільнення пам'яті до тих пір, поки всі відкриті користувацькі файлові дескриптори не будуть закриті функцією `close()`.

### Обробка сигналів переривання системних викликів (EINTR)

При читанні потокового файлу `/sys/kernel/tracing/trace_pipe` процес користувача перебуває у стані очікування події. Якщо в цей момент процесу надсилається сигнал (наприклад, `SIGINT` при натисканні Ctrl+C або `SIGTERM`), системний виклик `read()` переривається з кодом помилки `EINTR`.

Утиліти простору користувача повинні коректно обробляти код `EINTR`, відрізняючи сигнальне переривання від реальних збоїв введення-виведення на рівні ВФС, що гарантує чисте завершення роботи та закриття відкритих дескрипторів.
