# 📋 Інтерфейс аналізатора складності булевих функцій (API Reference)

Цей довідник описує повну специфікацію публічного інтерфейсу бібліотеки та інструменту командного рядка (CLI) для аналізу складності дерев рішень булевих функцій `tree-complexity-analyzer`. Інтерфейс надає засоби для обчислення детермінованої складності `D(f)`, ймовірнісної `R(f)`, складності сертифікатів `C(f)`, чутливості `s(f)`, блокової чутливості `bs(f)` та алгебраїчного степеня `deg(f)`.

Програмний інтерфейс спроєктовано за принципами низького накладного витрачання ресурсів (zero-cost abstractions) та повної сумісності з POSIX-системами. Бібліотека складається з низькорівневого C ABI, який гарантує стабільне бінарне зв'язування, та високорівневого C++20 інтерфейсу, що забезпечує безпеку типів, обробку помилок через семантику `std::expected` та відсутність витоків пам'яті за допомогою RAII.

Окрім прямого застосування в алгоритмічному аналізі, цей інтерфейс використовується у системах символьного виконання (symbolic execution), аналізі стійкості криптографічних примітивів та оптимізації комбінаційних логічних схем. Завдяки чіткому розділенню обчислювальних прапорців користувач може запускати лише ті вимірювання, які необхідні для поточного дослідження, уникаючи зайвих обчислювальних витрат на побудову повного дерева рішень там, де достатньо оцінити звичайну чутливість.

---

## 1. Архітектурні принципи та життєвий цикл об'єктів

Аналізатор складності булевих функцій побудовано як модульну обчислювальну бібліотеку з чітким розділенням етапів ініціалізації, перевірки вхідних даних, безпосередньо обчислення комбінаторних параметрів та вилучення ресурсів.

### Потокобезпечність та керування пам'яттю
1. **Потокобезпечність (Thread-Safety):** Усі обчислювальні функції є повністю потокобезпечними та не мають внутрішнього глобального стану (`reentrant`). Декілька потоків виконання можуть одночасно аналізувати різні булеві функції або обчислювати вибіркові метрики для одного й того самого контексту без потреби у зовнішньому блокуванні (`mutex`).
2. **Стратегія виділення пам'яті:** Під час обчислення детермінованої складності `D(f)` бібліотека створює локальну таблицю мемоїзації підпросторів. Пам'ять під хеш-таблицю виділяється у системній купі (`heap`) і повністю звільняється одразу після завершення функції `tc_analyze_truth_table` чи методу `analyze()`.
3. **Обмеження ресурсів та сигнал-безпека:** Для запобігання переповненню пам'яті при великих значеннях `n` (для `n > 16`) бібліотека застосовує арену пам'яті з фіксованим верхнім лімітом. Якщо розмір мемоїзації перевищує виділений ліміт, обчислювальне ядро повертає код помилки `TC_ERR_OUT_OF_MEMORY`. Виклики функцій бібліотеки є асинхронно-сигнал-безпечними (`async-signal-safe`) у межах стандарту POSIX.1-2008, що дозволяє безпечно викликати перевірки у обробниках сигналів переривання.
4. **Сумісність з аналізаторами (Sanitizers):** Код повністю сумісний із `AddressSanitizer` (ASan), `ThreadSanitizer` (TSan) та `MemorySanitizer` (MSan). Усі виділення пам'яті гарантовано ініціалізуються до першого читання, упереджуючи появу невизначеного стану регістрів процесора.

---

## 2. Специфікація програмного інтерфейсу (C ABI та C++ Header)

Низькорівневий C API призначено для прямого використання у високопродуктивних обчислювальних ядрах, а також для побудови зв'язок (bindings) із мовами Python, Rust, Go та Julia. Високорівневий C++20 API інкапсулює стан у класі `BooleanAnalyzer` та повертає `std::expected`.

