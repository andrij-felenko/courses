# ⚙️ Практичний проект: Трасування викликів sys_execve через Perf Event Array

У цьому практичному проекті ми побудуємо повноцінну утиліту системного аналізу та безпеки, яка перехоплюватиме системний виклик `sys_execve` у ядрі Linux. Програма збиратиме ідентифікатори процесів (PID, PPID), ім'я виконуваного файла, атрибути команди та часову мітку з високою точністю, після чого надсилатиме їх у простір користувача через `BPF_MAP_TYPE_PERF_EVENT_ARRAY`.

Цей проект наочно демонструє весь виробничий цикл розробки eBPF-застосунків: від написання ядерного зонда мовою C до створення демона спостереження простору користувача мовами C та C++ з використанням сучасного API бібліотеки `libbpf`.

---

## 1. Архітектурне проектування та взаємодія компонентів

Проект розбито на три окремих файли, кожен з яких відповідає за свою частину ланцюжка обробки подій:

1. **`execve_event.h`**: Спільна заголовочна структура даних події. Вона гарантує ідентичне розташування полів пам'яті як у 64-бітному коді ядра, так і в коді простору користувача.
2. **`execve_monitor.bpf.c`**: Системний eBPF-зонд, що виконується в ядрі Linux у контексті переривання під час спрацьовування точки інструментування `tracepoint/syscalls/sys_enter_execve`.
3. **`execve_monitor.c` / `execve_monitor.cpp`**: Демон простору користувача, який завантажує скомпільований eBPF-байткод у ядро, ініціалізує пер-CPU кільцеві буфери `perf_buffer` та забезпечує обробку подій.

```
+-----------------------------------------------------------------------+
|                             USER SPACE                                |
|  [ execve_monitor (C) ]   OR   [ ExecveTracer (C++ RAII) ]            |
|            |                               ^                          |
|            | bpf_object__load()            | perf_buffer__poll()      |
|            v                               |                          |
+-----------------------------------------------------------------------+
|                             KERNEL SPACE                              |
|  [ Tracepoint: sys_enter_execve ] ---> [ execve_monitor.bpf.c ]       |
|                                                     |                 |
|                                                     v                 |
|                                       bpf_perf_event_output()         |
|                                                     |                 |
|                                                     v                 |
|                                       [ PERF_EVENT_ARRAY Map ]        |
+-----------------------------------------------------------------------+
```

### 1.1 Детальний аналіз ланцюжка подій

Коли будь-який процес у системі виконує системний виклик `execve()` (наприклад, при виклику команди `ls` у терміналі), ядро Linux проходить такі етапи:

- **Крок 1 (Спрацьовування зонда):** Ядро передає управління eBPF-програмі `tracepoint_sys_enter_execve`.
- **Крок 2 (Збір атрибутів):** Програма зчитує PID та TGID викликом `bpf_get_current_pid_tgid()`, поточний час ядра викликом `bpf_ktime_get_ns()` та назву процесу через `bpf_get_current_comm()`.
- **Крок 3 (Запис у буфер):** Виклик `bpf_perf_event_output()` локалізує кільцевий буфер поточного процесора та записує структуру події.
- **Крок 4 (Сповіщення userspace):** Якщо кількість подій досягла порогу пробудження, підсистема `perf` додає файловий дескриптор в `epoll`.
- **Крок 5 (Обробка демоном):** Демон користувача прокидається у виклику `perf_buffer__poll()`, зчитує дані з shared memory і викликає обробник `handle_event`.

---

## 2. Спільна структура даних (execve_event.h)

Спільна структура події вирівняна за межами 8 байт для забезпечення ідентичного розташування полів у пам'яті як у 64-бітному коді ядра, так і у коді простору користувача.

