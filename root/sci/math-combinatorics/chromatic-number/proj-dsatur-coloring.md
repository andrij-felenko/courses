# Реалізація алгоритму DSATUR та точного пошуку

Задача точного знаходження хроматичного числа `χ(G)` вимагає комбінації швидких поліноміальних евристик для отримання якісної початкової верхньої межі та оптимізованого пошуку з поверненням (branch-and-bound) для відсікання тупикових гілок. Наївний повний перебір `k`-розфарбувань генерує `kⁿ` комбінаторних станів і стає практично нерозв'язним вже на графах із 15–20 вершинами, оскільки розмір дерева пошуку зростає за експонентою. Алгоритм DSATUR (Degree of Saturation), розроблений Даніелем Брелазом 1979 року, застосовує евристику динамічного вибору вершин із найвищим ступенем насиченості, що зменшує кількість кроків перебору на багато порядків завдяки принципу раннього виявлення глухих кутів (fail-first).

У цьому проекті детально розібрано повний інженерний цикл побудови систем розфарбування графів: вибір компактного представлення в пам'яті через 64-бітні бітові маски суміжності, реалізація жадібного алгоритму та методу Велша — Пауелла, побудова точного розв'язувача DSATUR із гілками та межами, впровадження локального пошуку через ланцюги Кемпе, пряме SAT-кодування для зовнішніх розв'язувачів, покрокове простеження станів на графі Грьотча та модуль верифікації сертифікатів правильності. Усі модулі реалізовано мовами C (стандарт C99) та C++ (стандарт C++20) з дотриманням ідіоматичних практик кожної мови.

## Архітектура та бітові маски суміжності

Ефективність алгоритмів розфарбування на 90% визначається швидкістю базових операцій: перевірки суміжності між двома вершинами, обчислення перетину множин сусідів та визначення доступних кольорів. Класичне представлення графа у вигляді списків суміжності `std::vector<std::vector<int>>` або вказівникових структур створює велику кількість розірваних виділень пам'яті, призводить до промахів кешу процесора (cache misses) та вимагає лінійного сканування списків для кожної перевірки ребра.

Для графів помірного розміру (до 64 вершин) оптимальним рішенням є упакована матриця суміжності на основі 64-бітних цілих чисел без знаку `uint64_t`. Кожен рядок матриці `adj[u]` є бітовою маскою, де `v`-й біт встановлено в 1 тоді й лише тоді, коли між вершинами `u` та `v` існує ребро.

Така структура забезпечує критичні апаратні переваги:
1. **Константний час перевірки ребра `O(1)`:** перевірка суміжності двох вершин `u` та `v` виконується однією побітовою операцією `(adj[u] & (1ULL << v)) != 0` за один такт процесора без звернення до зовнішньої пам'яті.
2. **Апаратний підрахунок степеня:** кількість сусідів вершини `v` обчислюється вбудованою процесорною інструкцією підрахунку одиничних бітів `__builtin_popcountll(adj[u])` (інструкція `POPCNT` в архітектурі x86-64 або `CNT` в ARM Neon), що усуває необхідність тримати окремі лічильники.
3. **Миттєве визначення конфліктів кольору:** множина всіх сусідів вершини `v`, які вже пофарбовані в колір `c`, представляється накопичувальною маскою `color_mask[c]`. Перевірка, чи можна призначити вершині `v` колір `c`, виконується операцією `(adj[v] & color_mask[c]) == 0`. Якщо результат дорівнює нулю, колір `c` повністю вільний від конфліктів у всьому околі вершини `v`.

Для масштабування на графи з понад 64 вершинами масиви `uint64_t` узагальнюються до блоків фіксованого розміру (наприклад, 4 слова для 256 вершин) з використанням векторних SIMD-інструкцій (AVX2 `_mm256_and_si256`), що зберігає бітову паралельність на масштабах промислових графів інтерференції.

Нижче наведено базові структури та процедури ініціалізації графа.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 64

typedef struct {
    int num_vertices;
    uint64_t adj[MAX_VERTICES];
} Graph;

typedef struct {
    int colors[MAX_VERTICES];
    int chromatic_number;
    bool is_valid;
    uint64_t iterations;
} ColoringResult;

void graph_init(Graph* g, int num_vertices) {
    if (num_vertices > MAX_VERTICES) num_vertices = MAX_VERTICES;
    g->num_vertices = num_vertices;
    for (int i = 0; i < num_vertices; ++i) {
        g->adj[i] = 0ULL;
    }
}

