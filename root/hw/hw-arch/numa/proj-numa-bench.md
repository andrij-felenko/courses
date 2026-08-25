# ⚙️ Вимірювання затримок між вузлами та NUMA-aware виділення пам'яті

Коли програма працює на багатопроцесорному сервері, ціна читання пам'яті перестає бути сталою величиною. Доступ до байта, виділеного у локальному банку пам'яті поточного процесора, займає близько 60–70 наносекунд. Але якщо цей самий байт фізично розташований у модулі оперативної пам'яті сусіднього сокета, пакет запиту мусить пройти через міжпроцесорну шину (Intel UPI або AMD Infinity Fabric). Затримка зростає до 130–180 наносекунд, а пропускна здатність міжвузлового з'єднання стає жорстким лімітом для всієї системи.

Щоб побачити цей ефект на власні очі та навчитися писати програми, що уникають міжвузлових затримок, створимо практичний бенчмарк і спеціалізований алокатор пам'яті.

### Мета проєкту

1. Виміряти реальну затримку та пропускну здатність послідовного й випадкового доступу до пам'яті у двох сценаріях:
   - **Локальний доступ**: потік виконується на ядрі NUMA-вузла 0 і читає пам'ять, виділену на NUMA-вузлі 0.
   - **Віддалений доступ**: потік переноситься на ядро NUMA-вузла 1, але продовжує читати той самий буфер на NUMA-вузлі 0.
2. Продемонструвати дію політики першого дотику (англ. *First-Touch Policy*), коли системний виклик `malloc()` ще не прив'язує сторінку до жодного вузла, а фізичне виділення відбувається під час першого запису.
3. Реалізувати RAII-обгортку для NUMA-буфера, яка гарантує коректне виділення й звільнення сторінок на заданому вузлі через бібліотеку `libnuma`.

### Архітектура бенчмарка та типи вимірювань

Щоб отримати вичерпну картину асиметрії доступу, недостатньо виміряти лише пропускну здатність послідовного читання. Сучасні апаратні передвісники вибірки (англ. *Hardware Prefetchers*) у процесорних ядрах розпізнають лінійні патерни звернень і заздалегідь завантажують сусідні кеш-лінії в кеш L2/L3, що частково маскує затримку міжпроцесорного лінка.

Тому справжню ціну неоднорідності виявляють два різні тести:
1. **Послідовна пропускна здатність (Bandwidth)**: потокове читання великого суцільного масиву даних кроками по 64 байти (розмір кеш-лінії), що показує граничну пропускну здатність контролера пам'яті та лінків UPI/Infinity Fabric.
2. **Випадкова затримка (Pointer Chasing Latency)**: обхід псевдовипадкового циклічного списку покажчиків, де кожна наступна адреса залежить від щойно прочитаного значення. У цьому тесті апаратний передвісник не здатний вгадати наступну адресу, конвеєр процесора зупиняється на кожній ітерації (англ. *pipeline stall*), і ми вимірюємо чисту фізичну затримку вибірки однієї кеш-лінії з DRAM.

### Робота правила першого дотику в ядрі Linux

Коли застосунок викликає `malloc()` або системний виклик `mmap(MAP_ANONYMOUS | MAP_PRIVATE)`, ядро Linux не виділяє жодного фізичного байта в оперативній пам'яті. Воно лише реєструє структуру діапазону віртуальних адрес (`struct vm_area_struct` у структурі процесу `mm_struct`).

Фізичне виділення сторінки 4 КБ відбувається лише в момент, коли потік процесора вперше намагається прочитати або записати байт за цією адресою. Відбувається апаратне переривання — сторінковий промах (англ. *Page Fault*), обробник якого (`do_anonymous_page()`) викликає бадді-алокатор вузла:

1. Ядро визначає номер фізичного ядра, на якому виникло переривання, та відповідний йому NUMA-вузол.
2. Сторінка виділяється з пулу `free_area` дескриптора `NODE_DATA(current_node)`.
3. Фізична адреса записується в таблицю сторінок процесу, і виконання інструкції поновлюється.

Якщо ініціалізацію великого пулу пам'яті виконує один потік на сокеті 0 (наприклад, циклом `memset()` або конструктором масиву), усі гігабайти пам'яті фізично осядуть на вузлі 0. Коли пізніше до роботи підключаться робочі потоки на сокеті 1, кожне їхнє звернення до пам'яті перетвориться на віддалений міжвузловий запит.

### Реалізація бенчмарка

Наведемо повний робочий код бенчмарка мовами C та C++. Програма містить як потоковий тест пропускної здатності, так і тест затримки методом переходу за покажчиками (Pointer Chasing).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sched.h>
#include <unistd.h>
#include <numa.h>
#include <numaif.h>

#define BUFFER_SIZE (256 * 1024 * 1024) // 256 МБ
#define LAT_NODES   (4 * 1024 * 1024)   // 4M елементів (256 МБ)
#define ITERATIONS  5

static uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

// Прив'язка потоку до першого ядра вказаного вузла
static int bind_to_node_cpu(int node) {
    struct bitmask *cpus = numa_allocate_cpumask();
    if (numa_node_to_cpus(node, cpus) != 0) {
        numa_bitmask_free(cpus);
        return -1;
    }

    int target_cpu = -1;
    for (unsigned int i = 0; i < cpus->size; ++i) {
        if (numa_bitmask_isbitset(cpus, i)) {
            target_cpu = (int)i;
            break;
        }
    }
    numa_bitmask_free(cpus);

    if (target_cpu < 0) return -1;

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);
    return sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);
}

// 1. Тест пропускної здатності (послідовне читання)
static double run_bandwidth_test(const uint64_t *buffer, size_t count) {
    uint64_t sink = 0;
    uint64_t start_ns = get_time_ns();

    for (int iter = 0; iter < ITERATIONS; ++iter) {
        for (size_t i = 0; i < count; i += 8) {
            sink += buffer[i];
        }
    }

    uint64_t duration_ns = get_time_ns() - start_ns;
    if (sink == 0xdeadbeef) printf("Sink\n");

    double total_bytes = (double)count * sizeof(uint64_t) * ITERATIONS;
    double duration_sec = (double)duration_ns / 1e9;
    return (total_bytes / duration_sec) / (1024.0 * 1024.0 * 1024.0); // ГБ/с
}

// 2. Тест чистої затримки (обхід випадкового списку покажчиків)
static double run_latency_test(const uint32_t *indices, size_t count, size_t steps) {
    uint32_t current = 0;
    uint64_t start_ns = get_time_ns();

    for (size_t s = 0; s < steps; ++s) {
        current = indices[current]; // непередбачуваний стрибок на нову кеш-лінію
    }

    uint64_t duration_ns = get_time_ns() - start_ns;
    if (current == 0xdeadbeef) printf("Sink\n");

    return (double)duration_ns / (double)steps; // наносекунд на одну операцію
}

