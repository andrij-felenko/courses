# ⚙️ Практична реалізація алокатора регістрів Chaitin-Briggs

Розподіл регістрів є ключовою оптимізаційною фазою генератора коду (англ. *compiler backend*). Головне завдання цього етапу — перетворити проміжне представлення програми (IR), сформоване на основі нескінченної множини віртуальних регістрів (`v0, v1, v2, ...`), на машинний код для конкретної цільової архітектури (x86-64, ARM64, RISC-V), яка володіє строго обмеженим набором `K` фізичних апаратних регістрів.

У цій вставці наведено повний практичний розбір та вихідний код класичного алгоритму розфарбування графів Чейтіна–Бріґґса (англ. *Chaitin-Briggs Graph Coloring Register Allocator*). Розглянуто двомовну реалізацію на C та C++, детальний аналіз алгоритмічних фаз, покрокове простеження виконання, реалізацію консервативного злиття регістрів (Register Coalescing), механіку повторного обчислення (Rematerialization), а також розбір апаратних обмежень реальних процесорів та методів профілювання продуктивності.

---

### 1. Архітектурний контекст та детальна постановка задачі

Під час фронтенд-оптимізації компілятор оперує триадресним кодом або представленням у вигляді графів потоку керування (CFG), припускаючи, що кількість регістрів є необмеженою. Це дозволяє оптимізаторам виразів легко створювати нові проміжні змінні без оглядань на апаратні ресурси. Однак на стадії генерації бінарного коду виникає жорстке фізичне обмеження:
- Архітектура x86-64 має лише 16 регістрів загального призначення (`rax, rbx, rcx, rdx, rsi, rdi, rbp, rsp, r8..r15`).
- Архітектура ARM64 (AArch64) надає 31 регістр загального призначення (`x0..x30`).
- Архітектура RISC-V (RV64I) має 32 регістри (`x0..x31`, де `x0` строго дорівнює 0).

Якщо кількість одночасно живих змінних (англ. *register pressure*) у певній точці програми перевищує кількість доступних фізичних регістрів `K`, компілятор мусить вивантажити частину змінних у стек оперативної пам'яті (виконати операцію **Spill**). Звернення до оперативної пам'яті навіть через L1-кеш вимагає 3–5 тактів процесора, тоді як доступ до регістра виконується за 1 такт. Тому головна мета алокатора — мінімізувати кількість операцій зчитування та запису в стек для найчастіше використовуваних змінних.

Вхідними даними для нашого алокатора є список інтервалів життєвості віртуальних змінних `LiveInterval`. Кожен інтервал визначається початковою точкою `start` та кінцевою точкою `end` виконання в інструкціях IR (піввідкриті інтервали `[start, end)`). Дві змінні інтерферують (не можуть займати один і той самий фізичний регістр), якщо їхні інтервали перетинаються в часі:

```
Overlaps(A, B)  ⇔  !(end_A ≤ start_B  ∨  end_B ≤ start_A)
```

Для реалізації алокатора ми будуємо три ключові структури даних:
1. **Інтервал життєвості (`LiveInterval`):** ідентифікатор змінної, межі `[start, end)`, вартість скидання в пам'ять (Spill Cost) та прапор попереднього розфарбування для апаратних регістрів.
2. **Граф інтерференції (`InterferenceGraph`):** матриця або списки суміжності для кожної вершини, динамічний масив степеней та статус розфарбування.
3. **Стек спрощення Кемпе (`SimplificationStack`):** LIFO-структура для збереження порядку вилучення вершин з графа.

---

### 2. Структури даних та організація пам'яті компіляторного бекенду

Для високої ефективності алокатора регістрів у промислових компіляторах (GCC, LLVM) вибір структури даних графа інтерференції відіграє критичну роль. Матриця суміжності `adj[N][N]` надає перевірку наявності ребра за константний час `O(1)`, проте вимагає `O(N²)` пам'яті, що для великих функцій із тисячами змінних може вимагати мегабайти оперативної пам'яті.

Натомість списки суміжності `std::vector<std::vector<int>>` скорочують використання пам'яті до `O(|V| + |E|)`, але вимагають лінійного пошуку для перевірки існування ребра. У наших реалізаціях використовується комбінований підхід: двовимірний масив прапорців суміжності для миттєвої перевірки перетинів у поєднанні з динамічним масивом степеней вершин `degree`, який оновлюється за один прохід під час спрощення графа.