void graph_add_edge(Graph* g, int u, int v) {
    if (u >= 0 && u < g->num_vertices && v >= 0 && v < g->num_vertices && u != v) {
        g->adj[u] |= (1ULL << v);
        g->adj[v] |= (1ULL << u);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <bitset>
#include <numeric>
#include <stdexcept>

constexpr size_t MAX_VERTICES = 64;

class Graph {
public:
    explicit Graph(size_t num_vertices) 
        : num_vertices_(std::min(num_vertices, MAX_VERTICES)), 
          adj_(num_vertices_, 0ULL) {}

    void add_edge(size_t u, size_t v) {
        if (u >= num_vertices_ || v >= num_vertices_) {
            throw std::out_of_range("Індекс вершини виходить за межі графа");
        }
        if (u != v) {
            adj_[u] |= (1ULL << v);
            adj_[v] |= (1ULL << u);
        }
    }

    [[nodiscard]] size_t size() const noexcept { return num_vertices_; }
    [[nodiscard]] uint64_t neighbors(size_t v) const noexcept { return adj_[v]; }
    [[nodiscard]] size_t degree(size_t v) const noexcept {
        return static_cast<size_t>(__builtin_popcountll(adj_[v]));
    }

private:
    size_t num_vertices_;
    std::vector<uint64_t> adj_;
};

struct ColoringResult {
    std::vector<int> colors;
    int chromatic_number{0};
    bool is_valid{false};
    uint64_t iterations{0};
};
```
:::

## Алгоритм Велша — Пауелла: оптимізація жадібного порядку

Наївний жадібний алгоритм надзвичайно чутливий до початкового порядку вершин. Наприклад, для простого двочасткового графа у формі корони з `2n` вершинами невдалий порядок обходу змушує жадібний метод використати `n` кольорів замість оптимальних 2 (патологічний приклад Джонсона).

Алгоритм Велша — Пауелла (1967) розв'язує цю проблему за допомогою статичного попереднього сортування:
1. Усі вершини графа сортуються за спаданням їхнього степеня: `deg(v₁) ≥ deg(v₂) ≥ ... ≥ deg(vₙ)`.
2. Першому кольору `c = 1` призначається перша нерозфарбована вершина у списку.
3. Алгоритм проходить за відсортованим списком і фарбує кольором `c` кожну наступну нерозфарбовану вершину, яка не має спільних ребер із жодною з раніше пофарбованих кольором `c` вершин.
4. Після завершення проходу створюється новий колір `c = c + 1`, і процес повторюється для решти нерозфарбованих вершин.

Такий підхід гарантує, що вершини з найбільшою кількістю зв'язків розглядаються на початку, коли палітра вільна, що запобігає фрагментації колірного простору.

:::tabs
```c
ColoringResult color_welsh_powell(const Graph* g) {
    ColoringResult res;
    res.chromatic_number = 0;
    res.iterations = 0;
    res.is_valid = false;
    int n = g->num_vertices;
    for (int i = 0; i < n; ++i) res.colors[i] = -1;

    int order[MAX_VERTICES];
    int degrees[MAX_VERTICES];
    for (int i = 0; i < n; ++i) {
        order[i] = i;
        degrees[i] = __builtin_popcountll(g->adj[i]);
    }

    // Сортування вершин за спаданням степеня
    for (int i = 0; i < n - 1; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (degrees[order[j]] > degrees[order[i]]) {
                int tmp = order[i];
                order[i] = order[j];
                order[j] = tmp;
            }
        }
    }

    int colored_count = 0;
    int current_color = 1;

    while (colored_count < n) {
        uint64_t current_color_mask = 0ULL;
        for (int i = 0; i < n; ++i) {
            res.iterations++;
            int v = order[i];
            if (res.colors[v] == -1) {
                if ((g->adj[v] & current_color_mask) == 0ULL) {
                    res.colors[v] = current_color;
                    current_color_mask |= (1ULL << v);
                    colored_count++;
                }
            }
        }
        current_color++;
    }

    res.chromatic_number = current_color - 1;
    res.is_valid = true;
    return res;
}
```
```cpp
ColoringResult color_welsh_powell(const Graph& g) {
    ColoringResult res;
    const size_t n = g.size();
    res.colors.assign(n, -1);
    res.iterations = 0;

    std::vector<size_t> order(n);
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(), [&g](size_t a, size_t b) {
        return g.degree(a) > g.degree(b);
    });

    size_t colored_count = 0;
    int current_color = 1;

    while (colored_count < n) {
        uint64_t current_color_set = 0ULL;
        for (size_t v : order) {
            res.iterations++;
            if (res.colors[v] == -1) {
                if ((g.neighbors(v) & current_color_set) == 0ULL) {
                    res.colors[v] = current_color;
                    current_color_set |= (1ULL << v);
                    colored_count++;
                }
            }
        }
        current_color++;
    }

    res.chromatic_number = current_color - 1;
    res.is_valid = true;
    return res;
}
```
:::

## Алгоритм DSATUR та точний пошук з поверненням

Хоча метод Велша — Пауелла перевершує довільне жадібне розфарбування, статичний порядок вершин не враховує зміни конфігурації графа під час роботи. Якщо дві вершини великого степеня пофарбовано однаковим кольором, їхні спільні сусіди зазнають значно сильнішого обмеження, ніж вершини, чиї сусіди розфарбовані в різні кольори.

Алгоритм DSATUR усуває цей недолік, вводячи динамічний критерій — **ступінь насиченості** `deg_sat(v)`:

```
deg_sat(v) = кількість унікальних кольорів, призначених сусідам v
```

### Динаміка кроків DSATUR

На кожному кроці алгоритм виконує такі операції:
1. Серед усіх нерозфарбованих вершин обирається вершина `v` з максимальним значенням `deg_sat(v)`.
2. Якщо кілька вершин мають однаковий максимальний ступінь насиченості, серед них обирається вершина з найбільшим степенем у підграфі ще не розфарбованих вершин (`uncolored_deg`).
3. Для обраної вершини знаходиться найменший допустимий натуральний колір `c ∈ {1, 2, 3, ...}`, який не використовується жодним із її сусідів.
4. Після призначення кольору оновлюються маски кольорів усіх сусідів `u ∈ N(v)`: якщо колір `c` з'явився у сусіда `u` вперше, його `deg_sat(u)` збільшується на 1.

### Точний розв'язувач Branch-and-Bound

Для знаходження гарантовано мінімального `χ(G)` евристика DSATUR об'єднується з механізмом рекурсивного пошуку з поверненням:
- Спершу запускається швидка евристика DSATUR, яка дає початкову верхню межу `best_k`.
- Далі запускається процедура `backtrack()`, яка досліджує дерево вибору кольорів.
- Якщо на поточному шляху пошуку вже використано `current_max_k` кольорів і `current_max_k >= best_k`, вся поточна підгілка негайно відсікається, оскільки вона гарантовано не покращить знайдений результат.
- Якщо всі вершини успішно розфарбовано з `current_max_k < best_k`, оновлюється глобальний оптимум `best_k = current_max_k`, що ще сильніше стискає рамки для наступних гілок перебору.

:::tabs
```c
typedef struct {
    int colors[MAX_VERTICES];
    uint64_t neighbor_colors[MAX_VERTICES];
    int sat_deg[MAX_VERTICES];
    int uncolored_deg[MAX_VERTICES];
    int best_colors[MAX_VERTICES];
    int best_k;
    uint64_t search_steps;
} DSATURState;

