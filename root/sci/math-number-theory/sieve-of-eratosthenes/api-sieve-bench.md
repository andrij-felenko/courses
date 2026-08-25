# 📋 Інтерфейс та інструментарій бенчмаркінгу решета

Цей довідник описує специфікацію програмного інтерфейсу (C/C++ API), конфігураційні параметри, консольний інструментарій (CLI), коди помилок, правила безпечного управління пам'яттю у багаторазових та багатопотокових середовищах, а також метрики бенчмаркінгу для високопродуктивної бібліотеки просіювання простих чисел `libsieve`.

## 1. Специфікація програмного інтерфейсу (C / C++ API)

Бібліотека надає C-сумісний ABI (Application Binary Interface) для безпечної та бінарно сумісної інтеграції з іншими мовами програмування (Python, Rust, Go, Java, C#) та сучасну C++17 обгортку з дотриманням принципів RAII (Resource Acquisition Is Initialization) та гарантією відсутності накладних витрат під час викликів.

:::tabs
```c
/* sieve_api.h — C Interface specification for libsieve */
#ifndef SIEVE_API_H
#define SIEVE_API_H

#include <stdint.h>
#include <size_t.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    SIEVE_SUCCESS             =  0,
    SIEVE_ERR_INVALID_RANGE   = -1,
    SIEVE_ERR_OUT_OF_MEMORY   = -2,
    SIEVE_ERR_OVERFLOW        = -3,
    SIEVE_ERR_THREAD_FAILURE  = -4
} sieve_status_t;

/* Варіанти оптимізації колесом факторів */
typedef enum {
    SIEVE_WHEEL_NONE = 0, /* Без колеса (просіювання всіх чисел) */
    SIEVE_WHEEL_2    = 1, /* Просіювання непарних чисел (mod 2) */
    SIEVE_WHEEL_30   = 2, /* Колесо Modulo 30 (8 кандидатів із 30) */
    SIEVE_WHEEL_210  = 3  /* Колесо Modulo 210 (48 кандидатів із 210) */
} sieve_wheel_t;

/* Структура конфігурації просіювання */
typedef struct {
    uint64_t start_n;        /* Початкова межа інтервалу L */
    uint64_t end_n;          /* Кінцева межа інтервалу R */
    uint32_t segment_size;   /* Розмір сегмента у байтах (0 = авто під L1) */
    uint32_t thread_count;   /* Кількість потоків (0 = усі доступні ядра) */
    sieve_wheel_t wheel;     /* Тип колеса факторів */
    bool      count_only;    /* Зберігати лише кількість, не зберігати прості */
} sieve_config_t;

/* Результат обчислень */
typedef struct {
    uint64_t total_primes;   /* Кількість знайдених простих чисел π(R) - π(L-1) */
    uint64_t execution_us;   /* Час виконання у мікросекундах */
    uint64_t bytes_allocated;/* Загальний обсяг спожитої оперативної пам'яті */
    uint64_t* primes_array;  /* Масив знайдених чисел (NULL якщо count_only = true) */
    size_t   array_capacity; /* Ємність виділеного масиву */
} sieve_result_t;

/* Ініціалізація замовчувань для конфігурації */
sieve_config_t sieve_default_config(void);

/* Виконання просіювання згідно з конфігурацією */
sieve_status_t sieve_execute(const sieve_config_t* config, sieve_result_t* result);

/* Звільнення ресурсів результату */
void sieve_free_result(sieve_result_t* result);

/* Отримання текстового опису коду помилки */
const char* sieve_error_string(sieve_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* SIEVE_API_H */
```
```cpp
// sieve.hpp — C++17 Header-only Interface
#ifndef SIEVE_HPP
#define SIEVE_HPP

#include <cstdint>
#include <vector>
#include <string_view>
#include <system_error>
#include <optional>

namespace sieve {

enum class WheelType : std::uint8_t {
    None    = 0,
    Mod2    = 1,
    Mod30   = 2,
    Mod210  = 3
};

struct Configuration {
    std::uint64_t startRange{2};
    std::uint64_t endRange{100'000'000};
    std::uint32_t segmentSizeBytes{0}; // 0 = Auto-detect L1 Cache
    std::uint32_t threads{0};          // 0 = Hardware concurrency
    WheelType     wheel{WheelType::Mod30};
    bool          countOnly{true};
};

struct ExecutionReport {
    std::uint64_t totalPrimes{0};
    double        executionTimeMs{0.0};
    std::size_t   peakMemoryBytes{0};
    std::vector<std::uint64_t> primes;
};

class SieveEngine {
public:
    explicit SieveEngine(Configuration config = {}) : config_(config) {}

    [[nodiscard]] ExecutionReport run() const;

    void setConfig(Configuration config) { config_ = config; }
    [[nodiscard]] const Configuration& config() const noexcept { return config_; }

private:
    Configuration config_;
};

} // namespace sieve

#endif // SIEVE_HPP
```
:::

## 2. Детальний розбір типів даних та конфігураційних параметрів

### 2.1. Конфігураційна структура `sieve_config_t`

Параметри structures `sieve_config_t` контролюють усі аспекти обчислювального конвеєра:

1. `start_n` (uint64_t): Початкове значення шуканого інтервалу `L`. Мінімальне допустиме значення дорівнює `2`. Використання значень `0` або `1` перетворюється внутрішньо у `2`, оскільки числа 0 та 1 не є простими за визначенням.
2. `end_n` (uint64_t): Кінцева межа інтервалу `R`. Повинна задовольняти строгу умову `end_n >= start_n`. Максимальне значення обмежене межею 64-бітних цілих чисел без знака (`18.44 · 10¹⁸`), причому `√end_n` не повинно викликати переповнення при обчисленні `p * p`.
3. `segment_size` (uint32_t): Розмір внутрішнього буфера сегмента у байтах. Якщо передано значення `0`, бібліотека опитує операційну систему через виклики `sysconf(_SC_LEVEL1_DCACHE_SIZE)` в POSIX/Linux або `GetLogicalProcessorInformation` у Windows й обирає оптимальний розмір L1-кешу поточного процесора (зазвичай 32 KB або 64 KB). Якщо передано ненульове значення, воно автоматично вирівнюється до найближчого кратного 64 байтам (розміру кеш-лінії).
4. `thread_count` (uint32_t): Кількість паралельних робочих потоків. Якщо вказано `0`, обчислювальний рушій автоматично зчитує кількість фізичних/логічних ядер центрального процесора `std::thread::hardware_concurrency()`. При значеннях `thread_count > 1` бібліотека активує паралельне розбиття інтервалу між потоками без взаємних блокувань.
5. `wheel` (sieve_wheel_t): Вибір типу алгоритмічного колеса факторів. `SIEVE_WHEEL_NONE` просіює всі цілі числа поспіль; `SIEVE_WHEEL_2` пропускає парні числа (зберігає 50% елементів); `SIEVE_WHEEL_30` виконує колесо за модулем 30 (зберігає 8 кандидатів із 30, тобто 26.6% елементів); `SIEVE_WHEEL_210` виконує колесо за модулем 210 (зберігає 48 кандидатів із 210, тобто 22.8% елементів).
6. `count_only` (bool): Оптимізаційний прапорець режиму роботи. Якщо встановлено `true`, алгоритм підраховує лише загальну кількість простих чисел `π(R) - π(L-1)` і не виділяє пам'ять під збереження списку знайдених чисел, що зменшує споживання RAM до кількох кілобайт. Якщо встановлено `false`, прості числа динамічно записуються у масив `primes_array`, який розміщується у динамічній пам'яті.

### 2.2. Результативна структура `sieve_result_t` та правила її утилізації

Структура `sieve_result_t` повертає повну статистику виконання обчислювального ядра:

* `total_primes` (uint64_t): Точна кількість простих чисел, знайдених у заданому інтервалі.
* `execution_us` (uint64_t): Час виконання обчислювального ядра у мікросекундах (вимірюється високоточним таймером `std::chrono::high_resolution_clock`).
* `bytes_allocated` (uint64_t): Сумарний піковий обсяг пам'яті у байтах, виділений під час виконання програми.
* `primes_array` (uint64_t*): Вказівник на виділений у купі масив простих чисел. Якщо `count_only == true`, значення дорівнює `NULL`. 

**Правило безпеки пам'яті:** Для запобігання витокам пам'яті (Memory Leaks) користувач зобов'язаний передати вказівник на результативну структуру у функцію `sieve_free_result()`. Повторний виклик `sieve_free_result()` для вже звільненого об'єкта є безпечним (функція перевіряє `primes_array != NULL` і обнуляє вказівник після звільнення).

## 3. Багатопотокова безпека, NUMA-архітектура та прив'язка до ядер (Thread Affinity)

Бібліотека `libsieve` гарантує повну побічну безпеку (Thread-Safety) при викликах з різних потоків користувача, оскільки обчислювальний рушій не використовує глобального mutable-стану або статичних змінних.

### 3.1. Прив'язка потоків до ядер CPU (Thread Affinity)

На багатопроцесорних системах із NUMA-архітектурою (Non-Uniform Memory Access, наприклад, AMD EPYC або багатосокетні Intel Xeon) довільна міграція потоків між NUMA-вузлами спричиняє деградацію затримок кешу L3 та оперативної пам'яті. 

Для вирішення цієї проблеми утиліта `sieve-cli` надає можливість жорсткої прив'язки робочих потоків до фізичних ядер процесора через системні виклики `pthread_setaffinity_np` у Linux або `SetThreadAffinityMask` у Windows. Це гарантує, що локальний буфер сегмента розміром 32 KB надійно зберігається у L1-кеші конкретного обчислювального ядра протягом усього часу обробки даного відрізка діапазону.

## 4. Консольний інструментарій (CLI Interface)

Утиліта командного рядка `sieve-cli` надає гнучкі можливості управління процесом просіювання та бенчмаркінгу з термінала.

### 4.1. Синтаксис виклику

```bash
sieve-cli [ПАРАМЕТРИ] --limit <N>
sieve-cli [ПАРАМЕТРИ] --range <L>:<R>
```

### 4.2. Таблиця прапорців та опису параметрів

| Прапорець | Короткий | Опис параметра | Замовчування |
| :--- | :--- | :--- | :--- |
| `--limit <N>` | `-n` | Верхня межа просіювання (пошук в [2, N]) | 100 000 000 |
| `--range <L:R>` | `-r` | Точний інтервал просіювання [L, R] | 2:N |
| `--segment-size <KB>`| `-s` | Розмір сегмента у кілобайтах (напр. 32) | Auto (L1 Cache) |
| `--threads <T>` | `-t` | Кількість потоків обчислення | Кількість ядер CPU |
| `--wheel <TYPE>` | `-w` | Тип колеса факторів (`none`, `mod2`, `mod30`, `mod210`) | `mod30` |
| `--count-only` | `-c` | Режим підрахунку кількості (без виводу списку) | `true` |
| `--format <FMT>` | `-f` | Формат виводу (`text`, `json`, `csv`) | `text` |
| `--benchmark` | `-b` | Запуск тесту продуктивності | `false` |
| `--help` | `-h` | Вивід довідки та завершення | `false` |

### 4.3. Приклади використання CLI

1. **Підрахунок кількості простих чисел до N = 10⁹ на 8 паралельних потоках:**
   ```bash
   sieve-cli -n 1000000000 -t 8 --wheel mod30
   ```
2. **Пошук простих чисел у віддаленому інтервалі [10¹², 10¹² + 10⁷] з виводом у JSON:**
   ```bash
   sieve-cli -r 1000000000000:1000010000000 --format json
   ```
3. **Запуск аналітичного бенчмарку порівняння розмірів сегмента:**
   ```bash
   sieve-cli -n 1000000000 --benchmark --segment-size 16,32,64,128,256
   ```

## 5. Метрики та стандарти бенчмаркінгу

Для об'єктивної оцінки продуктивності алгоритму просіювання застосовуються чотири фундаментальні обчислювальні метрики:

1. **Пропускна здатність (Million Numbers / Sec або MNum/s):**
   Кількість просіяних елементів вихідного діапазону за одну секунду.
   ```
   Speed = (R - L + 1) / (t_execution_sec · 10⁶)   [Мільйонів чисел / сек]
   ```
2. **Ефективність використання кешу (L1d Cache Hit Rate):**
   Відсоток звернень до пам'яті, які були успішно виконані з L1-кешу без звернення до L2/L3 або DRAM. Оптимальне значення для правильно сегментованого решета становить **> 99.5%**. Вимірюється за допомогою системної утиліти `perf`:
   ```bash
   perf stat -e L1-dcache-load-misses,L1-dcache-loads ./sieve-cli -n 1000000000
   ```
3. **Обсяг споживаної оперативної пам'яті (Peak Memory Footprint):**
   Максимальний піковий обсяг RAM у байтах. Для сегментованого решета становить `O(√N + S · T)`, де `T` — кількість потоків.
4. **Масштабованість за потоками (Parallel Scaling Efficiency):**
   Відношення фактичного прискорення на `T` потоках до теоретичного лінійного прискорення `T`:
   ```
   Efficiency = Speed(T) / (T · Speed(1)) · 100%
   ```

## 6. Інтеграція з іншими мовами програмування

Завдяки чистому C-сумісному ABI бібліотека `libsieve` легко імпортується у вищорівневі мови програмування без накладних витрат на середовище виконання.

### 6.1. Інтеграція з Python через `ctypes`

У Python виклик C-бібліотеки виконується через модуль `ctypes`:

```python
import ctypes

class SieveConfig(ctypes.Structure):
    _fields_ = [
        ("start_n", ctypes.c_uint64),
        ("end_n", ctypes.c_uint64),
        ("segment_size", ctypes.c_uint32),
        ("thread_count", ctypes.c_uint32),
        ("wheel", ctypes.c_int),
        ("count_only", ctypes.c_bool),
    ]

class SieveResult(ctypes.Structure):
    _fields_ = [
        ("total_primes", ctypes.c_uint64),
        ("execution_us", ctypes.c_uint64),
        ("bytes_allocated", ctypes.c_uint64),
        ("primes_array", ctypes.POINTER(ctypes.c_uint64)),
        ("array_capacity", ctypes.c_size_t),
    ]

# Завантаження спільної бібліотеки libsieve.so
libsieve = ctypes.CDLL("./libsieve.so")
libsieve.sieve_execute.argtypes = [ctypes.POINTER(SieveConfig), ctypes.POINTER(SieveResult)]
libsieve.sieve_free_result.argtypes = [ctypes.POINTER(SieveResult)]
```

### 6.2. Інтеграція з Rust через FFI

У мові Rust виклик виконується у блоці `extern "C"` з оголошенням FFI-структур:

```rust
#[repr(C)]
pub struct SieveConfig {
    pub start_n: u64,
    pub end_n: u64,
    pub segment_size: u32,
    pub thread_count: u32,
    pub wheel: i32,
    pub count_only: bool,
}

extern "C" {
    pub fn sieve_execute(config: *const SieveConfig, result: *mut SieveResult) -> i32;
    pub fn sieve_free_result(result: *mut SieveResult);
}
```

## 7. Коди помилок та обробка виняткових ситуацій

При виклику програмного інтерфейсу можливі наступні виняткові ситуації:

* `SIEVE_SUCCESS` (0): Операція успішно завершена.
* `SIEVE_ERR_INVALID_RANGE` (-1): Початкова межа `L` більша за кінцеву `R`, або `R = 0`, або `L < 2`.
* `SIEVE_ERR_OUT_OF_MEMORY` (-2): Системна помилка виділення пам'яті. Неможливо виділити масив для базових простих чисел або буфер сегмента у купі (`malloc` повернув `NULL`).
* `SIEVE_ERR_OVERFLOW` (-3): Кінцева межа `R` викликає 64-бітне переповнення цілого числа при обчисленні `p * p`.
* `SIEVE_ERR_THREAD_FAILURE` (-4): Помилка створення або синхронізації потоків POSIX Threads (pthreads) або C++ `std::thread`.
