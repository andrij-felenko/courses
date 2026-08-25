# ⚙️ Створення власної точки TRACE_EVENT у модулі ядра та читання подій з простору користувача

Трасувальні точки ядра Linux не обмежені вбудованими підсистемами ядра. Будь-який завантажуваний модуль ядра (`LKM`, Loadable Kernel Module) — наприклад, драйвер периферійного пристрою, спеціалізований протокол зв'язку чи драйвер файлової системи — може визначити власні статичні точки `TRACE_EVENT`. Після завантаження модуля ядро автоматично створює для них повну ієрархію файлів у віртуальній файловій системі `tracefs`, підключає внутрішньоядерний механізм фільтрації, надає підтримку hist-тригерів та дозволяє програмам `eBPF` і `perf` підключатися до них без додаткової адаптації.

Нижче наведено практичний проєкт: створення модуля ядра з власною точкою трасування `sample_sensor_read`, інтеграція з інструментами `trace-cmd`, `perf` та `bpftrace`, а також розробка утиліти простору користувача для конфігурації фільтра й читання потоку даних у реальному часі.

## 1. Архітектура та правила створення заголовка подій

Для коректної роботи препроцесора C макрос `TRACE_EVENT` вимагає суворого дотримання правил багатофазного включення. Файл заголовка подій повинен вміти включатися повторно різними внутрішніми файлами ftrace, змінюючи своє значення залежно від макросів `CREATE_TRACE_POINTS` та `TRACE_HEADER_MULTI_READ`.

Створимо файл `tp_sample_events.h`:

```c
#undef TRACE_SYSTEM
#define TRACE_SYSTEM sample_subsys

#if !defined(_TP_SAMPLE_EVENTS_H) || defined(TRACE_HEADER_MULTI_READ)
#define _TP_SAMPLE_EVENTS_H

#include <linux/tracepoint.h>

TRACE_EVENT(sample_sensor_read,
    TP_PROTO(int sensor_id, int raw_value, const char *label),
    TP_ARGS(sensor_id, raw_value, label),
    TP_STRUCT__entry(
        __field(int, sensor_id)
        __field(int, raw_value)
        __string(label, label)
    ),
    TP_fast_assign(
        __entry->sensor_id = sensor_id;
        __entry->raw_value = raw_value;
        __assign_str(label, label);
    ),
    TP_printk("sensor_id=%d raw_val=%d label=%s",
              __entry->sensor_id, __entry->raw_value, __get_str(label))
);

#endif /* _TP_SAMPLE_EVENTS_H */

/* Цей розділ обов'язково розміщується ПОЗА межами блоку #ifndef _TP_SAMPLE_EVENTS_H */
#include <trace/define_trace.h>
```

### Ключові вимоги до структури заголовка

1. **Макрос `TRACE_SYSTEM`:** Визначає назву підсистеми (підкаталогу в `/sys/kernel/tracing/events/`). Перед його оголошенням обов'язково викликається директива `#undef TRACE_SYSTEM`, щоб запобігти конфліктам імен з іншими підсистемами ядра.
2. **Захист від повторного включення:** Умова `#if !defined(...) || defined(TRACE_HEADER_MULTI_READ)` дозволяє механізму ftrace включати цей файл тричі під час компіляції: для генерації C-структури запису, коду функції зворотного виклику та дескрипторів формату.
3. **Хвостовий інклуд `<trace/define_trace.h>`:** Повинен знаходитися в самому кінці файлу, строго за межами `#endif`. Саме цей заголовок керує процесом розгортання макросів ftrace.

## 2. Реалізація модуля ядра

Модуль ядра `tp_sample_mod.c` створює фоновий потік ядра (`kthread`), який періодично генерує покази віртуального сенсора та викликає автозгенеровану функцію `trace_sample_sensor_read()`.

Зверніть увагу: макрос `#define CREATE_TRACE_POINTS` повинен бути оголошений **рівно в одному** файлі вихідного коду C перед включенням `tp_sample_events.h`. Якщо цей заголовок використовується іншими файлами модуля, вони включають його без оголошення `CREATE_TRACE_POINTS`, щоб уникнути помилок лінкування дубльованих символів (multiple definition of tracepoint structures).

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kthread.h>
#include <linux/delay.h>

#define CREATE_TRACE_POINTS
#include "tp_sample_events.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("Демонстрація статичної точки TRACE_EVENT у модулі ядра");

static struct task_struct *worker_thread;

static int sensor_worker(void *data) {
    int counter = 0;
    while (!kthread_should_stop()) {
        int simulated_value = (counter * 7) % 100;
        
        /* Виклик статичної точки трасування.
         * Якщо точка вимкнена у tracefs, це виконує одну інструкцію NOP.
         */
        trace_sample_sensor_read(1, simulated_value, "temp_zone_0");

        counter++;
        msleep_interruptible(200); /* Генерація 5 подій на секунду */
    }
    return 0;
}