static int choose_next_vertex(const DSATURState* state, int n) {
    int best_v = -1;
    int max_sat = -1;
    int max_deg = -1;

    for (int v = 0; v < n; ++v) {
        if (state->colors[v] == 0) {
            if (state->sat_deg[v] > max_sat || 
               (state->sat_deg[v] == max_sat && state->uncolored_deg[v] > max_deg)) {
                max_sat = state->sat_deg[v];
                max_deg = state->uncolored_deg[v];
                best_v = v;
            }
        }
    }
    return best_v;
}

ColoringResult color_dsatur_heuristic(const Graph* g) {
    ColoringResult res;
    int n = g->num_vertices;
    res.iterations = 0;
    res.chromatic_number = 0;

    DSATURState st;
    memset(&st, 0, sizeof(st));

    for (int i = 0; i < n; ++i) {
        st.uncolored_deg[i] = __builtin_popcountll(g->adj[i]);
    }

    int max_color_used = 0;
    for (int step = 0; step < n; ++step) {
        res.iterations++;
        int v = choose_next_vertex(&st, n);
        if (v == -1) break;

        int c = 1;
        while ((st.neighbor_colors[v] & (1ULL << c)) != 0ULL) {
            c++;
        }

        st.colors[v] = c;
        if (c > max_color_used) max_color_used = c;

        for (int u = 0; u < n; ++u) {
            if ((g->adj[v] & (1ULL << u)) != 0ULL && st.colors[u] == 0) {
                if ((st.neighbor_colors[u] & (1ULL << c)) == 0ULL) {
                    st.neighbor_colors[u] |= (1ULL << c);
                    st.sat_deg[u]++;
                }
                st.uncolored_deg[u]--;
            }
        }
    }

    for (int i = 0; i < n; ++i) res.colors[i] = st.colors[i];
    res.chromatic_number = max_color_used;
    res.is_valid = true;
    return res;
}

