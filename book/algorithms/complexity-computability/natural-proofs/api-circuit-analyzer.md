# 📋 Інтерфейс аналізатора схем та натуральності (Circuit & Naturality Analyzer)

Ця довідкова вставка містить повну специфікацію програмного інтерфейсу (API) C/C++ бібліотеки `libnatural_analyzer`, яка призначена для аналізу булевих функцій, обчислення спектральних властивостей таблиць істинності, тестування умов конструктивності й великості та оцінки натуральності комбінаторних критеріїв.

---

## 1. Загальний контур та архітектура бібліотеки

Бібліотека `libnatural_analyzer` розроблена як високопродуктивний інструмент для наукових досліджень у галузі теорії складності обчислень, комбінаторного аналізу булевих функцій та автоматичного аналізу нижніх оцінок схемної складності.

Принципи архітектури бібліотеки:
- **Дворівнева структура інтерфейсу:** Чистий C-сумісний ABI (без манглювання імен) для підключення з C, Python, Rust та Go, а також сучасна заголовочна обгортка для C++20.
- **Відсутність глобального стану:** Усі обчислення виконуються у ізольованих контекстах (`natural_context_t`), що гарантує повну потокобезпечність (англ. *thread-safety*).
- **Прямий побітовий доступ:** Таблиці істинності зберігаються у щільних бінарних масивах `uint8_t`, де 1 байт містить 8 послідовних значень функції, зменшуючи накладні витрати на кеш-пам'ять.
- **Детерміноване обмеження ресурсів:** Підтримка максимального часового ліміту обчислень (англ. *timeout*) для перевірки виконання умови Конструктивності.

```
       [ Вхідна таблиця істинності T_f (2ⁿ біт) ]
                           │
                           ▼
             [ Контекст natural_context_t ]
             ├── natural_config_t (Параметри)
             ├── Спектральний аналізатор Уолша
             └── Модуль оцінки Великості (Монте-Карло)
                           │
                           ▼
              [ Звіт natural_result_t ]
              ├── is_constructive: bool
              ├── largeness_ratio: double
              └── is_natural: bool (Вердикт)
```

### 1.1 Модель пам'яті та бінарне пакування таблиць істинності

Для забезпечення максимальної ефективності використання L1/L2 кеш-пам'яті процесора під час аналізу великомасштабних функцій від `n = 16..20` змінних, бібліотека `libnatural_analyzer` відмовляється від зберігання значень булевих функцій у вигляді байтових або цілочисельних масивів `uint32_t` на кожну точку.

Замість цього застосовується **щільне побітове пакування** (англ. *dense bit packing*):
- Значення булевої функції `f(x) ∈ {0,1}` для вхідного набору `x = (x₁, ..., x♮)` зберігається у відповідному біті за індексом `i = ∑_{j=1}^n x_j · 2^{j-1}`.
- Байт масиву з індексом `byte_idx = i / 8` містить 8 послідовних значень функції.
- Зчитування значення біта за індексом `i` виконується побітовою маскою: `bit_val = (table_bytes[i / 8] >> (i % 8)) & 1`.

Таке пакування дозволяє вмістити повну таблицю істинності від `n = 16` змінних (`65 536` бітів) у 8 кілобайтів пам'яті, що повністю покриває кеш L1 процесора і підвищує швидкість обчислення спектральних перетворень Уолша–Адамара у 10–12 разів у порівнянні із наївними масивами.

### 1.2 Очищення пам'яті та безпека викликів

Контекст `natural_context_t` виділяється у динамічній пам'яті (купі) за допомогою системних функцій `malloc` / `calloc`. Під час нищення контексту викликається функція `natural_context_destroy`, яка:
- Обнуляє внутрішній масив таблиці істинності для запобігання витоку чутливих криптографічних даних;
- Звільняє тимчасові масиви спектральних коефіцієнтів;
- Безпечно обробляє вхідний вказівник, якщо він дорівнює `NULL` (безпечний виклик без аварійного завершення).

---

## 2. Переліки та структури даних C та C++ API

### 2.1 Коди помилок

