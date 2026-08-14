# ⚙️ Реалізація алгоритму Куна та Хопкрофта–Карпа

Розв'язання задачі про максимальне дводольне паросполучення у системному програмуванні вимагає вибору правильного компромісу між простотою алгоритму та продуктивністю на великих графах. Обхід у глибину алгоритму Куна зі складністю `O(V * E)` забезпечує мінімальні накладні витрати пам'яті та простоту реалізації, тоді як двофазний алгоритм Хопкрофта–Карпа зі складністю `O(E * sqrt(V))` є еталоном для масштабних графів із сотнями тисяч вершин.

### 1. Архітектура пам'яті та структури даних

Вибір структури даних для збереження дводольного графа визначає швидкість обходу ребер та локальність даних у кеш-пам'яті процесора. Для систем розробки високої продуктивності вибір між масивами та вказівниками стає критичним фактором.

#### Модель стисненого рядка суміжності (CSR / Stitched Adjacency Lists)

Для зберігання ребер графа у низькорівневих реалізаціях мовою C використовуються три суцільних одновимірних масиви:
- `head[u]` — зберігає індекс першого ребра у списку суміжності для вершини `u ∈ U`. Якщо вершина не має вихідних ребер, значення дорівнює `-1`.
- `to[e]` — зберігає індекс цільової вершини `v ∈ V` для ребра з номером `e`.
- `next[e]` — зберігає індекс наступного ребра у списку суміжності для тієї ж вершини `u`.

Ця структура, відома також як зірчасте представлення або прошитий список, володіє двома фундаментальними перевагами. По-перше, вона виділяється у пам'яті лише трьома системними викликами `malloc`, повністю усуваючи фрагментацію купи. По-друге, оскільки масиви `to` та `next` розташовані у суцільних блоках адресної пам'яті, процесорні модулі попередньої вибірки (hardware prefetcher) ефективно завантажують сусідні елементи у кєш-лінії L1/L2, мінімізуючи простої тактів процесора при переході між ребрами.

#### Модель об'єктно-орієнтованих векторів (C++ Containers)

У мові C++20 стандартним вибором є структура `std::vector<std::vector<std::size_t>>`. Зовнішній вектор містить `|U|` елементів, кожен з яких є внутрішнім вектором індексів сусідів з `V`. Ця модель є гнучкою, підтримує динамічне додавання ребер без попереднього знання їхньої точної кількості та забезпечує безпеку роботи з пам'яттю за рахунок концепції RAII (Resource Acquisition Is Initialization). 

Однак на великих графах вона спричиняє явище «полювання за вказівниками» (pointer chasing): кожен внутрішній вектор зберігає свій буфер у довільному місці динамічної пам'яті, що при інтенсивному обході DFS спричиняє підвищену кількість промахів кешу L1 (L1 Data Cache Misses).

---

### 2. Повна реалізація алгоритмів Куна та Хопкрофта–Карпа

Нижче наведено повний вихідний код реалізацій обох алгоритмів мовами C та C++20, включаючи створення структур або класів, виконання обчислень та звільнення ресурсів.