:::tabs
```c
/* C API: tree_complexity.h */
#ifndef TREE_COMPLEXITY_H
#define TREE_COMPLEXITY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи помилок */
typedef enum {
    TC_SUCCESS              =  0,
    TC_ERR_INVALID_N        = -1,
    TC_ERR_NULL_POINTER     = -2,
    TC_ERR_TABLE_SIZE       = -3,
    TC_ERR_OUT_OF_MEMORY    = -4,
    TC_ERR_TIMEOUT          = -5
} tc_error_t;

/* Прапорці обчислення для вибіркового аналізу метрик */
typedef enum {
    TC_OPT_NONE             = 0x00,
    TC_OPT_SENSITIVITY      = 0x01,  /* Обчислити s(f) */
    TC_OPT_BLOCK_SENSITIVITY= 0x02,  /* Обчислити bs(f) */
    TC_OPT_CERTIFICATE      = 0x04,  /* Обчислити C(f) */
    TC_OPT_DEGREE           = 0x08,  /* Обчислити deg(f) */
    TC_OPT_DECISION_TREE    = 0x10,  /* Обчислити D(f) */
    TC_OPT_ALL              = 0x1F   /* Обчислити всі метрики */
} tc_options_t;

/* Структура результатів аналізу */
typedef struct {
    uint32_t num_variables;      /* Кількість змінних n */
    uint32_t sensitivity;        /* Проста чутливість s(f) */
    uint32_t block_sensitivity;  /* Блокова чутливість bs(f) */
    uint32_t cert_complexity_0;  /* Складність 0-сертифіката C0(f) */
    uint32_t cert_complexity_1;  /* Складність 1-сертифіката C1(f) */
    uint32_t cert_complexity;    /* Загальна складність сертифікатів C(f) */
    uint32_t degree;             /* Степінь многочлена deg(f) */
    uint32_t decision_tree_depth;/* Детермінована складність D(f) */
    double   execution_time_ms;  /* Час виконання у мілісекундах */
} tc_result_t;

/* Створення контексту булевої функції та обчислення обраних метрик */
tc_error_t tc_analyze_truth_table(
    uint32_t num_vars,
    const uint8_t *truth_table,
    uint32_t options,
    tc_result_t *out_result
);

/* Отримання текстового опису помилки */
const char* tc_error_string(tc_error_t err);

#ifdef __cplusplus
}
#endif

#endif /* TREE_COMPLEXITY_H */
```
```cpp
// C++ API: tree_complexity.hpp
#ifndef TREE_COMPLEXITY_HPP
#define TREE_COMPLEXITY_HPP

#include <vector>
#include <string>
#include <span_view.hpp>
#include <expected>
#include <chrono>
#include <cstdint>

namespace complexity {

enum class ErrorCode {
    InvalidNumVars,
    NullPointer,
    InvalidTableSize,
    OutOfMemory,
    Timeout
};

struct AnalysisOptions {
    bool calc_sensitivity{true};
    bool calc_block_sensitivity{true};
    bool calc_certificate{true};
    bool calc_degree{true};
    bool calc_decision_tree{true};
    std::chrono::milliseconds timeout{5000};
};

struct AnalysisReport {
    size_t num_variables{0};
    size_t sensitivity{0};
    size_t block_sensitivity{0};
    size_t cert_0{0};
    size_t cert_1{0};
    size_t cert_total{0};
    size_t degree{0};
    size_t decision_tree_depth{0};
    std::chrono::microseconds elapsed_time{0};

    [[nodiscard]] std::string to_json() const;
};

class BooleanAnalyzer {
public:
    explicit BooleanAnalyzer(size_t num_vars, std::span<const uint8_t> truth_table);

    [[nodiscard]] std::expected<AnalysisReport, ErrorCode> analyze(
        const AnalysisOptions& opts = {}
    ) const noexcept;
};

} // namespace complexity

#endif // TREE_COMPLEXITY_HPP
```
:::