static int __init sample_init(void) {
    pr_info("sample_tp_mod: Ініціалізація модуля\n");
    worker_thread = kthread_run(sensor_worker, NULL, "k_sensor_tp");
    if (IS_ERR(worker_thread)) {
        pr_err("sample_tp_mod: Не вдалося запустити kthread\n");
        return PTR_ERR(worker_thread);
    }
    return 0;
}

static void __exit sample_exit(void) {
    if (worker_thread) {
        kthread_stop(worker_thread);
    }
    pr_info("sample_tp_mod: Модуль успішно вивантажено\n");
}

module_init(sample_init);
module_exit(sample_exit);
```

### Складання та завантаження модуля

Створимо стандартний `Makefile` для збірки модуля зовнішнім деревом Kbuild:

```makefile
obj-m += tp_sample_mod.o
CFLAGS_tp_sample_mod.o := -I$(src)

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

default:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

Після компіляції та завантаження модуля:

```bash
make
sudo insmod tp_sample_mod.ko
```

У віртуальній файловій системі `tracefs` з'являється новий каталог із повним набором керівних файлів:
`/sys/kernel/tracing/events/sample_subsys/sample_sensor_read/`.

Перевіримо вміст згенерованого файлу формату:

```bash
cat /sys/kernel/tracing/events/sample_subsys/sample_sensor_read/format
```

Ядро автоматично виведе опис зміщень полів `sensor_id`, `raw_value` та динамічного рядка `label`, а також форматний рядок для виводу в `trace_pipe`.

## 3. Читання та фільтрація подій через системні утиліти

Оскільки створена точка трасування зареєстрована через стандартний механізм `TRACE_EVENT`, вона негайно стає доступною для всіх стандартних інструментів аналізу продуктивності Linux без необхідності написання додаткового коду.

### Використання `trace-cmd`

Утиліта `trace-cmd` дозволяє записувати події нашої точки трасування у двійковий файл з мінімальними накладними витратами на введення-виведення:

```bash
# Запис подій тривалістю 5 секунд з фільтрацією значень
sudo trace-cmd record -e sample_subsys:sample_sensor_read -f "raw_value > 50" sleep 5

# Декодування та читання зібраного звіту
trace-cmd report
```

### Використання `bpftrace`

За допомогою мови сценаріїв `bpftrace` можна підключитися до нашої точки трасування та агрегувати статистику за допомогою eBPF у реальному часі безпосередньо в просторі ядра:

```bash
sudo bpftrace -e 'tracepoint:sample_subsys:sample_sensor_read { @values = hist(args.raw_value); }'
```

Після натискання `Ctrl+C` утиліта `bpftrace` надрукує логарифмічну ASCII-гістограму розподілу значень сенсора, обчислену всередині ядра Linux без перемикання контекстів.

### Використання `perf`

Підсистема `perf` також може використовувати нашу точку як джерело подій:

```bash
sudo perf record -e sample_subsys:sample_sensor_read -a sleep 3
sudo perf script
```

## 4. Програмний контролер трасування з простору користувача

Для створення спеціалізованих агентів моніторингу та діагностики розробимо програму простору користувача, яка реалізує повний життєвий цикл керування точкою трасування:
1. Записує умовний предикат у файл `filter` (наприклад, отримувати лише ті покази сенсора, де `raw_value > 40`).
2. Активує точку трасування через запис `1` у файл `enable`.
3. Відкриває потоковий дескриптор `/sys/kernel/tracing/trace_pipe` і вичитує події в міру їхньої появи.
4. При отриманні системного сигналу завершення (`SIGINT` або `SIGTERM`) деактивує трасування та скидає встановлені фільтри.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

static volatile sig_atomic_t keep_running = 1;

static void handle_sigint(int sig) {
    (void)sig;
    keep_running = 0;
}

static int write_sysfs(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t written = write(fd, value, strlen(value));
    close(fd);
    return written >= 0 ? 0 : -1;
}