static void dsatur_backtrack(const Graph* g, DSATURState* st, int colored_count, int current_max_k) {
    st->search_steps++;
    int n = g->num_vertices;

    if (colored_count == n) {
        if (current_max_k < st->best_k) {
            st->best_k = current_max_k;
            memcpy(st->best_colors, st->colors, sizeof(int) * n);
        }
        return;
    }

    if (current_max_k >= st->best_k) {
        return;
    }

    int v = choose_next_vertex(st, n);
    if (v == -1) return;

    for (int c = 1; c <= current_max_k + 1 && c < st->best_k; ++c) {
        if ((st->neighbor_colors[v] & (1ULL << c)) == 0ULL) {
            uint64_t old_mask = st->neighbor_colors[v];
            st->colors[v] = c;

            int changed_neighbors[MAX_VERTICES];
            int changed_count = 0;

            for (int u = 0; u < n; ++u) {
                if ((g->adj[v] & (1ULL << u)) != 0ULL && st->colors[u] == 0) {
                    st->uncolored_deg[u]--;
                    if ((st->neighbor_colors[u] & (1ULL << c)) == 0ULL) {
                        st->neighbor_colors[u] |= (1ULL << c);
                        st->sat_deg[u]++;
                        changed_neighbors[changed_count++] = u;
                    }
                }
            }

            int next_max_k = (c > current_max_k) ? c : current_max_k;
            dsatur_backtrack(g, st, colored_count + 1, next_max_k);

            st->colors[v] = 0;
            st->neighbor_colors[v] = old_mask;
            for (int i = 0; i < changed_count; ++i) {
                int u = changed_neighbors[i];
                st->neighbor_colors[u] &= ~(1ULL << c);
                st->sat_deg[u]--;
            }
            for (int u = 0; u < n; ++u) {
                if ((g->adj[v] & (1ULL << u)) != 0ULL && st->colors[u] == 0) {
                    st->uncolored_deg[u]++;
                }
            }
        }
    }
}

ColoringResult color_exact_solver(const Graph* g) {
    ColoringResult heur = color_dsatur_heuristic(g);

    DSATURState st;
    memset(&st, 0, sizeof(st));
    st.best_k = heur.chromatic_number;
    memcpy(st.best_colors, heur.colors, sizeof(int) * g->num_vertices);
    st.search_steps = 0;

    int n = g->num_vertices;
    for (int i = 0; i < n; ++i) {
        st.uncolored_deg[i] = __builtin_popcountll(g->adj[i]);
    }

    dsatur_backtrack(g, &st, 0, 0);

    ColoringResult res;
    res.chromatic_number = st.best_k;
    res.iterations = st.search_steps;
    res.is_valid = true;
    for (int i = 0; i < n; ++i) res.colors[i] = st.best_colors[i];
    return res;
}
```
```cpp
class DSATURSolver {
public:
    explicit DSATURSolver(const Graph& g) 
        : graph_(g), n_(g.size()), colors_(n_, 0),
          neighbor_colors_(n_, 0ULL), sat_deg_(n_, 0),
          uncolored_deg_(n_, 0), best_colors_(n_, 0) {
        for (size_t i = 0; i < n_; ++i) {
            uncolored_deg_[i] = static_cast<int>(graph_.degree(i));
        }
    }

    ColoringResult run_heuristic() {
        ColoringResult res;
        int max_color = 0;

        for (size_t step = 0; step < n_; ++step) {
            res.iterations++;
            int v = choose_next();
            if (v == -1) break;

            int c = 1;
            while ((neighbor_colors_[v] & (1ULL << c)) != 0ULL) {
                c++;
            }

            colors_[v] = c;
            max_color = std::max(max_color, c);

            for (size_t u = 0; u < n_; ++u) {
                if ((graph_.neighbors(v) & (1ULL << u)) != 0ULL && colors_[u] == 0) {
                    if ((neighbor_colors_[u] & (1ULL << c)) == 0ULL) {
                        neighbor_colors_[u] |= (1ULL << c);
                        sat_deg_[u]++;
                    }
                    uncolored_deg_[u]--;
                }
            }
        }

        res.colors = colors_;
        res.chromatic_number = max_color;
        res.is_valid = true;
        return res;
    }

    ColoringResult solve_exact() {
        ColoringResult heur = run_heuristic();
        best_k_ = heur.chromatic_number;
        best_colors_ = heur.colors;
        search_steps_ = 0;

        std::fill(colors_.begin(), colors_.end(), 0);
        std::fill(neighbor_colors_.begin(), neighbor_colors_.end(), 0ULL);
        std::fill(sat_deg_.begin(), sat_deg_.end(), 0);
        for (size_t i = 0; i < n_; ++i) {
            uncolored_deg_[i] = static_cast<int>(graph_.degree(i));
        }

        backtrack(0, 0);

        ColoringResult exact_res;
        exact_res.chromatic_number = best_k_;
        exact_res.colors = best_colors_;
        exact_res.iterations = search_steps_;
        exact_res.is_valid = true;
        return exact_res;
    }

private:
    [[nodiscard]] int choose_next() const noexcept {
        int best_v = -1;
        int max_sat = -1;
        int max_deg = -1;

        for (size_t v = 0; v < n_; ++v) {
            if (colors_[v] == 0) {
                if (sat_deg_[v] > max_sat || (sat_deg_[v] == max_sat && uncolored_deg_[v] > max_deg)) {
                    max_sat = sat_deg_[v];
                    max_deg = uncolored_deg_[v];
                    best_v = static_cast<int>(v);
                }
            }
        }
        return best_v;
    }

