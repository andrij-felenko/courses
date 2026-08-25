# ⚙️ Практична реалізація моніторингу затримки системних викликів на eBPF

Вимірювання точної тривалості системних викликів є ключовим завданням профілювання продуктивності підсистем ядра, де затримка введення-виведення у кілька мілісекунд може заблокувати роботу всього сервісу. Спроба виміряти затримку в просторі користувача за допомогою таймерів `clock_gettime()` до і після системного виклику `open()` дає спотворені результати: виміряний інтервал включає накладні витрати на перемикання контексту, витіснення потоку планувальником завдань, обробку апаратних переривань та очікування черги CPU. Для отримання справжнього часу виконання операції у віртуальній файловій системі (VFS) та на блокових пристроях вимірювання має відбуватися строго всередині ядра операційної системи.

Проєкт реалізує повноцінний трасувальник затримки системного виклику відкриття файлів `do_sys_openat2` на базі eBPF-зондів kprobe/kretprobe, хеш-карти збереження часових міток та кільцевого буфера BPF Ring Buffer для передачі структурованих подій у простір користувача.

---

## 1. Архітектура та потік даних трасувальника

Трасувальник складається з двох компонентів, що взаємодіють через пам'ять ядра:

1. **Програма простору ядра (`openat_tracker.bpf.c`)**:
   * Зонд `SEC("kprobe/do_sys_openat2")` перехоплює момент входу в системний виклик, зчитує 64-бітний комбінований ідентифікатор процесу й потоку `pid_tgid` та зберігає поточну мітку монотонного часу `bpf_ktime_get_ns()` у хеш-карті `start_times`.
   * Зонд `SEC("kretprobe/do_sys_openat2")` спрацьовує при завершенні виклику ядра, витягує стартовий час із карти, обчислює різницю `delta_ns`, негайно видаляє тимчасовий запис і публікує подію в буфер `BPF_MAP_TYPE_RINGBUF`.
2. **Програма простору користувача**:
   * Завантажує скомпільований об'єктний ELF-файл eBPF через бібліотеку `libbpf`.
   * Прикріплює зонди до символів ядра операційної системи.
   * Безперервно опитує Ring Buffer через механізм опитування без втрати подій і виводить у термінал назву процесу, PID, код повернення та тривалість виконання у мікросекундах.

```
+-----------------------------------------------------------------------------+
|                             ПРОСТІР ЯДРА (RING 0)                           |
|                                                                             |
|  [ do_sys_openat2 Enter ] ---> kprobe  ---> Зберегти t0 у start_times Map   |
|                                                     |                       |
|  [ do_sys_openat2 Exit  ] ---> kretprobe ---> t1 - t0 -> Відправити в       |
|                                               Ring Buffer & видалити з Map  |
+-----------------------------------------------------------------------------+
                                       |
                                       v (bpf_ring_buffer__poll)
+-----------------------------------------------------------------------------+
|                          ПРОСТІР КОРИСТУВАЧА (USER SPACE)                   |
|                                                                             |
|  Отримання структури: [ PID | COMM | Затримка (us) | Код повернення (FD) ]   |
+-----------------------------------------------------------------------------+
```

---

## 2. Код програми eBPF для простору ядра

Файл `openat_tracker.bpf.c` компілюється за допомогою Clang із прапорцем `-target bpf`. Зверніть увагу, що резервування пам'яті у кільцевому буфері виконується за допомогою функції `bpf_ringbuf_reserve()`, що виключає необхідність розміщення великої структури події на локальному стеку eBPF:

