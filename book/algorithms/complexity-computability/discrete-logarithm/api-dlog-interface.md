# 📋 Специфікація інтерфейсу та командного рядка модулів розв'язання DLP

Вставка містить повну технічну специфікацію програмного інтерфейсу (API) та інструментарію командного рядка (CLI) для бібліотеки `libdlog`. Модуль призначений для розв'язання проблеми дискретного логарифма у скінченних полях та скінченних циклічних групах. У документі детально висвітлено синтаксис та сигнатури C/C++ типів даних, коди статусів помилок, структури керування контекстом, режими потокобезпеки, алгоритми автоналаштування параметрів та сценарії командного рядка для інтеграції у високопродуктивні обчисливальні системи.

## 1. Архітектурні принципи та дизайн `libdlog`

Бібліотека `libdlog` розроблена як системний модуль низького рівня із нульовою зовнішньою залежністю (за винятком стандартної бібліотеки C/C++). Головна мета дизайну API — забезпечення максимальної обчислювальної швидкодії при повному контролі над виділенням оперативної пам'яті та безвідмовній роботі в багатопотокових середовищах.

Програмний інтерфейс розділено на чотири функціональні рівні:

1. **Рівень керування контекстом (Context Management Layer):** Відповідає за виділення буферів пам'яті, збереження псевдовипадкових станів, налаштування таймаутів та встановлення лімітів ресурсів.
2. **Рівень алгоритмічних рушіїв (Solver Engine Layer):** Містить прямі виклики конкретних методів обчислення дискретного логарифма — Shanks Baby-Step Giant-Step (BSGS), Pollard's Rho та Pohlig-Hellman.
3. **Рівень високорівневої автоадаптації (Auto-Tuning Layer):** Проводить автоматичний математичний аналіз вхідних параметрів групи `(g, y, p, N)` та підбирає оптимальний алгоритм і розмір таблиць.
4. **Рівень діагностики та телеметрії (Diagnostics & Telemetry Layer):** Збирає статистику виконання (ітерації, час в мікросекундах, споживання RAM, колізійні сплески).

### Режими потокобезпеки (Thread Safety Guarantees)
- **Рівень контексту:** Кожен екземпляр об'єкта контексту `dlog_context_t` не є внутрішньо синхронізованим. Якщо декілька паралельних потоків звертаються до одного контексту, зовнішній викликач повинен забезпечити взаємне виключення (mutex).
- **Потокобезпечні обчислення (Reentrant API):** Функції обчислення логарифма `dlog_solve_uint64` є строго чистими і повторно входжуваними (reentrant), якщо кожному потоку передається власний екземпляр контексту або виклик здійснюється у безконтекстному режимі з передачею `ctx = NULL`.

## 2. Повний довідник кодів статусів та помилок (`dlog_status_t`)

Усі функції системного API повертають 32-бітний перелічувальний код статусу `dlog_status_t`. Значення `0` (`DLOG_SUCCESS`) строго сигналізує про успішне завершення операції та наявність вірного результату.

:::tabs
```c
typedef enum {
    DLOG_SUCCESS             = 0,   // Логарифм успішно знайдено
    DLOG_NOT_FOUND           = 1,   // Логарифм не існує у вказаній групі або діапазоні
    DLOG_INVALID_PARAM       = 2,   // Некоректні вхідні аргументи (p <= 2, g = 0, y >= p)
    DLOG_OUT_OF_MEMORY       = 3,   // Недостатньо пам'яті для виділення хеш-таблиці BSGS
    DLOG_TIMEOUT             = 4,   // Перевищено встановлений ліміт часу виконання
    DLOG_MAX_STEPS_EXCEEDED  = 5,   // Перевищено максимальну кількість кроків алгоритму
    DLOG_COLLISION_FAILED    = 6,   // Непридатна колізія в Pollard Rho (НСД(Δb, N) > 1)
    DLOG_COMPUTE_ERROR       = 7,   // Арифметичне переповнення або ділення на нуль
    DLOG_NOT_IMPLEMENTED     = 99   // Метод не підтримується для даної конфігурації
} dlog_status_t;
```
```cpp
enum class Status : std::int32_t {
    Success            = 0,   // Логарифм успішно знайдено
    NotFound           = 1,   // Логарифм не існує у вказаній групі або діапазоні
    InvalidParam       = 2,   // Некоректні вхідні аргументи
    OutOfMemory        = 3,   // Недостатньо пам'яті для виділення хеш-таблиці BSGS
    Timeout            = 4,   // Перевищено встановлений ліміт часу виконання
    MaxStepsExceeded   = 5,   // Перевищено максимальну кількість кроків алгоритму
    CollisionFailed    = 6,   // Непридатна колізія в Pollard Rho (НСД > 1)
    ComputeError       = 7,   // Арифметичне переповнення або ділення на нуль
    NotImplemented     = 99   // Метод не підтримується для даної конфігурації
};
```
:::