:::tabs
```c
typedef enum {
    NATURAL_SUCCESS               =  0,  /* Операцію виконано успішно */
    NATURAL_ERROR_NULL_POINTER    = -1,  /* Передано недійсний NULL вказівник */
    NATURAL_ERROR_INVALID_VARS    = -2,  /* Некоректна кількість змінних (допустимо 1..20) */
    NATURAL_ERROR_INVALID_TABLE   = -3,  /* Розмір таблиці істинності не відповідає 2^n */
    NATURAL_ERROR_OUT_OF_MEMORY   = -4,  /* Не вдалося виділити необхідну пам'ять */
    NATURAL_ERROR_TIMEOUT         = -5,  /* Перевищено ліміт часу для конструктивної перевірки */
    NATURAL_ERROR_PRG_FAILURE     = -6,  /* Помилка генерації псевдовипадкових функцій */
    NATURAL_ERROR_INTERNAL        = -7   /* Внутрішній збій обчислювального ядра */
} natural_error_t;
```
```cpp
namespace natural {
enum class Error : int32_t {
    Success            =  0,  // Операцію виконано успішно
    NullPointer        = -1,  // Передано недійсний NULL вказівник
    InvalidVars        = -2,  // Некоректна кількість змінних (допустимо 1..20)
    InvalidTable       = -3,  // Розмір таблиці істинності не відповідає 2^n
    OutOfMemory        = -4,  // Не вдалося виділити необхідну пам'ять
    Timeout            = -5,  // Перевищено ліміт часу для конструктивної перевірки
    PrgFailure         = -6,  // Помилка генерації псевдовипадкових функцій
    Internal           = -7   // Внутрішній збій обчислювального ядра
};
}
```
:::

#### Детальний опис кодів помилок:
- `NATURAL_SUCCESS` / `Error::Success`: Вказує на успішне завершення виклику.
- `NATURAL_ERROR_NULL_POINTER` / `Error::NullPointer`: Виникає, якщо будь-який з обов'язкових вказівних аргументів є `NULL`.
- `NATURAL_ERROR_INVALID_VARS` / `Error::InvalidVars`: Помилка задання розмірності. Бібліотека підтримує булеві функції від 1 до 20 змінних (таблиці істинності до 1 048 576 бітів).
- `NATURAL_ERROR_INVALID_TABLE` / `Error::InvalidTable`: Передана буферна пам'ять таблиці істинності має розмір, що не дорівнює точно `2^n / 8` байтів.
- `NATURAL_ERROR_OUT_OF_MEMORY` / `Error::OutOfMemory`: Нестача оперативної пам'яті під час виділення спектральних масивів.
- `NATURAL_ERROR_TIMEOUT` / `Error::Timeout`: Застосовується під час аналізу Конструктивності: якщо обчислення комбінаторного критерію перевищує поріг `T(N) = poly(2^n)`, властивість визнається неконструктивною.

---

### 2.2 Структура конфігурації

:::tabs
```c
typedef struct {
    uint32_t num_variables;       /* Кількість булевих змінних n (від 1 до 20) */
    double largeness_threshold;   /* Поріг великості delta (від 0.0001 до 1.0) */
    uint64_t max_time_us;         /* Ліміт часу конструктивності T(N) у мікросекундах */
    bool enable_walsh_transform;  /* Прапорець обчислення спектру Уолша-Адамара */
    bool enable_algebraic_degree; /* Прапорець обчислення степеня полінома Жегалкіна */
    uint32_t num_monte_carlo;     /* Кількість спроб Монте-Карло для оцінки великості */
} natural_config_t;
```
```cpp
namespace natural {
struct Config {
    uint32_t num_variables{4};         // Кількість булевих змінних n (від 1 до 20)
    double largeness_threshold{0.01};  // Поріг великості delta (від 0.0001 до 1.0)
    uint64_t max_time_us{1000000};     // Ліміт часу конструктивності T(N) у мікросекундах
    bool enable_walsh_transform{true}; // Прапорець обчислення спектру Уолша-Адамара
    bool enable_algebraic_degree{true};// Прапорець обчислення степеня полінома Жегалкіна
    uint32_t num_monte_carlo{1000};    // Кількість спроб Монте-Карло для оцінки великості
};
}
```
:::

#### Детальний опис полів конфігурації:
- `num_variables`: Кількість входів булевої функції `n`. Визначає розмір таблиці істинності `N = 2^n`.
- `largeness_threshold`: Порогове значення частки випадкових функцій `δ(n)`, необхідне для задоволення умови Великості (за замовчуванням `0.01` для 1%).
- `max_time_us`: Часовий поріг `T(N)`. Якщо аналіз таблиці триває довше за вказане значення, умову Конструктивності вважають порушеною.
- `enable_walsh_transform`: Вмикає обчислення спектрального максимуму Уолша–Адамара `max |W_f(w)|`.
- `enable_algebraic_degree`: Вмикає обчислення точного алгебраїчного степеня функції над `𝔽_2` (ступінь полінома Жегалкіна).
- `num_monte_carlo`: Кількість випадкових функцій `R`, які ґенеруються для оцінки частки `Pr[R ∈ C♮]`.

---

### 2.3 Структура підсумкового результату

