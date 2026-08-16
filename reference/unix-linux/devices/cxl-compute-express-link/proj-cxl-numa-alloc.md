# ⚙️ Практичне виділення та вимірювання затримок пам'яті CXL

Практична реалізація роботи з пристроями розширення пам'яті CXL Type 3 вимагає від системного розробника глибокого розуміння того, як операційна система Linux експортує гетерогенну пам'ять у користувацький простір. У цій практичній роботі ми розглянемо алгоритм виявлення безпроцесорних вузлів NUMA (CPU-less NUMA nodes), явне керування розміщенням сторінок за допомогою системного виклику `mbind()` та проведення порівняльного бенчмарка затримок вибірки даних за допомогою апаратної інструкції `rdtsc`.

## Сценарій використання та конфігурація ядра Linux

Розглянемо двосокетний сервер, до якого підключено картку розширення CXL Type 3 обсягом 512 ГБ. Під час завантаження ядро Linux зчитує ACPI-таблиці SRAT (System Resource Affinity Table) та SLIT (System Locality Information Table). Оскільки пристрій CXL.mem не має власних обчислювальних ядер CPU, ядро створює для нього окремий «ізольований» вузол NUMA.

Типова конфігурація вузлів у системі:
- **NUMA Node 0:** 64 ядра CPU + 256 ГБ локальної оперативної пам'яті DDR5 (Tier 1, затримка ~80 нс).
- **NUMA Node 1:** 64 ядра CPU + 256 ГБ локальної оперативної пам'яті DDR5 (Tier 1, затримка ~80 нс).
- **NUMA Node 2:** 0 ядер CPU (CPU-less) + 512 ГБ пам'яті CXL Type 3 (Tier 2, затримка ~230 нс).

Для повноцінної роботи з даним прикладом у конфігурації ядра Linux повинні бути активовані опції:
- `CONFIG_NUMA=y` — підтримка архітектури неоднорідного доступу до пам'яті.
- `CONFIG_CXL_BUS=y` та `CONFIG_CXL_MEM=m` — драйвери підсистеми CXL.
- `CONFIG_DEV_DAX_HMEM=y` — підтримка гетерогенної пам'яті через DAX.
- `CONFIG_NUMA_BALANCING=y` (і залежний від нього `CONFIG_MEMORY_TIERING`) — автоматичне підвищення й пониження сторінок між рівнями памʼяті; сам режим вмикається окремо: `sysctl kernel.numa_balancing=2`.

## Покроковий алгоритм роботи програми

Наш програмний комплекс виконує такі кроки:
1. **Сканування бітової маски CPU у NUMA:** Через бібліотеку `libnuma` ми опитуємо розмір пам'яті та бітову маску процесорів для кожного вузла. Вузол із ненульовою пам'яттю та нульовим ваговим коефіцієнтом CPU-маски ідентифікується як CXL Tier 2.
2. **Алокація анонімної пам'яті:** За допомогою системного виклику `mmap()` виділяється буфер розміром 1 ГБ із прапорцями `MAP_PRIVATE | MAP_ANONYMOUS`.
3. **Застосування політики розміщення `MPOL_BIND`:** Викликається системний виклик `mbind()`, який примусово прив'язує фізичне виділення сторінок виключно до виявленого CXL вузла.
4. **Прогрів сторінок (Page Fault Initialization):** У Linux пам'ять виділяється за принципом «Lazy Allocation». Справжній виклик Page Fault та виділення осередків у CXL відбуваються під час першого запису. Ми виконуємо `memset()`, щоб гарантувати, що під час бенчмарку всі сторінки вже відображені в таблицях сторінок (PTE).
5. **Pointer Chasing Benchmark:** Щоб виключити вплив апаратного випереджального читання (Hardware Prefetcher), створюється циклічний ланцюг переходів у випадковому порядку. Програма виконує 10 мільйонів послідовних стрибків у пам'яті, вимірюючи точну кількість процесорних циклів через `rdtsc`.

## Код реалізації алокатора та бенчмарка

