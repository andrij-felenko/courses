# 📋 Інтерфейс та специфікація бібліотеки аналізу графа Рамсея

Цей документ містить повну специфікацію програмувального інтерфейсу (API) та консольного інструменту (CLI) бібліотеки `libramsey`, призначеної для програмної побудови, перевірки, серіалізації та аналізу розмальовок графів Рамсея у C та C++ додатках.

Бібліотека розроблена за принципами низькопакетної обчислювальної ефективності, нульової вартості абстракцій (Zero-cost Abstractions) та високої потокобезпеки. Вона надає мовні зв'язки для класичного C (стандарти C99/C11) та сучасного C++20, а також уніфіковану утиліту командного рядка для автоматизації обчислювальних експериментів у кластерних середовищах та інтеграції з автоматичними розв'язувачами задач виконуваності булевих формул (SAT-соловерами).

## 1. Специфікація заголовних файлів та інтерфейсів (API Header Reference)

C-інтерфейс та C++20 інтерфейс розроблені відповідно до суворих стандартів безпосереднього володіння пам'яттю, явними кодами повернення помилок та відсутністю невизначеної поведінки при передачі некоректних вхідних даних. Усі функції та класи перевіряють вхідні вказівники на `NULL` та дотримання допустимих меж для індексів вершин графа.

### Архітектура структур даних
Головною базовою структурою даних є матриця суміжності, яка зберігає розмірність графа `num_vertices` та динамічно виділений масив 64-бітних цілочисельних масок. Кожен елемент маски являє собою 64-бітне ціле число, у якому `j`-й біт вказує колір ребра між вершинами `i` та `j`. Значення біта `1` відповідає червоному кольору, а `0` — синьому кольору. Оскільки будь-яке ребро графа є ненапрямленим, при встановленні кольору ребра `(u, v)` бібліотека синхронно змінює відповідні біти у рядках `u` та `v`.

Така компактна бітова бінарна організація забезпечує мінімальне оперативне навантаження: граф розміром до 64 вершин займає у пам'яті лише 512 байт. Це гарантує, що вся колірна матриця повністю вміщується у швидкісний кеш процесора першого рівня (L1 Data Cache), виключаючи промихи кешу (cache misses) під час виконання мільйонів рекурсивних перевірок на секунду.