```c
#ifndef __EXECVE_EVENT_H
#define __EXECVE_EVENT_H

#define TASK_COMM_LEN 16

struct execve_event {
    unsigned int pid;           /* Ідентифікатор нового процесу (PID) */
    unsigned int ppid;          /* Ідентифікатор батьківського процесу (PPID) */
    unsigned long long boot_time_ns; /* Часова мітка від старту системи у наносекундах */
    char comm[TASK_COMM_LEN];   /* Скорочена назва виконуваного файла */
};

#endif /* __EXECVE_EVENT_H */
```

Обгрунтування вибору полів структури:
- **`pid`**: Беззнакове 32-бітне ціле число, що зберігає ідентифікатор створеного процесу.
- **`ppid`**: Ідентифікатор батьківського процесу, який ініціював виклик `execve`.
- **`boot_time_ns`**: 64-бітне число, що зберігає монотонний час ядра з моменту завантаження системи (`CLOCK_MONOTONIC`).
- **`comm`**: Масив із 16 символів (`TASK_COMM_LEN`), куди ядро копіює назву виконуваного файлу процесу.

---

## 3. Ядерна програма eBPF (execve_monitor.bpf.c)

eBPF-програма компілюється у цільову архітектуру `bpf` за допомогою Clang/LLVM і завантажується у ядро під час старту демона.

```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "execve_event.h"

/* Оголошення карти BPF_MAP_TYPE_PERF_EVENT_ARRAY */
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} events SEC(".maps");

SEC("tracepoint/syscalls/sys_enter_execve")
int tracepoint_sys_enter_execve(void *ctx)
{
    struct execve_event event = {};
    __u64 pid_tgid = bpf_get_current_pid_tgid();

    /* Витягуємо PID (старші 32 біти) та TGID */
    event.pid = (__u32)(pid_tgid >> 32);
    event.ppid = 0; /* У повноцінних проектах ppid витягують з task_struct */
    event.boot_time_ns = bpf_ktime_get_ns();
    
    /* Отримуємо назву поточного процесу */
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    /* Запис у кільцевий буфер поточного процесора */
    long err = bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    if (err) {
        /* При від'ємному значення err запис не вдався (наприклад, ENOSPC при переповненні) */
    }

    return 0;
}

char _license[] SEC("license") = "GPL";
```

### Деталі роботи ядерного коду:

1. **`SEC("tracepoint/syscalls/sys_enter_execve")`**: Макрос секції вказує `libbpf` автоматично визначити тип програми як `BPF_PROG_TYPE_TRACEPOINT` і прив'язати її до точної точки входу системного виклику `execve`.
2. **`bpf_get_current_pid_tgid()`**: Системний хелпер eBPF повертає 64-бітне число: старші 32 біти містять Process ID у просторі імен ядер (PID), а молодші 32 біти — Thread Group ID (TGID).
3. **`bpf_ktime_get_ns()`**: Повертає значення монотонного годинника ядра в наносекундах від моменту завантаження операційної системи.
4. **`bpf_perf_event_output()`**: Здійснює атомарний запис вирівняної структури `event` у буфер `perf` поточного логічного ядра CPU.

---

## 4. Демон простору користувача (Userspace Consumer)

Нижче наведено реалізацію демона для зчитування подій з кільцевих буферів. Реалізацію виконано двома мовами — чистою мовою C та ідіоматичною мовою C++ (із застосуванням концепції RAII, розумних вказівників `std::unique_ptr` та обробки винятків).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "execve_event.h"

static volatile bool keep_running = true;

static void sig_handler(int sig)
{
    (void)sig;
    keep_running = false;
}

/* Callback для обробки звичайних подій */
static void handle_event(void *ctx, int cpu, void *data, __u32 data_sz)
{
    (void)ctx;
    (void)data_sz;
    const struct execve_event *e = (const struct execve_event *)data;
    printf("[CPU %2d] TIME: %12llu ns | PID: %6u | COMM: %s\n",
           cpu, e->boot_time_ns, e->pid, e->comm);
}

