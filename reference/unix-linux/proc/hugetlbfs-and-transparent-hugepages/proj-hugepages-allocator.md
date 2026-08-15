# ⚙️ Практичний вимірювач продуктивності пам'яті: hugetlbfs, THP та стандартні сторінки

Цей приклад показує, як зібрати бенчмарк для вимірювання затримок випадкового доступу до великого масиву оперативної пам'яті розміром 256 МіБ за трьох різних стратегій виділення: стандартні сторінки 4 КіБ, прозорі сторінки THP із підказкою `MADV_HUGEPAGE` та явні великі сторінки `hugetlbfs`.

## Ідея бенчмарку та архітектура вимірювання

Головна мета цього проєкту — показати на практиці вплив апаратного кешування трансляцій адрес (TLB) на швидкість виконання операцій читання та запису у пам'яті під час доступу до великих даних.

Програма порівнює три режими керування пам'яттю:

1. **Стандартний `mmap()` (4 КіБ сторінки):** Стандартне анонімне відображення пам'яті у ядрі Linux. Для адресації масиву 256 МіБ ядро створює 65 536 записів у таблицях сторінок PTE, що спричиняє постійні промахи кешу TLB при випадковому доступі.
2. **THP `madvise()` (2 МіБ сторінки):** Стандартний `mmap()`, для якого одразу після створення викликається системний виклик `madvise(..., MADV_HUGEPAGE)`. Це підказує ядру спробувати прозоро згорнути 512 сторінок по 4 КіБ у суцільні блоки 2 МіБ, зменшуючи кількість записів у таблицях сторінок до 128.
3. **HugeTLB `mmap()` (2 МіБ сторінки):** Виклики `mmap()` із системними прапорцями `MAP_HUGETLB | MAP_HUGE_2MB`, які звертаються напряму до зарезервованого ядра пулу `hugetlbfs`. Це гарантує виділення 128 суцільних сторінок по 2 МіБ без затримок на дефрагментацію пам'яті та без ризику розщеплення.

Для усунення викривлення результатів обчислювальною потужністю центрального процесора алгоритм тестового обходу використовує швидкий лінійний конгруентний генератор псевдовипадкових чисел (LCG) `seed = seed * 1664525u + 1013904223u`. Це мінімізує кількість арифметичних інструкцій CPU на кожній ітерації, роблячи затримку шини пам'яті та кешу TLB головним обмежуючим фактором.

## Двомовна реалізація вимірювача пам'яті

Нижче наведено дві повноцінні реалізації бенчмарку: мовою C із застосуванням низькорівневого POSIX API та мовою C++ із використанням RAII, безпечного управління ресурсами через `std::unique_ptr`, обробки помилок через `std::expected` (це вже C++23) та вимірювання часу через `std::chrono`.