Приклад демонструє два підходи до виділення пам’яті CXL: низькорівневий C-підхід з прямими викликами `libnuma` та ідіоматичний C++23 підхід із застосуванням RAII, смарт-поінтерів та шаблонів алокаторів.

:::tabs
```c
/* cxl_allocator_bench.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <numa.h>
#include <numaif.h>
#include <sys/mman.h>
#include <x86intrin.h>

#define BUFFER_SIZE (1024ULL * 1024ULL * 1024ULL) // 1 ГБ
#define STRIDE 64 // 64 байти (розмір кеш-лінії)

// Функція пошуку першого CPU-less NUMA вузла (CXL Node)
static int find_cxl_numa_node(void) {
    if (numa_available() < 0) {
        fprintf(stderr, "Помилка: підсистема NUMA недоступна у ядрі\n");
        return -1;
    }

    int max_node = numa_max_node();
    struct bitmask *cpus = numa_allocate_cpumask();

    for (int n = 0; n <= max_node; n++) {
        long long free_mem = 0;  // numa_node_size64() чекає саме long long *
        long long node_size = numa_node_size64(n, &free_mem);
        
        if (node_size > 0) {
            numa_node_to_cpus(n, cpus);
            // Якщо на вузлі немає CPU ядер, але є пам'ять -> це CXL/Tier2
            if (numa_bitmask_weight(cpus) == 0) {
                numa_free_cpumask(cpus);
                return n;
            }
        }
    }

    numa_free_cpumask(cpus);
    return -1;
}

// Бенчмарк затримки випадкового читання пам'яті (Pointer Chasing)
static double measure_latency_ns(uint64_t *ptr, size_t count) {
    // Ініціалізація циклічного ланцюга переходів у ВИПАДКОВОМУ порядку.
    // Постійний крок (i + k) % count апаратний prefetcher розпізнає й
    // випереджає — саме цього бенчмарк і має уникнути. Тому перемішуємо
    // алгоритмом Саттоло: він дає рівно один цикл довжини count.
    for (size_t i = 0; i < count; i++) {
        ptr[i] = i;
    }
    uint64_t rnd = 88172645463325252ULL;   // xorshift64, фіксоване зерно
    for (size_t i = count - 1; i > 0; i--) {
        rnd ^= rnd << 13; rnd ^= rnd >> 7; rnd ^= rnd << 17;
        size_t j = (size_t)(rnd % i);      // строго j < i — умова Саттоло
        uint64_t tmp = ptr[i]; ptr[i] = ptr[j]; ptr[j] = tmp;
    }

    uint64_t idx = 0;
    uint64_t start_cycles = __rdtsc();
    
    // Виконання 10 мільйонів переходів
    const uint64_t iterations = 10000000ULL;
    for (uint64_t i = 0; i < iterations; i++) {
        idx = ptr[idx];
    }
    
    uint64_t end_cycles = __rdtsc();
    
    // Запобігаємо оптимізації компілятора
    if (idx == 0xFFFFFFFF) printf("checksum: %lu\n", (unsigned long)idx);

    double total_cycles = (double)(end_cycles - start_cycles);
    // rdtsc рахує такти НЕЗМІННОГО TSC — це номінальна частота процесора,
    // а не поточна. Тут підставлено 3.0 ГГц (1 такт = 0.333 нс); на іншому
    // залізі коефіцієнт треба взяти з реальної номінальної частоти.
    return (total_cycles / iterations) / 3.0; 
}

int main(void) {
    int cxl_node = find_cxl_numa_node();
    if (cxl_node < 0) {
        printf("CXL вузол не знайдено. Використовуємо вузол 0 як запасний.\n");
        cxl_node = 0;
    } else {
        printf("Знайдено пам'ять CXL на NUMA Node %d\n", cxl_node);
    }

    // Виділяємо пам'ять через mmap
    void *addr = mmap(NULL, BUFFER_SIZE, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (addr == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    // Прив'язуємо адресний простір до CXL вузла через mbind
    unsigned long nodemask = (1UL << cxl_node);
    if (mbind(addr, BUFFER_SIZE, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) < 0) {
        perror("mbind failed");
        munmap(addr, BUFFER_SIZE);
        return 1;
    }

    // Примусова ініціалізація сторінок (Fault-in)
    memset(addr, 1, BUFFER_SIZE);

    size_t element_count = BUFFER_SIZE / sizeof(uint64_t);
    double latency = measure_latency_ns((uint64_t *)addr, element_count);
    printf("Середня затримка доступу до пам'яті CXL: %.2f нс\n", latency);

    munmap(addr, BUFFER_SIZE);
    return 0;
}
```
```cpp
// cxl_allocator_bench.cpp
#include <iostream>
#include <memory>
#include <vector>
#include <span>
#include <expected>
#include <chrono>
#include <cstdint>
#include <numeric>
#include <random>
#include <algorithm>
#include <cstring>
#include <numa.h>
#include <numaif.h>
#include <sys/mman.h>
#include <x86intrin.h>

namespace cxl {

enum class AllocationError {
    NumaUnavailable,
    NodeNotFound,
    MmapFailed,
    MbindFailed
};

// C++23 Custom Allocator із підтримкою RAII для CXL NUMA Node
template <typename T>
class CxlDeleter {
    size_t size_bytes_;
public:
    explicit CxlDeleter(size_t size_bytes = 0) : size_bytes_(size_bytes) {}
    void operator()(T* ptr) const noexcept {
        if (ptr && size_bytes_ > 0) {
            munmap(static_cast<void*>(ptr), size_bytes_);
        }
    }
};

template <typename T>
using UniqueCxlPtr = std::unique_ptr<T[], CxlDeleter<T>>;

class CxlMemoryManager {
public:
    static std::expected<int, AllocationError> find_cxl_node() noexcept {
        if (numa_available() < 0) {
            return std::unexpected(AllocationError::NumaUnavailable);
        }

        const int max_node = numa_max_node();
        struct bitmask* cpus = numa_allocate_cpumask();

        for (int n = 0; n <= max_node; ++n) {
            long long free_mem = 0;  // сигнатура: long long numa_node_size64(int, long long *)
            if (numa_node_size64(n, &free_mem) > 0) {
                numa_node_to_cpus(n, cpus);
                if (numa_bitmask_weight(cpus) == 0) {
                    numa_free_cpumask(cpus);
                    return n;
                }
            }
        }

        numa_free_cpumask(cpus);
        return std::unexpected(AllocationError::NodeNotFound);
    }

    template <typename T>
    static std::expected<UniqueCxlPtr<T>, AllocationError> allocate_cxl_span(size_t count, int node) {
        const size_t size_bytes = count * sizeof(T);
        void* addr = mmap(nullptr, size_bytes, PROT_READ | PROT_WRITE,
                          MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        
        if (addr == MAP_FAILED) {
            return std::unexpected(AllocationError::MmapFailed);
        }

        unsigned long nodemask = (1UL << node);
        if (mbind(addr, size_bytes, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) < 0) {
            munmap(addr, size_bytes);
            return std::unexpected(AllocationError::MbindFailed);
        }

        // Прогрів сторінок
        std::memset(addr, 0, size_bytes);

        return UniqueCxlPtr<T>(static_cast<T*>(addr), CxlDeleter<T>(size_bytes));
    }
};

class LatencyBenchmark {
public:
    static double run_pointer_chase(std::span<uint64_t> buffer) {
        const size_t count = buffer.size();
        // Перемішування Саттоло: рівно один цикл довжини count, який
        // апаратний prefetcher передбачити не може.
        std::iota(buffer.begin(), buffer.end(), uint64_t{0});
        std::mt19937_64 gen{20240601ULL};
        for (size_t i = count - 1; i > 0; --i) {
            const size_t j = std::uniform_int_distribution<size_t>{0, i - 1}(gen);
            std::swap(buffer[i], buffer[j]);
        }

        uint64_t idx = 0;
        const auto start = std::chrono::high_resolution_clock::now();
        const uint64_t iterations = 10'000'000ULL;

        for (uint64_t i = 0; i < iterations; ++i) {
            idx = buffer[idx];
        }

        const auto end = std::chrono::high_resolution_clock::now();
        const std::chrono::duration<double, std::nano> elapsed = end - start;

        if (idx == 0xFFFFFFFF) std::cout << "checksum: " << idx << '\n';

        return elapsed.count() / static_cast<double>(iterations);
    }
};

} // namespace cxl

int main() {
    auto cxl_node_res = cxl::CxlMemoryManager::find_cxl_node();
    int node = cxl_node_res.value_or(0);
    
    if (cxl_node_res.has_value()) {
        std::cout << "[C++23] Виявлено CXL пам'ять на вузлі: " << node << '\n';
    } else {
        std::cout << "[C++23] CXL вузол не знайдено, використовуємо резервний вузол 0\n";
    }

    constexpr size_t element_count = (1024ULL * 1024ULL * 1024ULL) / sizeof(uint64_t); // 1 ГБ
    auto alloc_res = cxl::CxlMemoryManager::allocate_cxl_span<uint64_t>(element_count, node);

    if (!alloc_res) {
        std::cerr << "Помилка виділення CXL пам'яті!\n";
        return 1;
    }

    auto& cxl_buf = alloc_res.value();
    std::span<uint64_t> buf_span(cxl_buf.get(), element_count);

    double latency_ns = cxl::LatencyBenchmark::run_pointer_chase(buf_span);
    std::cout << "[C++23] Середня затримка CXL RAM: " << latency_ns << " нс\n";

    return 0;
}
```
:::

