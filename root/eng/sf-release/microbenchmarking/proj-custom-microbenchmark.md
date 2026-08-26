# ⚙️ Автономний каркас мікробенчмаркінгу на C та C++

Готові індустріальні бібліотеки на зразок Google Benchmark є стандартом для великих прикладних проєктів, проте вбудовані системи (embedded), ядра операційних систем, завантажувачі, прошивки мікроконтролерів та автономні алгоритмічні бібліотеки вимагають компактного вимірювального каркаса без зовнішніх залежностей. Спроба написати такий каркас самостійно зазвичай завершується наївним циклом із викликом `gettimeofday()`, який або повністю знищується оптимізатором, або вимірює накладні витрати операційної системи замість корисного алгоритму. Нижче наведено завершену реалізацію автономного мікробенчмаркінгового рушія, спроєктованого з урахуванням апаратних бар'єрів компілятора, прив'язки до процесорного ядра, автокалібрування циклів та непараметричної статистики.

## Інженерні виклики та вимоги до автономного каркаса

Створення надійного мікробенчмарку без сторонніх бібліотек вимагає одночасного розв'язання чотирьох фундаментальних проблем на стику апаратури, операційної системи та транслятора:

1. **Ізоляція від планувальника ОС (CPU Affinity):**
   Сучасні багатоядерні операційні системи постійно мігрують потоки між фізичними ядрами для вирівнювання теплового балансу. Міграція потоку посеред заміру призводить до миттєвої втрати вмісту L1-кешу інструкцій і даних, скидання конвеєра та появи гігантського викиду на 10 000–50 000 наносекунд. Каркас зобов'язаний жорстко прив'язувати вимірювальний потік до обраного ядра через системний виклик `sched_setaffinity()` (у Linux) або `pthread_setaffinity_np()`.

2. **Подолання дискретності системного таймера:**
   Якщо досліджувана операція триває 2 наносекунди, а роздільна здатність системного годинника становить 20 наносекунд, один замір матиме 1000% відносної похибки. Каркас повинен автоматично визначати кількість ітерацій `N` у внутрішньому циклі (батчі), експоненціально нарощуючи лічильник, доки сумарний час виконання батчу не досягне безпечного порогу в 2–5 мілісекунд (що перевищує похибку таймера в сотні тисяч разів).

3. **Абсолютний захист від компілятора (Optimization Barriers):**
   Компілятор не повинен мати змоги передбачити вхідні дані, згорнути цикл у константу або видалити обчислення як мертвий код (DCE). Водночас бар'єр захисту не має додавати жодної зайвої інструкції в асемблерний лістинг гарячого циклу.

4. **Непараметрична агрегація вибірки:**
   Вимірювання одного батчу не дає повної картини. Необхідно зібрати серію з кількох сотень незалежних замірів, впорядкувати їх за зростанням та обчислити стійкі статистичні квантилі: медіану (`p50`), інтерквартильний розмах (`IQR`) та хвостові перцентилі (`p95`, `p99`), відкинувши хибну практику використання середнього арифметичного.

## Вихідний код каркаса

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <sched.h>
#include <unistd.h>

/* Оптимізаційний бар'єр для C: змушує компілятор вважати, що значення
   змінної val передано в непрозорий асемблерний блок */
static inline void do_not_optimize_val(uint64_t val) {
    __asm__ volatile("" : : "r,m"(val) : "memory");
}

/* Читання монотонного фізичного таймера в наносекундах */
static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Прив'язка поточного потоку до конкретного процесорного ядра */
static bool pin_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    return sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) == 0;
}

/* Структура підсумкових статистичних результатів */
typedef struct {
    double min_ns;
    double median_ns;
    double p95_ns;
    double p99_ns;
    double iqr_ns;
} BenchmarkResult;

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Визначення перцентиля за лінійною інтерполяцією */
static double compute_percentile(const double *sorted, size_t n, double p) {
    if (n == 0) return 0.0;
    if (n == 1) return sorted[0];
    double k = p * (double)(n - 1);
    size_t i = (size_t)k;
    double f = k - (double)i;
    if (i >= n - 1) return sorted[n - 1];
    return sorted[i] + f * (sorted[i + 1] - sorted[i]);
}

/* Тип випробуваної функції: приймає цілочисельний стан або індекс */
typedef uint64_t (*BenchFunc)(uint64_t);

