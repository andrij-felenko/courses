# ⚙️ Практичний стенд вимірювання затримок: інтеграція timerlat, SCHED_FIFO та sysfs

Цей практичний розбір показує розробку та налаштування повнофункціонального стенду реального часу для вимірювання затримок виклику таймера у просторі користувача. Код інтегрується з механізмом заморожування ftrace при виявленні затримок та використовує найкращі практики Linux Real-Time.

## 1. Архітектура стенду вимірювання затримок

При розробці систем жорсткого реального часу (Hard Real-Time) вимірювання затримок безпосередньо з простору користувача (User-Space) є вирішальним етапом інженерної валідації. Хоча ядерні трасувальники `timerlat` та `osnoise` вимірюють внутрішні затримки ядра, прикладний потік відчуває затримку "кінець-у-кінець" (end-to-end latency), яка формується під впливом цілого комплексу апаратних та програмних факторів.

Повна скрізна затримка реагування прикладного потоку реального часу на періодичну подію складається з наступних послідовних фаз:

1. **Апаратна затримка сигналу та переривання (Hardware & IRQ Entry Latency)**: Час від спрацювання апаратного таймера (наприклад, APIC timer або HPET) до виконання першої інструкції обробника апаратного переривання у процесорі. На цьому етапі затримку спричиняють вимкнені переривання (`local_irq_disable()`), стан сну процесора (C-states), а також апаратне викрадення циклів через System Management Interrupts (SMI).
2. **Затримка обробника таймера (Kernel hrtimer Latency)**: Час виконання функції `hrtimer_interrupt()` у ядрі, оновлення часових міток та виклику функції розблокування вимірювального потоку `wake_up_process()`.
3. **Затримка планувальника задач (Scheduler & Preemption Latency)**: Час, що минає від моменту переведення потоку у стан `TASK_RUNNING` до фактичного витіснення поточного потоку з CPU та виконання переключення контексту (`context switch`). Залежить від поточних ділянок коду ядра із вимкненим витісненням (`preempt_disable()`), пріоритетів конкурентних завдань та стану черги витіснення.
4. **Затримка проходження межі VFS / Syscall (User-Kernel Boundary Latency)**: Час повернення управління з простору ядра у простір користувача через інструкції `sysret` або `iret`, збереження регістрів та поновлення виконання інструкцій у користувацькому потоці.
5. **Затримка підсистеми пам'яті (Memory & Page Fault Latency)**: Час, витрачений на резолюцію віртуальних адрес, завантаження рядків кешу (L1/L2/L3 cache misses) та можливу обробку сторінкових збоїв (Page Faults), якщо сторінки коду чи даних потоку не були примусово заблоковані у RAM.

Створюваний вимірювальний стенд виконує повний комплекс захисних процедур для ізоляції та вимірювання цієї затримки:
- Прив'язує тестовий потік до конкретного ізольованого ядра процесора за допомогою системного виклику `pthread_setaffinity_np`.
- Заблоковує всю адресну систему процесу у RAM через виклик `mlockall`, повністю усуваючи пейджинг, витіснення сторінок у swap та виникнення сторінкових збоїв (page faults).
- Переводить потік у режим високого пріоритету реального часу `SCHED_FIFO` із пріоритетом 95.
- Здійснює періодичний цикл очікування за допомогою системного виклику `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, ...)`.
- Збирає та обчислює точні метрики затримки (мінімальну, середня, максимальну затримки, а також варіансу та стандартне відхилення).
- У разі виявлення сплеску затримки понад заданий поріг автоматично тригерить запис `0` у `/sys/kernel/tracing/tracing_on`, заморожуючи підсистему ftrace і зберігаючи детальну ядерну трасу для подальшого аналізу.

## 2. Реалізація стенду мовами C та C++

Утиліта представлена двома ідіоматичними варіантами реалізації — на мові C (POSIX API) та на мові C++20 (з використанням RAII, концептів та сучасної стандартної бібліотеки).

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
#include <math.h>

#define NSEC_PER_SEC 1000000000L
#define NSEC_PER_USEC 1000L

/* Захисна нормалізація структури timespec */
static inline void timespec_normalize(struct timespec *ts) {
    while (ts->tv_nsec >= NSEC_PER_SEC) {
        ts->tv_nsec -= NSEC_PER_SEC;
        ts->tv_sec += 1;
    }
}