:::tabs
```c
/* ramsey.h - ANSI C99/C11 API Interface */
#ifndef LIBRAMSEY_H
#define LIBRAMSEY_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    RAMSEY_SUCCESS             =  0,
    RAMSEY_ERROR_INVALID_PARAM = -1,
    RAMSEY_ERROR_NO_MEMORY     = -2,
    RAMSEY_ERROR_OVERFLOW      = -3,
    RAMSEY_ERROR_TIMEOUT       = -4,
    RAMSEY_ERROR_IO            = -5
} ramsey_status_t;

/* Структура представлення двокольорового графа Рамсея */
typedef struct {
    size_t num_vertices;     /* Кількість вершин n (1 <= n <= 64) */
    uint64_t *adj_matrix;    /* Динамічний масив бітових масок (розмір n) */
} ramsey_graph_t;

/* Результат аналізу монохроматичних підграфів */
typedef struct {
    bool has_monochromatic_clique;  /* true, якщо знайдено кліку K_r або K_s */
    size_t found_clique_size;       /* Розмір знайденої кліки */
    bool is_red_clique;             /* true для червоного кольору, false для синього */
    uint64_t clique_mask;           /* Бітова маска вершин, що утворюють кліку */
} ramsey_clique_result_t;

/* Створення та знищення графа */
ramsey_status_t ramsey_graph_create(ramsey_graph_t **graph, size_t n);
void ramsey_graph_destroy(ramsey_graph_t *graph);

/* Маніпуляції з ребрами */
ramsey_status_t ramsey_graph_set_edge(ramsey_graph_t *graph, size_t u, size_t v, bool is_red);
ramsey_status_t ramsey_graph_get_edge(const ramsey_graph_t *graph, size_t u, size_t v, bool *out_is_red);

/* Перевірка та пошук клік */
ramsey_status_t ramsey_graph_check_clique(const ramsey_graph_t *graph, size_t r, size_t s, ramsey_clique_result_t *result);
ramsey_status_t ramsey_find_counterexample(ramsey_graph_t *out_graph, size_t n, size_t r, size_t s, uint32_t timeout_sec);

/* Серіалізація та експорт */
ramsey_status_t ramsey_graph_export_json(const ramsey_graph_t *graph, const char *filepath);
ramsey_status_t ramsey_graph_import_json(ramsey_graph_t **out_graph, const char *filepath);
ramsey_status_t ramsey_graph_export_dimacs(const ramsey_graph_t *graph, const char *filepath);

#ifdef __cplusplus
}
#endif

#endif /* LIBRAMSEY_H */
```
```cpp
// ramsey.hpp - C++20 Modern Object-Oriented API Interface
#ifndef LIBRAMSEY_HPP
#define LIBRAMSEY_HPP

#include <vector>
#include <optional>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <span>
#include <filesystem>
#include <chrono>

namespace ramsey {

enum class error_code {
    invalid_argument = 1,
    out_of_memory,
    search_timeout,
    file_io_error
};

class graph_color_matrix {
public:
    explicit graph_color_matrix(std::size_t num_vertices);
    ~graph_color_matrix() = default;

    graph_color_matrix(const graph_color_matrix&) = default;
    graph_color_matrix& operator=(const graph_color_matrix&) = default;
    graph_color_matrix(graph_color_matrix&&) noexcept = default;
    graph_color_matrix& operator=(graph_color_matrix&&) noexcept = default;

    [[nodiscard]] std::size_t vertices_count() const noexcept;
    
    void set_edge(std::size_t u, std::size_t v, bool is_red);
    [[nodiscard]] bool is_red_edge(std::size_t u, std::size_t v) const;

    [[nodiscard]] std::uint64_t get_row_mask(std::size_t v) const;

    void export_json(const std::filesystem::path& path) const;
    static graph_color_matrix import_json(const std::filesystem::path& path);

private:
    std::size_t num_vertices_;
    std::vector<std::uint64_t> adj_matrix_;
};

struct clique_search_result {
    bool has_monochromatic_clique{false};
    std::size_t clique_size{0};
    bool is_red{false};
    std::vector<std::size_t> clique_vertices;
};

class ramsey_analyzer {
public:
    explicit ramsey_analyzer(std::size_t r, std::size_t s);

    [[nodiscard]] clique_search_result analyze(const graph_color_matrix& graph) const;
    
    [[nodiscard]] std::optional<graph_color_matrix> find_counterexample(
        std::size_t num_vertices, 
        std::chrono::seconds timeout = std::chrono::seconds(60)
    ) const;

private:
    std::size_t r_;
    std::size_t s_;
};

} // namespace ramsey

#endif // LIBRAMSEY_HPP
```
:::

### Детальний регламент та контракт функцій API

#### 1. Створення графа
- **C API**: `ramsey_graph_create(ramsey_graph_t **graph, size_t n)` — Динамічно виділяє пам'ять у купі (heap) для структури `ramsey_graph_t` та внутрішнього масиву бітових масок для графа на `n` вершин. При успіху повертає `RAMSEY_SUCCESS`, при виході `n` за межі `[1, 64]` повертає `RAMSEY_ERROR_INVALID_PARAM`, а у разі збою виділення купі — `RAMSEY_ERROR_NO_MEMORY`.
- **C++ API**: `ramsey::graph_color_matrix g(n)` — Конструктор автоматично керує пам'яттю через `std::vector<std::uint64_t>`. При некоректних параметрах генерується виняток `std::invalid_argument`.

#### 2. Знищення графа
- **C API**: `ramsey_graph_destroy(ramsey_graph_t *graph)` — Звільняє динамічну пам'ять масиву `adj_matrix` та саму структуру `ramsey_graph_t`. Безпечно обробляє `NULL`.
- **C++ API**: Автоматичний деструктор RAII при виході об'єкта з області видимості.

#### 3. Модифікація кольору ребра
- **C API**: `ramsey_graph_set_edge(ramsey_graph_t *graph, size_t u, size_t v, bool is_red)` — Встановлює колір ненапрямленого ребра між вершинами `u` та `v`. Перевіряє умови `u != v` та межі `u, v < n`.
- **C++ API**: `g.set_edge(u, v, is_red)` — Встановлює колір ребра із перевіркою меж та викликом винятку `std::out_of_range` при порушенні індексації.