### Детальна інтерпретація та діагностика помилок

#### `DLOG_SUCCESS` (0)
Обчислення завершено успішно. Результат `exponent` у структурі `dlog_result_t` містить шукане число `x`, таке що `gˣ ≡ y (mod p)`.

#### `DLOG_NOT_FOUND` (1)
Алгоритм повністю вичерпав діапазон пошуку (наприклад, пройшов усі `m = ⌈√N⌉` кроків у BSGS), але не знайшов колізії. Це виникає, якщо елемент `y` не належить до підгрупи, згенерованої `g`, або якщо порядок групи `N` вказано некоректно.

#### `DLOG_INVALID_PARAM` (2)
Аргументи виклику порушують математичні обмеження:
- Модуль `p` є парним або меншим за 3.
- Генератор `g` дорівнює 0, 1 або є більшим/рівним `p`.
- Цільове значення `y` дорівнює 0 або перевищує `p - 1`.
- Указник на вихідний результат `result` дорівнює `NULL`.

#### `DLOG_OUT_OF_MEMORY` (3)
Запитаний обсяг пам'яті для таблиці baby-steps перевищує максимально дозволений ліміт `max_memory_bytes` у конфігурації, або операційна система відмовила у виділенні буфера через `malloc`. Модуль гарантує відсутність витоку пам'яті: усі частково виділені буфери негайно очищуються перед поверненням помилки.