У промислових фреймворках (наприклад, LLVM `MachineRegisterInfo`) замість густих матриць використовуються розріджені бітові множини (англ. *Sparse BitSets*), де кожне ребро зберігається як біт у словах розміром 64 біти. Це зменшує розмір графа у 64 рази порівняно з масивом булевих значень `bool`, зберігаючи високу локальність даних у L1-кеші процесора.

Важливим параметром структури `LiveInterval` є показник `spill_cost`. Він обчислюється на фазі аналізу потоку даних за формулою:

```
SpillCost(v) = ∑_{u ∈ Uses(v)} 10^{LoopDepth(u)} + ∑_{d ∈ Defs(v)} 10^{LoopDepth(d)}
```

Де `LoopDepth` — глибина вкладеності циклу, у якому розташована відповідна інструкція зчитування або запису змінної `v`. Вага `10^{LoopDepth}` відображає статистичну частоту виконання інструкцій усередині вкладених циклів: інструкція всередині потрійного вкладеного циклу виконується орієнтовно у 1000 разів частіше, ніж інструкція у лінійному коді поза циклами.

---

### 3. Практична реалізація: порівняльний код на C та C++

Нижче наведено дві повноцінні, автономні реалізації алокатора Чейтіна–Бріґґса. Перша реалізація написана чистою мовою C (ANSI C / C99) з орієнтацією на максимальну простоту та відсутність зовнішніх залежностей. Друга реалізація виконана сучасною мовою C++20 із застосуванням концепції RAII, стандартних контейнерів `std::vector`, `std::unordered_set` та виразної обробки помилок.

