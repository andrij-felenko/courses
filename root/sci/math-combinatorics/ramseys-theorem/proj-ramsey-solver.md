# ⚙️ Практична реалізація пошуку та перевірки графа Рамсея

Ця вставка містить практичну реалізацію алгоритмів аналізу розмальовок Рамсея: перевірку наявності монохроматичних клік заданого розміру у 2-розфарбованому повному графі `Kₙ` та рекурсивний алгоритм пошуку контрприкладів (розфарбувань без монохроматичних підграфів) з оптимізаційним відтинанням гілок пошукового дерева.

## 1. Структура даних та алгоритмічні засади

Обчислювальна складність точного аналізу графів Рамсея безпосередньо обумовлена вибуховим зростанням кількості ребер. У повній сітці з `n` вершин загальна кількість ребер задається біноміальним коефіцієнтом `n(n - 1) / 2`. При двокольоровому розфарбуванні кожне ребро приймає один з двох кольорів — умовно червоний (значення 1) або синій (значення 0). Отже, загальна кількість усіх можливих розфарбувань ребер графа `Kₙ` становить `2^(n(n-1)/2)`.

Для невеликих графів (`n ≤ 64`) найбільш ефективним математичним представленням колірної матриці є використання масиву 64-бітних цілочисельних бітових масок (`uint64_t`). У цій моделі `v`-й рядок матриці являє собою 64-бітне число, де `u`-й біт встановлено в 1, якщо ребро `(v, u)` має червоний колір, і в 0, якщо ребро є синім. Таке представлення забезпечує апаратну паралелізацію побітових операцій на рівні процесорних регістрів.

### Алгоритм перевірки монохроматичної кліки
Щоб перевірити, чи містить поточна розмальовка графа `Kₙ` монохроматичний червоний підграф `Kᵣ` або синій підграф `K⛛`, застосовується алгоритм рекурсивного пошуку з відтинанням кандидатів (англ. *clique-search with candidate reduction*):

1. **Ініціалізація множини кандидатів**: Стартова множина кандидатів містить усі `n` вершин графа.
2. **Вибір поточної вершини**: З множини кандидатів вибирається вершина `v` з найменшим індексом за допомогою інструкції пошуку молодшого встановленого біта (`ctz` — count trailing zeros).
3. **Звуження кандидатів**: Нова множина кандидатів формується як побітове «І» (AND) поточної множини кандидатів, маски сусідів вершини `v` відповідного кольору та маски вершин з індексами, більшими за `v`. Маска майбутніх вершин гарантує впорядкований перебір підмножин без повторних перевірок аналогічних комбінацій у різному порядку.
4. **Оптимізаційне відтинання гілок (Popcount Pruning)**: Перед здійсненням глибшого рекурсивного виклику обчислюється кількість підключених кандидатів за допомогою апаратної інструкції `popcount`. Якщо сума поточного розміру знайденої кліки та кількості залишкових кандидатів строго менша за цільовий розмір `target_size`, дана гілка рекурсивного дерева негайно відтинається як безперспективна.

```
Вхід: Кількість вершин n, параметри клік (r, s), колірна матриця C
 ├─► Для кожної підмножини S розміру r:
 │    └─► Якщо всі ребра в S червоні (1) ──► Знайдено червоний K_r!
 ├─► Для кожної підмножини S розміру s:
 │    └─► Якщо всі ребра в S сині (0)    ──► Знайдено синій K_s!
 └─► Якщо жодної монохроматичної кліки не знайдено:
      └─► Граф є контрприкладом для R(r, s) > n!
```

## 2. Реалізація аналізатора та пошукача Рамсея

Нижче наведено робочі реалізації мовами C та C++. Обидві версії вирішують дві базові задачі:
1. Перевірка довільної колірної матриці `Kₙ` на наявність червоного `Kᵣ` або синього `K⛛`.
2. Пошук розфарбування `Kₙ`, яке доводить, що `R(r, s) > n` (пошук контрприкладу).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_VERTICES 64

typedef struct {
    int num_vertices;
    uint64_t adj[MAX_VERTICES]; /* adj[i] бітова маска: j-й біт = 1 (червоне), 0 (синє) */
} ramsey_graph_t;

static void graph_init(ramsey_graph_t *g, int n) {
    g->num_vertices = n;
    for (int i = 0; i < n; i++) {
        g->adj[i] = 0;
    }
}