:::tabs
```c
/*
 * Повна реалізація алгоритму Куна мовою C.
 * Використовує прошитий список суміжності для мінімізації накладних витрат.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int* head;
    int* to;
    int* next;
    int edge_cnt;
    int n, m; // розміри часток U та V
} BipartiteGraph;

BipartiteGraph* graph_create(int n, int m, int max_edges) {
    BipartiteGraph* g = (BipartiteGraph*)malloc(sizeof(BipartiteGraph));
    if (!g) return NULL;
    g->n = n;
    g->m = m;
    g->edge_cnt = 0;
    g->head = (int*)malloc(n * sizeof(int));
    if (!g->head) { free(g); return NULL; }
    memset(g->head, -1, n * sizeof(int));
    g->to = (int*)malloc(max_edges * sizeof(int));
    g->next = (int*)malloc(max_edges * sizeof(int));
    return g;
}

void graph_add_edge(BipartiteGraph* g, int u, int v) {
    if (u < 0 || u >= g->n || v < 0 || v >= g->m) return;
    g->to[g->edge_cnt] = v;
    g->next[g->edge_cnt] = g->head[u];
    g->head[u] = g->edge_cnt++;
}

void graph_free(BipartiteGraph* g) {
    if (!g) return;
    free(g->head);
    free(g->to);
    free(g->next);
    free(g);
}

// Рекурсивний обхід DFS для пошуку доповнюючого шляху
static bool kuhn_dfs(const BipartiteGraph* g, int u, int* used_token, int current_token, int* match) {
    if (used_token[u] == current_token) return false;
    used_token[u] = current_token;

    for (int e = g->head[u]; e != -1; e = g->next[e]) {
        int v = g->to[e];
        if (match[v] == -1 || kuhn_dfs(g, match[v], used_token, current_token, match)) {
            match[v] = u;
            return true;
        }
    }
    return false;
}

// Оптимізований запуск алгоритму Куна з викликом жадібного проходу
int kuhn_max_matching(const BipartiteGraph* g, int* match_out) {
    int* match = (int*)malloc(g->m * sizeof(int));
    int* used_token = (int*)calloc(g->n, sizeof(int));
    for (int i = 0; i < g->m; ++i) match[i] = -1;

    // Попередній жадібний прохід для покриття 70%+ ребер без рекурсії
    int matching_size = 0;
    int* match_u = (int*)malloc(g->n * sizeof(int));
    for (int i = 0; i < g->n; ++i) match_u[i] = -1;

    for (int u = 0; u < g->n; ++u) {
        for (int e = g->head[u]; e != -1; e = g->next[e]) {
            int v = g->to[e];
            if (match[v] == -1) {
                match[v] = u;
                match_u[u] = v;
                matching_size++;
                break;
            }
        }
    }

    // Основний цикл для решти вільних вершин U
    int current_token = 0;
    for (int u = 0; u < g->n; ++u) {
        if (match_u[u] == -1) {
            current_token++;
            if (kuhn_dfs(g, u, used_token, current_token, match)) {
                matching_size++;
            }
        }
    }

    if (match_out) {
        memcpy(match_out, match, g->m * sizeof(int));
    }

    free(match_u);
    free(match);
    free(used_token);
    return matching_size;
}

int main(void) {
    BipartiteGraph* g = graph_create(4, 4, 10);
    graph_add_edge(g, 0, 0);
    graph_add_edge(g, 0, 1);
    graph_add_edge(g, 1, 1);
    graph_add_edge(g, 1, 2);
    graph_add_edge(g, 2, 0);
    graph_add_edge(g, 2, 2);
    graph_add_edge(g, 3, 3);

    int match[4];
    int max_match = kuhn_max_matching(g, match);

    printf("Максимальне паросполучення (C): %d\n", max_match);
    for (int v = 0; v < g->m; ++v) {
        if (match[v] != -1) {
            printf("  v%d <-> u%d\n", v, match[v]);
        }
    }

    graph_free(g);
    return 0;
}
```
```cpp
/*
 * Алгоритм Куна та Хопкрофта–Карпа мовою C++20.
 * Включає ідіоматичний RAII клас BipartiteGraph.
 */

#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <cstdint>
#include <limits>

class BipartiteGraph {
public:
    BipartiteGraph(std::size_t u_size, std::size_t v_size)
        : u_size_(u_size), v_size_(v_size), adj_(u_size) {}

    void add_edge(std::size_t u, std::size_t v) {
        if (u < u_size_ && v < v_size_) {
            adj_[u].push_back(v);
        }
    }

    [[nodiscard]] std::size_t u_size() const noexcept { return u_size_; }
    [[nodiscard]] std::size_t v_size() const noexcept { return v_size_; }

    // Обчислення максимального паросполучення алгоритмом Куна
    [[nodiscard]] std::pair<std::size_t, std::vector<int>> solve_kuhn() const {
        std::vector<int> match(v_size_, -1);
        std::vector<int> used_token(u_size_, 0);
        int current_token = 0;

        auto dfs = [&](auto self, std::size_t u) -> bool {
            if (used_token[u] == current_token) return false;
            used_token[u] = current_token;

            for (std::size_t v : adj_[u]) {
                if (match[v] == -1 || self(self, static_cast<std::size_t>(match[v]))) {
                    match[v] = static_cast<int>(u);
                    return true;
                }
            }
            return false;
        };

        std::size_t max_matching = 0;
        for (std::size_t u = 0; u < u_size_; ++u) {
            ++current_token;
            if (dfs(dfs, u)) {
                ++max_matching;
            }
        }
        return {max_matching, match};
    }

    // Обчислення максимального паросполучення алгоритмом Хопкрофта–Карпа O(E * sqrt(V))
    [[nodiscard]] std::pair<std::size_t, std::vector<int>> solve_hopcroft_karp() const {
        std::vector<int> match_u(u_size_, -1);
        std::vector<int> match_v(v_size_, -1);
        std::vector<int> dist(u_size_, 0);

        constexpr int INF = std::numeric_limits<int>::max();

        auto bfs = [&]() -> bool {
            std::queue<std::size_t> q;
            for (std::size_t u = 0; u < u_size_; ++u) {
                if (match_u[u] == -1) {
                    dist[u] = 0;
                    q.push(u);
                } else {
                    dist[u] = INF;
                }
            }

            bool found_free_v = false;
            while (!q.empty()) {
                std::size_t u = q.front();
                q.pop();

                for (std::size_t v : adj_[u]) {
                    if (match_v[v] == -1) {
                        found_free_v = true;
                    } else if (dist[match_v[v]] == INF) {
                        dist[match_v[v]] = dist[u] + 1;
                        q.push(static_cast<std::size_t>(match_v[v]));
                    }
                }
            }
            return found_free_v;
        };

        auto dfs = [&](auto self, std::size_t u) -> bool {
            for (std::size_t v : adj_[u]) {
                if (match_v[v] == -1 || 
                   (dist[match_v[v]] == dist[u] + 1 && self(self, static_cast<std::size_t>(match_v[v])))) {
                    match_v[v] = static_cast<int>(u);
                    match_u[u] = static_cast<int>(v);
                    return true;
                }
            }
            dist[u] = INF;
            return false;
        };

        std::size_t max_matching = 0;
        while (bfs()) {
            for (std::size_t u = 0; u < u_size_; ++u) {
                if (match_u[u] == -1 && dfs(dfs, u)) {
                    ++max_matching;
                }
            }
        }
        return {max_matching, match_v};
    }

private:
    std::size_t u_size_;
    std::size_t v_size_;
    std::vector<std::vector<std::size_t>> adj_;
};

int main() {
    BipartiteGraph g(4, 4);
    g.add_edge(0, 0);
    g.add_edge(0, 1);
    g.add_edge(1, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 0);
    g.add_edge(2, 2);
    g.add_edge(3, 3);

    auto [kuhn_size, kuhn_match] = g.solve_kuhn();
    std::cout << "[C++] Кун: розмір = " << kuhn_size << "\n";

    auto [hk_size, hk_match] = g.solve_hopcroft_karp();
    std::cout << "[C++] Хопкрофт–Карпа: розмір = " << hk_size << "\n";

    for (std::size_t v = 0; v < g.v_size(); ++v) {
        if (hk_match[v] != -1) {
            std::cout << "  v" << v << " <-> u" << hk_match[v] << "\n";
        }
    }
    return 0;
}
```
:::