:::tabs
```c
/* benchmark_hugepages.c — Реалізація мовою C із використанням POSIX API */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/mman.h>
#include <unistd.h>

#define ALLOC_SIZE (256 * 1024 * 1024) // 256 МіБ
#define NUM_ACCESSES 10000000          // 10 млн випадкових звернень

typedef enum {
    MODE_STANDARD_4K,
    MODE_THP_MADVISE,
    MODE_HUGETLB_2M
} alloc_mode_t;

// Допоміжна функція для точного вимірювання часу у секундах
static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

// Виділення пам'яті відповідно до обраного режиму
static uint8_t* allocate_buffer(alloc_mode_t mode) {
    uint8_t *ptr = NULL;

    switch (mode) {
        case MODE_STANDARD_4K:
            ptr = (uint8_t*)mmap(NULL, ALLOC_SIZE, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (ptr == MAP_FAILED) {
                perror("Помилка mmap (4K)");
                return NULL;
            }
            break;

        case MODE_THP_MADVISE:
            ptr = (uint8_t*)mmap(NULL, ALLOC_SIZE, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (ptr == MAP_FAILED) {
                perror("Помилка mmap (THP)");
                return NULL;
            }
            if (madvise(ptr, ALLOC_SIZE, MADV_HUGEPAGE) != 0) {
                perror("Попередження: madvise(MADV_HUGEPAGE) не вдалося");
            }
            break;

        case MODE_HUGETLB_2M:
            ptr = (uint8_t*)mmap(NULL, ALLOC_SIZE, PROT_READ | PROT_WRITE,
                                 MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB | MAP_HUGE_2MB,
                                 -1, 0);
            if (ptr == MAP_FAILED) {
                perror("Помилка mmap (HugeTLB 2M — перевірте vm.nr_hugepages)");
                return NULL;
            }
            break;
    }

    return ptr;
}

// Бенчмарк випадкового доступу до буфера
static void run_benchmark(const char *name, alloc_mode_t mode) {
    uint8_t *buffer = allocate_buffer(mode);
    if (!buffer) return;

    // 1. Прогрів пам'яті (ініціалізація сторінкових збоїв page fault)
    for (size_t i = 0; i < ALLOC_SIZE; i += 4096) {
        buffer[i] = 1;
    }

    // 2. Генерація псевдовипадкового обходу
    uint32_t seed = 0x12345678;
    double start_time = get_time_sec();

    volatile uint64_t sum = 0;
    size_t mask = ALLOC_SIZE - 1;

    for (size_t i = 0; i < NUM_ACCESSES; ++i) {
        // Простий генератор LCG для низьких накладних витрат CPU
        seed = seed * 1664525u + 1013904223u;
        size_t index = (size_t)seed & mask;
        sum += buffer[index];
        buffer[index] = (uint8_t)(sum & 0xFF);
    }

    double elapsed = get_time_sec() - start_time;
    double ns_per_access = (elapsed / NUM_ACCESSES) * 1e9;

    printf("[C] %-20s: Час = %.4f сек | Затримка = %.2f нс/доступ (sum=%lu)\n",
           name, elapsed, ns_per_access, (unsigned long)sum);

    munmap(buffer, ALLOC_SIZE);
}

int main(void) {
    printf("=== Вимірювач продуктивності пам'яті (256 МіБ, 10 млн операцій) ===\n");
    run_benchmark("Стандартні 4K", MODE_STANDARD_4K);
    run_benchmark("THP (madvise)", MODE_THP_MADVISE);
    run_benchmark("HugeTLB (2M)", MODE_HUGETLB_2M);
    return 0;
}
```
```cpp
// benchmark_hugepages.cpp — Ідіоматична реалізація мовою C++23 із використанням RAII та chrono
#include <iostream>
#include <vector>
#include <numeric>
#include <chrono>
#include <memory>
#include <random>
#include <string_view>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <unistd.h>

namespace memory_bench {

constexpr size_t ALLOC_SIZE = 256 * 1024 * 1024; // 256 МіБ
constexpr size_t NUM_ACCESSES = 10000000;          // 10 млн звернень

enum class AllocationMode {
    Standard4K,
    ThpMadvise,
    Hugetlb2M
};

// RAII-обгортка для безпечного управління пам'яттю mmap
struct MmapDeleter {
    size_t length{0};
    void operator()(uint8_t* ptr) const noexcept {
        if (ptr && ptr != MAP_FAILED) {
            ::munmap(ptr, length);
        }
    }
};

using UniqueMmap = std::unique_ptr<uint8_t[], MmapDeleter>;

// Клас фабрики з виділення пам'яті через std::expected
class MemoryBuffer {
public:
    static std::expected<UniqueMmap, std::string> create(AllocationMode mode) {
        int flags = MAP_PRIVATE | MAP_ANONYMOUS;
        if (mode == AllocationMode::Hugetlb2M) {
            flags |= MAP_HUGETLB | MAP_HUGE_2MB;
        }

        void* raw_ptr = ::mmap(nullptr, ALLOC_SIZE, PROT_READ | PROT_WRITE, flags, -1, 0);
        if (raw_ptr == MAP_FAILED) {
            return std::unexpected("Не вдалося виконати mmap: " + std::string(strerror(errno)));
        }

        auto ptr = static_cast<uint8_t*>(raw_ptr);

        if (mode == AllocationMode::ThpMadvise) {
            if (::madvise(ptr, ALLOC_SIZE, MADV_HUGEPAGE) != 0) {
                std::cerr << "Попередження: madvise(MADV_HUGEPAGE) повернув помилку: " 
                          << strerror(errno) << '\n';
            }
        }

        return UniqueMmap(ptr, MmapDeleter{ALLOC_SIZE});
    }
};

class BenchmarkRunner {
public:
    static void run(std::string_view name, AllocationMode mode) {
        auto result = MemoryBuffer::create(mode);
        if (!result) {
            std::cerr << "[C++] " << name << " -> Помилка: " << result.error() << '\n';
            return;
        }

        auto& buffer = result.value();

        // 1. Прогрів пам'яті через крок у 4 КіБ
        for (size_t i = 0; i < ALLOC_SIZE; i += 4096) {
            buffer[i] = 1;
        }

        // 2. Бенчмарк за допомогою шаблонів chrono та LCG
        uint32_t seed = 0x12345678;
        const size_t mask = ALLOC_SIZE - 1;
        volatile uint64_t sum = 0;

        const auto start = std::chrono::high_resolution_clock::now();

        for (size_t i = 0; i < NUM_ACCESSES; ++i) {
            seed = seed * 1664525u + 1013904223u;
            const size_t index = static_cast<size_t>(seed) & mask;
            sum += buffer[index];
            buffer[index] = static_cast<uint8_t>(sum & 0xFF);
        }

        const auto end = std::chrono::high_resolution_clock::now();
        const std::chrono::duration<double, std::nano> elapsed_ns = end - start;

        const double total_sec = elapsed_ns.count() * 1e-9;
        const double ns_per_access = elapsed_ns.count() / NUM_ACCESSES;

        std::cout << "[C++] " << name << ": Час = " << total_sec 
                  << " сек | Затримка = " << ns_per_access 
                  << " нс/доступ (sum=" << sum << ")\n";
    }
};

} // namespace memory_bench

int main() {
    std::cout << "=== C++ Вимірювач продуктивності пам'яті (256 МіБ) ===\n";
    memory_bench::BenchmarkRunner::run("Стандартні 4K", memory_bench::AllocationMode::Standard4K);
    memory_bench::BenchmarkRunner::run("THP (madvise)", memory_bench::AllocationMode::ThpMadvise);
    memory_bench::BenchmarkRunner::run("HugeTLB (2M)", memory_bench::AllocationMode::Hugetlb2M);
    return 0;
}
```
:::