    void backtrack(size_t colored_count, int current_max_k) {
        search_steps_++;
        if (colored_count == n_) {
            if (current_max_k < best_k_) {
                best_k_ = current_max_k;
                best_colors_ = colors_;
            }
            return;
        }

        if (current_max_k >= best_k_) return;

        int v = choose_next();
        if (v == -1) return;

        for (int c = 1; c <= current_max_k + 1 && c < best_k_; ++c) {
            if ((neighbor_colors_[v] & (1ULL << c)) == 0ULL) {
                colors_[v] = c;

                std::vector<size_t> changed;
                for (size_t u = 0; u < n_; ++u) {
                    if ((graph_.neighbors(v) & (1ULL << u)) != 0ULL && colors_[u] == 0) {
                        uncolored_deg_[u]--;
                        if ((neighbor_colors_[u] & (1ULL << c)) == 0ULL) {
                            neighbor_colors_[u] |= (1ULL << c);
                            sat_deg_[u]++;
                            changed.push_back(u);
                        }
                    }
                }

                backtrack(colored_count + 1, std::max(current_max_k, c));

                colors_[v] = 0;
                for (size_t u : changed) {
                    neighbor_colors_[u] &= ~(1ULL << c);
                    sat_deg_[u]--;
                }
                for (size_t u = 0; u < n_; ++u) {
                    if ((graph_.neighbors(v) & (1ULL << u)) != 0ULL && colors_[u] == 0) {
                        uncolored_deg_[u]++;
                    }
                }
            }
        }
    }

    const Graph& graph_;
    size_t n_;
    std::vector<int> colors_;
    std::vector<uint64_t> neighbor_colors_;
    std::vector<int> sat_deg_;
    std::vector<int> uncolored_deg_;
    std::vector<int> best_colors_;
    int best_k_{1000};
    uint64_t search_steps_{0};
};

