# ⚙️ Реалізація алгоритму Таржана для пошуку компонент сильної зв'язаності

Алгоритм Таржана є фундаментальним алгоритмом для виділення всіх компонент сильної зв'язаності (Strongly Connected Components, SCC) в орієнтованому графі за один-єдиний прохід обходу в глибину (DFS). Він забезпечує оптимальний лінійний час виконання `O(|V| + |E|)` та мінімальні витрати оперативної пам'яті `O(|V|)`.

У цьому практичному посібнику наведено детальні виробничі реалізації алгоритму Таржана мовами C та C++, включаючи класичну рекурсивну форму, ітеративну версію для запобігання переповненню стека (stack overflow) на надглибоких графах, а також оптимізоване за кеш-локальністю збереження графів у форматі CSR (Compressed Sparse Row).

## 1. Детальна класифікація ребер та динаміка lowlink

Під час виконання обходу в глибину (DFS) кожне вихідне орієнтоване ребро `(u, v)` класифікується на один із трьох типів залежно від стану вершини `v`:

1. **Деревні ребра (Tree edges):** Вершина `v` ще не була відвідана (`tin[v] == 0`). Обхід рекурсивно занурюється в `DFS(v)`. Після повернення з рекурсії мінімальний досяжний час входу для `u` оновлюється через значення з піддерева:
```
low[u] = min(low[u], low[v])
```
2. **Зворотні ребра (Back edges):** Вершина `v` уже відвідана і перебуває у поточному стеку активних вершин (`in_stack[v] == true`). Це сигналізує про наявність орієнтованого циклу, який повертається до одного з предків у дереві DFS. Значення `low[u]` оновлюється безпосередньо через час входу предка:
```
low[u] = min(low[u], tin[v])
```
3. **Поперечні ребра (Cross edges):** Вершина `v` уже відвідана, але її прапорець `in_stack[v] == false`. Це означає, що вершина `v` належить до іншої компоненти сильної зв'язаності, яка була повністю сформована й закрита раніше. Таке ребро не надає шляху до предків вершини `u`, тому воно повністю ігнорується, і `low[u]` залишається без змін.

Коли рекурсивний обхід повністю завершує перегляд усіх вихідних ребер вершини `u`, алгоритм перевіряє фундаментальну умову кореня компоненти:
```
low[u] == tin[u]
```

Якщо ця рівність виконується, вершина `u` є коренем нової компоненти сильної зв'язаності. Усі вершини, розташовані на стеку active-вершин вище за `u` (включаючи саму `u`), знімаються зі стека за один цикл і формують складу поточної SCC.

Механіка роботи з допоміжним стеком active-вершин спирається на три інженерні інваріанти:
- Інваріант 1: Кожна відвідана вершина додається до стека строго один раз при вході у `DFS(u)`.
- Інваріант 2: Вершини у стеку знаходяться у порядку зростання часу їхнього входу `tin`.
- Інваріант 3: Коли обхід повертається у корінь компоненти `low[u] == tin[u]`, усі вершини цієї SCC утворюють нерозривний верхній підсегмент стека.

## 2. Обробка складних топологій та крайових випадків

Виробничий код алгоритму повинен коректно обробляти всі можливі крайові випадки та складні топології графів:

1. **Ізольовані вершини:** Вершина із нульовим вхідним та вихідним ступенем має `tin[u] == low[u]`, тому вона негайно створює компоненту сильної зв'язаності розміром в одну вершину.
2. **Орієнтований ациклічний граф (DAG):** У графі без циклів кожна вершина утворює окрему компоненту з одного елемента, оскільки для всіх вершин `low[u] == tin[u]`.
3. **Повний орієнтований цикл:** Усі вершини об'єднуються в єдину SCC розміру `V`.
4. **Ребра-самопетлі (`u -> u`):** Петля веде до цієї ж вершини, перебуває у стеку і не змінює її `low[u]`.
5. **Кратості ребер (паралельні дуги):** Кілька орієнтованих ребер `u -> v` обробляються повторно без порушення масиву `low`.

