# 📋 Інтерфейс та API розв'язувача паросполучень

Ця вставка містить повну заголовну специфікацію та опис контракту програмного інтерфейсу (API) системної бібліотеки розв'язання задач досконалого та максимального паросполучення (`libmatching`). Специфікація деталізує структури даних, правила керування пам'яттю, обробку помилок, семантику потокобезпечності, C ABI сумісність та ідіоматичні C++ обгортки.

## 1. Архітектурні принципи та дизайн бібліотеки libmatching

Бібліотека `libmatching` розроблена як високоефективний системний модуль для обчислення максимальних та досконалих паросполучень у графах будь-якої топології. Модуль підтримує кілька ядер обчислень: детермінований алгоритм Едмондса (для довільних графів), спеціалізований алгоритм Хофкрофта-Карпа (для двочасткових графів) та алгебраїчний рандомізований тест Ловаса over finite fields.

### Ключові гарантії контракту API:

1. **Сувора ізоляція пам'яті та керування ресурсами:** Усі об'єкти графів та результатів обчислень створюються через явні фабричні функції. Бібліотека не здійснює неочевидних аллокацій у системній купі поза межами викликів конструювання. Вся пам'ять, виділена під результати, звільняється відповідними функціями-деструкторами.
2. **C ABI Сумісність:** Низькорівневий інтерфейс написаний на чистому C (стандарт C99) із збереженням стабільної бінарної сумісності (C ABI). Це дозволяє легко інтегрувати `libmatching` у мови високого рівня (Python через `ctypes`/`cffi`, Rust через FFI, Go через `cgo`, Java через JNI).
3. **Потокобезпечність (Thread-Safety & Reentrancy):** Об'єкти графа є моновласними та ненаправленими між потоками за замовчуванням. Проте виклики обчислення `matching_solve()` над різними екземплярами графів у різних потоках є повністю незалежними та реентабельними (reentrant), оскільки не використовують глобального або статичного стану.
4. **Семантика обробки помилок:** Системний C API повертає чисельний код помилки `matching_error_t` із передачею результату через вихідні вказівники. Високорівневий C++ API використовує сучасну семантику `std::expected` (C++23) для явно відстежуваної обробки помилок без викидання винятків.

---

## 2. Заголовний файл C API (`matching_solver.h`)

Нижче наведено повний заголовний файл низькорівневого інтерфейсу `matching_solver.h`.

