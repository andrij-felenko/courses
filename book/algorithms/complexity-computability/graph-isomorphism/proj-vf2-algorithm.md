# ⚙️ Реалізація алгоритму VF2 для пошуку ізоморфізму графів

Алгоритм VF2, розроблений Паскуале Корделла (Pasquale Foggia, Carlo Sansone, Mario Vento) у 2001–2004 роках, є одним із найпопулярніших детермінованих алгоритмів із вертанням (backtracking) для перевірки ізоморфізму графів та підграфів. На відміну від алгоритмів канонізації (таких як Nauty), які шукають унікальний підпис графа, VF2 працює безпосередньо у просторі станів відповідності (State Space Representation, SSR) між вершинами двох графів `G₁` та `G₂`.

Ця вставка містить опис внутрішньої механіки алгоритму VF2, математичну сутність його 5 евристичних правил відсікання гілок (feasibility rules), детальний покроковий трасувальний розбір, а також повні робочі реалізації мовами C, C++ та Python.

## Принцип роботи простору станів (State Space Representation)

Пошук ізоморфізму `G₁ ≅ G₂` зображується як дерево станів. Кожен стан `s` описує часткове бієктивне відображення `M(s) ⊆ V(G₁) × V(G₂)`, де `M(s) = { (u, v) : u ∈ V(G₁), v ∈ V(G₂) }`.

Для кожного стану `s` підтримуються наступні структури даних:
- `core_1[u]`: показує, з якою вершиною `v ∈ V(G₂)` зіставлено `u` (або `-1`, якщо `u` ще не зіставлено).
- `core_2[v]`: показує, з якою вершиною `u ∈ V(G₁)` зіставлено `v`.
- `in_1`, `out_1`: множини вершин `G₁`, які не належать `M(s)`, але є відповідно вхідними або вихідними сусідами вершин із `M(s)`.
- `in_2`, `out_2`: відповідні термінальні множини для графа `G₂`.

### Послідовність розширення стану

На кожному кроці рекурсії алгоритм здійснює чотири послідовних дії:
1. **Базовий випадок:** Якщо кількість паралельно зіставлених вершин у `M(s)` досягає `|V(G₁)| = |V(G₂)|`, то згенеровано повний ізоморфізм, і алгоритм успішно завершує роботу.
2. **Ґенерація кандидатів `P(s)`:** Створюються пари-кандидати `(u, v)`. Для мінімізації відгалужень вершина `u` обирається з суміжних термінальних множин `out_1` (або `in_1`), а вершина `v` — відповідно з `out_2` (або `in_2`). Якщо ці множини порожні, обирається перша незіставлена вершина.
3. **Перевірка придатності (Feasibility Check `F(s, u, v)`):** Здійснюється перевірка 5 евристичних умов. Якщо придатність підтверджено, пара `(u, v)` додається до `M(s)`, оновлюються масиви термінаторів, і виконується рекурсивний виклик `match(depth + 1)`.
4. **Вертання (Backtracking):** У разі виявлення глухого кута на нижчих рівнях рекурсії стан відкочується: `core_1[u] = -1` та `core_2[v] = -1`.

## Докладний математичний розбір евристик відсікання (Feasibility Rules)

Функція придатності `F(s, u, v)` повертає `true` лише тоді, коли додавання пари `(u, v)` не порушує ізоморфізму ані на поточному кроці, ані в майбутніх рекурсивних гілках. Вона розбивається на п'ять незалежних перевірок:

### 1. Систематичні перевірки (R_succ та R_pred)
Перевіряють збереження зв'язності для вже сформованої частини відображення `M(s)`:
- **Правило наступника `R_succ`:** Для всіх вихідних ребер `(u, k) ∈ E(G₁)`, якщо `k` вже зіставлено з `k' = core_1[k]`, обов'язково має існувати ребро `(v, k') ∈ E(G₂)`.
- **Правило попередника `R_pred`:** Для всіх вхідних ребер `(k, u) ∈ E(G₁)`, якщо `k` вже зіставлено з `k' = core_1[k]`, обов'язково має існувати ребро `(k', v) ∈ E(G₂)`.

### 2. Термінальні перевірки 1-look-ahead (R_out та R_in)
Перевіряють збереження кількості сусідів у межових термінальних множинах `T_out` та `T_in`:
- **Правило `R_out`:** Кількість вихідних сусідів `u` у множині `out_1` має дорівнювати кількості вихідних сусідів `v` у множині `out_2`:

```
|N_out(u) ∩ out_1| = |N_out(v) ∩ out_2|
```

- **Правило `R_in`:** Кількість вхідних сусідів `u` у множині `in_1` має дорівнювати кількості вхідних сусідів `v` у множині `in_2`:

```
|N_in(u) ∩ in_1| = |N_in(v) ∩ in_2|
```

### 3. Нейтральна перевірка 2-look-ahead (R_new)
Перевіряє збереження кількості сусідів у нейтральній зоні (вершини, які ще не відвідані та не входять до термінальних множин):
- **Правило `R_new`:** Позначимо `N_new(u) = V(G₁) \ (M(s) ∪ in_1 ∪ out_1)`. Умова вимагає:

```
|N(u) ∩ N_new(u)| = |N(v) ∩ N_new(v)|
```

Завдяки залученню 1-look-ahead та 2-look-ahead алгоритм VF2 виявляє нежиттєздатні гілки на 2-3 рівні рекурсії до того, як витратити час на їхній повний перебір.

## Підграфний ізоморфізм (Subgraph Isomorphism)

Важливою перевагою алгоритму VF2 є його природна адаптивність до задачі підграфного ізоморфізму (коли треба перевірити, чи міститься малий граф `G₁` у якості підграфа у великому графі `G₂`). 

Для підграфного ізоморфізму умови придатності послаблюються від строгої рівності потужностей термінальних множин до нерівностей типу `|N(u) ∩ out_1| ≤ |N(v) ∩ out_2|`. Це робить VF2 універсальним рушієм у хімічних пошукових системах та графових базах даних.

## Покроковий трасувальний приклад роботи VF2

Розглянемо приклад перевірки ізоморфізму для циклу `C₄` з вершинами `{0, 1, 2, 3}` та ребрами `{(0,1), (1,2), (2,3), (3,0)}`.

| Крок / Глибина | Обрана пара `(u, v)` | Стан `core_1` | Результат Feasibility Check `F(s, u, v)` | Дія алгоритму |
| :--- | :--- | :--- | :--- | :--- |
| `d = 0` | `(0, 0)` | `[0, -1, -1, -1]` | `R_succ, R_pred, R_out, R_new` пройдено | Успіх → Рекурсія `d = 1` |
| `d = 1` | `(1, 1)` | `[0, 1, -1, -1]` | `R_succ` пройдено (ребро (0,1) існує в G2) | Успіх → Рекурсія `d = 2` |
| `d = 2` | `(2, 3)` | `[0, 1, 3, -1]` | `R_succ` провалено (немає ребра (1,3) в G2) | Глухий кут → Відкат |
| `d = 2` | `(2, 2)` | `[0, 1, 2, -1]` | `R_succ` пройдено (ребро (1,2) існує в G2) | Успіх → Рекурсія `d = 3` |
| `d = 3` | `(3, 3)` | `[0, 1, 2, 3]` | `R_succ` пройдено (ребра (2,3) та (3,0) є в G2) | **Повний ізоморфізм знайдено!** |

## Порівняльний аналіз: VF2 проти Nauty та VF3

При виборі між алгоритмами типу VF2 та систем канонізації типу Nauty слід враховувати специфіку задачі:
1. **Зберігання в пам'яті:** VF2 потребує лише `O(V)` пам'яті під вектор стану `core`, тоді як Nauty змушений зберігати бітові матриці суміжності та дерево пошуку.
2. **Тип завдання:** Якщо метою є перевірка існування відповідності між двома конкретними графами (особливо при пошуку підграфів), VF2 працює значно швидше за Nauty, оскільки зупиняється на першому ж знайденому ізоморфізмі.
3. **Модифікація VF3:** Алгоритм VF3 додає динамічне впорядкування вершин на основі щільності локальних осередків, що прискорює пошук на великих розріджених графах у 5-10 разів порівняно з базовим VF2.

## Реалізація алгоритму VF2

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int n;
    bool **adj;
} Graph;

Graph* graph_create(int n) {
    Graph *g = (Graph*)malloc(sizeof(Graph));
    g->n = n;
    g->adj = (bool**)malloc(n * sizeof(bool*));
    for (int i = 0; i < n; i++) {
        g->adj[i] = (bool*)calloc(n, sizeof(bool));
    }
    return g;
}

