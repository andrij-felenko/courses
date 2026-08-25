# 📋 Специфікація інтерфейсу солвера гамільтонових циклів

Програмний контракт обчислювальної бібліотеки `libhamiltonian` визначає публічні структури даних, енумератори статусів, конфігураційні параметри та функції C/C++ API для пошуку гамільтонових шляхів і циклів у графів різної розмірності та щільності.

---

## 1. Загальний огляд архітектури інтерфейсу

Бібліотека `libhamiltonian` надає уніфікований, потокобезпечний C/C++ інтерфейс для розв'язання NP-повної задачі гамільтонового циклу. Архітектура бібліотеки розділена на три незалежні шари:

1. **Шар подання графів (Graph Representation Layer):** Забезпечує збереження топології неупорядкованого або орієнтованого графа у вигляді компактної матриці суміжності з бітовим пакуванням або векторного списку суміжності. Для малогабаритних графів (`n ≤ 32`) використовується пласка матриця байтів з вирівнюванням під кеш-лінії CPU (64 байти).
2. **Шар прийняття рішень та оптимізацій (Strategy Layer):** Автоматично аналізує параметри графа — розмірність `n`, кількість ребер `m` та щільність `d = 2m / (n(n-1))` — для вибору оптимального алгоритмічного двигуна.
3. **Обчислювальні двигуни (Execution Engines):**
   - **Двигун Backtracking (`HAMILTONIAN_ALGO_BACKTRACK`):** Оптимізований рекурсивний DFS із евристикою Варнсдорфа та динамічним відсіканням тупиків. Використовується за замовчуванням для розріджених графів (`d < 0.3`) великої розмірності (`n ≤ 64`).
   - **Двигун Held-Karp (`HAMILTONIAN_ALGO_HELD_KARP`):** Точне динамічне програмування з бітовими масками (`O(2ⁿ · n²)`). Використовується для щільних графів (`d ≥ 0.3`) середньої розмірності (`n ≤ 31`).
   - **Двигун SAT-редукції (`HAMILTONIAN_ALGO_SAT_REDUCE`):** Транслятор топології у формулу КНФ формату DIMACS для передачі зовнішнім CDCL SAT-солверам у високонавантажених прикладних задачах (`n > 64`).

---

## 2. Коди повернення та статус виконання (`hamiltonian_status_t` / `Status`)

Усі функції C-інтерфейсу та методи C++ класи обчислювального солвера повертають єдиний перелічуваний код статусу. Значення `>= 0` позначають успішне або завершене обчислення, а значення `< 0` вказують на критичні помилки виклику або обчислювальних ресурсів.

:::tabs
```c
typedef enum {
    HAMILTONIAN_SUCCESS            =  0,  /* Гамільтонів цикл знайдено успішно */
    HAMILTONIAN_NO_CYCLE_EXISTS    =  1,  /* Доведено відсутність циклу у графі */
    HAMILTONIAN_ERROR_NULL_POINTER = -1,  /* Передано невалідний вказівник NULL */
    HAMILTONIAN_ERROR_INVALID_SIZE = -2,  /* Некоректна кількість вершин (n < 3 або n > MAX) */
    HAMILTONIAN_ERROR_OUT_OF_MEMORY= -3,  /* Нестача оперативної пам'яті для масиву станів */
    HAMILTONIAN_ERROR_TIMEOUT      = -4,  /* Перевищено ліміт часу виконання (timeout_ms) */
    HAMILTONIAN_ERROR_CANCELED     = -5   /* Виконання скасовано за запитом користувача */
} hamiltonian_status_t;
```
```cpp
namespace hamiltonian {

enum class Status : int32_t {
    Success           =  0,  // Гамільтонів цикл знайдено успішно
    NoCycleExists     =  1,  // Доведено відсутність циклу у графі
    ErrorNullPointer  = -1,  // Передано невалідний вказівник nullptr
    ErrorInvalidSize  = -2,  // Некоректна кількість вершин
    ErrorOutOfMemory  = -3,  // Нестача оперативної пам'яті
    ErrorTimeout      = -4,  // Перевищено ліміт часу виконання
    ErrorCanceled     = -5   // Виконання скасовано за запитом
};

} // namespace hamiltonian
```
:::