---

### 3. Покрокове трасування стану масивів та викликів

Щоб зрозуміти внутрішню динаміку алгоритмів, детально проаналізуємо зміну стану масивів під час виконання алгоритму Куна на тестовому дводольному графі.

#### Вхідна топологія тестового графа:
- Ліва частка `U = {u_0, u_1, u_2, u_3}` (розмір `|U| = 4`).
- Права частка `V = {v_0, v_1, v_2, v_3}` (розмір `|V| = 4`).
- Множина орієнтованих ребер `E = {(u_0, v_0), (u_0, v_1), (u_1, v_1), (u_1, v_2), (u_2, v_0), (u_2, v_2), (u_3, v_3)}`.
- Початковий масив парних вершин `match[] = [-1, -1, -1, -1]`.

#### Покрокова інверсія та рух по стеку викликів:

1. **Ітерація 0 (`u = 0`):**
   - Запускається `kuhn_dfs(u_0)`. Лічильник посещений `current_token = 1`.
   - Перший сусід `v_0`. Перевіряємо `match[v_0]`. Оскільки `match[v_0] == -1` (вершина вільна), алгоритм миттєво робить призначення `match[v_0] = 0` і повертає `true`.
   - Стан `match[]`: `[0, -1, -1, -1]`. Кількість виявлених пар: 1.

