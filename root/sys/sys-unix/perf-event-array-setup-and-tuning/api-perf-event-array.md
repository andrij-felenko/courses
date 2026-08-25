# 📋 Інтерфейси та довідник API BPF_MAP_TYPE_PERF_EVENT_ARRAY

Цей довідник містить вичерпний опис системних інтерфейсів ядра Linux, структур даних, внутрішньоядерних помічників eBPF, констант прапорів та функцій високорівневого API бібліотеки `libbpf`, необхідних для побудови потокового каналу передачі подій через карту `BPF_MAP_TYPE_PERF_EVENT_ARRAY`.

---

## 1. Специфікація та BTF-оголошення карти eBPF

Карта `BPF_MAP_TYPE_PERF_EVENT_ARRAY` являє собою масив файлових дескрипторів `perf_event`, який индексируется ідентифікатором логічного процесора (CPU ID) системи. Кожен елемент карти вказує на відкритий кільцевий буфер ядра, виділений для конкретного ядра CPU.

### 1.1 BTF-оголошення карти у C/C++ (Modern Libbpf)

Оголошення карти в системному коді eBPF виконується через спеціальну секцію `.maps` з використанням макросів BTF-типізації:

```c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));   /* Ключ: CPU ID (від 0 до num_cpus - 1) */
    __uint(value_size, sizeof(__u32)); /* Значення: File Descriptor (FD) події perf */
    __uint(max_entries, 0);            /* 0 вказує ядру автоматично масштабувати розмір під кількість логічних CPU */
} events SEC(".maps");
```

### 1.2 Детальний розбір атрибутів карти

- **`type`**: Константа `BPF_MAP_TYPE_PERF_EVENT_ARRAY` (значення `4` у внутрішньому переліку ядра `enum bpf_map_type`). Вказує віртуальній машині eBPF, що дана карта оперує кільцевими буферами підсистеми `perf`.
- **`key_size`**: Обов'язково дорівнює `sizeof(__u32)` (4 байти). Вказує на беззнакове 32-бітне ціле число, що означає номер логічного ядра процесора (`0`, `1`, ..., `N-1`).
- **`value_size`**: Обов'язково дорівнює `sizeof(__u32)` (4 байти). На рівні простору користувача в це поле записується файловий дескриптор, отриманий у результаті виконання системного виклику `perf_event_open()`.
- **`max_entries`**: Якщо під час оголошення карти вказати `0`, бібліотека `libbpf` під час відкриття об'єкта автоматично визначить кількість доступних логічних ядер процесора через конфігурацію sysfs (`/sys/devices/system/cpu/possible`) і виділить відповідну кількість комірок.

---

## 2. Сигнатура та механіка помічника bpf_perf_event_output()

Для запису структури події з коду eBPF-програми у кільцевий буфер підсистеми `perf` використовується внутрішньоядерна функція-помічник `bpf_perf_event_output()`.

### 2.1 Прототип функції

```c
long bpf_perf_event_output(void *ctx, struct bpf_map *map, u64 flags, void *data, u64 size);
```

### 2.2 Докладний аналіз параметрів

1. **`ctx`**: Вказівник на контекст виконання поточного eBPF-зонда.
   - Для `kprobe` / `kretprobe`: вказівник `struct pt_regs *`.
   - Для `tracepoint`: вказівник `struct tracepoint_raw_context *` або відповідна структура аргументів конкретного tracepoint.
   - Для `socket filter` / `tc`: вказівник на структуру сокетного буфера `struct __sk_buff *`.
   - Для `raw_tracepoint`: вказівник `struct bpf_raw_tracepoint_args *`.
   Контекст є обов'язковим для ядра, оскільки з нього витягуються атрибути апаратного стану процесора та регістраційні дані події.

2. **`map`**: Вказівник на завантажену карту `BPF_MAP_TYPE_PERF_EVENT_ARRAY`.

3. **`flags`**: 64-бітне бітове поле конфігурації запису:
   - **Молодші 32 біти (`flags & 0xFFFFFFFFULL`)**: Вказують індекс процесора у масиві карти. Значення **`BPF_F_CURRENT_CPU`** (`0xFFFFFFFFULL`) інструктує ядро визначити номер поточного CPU під час виконання і записати дані у відповідний кільцевий буфер.
   - **Старші 32 біти (`flags >> 32`)**: Використовуються для вказівки розміру сирих даних події (`PERF_SAMPLE_RAW`), якщо потрібно включити додаткові апаратні регістри CPU.

4. **`data`**: Вказівник на область оперативної пам'яті (структуру події), яка містить корисне навантаження (payload).

5. **`size`**: Розмір payload даних у байтах.

### 2.3 Повернені значення та діагностика помилок

Функція повертає значення `0` у разі успішного запису події у буфер або від'ємний код помилки системи `errno`:

