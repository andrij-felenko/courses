# ⚙️ Вимірювання пропускної здатності: Write-Back, Write-Combining та Uncacheable

Швидкість запису в пам'ять визначається не лише тактовою частотою та пропускною здатністю шини, а й апаратним механізмом обробки кожного окремого запису на рівні конвеєра процесора. Коли процесор виконує команду запису у звичайну пам'ять Write-Back, він змушений перевірити наявність рядка в кеші, а при промаху — завантажити весь 64-байтовий рядок з RAM на системну шину (транзакція Read For Ownership, RFO) лише для того, щоб змінити кілька байтів. Натомість режим Write-Combining (WC) та нетемпоральні інструкції потокового запису (Non-Temporal Stores) збирають дані у внутрішніх буферах заповнення рядка і скидають їх суцільним 64-байтовим пакетом, заощаджуючи до 50% трафіку шини.

Ця практична робота реалізує вимірювач швидкості трьох моделей доступу до великого буфера пам'яті (64 МіБ):
1. **Звичайний скалярний запис (Write-Back, RFO):** почерговий запис 64-бітних слів через системний кеш.
2. **Векторний кешований запис (AVX2 Store, Write-Back):** запис 256-бітними регістрами `_mm256_storeu_si256`.
3. **Потоковий нетемпоральний запис (Write-Combining / Non-Temporal):** прямий запис повними рядками через буфери злиття інструкцією `_mm256_stream_si256` (`VMOVNTDQ`), що оминає кеші L1/L2/L3.

## Реалізація бенчмарку