## Покроковий розбір механізмів коду

Для глибокого розуміння роботи коду розберемо його ключові етапи та внутрішні механізми ядра:

### 1. Виділення пам'яті та ініціалізація сторінкових збоїв

У сучасних ОС Linux системні виклики `mmap()` застосовують механізм відкладеного виділення (*lazy allocation*). Виклик `mmap()` лише резервує діапазон адресового простору у структурі VMA процесу, не виділяючи реальних фізичних блоків у RAM. 

Саме тому в обох реалізаціях присутній обов'язковий цикл прогріву:

:::tabs
```c
// Прогрів пам'яті у мові C
for (size_t i = 0; i < ALLOC_SIZE; i += 4096) {
    buffer[i] = 1;
}
```
```cpp
// Прогрів пам'яті у мові C++
for (size_t i = 0; i < ALLOC_SIZE; i += 4096) {
    buffer[i] = 1;
}
```
:::

Запис першого байта в кожну сторінку викликає апаратний сторінковий збій (*page fault*). Обробник ядра виділяє фізичний фрейм RAM, записує в нього дані та оновлює записи в таблицях сторінок. Якщо цього прогріву не виконати, вимірювання затримок включатиме накладні витрати виділення сторінок ядром безпосередньо під час тесту, що сильно спотворить підсумкові результати.

### 2. Забезпечення безпеки C++ через RAII та std::expected

У C++ реалізації використання сирих вказівників та `goto`-структур замінено на власний засіб видалення (*deleter*) `MmapDeleter` для `std::unique_ptr`. Це гарантує автоматичне виконання системного виклику `munmap()` при виході об'єкта `UniqueMmap` із області видимості — навіть у разі генерування винятків чи передчасного виходу з функції.

