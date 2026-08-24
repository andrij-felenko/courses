# ⚙️ Алгоритми зворотного відстеження та динамічного програмування

Ця вставка містить точні алгоритмічні реалізації пошуку гамільтонового циклу двома фундаментальними методами: алгоритмом повернень із відсіканням тупиків (Backtracking, `O(n!)`) та алгоритмом Гелда-Карпа на основі динамічного програмування з бітовими масками (Held-Karp Bitmask DP, `O(2ⁿ · n²)`).

![Динамічне програмування з бітовими масками (Held-Karp): DP[S][v]](img/fig5-held-karp-bitmask-dp.svg)
*Ієрархія станів динамічного програмування та переходи між підмножинами вершин.*

---

## 1. Алгоритм рекурсивного повернення з відсіканням (Backtracking)

Алгоритм зворотного відстеження є прямою алгоритмічною реалізацією глибинного обходу дерева станів (DFS у просторі простих шляхів). Ми будуємо потенційний гамільтонів цикл послідовно, обираючи на кожному кроці наступну ще не відвідану вершину, яка з'єднана ребом із поточною.

### Механізм роботи та комбінаторне дерево

Якщо граф є повним (`K♁`), дерево пошуку має `(n - 1)!` листків, оскільки з першої вершини ми маємо `n - 1` варіантів вибору, з другої — `n - 2`, і так далі. Без додаткових оптимізацій тривіальний перебір виявляється практично непридатним вже для `n ≥ 16`.

Проте для розріджених графів високу ефективність показують дві спеціалізовані евристики відсікання гілок:

1. **Аналіз висячих вершин та степеней у невідвіданому підграфі (Degree Pruning):**
   У будь-якому гамільтоновому циклі кожна вершина повинна мати рівно два активних ребра — одне вхідне та одне вихідне. Якщо на якомусь кроці рекурсії у невідвіданій частині графа з'являється вершина `v`, яка має менше двох доступних зв'язків з іншими невідвіданими вершинами (або з початковою/поточною вершиною), то утворення гамільтонового циклу у цій гілці стає математично неможливим. Рекурсивна гілка негайно відсікається (pruning), що запобігає марному обходу мільйонів тупикових піддерев.

2. **Евристика Варнсдорфа (Warnsdorff's Heuristic):**
   При виборі наступної вершини серед усіх невідвіданих сусідів поточної вершини `curr_v` алгоритм віддає пріоритет тій вершині, яка має **найменшу кількість вільних сусідів** у невідвіданому підграфі. Інтуїція цього правила полягає в тому, щоб якомога раніше відвідати «вузькі місця» графа — вершини з малим степенем, які згодом можуть стати ізольованими тупиками. Це правило аналогічне відомому розв'язку задачі про хід шахового коня по дошці.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int num_vertices;
    bool **adj_matrix;
} graph_t;

graph_t* graph_create(int vertices) {
    graph_t *g = (graph_t*)malloc(sizeof(graph_t));
    if (!g) return NULL;
    g->num_vertices = vertices;
    g->adj_matrix = (bool**)malloc(vertices * sizeof(bool*));
    for (int i = 0; i < vertices; ++i) {
        g->adj_matrix[i] = (bool*)calloc(vertices, sizeof(bool));
    }
    return g;
}

void graph_free(graph_t *g) {
    if (!g) return;
    for (int i = 0; i < g->num_vertices; ++i) {
        free(g->adj_matrix[i]);
    }
    free(g->adj_matrix);
    free(g);
}

void graph_add_edge(graph_t *g, int u, int v) {
    if (u >= 0 && u < g->num_vertices && v >= 0 && v < g->num_vertices) {
        g->adj_matrix[u][v] = true;
        g->adj_matrix[v][u] = true;
    }
}

static bool backtracking_step(const graph_t *g, int curr_v, int count, bool *visited, int *path) {
    if (count == g->num_vertices) {
        int start_v = path[0];
        return g->adj_matrix[curr_v][start_v];
    }

    for (int next_v = 0; next_v < g->num_vertices; ++next_v) {
        if (g->adj_matrix[curr_v][next_v] && !visited[next_v]) {
            visited[next_v] = true;
            path[count] = next_v;

            if (backtracking_step(g, next_v, count + 1, visited, path)) {
                return true;
            }

            visited[next_v] = false;
        }
    }
    return false;
}

