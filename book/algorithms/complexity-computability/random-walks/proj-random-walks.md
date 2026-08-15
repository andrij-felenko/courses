# ⚙️ Реалізація алгоритмів випадкових блукань: s-t зв'язність, PageRank та алгоритм Уїлсона

У цій практичній вставці розглядається програмна реалізація трьох фундаментальних алгоритмів на графах, розроблених на основі випадкових блукань:
1. **Імовірнісна перевірка s-t зв'язності (Aleliunas Walk)** з обмеженням пам'яті `O(log n)`.
2. **Обчислення рангу сторінок (PageRank)** методом Монте-Карло блукань.
3. **Алгоритм Уїлсона (Wilson's UST)** для побудови рівномірно випадкового кістякового дерева через блукання з вилученням циклів.

---

## 1. Алгоритм перевірки s-t зв'язності у логарифмічній пам'яті (Aleliunas Walk)

### Задача та обчислювальна ідея
Дано неорієнтований граф `G = (V, E)` з `n` вершинами та дві вершини `s, t ∈ V`. Необхідно перевірити, чи існує шлях між початковою вершиною `s` та цільовою вершиною `t`.

Класичні алгоритми детермінованого обходу графів, такі як пошук у глибину (DFS) чи в ширину (BFS), вимагають збереження списку відвіданих вершин або черги, що вимагає щонайменше `O(n)` біт пам'яті (`O(n log n)` для вказівників). У системних середовищах із жорстким обмеженням ресурсів (наприклад, у мікроконтролерах або при виконанні обчислень у логарифмічній пам'яті класу `RL`) такий обсяг є недопустимим.

Алгоритм Алелюнаса — Карпа — Ліптона — Ловаса — Рака (1979) розв'язує цю задачу за допомогою стохастичного блукання. Блукач випускається з початкової вершини `s` і здійснює не більше `N_steps = 2m · n` кроків. На кожному кроці обирається довільне суміжне ребло з імовірністю `1 / d(u)`. Якщо під час блукання блукач торкається вершини `t`, граф є безперечно зв'язним між `s` та `t` (алгоритм повертає `true` із нульовою помилкою першого роду). 

Якщо за `N_steps` кроків вершину `t` не відвідано, за нерівністю Маркова ймовірність того, що шлях існує, але блукач його не знайшов, не перевищує `1/2`. Повторивши блукання `max_runs` разів на нових незалежних випадкових бітах, імовірність хибного рішення `false` зменшується до експоненційно малого рівня `(1/2)ᵏ`. Для виконання цього алгоритму програмі не потрібно зберігати історію відвіданих вершин: єдиними змінними є номер поточної вершини та лічильник виконаних кроків, що вимагає лише `O(log n)` біт робочої пам'яті.

### Реалізація коду

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int num_vertices;
    int num_edges;
    int** adj;
    int* degrees;
} GraphC;

GraphC* graph_create(int n) {
    GraphC* g = (GraphC*)malloc(sizeof(GraphC));
    g->num_vertices = n;
    g->num_edges = 0;
    g->degrees = (int*)calloc(n, sizeof(int));
    g->adj = (int**)malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        g->adj[i] = NULL;
    }
    return g;
}

void graph_add_edge(GraphC* g, int u, int v) {
    g->degrees[u]++;
    g->adj[u] = (int*)realloc(g->adj[u], g->degrees[u] * sizeof(int));
    g->adj[u][g->degrees[u] - 1] = v;

    g->degrees[v]++;
    g->adj[v] = (int*)realloc(g->adj[v], g->degrees[v] * sizeof(int));
    g->adj[v][g->degrees[v] - 1] = u;

    g->num_edges++;
}

void graph_free(GraphC* g) {
    for (int i = 0; i < g->num_vertices; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g->degrees);
    free(g);
}

// Імовірнісна перевірка s-t зв'язності (O(1) додаткової пам'яті окрім графа)
bool random_walk_st_connectivity(const GraphC* g, int s, int t, int max_runs) {
    if (s == t) return true;
    if (g->degrees[s] == 0 || g->degrees[t] == 0) return false;

    // Теоретична межа кроків: 2 * m * n
    long long max_steps = 2LL * g->num_edges * g->num_vertices;

    for (int run = 0; run < max_runs; run++) {
        int current = s;
        for (long long step = 0; step < max_steps; step++) {
            int deg = g->degrees[current];
            int next_idx = rand() % deg;
            current = g->adj[current][next_idx];

            if (current == t) {
                return true; // Шлях знайдено!
            }
        }
    }
    return false; // Шлях з високою ймовірністю відсутній
}
```
```cpp
#include <vector>
#include <random>
#include <iostream>
#include <cstdint>