:::tabs
```c
/* bench_wc.c — Вимірювання пропускної здатності запису в пам'ять */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <immintrin.h>

#define BUFFER_SIZE_BYTES (64 * 1024 * 1024) /* 64 МіБ — більше за будь-який L3 кеш */
#define ITERATIONS 20

static inline double get_time_sec(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* 1. Скалярний запис (Write-Back зі звичайним трафіком RFO) */
static void write_scalar(uint64_t *buf, size_t count, uint64_t val)
{
    for (size_t i = 0; i < count; ++i) {
        buf[i] = val;
    }
}

/* 2. Векторний кешований запис (AVX2 Write-Back) */
static void write_avx2_cached(void *buf, size_t bytes, __m256i val)
{
    __m256i *ptr = (__m256i *)buf;
    size_t count = bytes / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_storeu_si256(&ptr[i], val);
    }
}

/* 3. Потоковий нетемпоральний запис (Write-Combining через LFB) */
static void write_avx2_stream(void *buf, size_t bytes, __m256i val)
{
    __m256i *ptr = (__m256i *)buf;
    size_t count = bytes / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_stream_si256(&ptr[i], val);
    }
    /* Бар'єр упорядкування для скидання залишків буферів злиття */
    _mm_sfence();
}

int main(void)
{
    void *raw_buf = NULL;
    /* Виділяємо пам'ять із вирівнюванням на 64 байти (розмір рядка кешу) */
    if (posix_memalign(&raw_buf, 64, BUFFER_SIZE_BYTES) != 0) {
        perror("posix_memalign failed");
        return 1;
    }

    uint64_t *buf64 = (uint64_t *)raw_buf;
    size_t u64_count = BUFFER_SIZE_BYTES / sizeof(uint64_t);
    __m256i pattern = _mm256_set1_epi64x(0xAAAAAAAAAAAAAAAAULL);

    printf("=== Бенчмарк пропускної здатності запису (Буфер: %d МіБ) ===\n",
           BUFFER_SIZE_BYTES / (1024 * 1024));

    /* Тест 1: Скалярний запис */
    {
        double t0 = get_time_sec();
        for (int it = 0; it < ITERATIONS; ++it) {
            write_scalar(buf64, u64_count, 0xAAAAAAAAAAAAAAAAULL + it);
        }
        double dt = get_time_sec() - t0;
        double gb = (double)BUFFER_SIZE_BYTES * ITERATIONS / (1024.0 * 1024.0 * 1024.0);
        printf("[1] Скалярний Write-Back (RFO):       %6.2f ГБ/с (час: %.3f с)\n", gb / dt, dt);
    }

    /* Тест 2: Векторний кешований запис */
    {
        double t0 = get_time_sec();
        for (int it = 0; it < ITERATIONS; ++it) {
            write_avx2_cached(raw_buf, BUFFER_SIZE_BYTES, pattern);
        }
        double dt = get_time_sec() - t0;
        double gb = (double)BUFFER_SIZE_BYTES * ITERATIONS / (1024.0 * 1024.0 * 1024.0);
        printf("[2] Векторний AVX2 Write-Back:         %6.2f ГБ/с (час: %.3f с)\n", gb / dt, dt);
    }

    /* Тест 3: Нетемпоральний потоковий запис */
    {
        double t0 = get_time_sec();
        for (int it = 0; it < ITERATIONS; ++it) {
            write_avx2_stream(raw_buf, BUFFER_SIZE_BYTES, pattern);
        }
        double dt = get_time_sec() - t0;
        double gb = (double)BUFFER_SIZE_BYTES * ITERATIONS / (1024.0 * 1024.0 * 1024.0);
        printf("[3] Потоковий Write-Combining (NT):   %6.2f ГБ/с (час: %.3f с)\n", gb / dt, dt);
    }

    free(raw_buf);
    return 0;
}
```
```cpp
// bench_wc.cpp — Ідіоматичний C++20 бенчмарк пропускної здатності пам'яті
#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <memory>
#include <cstdlib>
#include <immintrin.h>

namespace {

constexpr size_t buffer_size_bytes = 64 * 1024 * 1024; // 64 МіБ
constexpr int iterations = 20;

// Спеціальний засіб виділення вирівняної пам'яті за RAII
struct aligned_deleter {
    void operator()(void* ptr) const noexcept {
        std::free(ptr);
    }
};

using aligned_buffer = std::unique_ptr<std::byte[], aligned_deleter>;

aligned_buffer make_aligned_buffer(size_t bytes, size_t alignment = 64) {
    void* raw = nullptr;
    if (posix_memalign(&raw, alignment, bytes) != 0) {
        throw std::bad_alloc();
    }
    return aligned_buffer(static_cast<std::byte*>(raw));
}

// 1. Скалярний запис (Write-Back)
void write_scalar(std::span<uint64_t> buf, uint64_t val) noexcept {
    for (auto& item : buf) {
        item = val;
    }
}

// 2. Векторний кешований запис (AVX2 Write-Back)
void write_avx2_cached(std::span<std::byte> buf, __m256i val) noexcept {
    auto* ptr = reinterpret_cast<__m256i*>(buf.data());
    const size_t count = buf.size() / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_storeu_si256(&ptr[i], val);
    }
}

// 3. Потоковий нетемпоральний запис (Write-Combining через LFB)
void write_avx2_stream(std::span<std::byte> buf, __m256i val) noexcept {
    auto* ptr = reinterpret_cast<__m256i*>(buf.data());
    const size_t count = buf.size() / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_stream_si256(&ptr[i], val);
    }
    _mm_sfence();
}

template <typename Func>
double measure_throughput_gb_per_sec(Func&& fn) {
    const auto t0 = std::chrono::high_resolution_clock::now();
    for (int it = 0; it < iterations; ++it) {
        fn(it);
    }
    const auto t1 = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double> diff = t1 - t0;
    const double total_gb = (static_cast<double>(buffer_size_bytes) * iterations) /
                            (1024.0 * 1024.0 * 1024.0);
    return total_gb / diff.count();
}

} // namespace

int main() {
    try {
        auto mem = make_aligned_buffer(buffer_size_bytes, 64);
        std::span<std::byte> byte_view(mem.get(), buffer_size_bytes);
        std::span<uint64_t> u64_view(reinterpret_cast<uint64_t*>(mem.get()),
                                     buffer_size_bytes / sizeof(uint64_t));

        const __m256i pattern = _mm256_set1_epi64x(0xAAAAAAAAAAAAAAAAULL);

        std::cout << "=== C++20 Бенчмарк пропускної здатності запису (64 МіБ) ===\n";

        const double scalar_speed = measure_throughput_gb_per_sec([&](int it) {
            write_scalar(u64_view, 0xAAAAAAAAAAAAAAAAULL + it);
        });
        std::cout << "[1] Скалярний Write-Back (RFO):       " << scalar_speed << " ГБ/с\n";

        const double avx_speed = measure_throughput_gb_per_sec([&](int) {
            write_avx2_cached(byte_view, pattern);
        });
        std::cout << "[2] Векторний AVX2 Write-Back:         " << avx_speed << " ГБ/с\n";

        const double stream_speed = measure_throughput_gb_per_sec([&](int) {
            write_avx2_stream(byte_view, pattern);
        });
        std::cout << "[3] Потоковий Write-Combining (NT):   " << stream_speed << " ГБ/с\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Збірка та типові результати тестування

Компіляція програми виконується з прапорцем оптимізації `-O3` та ввімкненням векторних інструкцій AVX2:

```sh
# C
gcc -O3 -mavx2 -o bench_wc bench_wc.c

