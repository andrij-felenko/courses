# ⚙️ Практична реалізація алгоритму Краскала: від масиву ребер до оптимізованого DSU

Практична швидкодія алгоритму Краскала безпосередньо залежить від двох ключових інженерних чинників: просторової локальності масиву ребер під час сортування та обчислювальної вартості операцій у системі неперетинних множин (Disjoint Set Union, DSU). На відміну від алгоритму Прима, який вимагає обходу списків суміжності через ланцюжки вказівників і створює нерегулярний патерн звернень до пам'яті, алгоритм Краскала оперує суцільним лінійним масивом структур ребер, що забезпечує максимальну ефективність апаратного кешу процесора.

## 1. Архітектура розв'язувача та представлення даних у пам'яті

Для представлення зваженого ребра використовується компактна структура без прихованого вирівнювання, оптимізована під 64-бітні регістри процесора:

:::tabs
```c
typedef struct {
    uint32_t u;
    uint32_t v;
    int64_t weight;
} Edge;
```
```cpp
struct Edge {
    uint32_t u{0};
    uint32_t v{0};
    int64_t weight{0};
};
```
:::

Такий формат дозволяє розмістити одне ребро рівно в 16 байтах пам'яті (два 32-бітні індекси вершин і 64-бітне знакове ціле для ваги). Масив із 1 мільйона ребер займає всього 16 МБ, що повністю вміщується в кеш L3 сучасних мікропроцесорів архітектури x86_64 та ARM64.

Система неперетинних множин підтримує два одномірні масиви розміром `V`:
- `parent[i]` — 32-бітний індекс батьківського вузла в дереві компонент;
- `rank[i]` — 8-бітна беззнакова оцінка глибини піддерева для збалансованого злиття.

Дві взаємодоповнюючі евристики забезпечують майже константний час виконання кожної операції `find` та `union`:
1. **Об'єднання за рангом (Union by Rank):** Корінь дерева з меншим рангом завжди приєднується до кореня з більшим рангом, обмежуючи максимальну висоту дерева величиною `O(log V)`.
2. **Стиснення шляхів (Path Compression):** Під час кожного запиту `find(x)` усі переглянуті вузли вздовж шляху переприв'язуються безпосередньо до знайденого абсолютного кореня, що амортизує вартість наступних запитів до `O(α(V))`.

Важливою деталлю реалізації є використання **двопрохідного нерекурсивного стиснення шляхів**. Рекурсивний підхід до пошуку кореня створює ризик переповнення стека викликів (Stack Overflow) на вироджених деревах глибиною в мільйони вузлів. Нерекурсивна реалізація спочатку знаходить корінь у простому циклі, а потім у другому короткому циклі перенаправляє покажчики `parent` усіх вузлів шляху на знайдений корінь. Це усуває накладні витрати на виклики функцій та зберігає компактність машинного коду.

## 2. Повна еталонна реалізація розв'язувача мовами C та C++

Наведений нижче код реалізує повнофункціональний розв'язувач мінімального кістякового дерева з підтримкою раннього виходу (коли набрано `V - 1` ребро) та коректною обробкою незв'язаних графів (побудова мінімального кістякового лісу, MSF).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Структура представлення зваженого ребра
typedef struct {
    uint32_t u;
    uint32_t v;
    int64_t weight;
} Edge;

// Структура системи неперетинних множин (DSU)
typedef struct {
    uint32_t *parent;
    uint8_t *rank;
    uint32_t num_sets;
} Dsu;

// Ініціалізація DSU
static bool dsu_init(Dsu *dsu, uint32_t n) {
    dsu->parent = (uint32_t *)malloc(n * sizeof(uint32_t));
    dsu->rank = (uint8_t *)calloc(n, sizeof(uint8_t));
    if (!dsu->parent || !dsu->rank) {
        free(dsu->parent);
        free(dsu->rank);
        return false;
    }
    for (uint32_t i = 0; i < n; ++i) {
        dsu->parent[i] = i;
    }
    dsu->num_sets = n;
    return true;
}