/* Callback для обробки втрачених подій при переповненні */
static void handle_lost_events(void *ctx, int cpu, __u64 lost_cnt)
{
    (void)ctx;
    fprintf(stderr, "УВАГА: Втрачено %llu подій на CPU %d!\n", lost_cnt, cpu);
}

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    struct bpf_object *obj = NULL;
    struct perf_buffer *pb = NULL;
    int map_fd, err;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* Завантажуємо eBPF об'єкт з файла */
    obj = bpf_object__open_file("execve_monitor.bpf.o", NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "Помилка відкриття BPF об'єкта execve_monitor.bpf.o\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка завантаження BPF програми у ядро: %d\n", err);
        bpf_object__close(obj);
        return 1;
    }

    map_fd = bpf_object__find_map_fd_by_name(obj, "events");
    if (map_fd < 0) {
        fprintf(stderr, "Не знайдено карту 'events'\n");
        bpf_object__close(obj);
        return 1;
    }

    /* Створення perf_buffer: 8 сторінок пам'яті (32 КБ) на кожен CPU */
    pb = perf_buffer__new(map_fd, 8, handle_event, handle_lost_events, NULL, NULL);
    if (libbpf_get_error(pb)) {
        fprintf(stderr, "Помилка створення perf_buffer\n");
        bpf_object__close(obj);
        return 1;
    }

    printf("Трасування викликів execve успішно запущено. Натисніть Ctrl+C для виходу.\n");

    while (keep_running) {
        err = perf_buffer__poll(pb, 100);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка опитування perf buffer: %d\n", err);
            break;
        }
    }

    printf("\nЗавершення роботи, очищення ресурсів...\n");
    perf_buffer__free(pb);
    bpf_object__close(obj);

    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <csignal>
#include <atomic>
#include <string_view>
#include <stdexcept>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "execve_event.h"

namespace {
std::atomic<bool> keep_running{true};

void sig_handler(int) {
    keep_running.store(false);
}

// RAII обгортка для BPF об'єкта
struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const noexcept {
        if (obj) bpf_object__close(obj);
    }
};
using UniqueBpfObject = std::unique_ptr<bpf_object, BpfObjectDeleter>;

// RAII обгортка для Perf Buffer
struct PerfBufferDeleter {
    void operator()(perf_buffer* pb) const noexcept {
        if (pb) perf_buffer__free(pb);
    }
};
using UniquePerfBuffer = std::unique_ptr<perf_buffer, PerfBufferDeleter>;
} // namespace

class ExecveTracer {
public:
    explicit ExecveTracer(std::string_view bpf_obj_path) {
        bpf_object* raw_obj = bpf_object__open_file(bpf_obj_path.data(), nullptr);
        if (libbpf_get_error(raw_obj)) {
            throw std::runtime_error("Не вдалося відкрити BPF об'єкт з файла " + std::string(bpf_obj_path));
        }
        bpf_obj_.reset(raw_obj);

        if (bpf_object__load(bpf_obj_.get()) != 0) {
            throw std::runtime_error("Не вдалося завантажити BPF програму у ядро Linux");
        }

        int map_fd = bpf_object__find_map_fd_by_name(bpf_obj_.get(), "events");
        if (map_fd < 0) {
            throw std::runtime_error("Карту 'events' не знайдено в завантаженому BPF об'єкті");
        }

        perf_buffer* raw_pb = perf_buffer__new(
            map_fd, 8,
            &ExecveTracer::on_sample,
            &ExecveTracer::on_lost,
            this, nullptr
        );

        if (libbpf_get_error(raw_pb)) {
            throw std::runtime_error("Помилка ініціалізації perf_buffer у C++");
        }
        pb_.reset(raw_pb);
    }

    void run() {
        std::cout << "Трасування викликів execve запущено (C++ RAII). Натисніть Ctrl+C для виходу.\n";
        while (keep_running.load()) {
            int err = perf_buffer__poll(pb_.get(), 100);
            if (err < 0 && err != -EINTR) {
                std::cerr << "Помилка опитування perf_buffer__poll: " << err << '\n';
                break;
            }
        }
    }

private:
    static void on_sample(void* ctx, int cpu, void* data, __u32 size) noexcept {
        (void)ctx;
        (void)size;
        const auto* event = static_cast<const execve_event*>(data);
        std::cout << "[CPU " << cpu << "] TIME: " << event->boot_time_ns
                  << " ns | PID: " << event->pid
                  << " | COMM: " << event->comm << '\n';
    }