int main(void) {
    const char *event_enable = "/sys/kernel/tracing/events/sample_subsys/sample_sensor_read/enable";
    const char *event_filter = "/sys/kernel/tracing/events/sample_subsys/sample_sensor_read/filter";
    const char *trace_pipe   = "/sys/kernel/tracing/trace_pipe";

    signal(SIGINT, handle_sigint);
    signal(SIGTERM, handle_sigint);

    printf("Налаштування ftrace для власної точки трасування...\n");

    /* 1. Встановлення предикату фільтрації */
    if (write_sysfs(event_filter, "raw_value > 40") != 0) {
        fprintf(stderr, "Помилка встановлення фільтра. Чи завантажено модуль tp_sample_mod?\n");
        return 1;
    }

    /* 2. Активація точки трасування */
    if (write_sysfs(event_enable, "1") != 0) {
        fprintf(stderr, "Помилка активації точки трасування\n");
        return 1;
    }

    /* 3. Читання безперервного потоку подій */
    int pipe_fd = open(trace_pipe, O_RDONLY);
    if (pipe_fd < 0) {
        perror("Не вдалося відкрити trace_pipe (потрібні права root)");
        write_sysfs(event_enable, "0");
        return 1;
    }

    printf("Очікування подій (фільтр: raw_value > 40)... Натисніть Ctrl+C для зупинки.\n");
    char buffer[512];

    while (keep_running) {
        ssize_t bytes = read(pipe_fd, buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            printf("%s", buffer);
        } else if (bytes < 0 && errno != EINTR) {
            perror("Помилка читання з trace_pipe");
            break;
        }
    }

    /* 4. Відновлення вихідного стану системи */
    printf("\nЗупинка трасування та скидання фільтрів...\n");
    close(pipe_fd);
    write_sysfs(event_enable, "0");
    write_sysfs(event_filter, "0");

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <csignal>
#include <atomic>
#include <chrono>
#include <thread>
#include <system_error>

namespace fs = std::filesystem;

class TracepointController {
public:
    explicit TracepointController(std::string_view subsys, std::string_view event)
        : basePath_("/sys/kernel/tracing/events/" + std::string(subsys) + "/" + std::string(event)) {
        disable();
        clearFilter();
    }

    ~TracepointController() {
        try {
            disable();
            clearFilter();
        } catch (...) {
            // Запобігаємо виходу винятків з деструктора
        }
    }

    TracepointController(const TracepointController&) = delete;
    TracepointController& operator=(const TracepointController&) = delete;

    bool setFilter(std::string_view filterExpression) const {
        return writeToFile(basePath_ / "filter", filterExpression);
    }

    bool enable() const {
        return writeToFile(basePath_ / "enable", "1");
    }

    bool disable() const noexcept {
        std::error_code ec;
        return writeToFileNoExcept(basePath_ / "enable", "0", ec);
    }

    bool clearFilter() const noexcept {
        std::error_code ec;
        return writeToFileNoExcept(basePath_ / "filter", "0", ec);
    }

private:
    fs::path basePath_;

    static bool writeToFile(const fs::path& path, std::string_view content) {
        std::ofstream file(path);
        if (!file.is_open()) {
            std::cerr << "Не вдалося записати у файл: " << path << '\n';
            return false;
        }
        file << content;
        return file.good();
    }

    static bool writeToFileNoExcept(const fs::path& path, std::string_view content, std::error_code& ec) noexcept {
        std::ofstream file(path);
        if (!file.is_open()) {
            return false;
        }
        file << content;
        return file.good();
    }
};

static std::atomic<bool> g_running{true};

void sigHandler(int) {
    g_running = false;
}

int main() {
    std::signal(SIGINT, sigHandler);
    std::signal(SIGTERM, sigHandler);

    TracepointController controller("sample_subsys", "sample_sensor_read");

    std::cout << "Налаштування ftrace (C++ RAII Controller)...\n";
    if (!controller.setFilter("raw_value > 40")) {
        std::cerr << "Переконайтеся, що модуль ядра tp_sample_mod завантажено.\n";
        return 1;
    }

    if (!controller.enable()) {
        std::cerr << "Не вдалося активувати подію.\n";
        return 1;
    }

    std::cout << "Читання /sys/kernel/tracing/trace_pipe (Ctrl+C для виходу)...\n";
    std::ifstream pipe("/sys/kernel/tracing/trace_pipe");
    if (!pipe.is_open()) {
        std::cerr << "Помилка відкриття trace_pipe (потрібні права root).\n";
        return 1;
    }

    std::string line;
    while (g_running && std::getline(pipe, line)) {
        std::cout << line << '\n';
    }

    std::cout << "\nЗавершення роботи. Автоматичне скидання налаштувань контролера.\n";
    return 0;
}
```
:::

## 5. Безпека життєвого циклу, конкурентність та типові помилки

Під час розробки модулів із точками трасування для багатопроцесорних систем необхідно враховувати тонкощі роботи підсистеми синхронізації ядра:

1. **Конкурентність виконання:** Функція `trace_sample_sensor_read()` може одночасно викликатися на десятках ядер процесора без використання блокувань. Кільцевий буфер ftrace використовує per-CPU буфери з атомарними покажчиками, що повністю усуває міжпроцесорне суперництво (cache-line bouncing) між різними ядрами CPU.
2. **Порядок вивантаження модуля:** Перед вивантаженням модуля командою `rmmod` ядро повинно переконатися, що жоден процесор не виконує функцію проби. Ядро автоматично викликає внутрішній хук `tracepoint_synchronize_unregister()`, який блокує процес вивантаження до завершення всіх активних критичних секцій RCU на всіх ядрах.
3. **Помилка компіляції `undefined reference to __tracepoint_...`:** Виникає, якщо в жодному `.c` файлі модуля не було оголошено `#define CREATE_TRACE_POINTS` перед включенням заголовка подій.
4. **Помилка компіляції `multiple definition of __tracepoint_...`:** Виникає, якщо макрос `#define CREATE_TRACE_POINTS` випадково оголошено у двох або більше `.c` файлах одного модуля.
5. **Залишковий стан фільтрів:** Якщо діагностична програма аварійно завершує роботу (наприклад, через сигнал `SIGKILL`), фільтри у `tracefs` залишаються активними. Рекомендується завжди перевіряти стан файлу `filter` перед початком нової діагностичної сесії або використовувати RAII-обгортки.