:::tabs
```c
/* register_allocator.c — Реалізація алокатора регістрів мовою C (ANSI C / C99) */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 64
#define NO_COLOR -1
#define SPILL_COLOR -2

typedef struct {
    int id;
    int start;
    int end;
    double spill_cost;
    bool is_precolored;
} LiveInterval;

typedef struct {
    int num_nodes;
    int num_colors; // K фізичних регістрів
    LiveInterval intervals[MAX_NODES];
    bool adj[MAX_NODES][MAX_NODES];
    int degree[MAX_NODES];
    int colors[MAX_NODES];
    bool removed[MAX_NODES];
} InterferenceGraph;

/* Ініціалізація графа інтерференції */
void graph_init(InterferenceGraph *g, int num_colors) {
    g->num_nodes = 0;
    g->num_colors = num_colors;
    for (int i = 0; i < MAX_NODES; i++) {
        g->degree[i] = 0;
        g->colors[i] = NO_COLOR;
        g->removed[i] = false;
        for (int j = 0; j < MAX_NODES; j++) {
            g->adj[i][j] = false;
        }
    }
}

/* Додавання віртуальної змінної */
int graph_add_node(InterferenceGraph *g, int id, int start, int end, double cost, bool precolored) {
    int idx = g->num_nodes++;
    g->intervals[idx].id = id;
    g->intervals[idx].start = start;
    g->intervals[idx].end = end;
    g->intervals[idx].spill_cost = cost;
    g->intervals[idx].is_precolored = precolored;
    return idx;
}

/* Перевірка перетину піввідкритих інтервалів життєвості [start, end) */
static bool intervals_overlap(const LiveInterval *a, const LiveInterval *b) {
    return !(a->end <= b->start || b->end <= a->start);
}

/* Побудова ребер графа інтерференції */
void graph_build_edges(InterferenceGraph *g) {
    for (int i = 0; i < g->num_nodes; i++) {
        for (int j = i + 1; j < g->num_nodes; j++) {
            if (intervals_overlap(&g->intervals[i], &g->intervals[j])) {
                g->adj[i][j] = true;
                g->adj[j][i] = true;
                g->degree[i]++;
                g->degree[j]++;
            }
        }
    }
}

/* Запуск алгоритму розфарбування Чейтіна-Бріґґса */
bool graph_allocate_registers(InterferenceGraph *g) {
    int stack[MAX_NODES];
    int stack_top = 0;
    int remaining = g->num_nodes;

    /* Фаза 1: Спрощення (Simplify & Spill) */
    while (remaining > 0) {
        int candidate = -1;

        /* Шукаємо вершину з deg < K (Правило Кемпе), яка не є precolored */
        for (int i = 0; i < g->num_nodes; i++) {
            if (!g->removed[i] && !g->intervals[i].is_precolored && g->degree[i] < g->num_colors) {
                candidate = i;
                break;
            }
        }

        /* Якщо всі вершини мають deg >= K, обираємо кандидат на Spill за мінімальним пріоритетом */
        if (candidate == -1) {
            double min_priority = 1e9;
            for (int i = 0; i < g->num_nodes; i++) {
                if (!g->removed[i] && !g->intervals[i].is_precolored) {
                    double priority = g->intervals[i].spill_cost / (double)(g->degree[i] + 1);
                    if (priority < min_priority) {
                        min_priority = priority;
                        candidate = i;
                    }
                }
            }
        }

        if (candidate == -1) break; // Залишилися лише precolored вершини

        /* Вилучаємо обрану вершину і додаємо у стек */
        g->removed[candidate] = true;
        stack[stack_top++] = candidate;
        remaining--;

        /* Оновлюємо степені сусідів */
        for (int i = 0; i < g->num_nodes; i++) {
            if (g->adj[candidate][i] && !g->removed[i]) {
                g->degree[i]--;
            }
        }
    }

    /* Фаза 2: Вибір кольорів (Select & Optimistic Coloring) */
    bool has_spills = false;
    while (stack_top > 0) {
        int node = stack[--stack_top];
        g->removed[node] = false;

        /* Визначаємо зайняті кольори сусідів */
        bool used_colors[MAX_NODES] = { false };
        for (int i = 0; i < g->num_nodes; i++) {
            if (g->adj[node][i] && !g->removed[i] && g->colors[i] >= 0) {
                used_colors[g->colors[i]] = true;
            }
        }

        /* Шукаємо перший вільний колір з K доступних */
        int assigned_color = NO_COLOR;
        for (int c = 0; c < g->num_colors; c++) {
            if (!used_colors[c]) {
                assigned_color = c;
                break;
            }
        }

        if (assigned_color != NO_COLOR) {
            g->colors[node] = assigned_color;
        } else {
            /* Оптимістичне розфарбування не вдалося -> Фактичний Spill */
            g->colors[node] = SPILL_COLOR;
            has_spills = true;
        }
    }

    return !has_spills;
}

int main(void) {
    InterferenceGraph g;
    graph_init(&g, 3); // K = 3 фізичні регістри (R0, R1, R2)

    /* Додаємо 5 віртуальних змінних */
    graph_add_node(&g, 1, 1, 3, 10.0, false); // v1
    graph_add_node(&g, 2, 2, 4, 15.0, false); // v2
    graph_add_node(&g, 3, 1, 5, 25.0, false); // v3
    graph_add_node(&g, 4, 4, 5, 5.0, false);  // v4
    graph_add_node(&g, 5, 3, 5, 12.0, false); // v5

    graph_build_edges(&g);
    bool success = graph_allocate_registers(&g);

    printf("=== Результат розподілу регістрів (C Implementation) ===\n");
    printf("Успішність розподілу без Spill: %s\n", success ? "ТАК" : "НІ");
    for (int i = 0; i < g.num_nodes; i++) {
        if (g.colors[i] >= 0) {
            printf("Змінна v%d -> Регістр R%d\n", g.intervals[i].id, g.colors[i]);
        } else {
            printf("Змінна v%d -> SPILL у стек пам'яті [rsp + %d]\n", g.intervals[i].id, i * 8);
        }
    }
    return 0;
}
```
```cpp
// register_allocator.cpp — Ідіоматична реалізація мовою C++20 (RAII, Containers, Expected)
#include <iostream>
#include <vector>
#include <stack>
#include <unordered_set>
#include <optional>
#include <algorithm>
#include <limits>
#include <format>

struct LiveInterval {
    int id;
    int start;
    int end;
    double spill_cost;
    bool is_precolored{false};

    [[nodiscard]] constexpr bool overlaps_with(const LiveInterval& other) const noexcept {
        return !(end <= other.start || other.end <= start);
    }
};

enum class AllocationStatus {
    Success,
    SpillRequired
};

class RegisterAllocator {
public:
    explicit RegisterAllocator(size_t num_physical_registers)
        : k_registers_(num_physical_registers) {}

    void add_interval(int id, int start, int end, double cost, bool precolored = false) {
        intervals_.push_back({id, start, end, cost, precolored});
    }

    struct AllocationResult {
        AllocationStatus status;
        std::vector<int> node_colors; // >= 0: колір регістру, -1: Spill
    };

    AllocationResult allocate() {
        const size_t n = intervals_.size();
        std::vector<std::vector<bool>> adj(n, std::vector<bool>(n, false));
        std::vector<int> degree(n, 0);

        // 1. Побудова графа інтерференції
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                if (intervals_[i].overlaps_with(intervals_[j])) {
                    adj[i][j] = adj[j][i] = true;
                    degree[i]++;
                    degree[j]++;
                }
            }
        }

        // 2. Фаза спрощення (Simplify & Potential Spills)
        std::vector<bool> removed(n, false);
        std::stack<size_t> simplify_stack;
        size_t remaining = n;

        while (remaining > 0) {
            std::optional<size_t> candidate;

            // Шукаємо deg < K серед не-precolored
            for (size_t i = 0; i < n; ++i) {
                if (!removed[i] && !intervals_[i].is_precolored && static_cast<size_t>(degree[i]) < k_registers_) {
                    candidate = i;
                    break;
                }
            }

            // Якщо deg >= K, обираємо кандидат на Spill за відносним пріоритетом
            if (!candidate) {
                double min_priority = std::numeric_limits<double>::max();
                for (size_t i = 0; i < n; ++i) {
                    if (!removed[i] && !intervals_[i].is_precolored) {
                        double priority = intervals_[i].spill_cost / static_cast<double>(degree[i] + 1);
                        if (priority < min_priority) {
                            min_priority = priority;
                            candidate = i;
                        }
                    }
                }
            }

            if (!candidate) break;

            size_t idx = *candidate;
            removed[idx] = true;
            simplify_stack.push(idx);
            remaining--;

            for (size_t i = 0; i < n; ++i) {
                if (adj[idx][i] && !removed[i]) {
                    degree[i]--;
                }
            }
        }

        // 3. Фаза вибору кольорів (Select & Optimistic Coloring)
        std::vector<int> colors(n, -1);
        bool has_spill = false;

        while (!simplify_stack.empty()) {
            size_t node = simplify_stack.top();
            simplify_stack.pop();
            removed[node] = false;

            std::unordered_set<int> used_colors;
            for (size_t i = 0; i < n; ++i) {
                if (adj[node][i] && !removed[i] && colors[i] >= 0) {
                    used_colors.insert(colors[i]);
                }
            }

            int assigned_color = -1;
            for (size_t c = 0; c < k_registers_; ++c) {
                if (!used_colors.contains(static_cast<int>(c))) {
                    assigned_color = static_cast<int>(c);
                    break;
                }
            }

            if (assigned_color != -1) {
                colors[node] = assigned_color;
            } else {
                colors[node] = -1; // Spill
                has_spill = true;
            }
        }

        return AllocationResult{
            .status = has_spill ? AllocationStatus::SpillRequired : AllocationStatus::Success,
            .node_colors = std::move(colors)
        };
    }

private:
    size_t k_registers_;
    std::vector<LiveInterval> intervals_;
};

int main() {
    RegisterAllocator allocator(3); // K = 3
    allocator.add_interval(1, 1, 3, 10.0);
    allocator.add_interval(2, 2, 4, 15.0);
    allocator.add_interval(3, 1, 5, 25.0);
    allocator.add_interval(4, 4, 5, 5.0);
    allocator.add_interval(5, 3, 5, 12.0);

    auto result = allocator.allocate();

    std::cout << "=== Результат розподілу регістрів (C++20 Implementation) ===\n";
    std::cout << std::format("Успішність розподілу: {}\n", 
        result.status == AllocationStatus::Success ? "УСПІХ (без Spill)" : "ПОТРІБЕН SPILL");

    for (size_t i = 0; i < result.node_colors.size(); ++i) {
        if (result.node_colors[i] >= 0) {
            std::cout << std::format("Змінна v{} -> Регістр R{}\n", i + 1, result.node_colors[i]);
        } else {
            std::cout << std::format("Змінна v{} -> SPILL у стек [rsp + {}]\n", i + 1, i * 8);
        }
    }

    return 0;
}
```
:::