### Деталізація семантики кодів статусу та обробка помилок

- `HAMILTONIAN_SUCCESS (0)`: Алгоритм знайшов замкнений гамільтонів цикл. Послідовність вершин записано у динамічний масив результату `path`, а довжина шляху `path_length` дорівнює `n`. Перша та остання вершини масиву з'єднані ребом у вихідному графі.
- `HAMILTONIAN_NO_CYCLE_EXISTS (1)`: Дослідження всього простору станів строго довело, що вихідний граф не містить жодного гамільтонового циклу. Масив `path` у цьому випадку дорівнює `NULL` / порожній, а `path_length` дорівнює 0.
- `HAMILTONIAN_ERROR_NULL_POINTER (-1)`: Спроба передати `NULL` або незаніціалізований вказівник на граф чи конфігурацію у будь-яку з функцій API. Функція негайно повертає цей код без модифікації стану системи.
- `HAMILTONIAN_ERROR_INVALID_SIZE (-2)`: Виклик функції для графа з `n < 3` (де гамільтонів цикл не існує за визначенням) або `n > 31` при спробі вручну обрати алгоритм Гелда-Карпа.
- `HAMILTONIAN_ERROR_OUT_OF_MEMORY (-3)`: Спроба виділення динамічної пам'яті під `dp`-таблицю розміром `2ⁿ × n` елементів завершилася невдачею системного виклику `malloc()`. Усі раніше виділені проміжні ресурси гарантовано звільняються.
- `HAMILTONIAN_ERROR_TIMEOUT (-4)`: Час обчислення перевищив поріг `timeout_ms`, заданий у конфігурації. Солвер перериває подальший перебір та повертає частково зібрану статистику обчислених станів.
- `HAMILTONIAN_ERROR_CANCELED (-5)`: Виконання було примусово перервано з іншого потоку через виклик процедури скасування або зворотного виклику (callback).

---

## 3. Перелічуваний тип алгоритмів (`hamiltonian_algo_t` / `Algorithm`)

Перелічуваний тип `hamiltonian_algo_t` дозволяє користувачеві примусово зафіксувати алгоритмічний двигун або надає бібліотеці право автоматичного вибору.

:::tabs
```c
typedef enum {
    HAMILTONIAN_ALGO_AUTO       = 0,  /* Автоматичний вибір двигуна за розмірністю та щільністю */
    HAMILTONIAN_ALGO_BACKTRACK  = 1,  /* Точний пошук у глибину з евристичним відсіканням */
    HAMILTONIAN_ALGO_HELD_KARP  = 2,  /* Динамічне програмування з бітовими масками */
    HAMILTONIAN_ALGO_SAT_REDUCE = 3   /* Звідність до 3SAT та виклик SAT-солвера */
} hamiltonian_algo_t;
```
```cpp
namespace hamiltonian {

enum class Algorithm : uint8_t {
    Auto      = 0,  // Автоматичний вибір двигуна
    Backtrack = 1,  // Точний пошук у глибину з відсіканням
    HeldKarp  = 2,  // Динамічне програмування з бітовими масками
    SatReduce = 3   // Звідність до 3SAT та виклик SAT-солвера
};

} // namespace hamiltonian
```
:::

---

## 4. Структура конфігурації солвера (`hamiltonian_config_t` / `Config`)

Структура `hamiltonian_config_t` задає робочі параметри солвера, обмежувачі ресурсів та прапорці попереднього топологічного аналізу.