Функція `MemoryBuffer::create()` повертає монадний тип `std::expected<UniqueMmap, std::string>` (стандарт C++23). Якщо виклик `mmap()` завершується помилкою (наприклад, через відсутність зарезервованих сторінок HugeTLB), функція повертає об'єкт `std::unexpected` із описом помилки `strerror(errno)`, не спричиняючи аварійного завершення програми.

### 3. Правила вирівнювання адрес для MAP_HUGETLB

При використанні прапорця `MAP_HUGETLB` виклики `mmap()` підлягають суворому обмеженню: як замовлюваний розмір пам'яті `ALLOC_SIZE`, так і адреса відображення мусять бути кратні розміру великої сторінки (2 МіБ = 2097152 байтів). Якщо передати розмір, не кратний 2 МіБ, ядро поверне помилку `EINVAL` або `ENOMEM`.

### 4. Взаємодія з алокаторами ptmalloc, jemalloc та tcmalloc

Стандартний алокатор пам'яті `glibc` (`ptmalloc`) для виділень масивів понад 128 КіБ за замовчуванням звертається до системного виклику `mmap()`, а не розширює купу через `sbrk()`. Високонавантажені алокатори пам'яті `jemalloc` та `tcmalloc` розроблені з урахуванням вирівнювання виділень під межі 2 МіБ. Вони автоматично застосовують системний виклик `madvise(..., MADV_HUGEPAGE)` до великих ділянок своїх арен (*arenas*), забезпечуючи автоматичну підтримку THP без втручання користувача.

## Збирання, конфігурація та запуск проєкту

Для компіляції та виконання бенчмарку на системі Linux підготуйте середовище:

### 1. Попередня резервація сторінок HugeTLB у системі

Перед запуском вимірювача необхідно виділити щонайменше 128 великих сторінок по 2 МіБ у пулі ядра (загалом 256 МіБ):

```bash
sudo sysctl vm.nr_hugepages=128
```

Перевірте статус резервації через procfs:

```bash
grep HugePages_Total /proc/meminfo
```

### 2. Компіляція вихідних файлів

Компіляція версії на C виконується з прапорцями оптимізації `-O3` та підтримкою POSIX `clock_gettime`:

```bash
gcc -O3 -std=c11 benchmark_hugepages.c -o benchmark_c
```

Реалізація на C++ спирається на `std::expected`, а це заголовок стандарту C++23, тож потрібні GCC 12+ або Clang 16+ і відповідний ключ стандарту:

```bash
g++ -O3 -std=c++23 benchmark_hugepages.cpp -o benchmark_cpp
```

### 3. Налаштування лімітів блокування пам'яті у /etc/security/limits.conf

Якщо додаток запускається від імені звичайного користувача без прав `root`, виклик `mmap()` із прапорцем `MAP_HUGETLB` або виклики `mlock()` можуть відхилятися через перевищення ліміту `RLIMIT_MEMLOCK`.

Для зняття обмежень додайте наступний рядок у файл `/etc/security/limits.conf`:

```text
*    soft    memlock    unlimited
*    hard    memlock    unlimited
```

Після оновлення конфігурації необхідно перезапустити сесію користувача.

## Простеження та діагностика під час виконання

Під час виконання тестового бінарного файлу можна перевірити реальний стан сторінок пам'яті за допомогою утиліт `smaps` та `meminfo`.

Для спостереження за процесом у реальному часі відкрийте другий термінал і виконайте команду:

```bash
watch -n 0.5 "cat /proc/\$(pgrep benchmark)/smaps | grep -E '(Size|AnonHugePages|KernelPageSize)'"
```

Під час виконання тесту `THP (madvise)` ви побачите, як поле `AnonHugePages` зростає від 0 до `262144 kB` (256 МіБ). Це свідчить про те, що демон `khugepaged` або обробник page fault успішно згорнув 512 сторінок по 4 КіБ у суцільні сторінки 2 МіБ.