```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

/* Структура події, що надсилається у простір користувача */
struct event_t {
    __u32 pid;
    __u32 tgid;
    __u64 duration_ns;
    __s32 ret_code;
    char comm[16];
};

/* Хеш-карта для збереження часу старту операції: ключ = pid_tgid, значення = u64 */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, __u64);
    __type(value, __u64);
} start_times SEC(".maps");

/* Кільцевий буфер подій */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); /* 256 KB буфер */
} events SEC(".maps");

SEC("kprobe/do_sys_openat2")
int BPF_KPROBE(trace_openat_enter)
{
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u64 ts = bpf_ktime_get_ns();

    /* Зберігаємо стартовий час за ідентифікатором потоку */
    bpf_map_update_elem(&start_times, &pid_tgid, &ts, BPF_ANY);
    return 0;
}

SEC("kretprobe/do_sys_openat2")
int BPF_KRETPROBE(trace_openat_exit, long ret)
{
    __u64 pid_tgid = bpf_get_current_pid_tgid();
    __u64 *start_ts = bpf_map_lookup_elem(&start_times, &pid_tgid);

    if (!start_ts) {
        return 0; /* Пропустити, якщо початок операції не зафіксовано */
    }

    __u64 delta_ns = bpf_ktime_get_ns() - *start_ts;

    /* Обов'язкове очищення карти для запобігання витоку пам'яті */
    bpf_map_delete_elem(&start_times, &pid_tgid);

    /* Резервування пам'яті у Ring Buffer без навантаження на стек */
    struct event_t *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) {
        return 0; /* Буфер переповнено */
    }

    e->tgid = pid_tgid >> 32;
    e->pid = (__u32)pid_tgid;
    e->duration_ns = delta_ns;
    e->ret_code = (__s32)ret;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    /* Публікація події */
    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

---

## 3. Програма простору користувача

Програма відкриває двійковий об'єкт BPF, передає його верифікатору ядра для перевірки безпеки, прикріплює обробники kprobe/kretprobe до ядра і зчитує структуровані події через функцію зворотного виклику (*callback*).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

static volatile sig_atomic_t stop_requested = 0;

static void sig_handler(int sig)
{
    (void)sig;
    stop_requested = 1;
}

struct event_t {
    unsigned int pid;
    unsigned int tgid;
    unsigned long long duration_ns;
    int ret_code;
    char comm[16];
};

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    (void)ctx;
    (void)data_sz;
    const struct event_t *e = (const struct event_t *)data;

    printf("[TGID %5u] %-16s | openat FD: %3d | Затримка: %6.2f мкс\n",
           e->tgid, e->comm, e->ret_code, (double)e->duration_ns / 1000.0);
    return 0;
}

int main(void)
{
    struct bpf_object *obj = NULL;
    struct ring_buffer *rb = NULL;
    int err = 0;

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* 1. Відкриття та завантаження скомпільованого BPF ELF */
    obj = bpf_object__open_file("openat_tracker.bpf.o", NULL);
    if (!obj) {
        fprintf(stderr, "Помилка відкриття об'єкта BPF\n");
        return 1;
    }

    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "Помилка завантаження програми верифікатором ядра: %d\n", err);
        bpf_object__close(obj);
        return 1;
    }

    /* 2. Прикріплення обробників зондів */
    struct bpf_program *prog_kprobe = bpf_object__find_program_by_name(obj, "trace_openat_enter");
    struct bpf_program *prog_kretprobe = bpf_object__find_program_by_name(obj, "trace_openat_exit");

    struct bpf_link *link_enter = bpf_program__attach(prog_kprobe);
    struct bpf_link *link_exit = bpf_program__attach(prog_kretprobe);

    if (!link_enter || !link_exit) {
        fprintf(stderr, "Помилка прикріплення kprobes\n");
        goto cleanup;
    }

    /* 3. Ініціалізація Ring Buffer */
    int events_map_fd = bpf_object__find_map_fd_by_name(obj, "events");
    rb = ring_buffer__new(events_map_fd, handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "Помилка створення обробника Ring Buffer\n");
        goto cleanup;
    }

    printf("Трасування openat запущено. Натисніть Ctrl+C для виходу...\n");

    /* 4. Головний цикл опитування */
    while (!stop_requested) {
        err = ring_buffer__poll(rb, 100 /* таймаут 100 мс */);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "Помилка опитування буфера: %d\n", err);
            break;
        }
    }

cleanup:
    if (rb) ring_buffer__free(rb);
    if (link_enter) bpf_link__destroy(link_enter);
    if (link_exit) bpf_link__destroy(link_exit);
    if (obj) bpf_object__close(obj);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <atomic>
#include <csignal>
#include <system_error>
#include <iomanip>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

namespace {
    std::atomic<bool> stop_requested{false};

    void sig_handler(int) {
        stop_requested.store(true, std::memory_order_relaxed);
    }
}

struct Event {
    uint32_t pid;
    uint32_t tgid;
    uint64_t duration_ns;
    int32_t ret_code;
    char comm[16];
};

struct BpfObjectDeleter {
    void operator()(bpf_object* obj) const noexcept {
        if (obj) bpf_object__close(obj);
    }
};

struct BpfLinkDeleter {
    void operator()(bpf_link* link) const noexcept {
        if (link) bpf_link__destroy(link);
    }
};

struct RingBufferDeleter {
    void operator()(ring_buffer* rb) const noexcept {
        if (rb) ring_buffer__free(rb);
    }
};

using UniqueBpfObject = std::unique_ptr<bpf_object, BpfObjectDeleter>;
using UniqueBpfLink = std::unique_ptr<bpf_link, BpfLinkDeleter>;
using UniqueRingBuffer = std::unique_ptr<ring_buffer, RingBufferDeleter>;

static int handle_event([[maybe_unused]] void* ctx, void* data, [[maybe_unused]] size_t data_sz) {
    const auto* e = static_cast<const Event*>(data);
    std::cout << "[TGID " << std::setw(5) << e->tgid << "] "
              << std::setw(16) << std::left << e->comm << std::right
              << " | openat FD: " << std::setw(3) << e->ret_code
              << " | Затримка: " << std::fixed << std::setprecision(2)
              << (static_cast<double>(e->duration_ns) / 1000.0) << " мкс\n";
    return 0;
}

int main() {
    std::signal(SIGINT, sig_handler);
    std::signal(SIGTERM, sig_handler);

    try {
        UniqueBpfObject obj{bpf_object__open_file("openat_tracker.bpf.o", nullptr)};
        if (!obj) {
            throw std::runtime_error("Не вдалося відкрити BPF-файл");
        }

        if (bpf_object__load(obj.get()) != 0) {
            throw std::runtime_error("Верифікатор ядра відхилив програму BPF");
        }

        auto* prog_enter = bpf_object__find_program_by_name(obj.get(), "trace_openat_enter");
        auto* prog_exit = bpf_object__find_program_by_name(obj.get(), "trace_openat_exit");

        UniqueBpfLink link_enter{bpf_program__attach(prog_enter)};
        UniqueBpfLink link_exit{bpf_program__attach(prog_exit)};

        if (!link_enter || !link_exit) {
            throw std::runtime_error("Не вдалося прикріпити зонди kprobe/kretprobe");
        }

        const int map_fd = bpf_object__find_map_fd_by_name(obj.get(), "events");
        UniqueRingBuffer rb{ring_buffer__new(map_fd, handle_event, nullptr, nullptr)};
        if (!rb) {
            throw std::runtime_error("Помилка ініціалізації Ring Buffer");
        }

        std::cout << "Трасування openat запущено (C++). Натисніть Ctrl+C для виходу...\n";

        while (!stop_requested.load(std::memory_order_relaxed)) {
            const int res = ring_buffer__poll(rb.get(), 100);
            if (res < 0 && res != -EINTR) {
                break;
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## 4. Збирання, автоматична генерація скелетів та привілеї

Для компіляції програми BPF та завантажувача використовується стандартний набір інструментів Clang та `libbpf`:

```bash
# 1. Компіляція байт-коду ядра eBPF
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -I/usr/include -c openat_tracker.bpf.c -o openat_tracker.bpf.o