static void dsu_free(Dsu *dsu) {
    free(dsu->parent);
    free(dsu->rank);
    dsu->parent = NULL;
    dsu->rank = NULL;
}

// Пошук представника множини зі стисненням шляху без рекурсії
static uint32_t dsu_find(Dsu *dsu, uint32_t i) {
    uint32_t root = i;
    while (root != dsu->parent[root]) {
        root = dsu->parent[root];
    }
    // Другий прохід: стиснення шляху
    uint32_t curr = i;
    while (curr != root) {
        uint32_t nxt = dsu->parent[curr];
        dsu->parent[curr] = root;
        curr = nxt;
    }
    return root;
}

// Об'єднання за рангом
static bool dsu_union(Dsu *dsu, uint32_t i, uint32_t j) {
    uint32_t root_i = dsu_find(dsu, i);
    uint32_t root_j = dsu_find(dsu, j);
    if (root_i == root_j) {
        return false; // Вже в одній компоненті (цикл)
    }

    if (dsu->rank[root_i] < dsu->rank[root_j]) {
        dsu->parent[root_i] = root_j;
    } else if (dsu->rank[root_i] > dsu->rank[root_j]) {
        dsu->parent[root_j] = root_i;
    } else {
        dsu->parent[root_j] = root_i;
        dsu->rank[root_i]++;
    }
    dsu->num_sets--;
    return true;
}

// Компаратор для швидкого сортування ребер
static int edge_compare(const void *a, const void *b) {
    const Edge *ea = (const Edge *)a;
    const Edge *eb = (const Edge *)b;
    if (ea->weight < eb->weight) return -1;
    if (ea->weight > eb->weight) return 1;
    return 0;
}

// Результат виконання алгоритму Краскала
typedef struct {
    Edge *mst_edges;
    size_t edge_count;
    int64_t total_weight;
    bool is_fully_connected;
} KruskalResult;

KruskalResult kruskal_solve(uint32_t num_vertices, Edge *edges, size_t num_edges) {
    KruskalResult res = { NULL, 0, 0, false };
    if (num_vertices == 0) {
        res.is_fully_connected = true;
        return res;
    }

    res.mst_edges = (Edge *)malloc((num_vertices - 1) * sizeof(Edge));
    if (!res.mst_edges && num_vertices > 1) {
        return res;
    }

    // Крок 1: Глобальне сортування ребер
    qsort(edges, num_edges, sizeof(Edge), edge_compare);

    // Крок 2: Ініціалізація DSU
    Dsu dsu;
    if (!dsu_init(&dsu, num_vertices)) {
        free(res.mst_edges);
        res.mst_edges = NULL;
        return res;
    }

    // Крок 3: Жадібний вибір ребер
    for (size_t i = 0; i < num_edges; ++i) {
        if (dsu_union(&dsu, edges[i].u, edges[i].v)) {
            res.mst_edges[res.edge_count++] = edges[i];
            res.total_weight += edges[i].weight;

            // Оптимізація раннього виходу
            if (res.edge_count == num_vertices - 1) {
                break;
            }
        }
    }

    res.is_fully_connected = (res.edge_count == num_vertices - 1);
    dsu_free(&dsu);
    return res;
}
```
```cpp
#include <vector>
#include <span>
#include <algorithm>
#include <cstdint>
#include <numeric>
#include <expected>
#include <optional>

struct Edge {
    uint32_t u{0};
    uint32_t v{0};
    int64_t weight{0};

    constexpr bool operator<(const Edge& other) const noexcept {
        return weight < other.weight;
    }
};

class DisjointSetUnion {
public:
    explicit DisjointSetUnion(uint32_t n)
        : parent_(n), rank_(n, 0), num_sets_(n) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    [[nodiscard]] uint32_t find(uint32_t node) noexcept {
        uint32_t root = node;
        while (root != parent_[root]) {
            root = parent_[root];
        }
        // Стиснення шляху (двопрохідний варіант без рекурсії)
        uint32_t curr = node;
        while (curr != root) {
            uint32_t nxt = parent_[curr];
            parent_[curr] = root;
            curr = nxt;
        }
        return root;
    }

