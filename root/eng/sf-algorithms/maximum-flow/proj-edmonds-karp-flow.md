# ⚙️ Практична реалізація алгоритму Едмондса — Карпа: від структури даних до вилучення мінімального розрізу

Алгоритм Едмондса — Карпа є базовим інструментом для розв'язання задач про максимальний потік у мережах загального вигляду. На відміну від абстрактного опису, промислова реалізація алгоритму вимагає врахування низки інженерних деталей: коректного представлення антипаралельних дуг, компактного зберігання залишкових місткостей, уникнення лінійного пошуку зворотних ребер у списках суміжності та ефективного відновлення мінімального s-t розрізу.

Нижче наведено повну архітектуру розв'язувача потоку двома мовами — C та ідіоматичним сучасним C++, детальний аналіз пасток реалізації, вилучення розрізу та порівняльний аналіз із наївним методом.

## Представлення графа та техніка парних індексів

Головним завданням при проектуванні структури даних для потокової мережі є швидкий доступ до зворотного ребра. Коли потік `Δ` проштовхується по прямій дузі `(u, v)`, залишок `c_f(u, v)` зменшується на `Δ`, а залишок зворотного ребра `c_f(v, u)` збільшується на `Δ`.

У наївній матричній реалізації матриця суміжності розміру `|V| × |V|` забезпечує доступ за час `O(1)`, проте для розріджених графів (де `|E| ≪ |V|²`) вона споживає надмірну пам'ять `O(V²)` та вимагає повного сканування всіх `|V|` стовпців під час обходу BFS, що збільшує час роботи до `O(V³)`. Списки суміжності скорочують час обходу до `O(E)`, проте вимагають ефективного зв'язування прямої дуги з її парною реверсивною дугою.

Існує два класичних підходи до організації зв'язку між прямою та зворотною дугами:

1. **Індекс зворотного елемента у векторі (Vector + rev index):**
   У списку суміжності кожна дуга зберігає індекс `to` (куди веде), поточну пропускну спроможність `cap`, потік `flow` та цілочисельний індекс `rev` — позицію парного ребра у списку суміжності вершини `to`.
   Цей підхід ідеально підходить для C++ зі `std::vector<std::vector<Edge>>`, оскільки не накладає жорстких обмежень на попереднє виділення статичної пам'яті та дозволяє динамічно нарощувати розмір графа під час виконання програми.

2. **Масив дуг та бітова інверсія парного індексу (Forward Star + XOR trick):**
   У мові C дуги додаються парами у загальний масив: пряма дуга отримує парний індекс `2k`, а відповідна зворотна дуга — непарний індекс `2k + 1`. Зворотне ребро для будь-якого індексу `e` знаходиться за одну процесорну операцію за допомогою побітового виключного АБО `e ^ 1`.
   Це дозволяє уникнути збереження окремого поля `rev`, забезпечує безперервне розташування парних ребер у сусідніх комірках пам'яті та мінімізує промахи кешу першого рівня (L1 Data Cache Misses) під час аугментації потоку.

Обидві мови надають вичерпні інструменти для реалізації обох стратегій:

:::tabs
```cpp
// C++: структура ребра зі зворотним індексом у векторі суміжності
struct FlowEdge {
    int to;
    int rev;
    int64_t cap;
    int64_t flow;
};
```
```c
// C: структура ребра списку суміжності Forward Star
typedef struct {
    int to;
    int next;
    int64_t cap;
    int64_t flow;
} FlowArcC;
```
:::

## Еталонна реалізація алгоритму

Нижче наведено завершену реалізацію розв'язувача задачі про максимальний потік. Реалізація на C++ використовує шаблонні типи для місткостей, інкапсуляцію в клас, стандартні контейнери та динамічне вилучення мінімального розрізу. Реалізація на C побудована на статичних масивах списків суміжності з бітовою адресацією `e ^ 1` та ручним керуванням чергою.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <cstdint>
#include <algorithm>

template <typename FlowType = int64_t>
class EdmondsKarp {
public:
    struct Edge {
        int to;
        int rev;
        FlowType cap;
        FlowType flow;
    };

    explicit EdmondsKarp(int vertices)
        : n(vertices), adj(vertices) {}

    // Додавання орієнтованої дуги (from -> to) з місткістю cap.
    // Якщо мережа неорієнтована, rev_cap встановлюється рівним cap.
    void add_edge(int from, int to, FlowType cap, FlowType rev_cap = 0) {
        if (from == to || from < 0 || to < 0 || from >= n || to >= n) return;
        Edge forward_edge{to, static_cast<int>(adj[to].size()), cap, 0};
        Edge backward_edge{from, static_cast<int>(adj[from].size()), rev_cap, 0};
        adj[from].push_back(forward_edge);
        adj[to].push_back(backward_edge);
    }