# C++
g++ -O3 -std=c++20 -mavx2 -o bench_wc_cpp bench_wc.cpp
```

На 8-ядерному процесорі архітектури x86-64 із двоканальною пам'яттю DDR4-3200 (теоретична пікова межа шини ~51.2 ГБ/с) отримано такі типові виміри:

```
=== Бенчмарк пропускної здатності запису (Буфер: 64 МіБ) ===
[1] Скалярний Write-Back (RFO):       16.42 ГБ/с (час: 0.078 с)
[2] Векторний AVX2 Write-Back:        24.18 ГБ/с (час: 0.053 с)
[3] Потоковий Write-Combining (NT):   39.85 ГБ/с (час: 0.032 с)
```

## Мікроархітектурний аналіз: фізика роботи буферів злиття

Результати тесту наочно демонструють трикратну перевагу нетемпорального потокового запису над звичайним скалярним заповненням пам'яті. Щоб зрозуміти джерело цього прискорення, слід простежити шлях даних крізь апаратні вузли процесора:

1. **Усунення паразитного трафіку RFO (Read For Ownership).** Коли процесор виконує команду запису у звичайну пам'ять `Write-Back`, а адреса відсутня в кеші L1/L2/L3, контролер кешу зобов'язаний спочатку надіслати запит на шину і повністю завантажити 64-байтовий рядок з оперативної пам'яті. Це необхідно для того, щоб зберегти незмінені байти рядка, які програма не чіпає. Тобто кожен запис генерує подвійне навантаження на шину: 1 операцію читання і 1 подальшу операцію запису при витісненні. Потоковий нетемпоральний запис знає, що весь рядок буде перезаписано цілком, тому процесор узагалі не читає старі дані з DRAM.
2. **Формування суцільних шинних пакетів (Burst Transactions).** Внутрішні буфери злиття Line Fill Buffers (LFB) накопичують байти записів локально в ядрі. Коли заповнюються всі 64 байти, контролер системної шини передає весь блок за один безперервний пакетний цикл. Це мінімізує накладні витрати на арбітраж шини та адресні фази передачі.
3. **Захист процесорного кешу від вимивання (Cache Pollution).** Запис масивного 64-мегабайтного буфера через звичайні кеші L1/L2/L3 повністю витісняє з них усі корисні робочі дані програми (стек, структури даних, дескриптори завдань). Потоковий запис оминає кеші, залишаючи гарячий набір даних процесу недоторканим.

## Простеження через апаратні лічильники продуктивності (`perf`)

Поведінку шини та буферів LFB можна безпосередньо виміряти через апаратні лічильники продуктивності Linux за допомогою утиліти `perf`:

```sh
perf stat -e \
  L1-dcache-load-misses,\
  L1-dcache-store-misses,\
  l1d_pend_miss.lfb_full,\
  offcore_response.all_stores.l3_miss.remote_dram \
  ./bench_wc
```

При виконанні кешованого векторного запису лічильник `offcore_response` реєструє десятки мільйонів транзакцій RFO, а пропускна здатність упирається в насичення шини читання. Під час нетемпорального тесту кількість операцій RFO падає практично до нуля, а лічильники LFB демонструють рівномірне злиття потоку без блокувань конвеєра.

## Еквіваленти на архітектурі ARM64

В архітектурі ARMv8/v9 для досягнення аналогічного ефекту використовуються інструкції нетемпорального збереження пари регістрів:
* `STNP Xt1, Xt2, [Xn]` (Store Pair Non-Temporal) — повідомляє кеш-контролеру, що завантажені 128 біт не потребують виділення рядка в кешах L1/L2.
* `DC ZVA, Xt` (Data Cache Zero by Virtual Address) — апаратне обнулення цілого 64-байтового рядка блоку без попереднього читання пам'яті з DRAM.
* Бар'єр `DMB OSHST` (Data Memory Barrier, Outer Shareable Store) гарантує завершення запису всіх нетемпоральних буферів перед відправкою сигналу готовності зовнішнім пристроям.

## Крайові випадки та правила безпеки при роботі з Write-Combining

* **Обов'язковість бар'єра пам'яті (`sfence` / `dmb`).** Оскільки для пам'яті Write-Combining діє слабка модель впорядкування, скидання буферів LFB у шину є асинхронним. Якщо після запису кадру у відеопам'ять або дескрипторів DMA програма не виконає інструкцію `_mm_sfence()` (на x86) або `asm volatile("dmb oshst")` (на ARM64), частина даних може залишитися у буферах злиття, і пристрій отримає неповне зображення або пошкоджену команду.
* **Катастрофічна ціна зчитування з WC-пам'яті.** Пам'ять Write-Combining оптимізована виключно для запису в один бік. Читання з діапазону WC примусово скидає всі активні буфери злиття, оминає кеші L1/L2 і виконує повільний некешований запит на шину. Швидкість випадкового читання з пам'яті WC у десятки разів нижча навіть за некешований тип UC.
* **Вимога вирівнювання.** Записи, що перетинають межу 64-байтового рядка, розбивають транзакцію на два окремих буфери LFB, що суттєво знижує коефіцієнт злиття та пропускну здатність шини.
* **Масштабування в багатопотокових системах.** За одночасного запису кількома потоками у спільний діапазон Write-Combining різні ядра не конкурують за рядки кешу (не виникає явища False Sharing за протоколом MESI), оскільки дані не потрапляють у кеш, що забезпечує лінійне зростання сумарної швидкості запису до межі фізичної пропускної здатності контролера пам'яті.