class Graph {
public:
    explicit Graph(size_t vertices) : adj_(vertices) {}

    void add_edge(size_t u, size_t v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
        num_edges_++;
    }

    [[nodiscard]] size_t num_vertices() const noexcept { return adj_.size(); }
    [[nodiscard]] size_t num_edges() const noexcept { return num_edges_; }
    [[nodiscard]] const std::vector<size_t>& neighbors(size_t u) const { return adj_[u]; }

private:
    std::vector<std::vector<size_t>> adj_;
    size_t num_edges_{0};
};

class RandomWalkChecker {
public:
    explicit RandomWalkChecker(uint32_t seed = 42) : rng_(seed) {}

    // Перевірка s-t зв'язності з мінімальним споживанням пам'яті
    bool check_st_connectivity(const Graph& g, size_t s, size_t t, size_t max_runs = 5) {
        if (s == t) return true;
        if (g.neighbors(s).empty() || g.neighbors(t).empty()) return false;

        const uint64_t max_steps = 2ULL * g.num_edges() * g.num_vertices();

        for (size_t run = 0; run < max_runs; ++run) {
            size_t current = s;
            for (uint64_t step = 0; step < max_steps; ++step) {
                const auto& neighbors = g.neighbors(current);
                std::uniform_int_distribution<size_t> dist(0, neighbors.size() - 1);
                current = neighbors[dist(rng_)];

                if (current == t) {
                    return true;
                }
            }
        }
        return false;
    }

private:
    std::mt19937 rng_;
};
```
:::

---

## 2. Обчислення PageRank методом Монте-Карло блукань

### Задача та алгоритмічні особливості
Дано орієнтований граф `G = (V, E)`, що моделює топологію веб-сторінок та гіперпосилань. Необхідно розрахувати вектор весов `PageRank`, який виражає важливість кожної вершини.

Класичний метод обчислення PageRank спирається на степеневі ітерації (Power Iteration) та множення векторов на гігантські матриці суміжності. У розподілених системах обробки даних (таких як Apache Spark або MapReduce) альтернативним підходом є **метод Монте-Карло блукань**.

Алгоритм запускає велику кількість `num_walks` незалежних блукачів. Кожен блукач починає з випадково обраної вершини і рухається графом протягом `walk_length` кроків. З імовірністю `α = 0.85` блукач переходить по випадковому вихідному посиланню, а з імовірністю `1 - α = 0.15` (або у випадку влучання в тупик без вихідних ребер) здійснює випадкову телепортацію на довільну сторінку мережі. Лічильники відвідувань вершин нормуються на загальну кількість зроблених кроків, утворюючи емпіричний стаціонарний розподіл.

### Реалізація коду

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int num_vertices;
    int** out_adj;
    int* out_degrees;
} DigraphC;

DigraphC* digraph_create(int n) {
    DigraphC* g = (DigraphC*)malloc(sizeof(DigraphC));
    g->num_vertices = n;
    g->out_degrees = (int*)calloc(n, sizeof(int));
    g->out_adj = (int**)malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) g->out_adj[i] = NULL;
    return g;
}

void digraph_add_edge(DigraphC* g, int u, int v) {
    g->out_degrees[u]++;
    g->out_adj[u] = (int*)realloc(g->out_adj[u], g->out_degrees[u] * sizeof(int));
    g->out_adj[u][g->out_degrees[u] - 1] = v;
}

void digraph_free(DigraphC* g) {
    for (int i = 0; i < g->num_vertices; i++) free(g->out_adj[i]);
    free(g->out_adj);
    free(g->out_degrees);
    free(g);
}

// Обчислення PageRank методом Монте-Карло
void compute_pagerank_monte_carlo(const DigraphC* g, double alpha, int num_walks, int walk_length, double* rank_out) {
    int n = g->num_vertices;
    long long* visit_counts = (long long*)calloc(n, sizeof(long long));
    long long total_visits = 0;

    for (int w = 0; w < num_walks; w++) {
        int curr = rand() % n;
        visit_counts[curr]++;
        total_visits++;

        for (int step = 0; step < walk_length; step++) {
            double r = (double)rand() / RAND_MAX;
            int out_deg = g->out_degrees[curr];

            if (r < alpha && out_deg > 0) {
                // Перехід по сужному ребру
                int next_idx = rand() % out_deg;
                curr = g->out_adj[curr][next_idx];
            } else {
                // Телепортація
                curr = rand() % n;
            }
            visit_counts[curr]++;
            total_visits++;
        }
    }

    for (int i = 0; i < n; i++) {
        rank_out[i] = (double)visit_counts[i] / total_visits;
    }
    free(visit_counts);
}
```
```cpp
#include <vector>
#include <random>
#include <numeric>
#include <iostream>

class DirectedGraph {
public:
    explicit DirectedGraph(size_t n) : out_adj_(n) {}

    void add_edge(size_t u, size_t v) {
        out_adj_[u].push_back(v);
    }

    [[nodiscard]] size_t size() const noexcept { return out_adj_.size(); }
    [[nodiscard]] const std::vector<size_t>& out_neighbors(size_t u) const { return out_adj_[u]; }

private:
    std::vector<std::vector<size_t>> out_adj_;
};

class PageRankEstimator {
public:
    explicit PageRankEstimator(uint32_t seed = 1337) : rng_(seed) {}

    std::vector<double> estimate(const DirectedGraph& g, double damping = 0.85, 
                                size_t num_walks = 10000, size_t walk_length = 50) {
        const size_t n = g.size();
        std::vector<uint64_t> visits(n, 0);
        uint64_t total_visits = 0;

        std::uniform_int_distribution<size_t> vert_dist(0, n - 1);
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);

        for (size_t w = 0; w < num_walks; ++w) {
            size_t curr = vert_dist(rng_);
            visits[curr]++;
            total_visits++;

            for (size_t step = 0; step < walk_length; ++step) {
                const auto& neighbors = g.out_neighbors(curr);
                if (prob_dist(rng_) < damping && !neighbors.empty()) {
                    std::uniform_int_distribution<size_t> neigh_dist(0, neighbors.size() - 1);
                    curr = neighbors[neigh_dist(rng_)];
                } else {
                    curr = vert_dist(rng_); // Телепортація
                }
                visits[curr]++;
                total_visits++;
            }
        }

        std::vector<double> rank(n);
        for (size_t i = 0; i < n; ++i) {
            rank[i] = static_cast<double>(visits[i]) / static_cast<double>(total_visits);
        }
        return rank;
    }

private:
    std::mt19937 rng_;
};
```
:::

