# ⚙️ Проєкт: Створення монітора безпеки процесів на eBPF та libbpf

Цей проєкт демонструє розробку повноцінного монітора безпеки процесів на базі eBPF та бібліотеки `libbpf`. Програма перехоплює системний виклик `execve` на вході в ядро Linux, вилучає повний контекст виконання (PID, PPID, UID, GID, назву команди та шлях до бінарного файла) й надсилає його через BPF Ring Buffer у демон простору користувача.

## 1. Архітектура монітора та джерела даних

Монітор складається з двох частин: BPF-програми, яка завантажується у простір ядра, та програми спостереження у просторі користувача (доступної у двох варіантах — C та C++20).

Для перехоплення обрано статичну точку трасування `tp/syscalls/sys_enter_execve`. На відміну від динамічних `kprobes`, tracepoint надає стабільне ABI аргументів системного виклику незалежно від версії ядра Linux. 

Контекст події передається через мапу типу `BPF_MAP_TYPE_RINGBUF`. Цей механізм забезпечує передачу даних із нульовим копіюванням у спільну пам'ять (memory-mapped region) та сповіщення демона користувача через виклик `epoll_wait()`.

---

## 2. BPF-програма ядра (`exec_monitor.bpf.c`)

BPF-код використовує метадані BTF (BPF Type Format) через заголовок `vmlinux.h` та макроси CO-RE (Compile Once – Run Everywhere) для забезпечення сумісності з різними дистрибутивами.

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_FILENAME_LEN 256
#define TASK_COMM_LEN 16

// Структура події аудиту, що передається у простір користувача
struct exec_event {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 gid;
    char comm[TASK_COMM_LEN];
    char filename[MAX_FILENAME_LEN];
};

// Оголошення мапи Ring Buffer на 256 КБ
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

// Tracepoint перехоплення входження у sys_enter_execve
SEC("tp/syscalls/sys_enter_execve")
int trace_execve(struct trace_event_raw_sys_enter *ctx)
{
    struct exec_event *event;
    struct task_struct *task;
    const char *filename_ptr;

    // 1. Зарезервувати ділянку пам'яті у Ring Buffer
    event = bpf_ringbuf_reserve(&rb, sizeof(*event), 0);
    if (!event) {
        // Якщо кільцевий буфер переповнений, відкидаємо подію
        return 0;
    }

    // 2. Зчитати ідентифікатори PID (tgid) та TID (pid)
    u64 pid_tgid = bpf_get_current_pid_tgid();
    event->pid = pid_tgid >> 32;

    // 3. Зчитати ідентифікатори UID та GID
    u64 uid_gid = bpf_get_current_uid_gid();
    event->uid = (u32)uid_gid;
    event->gid = uid_gid >> 32;

    // 4. Отримати вказівник на структуру task_struct поточного процесу
    task = (struct task_struct *)bpf_get_current_task();

    // 5. Витягти PPID батьківського процесу через CO-RE читання task->real_parent->tgid
    // Використання real_parent ізолює від тимчасової зміни батька при ptrace-налагодженні
    event->ppid = BPF_CORE_READ(task, real_parent, tgid);

    // 6. Зчитати коротку назву виконуваного файла (comm)
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    // 7. Зчитати шлях до виконуваного файла з аргументів системного виклику (args[0])
    filename_ptr = (const char *)ctx->args[0];
    bpf_probe_read_user_str(&event->filename, sizeof(event->filename), filename_ptr);

    // 8. Зафіксувати та відправити подію у Ring Buffer
    bpf_ringbuf_submit(event, 0);
    return 0;
}

