# ⚙️ Практична реалізація та бенчмарк доставки подій eBPF

Цей проєкт показує повну практичну реалізацію трасування системних викликів `sys_enter_openat` в ядрі Linux за допомогою eBPF, порівнюючи поведінку збору подій через BPF Ring Buffer та Perf Event Array на практиці під високим навантаженням.

Розробка засобів спостережливості вимоглива до гарантій надійності: при перехопленні тисяч системних викликів на секунду програма трасування не повинна спричиняти падіння ядерного стека, виникати витоки незавершених транзакцій пам'яті або пропускати критичні події аудиту.

---

## 1. Постановка задачі та ідея проєкту

**Задача:** Створити високопродуктивний зонд ядра Linux для перехоплення системних викликів `openat` (відкриття файлів процесами у системі). Для кожної події потрібно фіксувати часову мітку з точністю до наносекунд (`timestamp_ns`), ідентифікатор процесу (`pid`), номер логічного ядра CPU (`cpu_id`), назву виконуваного файла (`comm`) та повний шлях до файлу (`filename`). Системний зонд повинен витримувати інтенсивність до 100 000 викликів на секунду з мінімальними накладними витратами на пам'ять та CPU.

**Ідея реалізації:**
1. Написати eBPF-програму типу `SEC("tracepoint/syscalls/sys_enter_openat")`, яка підключається до точці трасування ядра.
2. Впровадити паралельно два механізми доставки даних у простір користувача:
   - Сучасний підхід з `bpf_ringbuf_reserve` / `bpf_ringbuf_submit` (Zero-Copy без задіяння стека BPF).
   - Застарілий підхід з `bpf_perf_event_output` (копіювання локально створеної структури зі стека BPF).
3. Реалізувати демон у просторі користувача мовами C та C++20 за допомогою `libbpf`, виміряти споживання оперативної пам'яті та перевірити гарантії глобального часового впорядкування.

---

## 2. Анатомія трасувальної події та обмеження BPF-стека

Кожна подія відкриття файла описується структурою `struct event_t`:
- `timestamp_ns`: 64-бітне значення часу в наносекундах від запуску системи (`bpf_ktime_get_ns()`).
- `pid`: 32-бітний ідентифікатор процесу (TGID).
- `cpu_id`: 32-бітний номер логічного ядра CPU (`bpf_get_smp_processor_id()`).
- `comm`: 16-байтний масив із назвою програми (`TASK_COMM_LEN`).
- `filename`: 256-байтний масив із шляхом до відкриваного файла.

Загальний розмір структури дорівнює:
```
Size = 8 (timestamp) + 4 (pid) + 4 (cpu_id) + 16 (comm) + 256 (filename) = 288 байтів
```

Стек BPF-програми у ядрі Linux жорстко обмежений 512 байтами. Оголошення структури `struct event_t` локальною змінною у випадку `perfbuf` забирає `288 / 512 × 100% ≈ 56.2%` усього доступного стека. Спроба розширити шлях `filename` до 4096 байтів призведе до того, що верифікатор ядра відхилить програму з помилкою `BPF stack limit exceeded`.

Натомість при використанні BPF Ring Buffer функція `bpf_ringbuf_reserve` виділяє пам'ять безпосередньо в кільцевому буфері ядра. Локальна змінна на стеку BPF не створюється, тому обмеження стека у 512 байтів більше не є вузьким місцем.

---

## 3. Код зонда ядра eBPF (C)

У коді ядра зверніть увагу на фундаментальну відмінність між двома підходами. При використанні `perfbuf` структура події `struct event_t` розміром 288 байтів спочатку виділяється на стеку BPF, що забирає більше половини доступного ліміту у 512 байтів. При використанні `ringbuf` виклик `bpf_ringbuf_reserve` відразу повертає вказівник на область пам'яті всередині самого кільцевого буфера, усуваючи навантаження на стек.