int main(void) {
    if (numa_available() < 0) {
        fprintf(stderr, "Помилка: NUMA не підтримується на цій системі.\n");
        return EXIT_FAILURE;
    }

    int max_node = numa_max_node();
    printf("Кількість доступних NUMA-вузлів: %d\n", max_node + 1);
    if (max_node < 1) {
        printf("Для повноцінного тесту потрібно щонайменше 2 вузли.\n");
        return EXIT_SUCCESS;
    }

    // Виділяємо пам'ять суворо на Вузлі 0
    size_t count = BUFFER_SIZE / sizeof(uint64_t);
    uint64_t *bw_buf = (uint64_t *)numa_alloc_onnode(BUFFER_SIZE, 0);
    uint32_t *lat_buf = (uint32_t *)numa_alloc_onnode(LAT_NODES * sizeof(uint32_t), 0);

    if (!bw_buf || !lat_buf) {
        perror("numa_alloc_onnode failed");
        return EXIT_FAILURE;
    }

    // Ініціалізація буфера пропускної здатності
    for (size_t i = 0; i < count; ++i) {
        bw_buf[i] = i ^ 0x5555555555555555ULL;
    }

    // Створення псевдовипадкового циклу з кроком 64 байти (16 елементів uint32_t)
    size_t stride_elements = 16;
    size_t num_lines = LAT_NODES / stride_elements;
    size_t *perm = (size_t *)malloc(num_lines * sizeof(size_t));
    for (size_t i = 0; i < num_lines; ++i) perm[i] = i;

    // Перемішування Фішера-Єйтса
    srand(42);
    for (size_t i = num_lines - 1; i > 0; --i) {
        size_t j = (size_t)rand() % (i + 1);
        size_t tmp = perm[i];
        perm[i] = perm[j];
        perm[j] = tmp;
    }

    // Формуємо циклічний список у пам'яті
    for (size_t i = 0; i < num_lines; ++i) {
        size_t curr_idx = perm[i] * stride_elements;
        size_t next_idx = perm[(i + 1) % num_lines] * stride_elements;
        lat_buf[curr_idx] = (uint32_t)next_idx;
    }
    free(perm);

    // --- Тестування Вузла 0 (Локальний доступ) ---
    bind_to_node_cpu(0);
    printf("\n=== Тест 1: Локальний доступ (ЦП 0 -> RAM 0) ===\n");
    double loc_bw = run_bandwidth_test(bw_buf, count);
    printf("  Пропускна здатність : %.2f ГБ/с\n", loc_bw);
    double loc_lat = run_latency_test(lat_buf, LAT_NODES, 20000000);
    printf("  Затримка (Pointer Chase) : %.2f нс\n", loc_lat);

    // --- Тестування Вузла 1 (Віддалений доступ) ---
    bind_to_node_cpu(1);
    printf("\n=== Тест 2: Віддалений доступ (ЦП 1 -> RAM 0) ===\n");
    double rem_bw = run_bandwidth_test(bw_buf, count);
    printf("  Пропускна здатність : %.2f ГБ/с\n", rem_bw);
    double rem_lat = run_latency_test(lat_buf, LAT_NODES, 20000000);
    printf("  Затримка (Pointer Chase) : %.2f нс\n", rem_lat);

    // --- Підсумок ---
    printf("\n=== Підсумок NUMA Ratio ===\n");
    printf("  Відношення пропускної здатності : %.2f×\n", loc_bw / rem_bw);
    printf("  Відношення затримок доступу      : %.2f× (штраф +%.1f нс)\n",
           rem_lat / loc_lat, rem_lat - loc_lat);

    numa_free(bw_buf, BUFFER_SIZE);
    numa_free(lat_buf, LAT_NODES * sizeof(uint32_t));
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <memory>
#include <span>
#include <random>
#include <numeric>
#include <format>
#include <stdexcept>
#include <sched.h>
#include <numa.h>
#include <numaif.h>

template <typename T>
class NumaBuffer {
public:
    NumaBuffer(std::size_t count, int node)
        : count_(count), node_(node), bytes_(count * sizeof(T)) {
        void *ptr = numa_alloc_onnode(bytes_, node_);
        if (!ptr) {
            throw std::runtime_error(std::format("Не вдалося виділити пам'ять на NUMA-вузлі {}", node_));
        }
        data_ = static_cast<T *>(ptr);
    }

    ~NumaBuffer() noexcept {
        if (data_) numa_free(data_, bytes_);
    }

    NumaBuffer(const NumaBuffer &) = delete;
    NumaBuffer &operator=(const NumaBuffer &) = delete;

    NumaBuffer(NumaBuffer &&other) noexcept
        : data_(other.data_), count_(other.count_), node_(other.node_), bytes_(other.bytes_) {
        other.data_ = nullptr;
        other.count_ = 0;
    }

    NumaBuffer &operator=(NumaBuffer &&other) noexcept {
        if (this != &other) {
            if (data_) numa_free(data_, bytes_);
            data_ = other.data_;
            count_ = other.count_;
            node_ = other.node_;
            bytes_ = other.bytes_;
            other.data_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<T> span() noexcept { return std::span<T>(data_, count_); }
    [[nodiscard]] std::span<const T> span() const noexcept { return std::span<const T>(data_, count_); }
    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] int node() const noexcept { return node_; }

private:
    T *data_{nullptr};
    std::size_t count_{0};
    int node_{0};
    std::size_t bytes_{0};
};

void pin_thread_to_node(int node) {
    struct bitmask *cpus = numa_allocate_cpumask();
    if (numa_node_to_cpus(node, cpus) != 0) {
        numa_bitmask_free(cpus);
        throw std::runtime_error("numa_node_to_cpus failed");
    }

    int target_cpu = -1;
    for (unsigned int i = 0; i < cpus->size; ++i) {
        if (numa_bitmask_isbitset(cpus, i)) {
            target_cpu = static_cast<int>(i);
            break;
        }
    }
    numa_bitmask_free(cpus);

    if (target_cpu < 0) {
        throw std::runtime_error(std::format("На NUMA-вузлі {} не знайдено активних ядер", node));
    }

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);

    if (sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) != 0) {
        throw std::runtime_error(std::format("sched_setaffinity failed для ЦП {}", target_cpu));
    }
}

double benchmark_bandwidth(std::span<const std::uint64_t> data, int iterations = 5) {
    std::uint64_t sink = 0;
    const auto start = std::chrono::high_resolution_clock::now();

    for (int iter = 0; iter < iterations; ++iter) {
        for (std::size_t i = 0; i < data.size(); i += 8) {
            sink += data[i];
        }
    }

    const auto finish = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double> elapsed = finish - start;

    if (sink == 0xdeadbeef) std::cout << "Sink\n";

    double total_bytes = static_cast<double>(data.size_bytes()) * iterations;
    return (total_bytes / elapsed.count()) / (1024.0 * 1024.0 * 1024.0); // ГБ/с
}

double benchmark_latency(std::span<const std::uint32_t> indices, std::size_t steps = 20'000'000) {
    std::uint32_t current = 0;
    const auto start = std::chrono::high_resolution_clock::now();

    for (std::size_t s = 0; s < steps; ++s) {
        current = indices[current];
    }

    const auto finish = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double, std::nano> elapsed = finish - start;

    if (current == 0xdeadbeef) std::cout << "Sink\n";

    return elapsed.count() / static_cast<double>(steps); // наносекунд
}