char _license[] SEC("license") = "GPL";
```

### Покроковий розбір BPF-коду

1. **Вирівнювання структури `exec_event`:** Усі поля у структурі `exec_event` вирівняні за 32-бітними межами. Це гарантує відсутність прихованих заповнювальних байтів (padding) і запобігає відмовам JIT-компілятора на архітектурах із суворими вимогами до вирівнювання адресації (наприклад, ARM64).
2. **Резервування у Ring Buffer:** `bpf_ringbuf_reserve` виділяє пам'ять безпосередньо у спільному буфері. Перевірка `if (!event)` є обов'язковою вимогою верифікатора: розімкнення `event` без перевірки на `NULL` призведе до відмови завантаження програми верифікатором ядра.
3. **Читання ідентифікаторів процесу:** Допоміжні функції `bpf_get_current_pid_tgid()` та `bpf_get_current_uid_gid()` повертають упаковані 64-бітні значення. Зміщення бітів `>> 32` дозволяє витягти реальний PID (tgid у термінах ядра) та GID.
4. **CO-RE розімкнення структури `task_struct`:** Макрос `BPF_CORE_READ(task, real_parent, tgid)` розгортається у безпечний ланцюжок релокацій `bpf_core_read()`. Якщо у майбутніх версіях ядра поле `tgid` зміститься всередині `task_struct`, бібліотека `libbpf` автоматично скоригує зміщення інструкції під час завантаження.
5. **Безопечне зчитування рядка з пам'яті користувача:** Функція `bpf_probe_read_user_str` зчитує шлях до файла за вказівником `ctx->args[0]`. Вона зупиняється при досягненні нульового байта або перевищенні ліміту `MAX_FILENAME_LEN`, гарантуючи відсутність читання за межами виділеної сторінки пам'яті.

---

## 3. Завантажувачі у просторі користувача

Демон простору користувача завантажує зкомпільований BPF-байткод, підключає його до відповідного tracepoint ядра та здійснює обробку подій у циклі `epoll_wait()`.

:::tabs
@tab C (libbpf)
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "exec_monitor.skel.h"

static volatile bool exiting = false;

// Обробник сигналів для коректного завершення роботи
static void sig_handler(int sig)
{
    exiting = true;
}

// Функція обробки події, яка викликається бібліотекою libbpf при отриманні даних з Ring Buffer
static int handle_event(void *ctx, void *data, size_t data_sz)
{
    const struct exec_event *e = data;
    printf("[EXEC] PID: %6d | PPID: %6d | UID: %4d | GID: %4d | COMM: %-16s | PATH: %s\n",
           e->pid, e->ppid, e->uid, e->gid, e->comm, e->filename);
    return 0;
}

int main(int argc, char **argv)
{
    struct exec_monitor_bpf *skel;
    struct ring_buffer *rb = NULL;
    int err;

    // Реєстрація обробників сигналів SIGINT та SIGTERM
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    // 1. Відкриття та завантаження BPF-скелета у ядро
    skel = exec_monitor_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка: не вдалося завантажити BPF-скелет\n");
        return 1;
    }

    // 2. Прив'язка BPF-програми до точки tracepoint sys_enter_execve
    err = exec_monitor_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Помилка: не вдалося прив'язати BPF-програму: %d\n", err);
        goto cleanup;
    }

    // 3. Створення об'єкта Ring Buffer із вказівником на колбек handle_event
    rb = ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка: не вдалося створити Ring Buffer\n");
        goto cleanup;
    }

    printf("eBPF Process Monitor (C) успішно запущено. Натисніть Ctrl-C для виходу...\n");

    // 4. Головний цикл зчитування подій з таймаутом 100 мс
    while (!exiting) {
        err = ring_buffer__poll(rb, 100);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка читання Ring Buffer: %d\n", err);
            break;
        }
    }

cleanup:
    // Звільнення ресурсів у зворотному порядку
    ring_buffer__free(rb);
    exec_monitor_bpf__destroy(skel);
    printf("\nМонітор зупинено, ресурси звільнено.\n");
    return 0;
}
```
@tab C++ (libbpf C++20 RAII)
```cpp
#include <iostream>
#include <memory>
#include <atomic>
#include <csignal>
#include <string_view>
#include <stdexcept>
#include <bpf/libbpf.h>
#include "exec_monitor.skel.h"

namespace {
// Атомарний прапор завершення для безпечної роботи між потоками та обробником сигналів
std::atomic<bool> exiting{false};

void signal_handler(int) {
    exiting.store(true);
}

// RAII-обгортка для керування життєвим циклом BPF-скелета
class bpf_monitor_skeleton {
public:
    bpf_monitor_skeleton() {
        skel_.reset(exec_monitor_bpf__open_and_load());
        if (!skel_) {
            throw std::runtime_error("Не вдалося завантажити BPF-скелет у ядро");
        }
        if (exec_monitor_bpf__attach(skel_.get()) != 0) {
            throw std::runtime_error("Не вдалося прив'язати BPF-програму до tracepoint");
        }
    }

    [[nodiscard]] int get_map_fd() const noexcept {
        return bpf_map__fd(skel_->maps.rb);
    }

private:
    struct skel_deleter {
        void operator()(exec_monitor_bpf* s) const noexcept {
            if (s) {
                exec_monitor_bpf__destroy(s);
            }
        }
    };
    std::unique_ptr<exec_monitor_bpf, skel_deleter> skel_;
};

// RAII-обгортка для керування життєвим циклом Ring Buffer
class bpf_ring_buffer {
public:
    using sample_cb = int (*)(void *ctx, void *data, size_t size);

    bpf_ring_buffer(int map_fd, sample_cb cb) {
        rb_.reset(ring_buffer__new(map_fd, cb, nullptr, nullptr));
        if (!rb_) {
            throw std::runtime_error("Не вдалося створити об'єкт Ring Buffer");
        }
    }

    void poll(int timeout_ms) {
        int err = ring_buffer__poll(rb_.get(), timeout_ms);
        if (err < 0 && err != -EINTR) {
            throw std::runtime_error("Помилка опитування Ring Buffer");
        }
    }

private:
    struct rb_deleter {
        void operator()(ring_buffer* r) const noexcept {
            if (r) {
                ring_buffer__free(r);
            }
        }
    };
    std::unique_ptr<ring_buffer, rb_deleter> rb_;
};

// C++20 колбек обробки подій з використанням std::string_view для відсутності копіювань
int handle_exec_event(void*, void* data, size_t) {
    const auto* e = static_cast<const exec_event*>(data);
    
    std::cout << "[EXEC] PID: " << e->pid 
              << " | PPID: " << e->ppid 
              << " | UID: " << e->uid 
              << " | GID: " << e->gid 
              << " | COMM: " << std::string_view(e->comm) 
              << " | PATH: " << std::string_view(e->filename) << "\n";
    return 0;
}
} // namespace

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    try {
        // Створення RAII об'єктів скелета та кільцевого буфера
        bpf_monitor_skeleton skeleton;
        bpf_ring_buffer rb(skeleton.get_map_fd(), handle_exec_event);

        std::cout << "eBPF Process Monitor (C++20 RAII) запущено. Ctrl-C для виходу...\n";

        // Головний цикл обробки podij
        while (!exiting.load(std::memory_order_relaxed)) {
            rb.poll(100);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << "\n";
        return 1;
    }

    std::cout << "Монітор коректно завершив роботу.\n";
    return 0;
}
```
:::

