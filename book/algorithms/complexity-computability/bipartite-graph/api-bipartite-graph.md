# 📋 Специфікація інтерфейсу та структур даних двочасткового графа

Цей документ є формальним системним довідником програмного інтерфейсу (API), структур даних, інваріантів пам'яті та угод про обробку помилок для системної бібліотеки двочасткових графів. Специфікація подана у формі суворого контракту розробника для двох мов програмування: C та C++.

## 1. Архітектура пам'яті та формальні типи даних

Двочастковий граф є алгебраїчною парою неперетинних множин вершин `U` (ліва частка) та `V` (права частка), де будь-яке ребро зв'язує вершину з `U` із вершиною з `V`. Для забезпечення максимальної швидкодії при обході графа та мінімізації промахів кєш-пам'яті процесора (L1/L2 cache misses) у системному API застосовано схему роздільного зберігання списків суміжності.

Вхідні вершини лівої частки `U` індексуються цілими числами в діапазоні від `0` до `n₁ - 1`, а вершини правої частки `V` — індексами від `0` до `n₂ - 1`. Така роздільна схема індексації дозволяє звертатися до масивів суміжності за константний час `O(1)` без використання додаткових хеш-таблиць чи словників.

### 1.1. Коди перелічення статусів та помилок `bipartite_status_t`

Усі процедури C API повертають статус виконання у вигляді 32-бітного цілого числа з перелічення `bipartite_status_t`. У C++ API помилки сигналізуються через систему винятків або через повернення безпечної обгортки `std::expected` (у стандарту C++23).

Нижче подано повну таблицю кодів помилок, їхніх C++ відповідників та причин виникнення при роботі з бібліотекою.

| Код константи C | Значення | Виняток / Аналог C++ | Опис стану та причини виникнення помилки |
| :--- | :--- | :--- | :--- |
| `BIPARTITE_OK` | `0` | Успіх / `std::expected` value | Операцію виконано успішно. Усі інваріанти структури даних повністю збережено. |
| `BIPARTITE_ERR_NOT_BIPARTITE` | `-1` | `std::invalid_argument` | Вхідний граф не є двочастковим (під час валідації виявлено непарний цикл). |
| `BIPARTITE_ERR_INVALID_PARTITION` | `-2` | `std::logic_error` | Задане розбиття порушує умову відсутності внутрішніх ребер усередині частки. |
| `BIPARTITE_ERR_INDEX_OUT_OF_BOUNDS` | `-3` | `std::out_of_range` | Переданий індекс вершини перевищує задекларований розмір частки `n₁` або `n₂`. |
| `BIPARTITE_ERR_NULL_POINTER` | `-4` | `std::invalid_argument` | Передано нульовий вказівник `NULL` у якості обов'язкового аргументу. |
| `BIPARTITE_ERR_NO_MEMORY` | `-5` | `std::bad_alloc` | Системне виділення пам'яті (`malloc` або `realloc`) повернуло нуль. |

---

### 1.2. Специфікація структур даних представлення графа

У C API двочастковий граф подається як прозора структура `bipartite_graph_t`, яка зберігає розміри часток, кількість ребер та масиви вказівників на списки суміжності. У C++ API структура повністю інкапсульована у клас `BipartiteGraph` із використанням стандартних контейнерів `std::vector` та шаблонів автоматичного керування ресурсами RAII.

Роздільне зберігання масивів `adj_left` та `adj_right` дозволяє здійснювати як прямий обхід від `U` до `V`, так і зворотний обхід від `V` до `U` без додаткового транспонування графа.

