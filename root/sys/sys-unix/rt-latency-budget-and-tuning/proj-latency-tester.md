# ⚙️ Практичне вимірювання затримок реального часу та написання RT-циклу

Перевірити, чи справді система тримає обіцяний детермінізм, можна лише власним вимірювачем — ідейним аналогом індустріального `cyclictest`, який проходить суворий ланцюг ініціалізації: блокування віртуальної пам'яті, прогрів стека, `SCHED_FIFO`, прив'язка до ізольованого ядра — і аж тоді міряє, на скільки пізніше за розрахунковий момент його насправді розбудило ядро. Такий вимірювач будується у півтори сотні рядків мовами C та C++.

## 1. Архітектурне завдання та вимірювальна методологія

Головним показником якості та детермінізму системи реального часу є затримка пробудження потоку (Scheduling Wakeup Latency). Ця величина описує часову різницю між моментами, коли потік реального часу *повинен був розбудитися* згідно з планом, та моментом, коли він *фактично отримав CPU* і почав виконувати першу інструкцію у просторі користувача.

Для вимірювання цієї затримки створюється спеціалізований потік із високим пріоритетом реального часу, який виконує циклічні розрахунки через рівні інтервали часу. На відміну від звичайного бенчмарку продуктивності, який вимірює кількість операцій за секунду (throughput), вимірювач затримок шукає **найгірший випадок** (Worst-Case Latency). Затримка в 15 мікросекунд на 99,999 % ітерацій нічого не варта, якщо на одній ітерації зі ста тисяч стався викид (spike) до 15 мілісекунд, бо у реальному виробництві такий викид означає аварію.

### Повний алгоритм підготовки та виконання RT-циклу

1. **Блокування пам'яті (`mlockall`)**: Захист від затримок підкачування сторінок (Page Faults). Стандартний розподільник віртуальної пам'яті Linux використовує ліниве відображення сторінок (Demand Paging). Коли програма вперше звертається до виділеного буфера, виконання перериває Page Fault: ядро знаходить вільну фізичну сторінку, обнуляє її та вставляє у таблицю сторінок `PTE`. Одна сторінка коштує одиниці мікросекунд, і для циклу з періодом 1 мс це вже помітно; якщо ж сторінку витіснено у swap на диск, затримка сягає десятків мілісекунд. Виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` примусово завантажує і блокує всі сторінки віртуальної пам'яті у фізичній RAM.
2. **Попереднє прогрівання стека (Stack Prefaulting)**: Навіть після виклику `mlockall()` стек процесу росте динамічно. При кожному глибшому виклику функції або оголошенні локальних змінних стек розширюється, що може спровокувати Page Fault усередині критичного циклу. Щоб цього уникнути, потік на етапі ініціалізації оголошує на стеку локальний масив у кілька десятків кілобайтів (тут — 64 КБ) і записує по одному байту у кожну 4-кілобайтову сторінку. Це змушує ядро Linux заздалегідь виділити й заблокувати ці фізичні сторінки стека. Розмір беруть із запасом на найглибший ланцюг викликів робочого циклу, але значно менший за межу стека (`ulimit -s`, типово 8 МБ): масив на всю межу просто зірве стек на першому ж записі.
3. **Встановлення пріоритету реального часу (`SCHED_FIFO`)**: Переведення самого вимірювального потоку у клас `SCHED_FIFO` з пріоритетом від 80 до 99. Це гарантує, що потік витіснить будь-які стандартні процеси `SCHED_OTHER` та більшість потоків обробки переривань.
4. **Закріплення за ізольованим ядром CPU (CPU Affinity)**: Прив'язка потоку до конкретного ядра процесора, яке вилучено із загального планування за допомогою параметрів завантаження `isolcpus` та `nohz_full`. Це унеможливлює між'ядерну міграцію потоку та усуває затримки від скидання кешу L1/L2 та IPI-переривань.
5. **Виконання циклу з абсолютним таймером (`clock_nanosleep`)**: Цикл виконується із заданим періодом (наприклад, 1000 Гц = 1 мс / 1 000 000 нс). На кожній ітерації потік розраховує час наступного пробудження `T_next = T_prev + T_period` і засинає через `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t_next, NULL)`.
6. **Вимірювання та запис статистичних відхилень**: Одразу після прокидання потік зчитує поточний час `T_actual = clock_gettime()`, обчислює відхилення `Δ = T_actual - T_next` у мікросекундах і фіксує мінімальну, максимальну та середню затримку.

```
+-------------------------------------------------------------------+
| ІНІЦІАЛІЗАЦІЯ:                                                   |
| 1. mlockall(MCL_CURRENT | MCL_FUTURE)                              |
| 2. stack_prefault() (запис у 64 КБ стека)                         |
| 3. sched_setscheduler(SCHED_FIFO, prio=80)                        |
| 4. pthread_setaffinity_np(cpu_id)                                 |
+-------------------------------------------------------------------+
                                  │
                                  ▼
                     clock_gettime(CLOCK_MONOTONIC)
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │ ЦИКЛ ВИМІРЮВАННЯ (N ітерацій):       │
               │                                      │
               │ 1. T_next += T_period                │
               │ 2. clock_nanosleep(TIMER_ABSTIME)    │
               │ 3. T_actual = clock_gettime()        │
               │ 4. Delta = T_actual - T_next         │
               │ 5. Update min, max, avg, histogram   │
               └──────────────────────────────────────┘
                                  │
                                  ▼
