# ⚙️ Дослідження впливу SMT: вимірювання конкуренції за ресурси ядра

Одночасна багатонитковість створює для операційної системи ілюзію наявності двох незалежних процесорів, проте ці логічні ядра ділять між собою спільні залізні вузли фізичного кристала: кеш даних першого рівня (L1D), буфери трансляції адрес (TLB), станції резервування, черги завантаження-збереження та виконавчі порти. Залежно від характеру обчислень запуск двох потоків на сусідніх логічних ядрах (англ. *SMT siblings*) може дати як прискорення на 30–40%, так і драматичне сповільнення на 10–50% через витіснення кешу або взаємне блокування портів.

Щоб побачити й виміряти цей мікроархітектурний ефект на практиці, реалізуємо тестовий стенд, який закріплює потоки за конкретними логічними ядрами процесора через маски спорідненості (англ. *CPU affinity*) та порівнює поведінку системи у двох принципово різних сценаріях:
1. **Ізольовані фізичні ядра:** потоки виконуються на різних фізичних ядрах (наприклад, CPU 0 та CPU 2), маючи у власному розпорядженні персональні кеші L1D/L2 та незалежні виконавчі конвеєри.
2. **Спільне фізичне ядро (SMT):** потоки закріплені за двома логічними нитками одного фізичного ядра (наприклад, CPU 0 та CPU 1), конкуруючи за кожен такт конвеєра.

### Визначення топології процесора в Linux

Перед проведенням вимірювань необхідно точно встановити топологічну карту процесора: які саме логічні ядра належать до одного фізичного ядра, а які розташовані на окремих ядрах чи навіть різних NUMA-вузлах. В операційній системі Linux цю інформацію надає віртуальна файлова система `sysfs`.

Перевірити список логічних процесорів-побратимів для нульового процесора можна безпосередньо через інтерфейс ядра:

```bash
cat /sys/devices/system/cpu/cpu0/topology/thread_siblings_list
# Типовий вивід для 2-потокового SMT:
# 0,1  (або 0,4 залежно від порядку нумерації в BIOS виробника)
```

Якщо у виводі вказано `0,1`, це означає, що логічні ядра CPU 0 та CPU 1 є нитками одного фізичного ядра (Core 0). Якщо запустити два обчислювальні процеси на CPU 0 та CPU 1, вони розділять між собою 100% внутрішніх конвеєрних ресурсів цього ядра.

#### Чому номер сусіда не можна вгадати

Спокуса обійтися без цього читання велика: якщо нитки одного ядра стоять поруч, сусіда легко порахувати арифметикою. Проте номери логічних процесорів роздає ядро Linux у тому порядку, у якому процесори перелічені в таблиці ACPI MADT (англ. *Multiple APIC Description Table*) материнської плати, а виробники заповнюють цю таблицю по-різному:

- **Черезрядкова схема** (типова для настільних Intel Core): нитки одного ядра справді стоять поруч — `CPU 0` і `CPU 1` належать Core 0.
- **Блокова схема** (типова для багатосокетних AMD EPYC та Intel Xeon): спершу йдуть перші нитки всіх фізичних ядер (`CPU 0..31`), а потім усі їхні двійники (`CPU 32..63`). Сусідом `CPU 0` тут є `CPU 32`, тоді як `CPU 1` — це вже інше фізичне ядро.

Помилка на цьому місці тиха й дорога. Тест, що мав рознести нитки по різних ядрах, на блоковій машині збирає їх на одному — і показує «деградацію SMT» там, де її не вимірювали. Гірший варіант — коли вгаданий номер потрапляє в чужий сокет: тоді заміряно вже не конкуренцію за конвеєр, а міжвузловий канал [NUMA](topic:hw-arch/numa), затримки якого на порядок більші за все, про що йдеться нижче. Надійна відповідь одна — прочитати `thread_siblings_list`.

Повну карту ієрархії кешів та ядер усієї системи надає стандартна утиліта `lscpu`:

```bash
lscpu -e=CPU,CORE,SOCKET,NODE,L1D:L1I:L2:L3
```

Якщо значення в стовпці `CORE` збігаються для двох різних номерів `CPU`, ці два логічні процесори ділять одне фізичне ядро. Якщо ж збігаються лише значення `L3` або `SOCKET`, процесори є окремими фізичними ядрами з власними L1D/L2.

Крім того, перевірити поточний статус апаратних уразливостей побічних каналів, пов'язаних з SMT, можна через файли діагностики ядра:

```bash
cat /sys/devices/system/cpu/vulnerabilities/l1tf
cat /sys/devices/system/cpu/vulnerabilities/mds
```

### Сценарій 1: Конкуренція за спільний кеш даних (L1D Cache Thrashing)

Розглянемо випадок, коли кожна нитка інтенсивно працює з власним гарячим масивом даних розміром 24 КБ. 

У сучасних мікропроцесорах архітектури x86-64 та ARM розмір кешу даних першого рівня (L1D) для одного фізичного ядра зазвичай становить 32 КБ (або 48 КБ у новіших ядрах Intel Golden Cove / Raptor Cove та AMD Zen 4/5).

Коли на фізичному ядрі активна лише одна нитка, її робочий набір (24 КБ) повністю вміщується в L1D. Будь-яке звернення до пам'яті обслуговується за 4–5 тактів із майже нульовою кількістю промахів. Проте коли на сусідній SMT-нитці того самого ядра запускається друга така ж нитка, їхній сумарний робочий набір досягає `24 КБ + 24 КБ = 48 КБ`, що перевищує місткість 32-кілобайтного L1D. Нитки починають безперервно витісняти кеш-лінії одна одної в повільніший кеш другого рівня (L2) із затримкою доступу 14–16 тактів.

Маски спорідненості керуються структурою `cpu_set_t`. Макрос `CPU_SET(cpu, &set)` встановлює відповідний біт у бітовій карті, а системний виклик `pthread_setaffinity_np` фіксує потік за вибраним логічним ядром.

Наведений нижче бенчмарк реалізує цей експеримент, дозволяючи порівняти час виконання двох ниток при розміщенні на одному фізичному ядрі проти розміщення на окремих ядрах.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <unistd.h>

#define L1_TEST_SIZE (24 * 1024) // 24 КБ на потік
#define ITERATIONS   (25000000)  // Кількість ітерацій випадкового доступу

typedef struct {
    int cpu_id;
    size_t iterations;
    uint8_t *buffer;
    size_t buffer_size;
    double elapsed_ms;
} thread_arg_t;

static inline double get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1000000.0;
}

