# ⚙️ Практична реалізація алгоритму Едмондса мовами C та C++

Ця вставка містить аналіз системної архітектури, інваріантів та повних, готових до компіляції реалізацій алгоритму Едмондса (Blossom Algorithm) для знаходження найбільшого паросполучення в довільному неорієнтованому графі мовами C та C++.

## Архітектурний огляд та інваріанти структури даних

Алгоритм Едмондса розв'язує задачу знаходження доповняльних шляхів шляхом побудови чергувального лісу за допомогою пошуку в ширину (BFS). Ключова відмінність недвочасткових графів від двочасткових полягає у наявності непарних циклів, які створюють ситуацію «подвійної парності» вершин. Для розв'язання цієї колізії алгоритм застосовує механізм динамічного стиснення квіток із підтриманням системи неперетинних множин (DSU):

1. **Масив парності та розбиття вершин (`type_arr`):** Кожній відвіданій вершині чергувального лісу присвоюється один із двох типів. Тип `0` (парна / Outer) означає, що вершина знаходиться на парній відстані від кореня чергувального дерева (включаючи самі корені). Тип `1` (непарна / Inner) відповідає непарній відстані від кореня.
2. **Бази вершин та DSU (`base_arr`):** Для ефективного підтримання вкладених квіток використовується система неперетинних множин з оптимізацією стиснення шляхів. Кожна вершина `u` має свій репрезентативний вузол `base[u]`, який вказує на основу найзовнішнішої квітки, що її містить. Усі операції перевірки суміжності та належності до однієї квітки виконуються через виклик `dsu_find(u)`.
3. **Знаходження найменшого спільного предка (`find_lca`):** При виявленні ребра між двома парними вершинами (`type[u] == 0` та `type[v] == 0`), що належать одному чергувальному дереву, виникає непарний цикл (квітка). Алгоритм знаходить найменшого спільного предка (LCA) у чергувальному дереві. Для уникнення квадратичних витрат часу на очищення масиву відвіданих вершин застосовується методика міток епохи (англ. *epoch timestamping*): глобальний лічильник `timer_lca` інкрементується на кожен виклик LCA, а вершини відмічаються значенням поточного таймера.
4. **Маркування та стиснення квітки (`mark_blossom`):** Знайшовши LCA (який стає новою основою квітки `b`), алгоритм проходить по двох гілках від `u` та `v` до `lca_node`. Для всіх внутрішніх непарних вершин квітки їхній тип змінюється на парний (`Even`), що дозволяє додавати їх у чергу BFS для подальшого сканування їхніх суміжних ребер. Масив `parent` оновлюється так, щоб забезпечити правильне розгортання шляху всередині циклу.
5. **Інвертування та відновлення шляху (`bfs_augment`):** Після виявлення ребра до вільної вершини або між двома окремими чергувальними деревами знайдений доповняльний шлях є замкненим ланцюгом. Цикл відновлення проходить по масиву `parent`, змінюючи ребра паросполучення на вільні і навпаки, після чого розмір паросполучення зростає на 1.

## Повний вихідний код реалізації

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAXV 500

typedef struct {
    int head[MAXV];
    int to[MAXV * MAXV];
    int next[MAXV * MAXV];
    int edge_count;
} Graph;

static void graph_init(Graph *g) {
    memset(g->head, -1, sizeof(g->head));
    g->edge_count = 0;
}

static void graph_add_edge(Graph *g, int u, int v) {
    g->to[g->edge_count] = v;
    g->next[g->edge_count] = g->head[u];
    g->head[u] = g->edge_count++;

    g->to[g->edge_count] = u;
    g->next[g->edge_count] = g->head[v];
    g->head[v] = g->edge_count++;
}

/* Глобальні структури стану алгоритму Едмондса */
static int match_arr[MAXV];
static int parent_arr[MAXV];
static int base_arr[MAXV];
static int type_arr[MAXV];  /* -1: невідвідана, 0: парна (Outer), 1: непарна (Inner) */
static int visited_lca[MAXV];
static int queue_arr[MAXV];
static int q_head, q_tail;
static int timer_lca = 0;

static int dsu_find(int u) {
    if (base_arr[u] == u) return u;
    return base_arr[u] = dsu_find(base_arr[u]);
}