---

### 4. Детальний аналіз алгоритмічних фаз реалізації

Наведений вище код реалізує повноцінний двофазний конвеєр Чейтіна–Бріґґса з підтримкою оптимістичного розфарбування та оцінки пріоритетів скидання.

#### Фаза 1: Побудова графа та перевірка перетинів
Функція `intervals_overlap` перевіряє умову `!(end_A <= start_B || end_B <= start_A)` для піввідкритих інтервалів `[start, end)`. Якщо два часові інтервали життєвості мають хоча б одну спільну точку виконання, у матриці суміжності `adj` виставляється значення `true`, а степені обох вершин збільшуються на 1. Це створює ребра інтерференції.

#### Фаза 2: Спрощення за правилом Кемпе (Simplify)
В циклі `while (remaining > 0)` алокатор шукає вершину з степенем `deg(v) < K`. Якщо таку вершину знайдено:
- Вона вважається «безпечною» для розфарбування.
- Вона позначається як вилучена `removed[v] = true`.
- Вона додається у стек спрощення `simplify_stack`.
- Степені усіх її сусідів у графі зменшуються на 1, що може вивільнити нові вершини для спрощення.

#### Фаза 3: Вибір кандидатів на скидання (Spill Choice)
Якщо на певному кроці у графі не залишилося жодної вершини з `deg(v) < K`, виникає стан затору (англ. *stall*). Алгоритм обчислює відносний пріоритет для кожної залишкової вершини:

```
Priority(v) = SpillCost(v) / (deg(v) + 1)
```

Вершина з найменшим значенням `Priority(v)` обирається як кандидат на скидання. Вона також вилучається з графа і кладеться у стек `simplify_stack` як **потенційний Spill**.

#### Фаза 4: Оптимістичний вибір кольору (Select)
У зворотному циклі `while (!simplify_stack.empty())` вершини витягуються зі стеку і повертаються у граф. Алгоритм збирає кольори вже розфарбованих сусідів у множину `used_colors` і шукає найменший доступний колір `c ∈ [0, K - 1]`.
- Якщо вільний колір знайдено, вершина отримує його (навіть якщо вона була кандидаткою на скидання!).
- Якщо всі `K` кольорів зайняті сусідами, вершині присвоюється колір `-1` (**фактичний Spill**).

---

### 5. Реалізація консервативного злиття регістрів (Register Coalescing)

Важливою складовою промислових алокаторах є скасування зайвих інструкцій копіювання `mov v1, v2`. Якщо дві змінні `v1` та `v2` з'єднані інструкцією копіювання і не мають ребра інтерференції, їх можна злити в одну вершину `v12`.

Нижче наведено алгоритм перевірки **критерію Джорджа** для консервативного злиття мовою C++:

```cpp
/* Перевірка консервативного критерію Джорджа для злиття v1 та v2 */
bool can_coalesce_george(size_t v1, size_t v2, size_t K, 
                         const std::vector<std::vector<bool>>& adj, 
                         const std::vector<int>& degree) {
    const size_t n = adj.size();
    for (size_t t = 0; t < n; ++t) {
        if (adj[v1][t]) { // For every neighbor t of v1
            // Condition: t must already interfere with v2 OR deg(t) < K
            bool interferes_with_v2 = adj[v2][t];
            bool low_degree = static_cast<size_t>(degree[t]) < K;
            if (!interferes_with_v2 && !low_degree) {
                return false; // Coalescing unsafe!
            }
        }
    }
    return true; // Coalescing safe
}
```

Якщо критерій Джорджа виконується, алокатор замінює всі посилання на `v2` посиланнями на `v1`, об'єднує їхні списки суміжності та видаляє інструкцію `mov` з IR-коду.

Поряд із критерієм Джорджа у компіляторах застосовується альтернативний **критерій Бріґґса**: злиття двох вершин `v1` та `v2` вважається консервативно безпечним, якщо об'єднана вершина `v12` матиме менше ніж `K` сусідів зі степенями `deg ≥ K`. Обидва критерії гарантують, що злиття не перетворить розфарбовуваний граф на нерозфарбовуваний.

---

### 6. Повторне обчислення (Rematerialization) та розташування інструкцій Spill

У випадках, коли вивантаження змінної в пам'ять є неминучим, компілятор застосовує додаткові інженерні оптимізації для зменшення вартості Spill.

#### Концепція Rematerialization
Якщо змінна `v` є константою (наприклад, посилання на глобальний рядок або числову константу `42`) чи обчислюється однією простою інструкцією без побічних ефектів (`lea rdx, [rbp - 16]`), її недоцільно зберігати у стек пам'яті за допомогою `STORE`.

Замість збереження у стек компілятор знищує змінну `v`, а у точках її використання повторно обчислює її значення (виконує **Rematerialization**). Виконання однієї арифметичної інструкції на зразок `lea` або `mov rx, const` коштує 1 такт, що у 4–5 разів швидше за читання зі стеку через `LOAD`.