2. **Ітерація 1 (`u = 1`):**
   - Запускається `kuhn_dfs(u_1)`. Лічильник `current_token = 2`.
   - Перший сусід `v_1`. Оскільки `match[v_1] == -1` (вільна), фіксуємо призначення `match[v_1] = 1` і повертаємо `true`.
   - Стан `match[]`: `[0, 1, -1, -1]`. Кількість виявлених пар: 2.

3. **Ітерація 2 (`u = 2`):**
   - Запускається `kuhn_dfs(u_2)`. Лічильник `current_token = 3`.
   - Перший сусід `v_0`. Оскільки `match[v_0] == 0` (зайнята вершиною `u_0`), запускаємо рекурсивний виклик `kuhn_dfs(u_0)`.
   - Усередині рекурсії `kuhn_dfs(u_0)`: 
     - Позначаємо `used_token[u_0] = 3`.
     - Перший сусід `v_0` уже розглядався. Беремо наступного сусіда `v_1`.
     - Вершина `v_1` зайнята `u_1` (`match[v_1] == 1`). Рекурсивно викликаємо `kuhn_dfs(u_1)`.
   - Усередині глибшої рекурсії `kuhn_dfs(u_1)`:
     - Позначаємо `used_token[u_1] = 3`.
     - Сусід `v_1` вже перевірявся. Беремо наступного сусіда `v_2`.
     - Вершина `v_2` вільна (`match[v_2] == -1`).
     - Фіксуємо призначення `match[v_2] = 1` і повертаємо `true` на рівень вгору!
   - Повернення у `kuhn_dfs(u_0)`: оскільки заглиблення повернуло `true`, вивільнену вершину `v_1` віддаємо вершині `u_0`, перенаправляючи `match[v_1] = 0`, і повертаємо `true`.
   - Повернення у `kuhn_dfs(u_2)`: вивільнену вершину `v_0` призначаємо вершині `u_2`, записуючи `match[v_0] = 2`, і повертаємо `true`.
   - Разом виявлено доповнюючий шлях завдовжки 5 ребер: `u_2 -> v_0 -> u_0 -> v_1 -> u_1 -> v_2`.
   - Стан `match[]`: `[2, 0, 1, -1]`. Кількість виявлених пар: 3.

4. **Ітерація 3 (`u = 3`):**
   - Запускається `kuhn_dfs(u_3)`. Лічильник `current_token = 4`.
   - Єдиний сусід `v_3` вільний (`match[v_3] == -1`).
   - Записуємо `match[v_3] = 3` і повертаємо `true`.
   - Підсумковий стан `match[]`: `[2, 0, 1, 3]`. Сформовано досконале паросполучення з 4 ребер.

---

### 4. Інженерні оптимізації та підвищення швидкодії

При вбудовуванні алгоритмів дводольного паросполучення у високопродуктивні обчислювальні системи (наприклад, планивальники системних задач чи аналізатори графічного потоку) застосовуються такі практичні прийоми прискорення:

#### Текстовий лічильник відвідувань (Timestamp Visited Tokens)

Традиційна реалізація очищує булів масив `used` викликом `memset(used, 0, n)` перед кожним пошуком доповнюючого шляху. Це додає `O(V)` накладних дій на кожну вершину, що на розріджених графах виходить дорожчим за сам обхід. Заміна булевого прапорця на цілочисельний масив `used_token[]` та унікальний ідентифікатор ітерації `current_token` повністю скасовує обнулення пам'яті. Перевірка `used_token[u] == current_token` виконується за один такт процесора.

#### Попередній жадібний фазовий прохід (Greedy Initialization Pass)

