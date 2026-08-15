# ⚙️ Практична реалізація перевірки двочастковості та пошуку максимального паросполучення

Ця вставка містить повністю працездатні реалізації двох ключових алгоритмів на двочасткових графах трьома мовами програмування: C, C++ та Python. Перший алгоритм виконує 2-розфарбовування вершин графа за допомогою обходу в ширину (BFS) для перевірки двочастковості за лінійний час `O(|V| + |E|)`. Другий алгоритм розв'язує задачу знаходження максимального двочасткового паросполучення методом пошуку збільшуючих шляхів (алгоритм Куна) за час `O(|V| · |E|)`.

## 1. Алгоритм перевірки двочастковості (2-розфарбовування графа)

### 1.1. Архітектура та покроковий механізм алгоритму

Перевірка двочастковості базується на теоремі Кеніга (1916): граф є двочастковим тоді й лише тоді, коли він не містить непарних циклів. Алгоритм намагається побудувати правильне 2-розфарбовування вершин за допомогою обходу в ширину (BFS).

Обхід відбувається наступним чином:
1. Ініціалізується масив кольорів `colors` розміром `|V|`, де кожна вершина отримує початкове значення `-1` (ще не відвідано).
2. Оскільки граф може складатися з кількох незв'язаних компонент зв'язності, зовнішній цикл перебирає всі вершини від `0` до `|V| - 1`. Якщо вершина вже має призначений колір, вона пропускається.
3. Для нової початкової вершини призначається Колір 0, і вона додається до черги BFS.
4. Поки черга не порожня, з неї вилучається поточна вершина `u`. Для кожного її сусіда `v`:
   - Якщо `colors[v] == -1`, вершині `v` призначається протилежний колір `1 - colors[u]`, і вона додається в чергу BFS.
   - Якщо `colors[v] == colors[u]`, виявлено ребро між вершинами одного кольору! Це свідчить про наявність непарного циклу. Алгоритм негайно зупиняється й повертає ознаку конфлікту.
5. Якщо всі компоненти успішно розфарбовано без конфліктів, граф є двочастковим, а масив `colors` задає шукане розбиття на частки.

### 1.2. Розбір реалізації у C: керування динамічною пам'яттю

У реалізації мовою C граф подається через структуру `Graph`, яка зберігає кількість вершин `num_vertices`, масив степенів `deg`, масив ємностей `capacity` та двовимірний динамічний масив `adj`. Для запобігання частим перевиділенням пам'яті використовується стратегія геометричного подвоєння ємності (`capacity *= 2`) при виклику `realloc`. Очищення пам'яті виконується функцією `graph_free`, яка послідовно звільняє кожен список суміжності.

### 1.3. Розбір реалізації у C++: контейнери та обгортка `std::optional`

У C++ реалізації використовується клас `BipartiteChecker`, який інкапсулює списки суміжності у контейнері `std::vector<std::vector<std::size_t>>`. Результат перевірки повертається через безпечний тип `std::optional<std::vector<int>>`. Якщо граф є двочастковим, метод повертає обгортку із вектором кольорів; якщо виявлено непарний цикл, повертається `std::nullopt`. Метод позначено атрибутом `[[nodiscard]]`, що змушує компілятор генерувати попередження, якщо результат перевірки ігнорується розробником.

### 1.4. Розбір реалізації у Python: аннотації типів та `collections.deque`

У Python реалізації функція `check_bipartite` приймає кількість вершин `n` та список ребер. Для ефективної роботи черги BFS використовується двосторонній список `collections.deque`, який забезпечує вилучення елементів з голови за константний час `O(1)` (на відміну від звичайного списку Python, де `pop(0)` коштує `O(N)`).