int main() {
    try {
        if (numa_available() < 0) {
            std::cerr << "Помилка: NUMA не підтримується на цій системі.\n";
            return 1;
        }

        const int max_node = numa_max_node();
        std::cout << std::format("Доступно NUMA-вузлів: {}\n", max_node + 1);

        if (max_node < 1) {
            std::cout << "Для повноцінного тесту потрібно щонайменше 2 вузли.\n";
            return 0;
        }

        constexpr std::size_t bw_elements = (256 * 1024 * 1024) / sizeof(std::uint64_t);
        constexpr std::size_t lat_elements = 4 * 1024 * 1024; // 4M індексів

        NumaBuffer<std::uint64_t> bw_buffer(bw_elements, 0);
        NumaBuffer<std::uint32_t> lat_buffer(lat_elements, 0);

        // Ініціалізація буфера пропускної здатності
        auto bw_span = bw_buffer.span();
        for (std::size_t i = 0; i < bw_span.size(); ++i) {
            bw_span[i] = i ^ 0x5555555555555555ULL;
        }

        // Побудова графа випадкових стрибків для перевірки затримки
        constexpr std::size_t stride = 16; // 64 байти
        const std::size_t num_lines = lat_elements / stride;
        std::vector<std::size_t> perm(num_lines);
        std::iota(perm.begin(), perm.end(), 0);

        std::mt19937_64 rng(42);
        std::shuffle(perm.begin(), perm.end(), rng);

        auto lat_span = lat_buffer.span();
        for (std::size_t i = 0; i < num_lines; ++i) {
            const std::size_t curr = perm[i] * stride;
            const std::size_t next = perm[(i + 1) % num_lines] * stride;
            lat_span[curr] = static_cast<std::uint32_t>(next);
        }

        // Локальний тест
        pin_thread_to_node(0);
        std::cout << "\n=== Тест 1: Локальний доступ (ЦП 0 -> RAM 0) ===\n";
        const double loc_bw = benchmark_bandwidth(bw_buffer.span());
        std::cout << std::format("  Пропускна здатність : {:.2f} ГБ/с\n", loc_bw);
        const double loc_lat = benchmark_latency(lat_buffer.span());
        std::cout << std::format("  Затримка (Pointer Chase) : {:.2f} нс\n", loc_lat);

        // Віддалений тест
        pin_thread_to_node(1);
        std::cout << "\n=== Тест 2: Віддалений доступ (ЦП 1 -> RAM 0) ===\n";
        const double rem_bw = benchmark_bandwidth(bw_buffer.span());
        std::cout << std::format("  Пропускна здатність : {:.2f} ГБ/с\n", rem_bw);
        const double rem_lat = benchmark_latency(lat_buffer.span());
        std::cout << std::format("  Затримка (Pointer Chase) : {:.2f} нс\n", rem_lat);

        // Результати
        std::cout << "\n=== Підсумок NUMA Ratio ===\n";
        std::cout << std::format("  Відношення пропускної здатності : {:.2f}×\n", loc_bw / rem_bw);
        std::cout << std::format("  Відношення затримок доступу      : {:.2f}× (штраф +{:.1f} нс)\n",
                                 rem_lat / loc_lat, rem_lat - loc_lat);

    } catch (const std::exception &ex) {
        std::cerr << std::format("Виняток: {}\n", ex.what());
        return 1;
    }
    return 0;
}
```
:::

### Теоретичний розрахунок: чому шина стає вузьким горлом

Порахуймо фізичну пропускну здатність каналів оперативної пам'яті сокета та порівняймо її з можливостями міжпроцесорної шини.

Нехай двосокетний сервер оснащено двома процесорами, кожен із яких має 8 каналів пам'яті DDR4-3200 (або DDR5-4800).
1. **Пропускна здатність локальної пам'яті одного сокета**:
   Один канал DDR4-3200 передає 64 біти (8 байтів) даних за такт зі швидкістю 3.2 млрд передач за секунду (3200 МТ/с):

```
Пропускна здатність 1 каналу = 8 байтів · 3.2 ГТ/с = 25.6 ГБ/с
Локальна пропускна здатність сокета (8 каналів) = 8 · 25.6 ГБ/с = 204.8 ГБ/с
```

2. **Пропускна здатність міжпроцесорного лінка Intel UPI**:
   Серверний процесор з'єднується із сусіднім сокетом двома або трьома лінками UPI. Кожен лінк працює зі швидкістю 11.2 ГТ/с, передаючи за такт 20 бітів корисної інформації (у форматі флітів, *Flit — Flow Control Unit*), з яких 16 бітів припадає на корисне навантаження:

```
Пропускна здатність 1 лінка UPI (в один бік) = (11.2 ГТ/с · 16 біт) / 8 = 22.4 ГБ/с
Сумарна пропускна здатність 2 лінків UPI = 2 · 22.4 ГБ/с = 44.8 ГБ/с
```

Порівняння чисел розкриває головний закон NUMA-архітектури:
- Локальні контролери сокета здатні видавати **204.8 ГБ/с**.
- Міжпроцесорний міст UPI здатен пропустити лише **44.8 ГБ/с**.

Шина зв'язку між сокетами має пропускну здатність у **4.5 раза меншу**, ніж локальні модулі DRAM. Якщо всі ядра Сокета 1 одночасно почнуть читати дані, виділені на Сокеті 0, вони миттєво наситять шину UPI на 100%. Виникне затримка буферизації (англ. *Queuing Delay*), і замість нормальних 70 нс ядра Сокета 1 чекатимуть на кожне слово з пам'яті по 250–350 наносекунд.

### Апаратні лічильники продуктивності: пряме читання через `perf_event_open`

Замість зовнішньої утиліти `perf` системні програмісти можуть зчитувати апаратні лічильники міжвузлового трафіку безпосередньо з коду через системний виклик `perf_event_open()`.

Сучасні процесори x86 підтримують лічильники `OFFCORE_RESPONSE`, які окремо фіксують:
- `L3_MISS.LOCAL_DRAM`: вибірка з локальної DRAM (вузол 0).
- `L3_MISS.REMOTE_DRAM`: вибірка через міжпроцесорний лінк (віддалений вузол).

Наведемо код ініціалізації та зчитування таких лічильників:

:::tabs
```c
#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// Обгортка над системним викликом perf_event_open
static int open_hw_perf_counter(uint32_t type, uint64_t config) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = type;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = config;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0);
}