/* Головна функція прогону бенчмарку */
BenchmarkResult run_benchmark(BenchFunc fn, uint64_t target_batch_ns, size_t num_samples) {
    BenchmarkResult res = {0};

    /* 1. Фаза калібрування: знаходимо N ітерацій, що тривають ~ target_batch_ns (наприклад 2 мс) */
    uint64_t iters = 16;
    while (true) {
        uint64_t t0 = get_time_ns();
        for (uint64_t i = 0; i < iters; ++i) {
            uint64_t v = fn(i);
            do_not_optimize_val(v);
        }
        uint64_t dt = get_time_ns() - t0;
        if (dt >= target_batch_ns || iters >= (1ULL << 30)) {
            break;
        }
        if (dt == 0) iters *= 4;
        else iters = (iters * target_batch_ns) / dt + 1;
    }

    /* 2. Фаза прогріву (Warmup): стабілізуємо кеш і стан гілок */
    for (uint64_t i = 0; i < iters; ++i) {
        uint64_t v = fn(i);
        do_not_optimize_val(v);
    }

    /* 3. Збір вибірки незалежних зразків */
    double *samples = (double *)malloc(sizeof(double) * num_samples);
    if (!samples) return res;

    for (size_t s = 0; s < num_samples; ++s) {
        uint64_t t0 = get_time_ns();
        for (uint64_t i = 0; i < iters; ++i) {
            uint64_t v = fn(i);
            do_not_optimize_val(v);
        }
        uint64_t dt = get_time_ns() - t0;
        samples[s] = (double)dt / (double)iters;
    }

    /* 4. Сортування та розрахунок квантилів */
    qsort(samples, num_samples, sizeof(double), compare_doubles);

    res.min_ns = samples[0];
    res.median_ns = compute_percentile(samples, num_samples, 0.50);
    double q1 = compute_percentile(samples, num_samples, 0.25);
    double q3 = compute_percentile(samples, num_samples, 0.75);
    res.iqr_ns = q3 - q1;
    res.p95_ns = compute_percentile(samples, num_samples, 0.95);
    res.p99_ns = compute_percentile(samples, num_samples, 0.99);

    free(samples);
    return res;
}

/* Приклад алгоритму: 64-бітне швидке хешування (xorshift64) */
static uint64_t bench_xorshift(uint64_t state) {
    uint64_t x = state + 0x9E3779B97F4A7C15ULL;
    x ^= x >> 30;
    x *= 0xBF58476D1CE4E5B9ULL;
    x ^= x >> 27;
    x *= 0x94D049BB133111EBULL;
    x ^= x >> 31;
    return x;
}