static void graph_set_edge(ramsey_graph_t *g, int u, int v, bool is_red) {
    if (is_red) {
        g->adj[u] |= (1ULL << v);
        g->adj[v] |= (1ULL << u);
    } else {
        g->adj[u] &= ~(1ULL << v);
        g->adj[v] &= ~(1ULL << u);
    }
}

/* Рекурсивна перевірка існування монохроматичної кліки target_size */
static bool check_clique_rec(const ramsey_graph_t *g, uint64_t candidates, int target_size, int current_size, bool is_red) {
    if (current_size == target_size) {
        return true;
    }

    while (candidates > 0) {
        /* Враховуємо кількість залишку для прискорення (pruning) */
        int popcount = __builtin_popcountll(candidates);
        if (current_size + popcount < target_size) {
            return false;
        }

        int v = __builtin_ctzll(candidates);
        candidates &= ~(1ULL << v);

        uint64_t neighbors = is_red ? g->adj[v] : ~(g->adj[v]);
        /* Виключаємо вершини зі старшими індексами для унікальності порядку */
        uint64_t mask_future = ~((1ULL << (v + 1)) - 1);
        uint64_t next_candidates = candidates & neighbors & mask_future;

        if (check_clique_rec(g, next_candidates, target_size, current_size + 1, is_red)) {
            return true;
        }
    }
    return false;
}

/* Визначення, чи містить граф червоний K_r чи синій K_s */
bool ramsey_has_monochromatic_clique(const ramsey_graph_t *g, int r, int s) {
    uint64_t all_vertices = (g->num_vertices == 64) ? ~0ULL : ((1ULL << g->num_vertices) - 1);

    /* Перевіряємо червоний K_r */
    if (check_clique_rec(g, all_vertices, r, 0, true)) {
        return true;
    }

    /* Перевіряємо синій K_s */
    if (check_clique_rec(g, all_vertices, s, 0, false)) {
        return true;
    }

    return false;
}

/* Пошук контрприкладу розфарбування методом рекурсивного пошуку з поверненням */
static bool search_counterexample_rec(ramsey_graph_t *g, int edge_idx, int total_edges, int edge_u[], int edge_v[], int r, int s) {
    if (edge_idx == total_edges) {
        return !ramsey_has_monochromatic_clique(g, r, s);
    }

    int u = edge_u[edge_idx];
    int v = edge_v[edge_idx];

    /* Спробувати червоне ребро */
    graph_set_edge(g, u, v, true);
    if (search_counterexample_rec(g, edge_idx + 1, total_edges, edge_u, edge_v, r, s)) {
        return true;
    }

    /* Спробувати синє ребро */
    graph_set_edge(g, u, v, false);
    if (search_counterexample_rec(g, edge_idx + 1, total_edges, edge_u, edge_v, r, s)) {
        return true;
    }

    return false;
}

bool ramsey_find_counterexample(ramsey_graph_t *out_graph, int n, int r, int s) {
    graph_init(out_graph, n);
    int total_edges = n * (n - 1) / 2;
    int *edge_u = (int *)malloc(total_edges * sizeof(int));
    int *edge_v = (int *)malloc(total_edges * sizeof(int));

    if (!edge_u || !edge_v) {
        free(edge_u);
        free(edge_v);
        return false;
    }

    int idx = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            edge_u[idx] = i;
            edge_v[idx] = j;
            idx++;
        }
    }

    bool found = search_counterexample_rec(out_graph, 0, total_edges, edge_u, edge_v, r, s);

    free(edge_u);
    free(edge_v);
    return found;
}