// Зчитування 64-бітного значення лічильника
static uint64_t read_perf_counter(int fd) {
    uint64_t val = 0;
    if (read(fd, &val, sizeof(uint64_t)) != sizeof(uint64_t)) {
        return 0;
    }
    return val;
}
```
```cpp
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <format>

class ScopedPerfCounter {
public:
    ScopedPerfCounter(std::uint32_t type, std::uint64_t config) {
        perf_event_attr pe{};
        pe.type = type;
        pe.size = sizeof(perf_event_attr);
        pe.config = config;
        pe.disabled = 1;
        pe.exclude_kernel = 1;
        pe.exclude_hv = 1;

        fd_ = static_cast<int>(syscall(__NR_perf_event_open, &pe, 0, -1, -1, 0));
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити апаратний лічильник perf");
        }
    }

    ~ScopedPerfCounter() noexcept {
        if (fd_ >= 0) close(fd_);
    }

    ScopedPerfCounter(const ScopedPerfCounter&) = delete;
    ScopedPerfCounter& operator=(const ScopedPerfCounter&) = delete;

    void start() const noexcept {
        ioctl(fd_, PERF_EVENT_IOC_ENABLE, 0);
    }

    void stop() const noexcept {
        ioctl(fd_, PERF_EVENT_IOC_DISABLE, 0);
    }

    [[nodiscard]] std::uint64_t read_value() const {
        std::uint64_t val = 0;
        if (read(fd_, &val, sizeof(std::uint64_t)) != sizeof(std::uint64_t)) {
            throw std::runtime_error("Помилка читання значення лічильника");
        }
        return val;
    }

private:
    int fd_{-1};
};
```
:::

### Патерн роботи з безпроцесорними вузлами: пам'ять CXL.mem

З появою шини Compute Express Link (CXL) та енергонезалежної пам'яті (Optane PMEM) з'явилися так звані **безпроцесорні NUMA-вузли** (англ. *CPU-less / Memory-Only Nodes*).

Це фізичні банки пам'яті, під'єднані через інтерфейс PCIe/CXL, які не мають власних процесорних ядер. У системній топології ядра Linux (`lscpu` або `numactl -H`) такий вузол відображається з нульовим списком процесорів:

```
node 2 cpus: 
node 2 size: 524288 MB
node 2 free: 524100 MB
node distances:
node   0   1   2 
  0:  10  21  28 
  1:  21  10  28 
  2:  28  28  10 