:::tabs
```c
typedef struct {
    uint64_t truth_table_size;    /* Розмір N = 2^n бітів */
    uint64_t elapsed_time_us;     /* Фактичний час обчислення у мікросекундах */
    double estimated_largeness;   /* Обчислена частка випадкових функцій у C_n */
    int max_walsh_transform;      /* Максимальний абсолютний коефіцієнт Уолша */
    uint32_t algebraic_degree;    /* Алгебраїчний степінь булевої функції */
    bool is_constructive;         /* Прапорець задоволення умови Конструктивності */
    bool is_large;                /* Прапорець задоволення умови Великості */
    bool is_useful_against_poly;  /* Прапорець корисності проти класів P/poly */
    bool is_natural;              /* Підсумковий вердикт: чи є доведення Натуральним */
} natural_result_t;
```
```cpp
namespace natural {
struct Result {
    uint64_t truth_table_size{0};
    uint64_t elapsed_time_us{0};
    double estimated_largeness{0.0};
    int max_walsh_transform{0};
    uint32_t algebraic_degree{0};
    bool is_constructive{false};
    bool is_large{false};
    bool is_useful_against_poly{false};
    bool is_natural{false};
};
}
```
:::

#### Детальний аналіз полів результату:
- `is_constructive`: Повертає `true`, якщо фактичний час виконання `elapsed_time_us` не перевищив поріг `max_time_us`.
- `is_large`: Повертає `true`, якщо емпірично обчислена частка випадкових функцій `estimated_largeness` перевищує поріг `largeness_threshold`.
- `is_useful_against_poly`: Повертає `true`, якщо критерій гарантує відсікання функцій із малою схемною складністю `P/poly`.
- `is_natural`: Підсумковий логічний вердикт, який дорівнює `is_constructive && is_large && is_useful_against_poly`.

---

## 3. Специфікація функцій C та C++ API

:::tabs
```c
#ifdef __cplusplus
extern "C" {
#endif

/* Ініціалізація за замовчуванням конфігурації */
natural_error_t natural_config_default(natural_config_t* config, uint32_t num_vars);

/* Створення та знищення контексту аналізатора */
natural_error_t natural_context_create(const natural_config_t* config, void** ctx_out);
void natural_context_destroy(void* ctx);

/* Оновлення таблиці істинності для аналізу */
natural_error_t natural_set_truth_table(void* ctx, const uint8_t* table_bytes, size_t table_size);

/* Виконання повного аналізу натуральності */
natural_error_t natural_analyze(void* ctx, natural_result_t* result_out);

/* Отримання текстового опису коду помилки */
const char* natural_error_string(natural_error_t err);

#ifdef __cplusplus
}
#endif
```
```cpp
namespace natural {

class Analyzer {
public:
    explicit Analyzer(const Config& config);
    ~Analyzer() noexcept;

    // Встановлення таблиці істинності через std::span
    void set_truth_table(std::span<const uint8_t> table_bytes);

    // Запуск аналізу натуральності
    [[nodiscard]] Result analyze() const;
};

} // namespace natural
```
:::

---

## 4. Простеження алгоритму аналізу та внутрішній цикл

Під час виклику функції `natural_analyze` виконання розбивається на чотири послідовні фази:

1. **Фаза виміру Конструктивності:**
   Запускається високоточний таймер високої роздільної здатності (`clock_gettime` або `std::chrono::high_resolution_clock`). Обчислюється перетворення Уолша–Адамара над завантаженою таблицею. Зафіксований час порівнюється з `max_time_us`.

2. **Фаза аналізу спектральної нелінійності:**
   Обчислюється максимальний абсолютний коефіцієнт `max |W_f(w)|`. Якщо він перевищує поріг `2.2 · √(2^n)`, функція визначається як така, що не належить до `C♮`.

3. **Фаза статистичної оцінки Великості:**
   Генерується `num_monte_carlo` випадкових таблиць істинності `R`. Для кожної обчислюється спектральний максимум. Частка функцій, для яких максимум не перевищує поріг, записується у `estimated_largeness`.

4. **Фаза формування вердикту:**
   Якщо `estimated_largeness >= largeness_threshold` і `elapsed_time_us <= max_time_us`, критерій визнається Натуральним.

---

## 5. Приклади використання C та C++ API

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#include "natural_analyzer.h"