### Порівняння реалізацій C та C++20

- **Керування ресурсами:** У версії C звільнення об'єктів `skel` та `rb` виконується через явні виклики у секції `cleanup:`. У версії C++20 використано паттерн RAII: деструктори `std::unique_ptr` автоматично гарантують звільнення ресурсів ядра та пам'яті навіть при виникненні винятків (`std::runtime_error`).
- **Атомарність сигналів:** У C++ використано `std::atomic<bool>` із relaxed-впорядкуванням пам'яті, що робить перевірку умови циклу атомарно безпечною з точки зору C++ Memory Model.
- **Ефективність виводу:** Використання `std::string_view` дозволяє обертати масиви `comm` та `filename` у C++ рядкові інтерфейси без здійснення динамічного виділення пам'яті на купі (`std::string`).

---

## 4. Конвеєр збірки та інструментарій (Build Pipeline)

Для збірки та генерації автозгенерованого C-скелета використовується утиліта `bpftool` та компілятор `clang`.

```bash
# Крок 1: Дамп системних типів BTF з поточного ядра Linux у vmlinux.h
bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# Крок 2: Компiляцiя BPF-коду ядра у BPF-байткод (об'єктний файл)
# Прапор -g є обов'язковим для збереження метаданих DWARF/BTF
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c exec_monitor.bpf.c -o exec_monitor.bpf.o

# Крок 3: Генерація C-скелета (header-only файлу) за допомогою bpftool
bpftool gen skeleton exec_monitor.bpf.o > exec_monitor.skel.h

# Крок 4а: Збірка демона на мові C
gcc -O2 -g exec_monitor.c -lbpf -lelf -lz -o exec_monitor

# Крок 4б: Збірка демона на мові C++20
g++ -O2 -g -std=c++20 exec_monitor.cpp -lbpf -lelf -lz -o exec_monitor_cpp

# Крок 5: Запуск із системними привілеями CAP_BPF / root
sudo ./exec_monitor
```