- **`0`**: Запис успішно здійснено.
- **`-EINVAL`** (`-22`): Передано некоректний вказівник карти, непідтримувані прапори або недійсний контекст eBPF-програми.
- **`-E2BIG`** (`-7`): Значення `size` перевищує максимальний розмір сторінки кільцевого буфера.
- **`-EFAULT`** (`-14`): Помилка адресації пам'яті при спробі зчитати дані за вказівником `data`.
- **`-ENOSPC`** (`-28`): Кільцевий буфер поточного CPU повністю заповнений (Userspace-демон не встигає читати події).
- **`-EOPNOTSUPP`** (`-95`): Операція не підтримується для даного типу eBPF-програми.

---

## 3. Системні структури даних ядра Linux та mmap-буфера

Пам'ять кільцевого буфера відображається у простір користувача через системний виклик `mmap()`. Вона складається з заголовочної сторінки (Header Page) та послідовності сторінок даних (Data Pages).

### 3.1 Конфігураційна структура perf_event_attr

Під час прямого відкриття події через системний виклик `perf_event_open()` ядру передається структура конфігурації `struct perf_event_attr`:

```c
struct perf_event_attr {
    __u32 type;           /* PERF_TYPE_SOFTWARE */
    __u32 size;           /* sizeof(struct perf_event_attr) */
    __u64 config;         /* PERF_COUNT_SW_BPF_OUTPUT */
    __u64 sample_period;  /* 1 (вибірка кожної події) */
    __u64 sample_type;    /* PERF_SAMPLE_RAW */
    __u64 read_format;    /* Формат зчитаних даних */
    __u64 disabled : 1,   /* Початковий стан: 0 = включено */
          inherit  : 1,   /* Успадкування дочірніми процесами */
          pinned   : 1,   /* Закріплення на CPU */
          exclusive: 1;   /* Ексклюзивний доступ */
    __u32 wakeup_events;  /* Кількість подій для генерації переривання (batching) */
};
```

Головні поля для роботи з eBPF:
- **`type = PERF_TYPE_SOFTWARE`**: Вказує ядру, що джерелом подій є програмна підсистема.
- **`config = PERF_COUNT_SW_BPF_OUTPUT`**: Спеціальна програмна подія ядра, призначена для виводу даних з eBPF-програм.
- **`sample_type = PERF_SAMPLE_RAW`**: Вказує, що запис містить довільний сирий бінарний payload, згенерований eBPF-програмою.
- **`wakeup_events`**: Поріг пробудження. Якщо встановити значення `64`, ядро розбудить userspace через `epoll` тільки після накопичення 64 подій.

### 3.2 Заголовочна сторінка mmap (struct perf_event_mmap_page)

Перша сторінка кільцевого буфера містить управляючу структуру ядра `struct perf_event_mmap_page`:

```c
struct perf_event_mmap_page {
    __u32 version;        /* Версія структури даних perf */
    __u32 compat_version; /* Версія сумісності */
    __u32 lock;           /* Поле локу для послідовного читання */
    __u32 index;          /* Індекс апаратного лічильника */
    __s64 offset;         /* Зсув лічильника */
    __u64 time_enabled;   /* Час активності події */
    __u64 time_running;   /* Час виконання події */

    /* Ключові покажчики кільцевого буфера */
    __u64 data_head;      /* Вказівник голови (монотонно зростає, оновлюється ядром) */
    __u64 data_tail;      /* Вказівник хвоста (монотонно зростає, оновлюється userspace) */
    __u64 data_offset;    /* Зсув початку даних від старту mmap області (4096 байт) */
    __u64 data_size;      /* Розмір буфера даних у байтах (ступінь двійки) */
};
```

Поля `data_head` та `data_tail` є основою логіки кільцевого буфера без блокувань:
- Ядро атомарно збільшує `data_head` на розмір кожного нового записаного елемента.
- Демон моніторингу читає дані з позиції `data_tail` до `data_head`.
- Після обробки накопичених записів демон записує нове значення `data_tail`, інформуючи ядро про звільнення простору.

### 3.3 Заголовок запису події (struct perf_event_header)

Кожен окремий запис у розділі даних кільцевого буфера починається з 8-байтового заголовка:

```c
struct perf_event_header {
    __u32 type; /* Тип запису (PERF_RECORD_SAMPLE, PERF_RECORD_LOST тощо) */
    __u16 misc; /* Допоміжні прапори (контекст виконання: kernel/user/guest) */
    __u16 size; /* Повний розмір запису у байтах (включаючи заголовок) */
};
```

Значення поля `type`:
- **`PERF_RECORD_SAMPLE`** (`9`): Запис містить корисний payload події eBPF.
- **`PERF_RECORD_LOST`** (`2`): Службове повідомлення ядра про кількість втрачених подій через переповнення буфера.

---

## 4. Високорівневе API бібліотеки libbpf

Бібліотека `libbpf` надає абстракцію `struct perf_buffer`, яка автоматизує системні виклики `perf_event_open()`, виклики `mmap()` та управління циклами `epoll`.

### 4.1 Сигнатури Callback-функцій