int main(void) {
    if (pin_to_core(1)) {
        printf("Потік успішно прив'язано до CPU 1\n");
    }

    printf("Запуск мікробенчмарку xorshift64...\n");
    BenchmarkResult r = run_benchmark(bench_xorshift, 2000000ULL /* 2 мс */, 200 /* зразків */);

    printf("--- Результати ---\n");
    printf("Min:    %.3f нс / операція\n", r.min_ns);
    printf("Median: %.3f нс / операція\n", r.median_ns);
    printf("IQR:    %.3f нс\n", r.iqr_ns);
    printf("p95:    %.3f нс\n", r.p95_ns);
    printf("p99:    %.3f нс\n", r.p99_ns);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <thread>
#include <pthread.h>

namespace bench {

/* Оптимізаційний бар'єр для C++: гарантує обчислення виразу без накладних інструкцій */
template <typename T>
inline void do_not_optimize(T&& value) {
    #if defined(__clang__)
    asm volatile("" : "+r,m"(value) : : "memory");
    #else
    asm volatile("" : : "g"(value) : "memory");
    #endif
}

inline void clobber_memory() {
    asm volatile("" : : : "memory");
}

/* Прив'язка поточного потоку до конкретного процесорного ядра */
inline bool pin_current_thread(int core_id) noexcept {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    return pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0;
}

struct Statistics {
    double min_ns{0.0};
    double median_ns{0.0};
    double p95_ns{0.0};
    double p99_ns{0.0};
    double iqr_ns{0.0};
};

/* Розрахунок перцентиля за лінійною інтерполяцією для відсортованого вектора */
inline double percentile(const std::vector<double>& sorted, double p) noexcept {
    if (sorted.empty()) return 0.0;
    if (sorted.size() == 1) return sorted.front();
    const double k = p * static_cast<double>(sorted.size() - 1);
    const auto i = static_cast<std::size_t>(k);
    const double f = k - static_cast<double>(i);
    if (i >= sorted.size() - 1) return sorted.back();
    return sorted[i] + f * (sorted[i + 1] - sorted[i]);
}

/* Каркас прогону мікробенчмарку для довільного callable-об'єкта */
template <typename Func>
Statistics benchmark(Func&& fn, std::chrono::nanoseconds target_batch = std::chrono::milliseconds(2), std::size_t num_samples = 200) {
    using clock = std::chrono::high_resolution_clock;

    // 1. Автоматичне калібрування кількості ітерацій у батчі
    std::uint64_t iters = 16;
    while (true) {
        const auto t0 = clock::now();
        for (std::uint64_t i = 0; i < iters; ++i) {
            auto res = fn(i);
            do_not_optimize(res);
        }
        const auto dt = std::chrono::duration_cast<std::chrono::nanoseconds>(clock::now() - t0);
        if (dt >= target_batch || iters >= (1ULL << 30)) {
            break;
        }
        const auto dt_count = std::max<std::int64_t>(1, dt.count());
        iters = static_cast<std::uint64_t>((static_cast<double>(iters) * target_batch.count()) / dt_count) + 1;
    }

    // 2. Фаза прогріву (Warmup)
    for (std::uint64_t i = 0; i < iters; ++i) {
        auto res = fn(i);
        do_not_optimize(res);
    }

    // 3. Збір незалежних замірів
    std::vector<double> samples;
    samples.reserve(num_samples);

    for (std::size_t s = 0; s < num_samples; ++s) {
        const auto t0 = clock::now();
        for (std::uint64_t i = 0; i < iters; ++i) {
            auto res = fn(i);
            do_not_optimize(res);
        }
        const auto dt = std::chrono::duration_cast<std::chrono::nanoseconds>(clock::now() - t0);
        samples.push_back(static_cast<double>(dt.count()) / static_cast<double>(iters));
    }

    // 4. Статистичний аналіз
    std::sort(samples.begin(), samples.end());

    Statistics stats;
    stats.min_ns = samples.front();
    stats.median_ns = percentile(samples, 0.50);
    const double q1 = percentile(samples, 0.25);
    const double q3 = percentile(samples, 0.75);
    stats.iqr_ns = q3 - q1;
    stats.p95_ns = percentile(samples, 0.95);
    stats.p99_ns = percentile(samples, 0.99);

    return stats;
}

} // namespace bench

// Тестовий алгоритм: швидке 64-бітне псевдовипадкове перемішування
constexpr std::uint64_t hash_mix(std::uint64_t state) noexcept {
    std::uint64_t x = state + 0x9E3779B97F4A7C15ULL;
    x ^= (x >> 30);
    x *= 0xBF58476D1CE4E5B9ULL;
    x ^= (x >> 27);
    x *= 0x94D049BB133111EBULL;
    x ^= (x >> 31);
    return x;
}

int main() {
    if (bench::pin_current_thread(1)) {
        std::cout << "Потік успішно прив'язано до CPU 1\n";
    }

    std::cout << "Запуск мікробенчмарку hash_mix...\n";
    const auto stats = bench::benchmark(hash_mix, std::chrono::milliseconds(2), 200);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "--- Результати ---\n";
    std::cout << "Min:    " << stats.min_ns << " нс / операція\n";
    std::cout << "Median: " << stats.median_ns << " нс / операція\n";
    std::cout << "IQR:    " << stats.iqr_ns << " нс\n";
    std::cout << "p95:    " << stats.p95_ns << " нс\n";
    std::cout << "p99:    " << stats.p99_ns << " нс\n";

    return 0;
}
```
:::

## Покроковий розбір критичних блоків каркаса

Реалізація містить кілька тонких інженерних рішень, які гарантують математичну та апаратну коректність вимірів:

### 1. Вибір джерела часу `CLOCK_MONOTONIC_RAW`
У версії на мові C використано виклик `clock_gettime(CLOCK_MONOTONIC_RAW)`. На відміну від стандартного `CLOCK_MONOTONIC`, версія `RAW` звертається безпосередньо до апаратного тактового генератора й не піддається плавному коригуванню швидкості ходу з боку мережевого протоколу NTP (NTP Slew/Drift adjustments). Це повністю виключає штучне розтягування або стискання вимірюваних секунд під час прогону.

### 2. Експоненціальне автокалібрування батчу
Калібрувальний цикл починається з 16 ітерацій. Якщо тривалість заміру `dt` менша за цільовий час батчу `target_batch_ns` (наприклад, 2 000 000 нс), алгоритм виконує пропорційну екстраполяцію:
`iters = (iters * target_batch_ns) / dt + 1`.
Якщо час заміру був настільки малим, що таймер показав 0 нс, розмір ітерацій збільшується вчетверо. Це дозволяє за 3–4 кроки підібрати точний розмір батчу для будь-якої функції — як тієї, що триває 1 наносекунду, так і тієї, що триває 50 мікросекунд.

### 3. Гарантії безпеки оптимізаційного бар'єра
Вставка `asm volatile("" : : "g"(val) : "memory")` використовує обмеження `"g"` (general operand: регістр, пам'ять або цілочисельна константа) у поєднанні з клоббером `"memory"`. Це повідомляє оптимізатору GCC та Clang, що асемблерний фрагмент може прочитати значення `val` та виконати довільне читання/запис у пам'ять. В результаті компілятор змушений повністю виконати код обчислення `val`, але не генерує жодної додаткової інструкції `mov` чи `push/pop`.

### 4. Калібрування та віднімання зсуву таймера (Timer Bias)
Під час вимірювання надкоротких батчів накладні витрати на два системні виклики `clock_gettime` (приблизно 30–40 наносекунд сумарно) можуть вносити невеликий систематичний зсув. У прецизійних вимірах перед початком сесії викликають порожній калібрувальний цикл:
:::tabs
```c
uint64_t t0 = get_time_ns();
for (uint64_t i = 0; i < iters; ++i) {
    do_not_optimize_val(i);
}
uint64_t t_bias = get_time_ns() - t0;
```
```cpp
const auto t0 = std::chrono::high_resolution_clock::now();
for (std::uint64_t i = 0; i < iters; ++i) {
    bench::do_not_optimize(i);
}
const auto t_bias = std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::high_resolution_clock::now() - t0).count();
```
:::
Цей базовий час `t_bias` фіксує накладні витрати самого циклу та читання таймера і віднімається від підсумкового часу батчу `dt`, усуваючи апаратний зсув спостереження.

## Керування енергозбереженням CPU та холодними станами

Сучасні процесори використовують стани енергозбереження C-states (C1, C6). Якщо ядро перебувало в глибокому сні, його пробудження забирає від 10 до 50 мікросекунд. Якщо перші виміри батчу виконуються на сплячому ядрі, перший зразок вибірки отримує штучне сповільнення.

Фаза прогріву (Warmup) у нашому каркасі розв'язує цю проблему двома шляхами:
- Вона виводить процесорне ядро зі стану C-state у робочий стан C0 на максимальній частоті;
- Вона завантажує інструкції вимірюваного циклу в L1-кеш інструкцій (L1i) та прогріває таблиці передбачувача переходів (BTB).

Для вимірювання алгоритмів у «холодному» стані (наприклад, коли функція викликається рідко й завжди страждає від промаху L1-кешу), каркас можна розширити примусовим очищенням кеш-ліній перед кожним батчем за допомогою асемблерної інструкції `clflushopt`:
:::tabs
```c
static inline void flush_cache_range(const void *addr, size_t len) {
    const char *p = (const char *)addr;
    for (size_t i = 0; i < len; i += 64) {
        __builtin_ia32_clflushopt((const void *)(p + i));
    }
    asm volatile("sfence" : : : "memory");
}
```
```cpp
#include <span>
#include <cstdint>

