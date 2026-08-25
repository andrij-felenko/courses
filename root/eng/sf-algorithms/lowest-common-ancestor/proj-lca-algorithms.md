# ⚙️ Практична реалізація алгоритмів LCA

У цій практичній вставці наведено вичерпний аналіз та реалізацію алгоритмів бінарного підйому (Binary Lifting) та зведення до RMQ через обхід Ейлера мовами C та C++ з детальними поясненнями часових і просторових витрат.

---

### 1. Метод бінарного підйому (Binary Lifting)

Алгоритм бінарного підйому базується на концепції динамічного програмування на деревах. Замість збереження лише одного безпосереднього батька для кожної вершини, ми будуємо двовимірну таблицю `up[u][k]`, де `up[u][k]` вказує на `2^k`-го предка вершини `u` в напрямку до кореня дерева.

#### Механізм побудови та рекурентне співвідношення

Підйом на `2^k` кроків можна розбити на два послідовних підйоми на `2^{k-1}` кроків:
1. Спочатку піднімаємося від вершини `u` на `2^{k-1}` кроків і потрапляємо у вершину `w = up[u][k-1]`.
2. Потім від вершини `w` піднімаємося ще на `2^{k-1}` кроків і потрапляємо у підсумкову вершину `up[w][k-1]`.

Звідси випливає фундаментальне рекурентке співвідношення:
```
up[u][k] = up[ up[u][k-1] ][ k-1 ]
```

#### Покроковий алгоритм розв'язання запиту `LCA(u, v)`

1. **Ініціалізація та DFS обхід (`O(N log N)`):**
   - За допомогою обходу в глибину (DFS) обчислюємо глибину кожної вершини `depth[u]` та її безпосереднього батька `up[u][0] = parent`. Для кореня дерева `up[root][0] = root`.
   - Заповнюємо таблицю `up[u][k]` для всіх `1 ≤ k < LOGN`, де `LOGN = ⌈log₂ N⌉ + 1`.

2. **Вирівнювання глибин:**
   - Якщо вершина `u` розташована глибше за `v` (`depth[u] > depth[v]`), обчислюємо різницю `Δd = depth[u] - depth[v]`.
   - Проходимо по бітах числа `Δd` від найстаршого до наймолодшого. Якщо `k`-й біт числа `Δd` дорівнює 1, замінюємо `u` на `up[u][k]`. Це піднімає вершину `u` на рівень глибини вершини `v`.

3. **Базовий перевірочний випадок:**
   - Якщо після вирівнювання `u == v`, це означає, що вершина `v` була предком `u`. Повертаємо `u` як результат.

4. **Одночасний бінарний підйом:**
   - Перебираємо степені двійки від `k = LOGN - 1` спадаючи до `0`.
   - Якщо `up[u][k] != up[v][k]`, це означає, що спільний предок лежить строго вище рівня `2^k`. Ми одночасно піднімаємо обидві вершини: `u = up[u][k]` та `v = up[v][k]`.
   - Якщо ж `up[u][k] == up[v][k]`, ми не робимо крок, оскільки цей предок може бути не найменшим спільним предком, а розташованим вище.

5. **Фінал:**
   - Після завершення циклу вершини `u` та `v` зупиняться строго на рівні безпосередньо під їхнім найменшим спільним предком. Звідси відповіддю є безпосередній батько будь-якої з них: `LCA(u, v) = up[u][0]`.

#### Покрокове простеження бітової математики підйому

Розглянемо випадок, коли глибина вершини `u` дорівнює 13, а глибина вершини `v` дорівнює 5. Різниця глибин становить `Δd = 13 - 5 = 8`.
У двійковій системі число 8 записується як `1000₂` (встановився лише 3-й біт, оскільки `2³ = 8`).
Під час виконання циклу вирівнювання умова `(diff >> 3) & 1` виявляється істинною. Алгоритм виконує рівно один прямокутний стрибок `u = up[u][3]`, миттєво піднімаючи вершину `u` на 8 рівнів угору.

Якщо ж різниця глибин була б, наприклад, `Δd = 11` (`1011₂ = 8 + 2 + 1`), алгоритм виконує три послідовні стрибки:
- Спочатку при `k = 3` стрибок на `2³ = 8` рівнів.
- Потім при `k = 1` стрибок на `2¹ = 2` рівні.
- Нарешті при `k = 0` стрибок на `2⁰ = 1` рівень.
Всього виконано 3 кроки замість 11 послідовних ітерацій. Це й пояснює логарифмічну складність вирівнювання `O(log N)`.

#### Код алгоритму Binary Lifting мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAXN 100005
#define LOGN 20

typedef struct Edge {
    int to;
    struct Edge* next;
} Edge;