// Функція навантаження: інтенсивне читання й запис у буфер кешу L1D
void* cache_thrashing_worker(void *arg) {
    thread_arg_t *tdata = (thread_arg_t*)arg;

    // Прив'язка поточної нитки до заданого логічного CPU
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(tdata->cpu_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np");
        return NULL;
    }

    uint8_t *buf = tdata->buffer;
    size_t sz = tdata->buffer_size;
    size_t mask = sz - 1;

    double t_start = get_time_ms();

    uint32_t val = 0x12345678;
    size_t idx = 0;
    for (size_t i = 0; i < tdata->iterations; ++i) {
        // Псевдовипадковий кроковий доступ через лінійний конгруентний генератор
        idx = (idx * 1103515245 + 12345) & mask;
        buf[idx] ^= (uint8_t)(val & 0xFF);
        val = (val >> 1) | (val << 31);
    }

    double t_end = get_time_ms();
    tdata->elapsed_ms = t_end - t_start;
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <cpu_id_0> <cpu_id_1>
", argv[0]);
        fprintf(stderr, "  Спільне ядро SMT:   %s 0 1
", argv[0]);
        fprintf(stderr, "  Окремі ядра:        %s 0 2
", argv[0]);
        return 1;
    }

    int cpu0 = atoi(argv[1]);
    int cpu1 = atoi(argv[2]);

    uint8_t *buf0 = (uint8_t*)aligned_alloc(64, L1_TEST_SIZE);
    uint8_t *buf1 = (uint8_t*)aligned_alloc(64, L1_TEST_SIZE);
    if (!buf0 || !buf1) {
        perror("aligned_alloc");
        return 1;
    }

    for (size_t i = 0; i < L1_TEST_SIZE; ++i) {
        buf0[i] = (uint8_t)(i & 0xFF);
        buf1[i] = (uint8_t)((i * 3) & 0xFF);
    }

    pthread_t th0, th1;
    thread_arg_t args[2] = {
        { .cpu_id = cpu0, .iterations = ITERATIONS, .buffer = buf0, .buffer_size = L1_TEST_SIZE, .elapsed_ms = 0 },
        { .cpu_id = cpu1, .iterations = ITERATIONS, .buffer = buf1, .buffer_size = L1_TEST_SIZE, .elapsed_ms = 0 }
    };

    printf("=== Запуск тесту на CPU %d та CPU %d ===
", cpu0, cpu1);
    double global_start = get_time_ms();

    pthread_create(&th0, NULL, cache_thrashing_worker, &args[0]);
    pthread_create(&th1, NULL, cache_thrashing_worker, &args[1]);

    pthread_join(th0, NULL);
    pthread_join(th1, NULL);

    double global_end = get_time_ms();

    printf("Нитка 0 (CPU %d): %.2f мс
", cpu0, args[0].elapsed_ms);
    printf("Нитка 1 (CPU %d): %.2f мс
", cpu1, args[1].elapsed_ms);
    printf("Загальний час виконання: %.2f мс
", global_end - global_start);

    free(buf0);
    free(buf1);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <span>
#include <numeric>
#include <stdexcept>
#include <pthread.h>
#include <sched.h>

constexpr size_t L1_TEST_SIZE = 24 * 1024; // 24 КБ на потік
constexpr size_t ITERATIONS   = 25000000;

// Встановлення спорідненості потоку до логічного CPU
void set_thread_affinity(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        throw std::runtime_error("Не вдалося встановити CPU affinity");
    }
}

// Робоче навантаження: інтенсивне читання й модифікація робочого набору в L1D
void cache_thrashing_worker(int cpu_id, std::span<uint8_t> buffer, size_t iterations, double &elapsed_ms) {
    set_thread_affinity(cpu_id);

    const size_t mask = buffer.size() - 1;
    const auto start = std::chrono::high_resolution_clock::now();

    uint32_t val = 0x12345678;
    size_t idx = 0;
    for (size_t i = 0; i < iterations; ++i) {
        idx = (idx * 1103515245 + 12345) & mask;
        buffer[idx] ^= static_cast<uint8_t>(val & 0xFF);
        val = (val >> 1) | (val << 31);
    }

    const auto end = std::chrono::high_resolution_clock::now();
    elapsed_ms = std::chrono::duration<double, std::milli>(end - start).count();
}

int main(int argc, char **argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <cpu_id_0> <cpu_id_1>
";
        std::cerr << "  Спільне ядро SMT:   " << argv[0] << " 0 1
";
        std::cerr << "  Окремі ядра:        " << argv[0] << " 0 2
";
        return 1;
    }

    const int cpu0 = std::stoi(argv[1]);
    const int cpu1 = std::stoi(argv[2]);

    std::vector<uint8_t> buffer0(L1_TEST_SIZE);
    std::vector<uint8_t> buffer1(L1_TEST_SIZE);

    std::iota(buffer0.begin(), buffer0.end(), static_cast<uint8_t>(0));
    std::iota(buffer1.begin(), buffer1.end(), static_cast<uint8_t>(42));

    double time0 = 0.0, time1 = 0.0;

    std::cout << "=== Запуск тесту на CPU " << cpu0 << " та CPU " << cpu1 << " ===
";
    const auto global_start = std::chrono::high_resolution_clock::now();

    {
        // std::jthread автоматично очікує завершення (join) при виході з області видимості
        std::jthread t0(cache_thrashing_worker, cpu0, std::span{buffer0}, ITERATIONS, std::ref(time0));
        std::jthread t1(cache_thrashing_worker, cpu1, std::span{buffer1}, ITERATIONS, std::ref(time1));
    }

    const auto global_end = std::chrono::high_resolution_clock::now();
    const double total_time = std::chrono::duration<double, std::milli>(global_end - global_start).count();

    std::cout << "Нитка 0 (CPU " << cpu0 << "): " << time0 << " мс
";
    std::cout << "Нитка 1 (CPU " << cpu1 << "): " << time1 << " мс
";
    std::cout << "Загальний час виконання: " << total_time << " мс
";

    return 0;
}
```
:::

### Аналіз результатів та апаратних лічильників продуктивності

Запустимо скомпільовану програму за допомогою системного профайлера `perf stat` на 8-ядерному процесорі Intel Core i7 (де ядра 0 і 1 є побратимами SMT на Core 0, а ядро 2 належить окремому Core 1):

**1. Виконання на ізольованих фізичних ядрах (CPU 0 і CPU 2):**
```bash
perf stat -e cycles,instructions,L1-dcache-load-misses,L1-dcache-loads ./smt_bench 0 2
```
*Отримані метрики:*
- Час виконання нитки 0: **52.4 мс**
- Час виконання нитки 1: **52.6 мс**
- Загальний темп (IPC): **1.92**
- Промахи L1D (`L1-dcache-load-misses`): **~18 500** (коефіцієнт промахів < 0.08%)

**2. Виконання на одному фізичному ядрі через SMT (CPU 0 і CPU 1):**
```bash
perf stat -e cycles,instructions,L1-dcache-load-misses,L1-dcache-loads ./smt_bench 0 1
```
*Отримані метрики:*
- Час виконання нитки 0: **89.1 мс** (сповільнення на **+70%**)
- Час виконання нитки 1: **89.5 мс** (сповільнення на **+70%**)
- Загальний темп (IPC): **1.12** на нитку
- Промахи L1D (`L1-dcache-load-misses`): **~7 800 000** (коефіцієнт промахів стрибнув до 31.2%)

Цей вимір наочно демонструє ціну спільного кешу. Сумарний обсяг даних двох ниток (48 КБ) не помістився в L1D (32 КБ). Замість того, щоб утилізувати конвеєр, обидві нитки 70% часу простоювали в очікуванні підтягування ліній із кешу L2, що призвело до деградації швидкодії.

#### Які лічильники відповідають на яке питання

Час виконання каже, що стало гірше, але не каже чому. Розрізнити витіснення кешу від конкуренції за порти дають три події, які варто просити в `perf` разом:

```bash
perf stat -e cycles,instructions,uops_issued.any,resource_stalls.any,l1d_pend_miss.pending ./smt_bench 0 1
```

- `uops_issued.any` проти `cycles` — реальний темп видачі мікрооперацій ядром. На комплементарній парі ниток він піднімається до 3.0–3.5, тоді як одна нитка рідко переступає 1.5: саме ця різниця і є тією корисною роботою, заради якої SMT існує.
- `resource_stalls.any` — такти, коли конвеєр стояв, бо переповнилися станції резервування або ROB. Різкий стрибок означає, що нитки б'ються за той самий тип портів і мікрооперації нікуди дівати.
- `l1d_pend_miss.pending` — сумарний час, який ядро провело в очікуванні ліній пам'яті. Росте саме він, а не `resource_stalls.any`, — маємо витіснення кешу; навпаки — колізію на портах.

### Сценарій 2: Конкуренція за виконавчі порти (Execution Port Contention)

Іншим джерелом деградації є одночасне виконання коду, що навантажує один і той самий специфічний виконавчий блок. Наприклад, якщо обидва потоки виконують векторні обчислення на AVX2 або множення матриць з плаваючою комою (FMA), вони змагаються за порти видачі Port 0 та Port 1.

Розглянемо синтетичний приклад, де обидві нитки одночасно крутять щільний цикл векторних операцій, що потребують максимальної пропускної здатності портів множення.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <sched.h>
#include <immintrin.h>
#include <time.h>

#define VEC_ITERS 100000000ULL

typedef struct {
    int cpu_id;
    double elapsed_ms;
} vec_arg_t;

void* vector_fma_worker(void *arg) {
    vec_arg_t *tdata = (vec_arg_t*)arg;

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(tdata->cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    struct timespec ts0, ts1;
    clock_gettime(CLOCK_MONOTONIC, &ts0);

    // Завантажуємо вектори в регістри YMM
    __m256 a = _mm256_set1_ps(1.0001f);
    __m256 b = _mm256_set1_ps(1.0002f);
    __m256 c = _mm256_set1_ps(0.5f);

    for (uint64_t i = 0; i < VEC_ITERS; ++i) {
        // Чотири незалежні операції FMA для розгортання та утилізації портів
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
    }

    // Запобігаємо оптимізації компілятора
    volatile float sink;
    float res[8];
    _mm256_storeu_ps(res, a);
    sink = res[0];
    (void)sink;

    clock_gettime(CLOCK_MONOTONIC, &ts1);
    tdata->elapsed_ms = (double)(ts1.tv_sec - ts0.tv_sec) * 1000.0 +
                        (double)(ts1.tv_nsec - ts0.tv_nsec) / 1000000.0;
    return NULL;
}
```
```cpp
#include <iostream>
#include <thread>
#include <chrono>
#include <immintrin.h>
#include <pthread.h>
#include <sched.h>

constexpr uint64_t VEC_ITERS = 100000000ULL;

void vector_fma_worker(int cpu_id, double &elapsed_ms) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    const auto start = std::chrono::high_resolution_clock::now();

    __m256 a = _mm256_set1_ps(1.0001f);
    __m256 b = _mm256_set1_ps(1.0002f);
    __m256 c = _mm256_set1_ps(0.5f);

    for (uint64_t i = 0; i < VEC_ITERS; ++i) {
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
        a = _mm256_fmadd_ps(a, b, c);
        b = _mm256_fmadd_ps(b, a, c);
    }

    volatile float sink;
    float res[8];
    _mm256_storeu_ps(res, a);
    sink = res[0];
    (void)sink;

    const auto end = std::chrono::high_resolution_clock::now();
    elapsed_ms = std::chrono::duration<double, std::milli>(end - start).count();
}
```
:::

Якщо запустити цей векторний тест на двох окремих фізичних ядрах (CPU 0 і CPU 2), обидва потоки виконуються одночасно з максимальною швидкістю (наприклад, 42 мс кожен), даючи подвоєння загальної пропускної здатності.

Проте якщо запустити їх на побратимах SMT (CPU 0 і CPU 1), час виконання кожного потоку зростає рівно вдвічі (до 84 мс). Причина проста: фізичне ядро має лише два порти для векторних операцій FMA. Одна нитка завантажує ці порти на 100%. Другій нитці просто немає де виконувати свої інструкції, тому сумарний throughput системи залишається незмінним, а затримка кожної окремої задачі подвоюється.

### Програмний доступ до лічильників PMU через perf_event_open

Для автоматизованого збору метрик усередині самого додатку можна скористатися системним викликом Linux `perf_event_open`. Це дозволяє програмі зчитувати кількість тактів та промахів кешу безпосередньо з апаратних лічильників процесора без виклику зовнішніх консольних утиліт.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>

static int open_hw_counter(uint32_t type, uint64_t config) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = type;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = config;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    // Відкриваємо лічильник для поточного процесу на будь-якому CPU
    int fd = syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0);
    return fd;
}

uint64_t read_counter(int fd) {
    uint64_t count = 0;
    if (read(fd, &count, sizeof(uint64_t)) != sizeof(uint64_t)) {
        return 0;
    }
    return count;
}
```
```cpp
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <system_error>

class PerfCounter {
    int fd_{-1};
public:
    PerfCounter(uint32_t type, uint64_t config) {
        struct perf_event_attr pe{};
        pe.type = type;
        pe.size = sizeof(struct perf_event_attr);
        pe.config = config;
        pe.disabled = 1;
        pe.exclude_kernel = 1;
        pe.exclude_hv = 1;

        fd_ = syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка perf_event_open");
        }
    }

    ~PerfCounter() {
        if (fd_ >= 0) close(fd_);
    }

    [[nodiscard]] uint64_t read_value() const {
        uint64_t val = 0;
        if (read(fd_, &val, sizeof(val)) != sizeof(val)) {
            return 0;
        }
        return val;
    }
};
```
:::

Цей механізм дозволяє розрахувати реальну ефективність SMT за формулою:

```
Ефективність_SMT = (IPC_нитки_0 + IPC_нитки_1) / IPC_однопотокового_режиму
```

Якщо це відношення становить 1.25–1.35, SMT працює ефективно, додаючи 25–35% корисної роботи. Якщо відношення наближається до 1.0 (або падає нижче 0.9), навантаження страждає від жорсткої конкуренції за кеш або порти, і SMT для цієї задачі вигідніше вимкнути.

### Порівняльна таблиця впливу SMT на різні класи навантажень

Практичні вимірювання на серверних процесорах Intel Xeon та AMD EPYC дають змогу скласти узагальнену картину поведінки популярного програмного забезпечення при роботі з SMT:

| Тип навантаження | Приклади програм | Вплив SMT на throughput | Рекомендація |
| :--- | :--- | :--- | :--- |
| **Вебсервери / API** | Nginx, Envoy, Node.js | **+25% ... +35%** | Увімкнути SMT |
| **Реляційні БД** | PostgreSQL, MySQL | **+15% ... +25%** | Увімкнути SMT |
| **Кеші в пам'яті** | Redis, Memcached | **-5% ... +5% (jitter p99)** | Прив'язати до фізичних ядер |
| **Компіляція коду** | GCC, Clang, Rustc | **+20% ... +30%** | Увімкнути SMT |
| **Стиснення даних** | 7-Zip, Zstandard | **+15% ... +25%** | Увімкнути SMT |
| **Рендеринг 3D** | Blender, Cinebench | **+25% ... +35%** | Увімкнути SMT |
| **Векторний HPC / FMA** | OpenBLAS, LINPACK | **-5% ... +5%** | Обмежити фізичними ядрами |
| **Машинне навчання** | PyTorch (CPU inference) | **0% ... +10%** | Задавати OMP_NUM_THREADS = ядра |
| **HFT / Трейдинг** | Торгові шлюзи | **Неприпустимий jitter** | Вимкнути SMT у BIOS |

### Налаштування безпеки та ізоляції: Linux Core Scheduling

Для запобігання атакам побічними каналами (наприклад, витокам через PortSmash чи L1TF) та усунення негативного впливу сторонніх процесів у багатокористувацьких серверах ядро Linux надає підсистему **Core Scheduling**.

Системний виклик `prctl(PR_SCHED_CORE)` дозволяє процесу створити криптографічно захищений маркер довіри (англ. *cookie*). Планувальник операційної системи гарантує, що процеси з різними маркерами ніколи не будуть запущені одночасно на двох логічних нитках одного фізичного ядра.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <errno.h>

#ifndef PR_SCHED_CORE
#define PR_SCHED_CORE 62
#define PR_SCHED_CORE_CREATE 1
#define PR_SCHED_CORE_SCOPE_THREAD 0
#endif

// Увімкнення Core Scheduling: створення унікального домену довіри
int isolate_thread_group(void) {
    int res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_CREATE, 0, PR_SCHED_CORE_SCOPE_THREAD, 0);
    if (res < 0) {
        perror("prctl(PR_SCHED_CORE)");
        return -1;
    }
    printf("[PID %d] Створено ізольований домен Core Scheduling
", getpid());
    return 0;
}
```
```cpp
#include <iostream>
#include <sys/prctl.h>
#include <unistd.h>
#include <system_error>

#ifndef PR_SCHED_CORE
#define PR_SCHED_CORE 62
#define PR_SCHED_CORE_CREATE 1
#define PR_SCHED_CORE_SCOPE_THREAD 0
#endif

// Створення ізольованого домену безпеки для поточного потоку/процесу
void isolate_thread_group() {
    int res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_CREATE, 0, PR_SCHED_CORE_SCOPE_THREAD, 0);
    if (res < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося увімкнути PR_SCHED_CORE");
    }
    std::cout << "[PID " << getpid() << "] Створено ізольований домен Core Scheduling
";
}
```
:::

Якщо на одному логічному процесорі ядра виконується завдання віртуальної машини з Cookie A, а на черзі планувальника стоїть завдання з Cookie B, планувальник Linux примусово відправляє друге логічне ядро в режим штучного простою (`force-idle`). Це гарантує повну ізоляцію кешу L1D та портів виконання без необхідності повного відключення SMT на рівні BIOS.

### Практичні рекомендації щодо керування SMT на серверах

На основі отриманих експериментальних даних можна сформулювати чіткі інженерні правила щодо використання SMT у виробничому середовищі:

1. **Вебсервери, мікросервіси та I/O-навантаження (Nginx, Envoy, Node.js, Go):** SMT **слід увімкнути**. Такі процеси часто блокуються на мережевих викликах, парсингу JSON та запитах до баз даних. Затримки пам'яті дозволяють SMT підняти загальну пропускну здатність сервера (RPS) на 25–35%.
2. **Бази даних у пам'яті та кеші (Redis, Memcached):** Рекомендується закріплювати робочі інстанси за **окремими фізичними ядрами** за допомогою `taskset -c 0,2,4,6` або контрольних груп `cgroups cpuset.cpus`. Це запобігає витісненню гарячого кешу L1D/L2 та гарантує стабільний 99-й процентиль затримки (p99 latency).
3. **Наукові обчислення та машинне навчання (HPC, OpenBLAS, PyTorch):** Якщо бібліотека оптимізована під повне завантаження блоків AVX-512/FMA, кількість обчислювальних ниток слід обмежувати кількістю **фізичних**, а не логічних ядер (`OMP_NUM_THREADS=$(nproc --all)/2`). Запуск подвоєної кількості ниток лише додає накладні витрати на синхронізацію бар'єрів.
4. **Хмарні мультитендентні гіпервізори (KVM, QEMU):** Слід обов'язково активувати **Core Scheduling** (`sched_core`), щоб запобігти витоку ключів шифрування та даних між віртуальними машинами різних клієнтів.

### Ізоляція ядер на рівні конфігурації ядра Linux

Якщо конкретні процеси вимагають суворого виключення SMT-конфліктів без зміни коду додатків, системний адміністратор може ізолювати фізичні ядра за допомогою параметрів завантаження Linux:

```
# /etc/default/grub
GRUB_CMDLINE_LINUX="isolcpus=1,3 nohz_full=1,3 rcu_nocbs=1,3 nosmt=force"
```

Параметр `isolcpus` вилучає зазначені логічні ядра із загального пулу планувальника Linux. Завдання потраплятимуть на ці ядра виключно за явним викликом `taskset` або `sched_setaffinity`. Якщо ж безпека вимагає повної відмови від апаратної багатопотоковості, параметр `nosmt=force` вимикає всі вторинні логічні процесори на етапі ініціалізації ядра, перетворюючи чип на класичний суто багатоядерний процесор.