:::tabs
```c
/* C API: Повний заголовочний файл бібліотеки libbipartite */
#ifndef BIPARTITE_GRAPH_H
#define BIPARTITE_GRAPH_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BIPARTITE_OK                         =  0,
    BIPARTITE_ERR_NOT_BIPARTITE          = -1,
    BIPARTITE_ERR_INVALID_PARTITION      = -2,
    BIPARTITE_ERR_INDEX_OUT_OF_BOUNDS    = -3,
    BIPARTITE_ERR_NULL_POINTER           = -4,
    BIPARTITE_ERR_NO_MEMORY              = -5
} bipartite_status_t;

typedef struct {
    size_t num_left;        /* Кількість вершин у лівій частці U (|U| = n₁) */
    size_t num_right;       /* Кількість вершин у правій частці V (|V| = n₂) */
    size_t num_edges;       /* Загальна кількість ребер |E| */
    size_t **adj_left;      /* Динамічний масив списків суміжності для U */
    size_t *deg_left;       /* Поточний ступінь кожної вершини U */
    size_t *cap_left;       /* Виділена ємність списків суміжності для U */
    size_t **adj_right;     /* Динамічний масив списків суміжності для V */
    size_t *deg_right;      /* Поточний ступінь кожної вершини V */
    size_t *cap_right;      /* Виділена ємність списків суміжності для V */
} bipartite_graph_t;

#ifdef __cplusplus
}
#endif

#endif /* BIPARTITE_GRAPH_H */
```
```cpp
// C++ API: Інкапсульований клас двочасткового графа
#ifndef BIPARTITE_GRAPH_HPP
#define BIPARTITE_GRAPH_HPP

#include <vector>
#include <cstddef>
#include <stdexcept>
#include <optional>
#include <span>

namespace net {

enum class Status {
    Ok = 0,
    NotBipartite = -1,
    InvalidPartition = -2,
    IndexOutOfBounds = -3,
    NullPointer = -4,
    NoMemory = -5
};

class BipartiteGraph {
public:
    BipartiteGraph(std::size_t num_left, std::size_t num_right);
    ~BipartiteGraph() = default;

    BipartiteGraph(const BipartiteGraph&) = default;
    BipartiteGraph& operator=(const BipartiteGraph&) = default;
    BipartiteGraph(BipartiteGraph&&) noexcept = default;
    BipartiteGraph& operator=(BipartiteGraph&&) noexcept = default;

    void add_edge(std::size_t u_left, std::size_t v_right);

    [[nodiscard]] std::size_t num_left() const noexcept { return num_left_; }
    [[nodiscard]] std::size_t num_right() const noexcept { return num_right_; }
    [[nodiscard]] std::size_t num_edges() const noexcept { return num_edges_; }

    [[nodiscard]] std::span<const std::size_t> neighbors_left(std::size_t u) const;
    [[nodiscard]] std::span<const std::size_t> neighbors_right(std::size_t v) const;

private:
    std::size_t num_left_;
    std::size_t num_right_;
    std::size_t num_edges_{0};
    std::vector<std::vector<std::size_t>> adj_left_;
    std::vector<std::vector<std::size_t>> adj_right_;
};

} // namespace net

#endif // BIPARTITE_GRAPH_HPP
```
:::

---

### 1.3. Специфікація структур результату аналізу та розфарбовування

При виконанні процедури перевірки двочастковості алгоритм будує детальний звіт `bipartite_partition_t`. Якщо граф є двочастковим, звіт містить масив кольорів для всіх вершин. Якщо ж у графі виявлено непарний цикл, звіт містить перше конфліктне ребро та повний список вершин непарного циклу для відладки.

Структура результату гарантує, що при отриманні статусу `BIPARTITE_OK` колір кожної вершини з частки `U` дорівнює `0`, а колір кожної вершини з частки `V` дорівнює `1`.

:::tabs
```c
/* C API: Результат перевірки 2-розфарбовування */
typedef struct {
    bool is_bipartite;      /* Прапорець: true, якщо граф двочастковий */
    int *colors;            /* Масив кольорів [0, 1] розміром n₁ + n₂ (-1 якщо не відвідано) */
    size_t conflict_u;      /* Перша вершина конфліктного ребра */
    size_t conflict_v;      /* Друга вершина конфліктного ребра */
    size_t *cycle_vertices; /* Динамічний масив вершин непарного циклу (NULL якщо немає) */
    size_t cycle_length;    /* Довжина непарного циклу (0 якщо двочастковий) */
} bipartite_partition_t;
```
```cpp
// C++ API: Результат 2-розфарбовування
namespace net {

struct PartitionResult {
    bool is_bipartite{true};
    std::vector<int> colors; // Колір 0 (частка U), 1 (частка V)
    std::optional<std::pair<std::size_t, std::size_t>> conflict_edge;
    std::vector<std::size_t> odd_cycle;
};

} // namespace net
```
:::

---

### 1.4. Специфікація результатів паросполучення та двоїстого покриття

За теоремою Кеніга (1931), у двочасткових графах розмір максимального паросполучення строго дорівнює розміру мінімального вершинного покриття: `ν(G) = τ(G)`. Структура результату обчислення паросполучення повертає обидва об'єкти одночасно, забезпечуючи перевірку цього фундаментального інваріанта.

Масив `match_left` кодує відображення `U → V`: якщо вершина `u` входить до паросполучення, `match_left[u]` містить індекс суміжної вершини `v ∈ V`; якщо `u` є вільною, `match_left[u] == -1`. Аналогічно масив `match_right` кодує зворотне відображення `V → U`.