:::tabs
```c
/* C Implementation: BFS 2-coloring for Bipartite Verification */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int num_vertices;
    int **adj;
    int *deg;
    int *capacity;
} Graph;

Graph* graph_create(int n) {
    Graph *g = (Graph*)malloc(sizeof(Graph));
    if (!g) return NULL;
    g->num_vertices = n;
    g->adj = (int**)malloc(n * sizeof(int*));
    g->deg = (int*)calloc(n, sizeof(int));
    g->capacity = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        g->capacity[i] = 4;
        g->adj[i] = (int*)malloc(g->capacity[i] * sizeof(int));
    }
    return g;
}

void graph_add_edge(Graph *g, int u, int v) {
    if (g->deg[u] >= g->capacity[u]) {
        g->capacity[u] *= 2;
        g->adj[u] = (int*)realloc(g->adj[u], g->capacity[u] * sizeof(int));
    }
    g->adj[u][g->deg[u]++] = v;

    if (g->deg[v] >= g->capacity[v]) {
        g->capacity[v] *= 2;
        g->adj[v] = (int*)realloc(g->adj[v], g->capacity[v] * sizeof(int));
    }
    g->adj[v][g->deg[v]++] = u;
}

void graph_free(Graph *g) {
    if (!g) return;
    for (int i = 0; i < g->num_vertices; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g->deg);
    free(g->capacity);
    free(g);
}

// Повертає true, якщо граф двочастковий; заповнює масив colors (0 або 1, -1 якщо непризначено)
bool check_bipartite_c(const Graph *g, int *colors) {
    int n = g->num_vertices;
    for (int i = 0; i < n; i++) {
        colors[i] = -1;
    }

    int *queue = (int*)malloc(n * sizeof(int));
    if (!queue) return false;

    for (int start = 0; start < n; start++) {
        if (colors[start] != -1) continue;

        int head = 0, tail = 0;
        colors[start] = 0;
        queue[tail++] = start;

        while (head < tail) {
            int u = queue[head++];
            int current_color = colors[u];
            int next_color = 1 - current_color;

            for (int i = 0; i < g->deg[u]; i++) {
                int v = g->adj[u][i];
                if (colors[v] == -1) {
                    colors[v] = next_color;
                    queue[tail++] = v;
                } else if (colors[v] == current_color) {
                    free(queue);
                    return false; // Конфлікт розфарбування (знайдено непарний цикл)
                }
            }
        }
    }

    free(queue);
    return true;
}
```
```cpp
// C++ Implementation: Idiomatic BFS 2-coloring with std::optional
#include <vector>
#include <queue>
#include <optional>
#include <iostream>
#include <cstddef>

class BipartiteChecker {
public:
    explicit BipartiteChecker(std::size_t vertices) : adj_(vertices) {}

    void add_edge(std::size_t u, std::size_t v) {
        adj_.at(u).push_back(v);
        adj_.at(v).push_back(u);
    }

    // Повертає вектор кольорів (0 або 1) або std::nullopt у разі непарного циклу
    [[nodiscard]] std::optional<std::vector<int>> check_bipartite() const {
        std::size_t n = adj_.size();
        std::vector<int> colors(n, -1);

        for (std::size_t start = 0; start < n; ++start) {
            if (colors[start] != -1) continue;

            std::queue<std::size_t> q;
            colors[start] = 0;
            q.push(start);

            while (!q.empty()) {
                std::size_t u = q.front();
                q.pop();

                int next_color = 1 - colors[u];

                for (std::size_t v : adj_[u]) {
                    if (colors[v] == -1) {
                        colors[v] = next_color;
                        q.push(v);
                    } else if (colors[v] == colors[u]) {
                        return std::nullopt; // Знайдено непарний цикл!
                    }
                }
            }
        }
        return colors;
    }

private:
    std::vector<std::vector<std::size_t>> adj_;
};
```
```python
# Python Implementation: Type-annotated BFS 2-coloring
from collections import deque
from typing import List, Optional, Tuple

def check_bipartite(n: int, edges: List[Tuple[int, int]]) -> Optional[List[int]]:
    """
    Перевіряє двочастковість графа з n вершинами (0..n-1).
    Повертає список кольорів [0, 1] для кожної вершини або None при наявності непарного циклу.
    """
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    colors = [-1] * n

    for start in range(n):
        if colors[start] != -1:
            continue

        colors[start] = 0
        queue = deque([start])

        while queue:
            u = queue.popleft()
            next_color = 1 - colors[u]

            for v in adj[u]:
                if colors[v] == -1:
                    colors[v] = next_color
                    queue.append(v)
                elif colors[v] == colors[u]:
                    return None  # Знайдено непарний цикл!

    return colors
```
:::

---

## 2. Пошук максимального двочасткового паросполучення (Алгоритм Куна)

### 2.1. Метод збільшуючих шляхів та рекурсивна реорганізація

Алгоритм Куна розв'язує задачу знаходження максимального паросполучення методом пошуку збільшуючих шляхів (знаного також як теорема Бержа 1957 року). 