:::tabs
```c
#ifndef MATCHING_SOLVER_H
#define MATCHING_SOLVER_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди помилок та станів виконання розв'язувача паросполучень.
 */
typedef enum {
    MATCHING_SUCCESS = 0,             /**< Операція виконана успішно */
    MATCHING_ERR_NULL_POINTER = -1,   /**< Передано нульовий вказівник у якості аргумента */
    MATCHING_ERR_INVALID_VERTEX = -2, /**< Індекс вершини виходить за дозволені межі [0, V-1] */
    MATCHING_ERR_OUT_OF_MEMORY = -3,  /**< Не вдалося виділити пам'ять у системній купі */
    MATCHING_ERR_NOT_BIPARTITE = -4,  /**< Вхідний граф не є двочастковим (для алгоритму Хофкрофта-Карпа) */
    MATCHING_ERR_ALGORITHM_FAIL = -5 /**< Внутрішній обчислювальний збій розв'язувача */
} matching_error_t;

/**
 * @brief Перелік алгоритмів розв'язання задачі паросполучення.
 */
typedef enum {
    MATCHING_ALG_EDMONDS_BLOSSOM = 0, /**< Детермінований алгоритм Едмондса для загальних графів (O(V²E)) */
    MATCHING_ALG_HOPCROFT_KARP = 1,   /**< Алгоритм Хофкрофта-Карпа для двочасткових графів (O(E√V)) */
    MATCHING_ALG_LOVASZ_RANDOM = 2    /**< Рандомізований алгебраїчний тест матриці Тутте (O(nʷ)) */
} matching_algorithm_t;

/**
 * @brief Структура, що описує окреме ребро у паросполученні.
 */
typedef struct {
    int32_t u; /**< Початкова вершина ребра */
    int32_t v; /**< Кінцева вершина ребра */
} matching_edge_t;

/**
 * @brief Результат обчислення паросполучення.
 */
typedef struct {
    int32_t matching_size;      /**< Загальна кількість ребер у максимальному паросполученні */
    bool is_perfect;            /**< Чи є паросполучення досконалим (покриває всі V вершин) */
    matching_edge_t* edges;     /**< Динамічний масив ребер паросполучення */
    size_t num_edges;           /**< Кількість елементів у масиві edges */
} matching_result_t;

/**
 * @brief Непрозорий тип (opaque handle) графа.
 */
typedef struct matching_graph matching_graph_t;

/**
 * @brief Створити екземпляр графа з заданою кількістю вершин.
 * @param num_vertices Кількість вершин у графі (повинна бути > 0)
 * @param out_graph Вихідний вказівник на створений об'єкт графа
 * @return MATCHING_SUCCESS у разі успіху або відповідний код помилки
 */
matching_error_t matching_graph_create(int32_t num_vertices, matching_graph_t** out_graph);

/**
 * @brief Знищити граф та звільнити всі пов'язані з ним ресурси.
 * @param graph Об'єкт графа для знищення (безпечно передавати NULL)
 */
void matching_graph_destroy(matching_graph_t* graph);

/**
 * @brief Додати неороієнтоване ребро між вершинами u та v.
 * @param graph Об'єкт графа
 * @param u Індекс першої вершини (0 <= u < V)
 * @param v Індекс другої вершини (0 <= v < V)
 * @return MATCHING_SUCCESS або код помилки MATCHING_ERR_INVALID_VERTEX
 */
matching_error_t matching_graph_add_edge(matching_graph_t* graph, int32_t u, int32_t v);

/**
 * @brief Обчислити паросполучення обраним алгоритмом.
 * @param graph Об'єкт графа
 * @param algorithm Алгоритм для обчислення
 * @param out_result Вихідна структура для збереження результату
 * @return MATCHING_SUCCESS або код помилки
 */
matching_error_t matching_solve(const matching_graph_t* graph,
                                 matching_algorithm_t algorithm,
                                 matching_result_t* out_result);

/**
 * @brief Звільнити пам'ять масиву ребер у структурі результату.
 * @param result Результат обчислення для очищення
 */
void matching_result_free(matching_result_t* result);

#ifdef __cplusplus
}
#endif

#endif /* MATCHING_SOLVER_H */
```
```cpp
#ifndef MATCHING_SOLVER_HPP
#define MATCHING_SOLVER_HPP

#include <vector>
#include <utility>
#include <cstdint>
#include <memory>
#include <system_error>
#include <expected>

namespace graph::matching {

enum class Algorithm {
    EdmondsBlossom, /**< General graph Edmonds Blossom algorithm O(V²E) */
    HopcroftKarp,   /**< Bipartite graph Hopcroft-Karp algorithm O(E√V) */
    LovaszRandom    /**< Algebraic randomized Tutte matrix determinant test O(nʷ) */
};

enum class ErrorCode {
    InvalidVertex = 1,
    NullPointer,
    OutOfMemory,
    NotBipartite,
    AlgorithmFailure
};

struct Edge {
    int32_t u;
    int32_t v;

    bool operator==(const Edge& other) const noexcept {
        return (u == other.u && v == other.v) || (u == other.v && v == other.u);
    }
};

struct MatchingResult {
    int32_t size{0};
    bool is_perfect{false};
    std::vector<Edge> edges;
};

class Graph {
public:
    explicit Graph(int32_t num_vertices);
    ~Graph();

    Graph(const Graph&) = delete;
    Graph& operator=(const Graph&) = delete;

    Graph(Graph&&) noexcept;
    Graph& operator=(Graph&&) noexcept;

    [[nodiscard]] int32_t num_vertices() const noexcept;
    
    std::expected<void, ErrorCode> add_edge(int32_t u, int32_t v);

    [[nodiscard]] std::expected<MatchingResult, ErrorCode> solve(
        Algorithm algo = Algorithm::EdmondsBlossom) const;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph::matching

#endif /* MATCHING_SOLVER_HPP */
```
:::

---

## 3. Докладна специфікація функцій та системна поведінка C API

У цьому розділі наведено покроковий опис кожної функції низькорівневого C API, правила передачі аргументів, внутрішні стани обробки даних та гарантії обробки помилок.