```

При роботі з CXL.mem ядро Linux використовує механізм автоматичного багаторівневого переміщення пам'яті (англ. *Tiered Memory / AutoNUMA Demotion*):
1. **Швидкий рівень (Tier 1)**: локальна DRAM (вузли 0 та 1) обслуговує гарячі сторінки, які активно читаються й модифікуються.
2. **Повільний рівень (Tier 2)**: CXL-пам'ять (вузол 2) зберігає холодні сторінки кешу чи рідко вживані структури даних.
3. Коли сторінка на швидкому рівні остигає (не має звернень тривалий час), демон `kswapd` не скидає її на диск, а мігрує на вузол CXL (`demote_page_list()`). Якщо ж потік знову звертається до цієї сторінки, ядро генерує NUMA-hint fault і підіймає її назад у локальну DRAM.

### Внутрішня будова пам'яттєвих алокаторів jemalloc та TCMalloc

Чому стандартний `malloc()` із бібліотеки glibc часто програє jemalloc та TCMalloc на 64- та 128-ядерних NUMA-серверах?

У стандартному алокаторі glibc (ptmalloc3) існує фіксована кількість арен (за замовчуванням `8 · cores`), але вони не прив'язані до NUMA-топології заліза. Потік, що виконується на Сокеті 0, може випадково захопити блокування на арені, сторінки якої були виділені на Сокеті 1.

Алокатор **jemalloc** розв'язує цю проблему архітектурно:
1. **Прив'язка арен до вузлів (`arenas.extend`)**: jemalloc створює окремі пули арен для кожного NUMA-вузла.
2. **Локальні кеші потоків (Thread-Specific Caching, TCACHE)**: невеликі об'єкти виділяються з локального масиву потоку взагалі без системних викликів і без міжпроцесорних блокувань.
3. **Екстенти пам'яті**: коли TCACHE вичерпується, jemalloc виділяє великий блок (extent) строго з фізичної арени свого NUMA-вузла через системний виклик `mbind(..., MPOL_LOCAL)`.

### Інтеграція з сучасним C++: NUMA-алокатор через `std::pmr::memory_resource`

У сучасному стандарті C++ (починаючи з C++17) з'явився механізм поліморфних ресурсів пам'яті (`std::pmr`), який дозволяє передавати конкретний спосіб виділення пам'яті в стандартні контейнери (`std::pmr::vector`, `std::pmr::string`, `std::pmr::unordered_map`) без зміни їхнього типу під час компіляції.

Створимо власний клас `NumaMemoryResource`, що успадковує `std::pmr::memory_resource`:

:::tabs
```c
// У мові C аналогом PMR є структура з покажчиками на функції виділення й звільнення
#include <numa.h>
#include <stdlib.h>

typedef struct {
    int node;
} numa_allocator_t;

static void* numa_allocator_alloc(numa_allocator_t *alloc, size_t bytes) {
    return numa_alloc_onnode(bytes, alloc->node);
}

static void numa_allocator_free(numa_allocator_t *alloc, void *ptr, size_t bytes) {
    numa_free(ptr, bytes);
}
```
```cpp
#include <memory_resource>
#include <numa.h>
#include <format>
#include <stdexcept>

class NumaMemoryResource : public std::pmr::memory_resource {
public:
    explicit NumaMemoryResource(int node) : node_(node) {
        if (numa_available() < 0) {
            throw std::runtime_error("NUMA не підтримується системою");
        }
    }

    [[nodiscard]] int node() const noexcept { return node_; }

protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        // libnuma виділяє пам'ять сторінками, тому вирівнювання задовольняється автоматично
        void* ptr = numa_alloc_onnode(bytes, node_);
        if (!ptr) {
            throw std::bad_alloc();
        }
        return ptr;
    }

    void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override {
        numa_free(p, bytes);
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        if (this == &other) return true;
        const auto* casted = dynamic_cast<const NumaMemoryResource*>(&other);
        return casted && (casted->node_ == node_);
    }

private:
    int node_{0};
};
```
:::

Тепер будь-який стандартний контейнер може працювати суворо в межах заданого NUMA-вузла:

:::tabs
```c
// Використання в C: явна передача вузла при створенні структур даних
typedef struct {
    uint64_t *items;
    size_t count;
    int node;
} numa_vector_t;

numa_vector_t* numa_vector_create(size_t count, int node) {
    numa_vector_t *vec = (numa_vector_t*)malloc(sizeof(numa_vector_t));
    vec->count = count;
    vec->node = node;
    vec->items = (uint64_t*)numa_alloc_onnode(count * sizeof(uint64_t), node);
    return vec;
}

void numa_vector_destroy(numa_vector_t *vec) {
    if (vec) {
        numa_free(vec->items, vec->count * sizeof(uint64_t));
        free(vec);
    }
}
```
```cpp
// Використання в C++: передача ресурсу пам'яті в контейнер std::pmr::vector
void process_node_data(int node_id) {
    NumaMemoryResource node_res(node_id);
    
    // Вектор гарантовано виділяє внутрішній динамічний буфер на node_id
    std::pmr::vector<std::uint64_t> vec(&node_res);
    vec.reserve(1'000'000);
    for (std::size_t i = 0; i < 1'000'000; ++i) {
        vec.push_back(i);
    }
}
```
:::

### Використання величезних сторінок (HugePages) у NUMA-системах

Один із найпотужніших способів зниження накладних витрат на звернення до пам'яті — це комбінація NUMA-прив'язки з величезними сторінками пам'яті розміром 2 МБ або 1 ГБ (англ. *HugePages*).

Звичайні сторінки розміром 4 КБ створюють значне навантаження на буфер асоціативної трансляції (TLB). При розмірі робочого набору в 64 ГБ процесору потрібно 16 мільйонів записів у таблицях сторінок. Якщо потік на сокеті 0 звертається до пам'яті сокета 1, кожен промах TLB призводить до того, що апаратний транслятор (англ. *Page Table Walker*) змушений робити 4-5 послідовних читань таблиць сторінок через повільний міжпроцесорний лінк UPI/Infinity Fabric!

Використання сторінок 2 МБ скорочує кількість рівнів трансляції та зменшує навантаження на міжвузлові шини:

```bash
# Перевірка наявності HugePages для кожного вузла в sysfs
cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
cat /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