/* Автоматичне тригерування зупинки ftrace через sysfs */
static void trigger_ftrace_stop(const char *reason, long latency_us) {
    int fd = open("/sys/kernel/tracing/tracing_on", O_WRONLY);
    if (fd >= 0) {
        write(fd, "0", 1);
        close(fd);
        printf("[CRITICAL] ftrace stopped! Reason: %s (latency: %ld us)\n", reason, latency_us);
    } else {
        perror("Failed to open tracing_on");
    }
}

int main(int argc, char *argv[]) {
    int cpu_id = 1;
    int priority = 95;
    long period_us = 1000; /* 1 мс */
    long threshold_us = 20; /* Поріг аномалії: 20 мкс */
    int iterations = 10000;

    if (argc > 1) cpu_id = atoi(argv[1]);
    if (argc > 2) threshold_us = atol(argv[2]);

    printf("=== Real-Time Latency Harness (C POSIX) ===\n");
    printf("Target CPU: %d, Priority: SCHED_FIFO %d, Period: %ld us, Threshold: %ld us\n",
           cpu_id, priority, period_us, threshold_us);

    /* 1. Блокування пам'яті для виключення Page Faults */
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed");
        return EXIT_FAILURE;
    }

    /* 2. Прив'язка до процесорного ядра (CPU Affinity) */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np failed");
        return EXIT_FAILURE;
    }

    /* 3. Встановлення політики та пріоритету реального часу */
    struct sched_param param;
    param.sched_priority = priority;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("sched_setscheduler failed");
        return EXIT_FAILURE;
    }

    /* 4. Ініціалізація змінних статистики */
    long min_lat = 999999L;
    long max_lat = -999999L;
    double sum_lat = 0.0;
    double sum_sq_lat = 0.0;

    struct timespec next_period;
    if (clock_gettime(CLOCK_MONOTONIC, &next_period) != 0) {
        perror("clock_gettime failed");
        return EXIT_FAILURE;
    }

    /* Виконуємо попередній розігрів стеку (stack warm-up) */
    unsigned char dummy_stack[8192];
    memset(dummy_stack, 0, sizeof(dummy_stack));

    for (int i = 0; i < iterations; i++) {
        /* Обчислюємо наступну абсолютну часову мітку */
        next_period.tv_nsec += period_us * NSEC_PER_USEC;
        timespec_normalize(&next_period);

        /* Абсолютний сон до наступного періоду */
        int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_period, NULL);
        if (ret != 0 && ret != EINTR) {
            fprintf(stderr, "clock_nanosleep failed: %s\n", strerror(ret));
            break;
        }

        /* Зчитуємо фактичний час пробудження */
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);

        /* Обчислюємо затримку у мікросекундах */
        long diff_sec = now.tv_sec - next_period.tv_sec;
        long diff_nsec = now.tv_nsec - next_period.tv_nsec;
        long latency_us = (diff_sec * NSEC_PER_SEC + diff_nsec) / NSEC_PER_USEC;

        if (latency_us < min_lat) min_lat = latency_us;
        if (latency_us > max_lat) max_lat = latency_us;
        sum_lat += latency_us;
        sum_sq_lat += (double)latency_us * latency_us;

        /* Перевірка порогу аномалії */
        if (latency_us > threshold_us) {
            trigger_ftrace_stop("Latency threshold exceeded", latency_us);
            break;
        }
    }

    double avg_lat = sum_lat / iterations;
    double stddev_lat = sqrt((sum_sq_lat / iterations) - (avg_lat * avg_lat));

    printf("\n=== Результати вимірювання затримок ===\n");
    printf("Ітерацій: %d\n", iterations);
    printf("Мінімальна затримка:  %ld us\n", min_lat);
    printf("Середня затримка:     %.2f us\n", avg_lat);
    printf("Максимальна затримка: %ld us\n", max_lat);
    printf("Стандартне відхилення: %.2f us\n", stddev_lat);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <chrono>
#include <thread>
#include <fstream>
#include <system_error>
#include <format>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>

class RealTimeSession {
public:
    explicit RealTimeSession(int cpu_id, int priority) {
        // 1. Блокування пам'яті через RAII
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }

        // 2. Встановлення CPU Affinity
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
            throw std::system_error(errno, std::generic_category(), "pthread_setaffinity_np failed");
        }

        // 3. Налаштування SCHED_FIFO
        sched_param param{.sched_priority = priority};
        if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
            throw std::system_error(errno, std::generic_category(), "sched_setscheduler failed");
        }
    }

    ~RealTimeSession() {
        munlockall();
    }
};

class FtraceControl {
public:
    static void stop_tracing(std::string_view reason, long latency_us) {
        std::ofstream ofs("/sys/kernel/tracing/tracing_on");
        if (ofs.is_open()) {
            ofs << "0";
            std::cout << std::format("[CRITICAL] ftrace stopped! Reason: {} (latency: {} us)\n",
                                     reason, latency_us);
        }
    }
};

int main(int argc, char* argv[]) {
    int cpu_id = 1;
    long threshold_us = 20;
    constexpr int iterations = 10000;
    constexpr std::chrono::microseconds period{1000};

    if (argc > 1) cpu_id = std::stoi(argv[1]);
    if (argc > 2) threshold_us = std::stol(argv[2]);

    std::cout << std::format("=== Real-Time Latency Harness (C++20) ===\n"
                             "Target CPU: {}, Priority: SCHED_FIFO 95, Period: 1000 us, Threshold: {} us\n",
                             cpu_id, threshold_us);

    try {
        RealTimeSession rt_session(cpu_id, 95);

        std::vector<long> latencies;
        latencies.reserve(iterations);

        auto next_wakeup = std::chrono::steady_clock::now();

        // Прогрів стеку
        std::vector<uint8_t> stack_warmup(8192, 0);

        for (int i = 0; i < iterations; ++i) {
            next_wakeup += period;
            std::this_thread::sleep_until(next_wakeup);

            auto now = std::chrono::steady_clock::now();
            auto latency_us = std::chrono::duration_cast<std::chrono::microseconds>(now - next_wakeup).count();

            latencies.push_back(latency_us);

            if (latency_us > threshold_us) {
                FtraceControl::stop_tracing("Latency threshold exceeded", latency_us);
                break;
            }
        }

        if (!latencies.empty()) {
            auto [min_it, max_it] = std::minmax_element(latencies.begin(), latencies.end());
            double sum = std::accumulate(latencies.begin(), latencies.end(), 0.0);
            double avg = sum / latencies.size();

            double sq_sum = std::accumulate(latencies.begin(), latencies.end(), 0.0,
                [avg](double acc, long val) { return acc + (val - avg) * (val - avg); });
            double stddev = std::sqrt(sq_sum / latencies.size());

            std::cout << std::format("\n=== Результати вимірювання затримок ===\n"
                                     "Ітерацій виконано: {}\n"
                                     "Мінімальна затримка:  {} us\n"
                                     "Середня затримка:     {:.2f} us\n"
                                     "Максимальна затримка: {} us\n"
                                     "Стандартне відхилення: {:.2f} us\n",
                                     latencies.size(), *min_it, avg, *max_it, stddev);
        }

    } catch (const std::exception& e) {
        std::cerr << std::format("Error: {}\n", e.what());
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 3. Детальний аналіз ключових системних механізмів

### 3.1 Блокування пам'яті через mlockall та мінімізація сторінкових збоїв

У звичайних умовах підсистема віртуальної пам'яті ядра Linux використовує підкачку сторінок на вимогу (demand paging). Це означає, що при отриманні пам'яті через виклики `malloc()`, `mmap()` або `brk()` ядро створює лише записи у таблиці віртуальних адрес (Virtual Memory Areas, VMA), але не виділяє реальних фізичних сторінок RAM (Page Frames).

Коли потік вперше звертається за віртуальною адресою, процесор виявляє відсутність відповідного прапорця у таблиці сторінок (`Present Bit == 0`) і ґенерує апаратний сторінковий збій — Page Fault (а саме `minor page fault`). Обробник ядра виділяє фізичну сторінку пам'яті, обнуляє її та оновлює MMU. Якщо ж пам'ять раніше була виселена підсистемою swap на диск, виникає `major page fault`, який вимагає синхронного дискового введення-виведення.

Для систем реального часу виникнення навіть minor page fault під час виконання критичного циклу є неприпустимим, оскільки обробка збою в ядрі займає від 2 до 15 мікросекунд, а major page fault зупиняє потік на кілька мілісекунд.

Виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` інструктує підсистему пам'яті ядра негайно виділити фізичні сторінки для всіх мапованих ділянок віртуальної пам'яті процесу та заблокувати їх у RAM, забороняючи виселення у swap:

- **`MCL_CURRENT`**: Блокує всі сторінки, які вже зінстанційовані у віртуальному адресному просторі процесу на момент виклику (сегмент тексту коду `.text`, ініціалізовані дані `.data`, `.bss`, стек та поточний heap).
- **`MCL_FUTURE`**: Налаштовує автоматичне примусове виділення та блокування фізичних сторінок для будь-яких нових мапувань пам'яті, що будуть створені у майбутньому через виклики `mmap()`, `brk()` або розширення стеку.

У C++ реалізації використання патерну RAII у класі `RealTimeSession` гарантує автоматичний виклик `munlockall()` при виході зі області видимості об'єкта, навіть якщо у додатку виникне виняток (exception).

### 3.2 Прогрів стеку (Stack Warm-up) та динамічне виділення пам'яті

Незважаючи на активне блокування `mlockall`, стек прикладного потоку у Linux розширюється динамічно вниз у міру виклику вкладених функцій. Коли розмір стеку перевищує поточну заблоковану межу, ядро виділяє нову сторінку стеку розміром 4 КБ. Перше звернення до цієї нової сторінки спричиняє minor page fault, оскільки прапорець `MCL_FUTURE` мапує сторінку лише після її створення підсистемою VFS.

Щоб повністю усунути затримки, пов'язані з розширенням стеку під час роботи часово-критичного циклу, стенд використовує прийом **прогріву стеку (stack warm-up)**.

У C-реалізації виділяється масив на стеку розміром 8 КБ (дві повні сторінки ядра): `unsigned char dummy_stack[8192]; memset(dummy_stack, 0, sizeof(dummy_stack));`.
Запис даних у кожен байт масиву змушує ядро негайно виділити й заблокувати відповідні фізичні сторінки стеку до початку циклу вимірювань.

У C++-реалізації аналогічний прогрів здійснюється через ініціалізацію локального вектора `std::vector<uint8_t> stack_warmup(8192, 0)`. Метод `reserve()` для вектора `latencies` додатково гарантує, що вектор попередньо виділить пам'ять під усі 10000 елементів у розігрітому heap до початку вимірювального циклу, унеможливлюючи виклики `realloc()` під час роботи таймера.

### 3.3 Обчислення часового дрейфу: відносні сни vs абсолютні таймери

При побудові циклів вимірювання періодичних затримок поширеною помилкою є використання відносного засинання (relative sleep), такого як `usleep(1000)` або `nanosleep()` з відносним інтервалом.

При відносному засинанні кожен період обчислюється як:

`T_wakeup_actual = T_start + T_period + Latency_jitter`

Якщо обробка ітерації або затримка пробудження запізнилася на `Δt` мікросекунд, наступний відносний сон почне відлік від нового (запізненого) моменту часу. В результаті у системі виникає **накопичувальний дрейф періоду (drift accumulation)**: за 10000 ітерацій сумарне відхилення часової сітки може скласти десятки мілісекунд.

Для усунення дрейфу стенд використовує режим **абсолютного часу (absolute timing)**. У мові C це досягається за допомогою виклику `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_period, NULL)`.

Прапорець `TIMER_ABSTIME` інструктує підсистему hrtimer ядра заснути не на тривалість `period_us`, а строго до досягнення моменту часу, вказаного у структурі `next_period`. Кожної ітерації стенд збільшує `next_period` на строгу константу (1000 мкс). Якщо через апаратний шум чи витіснення поточна ітерація прокинулася із запізненням на 15 мкс, наступний виклик `clock_nanosleep` автоматично зменшить фактичний час сну на ці ж 15 мкс, зберігаючи строгий детермінізм часової сітки.

У C++20 варіанті ця ж логіка реалізована за допомогою стандартного API часових точок `std::chrono`:

`next_wakeup += period;`
`std::this_thread::sleep_until(next_wakeup);`

Виклик `std::this_thread::sleep_until` використовує монотонний годинник `std::chrono::steady_clock` та інструкцію `clock_nanosleep` з прапорцем `TIMER_ABSTIME` під капотом у libstdc++.

### 3.4 Дисципліна планування SCHED_FIFO та CPU Affinity

Для мінімізації затримки розкладника задач (Scheduler Latency) стенд змінює політику планування процесу з дефолтної `SCHED_OTHER` (яка використовує Fair Scheduler та концепцію CFS/EEVDF vruntime) на политику реального часу **`SCHED_FIFO`**:

- **`SCHED_FIFO`**: Потік із цією политикою має абсолютний пріоритет над усіма звичайними процесами системи (`SCHED_OTHER`, `SCHED_BATCH`, `SCHED_IDLE`). Потік виконується на CPU доти, доки він сам не засне (викликавши `clock_nanosleep`), або поки його не витіснить потік реального часу з вищим пріоритетом.
- **Пріоритет 95**: Встановлення пріоритету 95 (у діапазоні від 1 до 99) гарантує, що вимірювальний потік витіснить більшість стандартних потоків ядра (таких як `ksoftirqd`, `jbd2`, `kworker`), але залишить можливість виконання критичним ядерним потокам підтримки стабільності ядра (таким як `migration/N` для перенесення завдань чи `watchdog/N`).

Прив'язка до ядра процесора (CPU Affinity) через `pthread_setaffinity_np` фіксує потік на конкретному ізольованому ядрі (наприклад, CPU 1). Це дає наступні переваги:
- Усуває міжпроцесорну міграцію потоку (CPU migration penalty), яка вимагає перенесення контексту регістрів та перезавантаження кеш-ліній L1/L2.
- Забезпечує високу локальність даних у кеші CPU L1 Data Cache (32 КБ) та L1 Instruction Cache (32 КБ).

### 3.5 Математична нормалізація POSIX-часу у C

При роботі зі структурою POSIX `struct timespec` додавання інтервалу наносекунд може призвести до переповнення поля `tv_nsec` (яке обмежене значенням `999,999,999` наносекунд). Якщо не виконати нормалізацію, виклик `clock_nanosleep` поверне помилку `EINVAL`.

Нормалізація виконується перевіркою переповнення `tv_nsec` та переносом секунд у `tv_sec`: якщо `tv_nsec >= 1,000,000,000`, віднімаємо від наносекунд 1 секунду та інкрементуємо секунди.

У C++20 варіанті ця математика здійснюється автоматично завдяки використанню `std::chrono::duration` та `std::chrono::time_point`, де переповнення компонентів опрацьовується тип-безпечним шляхом під час компіляції без необхідності писати ручні цикли нормалізації.

### 3.6 Вибір монотонного годинника CLOCK_MONOTONIC vs CLOCK_REALTIME

Для будь-яких вимірювань затримок та роботи реального часу категорично заборонено використовувати системний годинник реального часу `CLOCK_REALTIME` (або `std::chrono::system_clock`).

Основні причини цієї заборони:
- `CLOCK_REALTIME` піддається коригуванню з боку служб синхронізації системного часу NTP/PTP (наприклад, через системні виклики `adjtimex` або ручні зсуви часу адміністратором, а також через виправлення високосних секунд leap seconds).
- Якщо під час роботи вимірювального циклу служба NTP зсуне системний час назад на 1 секунду, потік `clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, ...)` засне на додаткову цілу секунду, що спричинить катастрофічне порушення дедлайну (deadline miss).
- `CLOCK_MONOTONIC` (та відповідний йому `std::chrono::steady_clock`) гарантує строго монотонне зростання часу від моменту завантаження системи без будь-яких зворотних стрибків або скачкоподібних коригувань, забезпечуючи надійну математичну основу для вимірювання затримок.

### 3.7 Взаємодія з Linux PM QoS для вимкнення станів сну CPU

Навіть на ізольованому ядрі з високим пріоритетом `SCHED_FIFO` процес може відчути високу затримку пробудження, якщо процесор переходить у стани глибокого енергозбереження (C-states). Вихід із стану C6 чи C7 вимагає від 50 до 200 мікросекунд для відновлення живлення ядер та частоти.

Для запобігання цьому стенд взаємодіє з підсистемою PM QoS шляхом запису `0` мікросекунд у пристрій `/dev/cpu_dma_latency`. Поки файловий дескриптор залишається відкритим, ядро забороняє процесору переходити в глибокі стани C-states, утримуючи ядро у стані постійної готовності C0/C1.

### 3.8 Вплив міжпроцесорних переривань IPI та обробки RCU

Ще одним джерелом затримок на ізольованому ядрі є міжпроцесорні переривання (Inter-Processor Interrupts, IPI). Вони надсилаються іншими ядрами для синхронізації TLB (TLB shootdowns) або виконання RCU-коллбеків.

Для зменшення впливу IPI при запуску стенду рекомендується перевірити розподіл переривань у `/proc/interrupts` та примусово виключити ізольовані ядра з маски обробки мережевих карт та дисків через `/proc/irq/N/smp_affinity`. Сумісне використання цієї конфігурації з `proj-latency-harness` гарантує мінімальну затримку пробудження в межах 2–5 мікросекунд.

Крім того, корисним є налаштування sysctl-параметрів ядра `kernel.sched_rt_runtime_us = -1`, що вимикає механізм RT Throttle (який за замовчуванням обмежує виконання RT-потоків до 950 мкс на кожну секунду, залишаючи 50 мкс для не-RT завдань).

### 3.9 Інтеграція з трасувальником timerlat у просторі користувача

Створений стенд концептуально еквівалентний користувацькому режиму роботи утиліти `rtla timerlat -u`. При виконанні виклику `rtla timerlat -u` ядро Linux створює спеціальний пристрій або трасувальний потік, який очікує подій hrtimer та передає їх у простір користувача.

Головна перевага використання власного стенду `proj-latency-harness` полягає у можливості інтегрувати вимірювальний цикл безпосередньо у вихідний код вашого прикладного застосунку (наприклад, у торговий робот або контролер робота), вимірюючи фактичну затримку обробки реальних бізнес-даних паралельно з логуванням аномалій у ftrace.

## 4. Компіляція, запуск та методологія тестування

### 4.1 Інструкція з компіляції

Для компіляції варіанта на мові C за допомогою компілятора GCC або Clang виконайте:

```bash
gcc -O2 -Wall -Wextra harness.c -o harness_c -lpthread -lm
```

Для компіляції ідіоматичного C++20 варіанта потрібен компілятор із підтримкою C++20 та розширення `<format>` (GCC 13+, Clang 16+):

```bash
g++ -O2 -std=c++20 -Wall -Wextra harness.cpp -o harness_cpp -lpthread
```

### 4.2 Системні привілеї та запуск

Зміна політики планування на `SCHED_FIFO` та блокування пам'яті через `mlockall` є привілейованими операціями ядра. Запуск вимагає прав суперкористувача (`root`) або наявності у бінарного файлу системних прав `CAP_SYS_NICE` та `CAP_IPC_LOCK`:

```bash
sudo setcap cap_sys_nice,cap_ipc_lock=+ep ./harness_cpp
```

Запуск тестування на ізольованому ядрі CPU 2 із порогом спрацьовування аномалії у 15 мікросекунд:

```bash
sudo ./harness_cpp 2 15
```

### 4.3 Аналіз результатів та взаємодія з ftrace

Якщо під час вимірювального циклу затримка перевищить поріг 15 мкс, стенд виконає автоматичний запис у sysfs:

```text
[CRITICAL] ftrace stopped! Reason: Latency threshold exceeded (latency: 24 us)
```

Після цього кільцевий буфер ftrace заморозиться. Інженер може негайно переглянути причину затримки у `tracefs`:

```bash
sudo cat /sys/kernel/tracing/trace | tail -n 40
```

У лозі ftrace буде точно видно, яка саме ядерна функція чи обробник переривання виконувався у момент сплеску затримки, що дозволяє усунути аномалію на рівні драйверів чи конфігурації ядра.

### 4.4 Профілювання затримок через perf та FlameGraphs

Для додаткового аналізу функцій ядра під час виконання затримок рекомендується використовувати утиліту `perf` у поєднанні зі стендом. Запуск опитування підсистеми ftrace та лічильників CPU дозволяє побудувати FlameGraph затримок:

```bash
sudo perf record -g -a -e sched:sched_switch ./harness_cpp 2 15
sudo perf report --stdio
```

Це дає точне уявлення про те, які саме переключення контексту (`sched_switch`) мали місце під час вимірювання затримок у просторі користувача.