# 2. Опціональна генерація C-скелета (bpftool gen skeleton)
bpftool gen skeleton openat_tracker.bpf.o > openat_tracker.skel.h

# 3. Компіляція програми простору користувача на C
gcc -O2 -g -Wall openat_tracker.c -lbpf -lelf -lz -o openat_tracker

# 4. Запуск з привілеями CAP_BPF та CAP_PERFMON (або root)
sudo ./openat_tracker
```

У сучасній розробці замість ручного виклику `bpf_object__find_program_by_name()` застосовують утиліту `bpftool gen skeleton`. Вона генерує типізовану структуру даних, де кожна карта і кожна програма доступні як звичайні поля структури (`skel->maps.events`, `skel->progs.trace_openat_enter`). Це запобігає друкарським помилкам у назвах символів під час виконання.

Перед запуском програми ядро перевіряє права процесу. Для успішного виконання системного виклику `bpf(BPF_PROG_LOAD)` та прикріплення зондів процес повинен мати права `CAP_BPF` та `CAP_PERFMON` (у ядрах, старіших за Linux 5.8, вимагався загальний `CAP_SYS_ADMIN`). Також системне обмеження заблокованої в пам'яті сторінок `RLIMIT_MEMLOCK` має бути достатнім для виділення карт BPF.

---

## 5. Тестування та перевірка роботи під навантаженням

Для перевірки роботи трасувальника можна згенерувати інтенсивний потік операцій відкриття файлів у паралельному терміналі за допомогою утиліти `dd` або `find`:

```bash
# Генерація потоку викликів openat
find /usr/include -name "*.h" -exec cat {} + > /dev/null
```

У вікні трасувальника з'явиться вивід з реальними затримками:

```text
[TGID  4512] find             | openat FD:   3 | Затримка:   4.15 мкс
[TGID  4513] cat              | openat FD:   3 | Затримка:  12.80 мкс
[TGID  4513] cat              | openat FD:   3 | Затримка:   3.90 мкс
```

---

## 6. Механізм пробудження процесу та опитування Ring Buffer

Утиліта `ring_buffer__poll()` під капотом використовує механізм ядра `epoll` та файловий дескриптор сповіщень. Коли програма eBPF викликає `bpf_ringbuf_submit()`, ядро перевіряє, чи очікує користувацький процес нових даних. Якщо буфер містить записи, ядро ініціює подію готовності для читання (*EPOLLIN*) і будить заблокований системний виклик `epoll_wait()`. Якщо системних викликів `openat` не відбувається, процес простору користувача перебуває у стані сну (*TASK_INTERRUPTIBLE*) з нульовим споживанням процесорного часу (0% CPU).

---

## 7. Порівняння зондів: kprobe проти статичних tracepoints

У цьому проєкті використано динамічні зонди `kprobe/do_sys_openat2`. Проте для серійних інструментів моніторингу рекомендується враховувати відмінності:
* **Динамічні зонди kprobe**: Можуть перехоплювати будь-яку функцію ядра, але спираються на внутрішні символи `vmlinux`. Якщо розробники ядра змінюють назву функції або компілятор GCC/Clang вбудовує (*inlines*) функцію під час оптимізації, зонд не зможе прикріпитися.
* **Статичні точки tracepoint (`SEC("tracepoint/syscalls/sys_enter_openat")`)**: Мають стабільний ABI, визначений у підсистемі трасування ядра Linux. Їхня сигнатура аргументів не змінюється між релізами, що забезпечує максимальну сумісність програми без прив'язки до внутрішніх оптимізацій конкретного ядра.

---

## 8. Підводні камені та типові пастки розробки

1. **Витік пам'яті у хеш-карті**: Якщо процес викликає `openat`, але аварійно завершується (наприклад, отримує сигнал `SIGKILL`) всередині виклику ядра, зонд `kretprobe` ніколи не спрацює. Ключ назавжди залишиться у карті `start_times`. За тривалої роботи системи таблиця переповниться (`-E2BIG`). Для вирішення застосовують `BPF_MAP_TYPE_LRU_HASH` або періодичний фоновий аудит ключів із простору користувача.
2. **Розрізнення потоків виконання**: Використання звичайного PID (ID процесу) призведе до колізій, якщо декілька потоків одного процесу одночасно відкривають файли. Обов'язково слід використовувати повне 64-бітне значення `bpf_get_current_pid_tgid()`, де старші 32 біти є PID процесу (TGID), а молодші 32 біти — унікальним ідентифікатором ядра для конкретного потоку (TID).
3. **Перевірка результату вибірки з карти на NULL**: Якщо в коді `trace_openat_exit` пропустити перевірку `if (!start_ts) return 0;` і спробувати одразу розіменувати `*start_ts`, верифікатор ядра негайно відхилить програму з помилкою `R0 invalid mem access 'map_value_or_null'`. Верифікатор відстежує тип як `PTR_TO_MAP_VALUE_OR_NULL` і дозволяє читання лише після явної перевірки на ненульове значення.
4. **Оверхед зондів kprobes**: Зонди `kprobe` ініціюють заміну інструкції ядра на точку зупину (`int3` або ftrace-трамплін). Для надвисоких навантажень (мільйони викликів на секунду) рекомендується замінювати kprobe/kretprobe на сучасні механізми **fentry** та **fexit**, які використовують прямий прямий стрибок без збереження зайвого контексту переривання.
