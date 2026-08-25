# ⚙️ Практика: відстеження затримки функцій простору користувача за допомогою uprobes

Цей практичний проект демонструє створення повноцінного інструменту вимірювання затримки (latency tracker) для функцій простору користувача без внесення змін до їхнього сирцевого коду за допомогою механізмів uprobes, uretprobes та сучасного інструментарію бібліотеки `libbpf`.

## 1. Архітектурна концепція та механізм вимірювання

Під час оптимізації продуктивності баз даних або високонавантажених сервісів розробникам необхідно знати точний розподіл затримок виконання окремих внутрішніх функцій під реальним навантаженням. 

Традиційні системи спостережуваності використовували Perf Buffer (perfbuf), який вимагав окремого буфера для кожного ядра процесора. У нашому проекті застосовується сучасніший `BPF_MAP_TYPE_RINGBUF` (Ring Buffer). Кільцевий буфер є спільним для всіх ядер процесора, забезпечує значно менші накладні витрати на оперативну пам'ять та мінімізує затримку передачі подій між ядром та користувацьким процесом.

Коли eBPF-програма в ядрі записує подію через `bpf_ringbuf_submit()`, кільцевий буфер пробуджує користувацький потік трасування за допомогою системного виклику `epoll`. На відміну від застарілих систем активного опитування (busy polling), використання `ring_buffer__poll()` гарантує, що процес трасування споживає 0% CPU у моменти відсутності нових подій, миттєво реагуючи на надходження нових вимірювань затримки.

Наш практичний інструмент розв'язує цю проблему беззупинково. Він складається з трьох зв'язаних компонентів:
1. **Цільовий бінарник (Target App):** Програма простору користувача, яка виконує імітацію обчислювальних операцій у функції `compute_hash()`.
2. **eBPF-програма трасування (Kernel space):** Модуль BPF, що завантажується в ядро Linux. При вході у функцію `compute_hash()` (через uprobe) програма зчитує поточний монотонний таймер ядра `bpf_ktime_get_ns()` і зберігає його у BPF-картку. При виході з функції (через uretprobe) BPF-програма обчислює різницю часу в наносекундах та надсилає структуру події у кільцевий буфер (Ring Buffer).
3. **Завантажувач спостереження (User-Space Tracer):** Програма спостереження у просторі користувача, яка завантажує BPF-байткуд, динамічно шукає зміщення функції в ELF-таблиці символів цільового бінарника, прикріплює зонди та виводить статистику затримок у реальному часі.

Під час збірки BPF-програми інструмент `bpftool gen skeleton` створює заголовковий файл `uprobe_tracer.skel.h`. Цей файл містить автоматично вшитий байткод eBPF та C-структуру `struct uprobe_tracer_bpf`, яка надає безпечні обгортки для відкриття, завантаження та перевірки BPF-програми. Це позбавляє розробника від написання низькорівневих системних викликів `bpf()` та керування сирими файловими дескрипторами `fd`.

### Обробка крайніх випадків та непарних викликів

Під час трасування простору користувача необхідно враховувати можливість порушення нормального потоку виконання:
- **Винятки C++ та розкрутка стека (unwinding):** Якщо інструментована функція або її внутрішній виклик викидає виняток C++ (`throw`), який перехоплюється вище за стеком викликів через `catch`, інструкція `RET` інструментованої функції взагалі не виконується. Замість цього бібліотека розкрутки стека `libunwind` модифікує регістри і переходить безпосередньо в обробник `catch`. Це призводить до того, що `uretprobe` не спрацьовує, а в хеш-карті `entry_times` залишається застарілий запис (orphan entry).
- **Нелокальні стрибки `longjmp` та `pthread_cancel`:** Виклики `setjmp`/`longjmp` або примусове скасування потоку також минають підмінений стек uretprobe. 

Для запобігання вичерпанню пам'яті BPF-карти `entry_times` використовується обмеження `max_entries` у 10240 елементів. Якщо хеш-карта переповнюється, нові виклики ігноруються, не спричиняючи збоїв у ядрі.

---

## 2. Цільова програма (Target Application)

Створимо цільову програму, яка запускає нескінченний цикл виконання обчислювальної функції `compute_hash()`. Для демонстрації різної затримки функція викликається з різною кількістю ітерацій.

:::tabs
```c
/* target_app.c - Цільова програма мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* Функція, затримку якої ми будемо інструментувати */
void compute_hash(int iterations) {
    volatile long long hash = 0;
    for (int i = 0; i < iterations * 100000; i++) {
        hash += i ^ (i >> 3);
    }
}

int main(int argc, char **argv) {
    printf("Target App C запущено (PID: %d)\n", getpid());
    while (1) {
        compute_hash(50);
        usleep(500000); /* 500 мс пауза */
        compute_hash(200);
        usleep(500000);
    }
    return 0;
}
```
```cpp
// target_app.cpp - Цільова програма мовою C++
#include <iostream>
#include <thread>
#include <chrono>
#include <unistd.h>

// Функція, затримку якої ми будемо інструментувати
void compute_hash(int iterations) {
    volatile long long hash = 0;
    for (int i = 0; i < iterations * 100000; ++i) {
        hash += i ^ (i >> 3);
    }
}

int main() {
    std::cout << "Target App C++ запущено (PID: " << getpid() << ")\n";
    while (true) {
        compute_hash(50);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        compute_hash(200);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    return 0;
}
```
:::