:::tabs
```c
typedef struct {
    hamiltonian_algo_t algorithm;  /* Обраний алгоритм обчислення */
    uint32_t timeout_ms;           /* Максимальний час виконання у мілісекундах (0 = без ліміту) */
    size_t max_memory_bytes;       /* Максимальний обсяг пам'яті у байтах (0 = без ліміту) */
    bool find_all_cycles;          /* true: шукати всі можливі цикли; false: зупинитися на першому */
    bool enable_dirac_check;       /* Пре-перевірка достатніх умов Дірака та Оре за O(V + E) */
    int num_threads;               /* Кількість паралельних потоків (1 = однопотоковий режим) */
} hamiltonian_config_t;
```
```cpp
#include <chrono>
#include <cstddef>

namespace hamiltonian {

struct Config {
    Algorithm algorithm{Algorithm::Auto};
    std::chrono::milliseconds timeout{0};
    size_t max_memory_bytes{0};
    bool find_all_cycles{false};
    bool enable_dirac_check{true};
    int num_threads{1};
};

} // namespace hamiltonian
```
:::

### Опис полів конфігурації

- `algorithm`: Вибір обчислювального двигуна (`AUTO`, `BACKTRACK`, `HELD_KARP`, `SAT_REDUCE`). За замовчуванням встановлюється в `HAMILTONIAN_ALGO_AUTO`.
- `timeout_ms` / `timeout`: Граничний час роботи солвера. Якщо обчислення не завершилося за вказаний інтервал, солвер перериває рекурсію і повертає `HAMILTONIAN_ERROR_TIMEOUT`. Значення `0` означає відсутність часового ліміту.
- `max_memory_bytes`: Максимальний обсяг оперативної пам'яті у байтах, який дозволено виділяти під масиви станів. Якщо алгоритму Гелда-Карпа потрібно більше пам'яті ніж вказано, солвер автоматично переключається на `BACKTRACK` або повертає помилку `HAMILTONIAN_ERROR_OUT_OF_MEMORY`.
- `find_all_cycles`: При значенні `false` солвер зупиняється негайно після виявлення першого гамільтонового циклу. При `true` відбувається повне вирахування усіх унікальних гамільтонових циклів.
- `enable_dirac_check`: Якщо `true`, перед запуском експоненційного перебору солвер виконує швидкі перевірки умов Дірака (`deg(v) ≥ n/2`) та Оре (`deg(u) + deg(v) ≥ n`). Якщо умови виконуються, гамільтоновість вважається доведеною без запускання важкого перебору.
- `num_threads`: Кількість робочих потоків для паралельного виконання. При `num_threads = 1` обчислення виконуються в поточному викликовому потоці.

---

## 5. Структура результату (`hamiltonian_result_t` / `Result`)

Структура `hamiltonian_result_t` містить підсумковий статус, знайдену послідовність обходу та обчислювальні метрики виконання.

:::tabs
```c
typedef struct {
    hamiltonian_status_t status;  /* Статус завершення обчислення */
    size_t path_length;           /* Кількість вершин у шляху (n для циклу) */
    size_t *path;                 /* Динамічний масив вершин послідовності обходу */
    uint64_t states_explored;     /* Кількість досліджених станів / рекурсивних викликів */
    double elapsed_seconds;       /* Точний витрачений час у секундах */
} hamiltonian_result_t;
```
```cpp
#include <vector>
#include <chrono>
#include <cstdint>

namespace hamiltonian {

struct Result {
    Status status{Status::NoCycleExists};
    std::vector<size_t> path{};
    uint64_t states_explored{0};
    std::chrono::duration<double> elapsed_time{0};
};

} // namespace hamiltonian
```
:::

### Правила володіння пам'яттю (Memory Ownership Contract)

1. **У C API:** Масив `result.path` виділяється всередині функції `hamiltonian_solve()` за допомогою `malloc()`. Користувач зобов'язаний передати вказівник на структуру результату у функцію `hamiltonian_result_free()`, яка безпечно звільняє виділений масив та обнуляє вказівники.
2. **У C++ API:** Використовується RAII-контейнер `std::vector<size_t>`, що унеможливлює витоки пам'яті. Вся пам'ять звільняється автоматично при руйнуванні об'єкта `Result`.

---

## 6. Публічний API (`libhamiltonian.h` / `libhamiltonian.hpp`)

Нижче наведено повні заголовочні файли інтерфейсу для C та C++.