### 3.1. Ініціалізація та знищення графа (`matching_graph_create` та `matching_graph_destroy`)

Функція `matching_graph_create` відповідає за первинне створення внутрішньої структури графа у системній купі.

```c
matching_error_t matching_graph_create(int32_t num_vertices, matching_graph_t** out_graph);
```

- **Призначення:** Конструює об'єкт графа з заданою фіксованою кількістю вершин `num_vertices`. Внутрішньо ініціалізуються списки суміжності для кожної вершини у формі динамічних масивів або розрідженої структури CSR (Compressed Sparse Row).
- **Вхідні параметри:**
  - `num_vertices`: Кількість вершин графа. Значення має задовольняти умові `num_vertices > 0`. Передача від'ємного значення або нуля повертає код помилки `MATCHING_ERR_INVALID_VERTEX`.
  - `out_graph`: Вказівник на змінну-вказівник `matching_graph_t*`. Передача `NULL` спричиняє негайне повернення `MATCHING_ERR_NULL_POINTER`.
- **Повертане значення:** `MATCHING_SUCCESS` у разі успішного конструювання. Якщо не вдалося виділити пам'ять під масиви суміжності, повертається `MATCHING_ERR_OUT_OF_MEMORY`, а `*out_graph` встановлюється у `NULL`.
- **Правила очищення:** Кожен успішно створений граф має бути знищений за допомогою функції `matching_graph_destroy(graph)`. Викликати `matching_graph_destroy(NULL)` є безпечним і не викликає невизначеної поведінки (no-op).

### 3.2. Модифікація топології (`matching_graph_add_edge`)

Додавання ребер здійснюється послідовно через виклики функції `matching_graph_add_edge`.

```c
matching_error_t matching_graph_add_edge(matching_graph_t* graph, int32_t u, int32_t v);
```

- **Призначення:** Додає неороієнтоване ребро між вершиною `u` та вершиною `v`. Оскільки граф є симетричним та неорієнтованим, ребро реєструється як у списку суміжності вершини `u`, так і у списку суміжності вершини `v`.
- **Перевірка індексів:** Функція перевіряє, щоб обидва індекси задовольняли умові `0 <= u < V` та `0 <= v < V`. Якщо хоча б один індекс виходить за межі діапазону, додавання скасовується, а функція повертає `MATCHING_ERR_INVALID_VERTEX`.
- **Обробка мультитегів та петель:** Петлі (`u == v`) автоматично відсікаються, оскільки самопетля не може входити до жодного паросполучення. Повторні ребра між тими самими вершинами (мультиребра) ігноруються, або зберігаються в одному примірнику.

### 3.3. Виконання розв'язання (`matching_solve`)

Головна обчислювальна функція бібліотеки.

```c
matching_error_t matching_solve(const matching_graph_t* graph,
                                 matching_algorithm_t algorithm,
                                 matching_result_t* out_result);
```

- **Призначення:** Запускає обране ядро розв'язання (`EDMONDS_BLOSSOM`, `HOPCROFT_KARP` або `LOVASZ_RANDOM`) над топологією графа `graph`.
- **Обробка результатів:** У разі успішного завершення функція ініціалізує структуру `out_result`:
  - `matching_size`: кількість знайдених взаємно-диз'юнктних ребер;
  - `is_perfect`: булевий прапорець `true`, якщо `matching_size == V / 2`;
  - `edges`: динамічний масив точних пар `matching_edge_t`, виділений у купі;
  - `num_edges`: кількість елементів у масиві `edges`.
- **Спеціальні умови для алгоритму Хофкрофта-Карпа:** Якщо обрано `MATCHING_ALG_HOPCROFT_KARP`, але вхідний граф містить принаймні один непарний цикл (не є двочастковим), обчислення переривається, а функція повертає код `MATCHING_ERR_NOT_BIPARTITE`.

### 3.4. Звільнення результатів (`matching_result_free`)

```c
void matching_result_free(matching_result_t* result);
```

- **Призначення:** Звільняє динамічний масив `result->edges`, виділений під час виконання `matching_solve()`, та скидає лічильники `num_edges` та `matching_size` до 0.
- **Обов'язковість:** Клієнтський код зобов'язаний викликати цю функцію для кожного результату, отриманого після успішного виконання `matching_solve()`.