static int find_lca(int u, int v) {
    timer_lca++;
    u = dsu_find(u);
    v = dsu_find(v);

    while (true) {
        if (u != -1) {
            if (visited_lca[u] == timer_lca) return u;
            visited_lca[u] = timer_lca;
            if (match_arr[u] != -1) {
                u = dsu_find(parent_arr[match_arr[u]]);
            } else {
                u = -1;
            }
        }
        /* Міняємо місцями u та v для паралельного підйому вгору по дереву */
        int temp = u;
        u = v;
        v = temp;
    }
}

static void mark_blossom(int u, int v, int lca_node) {
    while (dsu_find(u) != lca_node) {
        parent_arr[u] = v;
        v = match_arr[u];

        if (type_arr[v] == 1) {
            type_arr[v] = 0;
            queue_arr[q_tail++] = v;
        }

        base_arr[u] = lca_node;
        base_arr[v] = lca_node;
        u = parent_arr[v];
    }
}

static bool bfs_augment(const Graph *g, int num_vertices, int start_root) {
    for (int i = 0; i < num_vertices; ++i) {
        base_arr[i] = i;
        parent_arr[i] = -1;
        type_arr[i] = -1;
    }

    q_head = 0;
    q_tail = 0;

    type_arr[start_root] = 0;
    queue_arr[q_tail++] = start_root;

    while (q_head < q_tail) {
        int u = queue_arr[q_head++];

        for (int e = g->head[u]; e != -1; e = g->next[e]) {
            int v = g->to[e];

            if (dsu_find(u) == dsu_find(v) || type_arr[v] == 1) {
                continue;
            }

            if (type_arr[v] == -1) {
                parent_arr[v] = u;
                type_arr[v] = 1;

                if (match_arr[v] == -1) {
                    /* Знайдено доповняльний шлях! Оновлюємо паросполучення */
                    int curr = v;
                    while (curr != -1) {
                        int p = parent_arr[curr];
                        int next_p = (p != -1) ? match_arr[p] : -1;
                        match_arr[curr] = p;
                        match_arr[p] = curr;
                        curr = next_p;
                    }
                    return true;
                }

                type_arr[match_arr[v]] = 0;
                queue_arr[q_tail++] = match_arr[v];
            } else if (type_arr[v] == 0) {
                /* Виявлено квітку (ребро між двома парними вершинами) */
                int lca_node = find_lca(u, v);
                mark_blossom(u, v, lca_node);
                mark_blossom(v, u, lca_node);
            }
        }
    }
    return false;
}

int edmonds_max_matching(const Graph *g, int num_vertices) {
    memset(match_arr, -1, sizeof(match_arr));
    memset(visited_lca, 0, sizeof(visited_lca));
    timer_lca = 0;

    int max_matching_size = 0;
    for (int i = 0; i < num_vertices; ++i) {
        if (match_arr[i] == -1) {
            if (bfs_augment(g, num_vertices, i)) {
                max_matching_size++;
            }
        }
    }
    return max_matching_size;
}