typedef struct {
    Edge* head[MAXN];
    int depth[MAXN];
    int up[MAXN][LOGN];
    int n;
} BinaryLiftingLCA;

BinaryLiftingLCA* lca_create(int n) {
    BinaryLiftingLCA* tree = (BinaryLiftingLCA*)calloc(1, sizeof(BinaryLiftingLCA));
    if (!tree) return NULL;
    tree->n = n;
    return tree;
}

void lca_add_edge(BinaryLiftingLCA* tree, int u, int v) {
    Edge* e1 = (Edge*)malloc(sizeof(Edge));
    e1->to = v; e1->next = tree->head[u]; tree->head[u] = e1;
    
    Edge* e2 = (Edge*)malloc(sizeof(Edge));
    e2->to = u; e2->next = tree->head[v]; tree->head[v] = e2;
}

static void dfs_build(BinaryLiftingLCA* tree, int u, int p, int d) {
    tree->depth[u] = d;
    tree->up[u][0] = p;

    for (int k = 1; k < LOGN; k++) {
        tree->up[u][k] = tree->up[tree->up[u][k - 1]][k - 1];
    }

    for (Edge* e = tree->head[u]; e != NULL; e = e->next) {
        if (e->to != p) {
            dfs_build(tree, e->to, u, d + 1);
        }
    }
}

void lca_init(BinaryLiftingLCA* tree, int root) {
    dfs_build(tree, root, root, 0);
}

int lca_query(const BinaryLiftingLCA* tree, int u, int v) {
    if (tree->depth[u] < tree->depth[v]) {
        int tmp = u; u = v; v = tmp;
    }

    int diff = tree->depth[u] - tree->depth[v];
    for (int k = LOGN - 1; k >= 0; k--) {
        if ((diff >> k) & 1) {
            u = tree->up[u][k];
        }
    }

    if (u == v) return u;

    for (int k = LOGN - 1; k >= 0; k--) {
        if (tree->up[u][k] != tree->up[v][k]) {
            u = tree->up[u][k];
            v = tree->up[v][k];
        }
    }

    return tree->up[u][0];
}