## 3. Рекурсивна реалізація мовами C та C++

У наведеній нижче вкладці показано класичну реалізацію алгоритму Таржана. C-версія використовує пряме управління пам'яттю та списки суміжності на покажчиках, тоді як C++ версія застосовує контейнери `std::vector`, `std::stack` та автоматичне керування ресурсами.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MIN(a, b) ((a) < (b) ? (a) : (b))

typedef struct EdgeNode {
    int to;
    struct EdgeNode* next;
} EdgeNode;

typedef struct {
    int num_vertices;
    EdgeNode** adj;
} Graph;

Graph* graph_create(int vertices) {
    Graph* g = (Graph*)malloc(sizeof(Graph));
    g->num_vertices = vertices;
    g->adj = (EdgeNode**)calloc(vertices, sizeof(EdgeNode*));
    return g;
}

void graph_add_edge(Graph* g, int u, int v) {
    EdgeNode* node = (EdgeNode*)malloc(sizeof(EdgeNode));
    node->to = v;
    node->next = g->adj[u];
    g->adj[u] = node;
}

void graph_free(Graph* g) {
    for (int i = 0; i < g->num_vertices; i++) {
        EdgeNode* curr = g->adj[i];
        while (curr) {
            EdgeNode* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(g->adj);
    free(g);
}

typedef struct {
    int timer;
    int stack_top;
    int* tin;
    int* low;
    int* stack;
    bool* in_stack;
    int scc_count;
} TarjanContext;

static void tarjan_dfs(int u, const Graph* g, TarjanContext* ctx) {
    ctx->tin[u] = ctx->low[u] = ++(ctx->timer);
    ctx->stack[++(ctx->stack_top)] = u;
    ctx->in_stack[u] = true;

    for (EdgeNode* edge = g->adj[u]; edge != NULL; edge = edge->next) {
        int v = edge->to;
        if (ctx->tin[v] == 0) {
            tarjan_dfs(v, g, ctx);
            ctx->low[u] = MIN(ctx->low[u], ctx->low[v]);
        } else if (ctx->in_stack[v]) {
            ctx->low[u] = MIN(ctx->low[u], ctx->tin[v]);
        }
    }

    if (ctx->low[u] == ctx->tin[u]) {
        ctx->scc_count++;
        printf("SCC #%d: [ ", ctx->scc_count);
        while (1) {
            int v = ctx->stack[(ctx->stack_top)--];
            ctx->in_stack[v] = false;
            printf("%d ", v);
            if (u == v) break;
        }
        printf("]\n");
    }
}

void find_scc_recursive(const Graph* g) {
    int v_count = g->num_vertices;
    TarjanContext ctx;
    ctx.timer = 0;
    ctx.stack_top = -1;
    ctx.scc_count = 0;

    ctx.tin = (int*)calloc(v_count, sizeof(int));
    ctx.low = (int*)calloc(v_count, sizeof(int));
    ctx.stack = (int*)malloc(v_count * sizeof(int));
    ctx.in_stack = (bool*)calloc(v_count, sizeof(bool));

    for (int i = 0; i < v_count; i++) {
        if (ctx.tin[i] == 0) {
            tarjan_dfs(i, g, &ctx);
        }
    }

    free(ctx.tin);
    free(ctx.low);
    free(ctx.stack);
    free(ctx.in_stack);
}
```
```cpp
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <span >

class TarjanSCCSolver {
public:
    explicit TarjanSCCSolver(int vertices)
        : adj_(vertices), tin_(vertices, 0), low_(vertices, 0), in_stack_(vertices, false) {}

    void add_edge(int u, int v) {
        adj_[u].push_back(v);
    }

    std::vector<std::vector<int>> compute_scc() {
        sccs_.clear();
        timer_ = 0;
        std::fill(tin_.begin(), tin_.end(), 0);
        std::fill(low_.begin(), low_.end(), 0);
        std::fill(in_stack_.begin(), in_stack_.end(), false);

        for (int i = 0; i < static_cast<int>(adj_.size()); ++i) {
            if (tin_[i] == 0) {
                dfs(i);
            }
        }
        return sccs_;
    }

private:
    std::vector<std::vector<int>> adj_;
    std::vector<int> tin_;
    std::vector<int> low_;
    std::vector<bool> in_stack_;
    std::stack<int> st_;
    std::vector<std::vector<int>> sccs_;
    int timer_{0};

    void dfs(int u) {
        tin_[u] = low_[u] = ++timer_;
        st_.push(u);
        in_stack_[u] = true;

        for (int v : adj_[u]) {
            if (tin_[v] == 0) {
                dfs(v);
                low_[u] = std::min(low_[u], low_[v]);
            } else if (in_stack_[v]) {
                low_[u] = std::min(low_[u], tin_[v]);
            }
        }

        if (low_[u] == tin_[u]) {
            std::vector<int> current_scc;
            while (true) {
                int v = st_.top();
                st_.pop();
                in_stack_[v] = false;
                current_scc.push_back(v);
                if (u == v) break;
            }
            sccs_.push_back(std::move(current_scc));
        }
    }
};
```
:::

## 4. Ітеративна нерекурсивна версія для захисту від Stack Overflow

На надвеликих графах із глибиною обходу `|V| > 100 000` (наприклад, глибинних ланцюжках залежностей чи бамбукових графах) рекурсивний DFS заповнює системний стек виконання, що призводить до падіння програми через переповнення стека (`stack overflow`). Щоб цього уникнути, системну рекурсію замінюють явним програмним стеком фреймів `(u, edge_index)`.

Кожен фрейм ітеративного стека зберігає поточну вершину `u` та індекс `edge_idx` наступного ребра у списку суміжності `adj[u]`. При переході по деревному ребру новий фрейм додається на вершину стека, а при поверненні значення `low` батьківського фрейму релаксується.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MIN(a,b) ((a) < (b) ? (a) : (b))

typedef struct {
    int u;
    EdgeNode* curr_edge;
} FrameC;

void find_scc_iterative_c(const Graph* g) {
    int n = g->num_vertices;
    int* tin = (int*)calloc(n, sizeof(int));
    int* low = (int*)calloc(n, sizeof(int));
    bool* in_stack = (bool*)calloc(n, sizeof(bool));
    int* scc_stack = (int*)malloc(n * sizeof(int));
    int scc_top = -1;
    int timer = 0;

    FrameC* dfs_stack = (FrameC*)malloc(n * sizeof(FrameC));
    int dfs_top = -1;

    for (int start = 0; start < n; start++) {
        if (tin[start] != 0) continue;

        dfs_stack[++dfs_top] = (FrameC){start, g->adj[start]};
        tin[start] = low[start] = ++timer;
        scc_stack[++scc_top] = start;
        in_stack[start] = true;

        while (dfs_top >= 0) {
            FrameC* frame = &dfs_stack[dfs_top];
            int u = frame->u;

            if (frame->curr_edge != NULL) {
                int v = frame->curr_edge->to;
                frame->curr_edge = frame->curr_edge->next;

                if (tin[v] == 0) {
                    tin[v] = low[v] = ++timer;
                    scc_stack[++scc_top] = v;
                    in_stack[v] = true;
                    dfs_stack[++dfs_top] = (FrameC){v, g->adj[v]};
                } else if (in_stack[v]) {
                    low[u] = MIN(low[u], tin[v]);
                }
            } else {
                dfs_top--;
                if (dfs_top >= 0) {
                    int parent = dfs_stack[dfs_top].u;
                    low[parent] = MIN(low[parent], low[u]);
                }

                if (low[u] == tin[u]) {
                    printf("SCC (iterative C): [ ");
                    while (1) {
                        int v = scc_stack[scc_top--];
                        in_stack[v] = false;
                        printf("%d ", v);
                        if (u == v) break;
                    }
                    printf("]\n");
                }
            }
        }
    }

    free(tin); free(low); free(in_stack); free(scc_stack); free(dfs_stack);
}
```
```cpp
#include <vector>
#include <stack>
#include <algorithm>

std::vector<std::vector<int>> compute_scc_iterative_cpp(int n, const std::vector<std::vector<int>>& adj) {
    std::vector<int> tin(n, 0), low(n, 0);
    std::vector<bool> in_stack(n, false);
    std::stack<int> scc_stack;
    std::vector<std::vector<int>> result;
    int timer = 0;

    struct DfsFrame {
        int u;
        size_t edge_idx;
    };
    std::stack<DfsFrame> dfs_stack;

    for (int start = 0; start < n; ++start) {
        if (tin[start] != 0) continue;

        dfs_stack.push({start, 0});
        tin[start] = low[start] = ++timer;
        scc_stack.push(start);
        in_stack[start] = true;

        while (!dfs_stack.empty()) {
            auto& [u, idx] = dfs_stack.top();

            if (idx < adj[u].size()) {
                int v = adj[u][idx++];
                if (tin[v] == 0) {
                    tin[v] = low[v] = ++timer;
                    scc_stack.push(v);
                    in_stack[v] = true;
                    dfs_stack.push({v, 0});
                } else if (in_stack[v]) {
                    low[u] = std::min(low[u], tin[v]);
                }
            } else {
                dfs_stack.pop();
                if (!dfs_stack.empty()) {
                    int parent = dfs_stack.top().u;
                    low[parent] = std::min(low[parent], low[u]);
                }

                if (low[u] == tin[u]) {
                    std::vector<int> current_scc;
                    while (true) {
                        int v = scc_stack.top();
                        scc_stack.pop();
                        in_stack[v] = false;
                        current_scc.push_back(v);
                        if (u == v) break;
                    }
                    result.push_back(std::move(current_scc));
                }
            }
        }
    }
    return result;
}
```
:::

## 5. Покроковий розбір трасування на конкретному прикладі

Розглянемо виконання алгоритму Таржана на орієнтованому графі з 5 вершин (нумерація 0..4) із ребрами: `1 -> 0`, `0 -> 2`, `2 -> 1`, `0 -> 3`, `3 -> 4`.

Детальна послідовність дій алгоритму:
- Крок 1: Обхід починається з вершини 0. Встановлюються значення `tin[0] = 1`, `low[0] = 1`. Вершина 0 штовхається у стек активних вершин. Стек = `[0]`.
- Крок 2: З 0 переходимо по деревній дузі `0 -> 2`. Встановлюються `tin[2] = 2`, `low[2] = 2`. Стек = `[0, 2]`.
- Крок 3: З 2 переходимо по деревній дузі `2 -> 1`. Встановлюються `tin[1] = 3`, `low[1] = 3`. Стек = `[0, 2, 1]`.
- Крок 4: З 1 переглядаємо вихідне ребро `1 -> 0`. Вершина 0 вже була відвідана (`tin[0] = 1`) і перебуває у стеку active-вершин (`in_stack[0] == true`). Це зворотне ребро. Значення `low[1]` оновлюється через час входу предка: `low[1] = min(low[1], tin[0]) = min(3, 1) = 1`.
- Крок 5: Повернення в рекурсивному обході до вершини 2. Значення `low[2]` підтягує мінімальний досяжний час з піддерева: `low[2] = min(low[2], low[1]) = min(2, 1) = 1`.
- Крок 6: Повернення до вершини 0. Значення `low[0]` релаксується: `low[0] = min(low[0], low[2]) = min(1, 1) = 1`.
- Крок 7: З 0 переходимо по другому вихідному ребру `0 -> 3`. Встановлюються `tin[3] = 4`, `low[3] = 4`. Стек = `[0, 2, 1, 3]`.
- Крок 8: З 3 переходимо по деревній дузі `3 -> 4`. Встановлюються `tin[4] = 5`, `low[4] = 5`. Стек = `[0, 2, 1, 3, 4]`.
- Крок 9: Вершина 4 не має вихідних ребер. Обхід перевіряє умову кореня: `low[4] == tin[4]` (5 == 5). Вершина 4 є коренем нової SCC. Зі стека вилучаються вершини до 4 включно. Сформовано компоненту SCC #1 = `{4}`.
- Крок 10: Повернення у вершину 3. Релаксація `low[3] = min(4, low[4]) = 4`. Умова кореня: `low[3] == tin[3]` (4 == 4). Вершина 3 є коренем нової SCC. Зі стека вилучається `{3}`. Сформовано SCC #2 = `{3}`.
- Крок 11: Повернення у вершину 0. Перевірка умови кореня: `low[0] == tin[0]` (1 == 1). Вершина 0 є коренем першої компоненти. Зі стека вилучаються всі вершини до 0 включно: `{1, 2, 0}`. Сформовано SCC #3 = `{0, 1, 2}`.

Підсумковий результат розбиття: три компоненти сильної зв'язаності SCC #1 = `{4}`, SCC #2 = `{3}`, SCC #3 = `{0, 1, 2}`.

## 6. Кеш-оптимізоване представлення CSR (Compressed Sparse Row)

Використання зв'язаних списків `EdgeNode*` або векторів векторів `std::vector<std::vector<int>>` призводить до частих промахів повз кеш L1/L2 процесора через розсіювання вузлів у пам'яті. Збереження графа у вигляді CSR (стиснений плаский масив) прискорює аналіз у 3–5 разів на щільних графах.

:::tabs
```c
typedef struct {
    int num_vertices;
    int num_edges;
    int* row_ptr; /* Масив розміром V + 1 зі зсувами для кожної вершини */
    int* cols;    /* Плаский масив мети ребер розміром E */
} CSRGraph;

void tarjan_csr_c(const CSRGraph* g) {
    int n = g->num_vertices;
    int* tin = (int*)calloc(n, sizeof(int));
    int* low = (int*)calloc(n, sizeof(int));
    bool* in_stack = (bool*)calloc(n, sizeof(bool));
    int* stack = (int*)malloc(n * sizeof(int));
    int top = -1, timer = 0;

    for (int i = 0; i < n; i++) {
        if (tin[i] == 0) {
            /* Запуск обходу з вершини i */
        }
    }

    free(tin); free(low); free(in_stack); free(stack);
}
```
```cpp
struct CSRGraphCPP {
    int vertex_count{0};
    std::vector<int> row_offsets; // Size V + 1
    std::vector<int> column_indices; // Size E

    [[nodiscard]] std::span<const int> neighbors(int u) const noexcept {
        return std::span<const int>(
            column_indices.data() + row_offsets[u],
            row_offsets[u + 1] - row_offsets[u]
        );
    }
};
```
:::

## 7. Комплексний тестовий стенд (Unit Test Runner)

Нижче наведено тестовий модуль для перевірки коректності функціонування обчислювача Таржана.

```cpp
#include <iostream>
#include <cassert>

void run_unit_tests() {
    // Тест 1: Простий граф із циклом 1->0->2->1
    TarjanSCCSolver test1(5);
    test1.add_edge(1, 0);
    test1.add_edge(0, 2);
    test1.add_edge(2, 1);
    test1.add_edge(0, 3);
    test1.add_edge(3, 4);

    auto res1 = test1.compute_scc();
    assert(res1.size() == 3);
    std::cout << "Unit test 1 (Cycle + DAG path): PASSED\n";

    // Тест 2: DAG граф (кожна вершина — окрема SCC)
    TarjanSCCSolver test2(4);
    test2.add_edge(0, 1);
    test2.add_edge(1, 2);
    test2.add_edge(2, 3);

    auto res2 = test2.compute_scc();
    assert(res2.size() == 4);
    std::cout << "Unit test 2 (DAG graph): PASSED\n";

    std::cout << "All unit tests completed successfully!\n";
}

int main() {
    run_unit_tests();
    return 0;
}
```