---

## 5. Відлагодження та діагностика BPF-програми

При виникненні відмов під час завантаження BPF-програми основними інструментами діагностики є:

1. **Перегляд логів верифікатора BPF:** Якщо `exec_monitor_bpf__open_and_load()` повертає `NULL`, бібліотека `libbpf` виводить детальний трасувальний лог перевірки інструкцій верифікатором. Найчастішою причиною відмови є відсутність перевірки вказівників на `NULL` після `bpf_ringbuf_reserve()`.
2. **Друк налагоджувальних повідомлень (`bpf_trace_printk`):** Всередині BPF-коду можна використовувати макрос `bpf_printk("PID: %d\n", pid);`. Повідомлення зчитуються в реальному часі через відлагоджувальний псевдофайл ядра:
   ```bash
   sudo cat /sys/kernel/debug/tracing/trace_pipe
   ```
3. **Інспекція завантажених об'єктів BPF:** Утиліта `bpftool` дозволяє перевірити стан мап та завантажених програм у ядрі:
   ```bash
   # Перелік активних BPF програм
   sudo bpftool prog list
   
   # Дамп байткоду або JIT-інструкцій конкретної програми
   sudo bpftool prog dump xlated id <PROG_ID>
   ```

---

## 6. Крайові випадки та шляхи вдосконалення

Впровадження даного монітора у промислових середовищах вимагає врахування наступних крайових випадків:

- **Пропущені події при високому навантаженні:** Якщо демон простору користувача не встигає зчитувати події з `BPF Ring Buffer`, функція `bpf_ringbuf_reserve` починає повертати `NULL`. У практичних інструментах рекомендується додавати атомарний лічильник втрачених подій (Drop Counter) через мапу `BPF_MAP_TYPE_PERCPU_ARRAY`, щоб демон міг сповістити про втрату цілісності аудиту.
- **Усічення довгих шляхів:** Якщо шлях до виконуваного файла перевищує `MAX_FILENAME_LEN` (256 байт), функція `bpf_probe_read_user_str` збереже лише перші 255 символів. Для повного відновлення шляху у VFS BPF LSM-програми використовують обхід ієрархії `dentry` через макроси `BPF_CORE_READ(dentry, d_name.name)`.
- **Аналіз масиву аргументів `argv`:** Для витягування всіх аргументів командного рядка (наприклад, `-la /root`) BPF-програма повинна виконувати цикл по масиву вказівників `ctx->args[1]` за допомогою зчитування `bpf_probe_read_user()`, дотримуючись встановлених верифікатором меж циклу.