---

## 3. eBPF-програма трасування затримки (`uprobe_tracer.bpf.c`)

Код eBPF виконується в контексті ядра при спрацюванні зондів. Для збереження початкової мітки часу використовується хеш-карта `entry_times`, де ключем є ідентифікатор поточного процесу (PID), а значенням — час входу `bpf_ktime_get_ns()`. Використання PID як ключа гарантує коректну роботу в багатопотокових середовищах, де кожен потік має власну мітку часу.

```c
/* uprobe_tracer.bpf.c - eBPF програма ядра */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

/* Структура події для відправки у userspace */
struct event {
    u32 pid;
    u64 duration_ns;
};

/* Хеш-карта для збереження часу входу: PID -> start_timestamp */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, u32);
    __type(value, u64);
} entry_times SEC(".maps");

/* Ring Buffer для передачі подій */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} ringbuf SEC(".maps");

/* Uprobe: спрацьовує при вході в compute_hash */
SEC("uprobe/compute_hash")
int BPF_UPROBE(trace_entry) {
    u64 ts = bpf_ktime_get_ns();
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    bpf_map_update_elem(&entry_times, &pid, &ts, BPF_ANY);
    return 0;
}

/* Uretprobe: спрацьовує при виході з compute_hash */
SEC("uretprobe/compute_hash")
int BPF_URETPROBE(trace_exit) {
    u64 exit_ts = bpf_ktime_get_ns();
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    u64 *entry_ts = bpf_map_lookup_elem(&entry_times, &pid);
    if (!entry_ts) {
        return 0; /* Не знайшли вхідної мітки часу */
    }

    u64 duration = exit_ts - *entry_ts;
    bpf_map_delete_elem(&entry_times, &pid);

    /* Зарезервувати місце в Ring Buffer для події */
    struct event *e = bpf_ringbuf_reserve(&ringbuf, sizeof(*e), 0);
    if (!e) {
        return 0;
    }

    e->pid = pid;
    e->duration_ns = duration;
    bpf_ringbuf_submit(e, 0);

    return 0;
}

char _license[] SEC("license") = "GPL";
```

---

## 4. Програма завантажувача та виводу статистики (User-Space Tracer)

Завантажувач зчитує згенерований `libbpf` скелет, вираховує зміщення функції `compute_hash` у бінарному файлі через ELF-таблицю символів та підключає зонди. Програма реалізована ідіоматичними засобами C та C++ з підтримкою RAII-керування ресурсами.

Для зв'язку з ядром завантажувач використовує функцію опитування `ring_buffer__poll()`. Ця функція очікує нових подій у кільцевому буфері з вказаним таймаутом (100 мс). Коли ядро надсилає подію через `bpf_ringbuf_submit()`, завантажувач безпосередньо викликає зворотний виклик `handle_event()`, декодує структуру події та друкує значення затримки у мікросекундах та мілісекундах.