### Таблиця параметрів та контрактів C API

Головна функція `tc_analyze_truth_table` приймає вхідну таблицю істинності булевої функції, заповнює передану структуру результатів `tc_result_t` та повертає код статусу `tc_error_t`. Вхідна таблиця істинності повинна містити точно `2ⁿ` байтів, де кожен байт дорівнює `0` або `1`. Якщо передано неочікуваний розмір або нульовий вказівник, функція негайно припиняє виконання та повертає відповідний код помилки, не викликаючи витоків пам'яті.

| Параметр / Поле | Тип | Опис / Значення за замовчуванням | Необхідність |
| :--- | :--- | :--- | :--- |
| `num_vars` | `uint32_t` | Кількість змінних булевої функції `n` (`1 ≤ n ≤ 20`). | Обов'язкове |
| `truth_table` | `const uint8_t*` | Масив із `2ⁿ` елементів (0 або 1), що описує таблицю істинності. | Обов'язкове |
| `options` | `uint32_t` | Бітова маска прапорців `tc_options_t` для вибору обчислюваних метрик. | Обов'язкове |
| `out_result` | `tc_result_t*` | Вказівник на структуру для запису обчислених результатів. | Обов'язкове |

---

## 3. Інтерфейс командного рядка (CLI)

Інструмент `tree-complexity-cli` дозволяє проводити миттєвий аналіз булевих функцій із термінала, інтегрувати обчислення у CI/CD конвеєри та автоматизовані тестові скрипти.

Програма підтримує передачу таблиці істинності в двійковому форматі (символи `0` та `1`) або у компактному шістнадцятковому вигляді з префіксом `0x`. CLI автоматично перевіряє коректність вхідного рядка та виводить інформативні повідомлення про помилки в стандартний потік помилок `stderr`.

```bash
tree-complexity-cli --vars <N> --table <TRUTH_TABLE_HEX_OR_BIN> [ОПЦІЇ]
```

### Таблиця прапорців CLI

| Флаг CLI | Короткий | Тип | Опис | За замовчуванням |
| :--- | :--- | :--- | :--- | :--- |
| `--vars` | `-n` | Ціле число | Кількість змінних `n`. | **Обов'язковий** |
| `--table` | `-t` | Рядок | Таблиця істинності у двійковому (`0101...`) або шістнадцятковому (`0xA6`) форматі. | **Обов'язковий** |
| `--metrics` | `-m` | Рядок | Список метрик через кому: `all`, `s`, `bs`, `cert`, `deg`, `dt`. | `all` |
| `--format` | `-f` | Enum | Формат виводу результатів: `text`, `json`, `csv`. | `text` |
| `--timeout` | `-s` | Ціле число | Таймаут виконання в секундах. | `10` |
| `--verbose` | `-v` | Прапор | Розширений вивід із проміжними кроками та сертифікатами. | `false` |

### Приклад використання CLI

Для аналізу функції більшості `MAJ(x_1, x_2, x_3)` трьох змінних із виводом у форматі JSON виконується команда:

```bash
tree-complexity-cli -n 3 -t 01010111 --format json
```

---

## 4. Схема даних JSON (Input & Output Contract)

При взаємодії через REST API або CLI з прапорцем `--format json` обмін даними здійснюється за строгим контрактом JSON-схеми. Це дозволяє легко обробляти результати у середовищах Python, JavaScript/TypeScript та Go.

