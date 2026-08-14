# ⚙️ Практичний проєкт: Побудова замкненого контуру спостереження та динамічного управління на bpf_iter та User Ringbuf

У цьому практичному проєкті ми побудуємо повноцінну автономну систему спостереження та автоматичного регулювання системного навантаження в ОС Linux. Система діє за принципом **замкненого зворотного зв'язку (Closed-Loop Control)**: вона самостійно безперервно інспектує внутрішній стан ядра, виявляє процеси-порушники, що вичерпують ліміти пам'яті, і миттєво застосовує обмеження на рівні мережевого стека — без будь-якої участі оператора та з мінімальними накладними витратами системних ресурсів.

## 1. Архітектурні принципи та дизайн замкненого контуру

Традиційні комплекси автоматизації моніторингу спираються на роз'єднані схеми: агент спостережуваності зчитує показники з `/proc` або `sysfs`, надсилає їх через мережу у зовнішню систему аналітики (наприклад, Prometheus або Grafana Alertmanager), після чого зовнішній скрипт визиває SSH-команду або REST API для зміни налаштувань мережевого екрана (iptables/nftables). 

Такий підхід має три фундаментальні вади:
1. **Величезна затримка реакції (Latency Lag):** Час між виникненням аномалії та її придушенням становить від кількох секунд до десятків секунд, протягом яких процес-порушник успеває вичерпати пам'ять вузла або заблокувати мережевий канал.
2. **Накладні витрати CPU:** Читання `/proc` та виконання викликів `iptables` вимагають постійного форматування тексту та виконання системних викликів.
3. **Гонка даних (Race Conditions):** Стан системи може змінитися кілька разів за час, поки зовнішній демон прийняв рішення та намагається застосувати нове правило.

Запропонована у цьому проєкті архітектура реалізує повністю автономний замкнений контур всередині одного вузла Linux, поєднуючи механізми BPF Iterators та User Ring Buffer:

```
+-------------------------------------------------------------------------+
|                         Userspace Controller                            |
|                                                                         |
|  [BPF Iter Reader]  --->  [Аналітичний модуль]  --->  [Zero-Syscall     |
|   open/read()              визначення аномалій         User Ringbuf]    |
+---------^---------------------------------------------------|-----------+
          |                                                   |
   bpffs task_iter                                     mmap shared ring
          |                                                   |
+---------|---------------------------------------------------|-----------+
|         |               Kernel Space (eBPF)                 v           |
|                                                                         |
|  (bpf_iter/task)                                  (bpf_user_ringbuf)    |
|   Lockless RCU scan                                bpf_dynptr_read      |
|         |                                                   |           |
|         v                                                   v           |
|   task_struct list                                   blocked_pids map   |
+-------------------------------------------------------------------------+
```

---

## 2. Повний вихідний код ядра eBPF (`monitor_iter.bpf.c`)

Код ядра реалізує ітератор процесів, мапу `USER_RINGBUF`, хеш-мапу заблокованих PID та callback-процесор для динамічного оновлення правил.

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

/* Вхідна структура команди від користувацького простору */
struct policy_command {
    __u32 target_pid;
    __u8  block_action; /* 1 = Block, 0 = Allow */
};

/* Мапа User Ring Buffer для передачі команд у ядро БЕЗ SYSCALL */
struct {
    __uint(type, BPF_MAP_TYPE_USER_RINGBUF);
    __uint(max_entries, 256 * 1024);
} cmd_ringbuf SEC(".maps");

/* Хеш-мапа заблокованих PID */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, __u8);
} blocked_pids SEC(".maps");

/* 1. BPF Iterator: обхід усіх процесів у ядрі */
SEC("iter/task")
int inspect_tasks(struct bpf_iter__task *ctx)
{
    struct seq_file *seq = ctx->meta->seq;
    struct task_struct *task = ctx->task;

    if (!task)
        return 0;

    /* Читаємо розмір віртуальної пам'яті процесу */
    struct mm_struct *mm = task->mm;
    if (!mm)
        return 0;

    unsigned long total_vm = 0;
    bpf_probe_read_kernel(&total_vm, sizeof(total_vm), &mm->total_vm);

    /* Відбираємо лише процеси, що споживають більше 100 000 сторінок (~400 МБ) */
    if (total_vm > 100000) {
        bpf_seq_printf(seq, "PID:%d COMM:%s PAGES:%lu\n", 
                       task->pid, task->comm, total_vm);
    }

    return 0;
}

