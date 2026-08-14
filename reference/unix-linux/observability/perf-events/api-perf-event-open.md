# 📋 Інтерфейс системного виклику perf_event_open

Цей довідник містить повну специфікацію бінарного інтерфейсу системного виклику `perf_event_open()`, конфігураційних структур ядра Linux `struct perf_event_attr`, заголовочної сторінки розділюваної пам'яті `struct perf_event_mmap_page` та форматів подій кільцевого буфера.

## 1. Сигнатура та матриця параметрів системного виклику

Системний виклик `perf_event_open()` відсутній у стандартній заголовочній бібліотеці C (`libc`) і викликається у користувацьких програмах через низькорівневий мостик системних викликів `syscall()`:

:::tabs
```c
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>

long perf_event_open(struct perf_event_attr *attr,
                     pid_t pid,
                     int cpu,
                     int group_fd,
                     unsigned long flags) {
    return syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}
```
```cpp
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>

namespace sys::abi {
    inline std::expected<int, std::error_code> perf_event_open(
        struct perf_event_attr* attr, pid_t pid, int cpu, int group_fd, unsigned long flags) noexcept {
        long res = ::syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
        if (res == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<int>(res);
    }
}
```
:::

### Детальний опис параметрів виклику

1. `attr`: Вказівник на структуру `struct perf_event_attr`, яка визначає тип події, режим вибірки або підрахунку, фільтри та атрибути обробки. Структура повинна бути обнулена через `memset()` чи ініціалізацію `{}` у C++, а її поле `size` має дорівнювати `sizeof(struct perf_event_attr)` для забезпечення зворотної сумісності версій ядра.
2. `pid`: Ідентифікатор процесу або потоку:
   - `pid == 0`: Моніторинг поточного процесу/потоку, який здійснив системний виклик.
   - `pid > 0`: Моніторинг конкретного процесу з вказаним PID у системі.
   - `pid == -1`: Моніторинг усіх процесів у системі (вимагає наявності привілеїв `CAP_PERFMON` або `CAP_SYS_ADMIN`).
3. `cpu`: Ідентифікатор ядра процесора:
   - `cpu >= 0`: Моніторинг подій лише на вказаному процесорному ядрі.
   - `cpu == -1`: Моніторинг подій на будь-якому процесорному ядрі для вказаного `pid`.
4. `group_fd`: Файловий дескриптор лідера групи подій:
   - `group_fd == -1`: Подія створюється як незалежний лідер нової групи подій.
   - `group_fd > 0`: Подія приєднується до існуючої групи подій під керівництвом `group_fd`. Усі події однієї групи розкладаються на апаратні лічильники PMU атомарно за один системний виклик і зчитуються разом при використанні прапорця `PERF_FORMAT_GROUP`.
5. `flags`: Прапорці поведінки системного виклику:
   - `PERF_FLAG_FD_CLOEXEC` (1U << 0): Встановлює прапор `FD_CLOEXEC` на створеному файловому дескрипторі, запобігаючи його спадкуванню при дочірніх викликах `execve()`.
   - `PERF_FLAG_FD_NO_GROUP` (1U << 1): Ігнорує створення групи подій при передачі `group_fd`.
   - `PERF_FLAG_FD_OUTPUT` (1U << 2): Перенаправляє кільцевий буфер вибірок даної події у кільцевий буфер події `group_fd`, заощаджуючи пам'ять.
   - `PERF_FLAG_PID_CGROUP` (1U << 3): Параметр `pid` інтерпретується як відкритий файловий дескриптор каталогів cgroup v2 (`/sys/fs/cgroup/...`) для моніторингу цілої контрольної групи процесів.

### Матриця дозволених комбінацій pid та cpu

| pid | cpu | Область вимірювання (Measurement Scope) | Необхідні права |
|---|---|---|---|
| `> 0` | `-1` | Конкретний процес/потік на будь-якому CPU | Права власника процесу |
| `0` | `-1` | Викликаючий потік на будь-якому CPU | Дозволено усім |
| `-1` | `>= 0` | Усі процеси на конкретному CPU (System-wide CPU mode) | `CAP_PERFMON` / `CAP_SYS_ADMIN` |
| `> 0` | `>= 0` | Конкретний процес лише коли він виконується на вказаному CPU | Права власника процесу |
| `-1` | `-1` | Неприпустима комбінація (повертає помилку `EINVAL`) | N/A |