Під час виконання тесту `HugeTLB (2M)` у файлі `/proc/meminfo` два поля змінюються по черзі: одразу після `mmap()` на 128 зростає `HugePages_Rsvd` (ядро закріплює за відображенням резерв, ще не торкаючись пулу), а вже під час циклу прогріву `HugePages_Rsvd` спадає назад до нуля й рівно на ці ж 128 сторінок зменшується `HugePages_Free` — резерв перетворюється на справді виділені сторінки.

Також можна виміряти точну кількість промахів TLB за допомогою інструменту `perf`:

```bash
perf stat -e dTLB-loads,dTLB-load-misses ./benchmark_hugepages
```

Ви побачите, що у режимах THP та HugeTLB кількість промахів `dTLB-load-misses` буде в 10–20 разів меншою, ніж у режимі стандартних сторінок 4 КіБ.

## Порівняльний аналіз архітектурних ідіом C та C++

При порівнянні обох реалізацій помітна фундаментальна відмінність у стилях програмування під Linux:

1. **Управління ресурсами.** Мова C покладається на ручний виклик `munmap(buffer, ALLOC_SIZE)` перед кожним виходом із функції, що створює ризик витоку адресового простору у разі передчасного `return`. Мова C++ вирішує це за допомогою структури `MmapDeleter`, яка зв'язує розмір відображення із самою сутністю вказівника `std::unique_ptr`.
2. **Обробка виняткових ситуацій.** У мові C перевірка помилок виконується через повернення указівника `MAP_FAILED` та аналіз глобальної змінної `errno`. Мова C++ застосовує концепцію функціональної обробки через `std::expected`, яка дозволяє коду, що викликає, чітко розрізняти успішний об'єкт та об'єкт помилки без використання важких винятків `try/catch`.
3. **Вимірювання інтервалів часу.** Функція `clock_gettime(CLOCK_MONOTONIC)` у C вимагає ручного переведення наносекунд у дробову частину секунд. Модуль `std::chrono` у C++ виконує перетворення типів вимірювачів автоматично на етапі компіляції, без накладних витрат під час виконання.

## Типові помилки та пастки при розробці

1. **Відсутність попередньої резервації HugeTLB.** Запуск тесту HugeTLB без попередньої конфігурації `sysctl vm.nr_hugepages=128` призведе до помилки `MAP_FAILED` (`ENOMEM`), оскільки порожній пул ядра не зможе задовольнити запит `MAP_HUGETLB`.
2. **Пастка Copy-on-Write при викликах fork().** Якщо програма виконує `fork()` після виділення пам'яті THP або HugeTLB, ядро змушене скидати прапорці запису і позначати сторінки як Copy-on-Write (CoW). При першому ж записі дочірнього або батьківського процесу ядро виконає примусове розщеплення 2 МіБ сторінки на 512 сторінок 4 КіБ, що призведе до величезного падіння продуктивності.
3. **Нехтування NUMA-локальністю.** На двосокетних серверах виділення пам'яті HugeTLB на вузлі NUMA 0 при виконанні потоку на сокеті 1 призводить до міжпроцесорних затримок шини UPI, які повністю перекривають виграш від кешування TLB. Для усунення цього ефекту слід прив'язувати процес до вузла через `numactl --membind=0 --cpunodebind=0`.

## Аналіз результатів вимірювання

Типовий результат виконання вимірювача на сервері x86_64 з підсистемою пам'яті DDR4/DDR5:

```text
=== Вимірювач продуктивності пам'яті (256 МіБ, 10 млн операцій) ===
[C] Стандартні 4K       : Час = 0.2845 сек | Затримка = 28.45 нс/доступ (sum=1420583)
[C] THP (madvise)       : Час = 0.1820 сек | Затримка = 18.20 нс/доступ (sum=1420583)
[C] HugeTLB (2M)        : Час = 0.1742 сек | Затримка = 17.42 нс/доступ (sum=1420583)
```

Завдяки використанню великих сторінок 2 МіБ (HugeTLB та THP) середній час доступу до кожного елемента масиву зменшується майже на **35–40%** за рахунок кардинального зменшення промахів TLB L2.