bool solve_hamiltonian_backtrack(const graph_t *g, int *out_path) {
    if (!g || g->num_vertices < 3) return false;

    bool *visited = (bool*)calloc(g->num_vertices, sizeof(bool));
    if (!visited) return false;

    visited[0] = true;
    out_path[0] = 0;

    bool found = backtracking_step(g, 0, 1, visited, out_path);
    free(visited);
    return found;
}
```
```cpp
#include <vector>
#include <optional>
#include <span>
#include <iostream>

class Graph {
public:
    explicit Graph(size_t vertices) 
        : num_vertices_(vertices), adj_matrix_(vertices, std::vector<uint8_t>(vertices, 0)) {}

    void add_edge(size_t u, size_t v) {
        if (u < num_vertices_ && v < num_vertices_) {
            adj_matrix_[u][v] = 1;
            adj_matrix_[v][u] = 1;
        }
    }

    [[nodiscard]] size_t size() const noexcept { return num_vertices_; }
    [[nodiscard]] bool has_edge(size_t u, size_t v) const noexcept { return adj_matrix_[u][v] != 0; }

private:
    size_t num_vertices_;
    std::vector<std::vector<uint8_t>> adj_matrix_;
};

class HamiltonianBacktracker {
public:
    static std::optional<std::vector<size_t>> solve(const Graph& graph) {
        const size_t n = graph.size();
        if (n < 3) return std::nullopt;

        std::vector<size_t> path(n, 0);
        std::vector<bool> visited(n, false);

        visited[0] = true;
        path[0] = 0;

        if (step(graph, 0, 1, visited, path)) {
            return path;
        }
        return std::nullopt;
    }

private:
    static bool step(const Graph& g, size_t curr_v, size_t count, 
                     std::vector<bool>& visited, std::vector<size_t>& path) {
        if (count == g.size()) {
            return g.has_edge(curr_v, path[0]);
        }

        for (size_t next_v = 0; next_v < g.size(); ++next_v) {
            if (g.has_edge(curr_v, next_v) && !visited[next_v]) {
                visited[next_v] = true;
                path[count] = next_v;

                if (step(g, next_v, count + 1, visited, path)) {
                    return true;
                }

                visited[next_v] = false;
            }
        }
        return false;
    }
};
```
:::

---

## 2. Алгоритм Гелда-Карпа (Held-Karp Bitmask DP)

Алгоритм Гелда-Карпа корінним чином змінює підхід до обчислень: замість дослідження гілок рекурсивного дерева ми будуємо таблицю досяжності підмножин вершин у порядку зростання їх розміру.

### Бітові маски та операції над станами

У комп'ютерній реалізації підмножина вершин `S ⊆ V` кодується цілим беззнаковим числом — бітовою маскою `mask`. 

- Якщо `i`-й біт `mask & (1 << i)` дорівнює `1`, це означає, що вершина `vᵢ` належить до підмножини `S`.
- Додавання вершини `vᵢ` до підмножини виконується бітовим поразрядним АБО: `mask | (1 << i)`.
- Вилучення вершини `vᵢ` з підмножини виконується порозрядним І-НЕ: `mask & ~(1 << i)` або виключальним АБО `mask ^ (1 << i)`.

**Структура таблиці станів:**
Масив `dp[mask][v]` зберігає булеве значення `true` або `false`: чи існує простий шлях у графі `G`, який:
1. Починається у фіксованій початковій вершині `0`.
2. Відвідує рівно ті вершини, біти яких встановлені в одиницю у бітовій масці `mask`.
3. Закінчується у вершині `v` (причому біт `v` обов'язково встановлений у `mask`).

### Математичний перехід та реконструювання шляху

Послідовне заповнення таблиці здійснюється за розмірами масок від `|S| = 1` до `|S| = n`:

1. **Базовий стан (`|S| = 1`):** 
   Лише для стартової вершини `0` (бітова маска `1`):
   ```
   dp[1][0] = true
   ```
   Для всіх інших вершин `v ≠ 0` значення `dp[1][v] = false`.

2. **Заповнення для масок розміром від 2 до n:**
   Для кожної маски `mask`, яка містить вершину `0` (`mask & 1 == 1`) та має принаймні один інший встановлений біт, ми ітегруємо по всіх можливих кінцевих вершинах `v ∈ mask` (`v ≠ 0`).
   
   Значення `dp[mask][v]` обчислюється як диз'юнкція по всіх можливих попередниках `u ∈ (mask \ {v})`:
   ```
   dp[mask][v] = ⋁ { dp[mask \ {v}][u] ∧ HasEdge(u, v) }
   ```

3. **Замикання циклу (`|S| = n`):**
   Повний гамільтонів цикл існує тоді й лише тоді, коли для повної маски `full_mask = (1 << n) - 1` існує така вершина `v ≠ 0`, що:
   ```
   dp[full_mask][v] == true  AND  HasEdge(v, 0) == true
   ```

Для реконструкції самого порядку відвідування вершин використовується паралельний масив батьківських вказівників `parent[mask][v]`, який зберігає індекс вершини `u`, з якої було здійснено оптимальний перехід у стан `(mask, v)`. Після знаходження успішного замикаючого ребра `(v, 0)` алгоритм розмотує шлях у зворотному напрямку від `n - 1` до `0`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

bool solve_hamiltonian_held_karp(const graph_t *g, int *out_path) {
    int n = g->num_vertices;
    if (n < 3 || n > 31) return false;

    int num_states = 1 << n;
    bool **dp = (bool**)malloc(num_states * sizeof(bool*));
    int **parent = (int**)malloc(num_states * sizeof(int*));
    for (int i = 0; i < num_states; ++i) {
        dp[i] = (bool*)calloc(n, sizeof(bool));
        parent[i] = (int*)malloc(n * sizeof(int));
        for (int j = 0; j < n; ++j) parent[i][j] = -1;
    }

    dp[1][0] = true;

    for (int mask = 1; mask < num_states; ++mask) {
        if (!(mask & 1)) continue;

        for (int v = 0; v < n; ++v) {
            if (!(mask & (1 << v)) || !dp[mask][v]) continue;

            for (int next_v = 0; next_v < n; ++next_v) {
                if (mask & (1 << next_v)) continue;
                if (!g->adj_matrix[v][next_v]) continue;

                int next_mask = mask | (1 << next_v);
                dp[next_mask][next_v] = true;
                parent[next_mask][next_v] = v;
            }
        }
    }

    int full_mask = num_states - 1;
    int last_v = -1;

    for (int v = 1; v < n; ++v) {
        if (dp[full_mask][v] && g->adj_matrix[v][0]) {
            last_v = v;
            break;
        }
    }

    bool success = false;
    if (last_v != -1) {
        success = true;
        if (out_path) {
            int curr_mask = full_mask;
            int curr_v = last_v;
            for (int step = n - 1; step >= 1; --step) {
                out_path[step] = curr_v;
                int prev_v = parent[curr_mask][curr_v];
                curr_mask ^= (1 << curr_v);
                curr_v = prev_v;
            }
            out_path[0] = 0;
        }
    }

    for (int i = 0; i < num_states; ++i) {
        free(dp[i]);
        free(parent[i]);
    }
    free(dp);
    free(parent);

    return success;
}
```
```cpp
#include <vector>
#include <optional>
#include <cstdint>

class HeldKarpSolver {
public:
    static std::optional<std::vector<size_t>> solve(const Graph& graph) {
        const size_t n = graph.size();
        if (n < 3 || n > 30) return std::nullopt;

        const size_t num_states = 1ULL << n;
        std::vector<std::vector<uint8_t>> dp(num_states, std::vector<uint8_t>(n, 0));
        std::vector<std::vector<int32_t>> parent(num_states, std::vector<int32_t>(n, -1));

        dp[1][0] = 1;

        for (size_t mask = 1; mask < num_states; ++mask) {
            if (!(mask & 1)) continue;

            for (size_t v = 0; v < n; ++v) {
                if (!dp[mask][v]) continue;

                for (size_t next_v = 0; next_v < n; ++next_v) {
                    if (mask & (1ULL << next_v)) continue;
                    if (!graph.has_edge(v, next_v)) continue;

                    size_t next_mask = mask | (1ULL << next_v);
                    dp[next_mask][next_v] = 1;
                    parent[next_mask][next_v] = static_cast<int32_t>(v);
                }
            }
        }

        const size_t full_mask = num_states - 1;
        int32_t last_v = -1;

        for (size_t v = 1; v < n; ++v) {
            if (dp[full_mask][v] && graph.has_edge(v, 0)) {
                last_v = static_cast<int32_t>(v);
                break;
            }
        }

        if (last_v == -1) return std::nullopt;

        std::vector<size_t> path(n);
        size_t curr_mask = full_mask;
        size_t curr_v = static_cast<size_t>(last_v);

        for (size_t step = n - 1; step >= 1; --step) {
            path[step] = curr_v;
            int32_t prev_v = parent[curr_mask][curr_v];
            curr_mask ^= (1ULL << curr_v);
            curr_v = static_cast<size_t>(prev_v);
        }
        path[0] = 0;

        return path;
    }
};
```
:::