+-------------------------------------------------------------------+
| ЗАВЕРШЕННЯ: Друк статистики, munlockall()                        |
+-------------------------------------------------------------------+
```

## 2. Апаратні джерела затримок та усунення C-states

Під час проведення вимірювань розробник може зіткнутися з ситуацією, коли навіть на ядрі з `PREEMPT_RT` періодично спостерігаються викиди затримки у сотню-другу мікросекунд. Найчастіша причина тут не програмна, а апаратна — механізми енергозбереження процесора:

1. **Глибокі стани сну CPU (C-states)**: Коли ядро процесора простоює, підсистема `cpuidle` переводить його в один із енергозберігаючих станів C1, C3, C6. Чим глибший стан, тим більше енергії економиться — і тим довше триває вихід із нього (увімкнення тактування, відновлення живлення, прогрів кешів): від одиниць мікросекунд для найдрібнішого C1 до сотні й більше для C6. Точні числа для конкретного процесора не вгадують, а читають із `/sys/devices/system/cpu/cpu0/cpuidle/state*/latency` — саме ці значення `cpuidle` і використовує, обираючи стан. Для систем реального часу C-states вимикаються через відкриття файлу `/dev/cpu_dma_latency` і запис у нього значення `0`, або через параметр ядра `intel_idle.max_cstate=0 processor.max_cstate=0`.
2. **Динамічна зміна частоти (P-states / Governors)**: Якщо регулятор частоти процесора встановлено у режим `powersave` або `schedutil`, процесор знижує тактову частоту під час сну потоку. При прокиданні RT-потоку регулятор не встигає миттєво підвищити частоту, і перші інструкції виконуються на зниженій частоті. На системах реального часу регулятор обов'язково переводиться у режим `performance` (`cpupower frequency-set -g performance`).
3. **Міграція між ядрами та кеш-промахи**: Якщо потік не прив'язаний до конкретного ядра CPU, планувальник може розбудити його на іншому ядрі. Робочий набір потоку лишається у кешах L1/L2 покинутого ядра, тож перші звернення після пробудження йдуть до кешу L3 або взагалі до пам'яті сусіднього NUMA-вузла (NUMA latency).

## 3. Реалізація мовами C та C++

Обидві реалізації проходять той самий ланцюг налаштувань і міряють ту саму величину в мікросекундах — різниця лише в тому, як мова тримає ресурси й помилки: у C кожен виклик перевіряється на місці, а звільнення (`munlockall()`, `close()`) розписане в кожній гілці виходу; у C++ блокування пам'яті та дескриптор `/dev/cpu_dma_latency` живуть у RAII-обгортках, а помилки повертаються через `std::expected`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>

#define ITERATIONS 10000
#define NSEC_PER_SEC 1000000000L
#define PERIOD_NSEC 1000000L /* 1 мілісекунда = 1 000 000 нс */
#define STACK_PREFAULT_SIZE (64 * 1024) /* 64 КБ — із запасом менше за межу стека */
#define PAGE_SIZE_BYTES 4096

/* Вимкнення C-states через /dev/cpu_dma_latency */
static int disable_cpu_cstates(void) {
    int fd = open("/dev/cpu_dma_latency", O_WRONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити /dev/cpu_dma_latency");
        return -1;
    }
    int32_t latency = 0; // 0 мкс дозволеної затримки
    if (write(fd, &latency, sizeof(latency)) != sizeof(latency)) {
        perror("Не вдалося записати у /dev/cpu_dma_latency");
        close(fd);
        return -1;
    }
    return fd; // Утримуємо відкритим на весь час роботи
}

static void stack_prefault(void) {
    volatile unsigned char dummy[STACK_PREFAULT_SIZE];
    /* По байту в кожну сторінку: змушує ядро підставити фізичні сторінки стека */
    for (size_t i = 0; i < STACK_PREFAULT_SIZE; i += PAGE_SIZE_BYTES) {
        dummy[i] = 0;
    }
}

static inline void timespec_add_ns(struct timespec *ts, long ns) {
    ts->tv_nsec += ns;
    while (ts->tv_nsec >= NSEC_PER_SEC) {
        ts->tv_nsec -= NSEC_PER_SEC;
        ts->tv_sec += 1;
    }
}

int main(int argc, char *argv[]) {
    struct sched_param param;
    struct timespec t_next, t_actual;
    cpu_set_t cpuset;
    long min_lat = LONG_MAX, max_lat = LONG_MIN, total_lat = 0;
    int done = 0; /* скільки ітерацій справді виміряно */
    int target_cpu = 1;

    if (argc > 1) {
        target_cpu = atoi(argv[1]);
    }

    printf("Запуск тестування затримки реального часу на CPU %d...\n", target_cpu);

    /* 1. Блокування пам'яті */
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed (потрібні права CAP_IPC_LOCK)");
        return EXIT_FAILURE;
    }

    /* 2. Прогрів стека */
    stack_prefault();

    /* 3. Вимкнення енергозбереження C-states */
    int cstate_fd = disable_cpu_cstates();

    /* 4. Прив'язка до конкретного ядра CPU */
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);
    /* pthread_* повертають код помилки й НЕ чіпають errno — perror тут збрехав би */
    int aff_ret = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    if (aff_ret != 0) {
        fprintf(stderr, "pthread_setaffinity_np failed: %s\n", strerror(aff_ret));
        munlockall();
        if (cstate_fd >= 0) close(cstate_fd);
        return EXIT_FAILURE;
    }

    /* 5. Встановлення RT-пріоритету SCHED_FIFO */
    memset(&param, 0, sizeof(param));
    param.sched_priority = 80;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("sched_setscheduler failed (потрібні права CAP_SYS_NICE)");
        munlockall();
        if (cstate_fd >= 0) close(cstate_fd);
        return EXIT_FAILURE;
    }

    /* 6. Початкова позначка часу */
    clock_gettime(CLOCK_MONOTONIC, &t_next);

    /* 7. Основний вимірювальний цикл */
    for (int i = 0; i < ITERATIONS; i++) {
        timespec_add_ns(&t_next, PERIOD_NSEC);

        int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t_next, NULL);
        if (ret != 0) {
            fprintf(stderr, "clock_nanosleep перервано: %s\n", strerror(ret));
            break;
        }

        clock_gettime(CLOCK_MONOTONIC, &t_actual);

        long diff_nsec = (t_actual.tv_sec - t_next.tv_sec) * NSEC_PER_SEC +
                         (t_actual.tv_nsec - t_next.tv_nsec);
        long diff_usec = diff_nsec / 1000;

        if (diff_usec < min_lat) min_lat = diff_usec;
        if (diff_usec > max_lat) max_lat = diff_usec;
        total_lat += diff_usec;
        done++;
    }

    /* Цикл могло обірвати сигналом на першій же ітерації — тоді міряти нічого */
    if (done == 0) {
        fprintf(stderr, "Жодної ітерації не виміряно.\n");
        if (cstate_fd >= 0) close(cstate_fd);
        munlockall();
        return EXIT_FAILURE;
    }

    printf("Результати тестування затримки (%d ітерацій):\n", done);
    printf("  Мінімальна затримка: %ld мкс\n", min_lat);
    printf("  Максимальна затримка: %ld мкс\n", max_lat);
    printf("  Середня затримка:    %.2f мкс\n", (double)total_lat / done);

    if (cstate_fd >= 0) close(cstate_fd);
    munlockall();
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <chrono>
#include <system_error>
#include <expected>
#include <memory>
#include <cstring>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>
#include <time.h>

// RAII для блокування пам'яті
class ScopedMemoryLock {
public:
    ScopedMemoryLock() {
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }
    }
    ~ScopedMemoryLock() {
        munlockall();
    }
    ScopedMemoryLock(const ScopedMemoryLock&) = delete;
    ScopedMemoryLock& operator=(const ScopedMemoryLock&) = delete;
};

// RAII для керування C-states через /dev/cpu_dma_latency
class ScopedCStateControl {
private:
    int fd_{-1};
public:
    ScopedCStateControl() {
        fd_ = open("/dev/cpu_dma_latency", O_WRONLY);
        if (fd_ >= 0) {
            int32_t latency = 0;
            if (write(fd_, &latency, sizeof(latency)) != sizeof(latency)) {
                close(fd_);
                fd_ = -1;
            }
        }
    }
    ~ScopedCStateControl() {
        if (fd_ >= 0) {
            close(fd_);
        }
    }
    [[nodiscard]] bool is_active() const noexcept { return fd_ >= 0; }
    ScopedCStateControl(const ScopedCStateControl&) = delete;
    ScopedCStateControl& operator=(const ScopedCStateControl&) = delete;
};

static void stack_prefault() noexcept {
    constexpr std::size_t stack_size = 64 * 1024; // 64 КБ, із запасом менше за межу стека
    constexpr std::size_t page_size = 4096;
    volatile unsigned char dummy[stack_size];
    // Саме масив на стеку, а не vector: купа тут не допомогла б — прогріваємо сторінки стека
    for (std::size_t i = 0; i < stack_size; i += page_size) {
        dummy[i] = 0;
    }
}

static std::expected<void, std::error_code> set_realtime_priority_and_affinity(int priority, int cpu_id) noexcept {
    // 1. Встановлення RT пріоритету
    sched_param param{};
    param.sched_priority = priority;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    // 2. Прив'язка до CPU: pthread_* повертає код помилки, errno не чіпає
    cpu_set_t cpuset{};
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (int res = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset); res != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(res)));
    }

    return {};
}

int main(int argc, char* argv[]) {
    try {
        int target_cpu = 1;
        if (argc > 1) {
            target_cpu = std::atoi(argv[1]);
        }

        std::cout << "Запуск C++ тесту затримки на CPU " << target_cpu << "...\n";

        ScopedMemoryLock mem_lock;
        stack_prefault();
        ScopedCStateControl cstate_ctrl;

        if (!cstate_ctrl.is_active()) {
            std::clog << "Попередження: не вдалося заблокувати C-states через /dev/cpu_dma_latency\n";
        }

        if (auto res = set_realtime_priority_and_affinity(80, target_cpu); !res) {
            std::cerr << "Не вдалося ініціалізувати RT/Affinity: " << res.error().message() 
                      << " (потрібні права root / CAP_SYS_NICE)\n";
            return 1;
        }

        constexpr int iterations = 10000;
        std::vector<long long> latencies_us;
        latencies_us.reserve(iterations);

        timespec t_next{};
        clock_gettime(CLOCK_MONOTONIC, &t_next);

        for (int i = 0; i < iterations; ++i) {
            t_next.tv_nsec += 1'000'000L; // +1 мілісекунда
            if (t_next.tv_nsec >= 1'000'000'000L) {
                t_next.tv_nsec -= 1'000'000'000L;
                t_next.tv_sec += 1;
            }

            if (int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t_next, nullptr); ret != 0) {
                std::cerr << "clock_nanosleep помилка: " << ret << "\n";
                break;
            }

            timespec t_actual{};
            clock_gettime(CLOCK_MONOTONIC, &t_actual);

            long long diff_ns = (t_actual.tv_sec - t_next.tv_sec) * 1'000'000'000LL +
                                (t_actual.tv_nsec - t_next.tv_nsec);
            latencies_us.push_back(diff_ns / 1000);
        }

        if (latencies_us.empty()) {           // цикл обірвало на першій же ітерації
            std::cerr << "Жодної ітерації не виміряно.\n";
            return 1;
        }

        auto [min_it, max_it] = std::minmax_element(latencies_us.begin(), latencies_us.end());
        double avg = std::accumulate(latencies_us.begin(), latencies_us.end(), 0.0) / latencies_us.size();

        std::cout << "Результати тестування затримки (" << latencies_us.size() << " ітерацій):\n"
                  << "  Мінімальна затримка: " << *min_it << " мкс\n"
                  << "  Максимальна затримка: " << *max_it << " мкс\n"
                  << "  Середня затримка:    " << avg << " мкс\n";

    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## 4. Автоматична діагностика аномалій через ftrace

Для виявлення причин окремих сплесків затримки (наприклад, якщо утиліта зафіксувала `max_lat > 50 мкс`) використовується зв'язок вимірювальної програми з підсистемою трасування ядра `ftrace`.

Сама по собі затримка нічого не пояснює: `max = 180 мкс` каже, що аварія була, але не каже, хто її спричинив. Відповідь є в буфері `ftrace` — щоправда, лише кілька мілісекунд, доки кільцевий буфер не затре подію новими записами. Тому буфер треба заморозити рукою самої вимірювальної програми, у той самий момент, коли вона побачила викид.

Алгоритм автоматичної зупинки трасування:
1. Перед запуском утиліта-обгортка вмикає трасувальник `wakeup_rt` (як показано в основній статті) і скидає попередній максимум.
2. Вимірювальний цикл дістає одну умову: щойно обчислена затримка `diff_usec` перевищує поріг (скажімо, 50 мкс), програма відкриває `/sys/kernel/tracing/tracing_on` і записує туди `0`. Файловий дескриптор для цього відкривають **заздалегідь**, на етапі ініціалізації, — `open()` усередині критичного циклу сам був би джерелом затримки.
3. Запис `0` миттєво заморожує кільцевий буфер у момент виникнення аномалії.
4. Інженер читає `/sys/kernel/tracing/trace` і бачить точний ланцюг викликів ядра (callgraph), що спричинив затримку — від конкретного драйвера до утриманого `raw_spinlock_t`.

Той самий прийом застосовний і без власної програми: `cyclictest --breaktrace=50 --tracemark` зупиняє трасування сам, щойно затримка перевищила задане число мікросекунд.

## 5. Практичні пастки під час розробки додатка реального часу

Розробка ПЗ під `PREEMPT_RT` вимагає повної відмови від стандартних патернів програмування загального призначення:

1. **Динамічне виділення пам'яті (`malloc` / `new`)**: У критичному циклі реального часу використання виділення пам'яті заборонено. Розподільник пам'яті (`ptmalloc`, `jemalloc`) може утримувати внутрішні м'ютекси, здійснювати системні виклики `brk` / `mmap` або запускати консолідацію вільних блоків, що дає затримки до сотень мікросекунд. Всі буфери виділяються заздалегідь при старті програми.
2. **Синхронне логування та вивід у консоль**: Виклики `printf()`, `std::cout` або запис у файл `fprintf()` є синхронними операціями виводу, які блокуються на локах буферів tty або дискового I/O. Вивід у лог повинен виконуватися за патерном Lock-Free Single-Producer Single-Consumer (SPSC) кільцевого буфера: RT-потік скидає повідомлення у безблокову чергу, а окремий низькопріоритетний фоновий потік вичищає чергу і записує дані на диск.
3. **Не-RT м'ютекси у системних бібліотеках**: Багато стандартних функцій усередині беруть звичайні `pthread_mutex_t` без підтримки Priority Inheritance — `syslog()` тримає лок журналу, `getaddrinfo()` і `gethostbyname()` — локи резолвера, `dlopen()` — лок динамічного завантажувача, а будь-який `printf()` — лок свого `FILE`. Кожен такий виклик у критичному циклі відчиняє двері неконтрольованій інверсії пріоритетів. Власні м'ютекси програми цієї вади позбавляють одним рядком: `pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT)` перед `pthread_mutex_init()` — і лок починає користуватися тим самим PI-механізмом ядра, що й `rt_mutex`.