    bool unite(uint32_t u, uint32_t v) noexcept {
        uint32_t root_u = find(u);
        uint32_t root_v = find(v);
        if (root_u == root_v) {
            return false;
        }

        if (rank_[root_u] < rank_[root_v]) {
            parent_[root_u] = root_v;
        } else if (rank_[root_u] > rank_[root_v]) {
            parent_[root_v] = root_u;
        } else {
            parent_[root_v] = root_u;
            ++rank_[root_u];
        }
        --num_sets_;
        return true;
    }

    [[nodiscard]] uint32_t component_count() const noexcept {
        return num_sets_;
    }

private:
    std::vector<uint32_t> parent_;
    std::vector<uint8_t> rank_;
    uint32_t num_sets_;
};

struct KruskalResult {
    std::vector<Edge> mst_edges;
    int64_t total_weight{0};
    bool is_fully_connected{false};
};

enum class KruskalError {
    InvalidVertexIndex,
    EmptyGraph
};

[[nodiscard]] std::expected<KruskalResult, KruskalError>
compute_kruskal_mst(uint32_t num_vertices, std::span<Edge> edges) {
    if (num_vertices == 0) {
        return KruskalResult{{}, 0, true};
    }

    // Перевірка коректності індексів вершин
    for (const auto& edge : edges) {
        if (edge.u >= num_vertices || edge.v >= num_vertices) {
            return std::unexpected(KruskalError::InvalidVertexIndex);
        }
    }

    // Крок 1: Швидке сортування масиву ребер за зростанням ваги
    std::ranges::sort(edges);

    // Крок 2: Ініціалізація DSU
    DisjointSetUnion dsu(num_vertices);

    KruskalResult result;
    result.mst_edges.reserve(num_vertices - 1);

    // Крок 3: Жадібний вибір ребер з раннім виходом
    for (const auto& edge : edges) {
        if (dsu.unite(edge.u, edge.v)) {
            result.mst_edges.push_back(edge);
            result.total_weight += edge.weight;

            if (result.mst_edges.size() == num_vertices - 1) {
                break;
            }
        }
    }

    result.is_fully_connected = (result.mst_edges.size() == num_vertices - 1);
    return result;
}
```
:::

## 3. Оптимізація: Порозрядне сортування (Radix Sort) для цілих ваг

Коли ваги ребер є невід'ємними цілими числами в обмеженому діапазоні (наприклад, `0 ≤ w(e) < 2³²`), загальну часову складність алгоритму Краскала можна зменшити з `O(E log E)` до строго лінійної `O(E + V)`.

Для цього використовується 8-бітний побайтовий порозрядний сортувальник (LSD Radix Sort) у 4 проходи по 256 кошиків. Замість порівнянь елементів ребра розкладаються по бакетах за відповідним байтом ваги:

:::tabs
```c
// Порозрядне сортування масиву ребер (32-бітні беззнакові ваги)
void radix_sort_edges(Edge *edges, size_t n) {
    Edge *temp = (Edge *)malloc(n * sizeof(Edge));
    if (!temp) return;

    for (int shift = 0; shift < 32; shift += 8) {
        size_t count[256] = {0};

        // Підрахунок частот для поточного байта
        for (size_t i = 0; i < n; ++i) {
            uint8_t byte = (uint8_t)((edges[i].weight >> shift) & 0xFF);
            count[byte]++;
        }

        // Перетворення частот на префіксні суми
        size_t total = 0;
        for (int i = 0; i < 256; ++i) {
            size_t old = count[i];
            count[i] = total;
            total += old;
        }

        // Стабільне перенесення в тимчасовий буфер
        for (size_t i = 0; i < n; ++i) {
            uint8_t byte = (uint8_t)((edges[i].weight >> shift) & 0xFF);
            temp[count[byte]++] = edges[i];
        }

        // Копіювання назад
        for (size_t i = 0; i < n; ++i) {
            edges[i] = temp[i];
        }
    }
    free(temp);
}
```
```cpp
#include <vector>
#include <span>
#include <array>
#include <cstdint>
#include <algorithm>