---

## 2. Специфікація конфігураційної структури struct perf_event_attr

Структура `struct perf_event_attr` визначає всі параметри налаштування події. Вона вирівняна за 64-бітним кордоном і має фіксований розмір `size`, що забезпечує зворотну сумісність між версіями ядра Linux.

:::tabs
```c
/* Структура конфігурації perf_event у C UAPI header <linux/perf_event.h> */
struct perf_event_attr {
    __u32 type;                 /* Тип події (PERF_TYPE_*) */
    __u32 size;                 /* Розмір структури sizeof(struct perf_event_attr) */
    __u64 config;               /* Конфігурація конкретної події */

    union {
        __u64 sample_period;    /* Період вибірки (кількість подій на NMI) */
        __u64 sample_freq;      /* Динамічна частота вибірки у Гц */
    };

    __u64 sample_type;          /* Бітова маска полів, що записуються у вибірку */
    __u64 read_format;          /* Формат даних при виклику read() */

    __u64 disabled       : 1,   /* Подія створюється у вимкненому стані */
          inherit        : 1,   /* Успадковувати подію дочірніми потоками (fork) */
          pinned         : 1,   /* Подія має залишатися на HW PMC (лише для лідерів) */
          exclusive      : 1,   /* Захоплює HW PMC монопольно */
          exclude_user   : 1,   /* Не рахувати події у user-space (ring 3) */
          exclude_kernel : 1,   /* Не рахувати події у kernel-space (ring 0) */
          exclude_hv     : 1,   /* Не рахувати події у гіпервізорі (KVM/Xen) */
          exclude_idle   : 1,   /* Не рахувати події коли CPU перебуває в idle */
          mmap           : 1,   /* Відстежувати виклики mmap (PERF_RECORD_MMAP) */
          comm           : 1,   /* Відстежувати зміни імені процесу (PERF_RECORD_COMM) */
          freq           : 1,   /* Використовувати sample_freq замість sample_period */
          inherit_stat   : 1,   /* Збирати статистику для дочірніх процесів */
          enable_on_exec : 1,   /* Автоматично вмикати подію при execve() */
          task           : 1,   /* Генерувати події fork/exit (PERF_RECORD_FORK/EXIT) */
          watermark      : 1,   /* Сигналізувати wakeup_watermark байтів у буфері */
          precise_ip     : 2,   /* Рівень точності RIP (0..3, PEBS/IBS) */
          mmap_data      : 1,   /* Відстежувати mmap для даних (non-executable) */
          sample_id_all  : 1,   /* Додавати TID/TIME до усіх типів PERF_RECORD_* */
          exclude_host   : 1,   /* Не рахувати події хоста у віртуалізації */
          exclude_guest  : 1,   /* Не рахувати події гостя у віртуалізації */
          exclude_callchain_kernel : 1, /* Виключити стек ядра з callchain */
          exclude_callchain_user   : 1, /* Виключити стек користувача з callchain */
          mmap2          : 1,   /* Розширені події mmap (PERF_RECORD_MMAP2) */
          comm_exec      : 1,   /* Помічати зміни COMM зумовлені саме execve() */
          use_clockid    : 1,   /* Використовувати специфічний clockid */
          context_switch : 1,   /* Записувати перемикання контексту */
          write_backward : 1,   /* Кільцевий буфер записується у зворотному напрямку */
          namespaces     : 1,   /* Записувати події зміни namespaces */
          ksymbol        : 1,   /* Записувати події завантаження kallsyms */
          bpf_event      : 1,   /* Записувати події завантаження/видалення BPF-програм */
          aux_output     : 1,   /* Перенаправляти вихід у AUX-буфер (Intel PT) */
          cgroup         : 1,   /* Записувати ідентифікатори cgroup */
          text_poke      : 1,   /* Записувати зміни коду ядра (kprobes/ftrace) */
          build_id       : 1,   /* Додавати Build-ID до подій MMAP2 */
          inherit_thread : 1,   /* Успадковувати лише потоками (не новими процесами) */
          remove_on_exec : 1,   /* Видаляти подію при виконанні execve() */
          sigtrap        : 1,   /* Надсилати SIGTRAP при переповненні замість NMI */
          __reserved_1   : 26;

    union {
        __u32 wakeup_events;    /* Кількість вибірок до генерування POLL_IN */
        __u32 wakeup_watermark; /* Кількість байтів у буфері до POLL_IN */
    };

    __u32 bp_type;              /* Тип HW Точки зупинки (HW_BREAKPOINT_R/W/X) */

    union {
        __u64 bp_addr;          /* Віртуальна адреса точки зупинки */
        __u64 kprobe_func;      /* Адреса або ім'я функції для kprobe */
        __u64 uprobe_path;      /* Шлях до ELF-файлу для uprobe */
        __u64 config1;          /* Додаткові параметри розширеного PMU */
    };

    union {
        __u64 bp_len;           /* Довжина маски точки зупинки (1, 2, 4, 8 байтів) */
        __u64 kprobe_addr;      /* Зсув всередині функції kprobe */
        __u64 probe_offset;     /* Зсув у файлі для uprobe */
        __u64 config2;          /* Додаткові параметри raw PMU */
    };

    __u64 branch_sample_type;   /* Бітова маска фільтрації подій LBR */
    __u64 sample_regs_user;     /* Маска CPU-регістрів користувача у вибірці */
    __u32 sample_stack_user;    /* Розмір сирого стеку користувача у вибірці */
    __s32 clockid;              /* Ідентифікатор годинника (CLOCK_MONOTONIC тощо) */
    __u64 sample_regs_intr;     /* Маска регістрів переривання у вибірці */
    __u32 aux_watermark;        /* Поріг водяного знака для AUX буфера */
    __u16 sample_max_stack;     /* Максимальна глибина кадру callchain */
    __u16 __reserved_2;
    __u32 aux_sample_size;      /* Розмір вибірки AUX даних */
    __u32 __reserved_3;
    __u64 sigtrap_data;         /* Пори користувача для SIGTRAP */
};
```
```cpp
// Обгортка створення конфігурації perf_event_attr у C++20
#include <linux/perf_event.h>
#include <cstdint>
#include <cstring>

namespace sys {
    inline perf_event_attr make_hardware_attr(std::uint64_t config, std::uint64_t sample_period) noexcept {
        perf_event_attr attr{};
        attr.type = PERF_TYPE_HARDWARE;
        attr.size = sizeof(perf_event_attr);
        attr.config = config;
        attr.sample_period = sample_period;
        attr.sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME;
        attr.disabled = 1;
        attr.exclude_kernel = 1;
        attr.exclude_hv = 1;
        return attr;
    }
}
```
:::