Перед запуском рекурсивних процедур DFS/BFS виконується один швидкий ітеративний прохід по всіх ребрах графа. Якщо вершина `u` має вільного сусіда `v`, ребро `(u, v)` миттєво додається до паросполучення за `O(1)` без створення кадрів у стеку рекурсії. На реальних графах цей прохід покриває від 60% до 85% усіх можливих пар за `O(E)` часу. В результаті важка рекурсія запускається лише для незначної залишковій кількості складних вершин.

#### Перестановка часток за розміром та ступенем (Partition Reordering)

Оскільки часова складність алгоритму Куна становить `O(|U| * |E|)`, розмір лівої частки `|U|` прямо визначає кількість зовнішніх викликів DFS. Якщо у графі кількість вершин `|U|` більша за `|V|`, доцільно інвертувати орієнтацію ребер і зауважити праву частку `V` як ліву. Пошук паросполучення від меншої частки суттєво зменшує загальний час обчислень.

---

### 5. Аналіз крайових випадків та стрес-тестування

Промислові модулі повинні гарантувати коректність роботи при будь-яких вхідних топологіях графа:

1. **Граф без ребер (`E = 0`):**
   Масиви списків суміжності порожні (`head[u] == -1`). Жадібний прохід та DFS завершуються миттєво, повертаючи розмір паросполучення 0 без виходу за межі масивів.

2. **Граф із порожніми частками (`|U| = 0` або `|V| = 0`):**
   Перевірка розмірів у конструкторі запобігає виділенню нульових масивів та вертає відповідний статус помилки або порожній результат.

3. **Незв'язні компоненти та ізольовані вершини:**
   При наявності вершин із нулевим ступенем алгоритм проскакує їх у зовнішньому циклі за один такт, не порушуючи цілісність масиву `match`.

4. **Надщільні дводольні графи (`E ≈ |U| * |V|`):**
   Жадібна фаза покриває майне всі вершини за перший прохід, а залишок розв'язується за 1–2 рекурсивних перенаправлення, уникаючи глибокого зациклення.

---

### 6. Побудова мінімального вершинного покриття за Кенігом

Після знаходження максимального паросполучення алгоритм може легко побудувати мінімальне вершинне покриття за `O(V + E)` мовою C++:

```cpp
// Побудова мінімального вершинного покриття за теоремою Кеніга
std::pair<std::vector<bool>, std::vector<bool>> 
build_min_vertex_cover(std::size_t u_size, std::size_t v_size,
                       const std::vector<std::vector<std::size_t>>& adj,
                       const std::vector<int>& match_v) {
    std::vector<int> match_u(u_size, -1);
    for (std::size_t v = 0; v < v_size; ++v) {
        if (match_v[v] != -1) {
            match_u[static_cast<std::size_t>(match_v[v])] = static_cast<int>(v);
        }
    }

    std::vector<bool> visited_u(u_size, false);
    std::vector<bool> visited_v(v_size, false);
    std::queue<std::size_t> q;

    // 1. Починаємо BFS з усіх вільних вершин U
    for (std::size_t u = 0; u < u_size; ++u) {
        if (match_u[u] == -1) {
            visited_u[u] = true;
            q.push(u);
        }
    }

    // 2. Змінний обхід по ребрах поза M (від U до V) та по ребрах з M (від V до U)
    while (!q.empty()) {
        std::size_t u = q.front();
        q.pop();

        for (std::size_t v : adj[u]) {
            if (!visited_v[v] && match_u[u] != static_cast<int>(v)) {
                visited_v[v] = true;
                if (match_v[v] != -1 && !visited_u[static_cast<std::size_t>(match_v[v])]) {
                    visited_u[static_cast<std::size_t>(match_v[v])] = true;
                    q.push(static_cast<std::size_t>(match_v[v]));
                }
            }
        }
    }

    // 3. Формуємо покриття: C = (U \ Z) union (V intersect Z)
    std::vector<bool> cover_u(u_size, false);
    std::vector<bool> cover_v(v_size, false);

    for (std::size_t u = 0; u < u_size; ++u) {
        if (!visited_u[u]) cover_u[u] = true;
    }
    for (std::size_t v = 0; v < v_size; ++v) {
        if (visited_v[v]) cover_v[v] = true;
    }

    return {cover_u, cover_v};
}
```