    static void on_lost(void* ctx, int cpu, __u64 lost_cnt) noexcept {
        (void)ctx;
        std::cerr << "УВАГА: Втрачено " << lost_cnt << " подій на CPU " << cpu << '\n';
    }

    UniqueBpfObject bpf_obj_;
    UniquePerfBuffer pb_;
};

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    try {
        ExecveTracer tracer("execve_monitor.bpf.o");
        tracer.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    std::cout << "Програму успішно завершено.\n";
    return 0;
}
```
:::

---

## 5. Порівняльний аналіз реалізацій C та C++

Наведена вище програма демонструє відмінності між підходами низькорівневого C-програмування та ідіоматичного C++:

1. **Управління ресурсами (Resource Lifetime Management):**
   - **У коді C:** Звільнення об'єктів `bpf_object` та `perf_buffer` виконується вручну наприкінці функції `main()` або у гілках обробки помилок за допомогою викликів `bpf_object__close()` та `perf_buffer__free()`.
   - **У коді C++:** Застосовано паттерн RAII (Resource Acquisition Is Initialization). Обгортки `UniqueBpfObject` та `UniquePerfBuffer` гарантують автоматичне звільнення системних ресурсів ядра та `mmap`-областей при виході з області видимості, навіть якщо виникне виняток `std::exception`.

2. **Беспомилковість та обробка сигналів (Signal Safety):**
   - В обох реалізаціях сигнал переривання `SIGINT` (Ctrl+C) обробляється атомарно прапорцем `std::atomic<bool> keep_running`, що гарантує коректне виходження з циклу опитування `perf_buffer__poll()` без витоків пам'яті.

---

## 6. Інструкції збирання, компіляції та перевірки

Для успішного збирання проекту в системі мають бути встановлені інструменти `clang`, `llvm`, `gcc`/`g++` та бібліотека `libbpf-dev`.

### 6.1 Компіляція eBPF-байткоду

Компіляція ядерного коду здійснюється компілятором Clang із вказівкою цільової архітектури BPF:

```bash
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c execve_monitor.bpf.c -o execve_monitor.bpf.o
```

### 6.2 Компіляція демонів користувача

- **Компіляція C-демона:**
```bash
gcc -O2 -Wall execve_monitor.c -lbpf -o execve_monitor
```

- **Компіляція C++-демона (C++20):**
```bash
g++ -O2 -Wall -std=c++20 execve_monitor.cpp -lbpf -o execve_monitor_cpp
```

### 6.3 Перевірка карти за допомогою bpftool

Після запуску демона утиліта **`bpftool`** дозволяє інспектувати створену карту у ядрі:

```bash
sudo bpftool map show name events
```

Приклад виведення bpftool:
```text
12: perf_event_array  name events  flags 0x0
    key 4B  value 4B  max_entries 8  memlock 4096B
    btf_id 24
```

### 6.4 Запуск та аналіз виведення

Запустіть зібраний демон з привілеями суперкористувача `root`:

```bash
sudo ./execve_monitor_cpp
```

У сусідньому терміналі виконайте декілька команд (наприклад, `ls`, `whoami`, `ps aux`). Демон моніторингу миттєво виведе спіймані події запусків процесів:

```text
Трасування викликів execve запущено (C++ RAII). Натисніть Ctrl+C для виходу.
[CPU  2] TIME: 1452394012849 ns | PID:  14205 | COMM: ls
[CPU  0] TIME: 1452399120401 ns | PID:  14206 | COMM: whoami
[CPU  3] TIME: 1452402941102 ns | PID:  14207 | COMM: ps
```
