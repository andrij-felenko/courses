# ⚙️ Алгоритми досяжності в логарифмічній пам'яті: детермінований перебір, 2-SAT та оракульний пошук

Перевірка досяжності у графах є основою для багатьох системних та компіляторних алгоритмів. Стандартний обхід у ширину (BFS) чи глибину (DFS) вимагає збереження масиву відвіданих вершин або стека викликів, що займає `O(|V|)` оперативної пам'яті. Проте у мікроконтролерах із суворим обмеженням RAM або при обробці велетенських графів на дисках потрібні алгоритми, які мінімізують просторову складність.

Мінімізація обсягу пам'яті досягається за допомогою алгоритму рекурсивного ділення навпіл (алгоритму Савича для `DSPACE(\log² n)`), а також детермінованого розв'язувача 2-SAT через граф імплікацій.

---

## 1. Детермінована досяжність за алгоритмом Савича

Алгоритм Савича дозволяє детерміновано перевірити досяжність вершини `t` з `s` у графі з `n` вершинами за допомогою пам'яті `O(\log² n)`. Його основа — рекурсивна перевірка існування проміжної вершини `w`, через яку можна пройти за половину від початкової кількості кроків.

Головна особливість алгоритму полягає у тому, що замість звичайного рекурсивного обходу у глибину, де глибина стека може сягати `n` рівнів, Савич розділяє шлях навпіл на кожному кроці. Це знижує глибину стека викликів до `\log_2 n` рівнів. Оскільки на кожному рівні зберігається лише індекс проміжної вершини `w` (який займає `\log_2 n` бітів), загальний обсяг пам'яті становить `\log_2 n · \log_2 n = O(\log² n)`.

При практичному програмуванні мовами C та C++ необхідно забезпечити відсутність динамічного виділення пам'яті у купі (`heap`). Виклик `malloc` або `new` під час рекурсивного обходу графа не лише призводить до накладних витрат часу, але й створює ризик фрагментації пам'яті. Рекурсивні виклики у реалізації Савича спираються виключно на кадр стека виконання (Stack Frame).

Для оптимізації розміру стек-кадра кожна зміна локальних змінних мінімізується: параметр `steps` передається як беззнакове ціле число `uint32_t`, а матриця суміжності відображається через вказівник на статичний масив або обгортку `std::span` без копіювання даних.

Нижче наведено практичні реалізації алгоритму Савича мовами C та C++.