### JSON-схема вихідних результатів (Output Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BooleanFunctionAnalysisResult",
  "type": "object",
  "properties": {
    "num_variables": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20
    },
    "metrics": {
      "type": "object",
      "properties": {
        "sensitivity": { "type": "integer" },
        "block_sensitivity": { "type": "integer" },
        "certificate_complexity": {
          "type": "object",
          "properties": {
            "c0": { "type": "integer" },
            "c1": { "type": "integer" },
            "total": { "type": "integer" }
          },
          "required": ["c0", "c1", "total"]
        },
        "degree": { "type": "integer" },
        "decision_tree_depth": { "type": "integer" }
      },
      "required": ["sensitivity", "block_sensitivity", "certificate_complexity", "degree", "decision_tree_depth"]
    },
    "theoretical_bounds": {
      "type": "object",
      "properties": {
        "huang_bound_satisfied": { "type": "boolean" },
        "nisan_bound_satisfied": { "type": "boolean" }
      }
    },
    "performance": {
      "type": "object",
      "properties": {
        "elapsed_ms": { "type": "number" },
        "nodes_evaluated": { "type": "integer" }
      }
    }
  },
  "required": ["num_variables", "metrics", "performance"]
}
```

### Приклад JSON-відповіді

```json
{
  "num_variables": 3,
  "metrics": {
    "sensitivity": 2,
    "block_sensitivity": 2,
    "certificate_complexity": {
      "c0": 2,
      "c1": 2,
      "total": 2
    },
    "degree": 3,
    "decision_tree_depth": 3
  },
  "theoretical_bounds": {
    "huang_bound_satisfied": true,
    "nisan_bound_satisfied": true
  },
  "performance": {
    "elapsed_ms": 0.142,
    "nodes_evaluated": 15
  }
}
```

---

## 5. Коди помилок та статусів виконання

Таблиця нижче містить вичерпний перелік кодів повернення C API та CLI, причин їхнього виникнення та рекомендацій щодо усунення помилок у клієнтському коді.

| Код помилки | Константа C API | Опис причини виникнення | Рекомендований спосіб усунення |
| :--- | :--- | :--- | :--- |
| `0` | `TC_SUCCESS` | Обчислення успішно завершено без помилок. | — |
| `-1` | `TC_ERR_INVALID_N` | Передано значення `n < 1` або `n > 20`. | Перевірте значення аргументу `num_vars`. |
| `-2` | `TC_ERR_NULL_POINTER` | Передано `NULL` вказівник на таблицю істинності. | Перевірте ініціалізацію вхідного буфера. |
| `-3` | `TC_ERR_TABLE_SIZE` | Довжина буфера не відповідає виразу `2ⁿ`. | Перевірте розмір масиву `truth_table`. |
| `-4` | `TC_ERR_OUT_OF_MEMORY` | Недостатньо пам'яті для мемоїзації станів. | Зменшіть `n` або обмежте використовувані метрики. |
| `-5` | `TC_ERR_TIMEOUT` | Перевищено максимально дозволений час обчислень. | Збільште таймаут у `AnalysisOptions`. |

---

## 6. Інтеграція з мовою Python (CFFI / ctypes)

Для зручності використання у наукових дослідженнях та дата-саєнс аналітиці C API обгорнуто в легковісну обгортку на мові Python із використанням модуля `ctypes`.

Вхідна таблиця істинності передається у вигляді байти-рядка `bytes` або масиву `numpy.ndarray` типу `uint8`. Власником пам'яті таблиці істинності залишається Python-інтерпретатор, тоді як C-бібліотека отримує вказівник на неперервний буфер у пам'яті (`C-contiguous array`).

У разі повернення коду помилки, відмінного від `TC_SUCCESS`, Python-обгортка перетворює результат на відповідний виняток `RuntimeError` або `ValueError` із повідомленням від `tc_error_string()`, що забезпечує ідіоматичну обробку помилок у середовищі Python.

Окрім прямого передавання масивів, CFFI забезпечує точне відтворення бінарного чуттєвого вирівнювання структур (`struct alignment`). Під час передавання структури `tc_result_t` між C-бібліотекою та інтерпретатором Python виключаються будь-які накладні витрати на маршалінг або копіювання полів: дані зчитуються безпосередньо з C-структури у пам'яті, гарантуючи нульові витрати часу на трансляцію типів.