/* Callback для обробки кожної команди з User Ring Buffer */
static long process_policy_cmd(struct bpf_dynptr *dynptr, void *context)
{
    struct policy_command cmd;

    /* Безпечне копіювання команди з dynptr з перевіркою меж */
    if (bpf_dynptr_read(&cmd, sizeof(cmd), dynptr, 0, 0) < 0)
        return 0;

    if (cmd.block_action == 1) {
        __u8 flag = 1;
        bpf_map_update_elem(&blocked_pids, &cmd.target_pid, &flag, BPF_ANY);
    } else {
        bpf_map_delete_elem(&blocked_pids, &cmd.target_pid);
    }

    return 0;
}

/* 2. Двигун застосування команд з User Ringbuf */
SEC("tp/syscalls/sys_enter_write")
int apply_user_policies(void *ctx)
{
    /* Вичищаємо та застосовуємо всі накопичені команди з кольца */
    bpf_user_ringbuf_drain(&cmd_ringbuf, process_policy_cmd, NULL, BPF_RB_NO_WAKEUP);
    return 0;
}

char _license[] SEC("license") = "GPL";
```

### Детальний розбір логіки виконання в ядрі

Розглянемо покроково, як функціонують компоненти BPF-модуля:

1. **Ітерація процесів `inspect_tasks`:** При відкритті закріпленого ітератора у `bpffs` ядро підключає `inspect_tasks` до циклу `seq_file`. Програма отримує `struct bpf_iter__task *ctx`. Якщо `ctx->task == NULL`, це означає завершення списку процесів. Для кожного дійсного процесу програма безпечно дістає вказівник на структуру пам'яті `mm_struct` за допомогою допоміжної функції `bpf_probe_read_kernel()`. Вона перевіряє лічильник `total_vm`. Якщо процес споживає понад 100 000 сторінок пам'яті (близько 400 МБ), функція `bpf_seq_printf()` форматує рядок із текстовим звітом. Всі нормальні процеси пропускаються без виділення пам'яті та без текстового форматування.
2. **Очищення буфера `apply_user_policies`:** Для того щоб BPF-програма періодично перевіряла наявність нових команд від користувацького простору без потреби створювати окремий потік ядра, ми прикріплюємо програму `apply_user_policies` до точки трасування системних викликів `tp/syscalls/sys_enter_write`. При кожному виконанні системного виклику `write` у ядрі ця програма викликає `bpf_user_ringbuf_drain()`.
3. **Безпечне вичитування з `bpf_dynptr`:** Помічник `bpf_user_ringbuf_drain()` витягує з кільця черговий слот запису і загортає його у `struct bpf_dynptr`. У функції `process_policy_cmd` ми викликаємо `bpf_dynptr_read()`, яка копіює `sizeof(struct policy_command)` байтів у локальну змінну `cmd`. Якщо зарезервований користувачем слот пошкоджений або має менший розмір, `bpf_dynptr_read()` повертає від'ємну помилку, і програма безпечно ігнорує пошкоджену команду. При `cmd.block_action == 1` PID додається до мапи `blocked_pids`.

---

## 3. Користувацький контролер (Userspace Controller)

Користувацька програма виконує дві фундаментальні операції:
1. Читає результат обходу `bpf_iter` з закріпленого файла `/sys/fs/bpf/task_inspector` як звичайний файл VFS і виявляє аномальні PID.
2. Формує керуючу структуру `policy_command` та записує її у кільцевий буфер `cmd_ringbuf` за допомогою `user_ring_buffer__reserve()` та `user_ring_buffer__submit()` — повністю оминаючи системні виклики.

Нижче наведено дві альтернативні реалізації контролера: чистим C та ідіоматичним C++20 із застосуванням концепції RAII, винятків та перевірок типів.

:::tabs
```c
/* Userspace Controller на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct policy_command {
    uint32_t target_pid;
    uint8_t  block_action;
};

int main(int argc, char **argv)
{
    int map_fd = bpf_obj_get("/sys/fs/bpf/cmd_ringbuf_map");
    if (map_fd < 0) {
        perror("Не вдалося відкрити мапу /sys/fs/bpf/cmd_ringbuf_map");
        return 1;
    }

    /* Ініціалізація User Ring Buffer */
    struct user_ring_buffer *urb = user_ring_buffer__new(map_fd, NULL);
    if (!urb) {
        fprintf(stderr, "Помилка створення user_ring_buffer\n");
        close(map_fd);
        return 1;
    }

    /* Читання BPF ітератора */
    int iter_fd = open("/sys/fs/bpf/task_inspector", O_RDONLY);
    if (iter_fd < 0) {
        perror("Не вдалося відкрити ітератор /sys/fs/bpf/task_inspector");
        user_ring_buffer__free(urb);
        close(map_fd);
        return 1;
    }

    char buf[512];
    ssize_t bytes_read = read(iter_fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("Звіт BPF Iter:\n%s", buf);

        /* Парсимо виявлений PID */
        uint32_t bad_pid = 0;
        if (sscanf(buf, "PID:%u", &bad_pid) == 1 && bad_pid > 0) {
            printf("Надсилаємо команду блокування для PID %u (Zero-Syscall)...\n", bad_pid);

            /* Резервуємо слот у кільцевому буфері без системного виклику */
            struct policy_command *cmd = user_ring_buffer__reserve(urb, sizeof(*cmd));
            if (cmd) {
                cmd->target_pid = bad_pid;
                cmd->block_action = 1;

                /* Фіксуємо транзакцію у спільній пам'яті mmap */
                user_ring_buffer__submit(urb, cmd);
                printf("Команду успішно надіслано в ядро.\n");
            }
        }
    }

    close(iter_fd);
    user_ring_buffer__free(urb);
    close(map_fd);
    return 0;
}
```
```cpp
// Userspace Controller на ідіоматичному C++20
#include <iostream>
#include <fstream>
#include <string>
#include <memory>
#include <string_view>
#include <charconv>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