:::tabs
```c
/* C11 implementation: Savitch's deterministic reachability algorithm */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_VERTICES 64

typedef struct {
    uint32_t num_vertices;
    bool adj[MAX_VERTICES][MAX_VERTICES];
} Graph;

/* 
 * Savitch's recursive reachability check.
 * Evaluates if vertex 'v' is reachable from 'u' in at most 'steps' edges.
 * Stack depth is limited to O(log2 N), each frame uses O(log2 N) memory.
 */
bool savitch_can_reach(const Graph *g, uint32_t u, uint32_t v, uint32_t steps) {
    if (u == v) {
        return true;
    }
    if (steps == 1) {
        return g->adj[u][v];
    }

    uint32_t half_steps = (steps + 1) / 2;

    /* Iterate over all potential intermediate vertices w */
    for (uint32_t w = 0; w < g->num_vertices; ++w) {
        if (savitch_can_reach(g, u, w, half_steps)) {
            if (savitch_can_reach(g, w, v, steps - half_steps)) {
                return true;
            }
        }
    }

    return false;
}

int main(void) {
    Graph g = { .num_vertices = 5 };
    
    /* Construct graph edges */
    g.adj[0][1] = true;
    g.adj[1][2] = true;
    g.adj[2][3] = true;
    g.adj[3][4] = true;

    uint32_t start_vertex = 0;
    uint32_t target_vertex = 4;

    bool reachable = savitch_can_reach(&g, start_vertex, target_vertex, g.num_vertices);

    if (reachable) {
        printf("Vertex %u is REACHABLE from %u\n", target_vertex, start_vertex);
    } else {
        printf("Vertex %u is NOT reachable from %u\n", target_vertex, start_vertex);
    }

    return 0;
}
```
```cpp
// C++20 implementation: Idiomatic zero-allocation Savitch reachability solver
#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <expected>
#include <system_error>

namespace space_complexity {

class GraphView {
public:
    explicit GraphView(uint32_t vertices, std::span<const uint8_t> matrix_data)
        : num_vertices_(vertices), matrix_(matrix_data) {}

    [[nodiscard]] bool has_edge(uint32_t u, uint32_t v) const noexcept {
        if (u >= num_vertices_ || v >= num_vertices_) {
            return false;
        }
        return matrix_[u * num_vertices_ + v] != 0;
    }

    [[nodiscard]] uint32_t size() const noexcept {
        return num_vertices_;
    }

private:
    uint32_t num_vertices_;
    std::span<const uint8_t> matrix_;
};

enum class ReachabilityError {
    InvalidVertexIndex,
    MaxDepthExceeded
};

class SavitchSolver {
public:
    // Evaluates if target is reachable from source within given steps
    [[nodiscard]] static std::expected<bool, ReachabilityError> is_reachable(
        const GraphView& graph, uint32_t source, uint32_t target) noexcept 
    {
        if (source >= graph.size() || target >= graph.size()) {
            return std::unexpected(ReachabilityError::InvalidVertexIndex);
        }
        return can_reach_recursive(graph, source, target, graph.size());
    }

private:
    static bool can_reach_recursive(
        const GraphView& graph, uint32_t u, uint32_t v, uint32_t steps) noexcept 
    {
        if (u == v) {
            return true;
        }
        if (steps == 1) {
            return graph.has_edge(u, v);
        }

        const uint32_t half_steps = (steps + 1) / 2;

        for (uint32_t w = 0; w < graph.size(); ++w) {
            if (can_reach_recursive(graph, u, w, half_steps) &&
                can_reach_recursive(graph, w, v, steps - half_steps)) {
                return true;
            }
        }

        return false;
    }
};

} // namespace space_complexity

int main() {
    constexpr uint32_t N = 5;
    const std::vector<uint8_t> adj_matrix = {
        0, 1, 0, 0, 0,
        0, 0, 1, 0, 0,
        0, 0, 0, 1, 0,
        0, 0, 0, 0, 1,
        0, 0, 0, 0, 0
    };

    space_complexity::GraphView graph(N, adj_matrix);
    
    auto result = space_complexity::SavitchSolver::is_reachable(graph, 0, 4);

    if (result.has_value()) {
        std::cout << "Reachable: " << std::boolalpha << result.value() << "\n";
    } else {
        std::cerr << "Reachability evaluation error occurred.\n";
    }

    return 0;
}
```
:::

---

## 2. Розв'язувач 2-SAT через граф імплікацій у логарифмічній пам'яті

Задача 2-SAT зводиться за логарифмічною пам'яттю до перевірки досяжності в орієнтованому графі імплікацій. Для кожної булевої змінної `x_i` у графі створюються дві вершини: `x_i` та `¬x_i`. Кожна диз'юнкція `(A ∨ B)` перетворюється на дві орієнтовані імплікаційні дуги: `¬A → B` та `¬B → A`.

Формула є здійсненною тоді й лише тоді, коли у графі імплікацій не існує такої змінної `x_i`, що з `x_i` можна дістатися до `¬x_i` **і** з `¬x_i` можна дістатися до `x_i`.

Для обчислення дуг графа імплікацій алгоритм не створює матрицю суміжності в оперативній пам'яті. Замість цього використовується **функція віртуального зчитування ребер (Virtual Edge Function)**, яка перевіряє наявність імплікації безпосередньо за вхідним масивом диз'юнктів. Це підтримує контракт логарифмічного трансд'юсера: вхідні дані лежать у пам'яті тільки для читання, а алгоритм лише повертає відповідь на запит належності ребра.

З точки зору теорії сильної зв'язності (Strongly Connected Components, SCC), суперечність виникає тоді, коли змінна `x_i` та її заперечення `¬x_i` потрапляють в одну й ту саму сильно зв'язану компоненту графа імплікацій. Стандартний алгоритм Тар'яна або Косарайю для пошуку SCC вимагає `O(|V| + |E|)` пам'яті для зберігання масиву відвіданих вершин та стеків обходу. Натомість наш підхід з рекурсією Савича замінює масив відвіданих вершин на повторну перевірку дуг за допомогою віртуальної функції, знижуючи використання RAM до `O(\log² n)`.

У практичній розробці комбіновані методи обробки 2-SAT застосовуються в статичних аналізаторах коду, розв'язувачах обмежень в мікроконтролерах та верифікаторах цифрових схем (Model Checking).