int main(void) {
    Graph g;
    graph_init(&g);

    int n = 5;
    /* Граф — непарний цикл 5 вершин (0-1-2-3-4-0) */
    graph_add_edge(&g, 0, 1);
    graph_add_edge(&g, 1, 2);
    graph_add_edge(&g, 2, 3);
    graph_add_edge(&g, 3, 4);
    graph_add_edge(&g, 4, 0);

    int matching_size = edmonds_max_matching(&g, n);
    printf("Розмір найбільшого паросполучення в C5: %d\n", matching_size);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <numeric>
#include <algorithm>
#include <optional>

class EdmondsMatchingSolver {
public:
    explicit EdmondsMatchingSolver(size_t vertices)
        : num_vertices_(vertices),
          adj_(vertices),
          match_(vertices, -1),
          parent_(vertices, -1),
          base_(vertices),
          type_(vertices, VertexType::Unvisited),
          visited_lca_(vertices, 0) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
    }

    int solve_max_matching() {
        std::fill(match_.begin(), match_.end(), -1);
        std::fill(visited_lca_.begin(), visited_lca_.end(), 0);
        timer_lca_ = 0;

        int matching_size = 0;
        for (size_t i = 0; i < num_vertices_; ++i) {
            if (match_[i] == -1) {
                if (bfs_augment(static_cast<int>(i))) {
                    matching_size++;
                }
            }
        }
        return matching_size;
    }

    [[nodiscard]] const std::vector<int>& get_matching() const noexcept {
        return match_;
    }

private:
    enum class VertexType { Unvisited = -1, Even = 0, Odd = 1 };

    size_t num_vertices_;
    std::vector<std::vector<int>> adj_;
    std::vector<int> match_;
    std::vector<int> parent_;
    std::vector<int> base_;
    std::vector<VertexType> type_;
    std::vector<int> visited_lca_;
    int timer_lca_{0};

    int dsu_find(int u) {
        if (base_[u] == u) return u;
        return base_[u] = dsu_find(base_[u]);
    }

    int find_lca(int u, int v) {
        timer_lca_++;
        u = dsu_find(u);
        v = dsu_find(v);

        while (true) {
            if (u != -1) {
                if (visited_lca_[u] == timer_lca_) return u;
                visited_lca_[u] = timer_lca_;
                u = (match_[u] != -1) ? dsu_find(parent_[match_[u]]) : -1;
            }
            std::swap(u, v);
        }
    }

    void mark_blossom(int u, int v, int lca_node, std::queue<int>& q) {
        while (dsu_find(u) != lca_node) {
            parent_[u] = v;
            v = match_[u];

            if (type_[v] == VertexType::Odd) {
                type_[v] = VertexType::Even;
                q.push(v);
            }

            base_[u] = lca_node;
            base_[v] = lca_node;
            u = parent_[v];
        }
    }

    bool bfs_augment(int start_root) {
        std::iota(base_.begin(), base_.end(), 0);
        std::fill(parent_.begin(), parent_.end(), -1);
        std::fill(type_.begin(), type_.end(), VertexType::Unvisited);

        std::queue<int> q;
        type_[start_root] = VertexType::Even;
        q.push(start_root);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj_[u]) {
                if (dsu_find(u) == dsu_find(v) || type_[v] == VertexType::Odd) {
                    continue;
                }

                if (type_[v] == VertexType::Unvisited) {
                    parent_[v] = u;
                    type_[v] = VertexType::Odd;

                    if (match_[v] == -1) {
                        /* Відновлення та інвертування шляху */
                        int curr = v;
                        while (curr != -1) {
                            int p = parent_[curr];
                            int next_p = (p != -1) ? match_[p] : -1;
                            match_[curr] = p;
                            match_[p] = curr;
                            curr = next_p;
                        }
                        return true;
                    }

                    type_[match_[v]] = VertexType::Even;
                    q.push(match_[v]);
                } else if (type_[v] == VertexType::Even) {
                    int lca_node = find_lca(u, v);
                    mark_blossom(u, v, lca_node, q);
                    mark_blossom(v, u, lca_node, q);
                }
            }
        }
        return false;
    }
};