### Детальні значення прапорців точного саплінгу (`precise_ip`)

- `precise_ip == 0`: Класичний саплінг через NMI переривання. Допускає апаратний скід (skid) адреси `RIP` на кілька інструкцій вперед.
- `precise_ip == 1`: Спроба усунути скід за допомогою константного зсуву ядра.
- `precise_ip == 2`: Використання апаратного саплінгу (Intel PEBS або AMD IBS), де процесор заморожує точну адресу `RIP` безпосередньо у момент переповнення лічильника.
- `precise_ip == 3`: Апаратний саплінг із гарантією відсутності будь-якого скіду (Must have zero skid). Якщо кремній не може гарантувати точність, виклик `perf_event_open()` повертає помилку `EINVAL`.

---

## 3. Таблиці типів подій та бітових масок

### 3.1. Основні типи подій (`attr.type`)

- `PERF_TYPE_HARDWARE` (0): Узагальнені апаратні події PMU процесора (цикли, інструкції, промахи кешу).
- `PERF_TYPE_SOFTWARE` (1): Програмні лічильники ядра (page faults, context switches, cpu-migrations, alignment faults).
- `PERF_TYPE_TRACEPOINT` (2): Статичні точки трасування ядра Linux (ftrace events з `/sys/kernel/tracing/events/...`).
- `PERF_TYPE_HW_CACHE` (3): Високодеталізовані події апаратного кешу (L1D, L1I, LLC, ITLB, DTLB read/write/miss).
- `PERF_TYPE_RAW` (4): Сирі маски MSR-регістрів конкретного процесора (наприклад, конфігурація `0x5301cb` для Intel Core).
- `PERF_TYPE_BREAKPOINT` (5): Апаратні точки зупинки за доступом до пам'яті.

### 3.2. Апаратні події (`attr.config` при `attr.type == PERF_TYPE_HARDWARE`)