---

## 3. Алгоритм Уїлсона для генерації кістякових дерев (Wilson's UST)

### Задача та принцип вилучення циклів
Побудувати рівномірно випадкове кістякове дерево (Uniform Spanning Tree, UST) для зв'язного неорієнтованого графа `G`. Рівномірність означає, що кожне можливе кістякове дерево графа має бути згенероване з однаковою ймовірністю `1 / N_UST(G)`, де `N_UST(G)` — кількість кістякових дерев (обчислювана через матричну теорему Кірхгофа).

Прості підходи, такі як вибір випадкових ваг для ребер із наступним запуском алгоритму Краскала або Прима, **не будують** рівномірного розподілу над кістяковими деревами. Алгоритм Уїлсона розв'язує цю задачу за допомогою блукання з вилученням циклів (Loop-Erased Random Walk, LERW).

Процес будується наступним чином:
1. Зафіксуємо довільну початкову вершину `r = 0` як корінь піддерева і позначимо її як відвідану (`in_tree[0] = true`).
2. Для кожної невідвіданої вершини `i`:
   - Випускаємо випадковий блукач із вершини `i`.
   - Записуємо у масив `next[u]` вершину, у яку здійснено перехід з `u`. Якщо блукач утворює цикл (перетинає власну траєкторію), попереднє значення `next[u]` просто перезаписується новим вектором руху, що **автоматично видаляє (стирає) утворений цикл**.
   - Як тільки блукач торкається вже сформованого дерева `in_tree`, ми проходимо від вершини `i` по масиву `next[]` до дерева й додаємо всі пройдені ребра, помічаючи нові вершини як відвідані.

### Реалізація коду

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int u;
    int v;
} EdgeC;