void lca_free(BinaryLiftingLCA* tree) {
    if (!tree) return;
    for (int i = 0; i <= tree->n; i++) {
        Edge* curr = tree->head[i];
        while (curr) {
            Edge* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(tree);
}
```
```cpp
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>

class BinaryLiftingLCA {
private:
    int n_;
    int logn_;
    std::vector<int> depth_;
    std::vector<std::vector<int>> up_;
    std::vector<std::vector<int>> adj_;

    void dfs(int u, int p, int d) {
        depth_[u] = d;
        up_[u][0] = p;

        for (int k = 1; k < logn_; ++k) {
            up_[u][k] = up_[up_[u][k - 1]][k - 1];
        }

        for (int v : adj_[u]) {
            if (v != p) {
                dfs(v, u, d + 1);
            }
        }
    }

public:
    explicit BinaryLiftingLCA(int n)
        : n_(n), logn_(std::ceil(std::log2(n + 1)) + 1),
          depth_(n + 1, 0), up_(n + 1, std::vector<int>(logn_, 0)), adj_(n + 1) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    void build(int root = 1) {
        dfs(root, root, 0);
    }

    [[nodiscard]] int query(int u, int v) const {
        if (depth_[u] < depth_[v]) {
            std::swap(u, v);
        }

        int diff = depth_[u] - depth_[v];
        for (int k = logn_ - 1; k >= 0; --k) {
            if ((diff >> k) & 1) {
                u = up_[u][k];
            }
        }

        if (u == v) return u;

        for (int k = logn_ - 1; k >= 0; --k) {
            if (up_[u][k] != up_[v][k]) {
                u = up_[u][k];
                v = up_[v][k];
            }
        }

        return up_[u][0];
    }

    [[nodiscard]] int distance(int u, int v) const {
        int l = query(u, v);
        return depth_[u] + depth_[v] - 2 * depth_[l];
    }
};
```
:::

---

### 2. Зведення до RMQ через обхід Ейлера (Euler Tour + Sparse Table)

Другий фундаментальний метод дозволяє розв'язувати кожен запит **за сталий час `O(1)`**, звівши задачу LCA до задачі **Range Minimum Query (RMQ)**.

#### Алгоритмічна суть обходу Ейлера

Ми здійснюємо обхід дерева в глибину (DFS), записуючи номер вершини в масив `euler[]` кожного разу, коли ми заходимо у вершину або повертаємося до неї від одного з її дітей.

При цьому ми підтримуємо паралельні масиви:
- `euler[]` — послідовність відвіданих вершин. Довжина цього масиву дорівнює `2N - 1`.
- `depth[]` — глибина відповідної вершини `depth[i] = depth(euler[i])`.
- `first[]` — позиція першого входження вершини `u` у масив Ейлера.

#### Ключова теорема RMQ-зведення

Найменший спільний предок `LCA(u, v)` відповідає вершині з **найменшою глибиною** на відрізку масиву Ейлера між їхніми першими входженнями `first[u]` та `first[v]`:
```
LCA(u, v) = euler[ argmin_{first[u] ≤ k ≤ first[v]} depth[k] ]
```

Для знаходження позиції мінімуму на стаціонарному масиві за `O(1)` ми будуємо структуру даних **Sparse Table** над масивом глибин.

#### Структура Sparse Table та логарифмічна перекривна аналітика

Таблиця Sparse Table зберігає позицію елемента з мінімальною глибиною для всіх підвідрізків довжиною, що є степенем двійки:
`st[i][j]` зберігає індекс мінімуму для відрізка `[i .. i + 2^j - 1]`.

Побудова здійснюється за `O(M log M)` часу (де `M = 2N - 1` — довжина обходу Ейлера):
```
st[i][j] = argmin( depth[st[i][j-1]], depth[st[i + 2^(j-1)][j-1]] )
```

При виконанні запиту на довільному інтервалі `[l .. r]` довжиною `len = r - l + 1`, ми знаходимо найстарший степінь двійки `k = ⌊log₂ len⌋`. Відрізок `[l .. r]` покривається двома перекривними блоками довжиною `2^k`:
- Перший блок починається в `l`: `[l .. l + 2^k - 1]`.
- Другий блок закінчується в `r`: `[r - 2^k + 1 .. r]`.

Мінімум на всьому інтервалі є мінімумом між цими двома блоками. Оскільки операція `min` є ідемпотентною (`min(x, x) = x`), факт перекриття блоків ніяк не спотворює результат. Обчислення виконується за 1 такт доступу до пам'яті: `O(1)`.

#### Повний код Euler Tour + Sparse Table мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAXN 100005
#define LOGN 20

typedef struct {
    int* euler;
    int* depth;
    int* first;
    int** st;
    int* log_table;
    int tour_len;
    int n;
} FastRMQLCA;

static int min_depth_node(const FastRMQLCA* rmq, int u, int v) {
    return (rmq->depth[u] < rmq->depth[v]) ? u : v;
}

static void dfs_euler(const int* const* adj, const int* deg, int u, int p, int d,
                      FastRMQLCA* rmq, int* visited) {
    rmq->first[u] = rmq->tour_len;
    rmq->euler[rmq->tour_len] = u;
    rmq->depth[rmq->tour_len] = d;
    rmq->tour_len++;

    for (int i = 0; i < deg[u]; i++) {
        int v = adj[u][i];
        if (v != p) {
            dfs_euler(adj, deg, v, u, d + 1, rmq, visited);
            rmq->euler[rmq->tour_len] = u;
            rmq->depth[rmq->tour_len] = d;
            rmq->tour_len++;
        }
    }
}

FastRMQLCA* rmq_lca_create(int n) {
    FastRMQLCA* rmq = (FastRMQLCA*)calloc(1, sizeof(FastRMQLCA));
    rmq->n = n;
    int max_tour = 2 * n + 5;
    rmq->euler = (int*)malloc(sizeof(int) * max_tour);
    rmq->depth = (int*)malloc(sizeof(int) * max_tour);
    rmq->first = (int*)malloc(sizeof(int) * (n + 1));
    rmq->log_table = (int*)malloc(sizeof(int) * max_tour);

    rmq->log_table[1] = 0;
    for (int i = 2; i < max_tour; i++) {
        rmq->log_table[i] = rmq->log_table[i / 2] + 1;
    }

    return rmq;
}

void rmq_lca_build(FastRMQLCA* rmq, const int* const* adj, const int* deg, int root) {
    rmq->tour_len = 0;
    int* visited = (int*)calloc(rmq->n + 1, sizeof(int));
    dfs_euler(adj, deg, root, 0, 0, rmq, visited);
    free(visited);

    int m = rmq->tour_len;
    int log_m = rmq->log_table[m] + 1;

    rmq->st = (int**)malloc(sizeof(int*) * m);
    for (int i = 0; i < m; i++) {
        rmq->st[i] = (int*)malloc(sizeof(int) * log_m);
        rmq->st[i][0] = rmq->euler[i];
    }

    for (int j = 1; j < log_m; j++) {
        for (int i = 0; i + (1 << j) <= m; i++) {
            int node1 = rmq->st[i][j - 1];
            int node2 = rmq->st[i + (1 << (j - 1))][j - 1];
            rmq->st[i][j] = min_depth_node(rmq, node1, node2);
        }
    }
}

int rmq_lca_query(const FastRMQLCA* rmq, int u, int v) {
    int l = rmq->first[u];
    int r = rmq->first[v];
    if (l > r) { int tmp = l; l = r; r = tmp; }

    int len = r - l + 1;
    int k = rmq->log_table[len];

    int node1 = rmq->st[l][k];
    int node2 = rmq->st[r - (1 << k) + 1][k];
    return min_depth_node(rmq, node1, node2);
}

void rmq_lca_free(FastRMQLCA* rmq) {
    if (!rmq) return;
    if (rmq->st) {
        for (int i = 0; i < rmq->tour_len; i++) {
            free(rmq->st[i]);
        }
        free(rmq->st);
    }
    free(rmq->euler);
    free(rmq->depth);
    free(rmq->first);
    free(rmq->log_table);
    free(rmq);
}
```
```cpp
#include <vector>
#include <algorithm>
#include <cmath>

class EulerTourRMQLCA {
private:
    int n_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> euler_;
    std::vector<int> depth_nodes_;
    std::vector<int> first_;
    std::vector<std::vector<int>> st_;
    std::vector<int> log_table_;

    void dfs(int u, int p, int d) {
        first_[u] = static_cast<int>(euler_.size());
        euler_.push_back(u);
        depth_nodes_.push_back(d);

        for (int v : adj_[u]) {
            if (v != p) {
                dfs(v, u, d + 1);
                euler_.push_back(u);
                depth_nodes_.push_back(d);
            }
        }
    }

public:
    explicit EulerTourRMQLCA(int n)
        : n_(n), adj_(n + 1), first_(n + 1, 0) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    void build(int root = 1) {
        dfs(root, 0, 0);

        int m = static_cast<int>(euler_.size());
        log_table_.assign(m + 1, 0);
        for (int i = 2; i <= m; ++i) {
            log_table_[i] = log_table_[i / 2] + 1;
        }

        int max_log = log_table_[m] + 1;
        st_.assign(m, std::vector<int>(max_log));

        for (int i = 0; i < m; ++i) {
            st_[i][0] = euler_[i];
        }

        auto min_node = [this](int u_node, int v_node) {
            return (depth_nodes_[first_[u_node]] < depth_nodes_[first_[v_node]]) ? u_node : v_node;
        };

        for (int j = 1; j < max_log; ++j) {
            for (int i = 0; i + (1 << j) <= m; ++i) {
                st_[i][j] = min_node(st_[i][j - 1], st_[i + (1 << (j - 1))][j - 1]);
            }
        }
    }

    [[nodiscard]] int query(int u, int v) const {
        int l = first_[u];
        int r = first_[v];
        if (l > r) std::swap(l, r);

        int len = r - l + 1;
        int k = log_table_[len];

        int node1 = st_[l][k];
        int node2 = st_[r - (1 << k) + 1][k];

        return (depth_nodes_[first_[node1]] < depth_nodes_[first_[node2]]) ? node1 : node2;
    }
};
```
:::

---

### 3. Порівняльний аналіз алгоритмів

| Алгоритм | Час препроцесингу | Час запиту | Пам'ять | Переваги та пастки |
| :--- | :--- | :--- | :--- | :--- |
| **Binary Lifting** | `O(N log N)` | `O(log N)` | `O(N log N)` | Проста реалізація, підтримує динамічні обчислення на шляхах (наприклад, max/min вага ребра). |
| **Euler Tour + RMQ** | `O(N log N)` | `O(1)` | `O(N log N)` | Абсолютна швидкість запиту `O(1)`. Ідеально для статичних дерев з мільйонами запитів. |
| **Tarjan DSU (Offline)** | `O(N + Q α(N))` | `O(α(N))` | `O(N + Q)` | Мінімальне споживання пам'яті, але вимагає наявності всіх запитів заздалегідь. |
| **Bender-Farach-Colton** | `O(N)` | `O(1)` | `O(N)` | Теоретично ідеальний, але має більшу константу через таблиці підблоків. |

---

### 4. Крайові випадки та аналіз продуктивності процесорного кешу

Під час практичної інженерної реалізації необхідно враховувати два критичні аспекти:

1. **Вироджені дерева (ланцюги):** Якщо дерево вироджується у бамбук глибини `N`, рекурсивний DFS може призвести до переповнення стеку викликів (Stack Overflow). У продакшн-коді для вироджених структур замість системного стеку використовують ітеративний DFS із власним масивом-стеком.
2. **Локальність даних у кеші L1/L2:** Масив Sparse Table розміром `(2N) × log₂ (2N)` краще зберігати у плоскому вирівняному векторах `std::vector<int>`, оскільки двовимірні динамічні масиви `int**` призводять до промахів кешу процесора (Cache Misses) через розкиданість вказівників у купі (Heap).