:::tabs
```c
#ifndef LIBHAMILTONIAN_H
#define LIBHAMILTONIAN_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct hamiltonian_graph hamiltonian_graph_t;

/* Створення нового графа на num_vertices вершин */
hamiltonian_graph_t* hamiltonian_graph_create(size_t num_vertices);

/* Звільнення ресурсів графа */
void hamiltonian_graph_free(hamiltonian_graph_t *graph);

/* Додавання неупорядкованого ребра між u та v */
hamiltonian_status_t hamiltonian_graph_add_edge(hamiltonian_graph_t *graph, size_t u, size_t v);

/* Ініціалізація структури конфігурації параметрами за замовчуванням */
void hamiltonian_config_init_default(hamiltonian_config_t *config);

/* Основна функція розв'язання задачі гамільтонового циклу */
hamiltonian_status_t hamiltonian_solve(
    const hamiltonian_graph_t *graph,
    const hamiltonian_config_t *config,
    hamiltonian_result_t *out_result
);

/* Звільнення внутрішніх ресурсів структури результату */
void hamiltonian_result_free(hamiltonian_result_t *result);

/* Допоміжна перевірка достатніх умов Дірака (O(V)) */
bool hamiltonian_check_dirac_condition(const hamiltonian_graph_t *graph);

/* Допоміжна перевірка достатніх умов Оре (O(V²)) */
bool hamiltonian_check_ore_condition(const hamiltonian_graph_t *graph);

#ifdef __cplusplus
}
#endif

#endif /* LIBHAMILTONIAN_H */
```
```cpp
#ifndef LIBHAMILTONIAN_HPP
#define LIBHAMILTONIAN_HPP

#include <vector>
#include <optional>
#include <cstdint>
#include <chrono>
#include <span>

namespace hamiltonian {

class Graph {
public:
    explicit Graph(size_t vertices);
    ~Graph() = default;

    Graph(const Graph&) = delete;
    Graph& operator=(const Graph&) = delete;
    Graph(Graph&&) noexcept = default;
    Graph& operator=(Graph&&) noexcept = default;

    Status add_edge(size_t u, size_t v);
    [[nodiscard]] size_t num_vertices() const noexcept;
    [[nodiscard]] size_t num_edges() const noexcept;
    [[nodiscard]] bool has_edge(size_t u, size_t v) const noexcept;

    [[nodiscard]] bool check_dirac() const noexcept;
    [[nodiscard]] bool check_ore() const noexcept;

private:
    size_t vertices_;
    size_t edges_{0};
    std::vector<std::vector<uint8_t>> adj_;
};

class Solver {
public:
    explicit Solver(Config config = {});
    
    [[nodiscard]] Result solve(const Graph& graph) const;
    
private:
    Config config_;
};

} // namespace hamiltonian

#endif /* LIBHAMILTONIAN_HPP */
```
:::

### Детальна специфікація функцій C API

#### 1. `hamiltonian_graph_create`
- **Опис:** Виділяє пам'ять під новий екземпляр графа з фіксованою кількістю вершин `num_vertices`.
- **Аргументи:** `size_t num_vertices` — кількість вершин у графі (`num_vertices ≥ 3`).
- **Повертає:** Вказівник на створену структуру `hamiltonian_graph_t*` або `NULL` при виникненні помилки виділення пам'яті.

#### 2. `hamiltonian_graph_add_edge`
- **Опис:** Додає симетричне (неупорядковане) ребро між вершинами з індексами `u` та `v`.
- **Аргументи:** `hamiltonian_graph_t *graph` — вказівник на граф; `size_t u`, `size_t v` — індекси вершин (`0 ≤ u, v < num_vertices`).
- **Повертає:** `HAMILTONIAN_SUCCESS` або `HAMILTONIAN_ERROR_INVALID_SIZE` якщо індекси виходять за межі.