:::tabs
```c
/* C11 implementation: 2-SAT Satisfiability Checker via Implication Graph */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int var1; /* Positive for x_i, negative for -x_i */
    int var2;
} Clause2SAT;

typedef struct {
    uint32_t num_vars;
    uint32_t num_clauses;
    const Clause2SAT *clauses;
} Formula2SAT;

/* Maps literal to vertex index in range [0 .. 2*num_vars - 1] */
static inline uint32_t literal_to_vertex(int lit, uint32_t num_vars) {
    if (lit > 0) {
        return (uint32_t)(lit - 1);
    } else {
        return (uint32_t)(-lit - 1) + num_vars;
    }
}

/* Returns negated literal vertex index */
static inline uint32_t negated_literal_vertex(int lit, uint32_t num_vars) {
    return literal_to_vertex(-lit, num_vars);
}

/* Checks if implication edge (u -> v) exists dynamically without allocating adjacency matrix */
static bool has_implication_edge(const Formula2SAT *f, uint32_t u, uint32_t v) {
    for (uint32_t i = 0; i < f->num_clauses; ++i) {
        int a = f->clauses[i].var1;
        int b = f->clauses[i].var2;

        /* (a v b) is equivalent to (-a -> b) and (-b -> a) */
        uint32_t not_a = negated_literal_vertex(a, f->num_vars);
        uint32_t pos_b = literal_to_vertex(b, f->num_vars);
        uint32_t not_b = negated_literal_vertex(b, f->num_vars);
        uint32_t pos_a = literal_to_vertex(a, f->num_vars);

        if ((u == not_a && v == pos_b) || (u == not_b && v == pos_a)) {
            return true;
        }
    }
    return false;
}

/* Savitch-style reachability check over virtual implication graph */
static bool impl_can_reach(const Formula2SAT *f, uint32_t u, uint32_t v, uint32_t steps) {
    if (u == v) return true;
    if (steps == 1) return has_implication_edge(f, u, v);

    uint32_t total_nodes = 2 * f->num_vars;
    uint32_t half_steps = (steps + 1) / 2;

    for (uint32_t w = 0; w < total_nodes; ++w) {
        if (impl_can_reach(f, u, w, half_steps)) {
            if (impl_can_reach(f, w, v, steps - half_steps)) {
                return true;
            }
        }
    }
    return false;
}

/* Evaluates if 2-SAT formula is satisfiable in O(log^2 N) space */
bool is_2sat_satisfiable(const Formula2SAT *f) {
    uint32_t total_nodes = 2 * f->num_vars;

    for (uint32_t i = 1; i <= f->num_vars; ++i) {
        uint32_t pos_v = literal_to_vertex((int)i, f->num_vars);
        uint32_t neg_v = negated_literal_vertex((int)i, f->num_vars);

        /* Check if x_i -> -x_i and -x_i -> x_i both exist */
        if (impl_can_reach(f, pos_v, neg_v, total_nodes) &&
            impl_can_reach(f, neg_v, pos_v, total_nodes)) {
            return false; /* Unsatisfiable due to contradiction cycle */
        }
    }
    return true;
}

int main(void) {
    /* Formula: (x1 v x2) ^ (-x1 v x2) ^ (x1 v -x2) ^ (-x1 v -x2) -> Unsatisfiable */
    const Clause2SAT clauses[] = {
        {  1,  2 },
        { -1,  2 },
        {  1, -2 },
        { -1, -2 }
    };
    Formula2SAT f = {
        .num_vars = 2,
        .num_clauses = 4,
        .clauses = clauses
    };

    bool sat = is_2sat_satisfiable(&f);
    printf("2-SAT Formula is %s\n", sat ? "SATISFIABLE" : "UNSATISFIABLE");

    return 0;
}
```
```cpp
// C++20 implementation: Functional zero-alloc 2-SAT Evaluator
#include <iostream>
#include <span>
#include <array>
#include <cstdint>
#include <optional>

namespace space_complexity {

struct Literal {
    int32_t id; // Positive for x_i, negative for NOT x_i

    [[nodiscard]] constexpr Literal operator-() const noexcept {
        return Literal{-id};
    }
};

struct Clause2 {
    Literal first;
    Literal second;
};

class Formula2SATView {
public:
    constexpr Formula2SATView(uint32_t num_vars, std::span<const Clause2> clauses) noexcept
        : num_vars_(num_vars), clauses_(clauses) {}

    [[nodiscard]] constexpr uint32_t num_variables() const noexcept {
        return num_vars_;
    }

    [[nodiscard]] constexpr uint32_t total_nodes() const noexcept {
        return 2 * num_vars_;
    }

    [[nodiscard]] constexpr uint32_t literal_to_node(Literal lit) const noexcept {
        if (lit.id > 0) {
            return static_cast<uint32_t>(lit.id - 1);
        }
        return static_cast<uint32_t>(-lit.id - 1) + num_vars_;
    }

    [[nodiscard]] bool has_implication(uint32_t u, uint32_t v) const noexcept {
        for (const auto& clause : clauses_) {
            const uint32_t not_a = literal_to_node(-clause.first);
            const uint32_t pos_b = literal_to_node(clause.second);
            const uint32_t not_b = literal_to_node(-clause.second);
            const uint32_t pos_a = literal_to_node(clause.first);

            if ((u == not_a && v == pos_b) || (u == not_b && v == pos_a)) {
                return true;
            }
        }
        return false;
    }

private:
    uint32_t num_vars_;
    std::span<const Clause2> clauses_;
};

class Evaluator2SAT {
public:
    [[nodiscard]] static bool solve(const Formula2SATView& formula) noexcept {
        const uint32_t n_nodes = formula.total_nodes();

        for (uint32_t i = 1; i <= formula.num_variables(); ++i) {
            const Literal x{static_cast<int32_t>(i)};
            const uint32_t pos_node = formula.literal_to_node(x);
            const uint32_t neg_node = formula.literal_to_node(-x);

            if (can_reach(formula, pos_node, neg_node, n_nodes) &&
                can_reach(formula, neg_node, pos_node, n_nodes)) {
                return false;
            }
        }
        return true;
    }

private:
    static bool can_reach(const Formula2SATView& formula, uint32_t u, uint32_t v, uint32_t steps) noexcept {
        if (u == v) return true;
        if (steps == 1) return formula.has_implication(u, v);

        const uint32_t half = (steps + 1) / 2;
        const uint32_t total = formula.total_nodes();

        for (uint32_t w = 0; w < total; ++w) {
            if (can_reach(formula, u, w, half) && can_reach(formula, w, v, steps - half)) {
                return true;
            }
        }
        return false;
    }
};

} // namespace space_complexity

int main() {
    using namespace space_complexity;

    constexpr std::array<Clause2, 4> clauses = {{
        { Literal{1},  Literal{2} },
        { Literal{-1}, Literal{2} },
        { Literal{1},  Literal{-2} },
        { Literal{-1}, Literal{-2} }
    }};

    Formula2SATView formula(2, clauses);
    const bool is_satisfiable = Evaluator2SAT::solve(formula);

    std::cout << "2-SAT Evaluation Result: " 
              << (is_satisfiable ? "SATISFIABLE" : "UNSATISFIABLE") << "\n";

    return 0;
}
```
:::