:::tabs
```c
/* C API: Результат обчислення паросполучення та покриття */
typedef struct {
    size_t matching_size;   /* Розмір максимального паросполучення ν(G) */
    int *match_left;        /* Масив розміром n₁: match_left[u] = v (-1 якщо вільна) */
    int *match_right;       /* Масив розміром n₂: match_right[v] = u (-1 якщо вільна) */
    size_t *vertex_cover;   /* Масив вершин мінімального вершинного покриття C */
    size_t cover_size;      /* Розмір покриття τ(G) (гарантовано дорівнює matching_size) */
} bipartite_matching_t;
```
```cpp
// C++ API: Результат паросполучення
namespace net {

struct MatchingResult {
    std::size_t matching_size{0};
    std::vector<int> match_left;  // Індекси вершин V (-1 якщо вільна)
    std::vector<int> match_right; // Індекси вершин U (-1 якщо вільна)
    std::vector<std::size_t> vertex_cover; // Вершини покриття C
    std::size_t cover_size{0};
};

} // namespace net
```
:::

---

## 2. Сигнатури функцій та специфікація виконання

### 2.1. Конструктор та деструктор графа

#### `bipartite_graph_create` / `BipartiteGraph`

:::tabs
```c
/* C API: Виділення пам'яті та ініціалізація структури */
bipartite_status_t bipartite_graph_create(
    size_t num_left,
    size_t num_right,
    bipartite_graph_t **out_graph
);
```
```cpp
// C++ API: Конструктор класу BipartiteGraph
explicit BipartiteGraph::BipartiteGraph(std::size_t num_left, std::size_t num_right);
```
:::

- **Опис процедури:** Функція виділяє пам'ять під головний контейнер та початкові масиви списків суміжності ємністю 4 елементи для кожної вершини.
- **Параметри:** `num_left` — кількість вершин у частці `U` (`num_left > 0`); `num_right` — кількість вершин у частці `V` (`num_right > 0`); `out_graph` — адреса вказівника для запису створеного об'єкта.
- **Помилки:** Якщо `num_left == 0` або `num_right == 0`, повертається `BIPARTITE_ERR_INDEX_OUT_OF_BOUNDS`. При невдачі виділення пам'яті C API повертає `BIPARTITE_ERR_NO_MEMORY`, C++ викидає `std::bad_alloc`.

#### `bipartite_graph_destroy`

:::tabs
```c
/* C API: Звільнення пам'яті графа */
void bipartite_graph_destroy(bipartite_graph_t *graph);
```
```cpp
// C++ API: Автоматичний деструктор RAII
~BipartiteGraph() = default;
```
:::

- **Опис процедури:** Звільняє всі внутрішні динамічні масиви списків суміжності та сам об'єкт графа. Виклик `bipartite_graph_destroy(NULL)` є повністю безпечним.

---

### 2.2. Модифікація ребер

#### `bipartite_graph_add_edge`

:::tabs
```c
/* C API: Додавання ребра між частками */
bipartite_status_t bipartite_graph_add_edge(
    bipartite_graph_t *graph,
    size_t u_left,
    size_t v_right
);
```
```cpp
// C++ API: Додавання ребра між частками
void BipartiteGraph::add_edge(std::size_t u_left, std::size_t v_right);
```
:::

- **Опис процедури:** Додає неорієнтоване ребро між вершиною `u_left ∈ U` та вершиною `v_right ∈ V`. Внутрішньо додає `v_right` до списку `adj_left[u_left]` та `u_left` до списку `adj_right[v_right]`.
- **Стратегія зміни ємності:** Якщо поточний ступінь вершини досягає ємності масиву (`deg == cap`), ємність автоматично подвоюється (`cap *= 2`) із використанням `realloc` у C або `std::vector::push_back` у C++. Це забезпечує амортизований константний час `O(1)`.

---

### 2.3. Алгоритми перевірки 2-розфарбовування

#### `bipartite_graph_verify` / `check_bipartite`

:::tabs
```c
/* C API: Валідація двочастковості та побудова 2-розфарбовування */
bipartite_status_t bipartite_graph_verify(
    const bipartite_graph_t *graph,
    bipartite_partition_t *out_partition
);
```
```cpp
// C++ API: Валідація двочастковості
[[nodiscard]] PartitionResult check_bipartite(const BipartiteGraph& graph);
```
:::