#### 3. `hamiltonian_solve`
- **Опис:** Основна процедура обчислення гамільтонового циклу.
- **Аргументи:**
  - `const hamiltonian_graph_t *graph` — вхідний граф.
  - `const hamiltonian_config_t *config` — налаштування солвера (якщо `NULL`, використовуються конфігурації за замовчуванням).
  - `hamiltonian_result_t *out_result` — вказівник на структуру для запису підсумків.
- **Повертає:** Код статусу `hamiltonian_status_t`.

---

## 7. Приклад ідіоматичного використання API

Нижче наведено повні приклади створення графа, налаштування конфігурації та обробки результатів мовами C та C++.

:::tabs
```c
#include "libhamiltonian.h"
#include <stdio.h>

int main(void) {
    size_t n = 5;
    hamiltonian_graph_t *g = hamiltonian_graph_create(n);
    if (!g) return 1;

    /* Створення циклу 0-1-2-3-4-0 з додатковими хордами */
    hamiltonian_graph_add_edge(g, 0, 1);
    hamiltonian_graph_add_edge(g, 1, 2);
    hamiltonian_graph_add_edge(g, 2, 3);
    hamiltonian_graph_add_edge(g, 3, 4);
    hamiltonian_graph_add_edge(g, 4, 0);
    hamiltonian_graph_add_edge(g, 1, 3);

    hamiltonian_config_t config;
    hamiltonian_config_init_default(&config);
    config.algorithm = HAMILTONIAN_ALGO_HELD_KARP;

    hamiltonian_result_t result;
    hamiltonian_status_t st = hamiltonian_solve(g, &config, &result);

    if (st == HAMILTONIAN_SUCCESS) {
        printf("Гамільтонів цикл знайдено (вершин %zu):\n", result.path_length);
        for (size_t i = 0; i < result.path_length; ++i) {
            printf("%zu ", result.path[i]);
        }
        printf("\nВитрачено часу: %.6f сек, станів: %lu\n", 
               result.elapsed_seconds, (unsigned long)result.states_explored);
    } else {
        printf("Гамільтонів цикл відсутній або сталася помилка: %d\n", st);
    }

    hamiltonian_result_free(&result);
    hamiltonian_graph_free(g);
    return 0;
}
```
```cpp
#include "libhamiltonian.hpp"
#include <iostream>

int main() {
    constexpr size_t n = 5;
    hamiltonian::Graph g(n);

    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 4);
    g.add_edge(4, 0);
    g.add_edge(1, 3);

    hamiltonian::Config config;
    config.algorithm = hamiltonian::Algorithm::HeldKarp;
    config.timeout = std::chrono::milliseconds(5000);

    hamiltonian::Solver solver(config);
    hamiltonian::Result res = solver.solve(g);

    if (res.status == hamiltonian::Status::Success) {
        std::cout << "Гамільтонів цикл знайдено (вершин " << res.path.size() << "):\n";
        for (size_t v : res.path) {
            std::cout << v << " ";
        }
        std::cout << "\nВитрачено часу: " << res.elapsed_time.count() 
                  << "s, досліджені стани: " << res.states_explored << "\n";
    } else {
        std::cout << "Гамільтонів цикл відсутній.\n";
    }

    return 0;
}
```
:::

---

## 8. Потокобезпечність та мультипоточне виконання

Бібліотека `libhamiltonian` забезпечує повну реентабельність (reentrancy) та підтримує мультипоточні обчислення:

1. **Читання графів (`const Graph&`):** Операції перевірки топології (`check_dirac()`, `check_ore()`) та обчислення циклу не модифікують внутрішній стан графа. Один і той самий граф може паралельно аналізуватися кількома незалежними потоками без необхідності зовнішніх блокувань (locks).
2. **Паралелізм у Held-Karp:** При налаштуванні `num_threads > 1` обчислення динамічного програмування для масок одного розміру `k` паралелиться між потоками за допомогою OpenMP або внутрішнього пулу задач (thread pool). Оскільки стани масок одного розміру обчислюються виключно на основі станів масок розміру `k - 1`, записи у масив `dp_next[mask]` є повністю ізольованими, що усуває гонки даних (data races) та надає майже лінійне прискорення від кількості обчислювальних ядер CPU.