#### Оптимізація розташування Spill-інструкцій та вирівнювання фрейму
Замість генерації `STORE` одразу після кожної ініціалізації та `LOAD` перед кожним використанням, сучасні алокатори вставляють інструкції вивантаження строго на межах базових блоків з високим тиском на регістри. Якщо змінна потрібна у кількох послідовних інструкціях одного блоку, вона завантажується у тимчасовий регістр лише один раз на початку блоку і зберігається до його завершення.

Кожна скинута у стек змінна вимагає зміщення у стековому кадрі (наприклад, `[rsp + 0]`, `[rsp + 8]`). Алокатор повторно використовує вже вивільнені комірки стека для змінних з диз'юнктними інтервалами життєвості, зменшуючи підсумковий розмір стекового кадра функції. Крім того, алокатор гарантує вирівнювання адрес стека за межою 16 байт відповідно до вимог x86-64 System V ABI.

#### Робота з апаратними обмеженнями (Pre-colored Nodes)
Апаратні регістри, зафіксовані специфікою інструкційного набору (наприклад, `rax` та `rdx` у діленні x86-64 або `rcx` у зсувах), обробляються у графі як вершини з позначкою `is_precolored = true`. При алгоритмічному спрощенні такі вершини ніколи не видаляються з графа і не вивантажуються у стек (`spill_cost = ∞`). Їхні кольори є строго наперед призначеними, що звужує простір доступних регістрів для звичайних змінних програми.

---

### 7. Покрокове простеження виконання та профілювання

Простежимо виконання алгоритму для тестового графа з 5 змінними та `K = 3` регістрами:

```
Змінна v1: [1, 3), cost = 10.0
Змінна v2: [2, 4), cost = 15.0
Змінна v3: [1, 5), cost = 25.0
Змінна v4: [4, 5), cost = 5.0
Змінна v5: [3, 5), cost = 12.0
```

1. **Ребра інтерференції:** `(v1,v2), (v1,v3), (v2,v3), (v2,v5), (v3,v4), (v3,v5), (v4,v5)`.
2. **Початкові степені:** `deg(v1)=2, deg(v2)=3, deg(v3)=4, deg(v4)=2, deg(v5)=3`.
3. **Крок 1 (Спрощення):** `deg(v1) = 2 < 3` → Push `v1` у стек, remaining = 4.
4. **Крок 2 (Спрощення):** Після вилучення `v1`, `deg(v4) = 2 < 3` → Push `v4` у стек, remaining = 3.
5. **Крок 3 (Спрощення):** `deg(v2) = 2 < 3`, `deg(v5) = 2 < 3` → Push `v2`, Push `v5`.
6. **Крок 4 (Спрощення):** `deg(v3) = 0 < 3` → Push `v3`.
7. **Фаза Select (Pop зі стеку):**
   - Pop `v3` → призначено колір `R0`.
   - Pop `v5` → сусіди {v3:R0}, призначено колір `R1`.
   - Pop `v2` → сусіди {v3:R0, v5:R1}, призначено колір `R2`.
   - Pop `v4` → сусіди {v3:R0, v5:R1}, призначено колір `R2`.
   - Pop `v1` → сусіди {v2:R2, v3:R0}, призначено колір `R1`.

**Результат:** Граф повністю розфарбовано 3 кольорами без жодного скидання у стек пам'яті!

#### Відналагодження розподілу регістрів у промислових компіляторах
Для аналізу рішень алокатора у Clang/LLVM застосовуються прапорці відналагодження:
- `-mllvm -debug-only=regalloc` — друкує детальний лог усіх кроків розщеплення інтервалів, побудови графа інтерференції та пріоритетів скидання.
- `-mllvm -print-after=regalloc` — виводить стан Machine IR одразу після завершення розподілу регістрів.
- В GCC прапорець `-fdump-rtl-ira` виводить проміжну інформацію про роботу Integrated Register Allocator (IRA).

#### Профілювання та продуктивність
Вимірювання продуктивності згенерованого коду на бенчмарках SPEC CPU показує, що застосування консервативного злиття (Coalescing) зменшує загальну кількість машинного коду на 8–12%, а використання оптимістичного розфарбування Бріґґса зменшує кількість операцій зі стеком на 15–20% порівняно з початковим алгоритмом Чейтіна.