- `PERF_COUNT_HW_CPU_CYCLES` (0): Загальна кількість тактових імпульсів CPU.
- `PERF_COUNT_HW_INSTRUCTIONS` (1): Кількість успішно завершених інструкцій (retired instructions).
- `PERF_COUNT_HW_CACHE_REFERENCES` (2): Кількість звернень до кеш-пам'яті останнього рівня (LLC).
- `PERF_COUNT_HW_CACHE_MISSES` (3): Кількість промахів кеш-пам'яті останнього рівня (LLC misses).
- `PERF_COUNT_HW_BRANCH_INSTRUCTIONS` (4): Кількість виконаних інструкцій умовного та безумовного переходу.
- `PERF_COUNT_HW_BRANCH_MISSES` (5): Кількість хибно передбачених розгалужень (branch mispredictions).
- `PERF_COUNT_HW_BUS_CYCLES` (6): Кількість тактових імпульсів шини пам'яті.
- `PERF_COUNT_HW_STALLED_CYCLES_FRONTEND` (7): Такти простою конвеєра через затримку декодування інструкцій.
- `PERF_COUNT_HW_STALLED_CYCLES_BACKEND` (8): Такти простою конвеєра через очікування виконання операцій пам'яті.
- `PERF_COUNT_HW_REF_CPU_CYCLES` (9): Загальні такти CPU без урахування зміни частоти (scaled reference cycles).

### 3.3. Бітова маска вмісту вибірки (`attr.sample_type`)

Прапорці `sample_type` визначають, які саме поля записуються у кожну структуру `PERF_RECORD_SAMPLE` всередині кільцевого буфера:

- `PERF_SAMPLE_IP` (1U << 0): Записує вказівник на поточну інструкцію (`sample_ip`).
- `PERF_SAMPLE_TID` (1U << 1): Записує PID та TID процесу/потоку.
- `PERF_SAMPLE_TIME` (1U << 2): Записує високоточний часовий штамп (наносекунди з CLOCK_MONOTONIC).
- `PERF_SAMPLE_ADDR` (1U << 3): Записує віртуальну адресу пам'яті (для подій промахів кешу або валувань пам'яті).
- `PERF_SAMPLE_READ` (1U << 4): Записує значення лічильників у форматі `read_format`.
- `PERF_SAMPLE_CALLCHAIN` (1U << 5): Записує весь стек викликів (масив вказівників інструкцій IP).
- `PERF_SAMPLE_ID` (1U << 6): Записує унікальний 64-бітний ідентифікатор події.
- `PERF_SAMPLE_CPU` (1U << 7): Записує номер процесорного ядра, де сталася вибірка.
- `PERF_SAMPLE_PERIOD` (1U << 8): Записує поточний період вибірки.
- `PERF_SAMPLE_STREAM_ID` (1U << 9): Записує 64-бітний ідентифікатор потоку події.
- `PERF_SAMPLE_RAW` (1U << 10): Записує сирий двійковий дамп даних (наприклад, аргументи tracepoint).
- `PERF_SAMPLE_BRANCH_STACK` (1U << 11): Записує історію останніх гілок LBR.
- `PERF_SAMPLE_REGS_USER` (1U << 12): Записує зріз регістрів процесора у user-space.
- `PERF_SAMPLE_STACK_USER` (1U << 13): Записує сирий дамп стеку користувача.
- `PERF_SAMPLE_WEIGHT` (1U << 14): Записує апаратну затримку виконання (наприклад, затримка доступу до DRAM у тактах).

### 3.4. Прапорці формату читання (`attr.read_format`)

Параметр `read_format` задає структуру даних, яка повертається системним викликом `read()` при роботі у режимі підрахунку:

- `PERF_FORMAT_TOTAL_TIME_ENABLED` (1U << 0): Додає 64-бітне поле `time_enabled` (загальний час активності події).
- `PERF_FORMAT_TOTAL_TIME_RUNNING` (1U << 1): Додає 64-бітне поле `time_running` (час фактичного вимірювання на HW PMC).
- `PERF_FORMAT_ID` (1U << 2): Додає 64-бітний ідентифікатор події.
- `PERF_FORMAT_GROUP` (1U << 3): Зчитує значення усіх подій у групі за один виклик `read()`.
- `PERF_FORMAT_LOST` (1U << 4): Додає кількість втрачених подій.

