# 📋 Інтерфейс бібліотеки реконструкції фазового простору

Інтерфейс довідника бібліотеки `libtakens` надає специфікацію публічного C та C++ API для налаштування параметрів реконструкції фазового простору, обчислення часових затримок, проведення алгоритму хибних найближчих сусідів та управління пам'яттю затримкових матриць. У цьому документі описано типи даних, конфігураційні структури, сигнатури функцій, коди помилок, вимоги до потокобезпечності, механізми обробки виключних ситуацій, обгортки для Python ctypes та Rust FFI, розрахунок динамічних інваріантів, інфраструктуру збирання CMake, телеметрію та простеження, тестування в CI/CD та виклики бібліотечних методологій для системного програмування.

---

### 1. Архітектура та принципи проєктування API

Бібліотека `libtakens` розроблена як низькорівневий обчислювальний рушій для нелінійного аналізу часових рядів та реконструкції фазових атракторів. При проєктуванні її програмного інтерфейсу було дотримано п'яти фундаментальних інженерних принципів:

1. **Сумісність ABI на рівні C (C-ABI Stability)**: Базовий заголовочний файл `takens.h` використовує стандартну C-угоду про виклики (`cdecl` / `extern "C"`), що гарантує бінарну сумісність між різними компіляторами (GCC, Clang, MSVC) та дозволяє безпосередньо інтегрувати бібліотеку в інші мови програмування (Python через `ctypes`/`cffi`, Rust, Go, Julia, C#, Java).
2. **Ідіоматична обгортка C++23 (`takens.hpp`)**: Для розробників мовою C++ надається заголовочний файл `takens.hpp`, який реалізує нульові за накладними витратами обгортки (Zero-overhead abstractions), оперує безпечними типами `std::span`, `std::expected` та гарантує відсутність витоків пам'яті завдяки концепції RAII.
3. **Потокобезпечність (Thread Safety)**: Усі обчислювальні функції є чистими (reentrant) і не використовують глобальний стан чи статичні змінні. Одночасно декілька потоків можуть проводити реконструкцію різних часових рядів без блокувань та м'ютексів.
4. **Явний контроль розподілу пам'яті**: Бібліотека дозволяє користувачеві надавати власні буфери пам'яті для вихідних матриць або використовувати вбудовані виділячі (custom allocators), що робить її придатною для використання в embedded-системах та системах реального часу.
5. **Передбачувана обробка помилок**: Жодна функція C API не генерує неперехоплених винятків чи аварійних завершень процесу. Усі критичні стани явно повертаються через перелічувальний тип статусів `TakensStatus`.

---

### 2. Коди помилок та статусів повернення

Усі публічні C-функції бібліотеки повертають статусний код типу `TakensStatus`. Значення `TAKENS_OK` (дорівнює `0`) відповідає успішному виконанню. Від'ємні значення вказують на конкретний тип помилки.

:::tabs
```c
typedef enum {
    TAKENS_OK                     =  0,  /* Успішне виконання операції */
    TAKENS_ERR_NULL_POINTER       = -1,  /* Передано вказівник NULL у критичний параметр */
    TAKENS_ERR_INVALID_PARAM      = -2,  /* Некоректне значення параметрів (наприклад, delay=0 чи n_bins=0) */
    TAKENS_ERR_SIGNAL_TOO_SHORT   = -3,  /* Довжина часового ряду є недостатньою для вказаних m та delay */
    TAKENS_ERR_OUT_OF_MEMORY      = -4,  /* Помилка виділення динамічної пам'яті у купі */
    TAKENS_ERR_NO_MINIMUM_FOUND   = -5,  /* У заданому діапазоні не знайдено локального мінімуму взаємної інформації */
    TAKENS_ERR_FNN_CONVERGENCE    = -6,  /* Дріб FNN не досяг заданого порогу при m <= max_m */
    TAKENS_ERR_ZERO_VARIANCE      = -7   /* Вхідний сигнал має нульову дисперсію (константний сигнал) */
} TakensStatus;
```
```cpp
#include <cstdint>

namespace takens {
enum class Status : int32_t {
    Ok                  =  0,
    NullPointer         = -1,
    InvalidParam        = -2,
    SignalTooShort      = -3,
    OutOfMemory         = -4,
    NoMinimumFound      = -5,
    FnnConvergenceError = -6,
    ZeroVariance        = -7
};
}
```
:::

#### 2.1. Опис семантики статусів помилок
- `TAKENS_ERR_NULL_POINTER`: Виникає, якщо один із критичних аргументів-вказівників (наприклад, `signal`, `out_mi_array` або `out_optimal_delay`) дорівнює `NULL`. Функція негайно припиняє виконання і не робить спроб запису за нульовою адресою.
- `TAKENS_ERR_INVALID_PARAM`: Виникає, якщо передано логічно недопустимі значення параметрів, наприклад, `config->n_bins < 2`, `config->max_delay == 0` або `r_tol <= 0.0`.
- `TAKENS_ERR_SIGNAL_TOO_SHORT`: Виникає, якщо довжина вхідного ряду `N` менша за необхідну довжину вікна затримки `(m-1)·p + 1`. Для надійного проведення алгоритмів взаємної інформації та FNN рекомендується довжина рядка `N ≥ 1000`.
- `TAKENS_ERR_OUT_OF_MEMORY`: Виникає при невдалій спробі виділення пам'яті функціями `malloc`/`calloc` під час створення затримкової матриці великих розмірів.
- `TAKENS_ERR_NO_MINIMUM_FOUND`: Виникає, якщо функція взаємної інформації `I(p)` є монотонно спадною або монотонно зростаючою у всьому діапазоні від `1` до `max_delay` без жодного локального мінімуму.
- `TAKENS_ERR_ZERO_VARIANCE`: Виникає, якщо вхідний сигнал є постійною величиною `s(t) = const`. У цьому випадку стандартне відхилення дорівнює нулю, і Z-нормалізація є неможливою.

Функція `takens_status_string(TakensStatus status)` повертає статичний рядок із символьним описом помилки.

---

### 3. Основні структури даних та конфігурації

Налаштування обчислювального конвеєра задається конфігураційною структурою `TakensConfig`.

:::tabs
```c
typedef struct {
    size_t max_delay;          /* Максимальна часова затримка для розрахунку взаємної інформації (за замовчуванням 50) */
    size_t n_bins;             /* Кількість комірок гістограми для оцінки ймовірностей (за замовчуванням 32) */
    size_t max_embedding_dim;  /* Максимальна перевірювана вимірність вкладення m (за замовчуванням 10) */
    double r_tol;              /* Поріг геометричного прискорення Kennel R1 (за замовчуванням 15.0) */
    double fnn_threshold;      /* Поріг зупинки FNN, наприклад 0.01 для 1% (за замовчуванням 0.01) */
    size_t num_threads;        /* Кількість потоків OpenMP для паралельних обчислень (0 — автовизначення) */
} TakensConfig;
```
```cpp
namespace takens {
struct Config {
    size_t max_delay{50};
    size_t n_bins{32};
    size_t max_embedding_dim{10};
    double r_tol{15.0};
    double fnn_threshold{0.01};
    size_t num_threads{0};
};
}
```
:::

#### 3.1. Детальний розбір полів структури `TakensConfig`
- `max_delay`: Задає верхню межу пошуку затримки `p` у відліках. Для високодискретизованих сигналів значення вибирають у діапазоні `50 - 200`.
- `n_bins`: Кількість інтервалів у двовимірній гістограмі для обчислення ймовірностей `P_{XY}(i, j)`. Оптимальні значення становлять `16`, `32` або `64`. Занадто велика кількість комірок при обмеженій довжині сигналу спричиняє розрідженість гістограми та шум оцінки ентропії.
- `max_embedding_dim`: Гранична вимірність `m_max`, до якої алгоритм FNN здійснює ітеративний пошук сусідів. Зазвичай вибирають `m_max = 10`.
- `r_tol`: Геометричний поріг розходження найближчих сусідів Kennel `R_1`. Типовий діапазон `10.0 ≤ r_tol ≤ 20.0`.
- `fnn_threshold`: Критичний відсоток хибних сусідів для зупинки пошуку `m`. При досягненні `FNN(m) < fnn_threshold` алгоритм вважає вимірність `m` достатньою.
- `num_threads`: Кількість паралельних потоків обчислення. Якщо `num_threads = 0`, бібліотека автоматично запитує кількість фізичних ядер процесора через OpenMP.

Функція `takens_config_init_default(TakensConfig *config)` ініціалізує структуру рекомендованими дефолтними параметрами.

Результат реконструкції фазового простору описується структурою `TakensEmbedding`:

:::tabs
```c
typedef struct {
    double *matrix_data;       /* Неперервний масив даних затримкової матриці Y розміром (rows * cols) */
    size_t rows;               /* Ефективна кількість точок атрактора N_eff = N - (m-1)*p */
    size_t cols;               /* Вимірність вкладення m */
    size_t delay;              /* Використана затримка у відліках p */
    double optimal_mi;         /* Значення взаємної інформації при вибраній затримці */
    double final_fnn_ratio;    /* Підсумкова частка хибних сусідів FNN */
} TakensEmbedding;
```
```cpp
namespace takens {
struct EmbeddingMetadata {
    size_t rows{0};
    size_t cols{0};
    size_t delay{0};
    double optimal_mi{0.0};
    double final_fnn_ratio{0.0};
};
}
```
:::

---

### 4. Специфікація функцій C API

#### 4.1. Ініціалізація конфігурації
Заповнює структуру конфігурації базовими параметрами за замовчуванням.

:::tabs
```c
TakensStatus takens_config_init_default(TakensConfig *config);
```
```cpp
namespace takens {
[[nodiscard]] Config make_default_config() noexcept {
    return Config{};
}
}
```
:::

**Параметри**:
- `config`: Вказівник на екземпляр структури `TakensConfig`, створений користувачем.

**Повертає**: `TAKENS_OK` у разі успіху або `TAKENS_ERR_NULL_POINTER`, якщо `config == NULL`.

#### 4.2. Розрахунок середньої взаємної інформації
Обчислює масив значень взаємної інформації `I(p)` для затримок від `1` до `config->max_delay` та повертає оптимальну затримку `out_optimal_delay`.

:::tabs
```c
TakensStatus takens_compute_mutual_information(
    const double *signal,
    size_t n,
    const TakensConfig *config,
    double *out_mi_array,
    size_t *out_optimal_delay
);
```
```cpp
namespace takens {
[[nodiscard]] std::expected<MutualInfoResult, Status>
compute_mutual_information(std::span<const double> signal, const Config& config = Config{});
}
```
:::

**Параметри**:
- `signal`: Масив вхідного часового ряду `s(t)` довжиною `n`.
- `n`: Кількість відліків сигналу.
- `config`: Конфігураційні параметри аналізу (якщо `NULL`, використовуються дефолтні).
- `out_mi_array`: Вихідний масив розміром `config->max_delay` (може бути `NULL`, якщо потрібен лише `out_optimal_delay`).
- `out_optimal_delay`: Вказівник на змінну, куди буде записано індекс першого локального мінімуму `I(p)`.

:::tabs
```c
#include "takens.h"
#include <stdio.h>

void run_mi_example(const double *signal, size_t n) {
    TakensConfig config;
    takens_config_init_default(&config);
    config.max_delay = 40;

    double mi_buffer[40];
    size_t opt_delay = 0;

    TakensStatus status = takens_compute_mutual_information(signal, n, &config, mi_buffer, &opt_delay);
    if (status == TAKENS_OK) {
        printf("Оптимальна затримка tau: %zu відліків\n", opt_delay);
    } else {
        printf("Помилка обчислення MI: %s\n", takens_status_string(status));
    }
}
```
```cpp
#include "takens.hpp"
#include <iostream>
#include <vector>

void run_mi_example_cpp(const std::vector<double>& signal) {
    takens::Config config;
    config.max_delay = 40;

    auto result = takens::compute_mutual_information(signal, config);
    if (result.has_value()) {
        std::cout << "Оптимальна затримка tau: " << result->optimal_delay << " відліків\n";
    } else {
        std::cerr << "Помилка обчислення MI\n";
    }
}
```
:::

#### 4.3. Розрахунок хибних найближчих сусідів (FNN)
Обчислює частку хибних найближчих сусідів `FNN(m)` для вимірностей від `1` до `config->max_embedding_dim` при фіксованій затримці `delay`.

:::tabs
```c
TakensStatus takens_compute_fnn(
    const double *signal,
    size_t n,
    size_t delay,
    const TakensConfig *config,
    double *out_fnn_array,
    size_t *out_optimal_dim
);
```
```cpp
namespace takens {
[[nodiscard]] std::expected<FNNResult, Status>
compute_fnn(std::span<const double> signal, size_t delay, const Config& config = Config{});
}
```
:::

**Параметри**:
- `signal`: Масив вхідного часового ряду.
- `n`: Кількість відліків сигналу.
- `delay`: Фіксована часова затримка `p` у відліках.
- `config`: Структура конфігурації.
- `out_fnn_array`: Вихідний масив розміром `config->max_embedding_dim` для збереження відсотків FNN.
- `out_optimal_dim`: Вказівник на змінну, куди записується найменше `m`, при якому `FNN(m) < config->fnn_threshold`.

:::tabs
```c
void run_fnn_example(const double *signal, size_t n, size_t delay) {
    TakensConfig config;
    takens_config_init_default(&config);
    config.max_embedding_dim = 8;
    config.r_tol = 15.0;

    double fnn_buffer[8];
    size_t opt_dim = 0;

    TakensStatus status = takens_compute_fnn(signal, n, delay, &config, fnn_buffer, &opt_dim);
    if (status == TAKENS_OK) {
        printf("Оптимальна вимірність m: %zu\n", opt_dim);
    }
}
```
```cpp
void run_fnn_example_cpp(const std::vector<double>& signal, size_t delay) {
    takens::Config config;
    config.max_embedding_dim = 8;
    config.r_tol = 15.0;

    auto result = takens::compute_fnn(signal, delay, config);
    if (result.has_value()) {
        std::cout << "Оптимальна вимірність m: " << result->optimal_dim << "\n";
    }
}
```
:::

#### 4.4. Створення та звільнення затримкової матриці
Формує підсумкову затримкову матрицю `TakensEmbedding` та виділяє динамічну пам'ять.

:::tabs
```c
TakensStatus takens_embedding_create(
    const double *signal,
    size_t n,
    size_t delay,
    size_t dim,
    TakensEmbedding **out_embedding
);

void takens_embedding_free(TakensEmbedding *embedding);
```
```cpp
namespace takens {
[[nodiscard]] std::expected<DelayMatrix, Status>
create_embedding(std::span<const double> signal, size_t delay, size_t dim);
}
```
:::

**Параметри**:
- `signal`: Масив вихідного сигналу.
- `n`: Довжина сигналу.
- `delay`: Вибрана затримка `p`.
- `dim`: Вибрана вимірність `m`.
- `out_embedding`: Вказівник на вказівник, куди буде записано адресу створеної структури `TakensEmbedding`.

:::tabs
```c
void run_full_pipeline_c(const double *signal, size_t n) {
    TakensConfig config;
    takens_config_init_default(&config);

    size_t opt_delay = 0;
    size_t opt_dim = 0;

    if (takens_compute_mutual_information(signal, n, &config, NULL, &opt_delay) != TAKENS_OK) return;
    if (takens_compute_fnn(signal, n, opt_delay, &config, NULL, &opt_dim) != TAKENS_OK) return;

    TakensEmbedding *emb = NULL;
    if (takens_embedding_create(signal, n, opt_delay, opt_dim, &emb) == TAKENS_OK) {
        printf("Успішно побудовано матрицю розміром %zu x %zu\n", emb->rows, emb->cols);
        
        /* Робота з даними emb->matrix_data ... */

        takens_embedding_free(emb); /* Обов'язкове звільнення пам'яті */
    }
}
```
```cpp
void run_full_pipeline_cpp(const std::vector<double>& signal) {
    try {
        takens::Embedder embedder(signal);
        auto embedding = embedder.auto_embed(); // Автоматичний вибір tau та m
        
        std::cout << "Успішно побудовано матрицю розміром " 
                  << embedding.rows() << " x " << embedding.cols() << "\n";
                  
        // Пам'ять звільняється автоматично у деструкторі embedding
    } catch (const std::exception& e) {
        std::cerr << "Помилка реконструкції: " << e.what() << "\n";
    }
}
```
:::

#### 4.5. Обчислення нелінійних інваріантів у C API
Бібліотека `libtakens` містить додаткові низькорівневі функції для аналізу побудованої затримкової матриці `TakensEmbedding`:

:::tabs
```c
/* Обчислення кореляційного інтегралу C(r) для заданого масиву радіусів */
TakensStatus takens_compute_correlation_integral(
    const TakensEmbedding *embedding,
    const double *r_values,
    size_t r_count,
    double *out_c_r
);

/* Оцінка старшого показника Ляпунова за алгоритмом Розенштейна */
TakensStatus takens_compute_lyapunov_max(
    const TakensEmbedding *embedding,
    size_t theiler_window,
    size_t max_steps,
    double *out_lyapunov_exp
);
```
```cpp
namespace takens {
[[nodiscard]] std::expected<std::vector<double>, Status>
compute_correlation_integral(const DelayMatrix& matrix, std::span<const double> r_values);

[[nodiscard]] std::expected<double, Status>
compute_lyapunov_max(const DelayMatrix& matrix, size_t theiler_window, size_t max_steps);
}
```
:::

##### Семантика параметрів інваріантних функцій:
- `embedding`: Вказівник на раніше побудовану затримкову матрицю `TakensEmbedding`.
- `r_values`: Масив вхідних радіусів `r` у логарифмічній шкалі від `r_min` до `r_max`.
- `r_count`: Кількість точок радіуса для побудови графіку `ln C(r)`.
- `out_c_r`: Вихідний масив для збереження обчислених значень `C(r)`.
- `theiler_window`: Розмір часового вікна Тейлера `W` для виключення часово близьких точок (зазвичай дорівнює затримці `delay` або часу згасання автокореляції).
- `max_steps`: Максимальна кількість кроків розходження `k` для відстеження траєкторій.
- `out_lyapunov_exp`: Вказівник на результат обчисленого значення старшого показника Ляпунова `λ₁`.

---

### 5. Специфікація обгортки C++ (`takens.hpp`)

Обгортка C++ надає високорівневий клас `takens::Embedder` та об'єкт матриці `takens::DelayMatrix`. Вона перетворює низькорівневі коди помилок у тип `std::expected` або генерує стандартні винятки `std::runtime_error`.

```cpp
namespace takens {

class DelayMatrix {
public:
    DelayMatrix() noexcept = default;
    DelayMatrix(size_t rows, size_t cols, size_t delay, std::vector<double> data);

    [[nodiscard]] size_t rows() const noexcept { return m_rows; }
    [[nodiscard]] size_t cols() const noexcept { return m_cols; }
    [[nodiscard]] size_t delay() const noexcept { return m_delay; }

    [[nodiscard]] double operator()(size_t r, size_t c) const {
        return m_data[r * m_cols + c];
    }

    [[nodiscard]] std::span<const double> row(size_t r) const {
        return std::span<const double>(&m_data[r * m_cols], m_cols);
    }

    [[nodiscard]] const std::vector<double>& data() const noexcept { return m_data; }

private:
    size_t m_rows{0};
    size_t m_cols{0};
    size_t m_delay{0};
    std::vector<double> m_data;
};

struct MutualInfoResult {
    std::vector<double> mi_values;
    size_t optimal_delay;
};

struct FNNResult {
    std::vector<double> fnn_ratios;
    size_t optimal_dim;
};

class Embedder {
public:
    explicit Embedder(std::span<const double> signal, Config config = Config{});

    [[nodiscard]] std::expected<MutualInfoResult, Status> compute_mutual_information() const;
    [[nodiscard]] std::expected<FNNResult, Status> compute_fnn(size_t delay) const;

    [[nodiscard]] std::expected<DelayMatrix, Status> embed(size_t delay, size_t dim) const;
    [[nodiscard]] std::expected<DelayMatrix, Status> auto_embed() const;

    [[nodiscard]] std::expected<double, Status> estimate_lyapunov(const DelayMatrix& matrix) const;

private:
    std::span<const double> m_signal;
    Config m_config;
};

} // namespace takens
```

---

### 6. Інтеграція з іншими мовами програмування

#### 6.1. Python ctypes обгортка (`takens.py`)
Завдяки стабільному C-ABI бібліотека `libtakens` миттєво підключається до Python без необхідності збирання складних C-розширень.

```python
import ctypes
import numpy as np

# Завантаження динамічної бібліотеки
lib = ctypes.CDLL("./libtakens.so")

# Визначення типів C
class TakensConfig(ctypes.Structure):
    _fields_ = [
        ("max_delay", ctypes.c_size_t),
        ("n_bins", ctypes.c_size_t),
        ("max_embedding_dim", ctypes.c_size_t),
        ("r_tol", ctypes.c_double),
        ("fnn_threshold", ctypes.c_double),
        ("num_threads", ctypes.c_size_t)
    ]

# Налаштування аргументів функцій
lib.takens_config_init_default.argtypes = [ctypes.POINTER(TakensConfig)]
lib.takens_config_init_default.restype = ctypes.c_int

def py_compute_mutual_info(signal: np.ndarray, max_delay: int = 50) -> int:
    signal = np.ascontiguousarray(signal, dtype=np.float64)
    config = TakensConfig()
    lib.takens_config_init_default(ctypes.byref(config))
    config.max_delay = max_delay

    opt_delay = ctypes.c_size_t(0)
    mi_buffer = (ctypes.c_double * max_delay)()

    res = lib.takens_compute_mutual_information(
        signal.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        len(signal),
        ctypes.byref(config),
        mi_buffer,
        ctypes.byref(opt_delay)
    )
    if res == 0:
        return opt_delay.value
    raise RuntimeError(f"Помилка libtakens код: {res}")
```

#### 6.2. Rust FFI зв'язування (`sys.rs`)
У мові Rust виклики C API відтворюються через модуль `foreign function interface (FFI)`.

```rust
#[repr(C)]
pub struct TakensConfig {
    pub max_delay: usize,
    pub n_bins: usize,
    pub max_embedding_dim: usize,
    pub r_tol: f64,
    pub fnn_threshold: f64,
    pub num_threads: usize,
}

extern "C" {
    pub fn takens_config_init_default(config: *mut TakensConfig) -> i32;
    pub fn takens_compute_mutual_information(
        signal: *const f64,
        n: usize,
        config: *const TakensConfig,
        out_mi: *mut f64,
        out_opt_delay: *mut usize,
    ) -> i32;
}

pub struct TakensEmbedder<'a> {
    signal: &'a [f64],
    config: TakensConfig,
}

impl<'a> TakensEmbedder<'a> {
    pub fn new(signal: &'a [f64]) -> Self {
        let mut config = unsafe { std::mem::zeroed() };
        unsafe { takens_config_init_default(&mut config) };
        Self { signal, config }
    }

    pub fn compute_mutual_info(&self) -> Result<usize, i32> {
        let mut opt_delay: usize = 0;
        let res = unsafe {
            takens_compute_mutual_information(
                self.signal.as_ptr(),
                self.signal.len(),
                &self.config,
                std::ptr::null_mut(),
                &mut opt_delay,
            )
        };
        if res == 0 { Ok(opt_delay) } else { Err(res) }
    }
}
```

---

### 7. Збирання бібліотеки за допомогою CMake та прапорці компілятора

Для забезпечення високої сумісності з різними операційними системами (Linux, macOS, Windows) збирання проєкту здійснюється за допомогою системи CMake версії `3.20` і вище.

Основними цілями збирання є:
- `libtakens_static`: статична бібліотека (`.a` / `.lib`);
- `libtakens_shared`: динамічна бібліотека (`.so` / `.dylib` / `.dll`);
- `takens_tests`: тестовий комплекс на базі GoogleTest;
- `takens_benchmarks`: бенчмарк продуктивності на базі Google Benchmark.

#### 7.1. Рекомендовані прапорці оптимізації компілятора
Для досягнення максимальної швидкодії при обчисленні відстаней у фазовому просторі рекомендуються наступні прапорці для компіляторів GCC та Clang:

```cmake
set(CMAKE_C_FLAGS_RELEASE "-O3 -march=native -ffast-math -flto -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math -flto -std=c++23 -DNDEBUG")
```

Прапорець `-march=native` автоматично вмикає інструкції AVX2 та FMA3 процесора носія, а `-flto` (Link-Time Optimization) дозволяє проводити міжмодульне вбудовування функцій (inlining) при зв'язуванні об'єктних файлів.

---

### 8. Простеження викликів, метрики продуктивності та телеметрія

При використанні бібліотеки у промислових вимірювальних демонах високої надійності вимагається простеження часу виконання обчислювальних кроків та моніторинг ресурсів пам'яті.

#### 8.1. Реєстрація зворотних викликів простеження (Tracing Callbacks)
Бібліотека дозволяє зареєструвати користувальницьку функцію зворотного виклику для логування подій:

:::tabs
```c
typedef void (*TakensTraceCallback)(int log_level, const char *message, double execution_time_ms);

void takens_set_trace_callback(TakensTraceCallback callback);
```
```cpp
namespace takens {
using TraceCallback = std::function<void(int log_level, std::string_view message, double execution_time_ms)>;

void set_trace_callback(TraceCallback callback);
}
```
:::

Рівні логування описуються константами `TAKENS_LOG_INFO`, `TAKENS_LOG_WARN`, `TAKENS_LOG_ERROR`. При виконанні тривалих обчислень FNN функція зворотного виклику повідомляє прогрес у відсотках та час обчислення кожної вимірності `m`, що дозволяє зовнішнім графічним інтерфейсам демонструвати прогрес-бар.

#### 8.2. Вбудовані лічильники процесорних тактів та метрики
Для аналізу продуктивності гарячих ділянок коду (Hotspots) обчислювальний рушій збирає внутрішні метрики:
- `cycles_per_vector`: Середня кількість тактів процесора (`rdtsc`), витрачена на пошук найближчого сусіда одного вектора у `R^m`;
- `l3_cache_misses_est`: Оціночна кількість промахів L3-кешу при випадковому доступі до елементів траєкторії;
- `peak_memory_bytes`: Максимальний обсяг оперативно виділеної пам'яті під час виконання конвеєра реконструкції.

Ці метрики доступні через функцію `takens_get_last_performance_metrics(TakensMetrics *out_metrics)` і можуть експортуватися у системи моніторингу Prometheus чи Grafana. Завдяки стандартному формату логування розробники можуть легко налаштовувати сповіщення (alerts) про деградацію продуктивності аналізу в реальному часі при збільшенні довжини вхідних часових рядів.

---

### 9. Налаштування паралелізму OpenMP та оптимізації SIMD

Обчислювальний рушій `libtakens` вимагає високої продуктивності при роботі з великими масивами даних. Для досягнення максимальної швидкодії реалізовано двопотокову модель розпаралелювання та векторизації.

#### 9.1. Модель паралелізму OpenMP
При обчисленні взаємної інформації `I(p)` для `max_delay` різних затримок кожен потік обробляє окремі затримки незалежно один від одного. Оскільки кожна затримка має власний локальний буфер гістограми `hist_2d`, між потоками повністю відсутній стан гонки (Race Condition).

В алгоритмі FNN паралелізм застосовується до зовнішнього циклу по векторах `i` від `0` до `N_{eff}`. Директива `#pragma omp parallel for schedule(static)` рівномірно розподіляє блоки векторів між робочими потоками OpenMP pool.

:::tabs
```c
#pragma omp parallel for schedule(static) num_threads(config->num_threads)
for (size_t i = 0; i < n_vectors; ++i) {
    /* Локальний пошук найближчого сусіда для вектора i у мові C */
}
```
```cpp
#include <execution>
#include <algorithm>

// Аналог паралельного обходу в C++23 з використанням std::execution::par
std::for_each(std::execution::par, indices.begin(), indices.end(), [&](size_t i) {
    /* Локальний пошук найближчого сусіда для вектора i у мові C++ */
});
```
:::

#### 9.2. Векторизація SIMD та запобігання помилкам False Sharing
Для прискорення обчислення квадрата відстані `||Y_i - Y_j||^2` пам'ять затримкової матриці вирівнюється за кордоном 64 байт (ширина кеш-рядка процесора). Використання директив `#pragma omp atomic` для накопичення суми хибних сусідів мінімізується: кожен потік накопичує приватний лічильник `local_false_count`, який додається до загальної суми лише при виході з паралельної секції. Це запобігає ефекту хибного спільного використання кеш-рядків (False Sharing), який міг би уповільнити обчислення на багатоядерних процесорах.

---

### 10. Методика тестування, модульні тести та валідація API у CI/CD

Автоматизоване тестування бібліотеки `libtakens` розбито на чотири шари валідації:

1. **Модульні тести (Unit Tests)**: Перевірка базових математичних операцій на синусоїдальних сигналах із відомим теоретичним результатом (для чисте синусоїди `s(t) = sin(ω t)` перший мінімум взаємної інформації повинен строго відповідати затримці `τ = T / 4`, а FNN падає до нуля при `m = 2`).
2. **Перевірка на витоки пам'яті (Valgrind / AddressSanitizer)**: Тестові комплекси збираються з прапорцями `-fsanitize=address,undefined` для автоматичного виявлення витоків пам'яті, виходу за межі масивів та некоректних вирівнювань.
3. **Fuzzing-тестування (LibFuzzer)**: Перевірка стійкості API до некоректних даних. На вхід `takens_compute_mutual_information` подаються випадкові бінарні дампи, сигнали з `NaN`, `Inf`, константні масиви та масиви з одного елемента. Бібліотека повинна повертати статус помилки без краху.
4. **Порівняльний регресійний бенчмаркінг (Benchmark Tests)**: Оцінка продуктивності обчислення FNN у порівнянні з референсними реалізаціями у пакунку `TISEAN` (Time Series Analysis package).

---

### 11. Вимоги до обробки помилок, пам'яті та критичні застереження

#### 11.1. Життєвий цикл пам'яті (Memory Lifetime)
При використанні C API пам'ять, виділена функцією `takens_embedding_create`, зберігається у купі (heap) доти, доки не буде викликано `takens_embedding_free`. Спроба звернутися до `matrix_data` після звільнення є невизначеною поведінкою (Use-After-Free). Для запобігання витокам пам'яті у разі виникнення помилок у зовнішньому коді рекомендується виклики `takens_embedding_create` вкладати у блоки `try-finally` або використовувати C++ обгортку `DelayMatrix`.

#### 11.2. Перевірка вказівників NULL та валідація даних
Усі функції C API явно перевіряють входження вказівників на `NULL`. Передача некоректних вказівників не викликає падіння (Segmentation Fault), а повертає статус `TAKENS_ERR_NULL_POINTER`. Перед проведенням фазового аналізу вхідні значення сигналу автоматично перевіряються на наявність некоректних чисел `NaN` та `Inf`.

#### 11.3. Паралелізм OpenMP та потокобезпечність
Якщо параметр `config.num_threads > 1`, обчислення внутрішніх циклів FNN та взаємної інформації паралеляться за допомогою специфікації OpenMP `#pragma omp parallel for`. Переданий масив `signal` повинен залишатися незмінним (read-only) під час обчислень. Жодна з функцій не модифікує вхідні буфери даних.

#### 11.4. Продуктивність та масштабованість пам'яті
Розмір затримкової матриці становить `(N - (m-1)p) × m × 8` байт. Для сигналу `N = 10⁶` відліків та `m = 5` матриця вимагає близько `40` Мегабайт оперативної пам'яті. Бібліотека виділяє пам'ять єдиним неперервним блоком, що гарантує високу кеш-локальність процесора і мінімізує промахи L2/L3 кешу. Завдяки послідовній укладці рядків (Row-Major format) векторизовані інструкції SIMD виконують читання пам'яті з максимальною пропускною здатністю шини даних, забезпечуючи високу швидкість обчислення нелінійних атракторів без затримок обробки.