    // Обчислення максимального s-t потоку
    FlowType max_flow(int s, int t) {
        if (s == t || s < 0 || t < 0 || s >= n || t >= n) return 0;
        FlowType total_flow = 0;

        // Зберігаємо для кожної вершини пару (батьківська вершина, індекс вихідного ребра)
        std::vector<int> parent_node(n, -1);
        std::vector<int> parent_edge(n, -1);

        while (bfs(s, t, parent_node, parent_edge)) {
            FlowType push_delta = std::numeric_limits<FlowType>::max();

            // 1. Пошук вузького місця (пляшкового горла) вздовж знайденого шляху
            for (int curr = t; curr != s; curr = parent_node[curr]) {
                int p = parent_node[curr];
                int edge_idx = parent_edge[curr];
                const Edge& e = adj[p][edge_idx];
                push_delta = std::min(push_delta, e.cap - e.flow);
            }

            // 2. Аугментація потоку вздовж шляху
            for (int curr = t; curr != s; curr = parent_node[curr]) {
                int p = parent_node[curr];
                int edge_idx = parent_edge[curr];
                Edge& forward_e = adj[p][edge_idx];
                Edge& backward_e = adj[curr][forward_e.rev];

                forward_e.flow += push_delta;
                backward_e.flow -= push_delta;
            }

            total_flow += push_delta;
        }

        return total_flow;
    }

    // Відновлення мінімального розрізу (S, T): повертає булеву маску,
    // де true відповідає вершинам множини S (досяжним з s у залишковій мережі).
    std::vector<bool> min_cut(int s) const {
        std::vector<bool> visited(n, false);
        std::queue<int> q;
        q.push(s);
        visited[s] = true;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (const auto& edge : adj[u]) {
                if (edge.cap - edge.flow > 0 && !visited[edge.to]) {
                    visited[edge.to] = true;
                    q.push(edge.to);
                }
            }
        }
        return visited;
    }

    const std::vector<Edge>& get_edges(int u) const {
        return adj[u];
    }

    int vertex_count() const {
        return n;
    }

private:
    int n;
    std::vector<std::vector<Edge>> adj;

    bool bfs(int s, int t, std::vector<int>& parent_node, std::vector<int>& parent_edge) {
        std::fill(parent_node.begin(), parent_node.end(), -1);
        std::fill(parent_edge.begin(), parent_edge.end(), -1);

        std::queue<int> q;
        q.push(s);
        parent_node[s] = s;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            if (u == t) break;

            for (size_t i = 0; i < adj[u].size(); ++i) {
                const Edge& edge = adj[u][i];
                if (edge.cap - edge.flow > 0 && parent_node[edge.to] == -1) {
                    parent_node[edge.to] = u;
                    parent_edge[edge.to] = static_cast<int>(i);
                    q.push(edge.to);
                }
            }
        }

        return parent_node[t] != -1;
    }
};
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 5000
#define MAX_ARCS  60000
#define FLOW_INF  INT64_MAX

typedef struct {
    int to;
    int next;
    int64_t cap;
    int64_t flow;
} FlowArc;

typedef struct {
    int n;
    int arc_count;
    int head[MAX_NODES];
    FlowArc arcs[MAX_ARCS];
} FlowNetworkC;

void flow_network_init(FlowNetworkC* net, int n) {
    net->n = n;
    net->arc_count = 0;
    memset(net->head, -1, sizeof(int) * n);
}

void flow_network_add_edge(FlowNetworkC* net, int from, int to, int64_t cap, int64_t rev_cap) {
    if (from == to || from < 0 || to < 0 || from >= net->n || to >= net->n) return;

    // Пряме ребро з парним індексом 2k
    net->arcs[net->arc_count] = (FlowArc){to, net->head[from], cap, 0};
    net->head[from] = net->arc_count++;

    // Зворотне ребро з непарним індексом 2k + 1
    net->arcs[net->arc_count] = (FlowArc){from, net->head[to], rev_cap, 0};
    net->head[to] = net->arc_count++;
}

static bool flow_network_bfs(FlowNetworkC* net, int s, int t, int parent_edge[MAX_NODES]) {
    memset(parent_edge, -1, sizeof(int) * net->n);
    int queue[MAX_NODES];
    int q_head = 0, q_tail = 0;

    queue[q_tail++] = s;
    parent_edge[s] = -2; // Спеціальна позначка для джерела

    while (q_head < q_tail) {
        int u = queue[q_head++];
        if (u == t) return true;

        for (int e = net->head[u]; e != -1; e = net->arcs[e].next) {
            int v = net->arcs[e].to;
            int64_t res_cap = net->arcs[e].cap - net->arcs[e].flow;

            if (res_cap > 0 && parent_edge[v] == -1) {
                parent_edge[v] = e;
                queue[q_tail++] = v;
            }
        }
    }

    return parent_edge[t] != -1;
}