---

## 4. Структура розділюваної пам'яті: struct perf_event_mmap_page

При виклику `mmap()` на файловому дескрипторі `perf` перша сторінка пам'яті (Page 0, розміром 4096 байтів) відводиться під заголовочну структуру управління `struct perf_event_mmap_page`.

:::tabs
```c
/* Заголовочна сторінка mmap буфера у C UAPI header <linux/perf_event.h> */
struct perf_event_mmap_page {
    __u32 version;              /* Версія структури ядра */
    __u32 compat_version;       /* Найменша сумісна версія */
    __u32 lock;                 /* Атомарний замок оновлення */
    __u32 index;                /* Апаратний індекс PMC регістру */
    __s64 offset;               /* Зсув для обчислення значення без syscall */
    __u64 time_enabled;         /* Загальний час активності події (наносекунди) */
    __u64 time_running;         /* Час фактичного виконання події на HW PMC */
    union {
        __u64 capabilities;
        struct {
            __u64 cap_bit0 : 1,
                  cap_user_rdpmc : 1, /* Дозволено пряме читання RDPMC з user-space */
                  cap_user_time  : 1, /* Дозволено пряме читання TSC з user-space */
                  cap_user_time_zero : 1,
                  cap_user_time_short: 1,
                  cap_cap_user_time_zero: 1,
                  cap_architectural_bits: 58;
        };
    };
    __u16 pmc_width;            /* Бітова ширина апаратного лічильника (наприклад, 48 біт) */
    __u16 time_shift;           /* Коефіцієнт зсуву для конвертації TSC у наносекунди */
    __u32 time_mult;            /* Множник для конвертації TSC у наносекунди */
    __u64 time_zero;            /* Базовий час для конвертації TSC */
    __u32 size;                 /* Розмір структури perf_event_mmap_page */

    __u64 data_head;            /* Курсор запису ядра (monotonically increasing) */
    __u64 data_tail;            /* Курсор читання користувача (підтримується user-space) */
    __u64 data_offset;          /* Зсув початку буфера даних (4096 байтів) */
    __u64 data_size;            /* Розмір буфера даних у байтах (2^N сторінок) */
    __u64 aux_head;             /* Курсор запису AUX буфера */
    __u64 aux_tail;             /* Курсор читання AUX буфера */
    __u64 aux_offset;           /* Зсув AUX буфера */
    __u64 aux_size;             /* Розмір AUX буфера */
};
```
```cpp
// Зчитування data_head у C++20 з використанням std::atomic_load_explicit
#include <linux/perf_event.h>
#include <atomic>
#include <cstdint>

namespace sys {
    inline std::uint64_t read_ring_buffer_head(const perf_event_mmap_page* page) noexcept {
        return std::atomic_load_explicit(
            reinterpret_cast<const std::atomic<std::uint64_t>*>(&page->data_head),
            std::memory_order_acquire
        );
    }
}
```
:::

### Формула обчислення наносекунд з інструкції RDTSC у user-space

Якщо прапор `cap_user_time` встановлено в 1, програма у користувацькому просторі може обчислити точний часовий штамп ядра без виклику системних функцій часу, прочитавши TSC через інструкцію `RDTSC`:

:::tabs
```c
#include <x86intrin.h>
#include <stdint.h>

uint64_t calculate_ns(uint64_t time_zero, uint32_t time_mult, uint16_t time_shift) {
    uint64_t tsc = __rdtsc();
    uint64_t quot = tsc >> time_shift;
    uint64_t rem  = tsc & ((1ULL << time_shift) - 1);
    return time_zero + quot * time_mult + ((rem * time_mult) >> time_shift);
}
```
```cpp
#include <x86intrin.h>
#include <cstdint>

namespace sys {
    inline std::uint64_t calculate_ns(std::uint64_t time_zero, std::uint32_t time_mult, std::uint16_t time_shift) noexcept {
        std::uint64_t tsc = __rdtsc();
        std::uint64_t quot = tsc >> time_shift;
        std::uint64_t rem  = tsc & ((1ULL << time_shift) - 1);
        return time_zero + quot * time_mult + ((rem * time_mult) >> time_shift);
    }
}
```
:::

---

## 5. Формати подій у буфері даних (PERF_RECORD_*)