## Аналіз результатів вимірювання та апаратні особливості

Під час запуску сформованого бенчмарку на реальному серверному обладнанні з карткою розширення CXL Type 3 можна спостерігати суттєву відмінність у затримках та пропускній здатності залежно від топологічного розміщення пам'яті.

При виділенні пам'яті на локальному вузлі DDR5 (Node 0) затримка вибірки через алгоритм Pointer Chasing становить орієнтовно від 78 до 85 наносекунд, а послідовна пропускна здатність сягає 120 гігабайтів на секунду.

При виділенні пам'яті на сусідньому процесорному сокеті (Node 1) затримка зростає до 130–145 наносекунд через додаткові кроки транзитного проходження через міжпроцесорні шини UPI/Infinity Fabric.

При виділенні пам'яті на пристрої CXL Type 3 (Node 2) затримка становить від 220 до 240 наносекунд. Послідовна пропускна здатність обмежується швидкістю фізичної шини PCIe 5.0 x16 (теоретична стеля — близько 64 ГБ/с в одному напрямку) і на практиці становить близько 45–50 гігабайтів на секунду.

### Типові пастки розробників при використанні CXL-пам'яті

Перша пастка: Ігнорування прапорця `MPOL_MF_MOVE` у виклику `mbind()`. Якщо сторінки процесу вже були проініціалізовані раніше, системний виклик `mbind()` без цього прапорця поверне успішний код `0`, але фізична міграція сторінок у CXL-пам'ять не відбудеться.

Друга пастка: Вплив апаратного випереджального читання (Hardware Prefetcher). Якщо замість випадкового ланцюга переходів застосувати послідовний обхід масиву — або навіть обхід із постійним кроком, — prefetcher кеша L2 розпізнає закономірність і підтягне лінії з CXL заздалегідь. Тоді вимірювання покаже не затримку памʼяті, а пропускну здатність, і цифра вийде у кілька разів меншою за справжню.

Третя пастка: Промахи буфера трансляції адрес (TLB Misses). При роботі з великими масивами даних (понад 1 ГБ) у пам'яті CXL виникають суттєві накладні витрати на трансляцію таблиць сторінок. Для усунення цієї проблеми в реальних промислових системах рекомендується використовувати величезні сторінки HugePages (2 МБ або 1 ГБ) шляхом додавання прапорця `MAP_HUGETLB` у виклику `mmap()`.