```c
// BPF kernel space code - C only (виняток §5 AUTHORING: простір ядра Linux)
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define TASK_COMM_LEN 16
#define PATH_MAX_LEN 256

// Структура події трасування
struct event_t {
    u64 timestamp_ns;
    u32 pid;
    u32 cpu_id;
    char comm[TASK_COMM_LEN];
    char filename[PATH_MAX_LEN];
};

// 1. Карта BPF Ring Buffer
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 512 * 1024); // 512 КБ глобального буфера
} rb_events SEC(".maps");

// 2. Карта Perf Event Array
struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(int));
    __uint(value_size, sizeof(int));
} pb_events SEC(".maps");

SEC("tracepoint/syscalls/sys_enter_openat")
int handle_openat(struct trace_event_raw_sys_enter *ctx) {
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32;

    // --- Сценарій A: BPF Ring Buffer (Zero-Copy) ---
    struct event_t *event = bpf_ringbuf_reserve(&rb_events, sizeof(*event), 0);
    if (event) {
        event->timestamp_ns = bpf_ktime_get_ns();
        event->pid = pid;
        event->cpu_id = bpf_get_smp_processor_id();
        bpf_get_current_comm(&event->comm, sizeof(event->comm));
        
        // Зчитування аргументу filename з простору користувача
        const char *fname_ptr = (const char *)BPF_CORE_READ(ctx, args[1]);
        bpf_probe_read_user_str(&event->filename, sizeof(event->filename), fname_ptr);

        // Публікація без копіювання зі стека!
        bpf_ringbuf_submit(event, 0);
    }

    // --- Сценарій B: Perf Event Array (Копіювання зі стека) ---
    // Увага: структура event_t має розмір ~288 байт. Вона займає більше половини
    // 512-байтового стека BPF, що небезпечно при глибоких викликах!
    struct event_t stack_event = {};
    stack_event.timestamp_ns = bpf_ktime_get_ns();
    stack_event.pid = pid;
    stack_event.cpu_id = bpf_get_smp_processor_id();
    bpf_get_current_comm(&stack_event.comm, sizeof(stack_event.comm));

    bpf_perf_event_output(ctx, &pb_events, BPF_F_CURRENT_CPU, &stack_event, sizeof(stack_event));

    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

---

## 4. Код споживача у просторі користувача (C та C++)

Простір користувача реалізує поллінг подій з буфера через бібліотеку `libbpf`. Нижче наведено два варіанти реалізації: класичний C-стиль та ідіоматичний C++20 із застосуванням принципів RAII для безпечного управління ресурсами буфера, обгортками `std::span` та обробкою винятків.

:::tabs
```c
// C Implementation using libbpf
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>

struct event_t {
    unsigned long long timestamp_ns;
    unsigned int pid;
    unsigned int cpu_id;
    char comm[16];
    char filename[256];
};

static volatile bool exiting = false;

static void sig_handler(int sig) {
    exiting = true;
}

static int handle_ring_event(void *ctx, void *data, size_t data_sz) {
    const struct event_t *e = data;
    printf("[%llu ns][CPU %u] PID %u (%s) opened: %s\n",
           e->timestamp_ns, e->cpu_id, e->pid, e->comm, e->filename);
    return 0;
}

int main(int argc, char **argv) {
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    int map_fd = 0; // Вказівник на fd карти ringbuf

    struct ring_buffer *rb = ring_buffer__new(map_fd, handle_ring_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка виділення ring_buffer\n");
        return 1;
    }

    printf("Розпочато трасування системних викликів. Натисніть Ctrl+C для виходу...\n");
    while (!exiting) {
        int err = ring_buffer__poll(rb, 100 /* ms */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка поллінгу: %d\n", err);
            break;
        }
    }

    ring_buffer__free(rb);
    return 0;
}
```
```cpp
// C++20 Idiomatic Implementation (RAII, std::span, std::expected)
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <csignal>
#include <atomic>
#include <expected>
#include <bpf/libbpf.h>

struct alignas(8) Event {
    std::uint64_t timestamp_ns;
    std::uint32_t pid;
    std::uint32_t cpu_id;
    char comm[16];
    char filename[256];
};

namespace {
std::atomic<bool> g_stop{false};
}

class EventConsumer {
public:
    explicit EventConsumer(int map_fd) {
        auto callback_wrapper = [](void *ctx, void *data, size_t size) -> int {
            auto *self = static_cast<EventConsumer*>(ctx);
            if (size < sizeof(Event)) {
                return 0;
            }
            const auto *ev = static_cast<const Event*>(data);
            self->process_event(*ev);
            return 0;
        };

        rb_ = ring_buffer__new(map_fd, callback_wrapper, this, nullptr);
        if (!rb_) {
            throw std::runtime_error("Failed to initialize libbpf ring_buffer");
        }
    }