#### 4. Перевірка наявних монохроматичних підграфів
- **C API**: `ramsey_graph_check_clique(const ramsey_graph_t *graph, size_t r, size_t s, ramsey_clique_result_t *result)` — Запускає оптимізований рекурсивний пошук клік. Записує детальні результати в структуру `result` (знайдений розмір, прапорець кольору та бітову маску вершин кліки).
- **C++ API**: `analyzer.analyze(graph)` — Константний потокобезпечний метод, що повертає структуру `ramsey::clique_search_result`.

#### 5. Серіалізація та імпорт у форматі DIMACS та JSON
- **C API**: `ramsey_graph_export_json` та `ramsey_graph_export_dimacs` записують граф у файлову систему. При виникненні помилок введення-виведення повертають `RAMSEY_ERROR_IO`.
- **C++ API**: Методи `g.export_json(path)` та `graph_color_matrix::import_json(path)` обробляють файли через бінарні потоки та `std::filesystem::path`.

### Політика обробки помилок та повернення кодів
C-функції повертають статус `ramsey_status_t`, а C++ API використовує винятки або `std::optional`. Приклад використання:

:::tabs
```c
ramsey_graph_t *g = NULL;
ramsey_status_t status = ramsey_graph_create(&g, 6);
if (status != RAMSEY_SUCCESS) {
    fprintf(stderr, "Помилка створення графа: %d\n", status);
    return status;
}
```
```cpp
try {
    ramsey::graph_color_matrix g(6);
} catch (const std::exception& e) {
    std::cerr << "Помилка створення графа: " << e.what() << '\n';
    return -1;
}
```
:::

### Таблиця методів API

| Функція / Метод | Опис | C повертане значення | C++ повертане значення | Складність |
| :--- | :--- | :--- | :--- | :--- |
| `create / constructor` | Виділяє пам'ять під граф на `n` вершин | `RAMSEY_SUCCESS` | Об'єкт графа | `O(n)` |
| `destroy / destructor` | Звільняє динамічну пам'ять графа | `void` | Автоматично RAII | `O(1)` |
| `set_edge` | Встановлює колір ребра між `u` та `v` | `RAMSEY_SUCCESS` | `void` | `O(1)` |
| `get_edge / is_red_edge` | Зчитує колір ребра між `u` та `v` | `RAMSEY_SUCCESS` | `bool` | `O(1)` |
| `check_clique / analyze` | Шукає монохроматичну кліку `Kᵣ` або `K⛛` | `RAMSEY_SUCCESS` | `clique_search_result` | `O(2ⁿ)` найгірша |
| `find_counterexample` | Шукає контрприклад `R(r,s) > n` | `RAMSEY_SUCCESS` | `std::optional<...>` | Експоненціальна |
| `export_json` | Зберігає граф у файловій системі у JSON | `RAMSEY_SUCCESS` | `void` | `O(n)` |
| `import_json` | Зчитує граф із файлу JSON | `RAMSEY_SUCCESS` | `graph_color_matrix` | `O(n)` |

---

## 2. Специфікація консольного інструменту (CLI Interface)

Консольна утиліта `ramsey-cli` призначена для запуску масових обчислювальних експериментів, аналізу графів із файлів та пошуку контрприкладів безпосередньо з командного рядка у конвеєрах Unix/Linux та Windows PowerShell. Вона підтримує обробку стандартних потоків `stdin`/`stdout`, що дозволяє вбудовувати її у скрипти bash та автоматизовані середовища CI/CD.

### Синтаксис виклику
```bash
ramsey-cli --mode=<check|search|info> --vertices=<N> -r=<R> -s=<S> [options]
```

### Таблиця консольних прапорців

| Прапорець | Короткий аналог | Тип | Опис | Значення за замовчуванням |
| :--- | :--- | :--- | :--- | :--- |
| `--mode` | `-m` | String | Режим роботи: `check` (перевірка файлу), `search` (пошук контрприкладу) | `search` |
| `--vertices` | `-n` | Integer | Кількість вершин графа `n` | `6` |
| `-r` | `-r` | Integer | Розмір червоної кліки `r` | `3` |
| `-s` | `-s` | Integer | Розмір синьої кліки `s` | `3` |
| `--input` | `-i` | Path | Шлях до вхідного JSON/DIMACS файлу графа | `""` |
| `--output` | `-o` | Path | Шлях до файлу збереження результату | `""` |
| `--timeout` | `-t` | Integer | Ліміт часу пошуку у секундах | `60` |
| `--threads` | `-j` | Integer | Кількість паралельних потоків обчислення | `4` |