Буфер даних починається за адресою `(char*)header + header->data_offset`. Кожна подія у буфері має вирівняний за 64-бітним кордоном заголовок `struct perf_event_header`:

:::tabs
```c
struct perf_event_header {
    __u32 type;                 /* Тип запису (PERF_RECORD_*) */
    __u16 misc;                 /* Додаткові прапорці середовища виконання */
    __u16 size;                 /* Загальний розмір запису у байтах (включаючи заголовок) */
};
```
```cpp
namespace sys {
    struct PerfEventHeaderWrapper {
        std::uint32_t type;
        std::uint16_t misc;
        std::uint16_t size;
    };
}
```
:::

### 5.1. Ключові типи записів `PERF_RECORD_*`

1. `PERF_RECORD_MMAP` (1): Звіт про відображення виконуваного файлу або лінкування бібліотеки у пам'ять. Містить `pid`, `tid`, `addr`, `len`, `pgoff` та `filename[]`.
2. `PERF_RECORD_LOST` (2): Звіт про втрачені вибірки через переповнення кільцевого буфера. Містить `id` події та `lost` (кількість пропущених подій).
3. `PERF_RECORD_COMM` (3): Звіт про зміну імені процесу (виклики `prctl(PR_SET_NAME)` або `execve`).
4. `PERF_RECORD_EXIT` (4): Звіт про завершення процесу або потоку (`sys_exit`).
5. `PERF_RECORD_THROTTLE` (5): Сигнал ядра про автоматичне зниження частоти вибірки через перевищення максимального ліміту навантаження CPU (`perf_cpu_time_max_percent`).
6. `PERF_RECORD_UNTHROTTLE` (6): Сигнал відновлення нормальної частоти вибірки.
7. `PERF_RECORD_FORK` (7): Звіт про створення нового дочірнього потоку або процесу (`sys_clone`/`sys_fork`).
8. `PERF_RECORD_SAMPLE` (9): Запис безпосередньої вибірки події. Структура залежить від маски `sample_type`.

### 5.2. Структура `PERF_RECORD_SAMPLE` при типовій конфігурації

Якщо `sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID | PERF_SAMPLE_TIME | PERF_SAMPLE_CALLCHAIN`, вибірка у буфері має наступну послідовність полів:

:::tabs
```c
struct sample_event {
    struct perf_event_header header;
    __u64 ip;                   /* Якщо встановлено PERF_SAMPLE_IP */
    __u32 pid, tid;             /* Якщо встановлено PERF_SAMPLE_TID */
    __u64 time;                 /* Якщо встановлено PERF_SAMPLE_TIME */
    __u64 nr;                   /* Кількість елементів у callchain (якщо PERF_SAMPLE_CALLCHAIN) */
    __u64 ips[1];               /* Масив вказівників інструкцій стеку викликів */
};
```
```cpp
#include <cstdint>
#include <vector>
#include <span>

namespace sys {
    struct ParsedSampleEvent {
        std::uint64_t ip;
        std::uint32_t pid;
        std::uint32_t tid;
        std::uint64_t time;
        std::vector<std::uint64_t> callchain;
    };
}
```
:::

---

## 6. Запити ioctl() для управління дескриптором

Керування станом лічильника або групи подій здійснюється через системний виклик `ioctl()` над відкритим дескриптором `fd`:

- `PERF_EVENT_IOC_ENABLE`: Вмикає вимірювання для даного дескриптора (або всієї групи, якщо передано прапор `PERF_IOC_FLAG_GROUP`).
- `PERF_EVENT_IOC_DISABLE`: Призупиняє вимірювання події.
- `PERF_EVENT_IOC_RESET`: Скидає поточне значення лічильника в 0.
- `PERF_EVENT_IOC_REFRESH`: Вмикає лічильник на виконання точно `N` переповнень, після чого він автоматично вимикається.
- `PERF_EVENT_IOC_PERIOD`: Динамічно змінює період вибірки `sample_period`.
- `PERF_EVENT_IOC_SET_FILTER`: Задає текстовий ftrace-фільтр для подій типу `PERF_TYPE_TRACEPOINT` (наприклад, `"common_pid == 1234"`).
- `PERF_EVENT_IOC_SET_BPF`: Прив'язує eBPF-програму типу `BPF_PROG_TYPE_PERF_EVENT` до дескриптора події.