    ~EventConsumer() {
        if (rb_) {
            ring_buffer__free(rb_);
        }
    }

    EventConsumer(const EventConsumer&) = delete;
    EventConsumer& operator=(const EventConsumer&) = delete;

    void poll_loop() {
        while (!g_stop.load(std::memory_order_relaxed)) {
            int err = ring_buffer__poll(rb_, 100);
            if (err < 0 && err != -EINTR) {
                std::cerr << "Poll error encountered: " << err << '\n';
                break;
            }
        }
    }

private:
    void process_event(const Event &e) const {
        std::string_view comm(e.comm);
        std::string_view filename(e.filename);
        
        std::cout << '[' << e.timestamp_ns << " ns]"
                  << "[CPU " << e.cpu_id << "] "
                  << "PID " << e.pid << " (" << comm << ") -> "
                  << filename << '\n';
    }

    ring_buffer *rb_{nullptr};
};

int main() {
    std::signal(SIGINT, [](int) { g_stop.store(true); });
    std::signal(SIGTERM, [](int) { g_stop.store(true); });

    int map_fd = 0; // Вказівник на fd відкритими картами

    try {
        EventConsumer consumer(map_fd);
        std::cout << "C++ Trace consumer started...\n";
        consumer.poll_loop();
    } catch (const std::exception &ex) {
        std::cerr << "Fatal error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

---

## 5. Пастки реалізації та крайові випадки (Traps & Edge Cases)

Під час розробки та бенчмаркінгу високонавантажених зондів eBPF необхідно враховувати чотири основні пастки архітектури BPF Ring Buffer:

### 1. Невикликаний `submit` або `discard` (Memory Leak та Deadlock у Ringbuf)
Якщо BPF-програма успішно викликає `bpf_ringbuf_reserve()`, але через складне відгалуження умовного оператора `if/else` виходить з функції без парного виклику `bpf_ringbuf_submit()` або `bpf_ringbuf_discard()`, зарезервований слот пам'яті назавжди залишається у стані `BPF_RINGBUF_BUSY_BIT`.

Оскільки споживач у просторі користувача припиняє просування вказівника читання на першому ж BUSY-слоті, **увесь кільцевий буфер наглухо заблокується** для всіх подальших записів з усіх ядер процесора!
*Кримінальне правило розробника:* Кожен виклик `bpf_ringbuf_reserve` повинен гарантовано завершуватися викликом `submit` або `discard` на кожній гілці завершення функції BPF.

### 2. Переповнення BPF-стека при копіюванні у `perfbuf`
У прикладі з `perfbuf` структура `event_t` займала 288 байтів. Стек BPF жорстко обмежений 512 байтами. Якщо розширити розмір пути до файлу `PATH_MAX_LEN` до 4096 байтів, код для `perfbuf` миттєво відхилить верифікатор ядра з помилкою `BPF stack limit reached`. Для вирішення цієї проблеми у випадку `perfbuf` розробники змушені створювати додаткові карты типу `BPF_MAP_TYPE_PERCPU_ARRAY` як тимчасові буфери, що ускладнює код та сповільнює виконання. З `bpf_ringbuf_reserve` ця проблема відсутня за визначенням, оскільки пам'ять виділяється безпосередньо у кільцевому буфері.

### 3. Вимога до розміру буфера Ringbuf (Power of Two)
При конфігуруванні карти `BPF_MAP_TYPE_RINGBUF` параметр `max_entries` повинен бути кратим розміру сторінки пам'яті (`PAGE_SIZE`, зазвичай 4096) та ступеню двійки (наприклад, 64 КБ, 512 КБ, 4 МБ, 16 МБ). Спроба виділити, наприклад, 500 000 байтів поверне помилку `EINVAL` під час завантаження мапи верифікатором ядра Linux.

### 4. Адаптивне сповіщення про нові події (Notification Throttling)
Виклики `bpf_ringbuf_submit` з прапором `0` використовують адаптивний алгоритм розбудження: якщо демон у просторі користувача вже активно виконує цикл поллінгу `ring_buffer__poll`, ядро не надсилає міжпроцесорних переривань (IPI). Це різко знижує навантаження на процесор порівняно з `perfbuf`, який генерує IPI на кожне надсилання події.