#### `DLOG_MAX_STEPS_EXCEEDED` (5)
Імовірнісний алгоритм (Pollard's Rho) виконав задану кількість ітерацій `max_steps`, але не знайшов колізію траєкторій. Рекомендація: змінити `random_seed` у конфігурації та повторити виклик.

#### `DLOG_COLLISION_FAILED` (6)
В алгоритмі Pollard's Rho знайдено колізію елементів `g^{a₁} · y^{b₁} = g^{a₂} · y^{b₂}`, але різниця коефіцієнтів `Δb = (b₁ - b₂) mod N` має спільний дільник із порядком `N` (`НСД(Δb, N) > 1`). У результаті обернений елемент `Δb⁻¹ mod N` не існує. Модуль автоматично очищає стан і вимагає перезапуску з іншими початковими станами.

## 3. Опис алгоритмічних режимів (`dlog_method_t`)

Модуль надає можливість вибору конкретного алгоритмічного рушія через перелічувальний тип `dlog_method_t`.

:::tabs
```c
typedef enum {
    DLOG_METHOD_AUTO           = 0, // Автоматичний вибір на основі математичного аналізу
    DLOG_METHOD_BSGS           = 1, // Shanks Baby-Step Giant-Step (детермінований)
    DLOG_METHOD_POLLARD_RHO    = 2, // Pollard's Rho (імовірнісний, O(1) пам'яті)
    DLOG_METHOD_POHLIG_HELLMAN = 3  // Pohlig-Hellman (декомпозиція гладких порядків)
} dlog_method_t;
```
```cpp
enum class Method : std::int32_t {
    Auto          = 0, // Автоматичний вибір на основі математичного аналізу
    BSGS          = 1, // Shanks Baby-Step Giant-Step (детермінований)
    PollardRho    = 2, // Pollard's Rho (імовірнісний, O(1) пам'яті)
    PohligHellman = 3  // Pohlig-Hellman (декомпозиція гладких порядків)
};
```
:::

Таблиця порівняльного аналізу алгоритмічних методів:

| Режим | Опис алгоритму | Часова складність | Пам'ять | Втрати при неуспіху |
| :--- | :--- | :--- | :--- | :--- |
| `DLOG_METHOD_AUTO` | Автоматичний вибір кращого алгоритму за аналізом порядку групи | Залежить від `N` | Автоналаштована | Мінімальні |
| `DLOG_METHOD_BSGS` | Алгоритм Shanks Baby-Step Giant-Step (детермінований) | `O(√N)` | `O(√N)` | Високе споживання RAM |
| `DLOG_METHOD_POLLARD_RHO` | `ρ`-алгоритм Полларда (імовірнісний) | `O(√N)` | `O(1)` | Ризик зациклення |
| `DLOG_METHOD_POHLIG_HELLMAN` | Алгоритм Поліґа — Геллмана з декомпозицією гладкого порядку | `O(∑ eᵢ √pᵢ)` | `O(max √pᵢ)` | Вимагає факторний розклад |

### Стратегія роботи режиму `DLOG_METHOD_AUTO`
При виборі `DLOG_METHOD_AUTO` бібліотека проводить первинний аналіз аргументів:
1. Перевіряється значення `N`. Якщо `N < 10⁶`, обирається класичний BSGS завдяки мінімальній константі часу.
2. Якщо `N >= 10⁶`, перевіряється доступний ліміт оперативної пам'яті `max_memory_bytes`. Якщо `⌈√N⌉ · 16` байтів вміщується у RAM, запускається BSGS з хеш-таблицею.
3. Якщо пам'яті недостатньо, бібліотека автоматично перемикається на `DLOG_METHOD_POLLARD_RHO` із захистом від зациклення.
4. Якщо порядок групи `N` попередньо розкладено на множники, рекомендується явно вказувати `DLOG_METHOD_POHLIG_HELLMAN`.

## 4. Специфікація структур даних (C та C++ API)

### 4.1. Структура конфігурації `dlog_config_t` / `Config`

Структура містить усі керуючі параметри для сеансу обчислень.

:::tabs
```c
typedef struct {
    dlog_method_t method;       // Обраний алгоритм розв'язання
    uint64_t max_memory_bytes;  // Максимальний обсяг RAM для BSGS (в байтах)
    uint64_t max_steps;         // Максимальна кількість кроків алгоритму
    uint32_t num_threads;       // Кількість паралельних потоків (0 = авто)
    uint32_t random_seed;       // Зерно для імовірнісного генератора (Pollard Rho)
    bool verbose_logging;       // Прапор виводу діагностичних логів у stdout
} dlog_config_t;
```
```cpp
struct Config {
    Method method = Method::Auto;
    std::uint64_t max_memory_bytes = 536870912ULL; // 512 MiB
    std::uint64_t max_steps = 10000000000ULL;
    std::uint32_t num_threads = 0;
    std::uint32_t random_seed = 0;
    bool verbose_logging = false;
};
```
:::

#### Поля структури конфігурації
- `method`: Алгоритм з переліку `dlog_method_t`. За замовчуванням `DLOG_METHOD_AUTO`.
- `max_memory_bytes`: Граничний обсяг динамічної пам'яті в байтах, який дозволено виділяти під хеш-таблиці. Значення за замовчуванням: `536870912` (512 МіБ).
- `max_steps`: Гранична кількість ітерацій циклу. Якщо ліміт досягнуто без результату, повертається `DLOG_MAX_STEPS_EXCEEDED`. Значення за замовчуванням: `10000000000ULL`.
- `num_threads`: Кількість потоків для паралельних обчислень. При `0` використовується `omp_get_max_threads()` або число апаратних ядер CPU.
- `random_seed`: Початкове значення для генерації початкових станів у Pollard's Rho. Значення `0` викликає ініціалізацію від системного таймера `time(NULL)`.
- `verbose_logging`: Якщо `true`, модуль виводить прогрес виконання кожні `10⁶` ітерацій у `stdout`.

### 4.2. Структура результату `dlog_result_t` / `Result`

Структура приймає підсумкові дані та телеметрію обчислювального процесу.

:::tabs
```c
typedef struct {
    uint64_t exponent;          // Знайдений дискретний логарифм x
    dlog_status_t status;       // Підсумковий статус виконання
    uint64_t steps_executed;    // Фактично виконано кроків/ітерацій
    double time_elapsed_ms;     // Витрачений час у мілісекундах
    uint64_t memory_used_bytes; // Фактичний обсяг використаної пам'яті
} dlog_result_t;
```
```cpp
struct Result {
    std::uint64_t exponent = 0;
    Status status = Status::NotFound;
    std::uint64_t steps_executed = 0;
    double time_elapsed_ms = 0.0;
    std::uint64_t memory_used_bytes = 0;
};
```
:::

#### Поля структури результату
- `exponent`: Значення дискретного логарифма `x`. Є дійсним лише за умови `status == DLOG_SUCCESS`.
- `status`: Підсумковий код повернення із переліку `dlog_status_t`.
- `steps_executed`: Сумарна кількість групових множень, виконаних під час обчислення.
- `time_elapsed_ms`: Астрономічний час виконання обчислення в мілісекундах із точністю до мікросекунд.
- `memory_used_bytes`: Пікове споживання оперативної пам'яті під час виконання (у байтах).

## 5. Сигнатури функцій API

### 5.1. Керування конфігурацією та контекстом

:::tabs
```c
/**
 * @brief Ініціалізує структуру конфігурації значеннями за замовчуванням.
 */
dlog_status_t dlog_config_init_default(dlog_config_t *config);

/**
 * @brief Створює непрозорий контекст розв'язувача.
 */
dlog_status_t dlog_context_create(const dlog_config_t *config, void **out_ctx);

/**
 * @brief Звільняє всі ресурси контексту.
 */
void dlog_context_destroy(void *ctx);
```
```cpp
namespace dlog::api {
    class Context {
    public:
        explicit Context(const Config& config = {});
        ~Context();
        Context(const Context&) = delete;
        Context& operator=(const Context&) = delete;
        Context(Context&&) noexcept;
        Context& operator=(Context&&) noexcept;

        [[nodiscard]] void* get_native_handle() const noexcept;
    private:
        void* handle_ = nullptr;
    };
}
```
:::

### 5.2. Виконання обчислення логарифма

:::tabs
```c
/**
 * @brief Обчислює дискретний логарифм x для рівняння g^x ≡ y (mod p).
 */
dlog_status_t dlog_solve_uint64(
    void *ctx,
    uint64_t g,
    uint64_t y,
    uint64_t p,
    uint64_t group_order,
    dlog_result_t *result
);
```
```cpp
namespace dlog::api {
    [[nodiscard]] Result solve(
        Context& ctx,
        std::uint64_t g,
        std::uint64_t y,
        std::uint64_t p,
        std::uint64_t group_order
    );
}
```
:::

## 6. Обгортка C++ (Object-Oriented API Engine)

Для розробників на C++ надається потокобезпечна Header-only обгортка у просторі імен `dlog::api`. Вона забезпечує суворе дотримання концепції RAII, обробку помилок через об'єкти `std::optional` або винятки `dlog::Exception`, а також підтримку типів `std::chrono`.

```cpp
#pragma once
#include <cstdint>
#include <optional>
#include <chrono>
#include <string>
#include <stdexcept>

namespace dlog::api {

// Виняток для помилок конфігурації або арифметики
class Exception : public std::runtime_error {
public:
    explicit Exception(const std::string& msg, dlog_status_t status)
        : std::runtime_error(msg), status_(status) {}

    [[nodiscard]] dlog_status_t status() const noexcept { return status_; }
private:
    dlog_status_t status_;
};

struct SolverOptions {
    Method method = Method::Auto;
    std::size_t max_memory_bytes = 1024 * 1024 * 512; // 512 MiB
    std::uint64_t max_steps = 10000000000ULL;
    std::uint32_t num_threads = 0;
    bool verbose = false;
};

struct ExecutionReport {
    std::uint64_t exponent = 0;
    bool success = false;
    std::uint64_t steps = 0;
    std::chrono::duration<double, std::milli> execution_time{0};
    std::size_t memory_bytes = 0;
    std::string error_message;
};

class DiscreteLogEngine {
public:
    explicit DiscreteLogEngine(SolverOptions options = {}) 
        : opts_(std::move(options)) {}

    [[nodiscard]] ExecutionReport solve(
        std::uint64_t g, 
        std::uint64_t y, 
        std::uint64_t p, 
        std::uint64_t group_order
    ) const {
        dlog_config_t cfg;
        dlog_config_init_default(&cfg);
        cfg.method = static_cast<dlog_method_t>(opts_.method);
        cfg.max_memory_bytes = opts_.max_memory_bytes;
        cfg.max_steps = opts_.max_steps;
        cfg.num_threads = opts_.num_threads;
        cfg.verbose_logging = opts_.verbose;

        void* ctx = nullptr;
        if (dlog_context_create(&cfg, &ctx) != DLOG_SUCCESS) {
            throw Exception("Failed to create dlog context", DLOG_OUT_OF_MEMORY);
        }

        dlog_result_t res;
        dlog_status_t st = dlog_solve_uint64(ctx, g, y, p, group_order, &res);
        dlog_context_destroy(ctx);

        ExecutionReport report;
        report.success = (st == DLOG_SUCCESS);
        report.exponent = res.exponent;
        report.steps = res.steps_executed;
        report.execution_time = std::chrono::duration<double, std::milli>(res.time_elapsed_ms);
        report.memory_bytes = res.memory_used_bytes;
        
        if (!report.success) {
            report.error_message = "Status code: " + std::to_string(static_cast<int>(st));
        }

        return report;
    }

    void update_options(const SolverOptions& opts) { opts_ = opts; }
    [[nodiscard]] const SolverOptions& options() const noexcept { return opts_; }

private:
    SolverOptions opts_;
};

} // namespace dlog::api
```

## 7. Специфікація інструментарію командного рядка (CLI Tool)

Консольна утиліта `dlog-solver` надає автономний доступ до обчисливального рушія бібліотеки. Вона призначена для використання в автоматизованих криптоаналітичних скриптах, пайплайнах тестування та системах бічмаркінгу.

### 7.1. Синтаксис виклику

```bash
dlog-solver --modulus <p> --generator <g> --target <y> [ОПЦІЇ]
```

### 7.2. Таблиця аргументів командного рядка

| Прапор CLI | Короткий варіант | Опис аргументу | Значення за замовчуванням |
| :--- | :--- | :--- | :--- |
| `--modulus` | `-p` | Модуль поля `p` (64-бітне ціле число) | **Обов'язковий** |
| `--generator` | `-g` | Основа/генератор групи `g` | **Обов'язковий** |
| `--target` | `-y` | Цільове значення `y = g^x mod p` | **Обов'язковий** |
| `--order` | `-N` | Порядок групи `N` | `p - 1` |
| `--method` | `-m` | Алгоритм: `auto`, `bsgs`, `rho`, `pohlig` | `auto` |
| `--max-mem` | `-M` | Ліміт оперативної пам'яті у мегабайтах | `512` |
| `--json` | `-j` | Вивід результату у форматі JSON | `false` |
| `--verbose` | `-v` | Увімкнути детальний лог ітерацій | `false` |
| `--help` | `-h` | Вивести довідку та завершити роботу | - |

### 7.3. Сценарії використання та приклади виводу

#### Сценарій 1: Інтерактивний виклик з текстовим виводом
Команда розв'язує дискретний логарифм у полі `𝔽₁₀₀₀₇*` для `g = 5`, `y = 4873`:

```bash
dlog-solver -p 10007 -g 5 -y 4873 --method bsgs -v
```

*Стандартний вивід у консоль (stdout):*
```text
[INFO] Initializing libdlog engine v2.4.0
[INFO] Modulus p = 10007, Generator g = 5, Target y = 4873, Order N = 10006
[INFO] Executing Shanks BSGS algorithm...
[INFO] Step 1: Computed 101 baby-step entries in hash table (Memory: 3.2 KB)
[INFO] Step 2: Executing giant-step lookup... Match found at i = 13, j = 79
[SUCCESS] Discrete logarithm found: x = 1234
[METRICS] Total steps: 180, Time elapsed: 0.38 ms, Peak Memory: 3276 bytes
```

#### Сценарій 2: Інтеграція в автоматизований скрипт у форматі JSON
Для парсингу результатів сторонніми мовами (Python, Go, Bash/jq) використовується прапор `--json`:

```bash
dlog-solver -p 10007 -g 5 -y 4873 -j
```

*Структура JSON-відповіді (stdout):*
```json
{
  "version": "2.4.0",
  "status": "DLOG_SUCCESS",
  "status_code": 0,
  "input": {
    "modulus": 10007,
    "generator": 5,
    "target": 4873,
    "group_order": 10006
  },
  "result": {
    "exponent": 1234,
    "verification": true
  },
  "metrics": {
    "method_used": "BSGS",
    "steps_executed": 180,
    "time_elapsed_ms": 0.38,
    "peak_memory_bytes": 3276
  }
}
```

### 7.4. Коди повернення процесу у системному середовищі (CLI Exit Codes)

Утиліта `dlog-solver` повертає стандартні коди завершення процесу (Exit Codes) для операційної системи:

- `0` (`EXIT_SUCCESS`): Логарифм успішно знайдено.
- `1` (`EXIT_FAILURE`): Математична помилка або логарифм не існує.
- `2` (`EXIT_INVALID_USAGE`): Сипомилка синтаксису аргументів командного рядка.
- `137` (`EXIT_OOM`): Процес зупинено через перевищення ліміту пам'яті.