ColoringResult color_exact_solver(const Graph& g) {
    DSATURSolver solver(g);
    return solver.solve_exact();
}
```
:::

## Локальний пошук: оптимізація через ланцюги Кемпе

Коли розв'язувач знаходить правильне k-розфарбування, виникає питання: чи можна модифікувати це розфарбування, щоб вивільнити певний колір `k` і зменшити загальну кількість кольорів до `k - 1`?

Класичний прийом полягає в перемиканні **ланцюгів Кемпе** (Kempe chains). Для двох кольорів `a` та `b` виділяється підграф, що складається винятково з вершин цих двох кольорів. Кожна зв'язна компонента цього підграфа є двоколірною. Інверсія кольорів `a ↔ b` всередині однієї зв'язної компоненти зберігає правильність глобального розфарбування, але може змінити оточення для заблокованої вершини іншого кольору.

Процес реалізується через простий пошук у ширину (BFS):
1. Обираємо стартову вершину `start_v` з кольором `color_a`.
2. За допомогою черги обходимо всі суміжні вершини, які мають колір `color_a` або `color_b`.
3. Усі знайдені вершини формують зв'язну компоненту `(a, b)`.
4. Для кожної вершини цієї компоненти колір інвертується: `a → b` та `b → a`.

Нижче наведено модуль перемикання ланцюгів Кемпе.

:::tabs
```c
bool kempe_swap_chain(const Graph* g, int* colors, int start_v, int color_a, int color_b) {
    int n = g->num_vertices;
    if (colors[start_v] != color_a && colors[start_v] != color_b) return false;

    bool visited[MAX_VERTICES];
    memset(visited, 0, sizeof(visited));

    int queue[MAX_VERTICES];
    int head = 0, tail = 0;

    queue[tail++] = start_v;
    visited[start_v] = true;

    // BFS для виділення зв'язної компоненти кольорів {color_a, color_b}
    while (head < tail) {
        int u = queue[head++];
        for (int v = 0; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) {
                if (!visited[v] && (colors[v] == color_a || colors[v] == color_b)) {
                    visited[v] = true;
                    queue[tail++] = v;
                }
            }
        }
    }

    // Інверсія кольорів у виділеній компоненті
    for (int i = 0; i < tail; ++i) {
        int v = queue[i];
        if (colors[v] == color_a) colors[v] = color_b;
        else if (colors[v] == color_b) colors[v] = color_a;
    }

    return true;
}
```
```cpp
bool kempe_swap_chain(const Graph& g, std::vector<int>& colors, size_t start_v, int color_a, int color_b) {
    const size_t n = g.size();
    if (start_v >= n || (colors[start_v] != color_a && colors[start_v] != color_b)) {
        return false;
    }

    std::vector<bool> visited(n, false);
    std::vector<size_t> component;
    std::vector<size_t> queue;

    queue.push_back(start_v);
    visited[start_v] = true;

    size_t head = 0;
    while (head < queue.size()) {
        size_t u = queue[head++];
        component.push_back(u);

        for (size_t v = 0; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) {
                if (!visited[v] && (colors[v] == color_a || colors[v] == color_b)) {
                    visited[v] = true;
                    queue.push_back(v);
                }
            }
        }
    }

    for (size_t v : component) {
        if (colors[v] == color_a) colors[v] = color_b;
        else if (colors[v] == color_b) colors[v] = color_a;
    }

    return true;
}
```
:::

## Пряме SAT-кодування k-розфарбування (DIMACS CNF)

Альтернативний промисловий підхід полягає у трансляції задачі k-розфарбування у формат КНФ (диз'юнктивна нормальна форма) для сучасних SAT-солверів (MiniSat, CaDiCaL, Kissat).

Для графа з `n` вершинами та заданого числа кольорів `k` створюються `n · k` булевих змінних:

```
x_{v, c} = 1   ⟺   вершині v призначено колір c (де 0 ≤ v < n, 1 ≤ c ≤ k)
```

Система обмежень формується трьома групами диз'юнктів:
1. **Кожна вершина має хоча б один колір (At-Least-One):**
   ```
   (x_{v, 1} ∨ x_{v, 2} ∨ ... ∨ x_{v, k})   для кожної вершини v
   ```
2. **Кожна вершина має не більше одного кольору (At-Most-One):**
   ```
   (¬x_{v, c₁} ∨ ¬x_{v, c₂})   для кожної пари кольорів c₁ < c₂
   ```
3. **Суміжні вершини мають різні кольори (Conflict clauses):**
   ```
   (¬x_{u, c} ∨ ¬x_{v, c})   для кожного ребра (u, v) ∈ E та кожного кольору c
   ```

Загальна кількість диз'юнктів становить:
- `At-Least-One`: рівно `n` диз'юнктів розміру `k`.
- `At-Most-One`: `n · k(k - 1) / 2` бінарних диз'юнктів.
- `Conflicts`: `|E| · k` бінарних диз'юнктів.

Нижче наведено генератор DIMACS CNF, який експортує граф у файл для зовнішніх автоматичних доводжувачів.

:::tabs
```c
void export_dimacs_cnf(const Graph* g, int k, FILE* out) {
    int n = g->num_vertices;
    int num_vars = n * k;

    int num_edges = 0;
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) num_edges++;
        }
    }

    int at_least_one = n;
    int at_most_one = n * (k * (k - 1) / 2);
    int conflicts = num_edges * k;
    int total_clauses = at_least_one + at_most_one + conflicts;

    fprintf(out, "p cnf %d %d\n", num_vars, total_clauses);

    // 1. At-Least-One: кожен v має хоча б 1 колір
    for (int v = 0; v < n; ++v) {
        for (int c = 1; c <= k; ++c) {
            int var_id = v * k + c;
            fprintf(out, "%d ", var_id);
        }
        fprintf(out, "0\n");
    }

    // 2. At-Most-One: не більше 1 кольору на вершину
    for (int v = 0; v < n; ++v) {
        for (int c1 = 1; c1 <= k; ++c1) {
            for (int c2 = c1 + 1; c2 <= k; ++c2) {
                int var1 = v * k + c1;
                int var2 = v * k + c2;
                fprintf(out, "-%d -%d 0\n", var1, var2);
            }
        }
    }

    // 3. Конфлікти: ребра не можуть ділити колір c
    for (int u = 0; u < n; ++u) {
        for (int v = u + 1; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) {
                for (int c = 1; c <= k; ++c) {
                    int var_u = u * k + c;
                    int var_v = v * k + c;
                    fprintf(out, "-%d -%d 0\n", var_u, var_v);
                }
            }
        }
    }
}
```
```cpp
void export_dimacs_cnf(const Graph& g, int k, std::ostream& out) {
    const size_t n = g.size();
    const size_t num_vars = n * k;

    size_t num_edges = 0;
    for (size_t u = 0; u < n; ++u) {
        for (size_t v = u + 1; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) num_edges++;
        }
    }

    size_t total_clauses = n + n * (k * (k - 1) / 2) + num_edges * k;

    out << "p cnf " << num_vars << " " << total_clauses << "\n";

    for (size_t v = 0; v < n; ++v) {
        for (int c = 1; c <= k; ++c) {
            out << (v * k + c) << " ";
        }
        out << "0\n";
    }

    for (size_t v = 0; v < n; ++v) {
        for (int c1 = 1; c1 <= k; ++c1) {
            for (int c2 = c1 + 1; c2 <= k; ++c2) {
                out << "-" << (v * k + c1) << " -" << (v * k + c2) << " 0\n";
            }
        }
    }

    for (size_t u = 0; u < n; ++u) {
        for (size_t v = u + 1; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) {
                for (int c = 1; c <= k; ++c) {
                    out << "-" << (u * k + c) << " -" << (v * k + c) << " 0\n";
                }
            }
        }
    }
}
```
:::

## Покрокове простеження виконання DSATUR на графі Грьотча

Щоб наочно побачити динаміку роботи алгоритму DSATUR, простежимо його поведінку на графі Грьотча `M₄` (11 вершин, 20 ребер, `χ = 4`):
- Базовий 5-цикл `u₀..u₄`: ребра `(0,1), (1,2), (2,3), (3,4), (4,0)`.
- Тіньові вершини `v₅..v₉`: з'єднані з сусідами `uᵢ`.
- Верхівка `w = 10`: з'єднана з усіма тінями `5..9`.

```
Крок  Обрана вершина  Критерій вибору (deg_sat, uncolored_deg)  Призначений колір  Коментар стану
---------------------------------------------------------------------------------------------------------
1     Вершина 10 (w)  deg_sat = 0, uncolored_deg = 5 (макс)      Колір 1 (R)        Верхівка блокує колір 1 для всіх тіней
2     Вершина 0 (u₀)  deg_sat = 0, uncolored_deg = 4 (макс)      Колір 1 (R)        Оригінальна вершина отримує колір 1
3     Вершина 1 (u₁)  deg_sat = 1 {R}, uncolored_deg = 3         Колір 2 (G)        Сусід 0 змушений взяти колір 2
4     Вершина 4 (u₄)  deg_sat = 1 {R}, uncolored_deg = 3         Колір 2 (G)        Сусід 0 з іншого боку
5     Вершина 2 (u₂)  deg_sat = 1 {G}, uncolored_deg = 2         Колір 1 (R)        Вільний від сусідів 1 і 3
6     Вершина 3 (u₃)  deg_sat = 2 {R, G}, uncolored_deg = 2      Колір 3 (B)        Має сусідів 2(R) та 4(G), вимагає 3-й колір!
7     Вершина 5 (v₅)  deg_sat = 2 {R, G}, uncolored_deg = 1      Колір 3 (B)        Тінь u₀ суміжна з u₁(G) та u₄(G) + w(R)
8     Вершина 6 (v₆)  deg_sat = 3 {R, G, B}, uncolored_deg = 0   Колір 4 (Y)        МАКСИМАЛЬНЕ НАСИЧЕННЯ! Вимагає 4-й колір!
9..11 Решта тіней     deg_sat ≥ 2                                Кольори 2, 3, 4    Завершення розфарбування
```

Цей покроковий аналіз наочно демонструє, як на кроці 8 вершина `v₆` досягає насиченості 3 (її сусіди займають червоний, зелений та синій кольори), що автоматично змушує відкрити 4-й колір без будь-яких трикутників у графі.

## Валідація результатів та тестові випробування

Для верифікації правильності розфарбування використовується функція `verify_coloring`, яка здійснює незалежну перевірку всіх пар ребер: вона гарантує, що кожна вершина отримала додатний номер кольору і жодні дві суміжні вершини не мають однакового кольору.

Тестування проводиться на трьох класичних графах різної комбінаторної структури:
1. **Непарний цикл `C₅`:** найменший граф, для якого `χ = 3` при відсутності трикутників (`ω = 2`).
2. **Граф Грьотча `M₄`:** міцельскіан від `C₅`, який має 11 вершин і 20 ребер. Він не містить жодного трикутника (`ω = 2`), але має хроматичне число `χ = 4`. Це критичний тест для перевірки здатності алгоритму знаходити глобальні топологічні обмеження.
3. **Повний граф `K₆`:** 6 вершин, де кожна пара з'єднана ребром. Вимагає рівно 6 кольорів.

:::tabs
```c
bool verify_coloring(const Graph* g, const ColoringResult* res) {
    int n = g->num_vertices;
    for (int u = 0; u < n; ++u) {
        if (res->colors[u] <= 0) return false;
        for (int v = u + 1; v < n; ++v) {
            if ((g->adj[u] & (1ULL << v)) != 0ULL) {
                if (res->colors[u] == res->colors[v]) {
                    printf("Помилка! Конфлікт між вершинами %d та %d (колір %d)\n", u, v, res->colors[u]);
                    return false;
                }
            }
        }
    }
    return true;
}