---

## 3. Аналіз часово-просторового компромісу (Time-Space Tradeoff)

Представлені реалізації демонструють фундаментальний компроміс сучасного системного програмування:

1. **Нульове динамічне виділення пам'яті (Zero Dynamic Allocation):** Алгоритми оперують виключно фіксованими стек-кадрами `O(\log² n)` або `O(\log n)`. Динамічна пам'ять (`malloc`, `new`) повністю виключена. Це гарантує відсутність дефрагментації RAM та унеможливлює виклики `OOM (Out Of Memory)` в ядерному середовищі або на мікроконтролерах.
2. **Отримання дуг «за вимогою» (On-Demand Virtual Graph Construction):** Граф імплікацій не будується у пам'яті у вигляді матриці чи списку суміжності. Функція `has_implication_edge()` в C або `has_implication()` в C++ динамічно зчитує вхідний масив диз'юнктів при кожній перевірці. Це дозволяє аналізувати графи нескінченного або згенерованого за допомогою генераторів розміру.
3. **Порівняння C та C++ підходів:** У C-версії застосовано низькорівневе приведення типів та чисті масиви. У C++20 використовуються безпечні абстракції `std::span`, семантика `noexcept`, `constexpr` та новітній стандарт обробки помилок `std::expected`. Це показує, що строго ідіоматичний C++ дозволяє зберігати максимальну просторову ефективність без втрати строкатості типів.
4. **Експоненційний час за логарифмічний простір:** Оскільки рекурсія Савича розгалужується для кожної з `|V|` вершин, загальний час виконання становить `O(n^{\log_2 n})`. На практиці цей підхід застосовують тоді, коли обсяг оперативної пам'яті є критичним обмеженням першого порядку.
5. **Профіль використання кек-пам'яті L1/L2:** Постійний прохід по масиву диз'юнктів має високу локальність даних, оскільки вхідний масив читається послідовно. Це дозволяє кешу процесора працювати із максимальним коефіцієнтом влучання (Cache Hit Rate), компенсуючи частину повторних обчислень.