---

## 4. Високорівнева C++ обгортка (`graph::matching::Graph`)

Високорівневий C++ API побудовано за принципом RAII (Resource Acquisition Is Initialization), унеможливлюючи витоки ресурсів та пропущені виклики деструкторів.

### Особливості семантики C++ API:

1. **Заборона копіювання (Non-copyable):** Клас `Graph` забороняє операції копіювання (`Graph(const Graph&) = delete`), оскільки володіє унікальним системним ресурсом графа.
2. **Підтримка переміщення (Movable):** Переміщення об'єктів (`Graph(Graph&&) noexcept`) дозволено і виконується за сталий час `O(1)` шляхом передачі внутрішнього вказівника `impl_`.
3. **Обробка помилок через `std::expected`:** Функція `solve()` повертає `std::expected<MatchingResult, ErrorCode>`. Клієнтський код перевіряє наявність значення за допомогою `result.has_value()` чи синтаксису monadic operations (`.and_then()`, `.transform()`).

```cpp
// Приклад використання C++ API
#include "matching_solver.hpp"
#include <iostream>

int main() {
    using namespace graph::matching;

    Graph g(6); // Створення графа на 6 вершин
    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 4);
    g.add_edge(4, 5);
    g.add_edge(5, 0);

    auto result = g.solve(Algorithm::EdmondsBlossom);
    if (result) {
        std::cout << "Паросполучення знайдено! Розмір: " << result->size << "\n";
        std::cout << "Досконале: " << (result->is_perfect ? "Так" : "Ні") << "\n";
        for (const auto& edge : result->edges) {
            std::cout << "Ребро: (" << edge.u << ", " << edge.v << ")\n";
        }
    } else {
        std::cerr << "Помилка обчислення паросполучення!\n";
    }
    return 0;
}
```

---

## 5. Таблиця конфігурації та параметрів виконання

Параметри виконання розв'язувача конфігуруються залежно від специфіки вхідних даних та вимог до швидкодії.

| Параметр конфігурації | Опис | За замовчуванням | Область допустимих значень |
| :--- | :--- | :--- | :--- |
| `matching_algorithm` | Обчислювальний модуль розв'язувача | `MATCHING_ALG_EDMONDS_BLOSSOM` | Enum `matching_algorithm_t` |
| `lovasz_field_modulus` | Модуль скінченного поля `F_p` для тесту Ловаса | `2¹²8 + 51` (просте число) | Прості числа `p > 2n` |
| `bipartite_auto_check` | Автоматична перевірка графа на двочастковість | `true` | `true` / `false` |
| `max_blossom_contractions` | Гранична кількість стискання квіток | `V` | `1 .. V` |

---

## 6. Профіль продуктивності та гарантії обчислювальної складності

1. **Алгоритм Едмондса (`MATCHING_ALG_EDMONDS_BLOSSOM`):**
   - **Часова складність:** `O(V² · E)` на загальних графах.
   - **Просторова складність:** `O(V + E)` додаткової пам'яті під відстеження баз квіток.
   - **Гарантії:** Детермінований 100% точний результат для графів довільної топології.
2. **Алгоритм Хофкрофта-Карпа (`MATCHING_ALG_HOPCROFT_KARP`):**
   - **Часова складність:** `O(E · √V)` для двочасткових графів.
   - **Просторова складність:** `O(V + E)`.
   - **Гарантії:** Оптимальний детермінований результат. Повертає `MATCHING_ERR_NOT_BIPARTITE`, якщо вхідний граф містить непарні цикли.
3. **Рандомізований тест Ловаса (`MATCHING_ALG_LOVASZ_RANDOM`):**
   - **Часова складність:** `O(nʷ)` (практична складність Гаусса `O(n³)`).
   - **Просторова складність:** `O(V²)` для зберігання щільної кососиметричної матриці Тутте.
   - **Гарантії:** Імовірність фальшиво-негативної помилки обмежена `P(err) ≤ n / p`.

Інтерфейс бібліотеки `libmatching` забезпечує оптимальне поєднання надійності, C ABI сумісності та сучасних стандартів мови C++, роблячи її універсальним інструментом для задач комбінаторної оптимізації.