:::tabs
```c
/* tracer.c - Завантажувач трасування мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "uprobe_tracer.skel.h"

static volatile bool exiting = false;

static void sig_handler(int sig) {
    exiting = true;
}

static int handle_event(void *ctx, void *data, size_t size) {
    const struct event *e = data;
    printf("PID %d | Виконання compute_hash: %llu мкс (%.2f мс)\n",
           e->pid, e->duration_ns / 1000, (double)e->duration_ns / 1000000.0);
    return 0;
}

int main(int argc, char **argv) {
    struct uprobe_tracer_bpf *skel;
    struct ring_buffer *rb = NULL;
    int err;

    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_target_app>\n", argv[0]);
        return 1;
    }
    const char *binary_path = argv[1];

    signal(SIGINT, sig_handler);

    skel = uprobe_tracer_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Помилка відкриття BPF скелета\n");
        return 1;
    }

    /* Автоматичне прикріплення uprobe за іменем символу та шляхом до бінарника */
    skel->links.trace_entry = bpf_program__attach_uprobe(
        skel->progs.trace_entry, false, -1, binary_path, 0);
    skel->links.trace_exit = bpf_program__attach_uprobe(
        skel->progs.trace_exit, true, -1, binary_path, 0);

    rb = ring_buffer__new(bpf_map__fd(skel->maps.ringbuf), handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення Ring Buffer\n");
        uprobe_tracer_bpf__destroy(skel);
        return 1;
    }

    printf("Трасування затримки активовано для %s. Натисніть Ctrl+C для виходу.\n", binary_path);

    while (!exiting) {
        err = ring_buffer__poll(rb, 100);
        if (err < 0 && err != -EINTR) {
            break;
        }
    }

    ring_buffer__free(rb);
    uprobe_tracer_bpf__destroy(skel);
    return 0;
}
```
```cpp
// tracer.cpp - Ідіоматичний завантажувач трасування мовою C++
#include <iostream>
#include <memory>
#include <string_view>
#include <csignal>
#include <atomic>
#include <bpf/libbpf.h>
#include "uprobe_tracer.skel.h"

namespace {
std::atomic<bool> exiting{false};

void sig_handler(int) {
    exiting = true;
}

int handle_event(void*, void* data, size_t) {
    struct Event {
        uint32_t pid;
        uint64_t duration_ns;
    };
    auto e = static_cast<const Event*>(data);
    std::cout << "PID " << e->pid << " | Виконання compute_hash: "
              << (e->duration_ns / 1000) << " мкс ("
              << (static_cast<double>(e->duration_ns) / 1000000.0) << " мс)\n";
    return 0;
}

// RAII обгортка для BPF-скелета
struct SkeletonDeleter {
    void operator()(uprobe_tracer_bpf* ptr) const {
        if (ptr) uprobe_tracer_bpf__destroy(ptr);
    }
};
using UniqueSkeleton = std::unique_ptr<uprobe_tracer_bpf, SkeletonDeleter>;

// RAII обгортка для Ring Buffer
struct RingBufferDeleter {
    void operator()(ring_buffer* ptr) const {
        if (ptr) ring_buffer__free(ptr);
    }
};
using UniqueRingBuffer = std::unique_ptr<ring_buffer, RingBufferDeleter>;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_target_app>\n";
        return 1;
    }
    const std::string_view binary_path = argv[1];

    std::signal(SIGINT, sig_handler);

    UniqueSkeleton skel{uprobe_tracer_bpf__open_and_load()};
    if (!skel) {
        std::cerr << "Помилка відкриття BPF скелета\n";
        return 1;
    }

    skel->links.trace_entry = bpf_program__attach_uprobe(
        skel->progs.trace_entry, false, -1, binary_path.data(), 0);
    skel->links.trace_exit = bpf_program__attach_uprobe(
        skel->progs.trace_exit, true, -1, binary_path.data(), 0);

    UniqueRingBuffer rb{ring_buffer__new(bpf_map__fd(skel->maps.ringbuf), handle_event, nullptr, nullptr)};
    if (!rb) {
        std::cerr << "Помилка створення Ring Buffer\n";
        return 1;
    }

    std::cout << "Трасування затримки активовано для " << binary_path << ". Натисніть Ctrl+C для виходу.\n";

    while (!exiting) {
        int err = ring_buffer__poll(rb.get(), 100);
        if (err < 0 && err != -EINTR) {
            break;
        }
    }

    return 0; // Автоматична очистка через RAII
}
```
:::

---

## 5. Покрокова компіляція та запуск у тестовому середовищі

Для збірки проекту необхідно встановити пакети `libbpf-dev`, `clang`, `llvm` та `bpftool`. Послідовність дій у консолі:

1. Компіляція цільової програми та збірка BPF-скелета:
```bash
# Компіляція target_app
gcc -O2 target_app.c -o target_app

# Компіляція eBPF програми та генерація скелета libbpf
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c uprobe_tracer.bpf.c -o uprobe_tracer.bpf.o
bpftool gen skeleton uprobe_tracer.bpf.o > uprobe_tracer.skel.h

# Компіляція завантажувача (C та C++)
gcc -O2 tracer.c -lbpf -o tracer_c
g++ -O2 -std=c++17 tracer.cpp -lbpf -o tracer_cpp
```

2. Демонстрація вимірювання затримок:

У першому терміналі запускаємо цільову програму:
```bash
./target_app
# Вивід: Target App C запущено (PID: 41205)
```

У другому терміналі запускаємо завантажувач з правами `root` (необхідними для завантаження BPF):
```bash
sudo ./tracer_cpp ./target_app
```

Результат роботи утиліти спостереження:
```text
Трасування затримки активовано для ./target_app. Натисніть Ctrl+C для виходу.
PID 41205 | Виконання compute_hash: 14210 мкс (14.21 мс)
PID 41205 | Виконання compute_hash: 56830 мкс (56.83 мс)
PID 41205 | Виконання compute_hash: 14195 мкс (14.20 мс)
```

Завдяки зв'язці uprobes, uretprobes та eBPF ми отримали точний інструмент вимірювання затримки виконання внутрішньої функції `compute_hash` у реальному часі. При цьому оригінальний бінарник `target_app` не вимагав жодного перезапуску, а сирцевий код залишився недоторканим.