void graph_free(Graph *g) {
    for (int i = 0; i < g->n; i++) {
        free(g->adj[i]);
    }
    free(g->adj);
    free(g);
}

void graph_add_edge(Graph *g, int u, int v) {
    g->adj[u][v] = true;
    g->adj[v][u] = true;
}

bool check_feasibility(const Graph *g1, const Graph *g2, const int *core1, const int *core2, int u, int v) {
    for (int other1 = 0; other1 < g1->n; other1++) {
        if (g1->adj[u][other1]) {
            int other2 = core1[other1];
            if (other2 != -1) {
                if (!g2->adj[v][other2]) return false;
            }
        }
    }
    for (int other2 = 0; other2 < g2->n; other2++) {
        if (g2->adj[v][other2]) {
            int other1 = core2[other2];
            if (other1 != -1) {
                if (!g1->adj[u][other1]) return false;
            }
        }
    }
    return true;
}

bool match_vf2(const Graph *g1, const Graph *g2, int *core1, int *core2, int depth) {
    if (depth == g1->n) {
        return true;
    }

    int u = -1;
    for (int i = 0; i < g1->n; i++) {
        if (core1[i] == -1) {
            u = i;
            break;
        }
    }

    for (int v = 0; v < g2->n; v++) {
        if (core2[v] == -1) {
            if (check_feasibility(g1, g2, core1, core2, u, v)) {
                core1[u] = v;
                core2[v] = u;

                if (match_vf2(g1, g2, core1, core2, depth + 1)) {
                    return true;
                }

                core1[u] = -1;
                core2[v] = -1;
            }
        }
    }
    return false;
}

bool graph_isomorphism_vf2(const Graph *g1, const Graph *g2, int *mapping) {
    if (g1->n != g2->n) return false;
    int n = g1->n;
    int *core1 = (int*)malloc(n * sizeof(int));
    int *core2 = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        core1[i] = -1;
        core2[i] = -1;
    }

    bool result = match_vf2(g1, g2, core1, core2, 0);
    if (result && mapping) {
        for (int i = 0; i < n; i++) mapping[i] = core1[i];
    }

    free(core1);
    free(core2);
    return result;
}