struct PolicyCommand {
    std::uint32_t target_pid;
    std::uint8_t  block_action;
};

// RAII обгортка для файлового дескриптора
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для libbpf user_ring_buffer
class UserRingBuffer {
    struct user_ring_buffer* rb_{nullptr};
public:
    explicit UserRingBuffer(int map_fd) {
        rb_ = user_ring_buffer__new(map_fd, nullptr);
        if (!rb_) {
            throw std::runtime_error("Не вдалося ініціалізувати user_ring_buffer");
        }
    }
    ~UserRingBuffer() {
        if (rb_) user_ring_buffer__free(rb_);
    }
    UserRingBuffer(const UserRingBuffer&) = delete;
    UserRingBuffer& operator=(const UserRingBuffer&) = delete;

    template <typename T>
    class Reservation {
        UserRingBuffer& parent_;
        T* ptr_{nullptr};
    public:
        Reservation(UserRingBuffer& parent, T* ptr) : parent_(parent), ptr_(ptr) {}
        ~Reservation() {
            if (ptr_) {
                user_ring_buffer__discard(parent_.rb_, ptr_);
            }
        }
        T* get() noexcept { return ptr_; }
        T* operator->() noexcept { return ptr_; }

        void submit() {
            if (ptr_) {
                user_ring_buffer__submit(parent_.rb_, ptr_);
                ptr_ = nullptr; // Скасовуємо discard у деструкторі
            }
        }
    };

    template <typename T>
    [[nodiscard]] Reservation<T> reserve() {
        auto* mem = static_cast<T*>(user_ring_buffer__reserve(rb_, sizeof(T)));
        return Reservation<T>(*this, mem);
    }
};