// Алгоритм Уїлсона мовою C
EdgeC* wilson_ust_c(const GraphC* g, int* out_edges_count) {
    int n = g->num_vertices;
    bool* in_tree = (bool*)calloc(n, sizeof(bool));
    int* next = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) next[i] = -1;

    // Включаємо вершину 0 у дерево
    in_tree[0] = true;
    int tree_size = 1;

    for (int i = 1; i < n; i++) {
        int u = i;
        while (!in_tree[u]) {
            int deg = g->degrees[u];
            int r = rand() % deg;
            int v = g->adj[u][r];
            next[u] = v; // Крок блукача (автоматично стирає попередні цикли!)
            u = v;
        }

        // Додаємо вилучений від циклів шлях до дерева
        u = i;
        while (!in_tree[u]) {
            in_tree[u] = true;
            u = next[u];
            tree_size++;
        }
    }

    EdgeC* tree = (EdgeC*)malloc((n - 1) * sizeof(EdgeC));
    int idx = 0;
    for (int i = 1; i < n; i++) {
        tree[idx].u = i;
        tree[idx].v = next[i];
        idx++;
    }

    *out_edges_count = n - 1;
    free(in_tree);
    free(next);
    return tree;
}
```
```cpp
#include <vector>
#include <random>
#include <unordered_set>
#include <utility>

struct Edge {
    size_t u;
    size_t v;
};

class WilsonUSTGenerator {
public:
    explicit WilsonUSTGenerator(uint32_t seed = 2026) : rng_(seed) {}

    // Генерація рівномірного кістякового дерева за алгоритмом Уїлсона
    std::vector<Edge> generate_ust(const Graph& g) {
        const size_t n = g.num_vertices();
        if (n == 0) return {};

        std::vector<bool> in_tree(n, false);
        std::vector<size_t> next(n, 0);

        // Вершина 0 слугує коренем початкового дерева
        in_tree[0] = true;

        for (size_t i = 1; i < n; ++i) {
            size_t u = i;
            while (!in_tree[u]) {
                const auto& neighbors = g.neighbors(u);
                std::uniform_int_distribution<size_t> dist(0, neighbors.size() - 1);
                size_t v = neighbors[dist(rng_)];
                next[u] = v; // Вилучення циклів відбувається перезаписом next[u]
                u = v;
            }

            u = i;
            while (!in_tree[u]) {
                in_tree[u] = true;
                u = next[u];
            }
        }

        std::vector<Edge> ust;
        ust.reserve(n - 1);
        for (size_t i = 1; i < n; ++i) {
            ust.push_back({i, next[i]});
        }
        return ust;
    }

private:
    std::mt19937 rng_;
};
```
:::

---

## 4. Пастки реалізації та алгоритмічні ризики

> 🔧 **Навіщо це.**
> Знання пасток дозволяє уникнути зациклень у детермінованих графах із «тупиками», а також витоків пам'яті при роботі зі стохастичними вибірками великої розмірності.

1. **Зациклення у тупикових вершинах (Dangling Nodes):**
   У орієнтованих графах вершини без вихідних ребер (`out_degree = 0`) стають поглинаючими стоками. Якщо блукач влучає у таку вершину без механізму телепортації, вектор розподілу втрачає ймовірнісну міру (`∑ π_i < 1`). Алгоритм мусить виявляти тупики та примусово здійснювати рівномірну телепортацію.

2. **Періодичність у дводольних графах:**
   Якщо граф є строго дводольним, блукач переходить між частками `A` та `B` на парних та непарних кроках відповідно. Звичайний розподіл `π⁽ᵗ⁾` не збігається до стаціонарного, а осцилює. Для усунення періодичності обов'язково застосовують **ледаче блукання** (`P_lazy = 0.5 I + 0.5 P`).

3. **Нерівномірність псевдовипадкових генераторів (PRNG):**
   Стандартна функція `rand()` у C має обмежений період (`2³¹ - 1`) та нижчу якість молодших бітів. При виконанні мільярдів кроків це призводить до зміщення стаціонарного розподілу. Слід використовувати сучасні вихрові генератори (Mersenne Twister `std::mt19937` у C++) або криптографічно стійкі джерела ентропії.

4. **Незв'язність графа у випадках Уїлсона:**
   Якщо граф має декілька компонент зв'язності, блукач з усамітненої компоненти ніколи не торкнеться дерева, збудованого в іншій компоненті. Алгоритм потрапляє у нескінченний цикл. Для запобігання цій ситуації перед запуском необхідно виконувати перевірку графа на зв'язність або запускати окремий екземпляр алгоритму Уїлсона для кожної компоненти.