Процес обчислення побудовано на послідовному рекурсивному розширенні:
1. Для кожної вершини лівої частки `u ∈ U` запускається процедура рекурсивного пошуку `try_kuhn` у глибину (DFS).
2. Масив `visited` очищається перед кожним запуском для `u`, що дозволяє відстежувати вершини частки `U`, вже відвідані під час поточного пошуку збільшуючого шляху.
3. Якщо для `u` знайдено вільну вершину `v ∈ V` (`match_v[v] == -1`), ребро `(u, v)` негайно додається до паросполучення (`match_v[v] = u`), і процедура повертає `true`.
4. Якщо ж вершина `v` вже зайнята іншою вершиною `u' = match_v[v]`, рекурсивний виклик `try_kuhn(u')` намагається знайти альтернативний збільшуючий шлях для `u'`. Якщо такий шлях існує, вершина `u'` перенаправляється на новий вузол, а ребро `(u, v)` переходить до `u`.
5. Кількість знайдених успішних збільшуючих шляхів точно дорівнює розміру максимального паросполучення `ν(G)`.

Часова складність алгоритму Куна в найгіршому випадку становить `O(|V| · |E|)`.

### 2.2. Детальний покроковий приклад виконання

Розглянемо граф із двома вершинами в `U` (`u₀, u₁`) та двома в `V` (`v₀, v₁`) з ребрами `(u₀, v₀)`, `(u₀, v₁)`, `(u₁, v₀)`:

1. **Крок 1 (u₀):** DFS знаходить вільну вершину `v₀`. Призначається `match_v[v₀] = u₀`. Розмір паросполучення дорівнює 1.
2. **Крок 2 (u₁):** DFS перевіряє `v₀`. Вершина `v₀` зайнята `u₀`. Алгоритм рекурсивно запускає `try_kuhn(u₀)`. Для `u₀` виявляється альтернативне вільне ребро `v₁`. Призначається `match_v[v₁] = u₀`, після чого вершина `v₀` звільняється для `u₁`: `match_v[v₀] = u₁`.
3. **Підсумок:** Отримано максимальне паросполучення з двох ребер: `{(u₀, v₁), (u₁, v₀)}`.

### 2.3. Повна реалізація трьома мовами