---

## 3. Оптимізація використання оперативної пам'яті

Найбільшим практичним обмеженням алгоритму Гелда-Карпа є високі вимоги до обсягу RAM для виділення масиву станів `O(2ⁿ · n)`.

### Техніка двох шарів (Two-Layer Dynamic Programming)

Якщо завдання полягає лише у перевірці **існування** гамільтонового циклу без виведення самого шляху, відпадає потреба зберігати стани для всіх `2ⁿ` масок одночасно.

Оскільки перехід до маски розміру `k + 1` вимагає знань лише про стани масок розміру `k`, ми можемо зберігати у пам'яті лише два шари таблиці:
- `dp_curr[v]` — стани для масок поточного розміру `k`.
- `dp_next[v]` — стани для масок наступного розміру `k + 1`.

При переході від `k` до `k + 1` ми очищаємо попередній шар та перевикористовуємо буфер. Максимальна кількість масок розміру `k` досягається у середині комбінаторного діапазону при `k = n / 2` і дорівнює біноміальному коефіцієнту `C(n, n/2)`. За формулою Стірлінга це дає зниження вимог до пам'яті у `~√(n)` разів, зберігаючи при цьому часову складність `O(2ⁿ · n²)`.

---

## 4. Складності та порівняльний аналіз підходів