namespace bench {

inline void flush_cache(std::span<const std::byte> memory_range) noexcept {
    const auto* ptr = reinterpret_cast<const char*>(memory_range.data());
    for (std::size_t i = 0; i < memory_range.size(); i += 64) {
        __builtin_ia32_clflushopt(reinterpret_cast<const void*>(ptr + i));
    }
    asm volatile("sfence" : : : "memory");
}

} // namespace bench
```
:::

## Діагностика аномалій та інтерпретація результатів

Під час аналізу отриманих значень інженер повинен оцінювати взаємозв'язок метрик:

- **Співвідношення `Min` та `Median`:** Якщо мінімальне значення істотно відрізняється від медіани (більш ніж на 10–15%), це свідчить про недостатній прогрів кешу або нестабільність тактової частоти ядра (CPU throttling).
- **Величина `IQR`:** Інтерквартильний розмах повинен становити не більше 2–5% від значення медіани. Високий `IQR` свідчить про те, що потік не було ізольовано від інших процесів ОС, або що в системі виникають регулярні конкурентні звернення до спільного L3-кешу чи контролера оперативної пам'яті.
- **Хвіст `p99` проти `p95`:** Сплеск на 99-му перцентилі вказує на поодинокі апаратні переривання операційної системи, які неминуче трапляються раз на кілька мілісекунд і мають відфільтровуватися ранговим аналізом.
