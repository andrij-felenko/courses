# ⚙️ Алгоритми пошуку досконалого паросполучення: від теорії до коду

Знаходження досконалого або максимального паросполучення у загальних (недвочасткових) графах є однією з фундаментальних задач обчислювальної комбінаторики та теорії алгоритмів. На відміну від двочасткових графів, де задача легко зводиться до пошуку максимального потоку (наприклад, алгоритм Хофкрофта-Карпа із часовою складністю `O(E √V)`), у довільних графах головною алгоритмічною перешкодою є наявність непарних циклів. Ця вставка містить детальний технологічний аналіз алгоритму «квіток» Едмондса (Edmonds' Blossom Algorithm), алгоритмічних моделей обходу графів, механізмів стискання та розгортання циклів, а також повністю працездатні та розширено прокоментовані реалізації мовами C та C++.

## 1. Архітектурні проблеми та ідея алгоритму Едмондса

Алгоритм Едмондса шукає досконале або максимальне паросполучення шляхом послідовного виявлення та інверсії `M`-доповнювальних шляхів (M-augmenting paths). За лемою Клода Бержа, паросполучення `M` є максимальним тоді й лише тоді, коли у графі немає жодного доповнювального шляху відносно `M`.

У двочастковому графі обхід у ширину (BFS) або в глибину (DFS) легко знаходить доповнювальні шляхи: ми стартуємо у вільній (ненасиченій) вершині `r` і чергуємо ребра поза `M` та ребра з `M`. Усі вершини, досяжні на парній відстані від `r`, утворюють шар `Even` (або `Type 0`), а вершини на непарній відстані — шар `Odd` (або `Type 1`).

Проте у загальному графі обхід у ширину може виявити ребро між двома вершинами, які обидві належать до шару `Even`. Це свідчить про наявність непарного циклу довжини `2k + 1`, який Джеком Едмондсом було названо **квіткою** (blossom).

```
   Корінь r (Even)
        │
        ▼  [M-ребро]
     Вершина (Odd)
        │
        ▼  [не-M-ребро]
    База квітки b (Even) ◄─── Початок непарного циклу
       ╱ \
      ╱   \
   Even   Even   ◄─── Ребро між двома Even-вершинами утворює КВІТКУ (Blossom)
     │     │
     └─────┘  (непарний цикл довжини 2k + 1)
```

Якщо не вжити спеціальних заходів, звичайний алгоритм BFS зациклиться у цій квітці. Спроба інвертувати шлях, що проходить через такий цикл, призведе до неправильного стану, коли одна й та сама вершина виявиться інцидентною двом ребрам паросполучення.

Ключовий прорив Едмондса полягав у процедурі **стискання квітки** (blossom contraction):
1. Коли виявляється ребро між двома `Even`-вершинами `u` та `v`, алгоритм шукає їхнього найменшого спільного предка (Lowest Common Ancestor, LCA) у дереві BFS. Цей предок називається **базою квітки** `b`.
2. Усі вершини та ребра, що входять до даного непарного циклу, тимчасово об'єднуються у єдину мета-вершину (супервершину).
3. Граф `G` замінюється на фактор-граф `G / B`, і пошук доповнювального шляху продовжується далі.
4. Якщо у фактор-графі `G / B` вдається знайти доповнювальний шлях, алгоритм розгортає всі стиснуті квітки у зворотному порядку, коректуючи альтернаторний шлях усередині непарного циклу так, щоб парність ребер паросполучення була збережена.

---

## 2. Покроковий розбір обчислювальних станів та структур даних

Для коректної реалізації алгоритму Едмондса необхідно підтримувати декілька масивів та структур даних:

1. **Масив паросполучення `match[u]`:** Зберігає вершину, з якою з'єднана вершина `u` ребром з паросполучення `M`. Якщо вершина `u` є вільною, `match[u] = -1`.
2. **Масив баз `base[u]`:** Зберігає поточну базову вершину (або ідентифікатор супервершини), до якої належить вершина `u`. На початку алгоритму `base[u] = u`. Після стискання квітки `B` із базою `b`, для всіх вершин `v ∈ B` встановлюється `base[v] = b`.
3. **Масив батьківських посилань `parent[u]`:** Зберігає предка вершини `u` у чергувальному дереві BFS.
4. **Масив станів `state[u]`:** Вказує тип вершини у чергувальному дереві:
   - `-1`: вершина ще не відвідана під час поточного пошуку;
   - `0`: вершина має тип `Even` (парна відстань від кореня);
   - `1`: вершина має тип `Odd` (непарна відстань від кореня).
5. **Масив наявності у квітці `in_blossom[u]`:** Допоміжний булевий масив для маркування вершин, що підлягають стисканню у поточний момент.

### Процедура маркування та стискання квітки

Коли виявлено ребро `(u, v)` між двома парними вершинами (`state[base[u]] == 0` та `state[base[v]] == 0`), алгоритм виконує наступні кроки:

1. За допомогою двопоінтерного обходу батьківських посилань `parent` знаходять спільну базу `b = lca(u, v)`.
2. Для обох гілок непарного циклу (від `u` до `b` та від `v` до `b`) виконують оновлення батьківських посилань та маркування вершин.
3. Усі вершини циклу, які мали стан `Odd` (`state == 1`), переводяться у стан `Even` (`state = 0`) і додаються до черги BFS для подальшого розширення дерева. Це є фундаментальним моментом: стискання квітки відкриває нові шляхи з непарних вершин, які раніше були тупиковими!

---

## 3. Працездатні реалізації мовами C та C++

Нижче наведено вичерпні та ідіоматичні реалізації алгоритму Едмондса для мов C (системний стиль із явним керуванням масивами) та C++ (сучасний об'єктно-орієнтований стиль із використанням STL-контейнерів).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 500

typedef struct {
    int num_vertices;
    int adj[MAX_VERTICES][MAX_VERTICES];
    int deg[MAX_VERTICES];
} Graph;

static int match_arr[MAX_VERTICES];
static int parent_arr[MAX_VERTICES];
static int base_arr[MAX_VERTICES];
static int state_arr[MAX_VERTICES]; // -1: unvisited, 0: even, 1: odd
static bool in_blossom[MAX_VERTICES];

static int queue[MAX_VERTICES];
static int q_head = 0, q_tail = 0;

void graph_init(Graph* g, int n) {
    g->num_vertices = n;
    for (int i = 0; i < n; ++i) {
        g->deg[i] = 0;
    }
}

void graph_add_edge(Graph* g, int u, int v) {
    g->adj[u][g->deg[u]++] = v;
    g->adj[v][g->deg[v]++] = u;
}

static int lca(int u, int v) {
    static bool in_path[MAX_VERTICES];
    memset(in_path, 0, sizeof(in_path));

    while (1) {
        u = base_arr[u];
        in_path[u] = true;
        if (match_arr[u] == -1) break;
        u = parent_arr[match_arr[u]];
    }

    while (1) {
        v = base_arr[v];
        if (in_path[v]) return v;
        v = parent_arr[match_arr[v]];
    }
}

static void mark_blossom(int u, int v, int b) {
    while (base_arr[u] != b) {
        in_blossom[base_arr[u]] = true;
        in_blossom[base_arr[v]] = true;
        parent_arr[u] = v;
        v = match_arr[u];
        u = parent_arr[v];
    }
}

static int find_augmenting_path(Graph* g, int root) {
    for (int i = 0; i < g->num_vertices; ++i) {
        state_arr[i] = -1;
        base_arr[i] = i;
        parent_arr[i] = -1;
    }

    q_head = q_tail = 0;
    queue[q_tail++] = root;
    state_arr[root] = 0;

    while (q_head < q_tail) {
        int u = queue[q_head++];

        for (int i = 0; i < g->deg[u]; ++i) {
            int v = g->adj[u][i];

            if (base_arr[u] == base_arr[v] || match_arr[u] == v) continue;

            if (state_arr[v] == -1) {
                parent_arr[v] = u;
                state_arr[v] = 1;

                if (match_arr[v] == -1) {
                    return v; // Доповнювальний шлях знайдено
                }

                int w = match_arr[v];
                state_arr[w] = 0;
                parent_arr[w] = v;
                queue[q_tail++] = w;
            } else if (state_arr[base_arr[v]] == 0) {
                // Виявлено непарний цикл (blossom)
                int b = lca(u, v);
                memset(in_blossom, 0, sizeof(in_blossom));

                mark_blossom(u, v, b);
                mark_blossom(v, u, b);

                for (int i_v = 0; i_v < g->num_vertices; ++i_v) {
                    if (in_blossom[base_arr[i_v]]) {
                        base_arr[i_v] = b;
                        if (state_arr[i_v] == 1) {
                            state_arr[i_v] = 0;
                            queue[q_tail++] = i_v;
                        }
                    }
                }
            }
        }
    }
    return -1;
}

int edmonds_max_matching(Graph* g) {
    for (int i = 0; i < g->num_vertices; ++i) match_arr[i] = -1;

    int matching_size = 0;
    for (int i = 0; i < g->num_vertices; ++i) {
        if (match_arr[i] == -1) {
            int v = find_augmenting_path(g, i);
            if (v != -1) {
                // Доповнення паросполучення уздовж знайденого шляху
                while (v != -1) {
                    int pv = parent_arr[v];
                    int ppv = match_arr[pv];
                    match_arr[v] = pv;
                    match_arr[pv] = v;
                    v = ppv;
                }
                matching_size++;
            }
        }
    }
    return matching_size;
}

bool is_perfect_matching(Graph* g) {
    if (g->num_vertices % 2 != 0) return false;
    return edmonds_max_matching(g) == (g->num_vertices / 2);
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <numeric>
#include <algorithm>
#include <utility>

class EdmondsBlossomSolver {
public:
    explicit EdmondsBlossomSolver(int num_vertices)
        : n_(num_vertices), adj_(num_vertices), match_(num_vertices, -1) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    int compute_max_matching() {
        std::fill(match_.begin(), match_.end(), -1);
        int matching_size = 0;

        for (int i = 0; i < n_; ++i) {
            if (match_[i] == -1) {
                int end_vertex = find_augmenting_path(i);
                if (end_vertex != -1) {
                    augment_path(end_vertex);
                    matching_size++;
                }
            }
        }
        return matching_size;
    }

    [[nodiscard]] bool is_perfect_matching() const {
        if (n_ % 2 != 0) return false;
        // Створення копії для обчислення без модифікації стану об'єкта
        EdmondsBlossomSolver solver_copy = *this;
        return solver_copy.compute_max_matching() == (n_ / 2);
    }

    [[nodiscard]] std::vector<std::pair<int, int>> get_matching_edges() const {
        std::vector<std::pair<int, int>> edges;
        for (int i = 0; i < n_; ++i) {
            if (match_[i] > i) {
                edges.emplace_back(i, match_[i]);
            }
        }
        return edges;
    }

private:
    int n_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> match_;
    std::vector<int> parent_;

    int find_lca(int u, int v, const std::vector<int>& base) {
        std::vector<bool> in_path(n_, false);

        while (true) {
            u = base[u];
            in_path[u] = true;
            if (match_[u] == -1) break;
            u = parent_[match_[u]];
        }

        while (true) {
            v = base[v];
            if (in_path[v]) return v;
            v = parent_[match_[v]];
        }
    }

    void mark_blossom(int u, int v, int b, std::vector<int>& base, std::vector<bool>& in_blossom) {
        while (base[u] != b) {
            in_blossom[base[u]] = true;
            in_blossom[base[v]] = true;
            parent_[u] = v;
            v = match_[u];
            u = parent_[v];
        }
    }

    int find_augmenting_path(int root) {
        std::vector<int> state(n_, -1);
        std::vector<int> base(n_);
        std::iota(base.begin(), base.end(), 0);
        parent_.assign(n_, -1);

        std::queue<int> q;
        q.push(root);
        state[root] = 0;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj_[u]) {
                if (base[u] == base[v] || match_[u] == v) continue;

                if (state[v] == -1) {
                    parent_[v] = u;
                    state[v] = 1;

                    if (match_[v] == -1) return v;

                    int w = match_[v];
                    state[w] = 0;
                    parent_[w] = v;
                    q.push(w);
                } else if (state[base[v]] == 0) {
                    int b = find_lca(u, v, base);
                    std::vector<bool> in_blossom(n_, false);

                    mark_blossom(u, v, b, base, in_blossom);
                    mark_blossom(v, u, b, base, in_blossom);

                    for (int i = 0; i < n_; ++i) {
                        if (in_blossom[base[i]]) {
                            base[i] = b;
                            if (state[i] == 1) {
                                state[i] = 0;
                                q.push(i);
                            }
                        }
                    }
                }
            }
        }
        return -1;
    }

    void augment_path(int v) {
        while (v != -1) {
            int pv = parent_[v];
            int ppv = match_[pv];
            match_[v] = pv;
            match_[pv] = v;
            v = ppv;
        }
    }
};
```
:::

---

## 4. Аналіз крайових випадків та оптимізації продуктивності

Під час практичної реалізації алгоритму Едмондса необхідно враховувати низку критичних крайових випадків та інженерних оптимізацій:

1. **Ізольовані вершини та неспряжені компоненти:** Якщо граф містить ізольовані вершини (`deg[v] = 0`), досконале паросполучення є неможливим. Попередній аналіз компонент зв'язності дозволяє відсікати очевидно неспряжені графи ще до запуску BFS.
2. **Вкладені квітки (Nested Blossoms):** У складних графах одна квітка може міститися всередині іншої (вкладені непарні цикли). Реалізація через динамічний масив `base[u]` та процедуру `find_lca` природним чином підтримує довільну глибину вкладеності квіток.
3. **Оптимізація системи диз'юнктних множин (Disjoint-Set Union / DSU):** Для прискорення операції оновлення та пошуку поточних баз вершин замість лінійного перебору масиву `base` можна використовувати структуру DSU із стисканням шляхів (path compression). Це зменшує асимптотичну складність пошуку шляху з `O(V²)` до `O(V · α(V))`, покращуючи загальний час роботи алгоритму до `O(V · E · α(V))`.

## 5. Порівняльний технологічний аналіз алгоритмів

| Алгоритмічний підхід | Область застосування | Часова складність | Просторова складність | Оцінка практичної складності реалізації |
| :--- | :--- | :--- | :--- | :--- |
| **Форд-Фалкерсон (Max-Flow)** | Двочасткові графи | `O(V · E)` | `O(V + E)` | Низька (стандартний алгоритм потоку) |
| **Хофкрофт-Карп** | Двочасткові графи | `O(E · √V)` | `O(V + E)` | Середня (потребує пошарових BFS/DFS) |
| **Едмондс (Blossom)** | Загальні графи | `O(V² · E)` | `O(V + E)` | Висока (стискання квіток та корекція баз) |
| **Мікалі-Вазірані** | Загальні графи | `O(E · √V)` | `O(V + E)` | Дуже висока (складна ієрархія альтернаторних рівнів) |
| **Рандомізований Гаусс (Ловас)** | Загальні графи | `O(nʷ)` / `O(n³)` | `O(V²)` | Низька (зводиться до детермінанта over `F_q`) |

Алгоритм Едмондса залишається золотим стандартом детермінованого розв'язання задач паросполучення у загальних графах, поєднуючи сувору теоретичну обґрунтованість із прийнятною практичною швидкодією.