```c
/* Обробник звичайних подій даних */
typedef void (*perf_buffer_sample_fn)(void *ctx, int cpu, void *data, __u32 size);

/* Обробник повідомлень про втрачені події */
typedef void (*perf_buffer_lost_fn)(void *ctx, int cpu, __u64 lost_cnt);
```

### 4.2 Створення та керування об'єктом perf_buffer

Для ініціалізації та управління кільцевим буфером у просторі користувача надаються C та C++ виклики:

:::tabs
```c
#include <stdio.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

void sample_handler(void *ctx, int cpu, void *data, __u32 size) {
    (void)ctx;
    printf("CPU %d: отримано %u байт\n", cpu, size);
}

void lost_handler(void *ctx, int cpu, __u64 lost_cnt) {
    (void)ctx;
    fprintf(stderr, "УВАГА: Втрачено %llu подій на CPU %d!\n", lost_cnt, cpu);
}

struct perf_buffer *init_buffer(int map_fd) {
    /* Створення буфера на 16 сторінок (64 КБ) на кожен CPU */
    struct perf_buffer *pb = perf_buffer__new(
        map_fd,
        16,
        sample_handler,
        lost_handler,
        NULL,
        NULL
    );

    if (libbpf_get_error(pb)) {
        return NULL;
    }
    return pb;
}

void poll_loop(struct perf_buffer *pb) {
    while (1) {
        int err = perf_buffer__poll(pb, 100 /* ms */);
        if (err < 0 && err != -EINTR) {
            break;
        }
    }
}
```
```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

class PerfBufferWrapper {
public:
    explicit PerfBufferWrapper(int map_fd, size_t page_cnt = 16) {
        perf_buffer* pb = perf_buffer__new(
            map_fd,
            page_cnt,
            &PerfBufferWrapper::on_sample,
            &PerfBufferWrapper::on_lost,
            this,
            nullptr
        );

        if (libbpf_get_error(pb)) {
            throw std::runtime_error("Не вдалося ініціалізувати perf_buffer у C++");
        }
        pb_.reset(pb);
    }

    void poll(int timeout_ms = 100) {
        int err = perf_buffer__poll(pb_.get(), timeout_ms);
        if (err < 0 && err != -EINTR) {
            throw std::runtime_error("Помилка опитування perf_buffer__poll");
        }
    }

private:
    static void on_sample(void* ctx, int cpu, void* data, __u32 size) noexcept {
        (void)ctx;
        std::cout << "[C++ Agent] CPU " << cpu << ": отримано " << size << " байт\n";
    }

    static void on_lost(void* ctx, int cpu, __u64 lost_cnt) noexcept {
        (void)ctx;
        std::cerr << "[C++ Agent] УВАГА: Втрачено " << lost_cnt << " подій на CPU " << cpu << "\n";
    }

    struct BufferDeleter {
        void operator()(perf_buffer* pb) const noexcept {
            if (pb) perf_buffer__free(pb);
        }
    };

    std::unique_ptr<perf_buffer, BufferDeleter> pb_;
};
```
:::

---

## 5. Додаткові опції структури perf_buffer_opts

Для тонкого налаштування поведінки під час виклику `perf_buffer__new_raw()` передається структура розширених опцій `struct perf_buffer_opts`:

```c
struct perf_buffer_opts {
    size_t sz;                     /* sizeof(struct perf_buffer_opts) */
    perf_buffer_sample_fn sample_cb; /* Callback для даних */
    perf_buffer_lost_fn lost_cb;   /* Callback для втрачених подій */
    void *ctx;                     /* Контекстний вказівник */
    int sample_period;             /* Період вибірки подій */
    int sample_type;               /* Тип вибірки perf */
    int wakeup_events;             /* Поріг пробудження epoll у кількості подій */
};
```

Використання `wakeup_events` дозволяє настроїти пакетну обробку подій (batching) безпосередньо через високорівневе API `libbpf`.

---

## 6. Обмеження пам'яті RLIMIT_MEMLOCK та адміністрування

Під час роботи з картками `PERF_EVENT_ARRAY` на версіях ядер Linux до **5.11** виділення пам'яті під кільцеві буфери обмежувалося системною квотою заблокованої пам'яті `RLIMIT_MEMLOCK`.

Якщо демон у просторі користувача намагався виділити великі буфери (наприклад, `128` сторінок на кожен з 64 CPU) без попереднього збільшення лімітів, системні виклики `mmap()` або `perf_event_open()` повертали помилку **`-EPERM`** або **`-ENOMEM`**.

### 6.1 Програмне підвищення лімітів у C/C++

```c
#include <sys/resource.h>
#include <stdio.h>

int bump_memlock_rlimit(void) {
    struct rlimit rlim_new = {
        .rlim_cur = RLIM_INFINITY,
        .rlim_max = RLIM_INFINITY,
    };
    return setrlimit(RLIMIT_MEMLOCK, &rlim_new);
}
```

У сучасних ядрах Linux (починаючи з версії 5.11) підсистема eBPF перейшла на облік пам'яті через контрольні групи cgroups (`memcg`), що позбавляє від потреби виклику `setrlimit()` у сучасних середовищах.
