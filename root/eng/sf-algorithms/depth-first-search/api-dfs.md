# 📋 Інтерфейс та шаблон Visitor для обходу DFS

Ця вставка містить повний довідник із програмного інтерфейсу (API) та архітектурного шаблону **Visitor (Відвідувач)** для алгоритму обходу в глибину (DFS). Описана специфікація розділяє універсальний механізм обходу графа від конкретної прикладної задачі — виявлення циклів, топологічного сортування, знаходження компонент сильно зв'язності, мостів чи побудови дерева досяжності. Завдяки такому розділенню розробник може написати алгоритм обходу один раз, а потім адаптувати його під довільну задачу без мутації вихідного коду алгоритму.

---

### 1. Концепція та архітектура шаблону Visitor

У класичній інженерії програмного забезпечення застосування процедурного підходу до алгоритмів на графах призводить до того, що під кожне нове завдання (наприклад, перевірка планарності чи пошук точок розчленування) розробник змушений переписувати весь цикл обходу. Це породжує дублювання коду, ускладнює тестування та підвищує ризик внесення помилок у базісну логіку підтримання кольорів вершин і часових міток.

Шаблон Visitor вирішує цю проблему за допомогою контракту подій. Під час виконання обходу алгоритм DFS послідовно проходить через фіксований набір точок контролю (Event Callbacks). У кожній такій точці алгоритм сповіщає зовнішній об'єкт-відвідувач про поточний стан обходу, передаючи йому ідентифікатори вершин та ребер.

---

### 2. Топологічна послідовність та детальний опис 9 подій обходу

Життєвий цикл сповіщень під час виконання DFS має суворий детермінований порядок, що випливає з теорії графа попередників. Нижче наведено детальний опис кожної з дев'яти точок контролю:

#### 1. `initialize_vertex(u)`
Викликається для кожної вершини `u ∈ V` на самому початку роботи алгоритму, ще до старту обходу будь-якої компоненти.
- **Математичний стан:** Всі вершини пофарбовано у білий колір (`WHITE`), часові мітки `d[u]` та `f[u]` не визначено, таймер дорівнює нулю.
- **Призначення:** Використовується для початкового виділення пам'яті, скидання масивів відстаней, ініціалізації веси вершин або обнулення лічильників відвідувача.

#### 2. `start_vertex(u)`
Викликається для вершини `u`, яка стає коренем нового дерева обходу у лісі DFS.
- **Математичний стан:** Вершина `u` є білою (`WHITE`), але вона обрана як початковий вузол зовнішнім циклом перебору компонент.
- **Призначення:** Сигналізує про початок обробки нової компоненти зв'язності. Використовується у розв'язанні задач підрахунку компонент та алгоритмах типу Косараю–Шаріра.