- **Опис процедури:** Виконує обхід у ширину (BFS) для кожної компоненти зв'язності графа. Призначає альтернативні кольори (0 для частки `U`, 1 для частки `V`).
- **Виявлення конфліктів:** Якщо під час обходу виявляється ребро між двома вершинами одинакового кольору, функція зупиняє обхід, встановлює `is_bipartite = false` і повертає `BIPARTITE_ERR_NOT_BIPARTITE`.
- **Часова складність:** `O(|U| + |V| + |E|)`.

---

### 2.4. Обчислення максимального паросполучення

#### `bipartite_matching_compute` / `compute_max_matching`

:::tabs
```c
/* C API: Обчислення паросполучення обраним алгоритмом */
typedef enum {
    MATCHING_ALG_KUHN          = 0,  /* Алгоритм Куна DFS (O(|V|·|E|)) */
    MATCHING_ALG_HOPCROFT_KARP = 1   /* Алгоритм Гопкрофта-Карпа (O(|E|·√|V|)) */
} matching_algorithm_t;

bipartite_status_t bipartite_matching_compute(
    const bipartite_graph_t *graph,
    matching_algorithm_t algorithm,
    bipartite_matching_t *out_matching
);
```
```cpp
// C++ API: Обчислення паросполучення
enum class MatchingAlgorithm {
    Kuhn = 0,
    HopcroftKarp = 1
};

[[nodiscard]] MatchingResult compute_max_matching(
    const BipartiteGraph& graph,
    MatchingAlgorithm algorithm = MatchingAlgorithm::HopcroftKarp
);
```
:::

- **Опис процедури:** Знаходить максимальне паросполучення та двоїсте мінімальне вершинне покриття. Для алгоритму Гопкрофта-Карпа використовується комбінований обхід BFS/DFS для пошуку найкоротших збільшуючих шляхів за фази.
- **Гарантія двоїстісті:** `out_matching->matching_size == out_matching->cover_size`.

---

## 3. Зведені характеристики складності та вимог до пам'яті

Нижче подано зведену таблицю характеристик обчислювальної складності та вимог до допоміжної пам'яті для кожної процедури системної бібліотеки.

| Функція / Метод API | Базовий алгоритм | Час (Найгірший) | Допоміжна пам'ять | Винятки / Коди помилок |
| :--- | :--- | :--- | :--- | :--- |
| `bipartite_graph_create` | Ініціалізація контейнера | `O(|U| + |V|)` | `O(|U| + |V|)` | `BIPARTITE_ERR_NO_MEMORY` / `bad_alloc` |
| `bipartite_graph_add_edge` | Пуш до списку суміжності | `O(1)` аморт. | `O(|E|)` | `BIPARTITE_ERR_INDEX_OUT_OF_BOUNDS` |
| `bipartite_graph_verify` | BFS 2-coloring | `O(|V| + |E|)` | `O(|V|)` | `BIPARTITE_ERR_NOT_BIPARTITE` |
| `bipartite_matching_compute` (Kuhn) | DFS Збільшуючі шляхи | `O(|V| · |E|)` | `O(|V|)` | `BIPARTITE_ERR_NULL_POINTER` |
| `bipartite_matching_compute` (HK) | BFS/DFS Фази Гопкрофта | `O(|E| · √|V|)` | `O(|V| + |E|)` | `BIPARTITE_ERR_NO_MEMORY` |

---

## 4. Контракт багатопотоковості, винятки та оцінка обсягу пам'яті

1. **Багатопотокова безпека (Thread-Safety):** Паралельний виклик константних функцій читання (`bipartite_graph_verify`, `bipartite_matching_compute`) над одним екземпляром графа з різних потоків виконання є повністю безпечним і не вимагає блокувань. Модифікуючі операції (`bipartite_graph_add_edge`) вимагають зовнішнього м'ютексу (`std::shared_mutex`).
2. **Гарантії винятків у C++:** Усі методи C++ API надають сильну гарантію винятків (strong exception guarantee): якщо під час виконання методу викидається виняток `std::bad_alloc`, стан графа залишається повністю незмінним, а витоки ресурсів повністю виключаються.
3. **Оцінка обсягу пам'яті (Memory Footprint):** Загальний обсяг оперативної пам'яті, необхідний для збереження двочасткового графа `G = (U ∪ V, E)` у списковому форматі, оцінюється за формулою:

```
Memory(G) = (n₁ + n₂) · sizeof(pointer) + 2 · |E| · sizeof(size_t)
```

Для графа з 100 000 вершин та 500 000 ребер це складає приблизно 9.6 МБ оперативної пам'яті, що робить дане представлення надзвичайно компактним.