int64_t flow_network_max_flow(FlowNetworkC* net, int s, int t) {
    if (s == t) return 0;
    int64_t total_flow = 0;
    int parent_edge[MAX_NODES];

    while (flow_network_bfs(net, s, t, parent_edge)) {
        int64_t push_delta = FLOW_INF;

        // 1. Пошук вузького місця
        for (int curr = t; curr != s; ) {
            int e = parent_edge[curr];
            int64_t res_cap = net->arcs[e].cap - net->arcs[e].flow;
            if (res_cap < push_delta) push_delta = res_cap;
            curr = net->arcs[e ^ 1].to; // Повернення назад до батька через реверсивне ребро
        }

        // 2. Аугментація потоку
        for (int curr = t; curr != s; ) {
            int e = parent_edge[curr];
            net->arcs[e].flow += push_delta;
            net->arcs[e ^ 1].flow -= push_delta;
            curr = net->arcs[e ^ 1].to;
        }

        total_flow += push_delta;
    }

    return total_flow;
}

void flow_network_min_cut(FlowNetworkC* net, int s, bool in_s[MAX_NODES]) {
    memset(in_s, false, sizeof(bool) * net->n);
    int queue[MAX_NODES];
    int q_head = 0, q_tail = 0;

    queue[q_tail++] = s;
    in_s[s] = true;

    while (q_head < q_tail) {
        int u = queue[q_head++];
        for (int e = net->head[u]; e != -1; e = net->arcs[e].next) {
            int v = net->arcs[e].to;
            if (net->arcs[e].cap - net->arcs[e].flow > 0 && !in_s[v]) {
                in_s[v] = true;
                queue[q_tail++] = v;
            }
        }
    }
}
```
:::

## Покроковий розбір прикладного використання: знаходження вузьких місць

Розглянемо практичний приклад: транспортна мережа розподілу вантажів із 6 вузлів, де джерело — центральний хаб (вузол 0), стік — кінцевий термінал (вузол 5), а решта — проміжні перевантажувальні станції. Необхідно не лише знайти максимальну пропускну спроможність, але й визначити критичні ділянки (ребра мінімального розрізу), розширення яких збільшить потік через усю мережу.

:::tabs
```cpp
int main() {
    // Створюємо мережу на 6 вершин (0..5)
    EdmondsKarp<int64_t> network(6);

    // Додаємо канали зв'язку: (from, to, capacity)
    network.add_edge(0, 1, 10);
    network.add_edge(0, 2, 10);
    network.add_edge(1, 2, 2);
    network.add_edge(1, 3, 4);
    network.add_edge(1, 4, 8);
    network.add_edge(2, 4, 9);
    network.add_edge(3, 5, 10);
    network.add_edge(4, 5, 10);

    // 1. Обчислюємо максимальний потік
    int64_t max_val = network.max_flow(0, 5);
    std::cout << "Максимальний потік: " << max_val << "\n";

    // 2. Отримуємо мінімальний розріз
    std::vector<bool> in_source_component = network.min_cut(0);

    std::cout << "Критичні ребра мінімального розрізу (S -> T):\n";
    for (int u = 0; u < network.vertex_count(); ++u) {
        if (!in_source_component[u]) continue;
        for (const auto& edge : network.get_edges(u)) {
            // Пряме ребро з S у T, яке було спочатку присутнє у графі
            if (!in_source_component[edge.to] && edge.cap > 0) {
                std::cout << "  Ребро " << u << " -> " << edge.to 
                          << " (насичено " << edge.flow << "/" << edge.cap << ")\n";
            }
        }
    }

    return 0;
}
```
```c
int main(void) {
    FlowNetworkC net;
    flow_network_init(&net, 6);

    flow_network_add_edge(&net, 0, 1, 10, 0);
    flow_network_add_edge(&net, 0, 2, 10, 0);
    flow_network_add_edge(&net, 1, 2, 2, 0);
    flow_network_add_edge(&net, 1, 3, 4, 0);
    flow_network_add_edge(&net, 1, 4, 8, 0);
    flow_network_add_edge(&net, 2, 4, 9, 0);
    flow_network_add_edge(&net, 3, 5, 10, 0);
    flow_network_add_edge(&net, 4, 5, 10, 0);

    int64_t max_val = flow_network_max_flow(&net, 0, 5);
    printf("Максимальний потік: %lld\n", (long long)max_val);

    bool in_s[6];
    flow_network_min_cut(&net, 0, in_s);

    printf("Критичні ребра мінімального розрізу (S -> T):\n");
    for (int u = 0; u < 6; ++u) {
        if (!in_s[u]) continue;
        for (int e = net.head[u]; e != -1; e = net.arcs[e].next) {
            int v = net.arcs[e].to;
            if (!in_s[v] && net.arcs[e].cap > 0) {
                printf("  Ребро %d -> %d (насичено %lld/%lld)\n",
                       u, v, (long long)net.arcs[e].flow, (long long)net.arcs[e].cap);
            }
        }
    }

    return 0;
}
```
:::

## Інженерні пастки та крайові випадки

1. **Антипаралельні дуги в початковому графі:**
   Якщо вихідний граф містить обидві дуги `u → v` (місткістю `c₁`) та `v → u` (місткістю `c₂`), наївна матриця залишкових місткостей перезаписала б значення. Наведена вище реалізація через списки суміжності створює дві незалежні пари дуг (усього 4 ребра в пам'яті). Кожна пара коректно відстежує свій власний прямий та зворотний потік, повністю усуваючи конфлікт.

2. **Захист від переповнення 32-бітних цілих чисел:**
   Сумарний потік через велику мережу може значно перевищувати діапазон типу `int32_t` (`2 · 10⁹`), навіть якщо місткості окремих ребер є помірними. Завжди використовуйте 64-бітні цілі типи (`int64_t` / `long long`) як для значень місткостей, так і для підсумкового накопичувача потоку.

3. **Коректне відновлення розрізу після зупинки:**
   Мінімальний розріз формується саме за досяжністю у **залишковій мережі `G_f`**, а не у вихідному графі. Ребро `(u, v)` вважається прохідним для завершального BFS лише тоді, коли `c_f(u, v) = c(u, v) - f(u, v) > 0`. Будь-яка насичена дуга (`f = c`) є непрохідною стіною, що відокремлює множину `S` від множини `T`.

4. **Від'ємний залишковий потік на зворотних дугах:**
   Зворотне ребро ініціалізується нульовою місткістю `cap = 0` та нульовим потоком `flow = 0`. Під час проштовхування потоку `Δ` вздовж прямого ребра його потік стає `+Δ`, а потік зворотного ребра — `-Δ`. Залишкова місткість зворотного ребра обчислюється як `cap - flow = 0 - (-Δ) = +Δ`, що математично відкриває можливість зворотного проштовхування без додаткових розгалужень у коді.

5. **Недосяжність стоку та ізольовані вузли:**
   Якщо в початковій мережі немає жодного шляху від `s` до `t`, перший же виклик BFS поверне `false`. Алгоритм коректно завершить роботу за час `O(V + E)`, повернувши `total_flow = 0`, а функція вилучення розрізу поверне компоненту зв'язності джерела `s`.

## Порівняння продуктивності: BFS проти DFS

Для демонстрації важливості вибору найкоротшого шляху зіставимо час роботи класичного пошуку в глибину (DFS, Ford-Fulkerson) та пошуку в ширину (BFS, Edmonds-Karp) на патологічній мережі з 4 вершин:
- `c(s, u) = 1000000`, `c(s, v) = 1000000`
- `c(u, v) = 1` (центральна перемичка)
- `c(u, t) = 1000000`, `c(v, t) = 1000000`

| Метод | Стратегія пошуку | Кількість ітерацій | Сумарний час |
|---|---|---|---|
| **Форд — Фалкерсон** | DFS (обирає шлях `s→u→v→t`) | **2 000 000** | ~850 мс |
| **Едмондс — Карп** | BFS (обирає найкоротші шляхи `s→u→t`, `s→v→t`) | **2** | < 0.01 мс |

## Оптимізація для розріджених графів: техніка масштабування (Capacity Scaling)
 
Хоча алгоритм Едмондса — Карпа має поліноміальну оцінку `O(V · E²)`, на великих мережах із високою розрідженістю та великим розкидом пропускних спроможностей пошук шляхів через звичайний BFS може виконувати багато дрібних аугментацій. 

Для прискорення роботи застосовується техніка масштабування пропускних спроможностей (Capacity Scaling):
- Вводиться порогова величина `Δ`, яка на старті дорівнює найбільшому ступеню двійки, що не перевищує максимальну місткість дуги: `Δ = 2^⌊log₂ U⌋`.
- На кожному кроці BFS розглядає лише ті дуги залишкової мережі, залишкова місткість яких `c_f(u, v) ≥ Δ`.
- Коли шляхів із залишком `≥ Δ` більше не залишається, поріг зменшується вдвічі: `Δ = Δ / 2`.
- Алгоритм завершує роботу після опрацювання порогу `Δ = 1`.

Масштабування скорочує кількість аугментацій до `O(E · log U)`, забезпечуючи час роботи `O(E² · log U)`. Це демонструє, як комбінація пошуку в ширину та контролю пляшкового горла перетворює теоретичний алгоритм на потужний інженерний інструмент.