#### 3. `discover_vertex(u)`
Викликається у момент, коли вершина `u` вперше відкривається алгоритмом і переходить у стан `GRAY`.
- **Математичний стан:** Колір вершини змінено з `WHITE` на `GRAY`, часова мітка відкриття `d[u]` зафіксована у таймері. Вершину додано на верхівку стеку викликів.
- **Призначення:** Використовується для фіксації вхідного порядку вершин (Pre-Order Traversal), занесення вершини у допоміжні стеки (наприклад, у алгоритмі Тар'яна для SCC) та ініціалізації локальних функцій на кшталт `lowlink[u] = d[u]`.

#### 4. `examine_edge(u, v)`
Викликається для кожного вихідного ребра `u → v` безпосередньо перед його аналізом і перевіркою кольору цільової вершини `v`.
- **Математичний стан:** Вершина `u` перебуває у стані `GRAY`, стан цільової вершини `v` ще не перевірявся у поточному кроці.
- **Призначення:** Логування траєкторії руху, облік ваги ребер, підрахунок загальної кількості переглянутих зв'язків.

#### 5. `tree_edge(u, v)`
Викликається, якщо цільова вершина `v` є білою (`WHITE`).
- **Математичний стан:** Ребро `u → v` додається до остовного лісу `G_π`. Після виконання цього callback алгоритм негайно здійснює рекурсивне занурення у вершину `v`.
- **Призначення:** Побудова остовного дерева, збереження батьківських посилань `parent[v] = u`, обчислення відстаней у дереві.

#### 6. `back_edge(u, v)`
Викликається, якщо цільова вершина `v` є сірою (`GRAY`).
- **Математичний стан:** Цільова вершина `v` перебуває вище за `u` на поточному стеку викликів (`d[v] <= d[u]`). Ребро `u → v` створює замкнений контур у графі.
- **Призначення:** Виявлення орієнтованих циклів, детекція взаємних блокувань (Deadlocks), оновлення функції `lowlink[u] = min(lowlink[u], d[v])` для знаходження точок розчленування.

#### 7. `forward_or_cross_edge(u, v)`
Викликається, якщо цільова вершина `v` є чорною (`BLACK`).
- **Математичний стан:** Обробку `v` повністю завершено (`f[v]` визначено). Якщо `d[u] < d[v]`, ребро є прямим (`FORWARD`); якщо `d[u] > d[v]`, ребро є перехресним (`CROSS`).
- **Призначення:** Перевірка альтернативних шляхів у графі, аналіз зв'язків між різними гілками дерева обходу.

#### 8. `finish_edge(u, v)`
Викликається після того, як обхід цільової вершини `v` та всього її піддерева повністю завершено, і контроль повернувся до ребра `u → v`.
- **Математичний стан:** Вершина `v` перейшла у стан `BLACK`, її мітка `f[v]` зафіксована. Усі нащадки `v` оброблені.
- **Призначення:** Передача агрегованих обчислювальних результатів з піддерева `v` нагору до предка `u` (наприклад, оновлення `lowlink[u] = min(lowlink[u], lowlink[v])` в алгоритмі Тар'яна).

#### 9. `finish_vertex(u)`
Викликається, коли всі вихідні ребра вершини `u` оброблені, і сама вершина переходить у стан `BLACK`.
- **Математичний стан:** Вершину `u` пофарбовано у чорний колір, мітка `f[u]` зафіксована, вершину вилучено зі стеку.
- **Призначення:** Формування зворотного порядку обробки (Post-Order Traversal). Оскільки для всіх нащадків `v` виклик `finish_vertex(v)` відбувається раніше за `finish_vertex(u)`, запис вершин у момент `finish_vertex` формує ідеальну основу для топологічного сортування.

---

### 3. Гарантії інваріантів та контракт виконання

Під час реалізації власного відвідувача розробник може покладатися на суворі математичні інваріанти, які гарантує алгоритм обходу:

- **Інваріант виклику `discover_vertex`**: На момент виклику `discover_vertex(u)` вершина `u` вже гарантовано має встановлену мітку `d[u]`, а її колір є `GRAY`. Жоден із сусідів `u` ще не починав обробку в рамках поточного занурення.
- **Інваріант вкладеності викликів `finish_vertex`**: Виклик `finish_vertex(v)` для будь-якого нащадка `v` вершини `u` відбудеться **строго раніше**, ніж виклик `finish_vertex(u)`. Це гарантує порядок Post-Order.
- **Інваріант зворотного ребра**: Виклик `back_edge(u, v)` відбувається тоді й тільки тоді, коли вершина `v` перебуває на поточному стеку викликів. На цей момент `d[v] <= d[u]`, а `f[v]` ще не визначено.
- **Послідовність викликів для ребра дерева**: Для кожного ребра дерева `u → v` послідовність подій є строго такою: `examine_edge(u, v)` → `tree_edge(u, v)` → `discover_vertex(v)` → ... (обхід піддерева v) ... → `finish_vertex(v)` → `finish_edge(u, v)`.

---

### 4. Специфікація API мовами C та C++

У мові C через відсутність шаблонів паттерн Visitor реалізується через структуру вказівників на функції та передачу контексту користувача `void* user_data`. Якщо відвідувач не потребує обробки певної події, відповідний вказівник у структурі встановлюється в `NULL`, що дозволяє алгоритму пропускати виклик без накладних витрат.

У мові C++20 паттерн Visitor досягає своєї ідеальної форми завдяки статичному поліморфізму та концептам. Замість віртуальних функцій або вказівників на функції використовується метапрограмування на шаблонах. Компілятор під час генерації коду повністю інлайнить (вбудовує) тіла методів відвідувача у сам цикл обходу, забезпечуючи **нульову ціну абстракції (Zero-Cost Abstraction)**.

:::tabs
```c
// C API (dfs_api.h) — реалізація на вказівниках на функції
#ifndef DFS_API_H
#define DFS_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int num_vertices;
    int** adj_matrix;
} dfs_graph_t;

typedef struct {
    void (*initialize_vertex)(int u, void* user_data);
    void (*start_vertex)(int u, void* user_data);
    void (*discover_vertex)(int u, int discovery_time, void* user_data);
    void (*examine_edge)(int u, int v, void* user_data);
    void (*tree_edge)(int u, int v, void* user_data);
    void (*back_edge)(int u, int v, void* user_data);
    void (*forward_or_cross_edge)(int u, int v, void* user_data);
    void (*finish_edge)(int u, int v, void* user_data);
    void (*finish_vertex)(int u, int finish_time, void* user_data);
} dfs_visitor_t;

typedef struct {
    bool stop_on_cycle;
    bool process_all_components;
} dfs_config_t;

bool dfs_traverse(const dfs_graph_t* graph, 
                  const dfs_visitor_t* visitor, 
                  void* user_data, 
                  const dfs_config_t* config);

#ifdef __cplusplus
}
#endif

#endif // DFS_API_H
```
```cpp
// C++ API (dfs_visitor.hpp) — шаблон з C++20 концептами
#ifndef DFS_VISITOR_HPP
#define DFS_VISITOR_HPP

#include <vector>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <utility>

namespace algo {

struct default_dfs_visitor {
    void initialize_vertex(int /*u*/) noexcept {}
    void start_vertex(int /*u*/) noexcept {}
    void discover_vertex(int /*u*/, int /*d_time*/) noexcept {}
    void examine_edge(int /*u*/, int /*v*/) noexcept {}
    void tree_edge(int /*u*/, int /*v*/) noexcept {}
    void back_edge(int /*u*/, int /*v*/) noexcept {}
    void forward_or_cross_edge(int /*u*/, int /*v*/) noexcept {}
    void finish_edge(int /*u*/, int /*v*/) noexcept {}
    void finish_vertex(int /*u*/, int /*f_time*/) noexcept {}
};

template <typename V>
concept DFSVisitor = requires(V v, int u, int target, int time) {
    { v.initialize_vertex(u) };
    { v.start_vertex(u) };
    { v.discover_vertex(u, time) };
    { v.examine_edge(u, target) };
    { v.tree_edge(u, target) };
    { v.back_edge(u, target) };
    { v.forward_or_cross_edge(u, target) };
    { v.finish_edge(u, target) };
    { v.finish_vertex(u, time) };
};

enum class Color : std::uint8_t { White, Gray, Black };

template <typename Graph, DFSVisitor Visitor>
class DFSEngine {
public:
    static void run(const Graph& g, Visitor visitor) {
        const std::size_t n = g.num_vertices();
        std::vector<Color> color(n, Color::White);
        std::vector<int> discovery_time(n, 0);
        std::vector<int> finish_time(n, 0);
        int timer = 0;

        for (std::size_t u = 0; u < n; ++u) {
            visitor.initialize_vertex(static_cast<int>(u));
        }

        auto visit = [&](auto& self, int u) -> void {
            color[u] = Color::Gray;
            discovery_time[u] = ++timer;
            visitor.discover_vertex(u, discovery_time[u]);

            for (int v : g.neighbors(u)) {
                visitor.examine_edge(u, v);

                if (color[v] == Color::White) {
                    visitor.tree_edge(u, v);
                    self(self, v);
                    visitor.finish_edge(u, v);
                } else if (color[v] == Color::Gray) {
                    visitor.back_edge(u, v);
                } else {
                    visitor.forward_or_cross_edge(u, v);
                }
            }

            color[u] = Color::Black;
            finish_time[u] = ++timer;
            visitor.finish_vertex(u, finish_time[u]);
        };

        for (std::size_t u = 0; u < n; ++u) {
            if (color[u] == Color::White) {
                visitor.start_vertex(static_cast<int>(u));
                visit(visit, static_cast<int>(u));
            }
        }
    }
};

template <typename Graph, typename Visitor>
void depth_first_search(const Graph& g, Visitor&& visitor) {
    DFSEngine<Graph, std::decay_t<Visitor>>::run(g, std::forward<Visitor>(visitor));
}

} // namespace algo

#endif // DFS_VISITOR_HPP
```
:::

---

### 5. Внутрішня реалізація виклику подій відвідувача

:::tabs
```c
// Виклик події в мові C за допомогою безпечного макросу
#define DFS_NOTIFY(event, ...) \
    do { \
        if (visitor && visitor->event) { \
            visitor->event(__VA_ARGS__, user_data); \
        } \
    } while(0)

static void dfs_internal_visit_c(const dfs_graph_t* g, int u, int* color, 
                                int* d, int* f, int* timer, 
                                const dfs_visitor_t* visitor, void* user_data) {
    color[u] = 1; // GRAY
    d[u] = ++(*timer);
    DFS_NOTIFY(discover_vertex, u, d[u]);

    for (int v = 0; v < g->num_vertices; v++) {
        if (g->adj_matrix[u][v]) {
            DFS_NOTIFY(examine_edge, u, v);
            if (color[v] == 0) { // WHITE
                DFS_NOTIFY(tree_edge, u, v);
                dfs_internal_visit_c(g, v, color, d, f, timer, visitor, user_data);
                DFS_NOTIFY(finish_edge, u, v);
            } else if (color[v] == 1) { // GRAY
                DFS_NOTIFY(back_edge, u, v);
            } else { // BLACK
                DFS_NOTIFY(forward_or_cross_edge, u, v);
            }
        }
    }

    color[u] = 2; // BLACK
    f[u] = ++(*timer);
    DFS_NOTIFY(finish_vertex, u, f[u]);
}
```
```cpp
// Прямий інлайнінг методів у C++20 (без виклику функцій через макроси або вказівники)
template <typename Graph, DFSVisitor Visitor>
void run_dfs_cpp_inlined(const Graph& g, Visitor& visitor, int u, 
                         std::vector<Color>& color, int& timer) {
    color[u] = Color::Gray;
    visitor.discover_vertex(u, ++timer);

    for (int v : g.neighbors(u)) {
        visitor.examine_edge(u, v);
        if (color[v] == Color::White) {
            visitor.tree_edge(u, v);
            run_dfs_cpp_inlined(g, visitor, v, color, timer);
            visitor.finish_edge(u, v);
        } else if (color[v] == Color::Gray) {
            visitor.back_edge(u, v);
        } else {
            visitor.forward_or_cross_edge(u, v);
        }
    }

    color[u] = Color::Black;
    visitor.finish_vertex(u, ++timer);
}
```
:::

---

### 6. Конкретні прикладні відвідувачі

Розглянемо, як за допомогою створення власних відвідувачів розв'язуються класичні прикладні задачі без зміни коду рушія DFS.

#### 1. Детектор циклів (Cycle Detector Visitor)

:::tabs
```c
// C-реалізація детектора циклів через контекст
typedef struct {
    bool has_cycle;
    int cycle_u;
    int cycle_v;
} cycle_detector_context_t;

void on_back_edge_c(int u, int v, void* user_data) {
    cycle_detector_context_t* ctx = (cycle_detector_context_t*)user_data;
    ctx->has_cycle = true;
    ctx->cycle_u = u;
    ctx->cycle_v = v;
}
```
```cpp
// C++20 реалізація детектора циклів
#include <iostream>

struct CycleDetectorVisitor : public algo::default_dfs_visitor {
    bool has_cycle{false};
    int cycle_src{-1};
    int cycle_dst{-1};

    void back_edge(int u, int v) noexcept {
        has_cycle = true;
        cycle_src = u;
        cycle_dst = v;
    }
};
```
:::

#### 2. Побудова топологічного сортування (Topological Sorter Visitor)

:::tabs
```c
// C-реалізація топологічного сортування
typedef struct {
    int* order;
    int index;
} topo_sort_context_t;

void on_finish_vertex_topo_c(int u, int finish_time, void* user_data) {
    topo_sort_context_t* ctx = (topo_sort_context_t*)user_data;
    ctx->order[ctx->index--] = u; // Заповнюємо масив з кінця
}
```
```cpp
// C++20 реалізація топологічного сортування
#include <vector>
#include <algorithm>

class TopologicalSortVisitor : public algo::default_dfs_visitor {
private:
    std::vector<int> post_order_;

public:
    void finish_vertex(int u, int /*f_time*/) {
        post_order_.push_back(u);
    }

    [[nodiscard]] std::vector<int> get_topological_order() const {
        std::vector<int> result = post_order_;
        std::reverse(result.begin(), result.end());
        return result;
    }
};
```
:::

#### 3. Підрахунок компонент зв'язності (Component Counter Visitor)

:::tabs
```c
// C-реалізація розмітки компонент
typedef struct {
    int current_component;
    int* component_map;
} component_context_t;

void on_start_vertex_c(int u, void* user_data) {
    component_context_t* ctx = (component_context_t*)user_data;
    ctx->current_component++;
}

void on_discover_vertex_comp_c(int u, int d_time, void* user_data) {
    component_context_t* ctx = (component_context_t*)user_data;
    ctx->component_map[u] = ctx->current_component;
}
```
```cpp
// C++20 реалізація розмітки компонент
#include <vector>

class ComponentLabelerVisitor : public algo::default_dfs_visitor {
private:
    int current_component_{-1};
    std::vector<int> component_ids_;

public:
    explicit ComponentLabelerVisitor(std::size_t num_vertices)
        : component_ids_(num_vertices, -1) {}

    void start_vertex(int u) noexcept {
        ++current_component_;
    }

    void discover_vertex(int u, int /*d_time*/) noexcept {
        component_ids_[u] = current_component_;
    }

    [[nodiscard]] int num_components() const noexcept {
        return current_component_ + 1;
    }

    [[nodiscard]] const std::vector<int>& component_ids() const noexcept {
        return component_ids_;
    }
};
```
:::

#### 4. Знаходження мостів та точок розчленування (Bridges & Articulation Points Visitor)

:::tabs
```c
// C-реалізація обчислення мостів та lowlink
typedef struct {
    int* d;
    int* low;
    int timer;
    bool* is_bridge_edge;
} bridge_context_t;

void on_discover_bridge_c(int u, int discovery_time, void* user_data) {
    bridge_context_t* ctx = (bridge_context_t*)user_data;
    ctx->d[u] = discovery_time;
    ctx->low[u] = discovery_time;
}

void on_finish_edge_bridge_c(int u, int v, void* user_data) {
    bridge_context_t* ctx = (bridge_context_t*)user_data;
    if (ctx->low[v] < ctx->low[u]) {
        ctx->low[u] = ctx->low[v];
    }
    if (ctx->low[v] > ctx->d[u]) {
        // Ребро (u, v) є мостом!
    }
}
```
```cpp
// C++20 реалізація знаходження мостів
#include <vector>
#include <algorithm>

class BridgeFinderVisitor : public algo::default_dfs_visitor {
private:
    std::vector<int> d_;
    std::vector<int> low_;
    std::vector<std::pair<int, int>> bridges_;

public:
    explicit BridgeFinderVisitor(std::size_t n) : d_(n, 0), low_(n, 0) {}

    void discover_vertex(int u, int time) noexcept {
        d_[u] = time;
        low_[u] = time;
    }

    void back_edge(int u, int v) noexcept {
        low_[u] = std::min(low_[u], d_[v]);
    }

    void finish_edge(int u, int v) noexcept {
        low_[u] = std::min(low_[u], low_[v]);
        if (low_[v] > d_[u]) {
            bridges_.push_back({u, v});
        }
    }

    [[nodiscard]] const std::vector<std::pair<int, int>>& bridges() const noexcept {
        return bridges_;
    }
};
```
:::

---

### 7. Порівняльний аналіз із Boost Graph Library (BGL)

Запропонована архітектура C++ Visitor узгоджується з дизайном популярної бібліотеки **Boost Graph Library (BGL)**, яка використовує функцію `boost::depth_first_search` та об'єкти-відвідувачі `boost::dfs_visitor`.

Основні відмінності та переваги сучасного підходу на C++20:

1. **Відсутність макросів Boost**: Більш старі версії BGL використовували складні макроси `BOOST_Concept_With_Default` для емуляції концептів. Сучасна реалізація спирається на ключове слово `concept` мови C++20, що робить помилки компіляції зрозумілими й короткими.
2. **Семантика переміщення**: Підтримка `std::forward` та rvalue-посилань дозволяє передавати тимчасові об'єкти відвідувачів без зайвого копіювання стану.
3. **Безпека винятків**: Оскільки методи відвідувача є inline-функціями, генерація винятку всередині відвідувача (наприклад, для дострокового переривання обходу під час виявлення шуканого елемента) коректно розгортає стек викликів без витоків пам'яті.

---

### 8. Практичні рекомендації щодо проектування API

- **Для бібліотек C/C++**: Рекомендується надавати C-заголовок `dfs_api.h` для бінарної сумісності (ABI) між різними мовами (Python, Rust, C# через FFI) та розширений заголовок C++ `dfs_visitor.hpp` для внутрішніх високоефективних обчислень.
- **Управління пам'яттю**: Внутрішній масив кольорів та міток у C++ варіанті виділяється один раз за запуск. У разі багаторазових запусків DFS на тому самому графі варто розглядати можливість передачі зовнішнього контексту пам'яті (Memory Arena) для уникнення частих викликів `std::vector::resize`.
- **Багатопотоковість**: Сам алгоритм обходу та об'єкт-відвідувач повинні бути потокобезпечними. Якщо граф використовується декількома потоками паралельно для читання, кожен потік повинен мати власний екземпляр відвідувача та локальні масиви кольорів.