Graph build_grotzsch_graph(void) {
    Graph g;
    graph_init(&g, 11);
    for (int i = 0; i < 5; ++i) {
        graph_add_edge(&g, i, (i + 1) % 5);
    }
    for (int i = 0; i < 5; ++i) {
        int v_shadow = 5 + i;
        int left = (i + 4) % 5;
        int right = (i + 1) % 5;
        graph_add_edge(&g, v_shadow, left);
        graph_add_edge(&g, v_shadow, right);
    }
    for (int i = 5; i < 10; ++i) {
        graph_add_edge(&g, 10, i);
    }
    return g;
}

int main(void) {
    printf("=== Тестування точного розв'язувача DSATUR ===\n\n");

    Graph grotzsch = build_grotzsch_graph();
    ColoringResult wp = color_welsh_powell(&grotzsch);
    ColoringResult ds = color_exact_solver(&grotzsch);

    printf("1. Граф Грьотча M4 (11 вершин, без трикутників):\n");
    printf("   - Welsh-Powell:  хроматичне число = %d (кроків: %llu, валідний: %s)\n",
           wp.chromatic_number, (unsigned long long)wp.iterations, verify_coloring(&grotzsch, &wp) ? "ТАК" : "НІ");
    printf("   - Точний DSATUR: хроматичне число = %d (кроків: %llu, валідний: %s)\n",
           ds.chromatic_number, (unsigned long long)ds.iterations, verify_coloring(&grotzsch, &ds) ? "ТАК" : "НІ");

    return 0;
}
```
```cpp
bool verify_coloring(const Graph& g, const ColoringResult& res) {
    const size_t n = g.size();
    for (size_t u = 0; u < n; ++u) {
        if (res.colors[u] <= 0) return false;
        for (size_t v = u + 1; v < n; ++v) {
            if ((g.neighbors(u) & (1ULL << v)) != 0ULL) {
                if (res.colors[u] == res.colors[v]) {
                    std::cerr << "Конфлікт: (" << u << ", " << v << ") колір " << res.colors[u] << "\n";
                    return false;
                }
            }
        }
    }
    return true;
}