Нижче наведено порівняльну таблицю часових та просторових характеристик розглянутих методів для графів різної розмірності.

| Параметр / Алгоритм | Простий перебір (Brute-force) | Алгоритм повернень з евристиками (Backtracking) | Алгоритм Гелда-Карпа (Held-Karp DP) | SAT-solver редукція (CDCL) |
| :--- | :--- | :--- | :--- | :--- |
| **Часова складність (найгірша)** | `O(n!)` | `O(n!)` | `O(2ⁿ · n²)` | Недетермінована `O(2ⁿ)` |
| **Просторова пам'ять** | `O(n)` | `O(n)` | `O(2ⁿ · n)` | `O(n² + m)` |
| **Приклад для `n = 20`** | `2.43 × 10¹⁸` операцій | `~10⁶..10⁹` операцій | `2.09 × 10⁸` операцій | `~10⁴` операцій |
| **Приклад для `n = 30`** | `2.65 × 10³²` операцій | Перевищення ліміту | `9.66 × 10¹¹` операцій | `~10⁶` операцій |
| **Область застосування** | Теоретична база | Розріджені графи (`n ≤ 50`) | Щільні графи (`n ≤ 30`) | Промислові задачі (`n > 100`) |

Практичний вибір між алгоритмом повернень та алгоритмом Гелда-Карпа визначається двома факторами: **щільністю ребер** та **розмірністю `n`**. Для розріджених графів (`m ≈ O(n)`) алгоритм повернень із відсіканням степеней працює значно швидше за динамічне програмування за рахунок швидкого виявлення тупиків. Для щільних графів (`m ≈ O(n²)`) при `n ≤ 30` алгоритм Гелда-Карпа є абсолютно переважним, оскільки гарантує фіксований час обчислення незалежно від комбінаторних пасток.