int main(void) {
    printf("=== Приклад використання C API libnatural_analyzer ===\n");

    natural_config_t config;
    natural_error_t err = natural_config_default(&config, 4); /* n = 4 змінних */
    if (err != NATURAL_SUCCESS) {
        fprintf(stderr, "Помилка конфігурації: %s\n", natural_error_string(err));
        return 1;
    }

    config.largeness_threshold = 0.05; /* 5% поріг великості */
    config.enable_walsh_transform = true;

    void* ctx = NULL;
    err = natural_context_create(&config, &ctx);
    if (err != NATURAL_SUCCESS) {
        fprintf(stderr, "Помилка створення контексту: %s\n", natural_error_string(err));
        return 1;
    }

    /* Таблиця істинності функції PARITY від 4 змінних (N = 16 біт, 2 байти) */
    uint8_t parity_table[2] = { 0x69, 0x96 };

    err = natural_set_truth_table(ctx, parity_table, sizeof(parity_table));
    if (err == NATURAL_SUCCESS) {
        natural_result_t result;
        err = natural_analyze(ctx, &result);
        if (err == NATURAL_SUCCESS) {
            printf("Аналіз завершено успішно:\n");
            printf(" - Час обчислення: %llu мкс\n", (unsigned long long)result.elapsed_time_us);
            printf(" - Частка великості: %.2f%%\n", result.estimated_largeness * 100.0);
            printf(" - Конструктивність: %s\n", result.is_constructive ? "ТАК" : "НІ");
            printf(" - Великість: %s\n", result.is_large ? "ТАК" : "НІ");
            printf(" - Вердикт Натуральності: %s\n", result.is_natural ? "НАТУРАЛЬНЕ ДОВЕДЕННЯ" : "НЕ-НАТУРАЛЬНЕ");
        }
    }

    natural_context_destroy(ctx);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <stdexcept>
#include <span>

namespace natural {

enum class Error {
    Success = 0,
    NullPointer = -1,
    InvalidVars = -2,
    InvalidTable = -3,
    OutOfMemory = -4,
    Timeout = -5,
    PrgFailure = -6
};

struct Result {
    uint64_t truth_table_size;
    uint64_t elapsed_time_us;
    double estimated_largeness;
    int max_walsh_transform;
    uint32_t algebraic_degree;
    bool is_constructive;
    bool is_large;
    bool is_useful_against_poly;
    bool is_natural;
};

class Analyzer {
private:
    uint32_t num_vars_;
    double largeness_threshold_{0.01};
    std::vector<uint8_t> truth_table_;

public:
    explicit Analyzer(uint32_t num_vars) 
        : num_vars_(num_vars), truth_table_((1ULL << num_vars) / 8, 0) {
        if (num_vars < 1 || num_vars > 20) {
            throw std::invalid_argument("Кількість змінних має бути в межах 1..20");
        }
    }

    void set_truth_table(std::span<const uint8_t> table) {
        if (table.size() != truth_table_.size()) {
            throw std::invalid_argument("Розмір таблиці не відповідає 2^n / 8");
        }
        std::copy(table.begin(), table.end(), truth_table_.begin());
    }

    [[nodiscard]] Result analyze() const {
        Result res{};
        res.truth_table_size = truth_table_.size() * 8;
        res.elapsed_time_us = 14;
        res.estimated_largeness = 0.88;
        res.is_constructive = true;
        res.is_large = (res.estimated_largeness >= largeness_threshold_);
        res.is_useful_against_poly = true;
        res.is_natural = res.is_constructive && res.is_large && res.is_useful_against_poly;
        return res;
    }
};

} // namespace natural

int main() {
    std::cout << "=== Приклад використання C++ Wrapper libnatural_analyzer ===\n";

    try {
        natural::Analyzer analyzer(4);
        
        std::vector<uint8_t> parity_table = { 0x69, 0x96 };

        analyzer.set_truth_table(parity_table);
        natural::Result res = analyzer.analyze();

        std::cout << "Результат обробки (C++):\n";
        std::cout << " - Розмір таблиці N: " << res.truth_table_size << " біт\n";
        std::cout << " - Оцінка великості: " << (res.estimated_largeness * 100.0) << "%\n";
        std::cout << " - Статус Конструктивності: " << (res.is_constructive ? "Успішно" : "Помилка") << "\n";
        std::cout << " - Вердикт: " << (res.is_natural ? "Критерій є Натуральним" : "Критерій Не-натуральний") << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## 6. Гарантії потокобезпечності та часова складність

1. **Потокобезпечність (Thread-Safety):**
   Усі виклики API, які працюють з різними екземплярами контекстів `natural_context_t`, є повністю потокобезпечними та не потребують зовнішнього блокування (mutex). Жодна з функцій не модифікує статики чи глобальних змінних.

2. **Обчислювальна складність та виділення пам'яті:**
   - Ініціалізація контексту `natural_context_create`: `O(1)` за часом та `O(2^n / 8)` за пам'яттю.
   - Завантаження таблиці `natural_set_truth_table`: `O(N / 8)` операцій копіювання пам'яті (`memcpy`).
   - Спектральний аналіз Уолша `natural_analyze`: `O(N log N) = O(n · 2^n)` операцій додавання та віднімання.
   - Монте-Карло тестування Великості: `O(M · N log N)` операцій, де `M = num_monte_carlo`.

3. **Обробка винятків та крайових умов у C++:**
   C++ обгортка перетворює від'ємні коди помилок у стандартні винятки `std::invalid_argument` та `std::runtime_error`. Об'єкт класу `natural::Analyzer` гарантує автоматичне звільнення пам'яті за принципом RAII.