# Виділення 1024 сторінок по 2 МБ (2 ГБ) суворо на Вузлі 0
echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
```

У коді C/C++ виділення HugePages на конкретному вузлі реалізується через прапорець `mmap(MAP_HUGETLB)` у поєднанні з системним викликом `mbind()`:

:::tabs
```c
#define _GNU_SOURCE
#include <sys/mman.h>
#include <numaif.h>
#include <stdio.h>
#include <stdlib.h>

void* alloc_hugepages_on_node(size_t size_2mb_aligned, int node) {
    void *ptr = mmap(NULL, size_2mb_aligned,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                     -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap MAP_HUGETLB failed");
        return NULL;
    }

    unsigned long nodemask = (1UL << node);
    if (mbind(ptr, size_2mb_aligned, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) != 0) {
        perror("mbind failed");
        munmap(ptr, size_2mb_aligned);
        return NULL;
    }

    return ptr;
}
```
```cpp
#include <sys/mman.h>
#include <numaif.h>
#include <cstddef>
#include <stdexcept>
#include <format>
#include <span>

class NumaHugePageBuffer {
public:
    NumaHugePageBuffer(std::size_t bytes, int node) : bytes_(bytes), node_(node) {
        // Розмір має бути кратним 2 МБ
        constexpr std::size_t huge_page_size = 2 * 1024 * 1024;
        if (bytes_ % huge_page_size != 0) {
            bytes_ = ((bytes_ + huge_page_size - 1) / huge_page_size) * huge_page_size;
        }

        void* ptr = mmap(nullptr, bytes_,
                         PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                         -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::runtime_error("mmap MAP_HUGETLB failed: перевірте наявність вільних HugePages");
        }

        unsigned long nodemask = (1UL << node_);
        if (mbind(ptr, bytes_, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) != 0) {
            munmap(ptr, bytes_);
            throw std::runtime_error(std::format("mbind failed для вузла {}", node_));
        }

        data_ = static_cast<std::byte*>(ptr);
    }

    ~NumaHugePageBuffer() noexcept {
        if (data_) munmap(data_, bytes_);
    }

    NumaHugePageBuffer(const NumaHugePageBuffer&) = delete;
    NumaHugePageBuffer& operator=(const NumaHugePageBuffer&) = delete;

    [[nodiscard]] std::span<std::byte> span() noexcept { return {data_, bytes_}; }
    [[nodiscard]] std::size_t size_bytes() const noexcept { return bytes_; }
    [[nodiscard]] int node() const noexcept { return node_; }

private:
    std::byte* data_{nullptr};
    std::size_t bytes_{0};
    int node_{0};
};
```
:::

### Методологія чистих вимірювань на багатопроцесорних серверах

При проведенні низькорівневих бенчмарків пам'яті на серверах легко отримати спотворені результати через системні шуми ядра та апаратні оптимізації. Щоб вимірювання затримок і пропускної здатності були статистично достовірними, необхідно дотримуватися суворих правил підготовки тестового середовища:

1. **Фіксація частоти ядер (CPU Frequency Governor)**:
   Динамічне масштабування частоти (DVFS, Intel SpeedStep, AMD Precision Boost) підвищує або знижує частоту ядер залежно від навантаження. Для тестування затримок пам'яті необхідно перевести всі ядра в режим максимальної фіксованої продуктивності:

```bash
# Встановлення максимальної продуктивності для всіх ядер
sudo cpupower frequency-set -g performance
```

2. **Скидання кешів процесора (Cache Flushing)**:
   Якщо потік щойно ініціалізував буфер, значна частина сторінок може залишитися в локальному L3-кеші процесора. Щоб виміряти справжню швидкість DRAM, а не кешу, перед кожним заміром необхідно повністю витіснити дані з кеш-ліній за допомогою апаратної інструкції `clflushopt` або `clflush`:

:::tabs
```c
#include <immintrin.h>
#include <stdint.h>

// Примусове скидання кеш-ліній буфера з усіх рівнів кешу
static void flush_buffer_from_cache(const void *addr, size_t bytes) {
    const char *ptr = (const char *)addr;
    for (size_t i = 0; i < bytes; i += 64) {
        _mm_clflushopt(ptr + i);
    }
    _mm_sfence(); // очікування завершення скидання
}
```
```cpp
#include <immintrin.h>
#include <span>
#include <cstddef>