:::tabs
```c
/* C Implementation: Kuhn's Algorithm for Maximum Bipartite Matching */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int n1; // Розмір лівої частки U
    int n2; // Розмір правої частки V
    int **adj;
    int *deg;
    int *capacity;
} BipartiteGraph;

BipartiteGraph* bg_create(int n1, int n2) {
    BipartiteGraph *g = (BipartiteGraph*)malloc(sizeof(BipartiteGraph));
    if (!g) return NULL;
    g->n1 = n1;
    g->n2 = n2;
    g->adj = (int**)malloc(n1 * sizeof(int*));
    g->deg = (int*)calloc(n1, sizeof(int));
    g->capacity = (int*)malloc(n1 * sizeof(int));
    for (int i = 0; i < n1; i++) {
        g->capacity[i] = 4;
        g->adj[i] = (int*)malloc(g->capacity[i] * sizeof(int));
    }
    return g;
}

void bg_add_edge(BipartiteGraph *g, int u_left, int v_right) {
    if (g->deg[u_left] >= g->capacity[u_left]) {
        g->capacity[u_left] *= 2;
        g->adj[u_left] = (int*)realloc(g->adj[u_left], g->capacity[u_left] * sizeof(int));
    }
    g->adj[u_left][g->deg[u_left]++] = v_right;
}

static bool try_kuhn(int u, const BipartiteGraph *g, bool *visited, int *match_v) {
    if (visited[u]) return false;
    visited[u] = true;

    for (int i = 0; i < g->deg[u]; i++) {
        int v = g->adj[u][i];
        if (match_v[v] < 0 || try_kuhn(match_v[v], g, visited, match_v)) {
            match_v[v] = u;
            return true;
        }
    }
    return false;
}

int max_bipartite_matching_c(const BipartiteGraph *g, int *match_v) {
    for (int i = 0; i < g->n2; i++) {
        match_v[i] = -1;
    }

    bool *visited = (bool*)malloc(g->n1 * sizeof(bool));
    if (!visited) return 0;
    int result = 0;

    for (int u = 0; u < g->n1; u++) {
        memset(visited, 0, g->n1 * sizeof(bool));
        if (try_kuhn(u, g, visited, match_v)) {
            result++;
        }
    }

    free(visited);
    return result;
}

void bg_free(BipartiteGraph *g) {
    if (!g) return;
    for (int i = 0; i < g->n1; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g->deg);
    free(g->capacity);
    free(g);
}
```
```cpp
// C++ Implementation: Kuhn's Algorithm using Modern C++ Standard Containers
#include <vector>
#include <utility>
#include <iostream>
#include <cstddef>
#include <algorithm>

class KuhnMatcher {
public:
    KuhnMatcher(std::size_t left_size, std::size_t right_size)
        : n1_(left_size), n2_(right_size), adj_(left_size), match_v_(right_size, -1) {}

    void add_edge(std::size_t u_left, std::size_t v_right) {
        adj_.at(u_left).push_back(v_right);
    }

    // Обчислює максимальне паросполучення і повертає список пар (u_left, v_right)
    [[nodiscard]] std::vector<std::pair<std::size_t, std::size_t>> find_max_matching() {
        std::fill(match_v_.begin(), match_v_.end(), -1);
        std::vector<bool> visited(n1_, false);

        for (std::size_t u = 0; u < n1_; ++u) {
            std::fill(visited.begin(), visited.end(), false);
            try_augment(u, visited);
        }

        std::vector<std::pair<std::size_t, std::size_t>> matching;
        for (std::size_t v = 0; v < n2_; ++v) {
            if (match_v_[v] != -1) {
                matching.emplace_back(static_cast<std::size_t>(match_v_[v]), v);
            }
        }
        return matching;
    }

private:
    bool try_augment(std::size_t u, std::vector<bool>& visited) {
        if (visited[u]) return false;
        visited[u] = true;

        for (std::size_t v : adj_[u]) {
            if (match_v_[v] == -1 || try_augment(static_cast<std::size_t>(match_v_[v]), visited)) {
                match_v_[v] = static_cast<int>(u);
                return true;
            }
        }
        return false;
    }

    std::size_t n1_;
    std::size_t n2_;
    std::vector<std::vector<std::size_t>> adj_;
    std::vector<int> match_v_;
};
```
```python
# Python Implementation: Object-Oriented Kuhn's Matching Solver
from typing import List, Tuple

class BipartiteMatchingKuhn:
    def __init__(self, n_left: int, n_right: int):
        self.n1 = n_left
        self.n2 = n_right
        self.adj: List[List[int]] = [[] for _ in range(n_left)]

    def add_edge(self, u_left: int, v_right: int) -> None:
        self.adj[u_left].append(v_right)

    def find_max_matching(self) -> List[Tuple[int, int]]:
        """
        Знаходить максимальне двочасткове паросполучення.
        Повертає список пар вершин (u_left, v_right).
        """
        match_v = [-1] * self.n2

        def try_augment(u: int, visited: List[bool]) -> bool:
            if visited[u]:
                return False
            visited[u] = True

            for v in self.adj[u]:
                if match_v[v] == -1 or try_augment(match_v[v], visited):
                    match_v[v] = u
                    return True
            return False

        for u in range(self.n1):
            visited = [False] * self.n1
            try_augment(u, visited)

        return [(u, v) for v, u in enumerate(match_v) if u != -1]
```
:::

---

## 3. Аналіз крайових випадків та порівняльні бенчмарки

При застосуванні поданих реалізацій у продакшн-системах слід враховувати поведінку алгоритмів на крайових ситуаціях:

1. **Ізольовані вершини:** Якщо граф містить вершини зі ступенем 0, BFS-перевірка розфарбовує їх у Колір 0 і продовжує обхід. Алгоритм Куна ігнорує їх, оскільки для них списки суміжності порожні.
2. **Незв'язані графи:** Зворотний цикл за `start` від 0 до `N-1` гарантує, що алгоритм обробить абсолютно всі окремі компоненти зв'язності.
3. **Порівняння алгоритмів Куна та Гопкрофта-Карпа:** Для розріджених графів (`|E| ≈ |V|`) алгоритм Куна працює за `O(|V|²)`, що є чудовим вибором для графів обсягом `|V| ≤ 10 000`. На надвеликих графах (`|V| > 100 000`) слід використовувати алгоритм Гопкрофта-Карпа (`O(|E| · √|V|)`).