int main() {
    EdmondsMatchingSolver solver(5);
    /* Граф С5: 0-1-2-3-4-0 */
    solver.add_edge(0, 1);
    solver.add_edge(1, 2);
    solver.add_edge(2, 3);
    solver.add_edge(3, 4);
    solver.add_edge(4, 0);

    int count = solver.solve_max_matching();
    std::cout << "C++ Solver: Максимальне паросполучення = " << count << std::endl;

    const auto& matching = solver.get_matching();
    for (size_t i = 0; i < matching.size(); ++i) {
        if (matching[i] > static_cast<int>(i)) {
            std::cout << "Ребро паросполучення: (" << i << ", " << matching[i] << ")\n";
        }
    }
    return 0;
}
```
:::

## Аналіз складності та підводних каменів реалізації

1. **Часова складність:** Зовнішній цикл шукає доповняльний шлях не більше ніж `O(V)` разів, оскільки кожен успішний шлях збільшує розмір паросполучення принаймні на 1. Для кожної ітерації BFS проглядається до `O(E)` ребер, а кожне згортання квітки виконує підйом до LCA за `O(V)` кроків. Отже, загальна часова складність становить `O(V · E)` або `O(V^3)` для щільних графів.
2. **Просторова складність:** Алгоритм потребує пам'яті `O(V + E)` для збереження списків суміжності та додаткових масивів стану (`match`, `parent`, `base`, `type`, `visited_lca`), що робить його вкрай лінійним за пам'яттю відносно розміру графа.
3. **Крайові випадки (Edge Cases):**
   - **Незв'язані графи:** Алгоритм ітерується по всіх вільних вершинах як можливих коренях BFS, тому компоненти зв'язності обробляються автономно.
   - **Петлі та паралельні ребра:** Петля `(u, u)` автоматично відсікається умовою `dsu_find(u) == dsu_find(v)`. Паралельні ребра не впливають на коректність, проте їх рекомендується фільтрувати на етапі ініціалізації.
   - **Вкладені квітки (Nested Blossoms):** Завдяки рекурсивному стисненню в DSU через `base_arr`, декілька вкладених непарних циклів стягуються в єдину псевдовершину без виникнення циклічних посилань.

## Детальний аналіз ключових підпрограм

### 1. Підпрограма `find_lca`

Підпрограма `find_lca` здійснює пошук найменшого спільного предка двох парних вершин `u` та `v`, які утворили непарний цикл. 

Паралельний підйом по чергувальному дереву реалізовано наступним чином:
- Алгоритм почергово здійснює один крок вгору від `u` до `parent[match[u]]`, а потім міняє місцями `u` та `v` (`std::swap(u, v)`).
- Для кожного відвіданого вузла встановлюється мітка `visited_lca[u] = timer_lca`.
- Оскільки обидва рукави піднімаються до спільного кореня, перша вершина, яка вже містить мітку поточного таймера, є найменшим спільним предком.

Такий підхід гарантує виконання пошуку LCA за час `O(|B|)`, де `|B|` — кількість вершин у виявленій квітці, не вимагаючи повного очищення масиву відвіданих вершин.

### 2. Підпрограма `mark_blossom`

Функція `mark_blossom(u, v, lca_node)` реалізує обхід одного з двох рукавів непарного циклу від вершини `u` до спільного предка `lca_node`:
- Переходячи від `u` до `parent[match[u]]`, функція встановлює `parent_arr[u] = v`.
- Якщо вершина `v = match[u]` раніше мала непарний тип (`type == 1`), її тип змінюється на парний (`type = 0`), і вона додається в чергу BFS.
- Усі вершини розкриваються для подальшого пошуку суміжних ребер, що дозволяє знайти доповняльні шляхи, які проходять крізь внутрішні ребра квітки.

### 3. Оптимізація пам'яті та кеш-локальність

У C++ реалізації використання `std::vector<int>` для списків суміжності забезпечує послідовне розміщення ребер у пам'яті, що оптимізує роботу L1/L2 кешу процесора при масовому скануванні ребер під час BFS.

Для розріджених графів великої розмірності (`V > 100,000`) рекомендується заміняти матрицю суміжності на стиснутий рядовий формат (CSR, або *Compressed Sparse Row*), що знижує витрати пам'яті до `2 · E · sizeof(int)` та усуває додаткові покажчики векторів.

## Тестування та верифікація коректності розв'язувача

Для гарантії відсутності регресій та помилок при реалізації алгоритму Едмондса застосовуються наступні стратегії тестування:
1. **Тестування на канонічних графах:**
   - **Непарні цикли `C3, C5, C7`:** Перевіряється, що для `C_{2k+1}` розв'язувач повертає паросполучення розміру `k`.
   - **Повні графи `K_n`:** Для `K_n` повертається паросполучення розміру `⌊n/2⌋`.
   - **Граф Петерсена (Petersen graph):** Відомий недвочастковий кубічний граф із 10 вершинами. Максимальне паросполучення має дорівнювати 5 (досконале паросполучення).
2. **Фуззинг-тестування (Randomized Fuzzing):**
   - Генеруються довільні неорієнтовані графи за моделлю Ердеша — Реньї `G(n, p)`.
   - Знайдений розмір паросполучення `|M|` порівнюється з результатом точного перебору (для малих `n <= 20`) або з вердиктом двоїстого ЛП-солвера за формулою Татта — Бержа.