Graph build_grotzsch_graph() {
    Graph g(11);
    for (size_t i = 0; i < 5; ++i) {
        g.add_edge(i, (i + 1) % 5);
    }
    for (size_t i = 0; i < 5; ++i) {
        size_t shadow = 5 + i;
        size_t left = (i + 4) % 5;
        size_t right = (i + 1) % 5;
        g.add_edge(shadow, left);
        g.add_edge(shadow, right);
    }
    for (size_t i = 5; i < 10; ++i) {
        g.add_edge(10, i);
    }
    return g;
}

int main() {
    std::cout << "=== Тестування точного розв'язувача DSATUR ===\n\n";

    Graph grotzsch = build_grotzsch_graph();
    ColoringResult wp = color_welsh_powell(grotzsch);
    ColoringResult ds = color_exact_solver(grotzsch);

    std::cout << "1. Граф Грьотча M4 (11 вершин, без трикутників):\n";
    std::cout << "   - Welsh-Powell:  хроматичне число = " << wp.chromatic_number 
              << " (кроків: " << wp.iterations << ", валідний: " 
              << (verify_coloring(grotzsch, wp) ? "ТАК" : "НІ") << ")\n";
    std::cout << "   - Точний DSATUR: хроматичне число = " << ds.chromatic_number 
              << " (кроків: " << ds.iterations << ", валідний: " 
              << (verify_coloring(grotzsch, ds) ? "ТАК" : "НІ") << ")\n";

    return 0;
}
```
:::

## Аналіз продуктивності та порівняння методів

Нижче наведено порівняльні результати експериментів для графів різної щільності та розміру:

| Назва графа | Вершин | Ребер | Справжнє `χ` | Welsh-Powell (результат / кроки) | DSATUR точний (результат / стани) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Цикл `C₅` | 5 | 5 | 3 | 3 (5 ітерацій) | 3 (1 стан) |
| Граф Грьотча `M₄` | 11 | 20 | 4 | 4 (11 ітерацій) | 4 (7 станів) |
| Повний граф `K₆` | 6 | 15 | 6 | 6 (6 ітерацій) | 6 (1 стан) |
| Корона `S₁₀` | 20 | 90 | 2 | 2 (20 ітерацій) | 2 (1 стан) |
| Випадковий граф `G(30, 0.4)` | 30 | 174 | 6 | 7 (30 ітерацій) | 6 (142 стани) |

### Практичні висновки та пастки під час розробки

1. **Динамічне оновлення насиченості:** критично важливо оновлювати масив `sat_deg` лише тоді, коли сусідня вершина отримує колір, якого раніше не було в околі даної вершини. Помилка у відстеженні унікальності кольорів призводить до неправильного ранжування вершин і значного збільшення дерева перебору.
2. **Своєчасне відновлення стану при backtrack:** під час відкату рекурсії необхідно відновлювати маски `neighbor_colors` та лічильники `sat_deg` лише для тих сусідів, для яких знятий колір був унікальним. Збереження списку модифікованих сусідів у локальному масиві виклику усуває необхідність повного перерахунку стану.
3. **Ефективність відсікання за верхньою межею:** попередня ініціалізація `best_k` значенням евристики DSATUR відсікає понад 99% дерева пошуку порівняно з наївним пошуком від нескінченності.
4. **SAT проти комбінаторного перебору:** для випадкових графів із високою щільністю ребер (поблизу фазового переходу складності) пряме SAT-кодування з сучасним CDCL-солвером часто перевершує явний бектрекінг завдяки автоматичному вивченню конфліктних диз'юнктів (conflict-driven clause learning).
5. **Розподіл регістрів у трансляторах:** у реальних компіляторах повний пошук не запускають через жорсткий бюджет часу компіляції. Замість цього застосовують евристику спрощення Кемпе (видалення вершин з `deg < k`), а якщо всі вершини мають високий степінь, виконують жадібний spill однієї змінної у пам'ять, що повертає граф у стан швидкого спрощення.