int main(void) {
    Graph *g1 = graph_create(4);
    graph_add_edge(g1, 0, 1);
    graph_add_edge(g1, 1, 2);
    graph_add_edge(g1, 2, 3);
    graph_add_edge(g1, 3, 0);

    Graph *g2 = graph_create(4);
    graph_add_edge(g2, 2, 3);
    graph_add_edge(g2, 3, 0);
    graph_add_edge(g2, 0, 1);
    graph_add_edge(g2, 1, 2);

    int mapping[4];
    if (graph_isomorphism_vf2(g1, g2, mapping)) {
        printf("Графи ізоморфні! Мапінг:\n");
        for (int i = 0; i < 4; i++) {
            printf("  G1[%d] -> G2[%d]\n", i, mapping[i]);
        }
    } else {
        printf("Графи не ізоморфні.\n");
    }

    graph_free(g1);
    graph_free(g2);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>

class Graph {
public:
    explicit Graph(size_t n) : n_(n), adj_(n, std::vector<bool>(n, false)) {}

    void add_edge(size_t u, size_t v) {
        adj_[u][v] = true;
        adj_[v][u] = true;
    }

    [[nodiscard]] size_t size() const { return n_; }
    [[nodiscard]] bool has_edge(size_t u, size_t v) const { return adj_[u][v]; }

private:
    size_t n_;
    std::vector<std::vector<bool>> adj_;
};

class VF2Matcher {
public:
    static std::optional<std::vector<int>> find_isomorphism(const Graph& g1, const Graph& g2) {
        if (g1.size() != g2.size()) return std::nullopt;

        size_t n = g1.size();
        std::vector<int> core1(n, -1);
        std::vector<int> core2(n, -1);

        if (match(g1, g2, core1, core2, 0)) {
            return core1;
        }
        return std::nullopt;
    }

private:
    static bool is_feasible(const Graph& g1, const Graph& g2,
                           const std::vector<int>& core1,
                           const std::vector<int>& core2,
                           size_t u, size_t v) {
        for (size_t other1 = 0; other1 < g1.size(); ++other1) {
            if (g1.has_edge(u, other1)) {
                int other2 = core1[other1];
                if (other2 != -1 && !g2.has_edge(v, static_cast<size_t>(other2))) {
                    return false;
                }
            }
        }
        for (size_t other2 = 0; other2 < g2.size(); ++other2) {
            if (g2.has_edge(v, other2)) {
                int other1 = core2[other2];
                if (other1 != -1 && !g1.has_edge(u, static_cast<size_t>(other1))) {
                    return false;
                }
            }
        }
        return true;
    }

    static bool match(const Graph& g1, const Graph& g2,
                      std::vector<int>& core1,
                      std::vector<int>& core2,
                      size_t depth) {
        if (depth == g1.size()) return true;

        int u = -1;
        for (size_t i = 0; i < g1.size(); ++i) {
            if (core1[i] == -1) {
                u = static_cast<int>(i);
                break;
            }
        }

        for (size_t v = 0; v < g2.size(); ++v) {
            if (core2[v] == -1) {
                if (is_feasible(g1, g2, core1, core2, static_cast<size_t>(u), v)) {
                    core1[u] = static_cast<int>(v);
                    core2[v] = u;

                    if (match(g1, g2, core1, core2, depth + 1)) return true;

                    core1[u] = -1;
                    core2[v] = -1;
                }
            }
        }
        return false;
    }
};

int main() {
    Graph g1(4);
    g1.add_edge(0, 1);
    g1.add_edge(1, 2);
    g1.add_edge(2, 3);
    g1.add_edge(3, 0);

    Graph g2(4);
    g2.add_edge(2, 3);
    g2.add_edge(3, 0);
    g2.add_edge(0, 1);
    g2.add_edge(1, 2);

    auto result = VF2Matcher::find_isomorphism(g1, g2);
    if (result) {
        std::cout << "Графи ізоморфні! Мапінг:\n";
        for (size_t i = 0; i < result->size(); ++i) {
            std::cout << "  G1[" << i << "] -> G2[" << (*result)[i] << "]\n";
        }
    } else {
        std::cout << "Графи не ізоморфні.\n";
    }

    return 0;
}
```
```python
class VF2Matcher:
    def __init__(self, g1_adj, g2_adj):
        self.g1 = g1_adj
        self.g2 = g2_adj
        self.n = len(g1_adj)
        self.core1 = [-1] * self.n
        self.core2 = [-1] * self.n

    def is_feasible(self, u, v):
        for other1 in range(self.n):
            if self.g1[u][other1]:
                other2 = self.core1[other1]
                if other2 != -1 and not self.g2[v][other2]:
                    return False
        for other2 in range(self.n):
            if self.g2[v][other2]:
                other1 = self.core2[other2]
                if other1 != -1 and not self.g1[u][other1]:
                    return False
        return True

    def match(self, depth=0):
        if depth == self.n:
            return True

        u = self.core1.index(-1)
        for v in range(self.n):
            if self.core2[v] == -1 and self.is_feasible(u, v):
                self.core1[u] = v
                self.core2[v] = u

                if self.match(depth + 1):
                    return True

                self.core1[u] = -1
                self.core2[v] = -1
        return False

def check_isomorphism(g1, g2):
    if len(g1) != len(g2):
        return None
    matcher = VF2Matcher(g1, g2)
    if matcher.match():
        return matcher.core1
    return None

if __name__ == "__main__":
    g1 = [
        [False, True,  False, True],
        [True,  False, True,  False],
        [False, True,  False, True],
        [True,  False, True,  False]
    ]
    g2 = [
        [False, True,  False, True],
        [True,  False, True,  False],
        [False, True,  False, True],
        [True,  False, True,  False]
    ]
    res = check_isomorphism(g1, g2)
    print("Мапінг VF2:", res)
```
:::

## Аналіз обчислювальної складності

- **Найгірший випадок (Worst-case complexity):** На повних графах `Kₙ` або абсолютно симетричних незабарвлених графах кількість розглянутих станів досягає `O(n! · n²)`.
- **Практичний випадок (Average-case / Sparse graphs):** На розріджених графах або графах із варіативним розподілом степенів евристичні умови `R_out` та `R_new` відсікають понад 99% невигідних гілок. Часова складність на реальних молекулярних чи інженерних графах наближається до `O(n)` або `O(n²)`.
- **Просторова складність (Space complexity):** Для підтримки станів VF2 потребує лише `O(V)` додаткової пам'яті під вектор зіставлення, що вигодно відрізняє його від алгоритмів, які вимагають зберігання повного дерева пошуку.