void radix_sort_edges(std::span<Edge> edges) {
    const size_t n = edges.size();
    if (n <= 1) return;

    std::vector<Edge> temp(n);

    for (int shift = 0; shift < 32; shift += 8) {
        std::array<size_t, 256> count{};

        for (const auto& edge : edges) {
            auto byte = static_cast<uint8_t>((edge.weight >> shift) & 0xFF);
            ++count[byte];
        }

        size_t total = 0;
        for (auto& cnt : count) {
            size_t old = cnt;
            cnt = total;
            total += old;
        }

        for (const auto& edge : edges) {
            auto byte = static_cast<uint8_t>((edge.weight >> shift) & 0xFF);
            temp[count[byte]++] = edge;
        }

        std::ranges::copy(temp, edges.begin());
    }
}
```
:::

Порозрядне сортування є стабільним (Stable Sort), що зберігає відносний порядок ребер з однаковою вагою. Оскільки кожен прохід читає та записує масив суто послідовно, пропускна здатність на сучасних каналах пам'яті DDR5 перевищує 50 ГБ/с.

## 4. Профілювання, кеш-пам'ять та аналіз крайових випадків

Практичні вимірювання показують, що алгоритм Краскала демонструє виняткову продуктивність на сучасних багатоядерних системах саме завдяки передбачуваному шаблону доступу до пам'яті:

1. **Фаза сортування:** Алгоритм `std::ranges::sort` або `qsort` виконує послідовні та локальні читання масиву `edges`. Процесорний кеш L1/L2 насичується даними з максимальною швидкістю, забезпечуючи нульові простої обчислювального конвеєра.
2. **Фаза DSU:** Операції `dsu_union` звертаються до компактного масиву `parent`, розмір якого для графа з `100 000` вершин становить лише 400 КБ. Цей масив повністю поміщається в кеш L2 процесора, усуваючи затримки доступу до оперативної пам'яті (DRAM Latency).
3. **Ефект ранньої зупинки:** На випадкових графах необхідні `V - 1` ребер часто знаходяться серед перших `20–30%` найдешевших ребер. Завдяки умові `mst_edges.size() == num_vertices - 1` алгоритм уникає перегляду решти `70–80%` масиву, що дає додаткове трикратне прискорення.

### Обробка специфічних конфігурацій графів

1. **Мультиграфи з паралельними ребрами:** Алгоритм Краскала не вимагає попереднього видалення дублікатів. Оскільки ребра впорядковані за вагою, найдешевше паралельне ребро між вузлами `u` та `v` буде перевірено першим і успішно додано. Наступні важчі дублікати між цими самими вершинами дадуть `dsu_find(u) == dsu_find(v)` і будуть відкинуті за `O(1)` часу.
2. **Петлі (Self-loops):** Для ребра вигляду `(u, u)` перевірка `dsu_find(u) == dsu_find(u)` негайно ідентифікує тривіальний цикл і запобігає включенню петлі до кістяка.
3. **Незв'язані топології:** Якщо у вхідному графі відсутній наскрізний маршрут між усіма вершинами, алгоритм будує множину кістякових дерев для кожної ізольованої компоненти окремо (Minimum Spanning Forest). Поле `is_fully_connected` дозволяє викликаючому модулю однозначно визначити цілісність топології.
4. **Графи з великою кількістю однакових ваг:** Якщо більшість ребер мають однакову вагу (наприклад, ваги 0 або 1), алгоритм гарантовано знаходить коректний кістяк. Порядок додавання однакових ребер визначає, яка саме з кількох можливих конфігурацій мінімального дерева буде побудована.