void flush_span_from_cache(std::span<const std::byte> memory) noexcept {
    const auto* ptr = memory.data();
    for (std::size_t offset = 0; offset < memory.size_bytes(); offset += 64) {
        _mm_clflushopt(ptr + offset);
    }
    _mm_sfence();
}
```
:::

3. **Ізоляція ядер від переривань операційної системи (CPU Isolation)**:
   Ядро операційної системи періодично генерує таймерні переривання (scheduler ticks) та обробляє мережеві пакети, перериваючи бенчмарк. У виробничих конфігураціях виділяють окремі ядра за допомогою параметрів ядра Linux `isolcpus` та `nohz_full`, повністю звільняючи їх від системних завдань.

### Патерн NUMA-Aware Work-Stealing у пулах потоків

У багатопотокових обчислювальних рушіях (наприклад, пулах задач вебсерверів чи графічних рендерерів) класичний алгоритм крадіжки задач (англ. *Work-Stealing*) часто спричиняє серйозну деградацію через NUMA.

У класичному пулі потоків (як у Go runtime чи Java ForkJoinPool):
- Кожен потік має власну чергу задач (deque).
- Коли черга порожня, потік випадковим чином обирає інший потік системи та «краде» в нього завдання.
- Якщо потік на Сокеті 1 краде задачу у потоку на Сокеті 0, він змушений читати дані задачі, які лежать у локальній пам'яті Сокета 0. Кожен крок виконання супроводжується віддаленими зверненнями.

**Ієрархічний NUMA Work-Stealing** виправляє цей недолік двома правилами:
1. **Пріоритет локального вузла**: вільний потік спершу намагається вкрасти задачу в сусідніх ядер свого NUMA-вузла (де затримка кешів L3 мінімальна, а пам'ять є локальною).
2. **Міжвузлова крадіжка лише великими пакетами**: звернення до черги чужого NUMA-вузла дозволяється лише тоді, коли всі локальні ядра повністю простояли без роботи понад визначений тайм-аут, причому крадеться не одна дрібна задача, а цілий пакет завдань, щоб виправдати витрати на міжвузлову синхронізацію.

### Профілювання кеш-ліній між вузлами за допомогою `perf c2c`

Найбільш підступною проблемою у багатопотоковому коді є передача модифікованих кеш-ліній між сокетами. Для її виявлення в ядрі Linux передбачено спеціалізований інструмент `perf c2c` (англ. *Cache-to-Cache*).

Команда записує події вибірки кешів із прив'язкою до фізичних адрес пам'яті:

```bash
# Запис профілю міжвузлових звернень до кеш-ліній
perf c2c record -F 60000 -- ./numa_bench_c

# Генерація звіту про спільні кеш-лінії
perf c2c report --stdio
```

У звіті `perf c2c` ключовим показником є `HITM` (англ. *Hit Modified*). Це ситуація, коли ядро одного сокета змушене зупинити свій конвеєр і очікувати, поки модифікована кеш-лінія буде витіснена з L1/L2 кешу сусіднього сокета та передана через шину UPI. Якщо показник `Remote HITM` становить понад 5–10% від усіх кеш-промахів, система страждає від міжвузлового контеншну, і структури даних вимагають негайного шардингу або додаткового вирівнювання пам'яті.

### Крайові випадки та типові пастки при оптимізації

1. **Міжвузлове хибне спільне використання (Cross-Node False Sharing)**:
   Якщо два ядра на різних сокетах модифікують різні змінні, що опинилися в одній 64-байтній кеш-лінії, протокол когерентності (ccNUMA) змушений постійно пересилати цю кеш-лінію через шину UPI/Infinity Fabric туди й назад (так званий «кеш-пінг-понг»). На міжвузловому рівні затримка кожного такого оновлення в 5–10 разів вища, ніж між ядрами одного кристала. Обов'язково вирівнюйте структури даних за `alignas(64)` або `alignas(128)` для роздільних змінних різних потоків.

2. **Непомітна міграція сторінок демоном AutoNUMA**:
   Якщо увімкнено ядровий механізм AutoNUMA (`kernel.numa_balancing=1`), ядро може несподівано перемістити сторінку вашого буфера на інший вузол, якщо зареєструє численні звернення з чужого сокета. Для критичних застосувань із жорсткою прив'язкою пам'яті обов'язково використовуйте політику `MPOL_BIND` або вимикайте автоматичне балансування.

3. **Блокування трансляцій сторінок (TLB Shootdown Storm)**:
   Коли один потік змінює права доступу сторінки або операційна система переносить сторінку на інший вузол, процесор надсилає міжпроцесорні переривання (IPI) всім іншим ядрам, щоб вони скинули застарілий запис у своєму TLB. На 128-ядерних серверах такий шторм переривань здатен повністю зупинити виконання корисного коду на мілісекунди.

Розуміння цих механізмів дозволяє створювати програмне забезпечення, що масштабується лінійно зі збільшенням кількості ядер і сокетів, перетворюючи складну топологію пам'яті з джерела проблем на інструмент досягнення рекордної продуктивності.