### Приклади використання CLI

1. **Пошук контрприкладу для R(3, 4) на n = 8 вершин**:
```bash
ramsey-cli --mode=search -n 8 -r 3 -s 4 --output=r34_n8.json --threads=8
```
*Вихід у консоль*:
```
[INFO] Ініціалізація пошуку контрприкладу для R(3, 4) на n = 8 вершин.
[INFO] Кількість ребер: 28. Простір пошуку: 2^28 = 268,435,456 варіантів.
[SUCCESS] Знайдено контрприклад за 0.042 сек!
[SUCCESS] Граф без червоного K_3 та синього K_4 збережено у r34_n8.json.
[RESULT] Доведено: R(3, 4) > 8.
```

2. **Перевірка доказу R(3, 3) = 6**:
```bash
ramsey-cli --mode=search -n 6 -r 3 -s 3
```
*Вихід у консоль*:
```
[INFO] Ініціалізація пошуку контрприкладу для R(3, 3) на n = 6 вершин.
[INFO] Повний обхід 32,768 конфігурацій завершено за 0.003 сек.
[RESULT] Контрприкладу НЕ знайдено. Будь-яке розфарбування K_6 містить K_3.
[RESULT] Підтверджено математичну межу: R(3, 3) <= 6.
```

---

## 3. Формати серіалізації даних

Бібліотека `libramsey` підтримує серіалізацію графів у стандартний формат JSON та формат DIMACS CNF для взаємодії з зовнішніми SAT-соловерами.

### Специфікація JSON Схеми (`ramsey_graph_spec.json`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RamseyGraphColoring",
  "type": "object",
  "properties": {
    "num_vertices": {
      "type": "integer",
      "minimum": 1,
      "maximum": 64
    },
    "parameters": {
      "type": "object",
      "properties": {
        "r": { "type": "integer" },
        "s": { "type": "integer" }
      }
    },
    "adjacency_masks": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["num_vertices", "adjacency_masks"]
}
```

### Приклад збереженого графа контрприкладу R(3, 3) > 5 (JSON)
```json
{
  "num_vertices": 5,
  "parameters": {
    "r": 3,
    "s": 3
  },
  "adjacency_masks": [
    "0x000000000000000A",
    "0x0000000000000014",
    "0x0000000000000009",
    "0x0000000000000012",
    "0x0000000000000005"
  ]
}
```

---

## 4. Потокобезпека, інтеграція та побудова проектів

1. **Володіння пам'яттю (Memory Ownership)**: Функція `ramsey_graph_create` динамічно виділяє пам'ять у купі, яка має бути обов'язково звільнена викликом `ramsey_graph_destroy`. У C++20 версії володіння ресурсами повністю автоматизовано за допомогою стандартних семантик RAII.
2. **Потокобезпека константних методів (Thread Safety)**: Усі константні класи та функції аналізу (`analyze`, `check_clique`, `is_red_edge`) є повністю потокобезпечними. Кілька потоків обробки можуть одночасно читати той самий об'єкт графа без використання м'ютексів чи блокувань.
3. **Паралельне виконання (Multi-threading)**: При запуск розв'язувача з прапорцем `--threads=J` простір пошуку розбігається на `2^J` незалежних піддерев. Кожен робочий потік отримує власну копію `graph_color_matrix`, що виключає стани перегонів (race conditions).
4. **Обробка винятків та системних помилок**: C++ API гарантує безпеку відносно винятків (Strong Exception Guarantee). У разі помилок виділення пам'яті або збоїв файлового введення-виведення стан об'єктів залишається узгодженим.
5. **Інтеграція з CMake**: Бібліотека `libramsey` надає готові конфігураційні файли CMake. Додавання бібліотеки у зовнішні проекти здійснюється через стандартну команду:

```cmake
find_package(libramsey REQUIRED)
target_link_libraries(my_ramsey_project PRIVATE libramsey::ramsey)
```