int main(void) {
    printf("=== Перевірка чисел Рамсея (C Implementation) ===\n");
    int r = 3, s = 3;

    for (int n = 3; n <= 6; n++) {
        ramsey_graph_t g;
        bool has_counterexample = ramsey_find_counterexample(&g, n, r, s);
        if (has_counterexample) {
            printf("n = %d: Знайдено контрприклад! R(%d, %d) > %d\n", n, r, s, n);
        } else {
            printf("n = %d: Не існує контрприкладу. Отже R(%d, %d) <= %d\n", n, r, s, n);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <bitset>
#include <optional>
#include <cstdint>
#include <numeric>
#include <array>
#include <bit>

namespace ramsey {

template <std::size_t N>
class graph_coloring {
public:
    static_assert(N <= 64, "Класова реалізація обмежена 64 вершинами для швидкодії бітових масок");

    graph_coloring() : num_vertices_(N) {
        adj_red_.fill(0);
    }

    explicit graph_coloring(std::size_t n) : num_vertices_(n) {
        adj_red_.fill(0);
    }

    [[nodiscard]] std::size_t size() const noexcept { return num_vertices_; }

    void set_edge(std::size_t u, std::size_t v, bool is_red) noexcept {
        if (is_red) {
            adj_red_[u] |= (1ULL << v);
            adj_red_[v] |= (1ULL << u);
        } else {
            adj_red_[u] &= ~(1ULL << v);
            adj_red_[v] &= ~(1ULL << u);
        }
    }

    [[nodiscard]] bool get_edge(std::size_t u, std::size_t v) const noexcept {
        return (adj_red_[u] & (1ULL << v)) != 0;
    }

    [[nodiscard]] std::uint64_t red_neighbors(std::size_t v) const noexcept {
        return adj_red_[v];
    }

    [[nodiscard]] std::uint64_t blue_neighbors(std::size_t v) const noexcept {
        uint64_t mask = (num_vertices_ == 64) ? ~0ULL : ((1ULL << num_vertices_) - 1);
        return (~adj_red_[v]) & mask & ~(1ULL << v);
    }

    [[nodiscard]] bool has_monochromatic_clique(std::size_t r, std::size_t s) const {
        uint64_t all_v = (num_vertices_ == 64) ? ~0ULL : ((1ULL << num_vertices_) - 1);
        return check_clique(all_v, r, 0, true) || check_clique(all_v, s, 0, false);
    }

private:
    std::size_t num_vertices_;
    std::array<std::uint64_t, N> adj_red_{};

    bool check_clique(std::uint64_t candidates, std::size_t target_size, std::size_t current_size, bool is_red) const {
        if (current_size == target_size) {
            return true;
        }

        while (candidates > 0) {
            int popcnt = std::popcount(candidates);
            if (current_size + static_cast<std::size_t>(popcnt) < target_size) {
                return false;
            }

            int v = std::countr_zero(candidates);
            candidates &= ~(1ULL << v);

            std::uint64_t neighbors = is_red ? red_neighbors(v) : blue_neighbors(v);
            std::uint64_t mask_future = ~((1ULL << (v + 1)) - 1);
            std::uint64_t next_candidates = candidates & neighbors & mask_future;

            if (check_clique(next_candidates, target_size, current_size + 1, is_red)) {
                return true;
            }
        }
        return false;
    }
};

template <std::size_t N>
class solver {
public:
    static std::optional<graph_coloring<N>> find_counterexample(std::size_t r, std::size_t s) {
        graph_coloring<N> g;
        std::vector<std::pair<std::size_t, std::size_t>> edges;
        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = i + 1; j < N; ++j) {
                edges.emplace_back(i, j);
            }
        }

        if (search(g, 0, edges, r, s)) {
            return g;
        }
        return std::nullopt;
    }

private:
    static bool search(graph_coloring<N>& g, std::size_t edge_idx,
                       const std::vector<std::pair<std::size_t, std::size_t>>& edges,
                       std::size_t r, std::size_t s) {
        if (edge_idx == edges.size()) {
            return !g.has_monochromatic_clique(r, s);
        }

        auto [u, v] = edges[edge_idx];

        // Спроба червоного ребра
        g.set_edge(u, v, true);
        if (search(g, edge_idx + 1, edges, r, s)) {
            return true;
        }

        // Спроба синього ребра
        g.set_edge(u, v, false);
        if (search(g, edge_idx + 1, edges, r, s)) {
            return true;
        }

        return false;
    }
};

} // namespace ramsey

int main() {
    std::cout << "=== Перевірка чисел Рамсея (C++20 Implementation) ===\n";
    constexpr std::size_t r = 3, s = 3;

    // Перевіряємо гранули від n = 3 до 6
    auto run_check = []<std::size_t N>() {
        auto result = ramsey::solver<N>::find_counterexample(r, s);
        if (result.has_value()) {
            std::cout << "n = " << N << ": Знайдено контрприклад! R(" << r << ", " << s << ") > " << N << "\n";
        } else {
            std::cout << "n = " << N << ": Не існує контрприкладу. Отже R(" << r << ", " << s << ") <= " << N << "\n";
        }
    };

    run_check.operator()<3>();
    run_check.operator()<4>();
    run_check.operator()<5>();
    run_check.operator()<6>();

    return 0;
}
```
:::

## 3. Детальний аналіз алгоритмічних оптимізацій та підводних каменів

Реалізація аналізу чисел Рамсея демонструє класичну проблему «прокляття розмірності» дискретного перебору. Розглянемо ключові інженерні та алгоритмічні аспекти побудованих розв'язувачів:

### Апаратне прискорення через бітові маски та інструкції SIMD
Представлення колірної матриці у вигляді 64-бітних цілих чисел дозволяє замінити традиційні вкладені цикли перевірки сусідства на одиничні інструкції процесора:
- **`__builtin_ctzll` / `std::countr_zero`**: Знаходить індекс першого встановленого біта у масці кандидатів за 1 такт процесора (використовуючи процесорну інструкцію `TZCNT` у x86-64).
- **`__builtin_popcountll` / `std::popcount`**: Обчислює кількість одиничних бітів за 1 такт (інструкція `POPCNT`). Це дозволяє виконувати миттєву оцінку верхньої межі залишку кандидатів перед рекурсивним зануренням.

### Метод відтинання за симетрією (Symmetry Pruning)
У наведеному реалізованому рекурсивному алгоритмі перевірки клік використовується маска `mask_future = ~((1ULL << (v + 1)) - 1)`. Вона гарантує, що при розгляді підмножин вершин нові вершини додаються строго у зростаючому порядку їхніх індексів `v₁ < v₂ < ... < vᵣ`. Це позбавляє перевіряючий алгоритм від повторного обходу тих самих `k!` перестановок тієї самої підмножини вершин.

### Канонізація ізоморфізмів графів (Graph Isomorphism Pruning)
Наївний перебір розфарбувань перевіряє багато графів, які є абсолютно ізоморфними один одному (відрізняються лише перенумерацією вершин). Для практичного обчислення великих графів (`n ≥ 10`) повний перебір зазвичай замінюють на:
1. Генерацію лише невзаємоізоморфних 2-розфарбованих графів за допомогою канонічного підрахунку автоморфізмів (бібліотека `nauty` або `Bliss`).
2. Кодування проблеми у вигляді SAT-формули (Boolean Satisfiability Problem) у кон'юнктивній нормальній формі (CNF) та її розв'язання за допомогою сучасного CDCL SAT-соловера.

### SAT-кодування проблеми Рамсея
Для перетворення задачі Рамсея у булеву формулу створюється `M = n(n - 1) / 2` логічних змінних `x_{u, v}`, де `x_{u, v} = 1` відповідає червоному кольору ребра `(u, v)`, а `x_{u, v} = 0` — синьому.

Для кожної підмножини з `r` вершин додається диз'юнкт (диз'юнкція заперечень ребер):

```
(¬x_{v₁, v₂} ∨ ¬x_{v₁, v₃} ∨ ... ∨ ¬x_{v_{r-1}, vᵣ})
```

Цей диз'юнкт забороняє всім ребрам підмножини бути одночасно червоними (запобігає утворенню червоного `Kᵣ`).

Аналогічно, для кожної підмножини з `s` вершин додається диз'юнкт з прямими змінними:

```
(x_{u₁, u₂} ∨ x_{u₁, u₃} ∨ ... ∨ x_{u_{s-1}, uₛ})
```

Цей диз'юнкт забороняє всім ребрам бути одночасно синіми (запобігає утворенню синього `K⛛`). Якщо SAT-соловер повертає статус `UNSAT` (невідповідна формула), це слугує математичним доказом того, що `R(r, s) ≤ n`. Якщо повернуто статус `SAT`, згенерована інтерпретація змінних дає конкретне розфарбування-контрприклад для `R(r, s) > n`.

### Паралелізація обчислень (OpenMP та Multi-threading)
При масштабуванні алгоритму пошуку розфарбувань Рамсея на велику кількість вершин рекурсивне дерево перебору може бути паралелізовано між ядрами процесора. Для цього фіксуються перші `k` ребер графа (утворюючи `2ᵏ` незалежних піддерев), після чого кожна гілка передається окремому потоку за допомогою OpenMP або `std::async`. Завдяки відсутності спільного стану між гілками прискорення є майже лінійним від кількості доступних ядер процесора.