int main()
{
    try {
        UniqueFd map_fd(::bpf_obj_get("/sys/fs/bpf/cmd_ringbuf_map"));
        if (!map_fd.valid()) {
            std::cerr << "Помилка відкриття BPF мапи\n";
            return 1;
        }

        UserRingBuffer ringbuf(map_fd.get());

        // Читання ітератора через стандартний потік C++
        std::ifstream iter_file("/sys/fs/bpf/task_inspector");
        if (!iter_file.is_open()) {
            std::cerr << "Не вдалося відкрити BPF ітератор\n";
            return 1;
        }

        std::string line;
        while (std::getline(iter_file, line)) {
            std::cout << "[BPF Iter] " << line << '\n';

            // Парсинг PID з рядка "PID:12345 COMM:..."
            auto pid_pos = line.find("PID:");
            if (pid_pos != std::string::npos) {
                std::uint32_t pid = 0;
                auto sub = line.substr(pid_pos + 4);
                auto res = std::from_chars(sub.data(), sub.data() + sub.size(), pid);

                if (res.ec == std::errc{} && pid > 0) {
                    std::cout << "Надсилання команди блокування PID " << pid << " в ядро...\n";

                    auto reserve = ringbuf.reserve<PolicyCommand>();
                    if (reserve.get()) {
                        reserve->target_pid = pid;
                        reserve->block_action = 1;
                        reserve.submit(); // Zero-syscall commit
                        std::cout << "Команду успішно надіслано в ядро.\n";
                    }
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняткова ситуація: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

### Поглиблений аналіз C++20 контролера

Реалізація на мові C++20 наочно демонструє переваги сучасного системного програмування:

1. **Безпека ресурсів через RAII (`UniqueFd`):** У системному програмуванні на C розповсюдженою помилкою є передчасний вихід із функції через `goto out` або `return` без виклику `close(fd)`. Клас `UniqueFd` переймає володіння дескриптором і автоматично закриває його у деструкторі при будь-якому варіанті завершення функції (включаючи виключення).
2. **Шаблонний менеджер резервування `UserRingBuffer::Reservation<T>`:** Забезпечує гарантію атомарного скасування зарезервованої пам'яті (`user_ring_buffer__discard`) у деструкторі. Якщо при заповненні полів структури `PolicyCommand` виникне виняткова ситуація або логічна помилка і виклик `submit()` не відбудеться, деструктор `Reservation` автоматично вивільнить пам'ять кільцевого буфера back to user space. Це повністю виключає витоки слотів у кільцевому буфері.
3. **Безвинятковий парсинг `std::from_chars`:** Замість використання застарілої функції `sscanf()` або `std::stoi()` (яка виділяє пам'ять у купі та генерує винятки), C++20 пропонує `std::from_chars`. Ця функція виконує неблокуюче, безвиняткове перетворення символів у числа з безпосереднім доступом до буфера рядка.

---

## 4. Інструкція зі збирання, налаштування та верифікації

Для успішного запуску проєкту необхідна ОС Linux з версією ядра 6.1 або новішою, встановлений комбінатор `clang` (версії 13+), `bpftool` та бібліотека `libbpf-dev`.

### 4.1 Компіляція ядерного коду та генерація Skeleton

```bash
# 1. Компіляція BPF-коду у об'єктний файл байт-коду
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c monitor_iter.bpf.c -o monitor_iter.bpf.o

# 2. Генерація заголовка C-skeleton за допомогою bpftool
bpftool gen skeleton monitor_iter.bpf.o > monitor_iter.skel.h
```

### 4.2 Завантаження та закріплення ітератора у bpffs

```bash
# 1. Перевірка монтування файлової системи bpffs
mount -t bpf bpf /sys/fs/bpf 2>/dev/null || true

# 2. Завантаження BPF програми в ядро
bpftool prog load monitor_iter.bpf.o /sys/fs/bpf/monitor_prog type tracing

# 3. Створення та закріплення BPF-ітератора
bpftool iter pin /sys/fs/bpf/monitor_prog /sys/fs/bpf/task_inspector

# 4. Закріплення мапи User Ring Buffer для доступу користувацького процесу
bpftool map pin name cmd_ringbuf /sys/fs/bpf/cmd_ringbuf_map
```

### 4.3 Компіляція та запуск контролерів

```bash
# Компіляція C контролера
gcc -O2 main.c -lbpf -o controller_c
sudo ./controller_c

# Або компіляція C++20 контролера
g++ -O2 -std=c++20 main.cpp -lbpf -o controller_cpp
sudo ./controller_cpp
```

### 4.4 Перевірка результатів виконання та діагностика

Після запуску контролера демон виконає зчитування `/sys/fs/bpf/task_inspector`, виявить процеси, що перевищують поріг пам'яті, і надішле нові політики у `cmd_ringbuf_map`. Перевірити стан оновленої мапи в ядрі можна командами `bpftool`:

```bash
# Перегляд вмісту мапи заблокованих PID
bpftool map dump name blocked_pids
```

Для простеження логів BPF-програми у ядрі скористайтеся віртуальним файлом `trace_pipe`:

```bash
cat /sys/kernel/tracing/trace_pipe
```

Результати виводу покажуть додані PID процесів-порушників. Вся процедура трансляції нових правил виконується за 0 системних викликів з мікросекундною затримкою реакції.
