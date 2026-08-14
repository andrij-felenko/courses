# ⚙️ Алгоритм зворотного тиску: Backpressure Routing у C та C++

Алгоритм зворотного тиску (Backpressure Routing), розроблений Лентісом Тассіуласом та Ентоні Ефімідесом у 1992 році, є алгоритмом динамічної маршрутизації та планування у мережевих графах. Замість обчислення статичних шляхів за допомогою алгоритмів найкоротших шляхів (таких як алгоритм Дейкстри або Bellman-Ford), Backpressure приймає рішення про пересилку кожного пакету на кожному кроці часу спираючись виключно на **різницю довжин черг** між сусідніми вузлами.

Головна теоретична перевага алгоритму — доведена максимальна стійкість (Throughput-Optimal): він гарантує обмеженість черг для будь-яких вхідних інтенсивностей трафіку, які взагалі можливо обслугувати даною мережею, без необхідності знати матрицю навантаження заздалегідь.

---

## 1. Теоретичні основи та стійкість за Ляпуновим

Розглянемо мережевий граф `G = (V, E)` із множиною вузлів `V` та орієнтованих ребер `E`. Нехай `C` позначає множину товарів (призначень). Кожен вузол `u ∈ V` підтримує окрему буферну чергу `Q[u][c](t)` для кожного призначення `c ∈ C` у момент часу `t`.

Для аналізу стійкості мережі використовується квадратна функція Ляпунова, яка вимірює сумарний "гравітаційний потенціал" незавершеної роботи у всіх чергах графа:

```
L(Q(t)) = 1/2 · ∑_{u ∈ V} ∑_{c ∈ C} ( Q[u][c](t) )²
```

Однокроковий зсув Ляпунова (Lyapunov Drift) визначається як зміна потенціалу між послідовними тактами часу:

```
ΔL(t) = L(Q(t + 1)) - L(Q(t))
```

Алгоритм Backpressure на кожному такті `t` приймає такі рішення про керування ребрами `(u, v) ∈ E`, які **мінімізують верхню межу зсуву Ляпунова `ΔL(t)`**.

Мінімізація зсуву зводиться до максимізації сумарного розрахункового важеля (Backpressure Weight) по всіх ребрах графа:

```
W[u][v][c](t) = Q[u][c](t) - Q[v][c](t)
```

Для кожного ребра `(u, v)` обирається той товар `c*`, який забезпечує найвищий перепад тиску:

```
c* = argmax_{c ∈ C} W[u][v][c](t)
```

Якщо `W[u][v][c*](t) > 0`, ребро `(u, v)` активується для передачі пакетів товару `c*` у обсязі до його максимальної ємності `Capacity(u, v)`. Якщо перепад тиску від'ємний або дорівнює нулю (`W ≤ 0`), передача через ребро не виконується, що запобігає затисканню трафіку у зворотний бік.

---

## 2. Покроковий алгоритм функціонування

На кожному часовому такті `t` система виконує чотири послідовні фази:

1. **Фаза спостереження:** кожен вузол `u` зчитує поточні довжини своїх черг `Q[u][c]` та обмінюється цими значеннями зі своїми безпосередніми сусідами `v ∈ Neighbor(u)`.
2. **Фаза вибору товарів (Commodity Selection):** для кожного орієнтованого ребра `(u, v)` шукається товар `c* = argmax_{c} (Q[u][c] - Q[v][c])`.
3. **Фаза передачі даних (Transmission Phase):** для кожного ребра з `W[u][v][c*] > 0` з черги `Q[u][c*]` вилучається `N = min(Q[u][c*], Capacity(u, v))` пакетів, які передаються у вузол `v`.
4. **Фаза оновлення та поглинання (Queue Update & Sink):**
   - У вузлах-отримувачах (`u == c`) пакети вважаються доставленими і видаляються з черги (`Q[c][c] := 0`).
   - У проміжних вузлах переслані пакети додаються до відповідних черг `Q[v][c*] := Q[v][c*] + N`.

---

## 3. Реалізація симулятора Backpressure у коді (C та C++)

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 10
#define MAX_COMMODITIES 5

typedef struct {
    int u;
    int v;
    int capacity;
} Edge;

typedef struct {
    int num_nodes;
    int num_edges;
    int num_commodities;
    Edge edges[20];
    int queue[MAX_NODES][MAX_COMMODITIES];
} Network;

void network_init(Network *net, int n, int num_comm) {
    net->num_nodes = n;
    net->num_edges = 0;
    net->num_commodities = num_comm;
    for (int i = 0; i < n; i++) {
        for (int c = 0; c < num_comm; c++) {
            net->queue[i][c] = 0;
        }
    }
}

void network_add_edge(Network *net, int u, int v, int cap) {
    net->edges[net->num_edges].u = u;
    net->edges[net->num_edges].v = v;
    net->edges[net->num_edges].capacity = cap;
    net->num_edges++;
}

void backpressure_step(Network *net) {
    // Тимчасовий масив для накопичення змін черг за один крок
    int delta[MAX_NODES][MAX_COMMODITIES] = {0};

    for (int e = 0; e < net->num_edges; e++) {
        int u = net->edges[e].u;
        int v = net->edges[e].v;
        int cap = net->edges[e].capacity;

        int max_weight = 0;
        int best_commodity = -1;

        // Пошук товару з максимальним різницевим тиском
        for (int c = 0; c < net->num_commodities; c++) {
            int weight = net->queue[u][c] - net->queue[v][c];
            if (weight > max_weight) {
                max_weight = weight;
                best_commodity = c;
            }
        }

        // Якщо є позитивний тиск, виконуємо передачу
        if (best_commodity != -1 && max_weight > 0) {
            int packets_to_send = net->queue[u][best_commodity];
            if (packets_to_send > cap) {
                packets_to_send = cap;
            }

            delta[u][best_commodity] -= packets_to_send;
            delta[v][best_commodity] += packets_to_send;

            printf("  Ребро (%d->%d): переслано %d пакетів товару %d (тиск = %d)\n",
                   u, v, packets_to_send, best_commodity, max_weight);
        }
    }

    // Оновлюємо стан черг
    for (int i = 0; i < net->num_nodes; i++) {
        for (int c = 0; c < net->num_commodities; c++) {
            net->queue[i][c] += delta[i][c];
            // Списання пакетів при досягненні вузла-призначення
            if (i == c) {
                net->queue[i][c] = 0;
            }
        }
    }
}

int main(void) {
    Network net;
    network_init(&net, 4, 2);

    // Додаємо орієнтовані ребра з ємностями
    network_add_edge(&net, 0, 1, 5);
    network_add_edge(&net, 0, 2, 5);
    network_add_edge(&net, 1, 3, 4);
    network_add_edge(&net, 2, 3, 4);

    // Початкове заповнення черг трафіком
    net.queue[0][3] = 20; // 20 пакетів у вузлі 0 із призначенням у вузол 3

    printf("=== Початковий стан черги у вузлі 0: %d ===\n", net.queue[0][3]);

    for (int t = 1; t <= 4; t++) {
        printf("\nТакт %d:\n", t);
        backpressure_step(&net);
        printf("Стан черг: Node 0=%d, Node 1=%d, Node 2=%d, Node 3=%d\n",
               net.queue[0][3], net.queue[1][3], net.queue[2][3], net.queue[3][3]);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>

struct Edge {
    int u;
    int v;
    int capacity;
};

class BackpressureNetwork {
private:
    int num_nodes_;
    int num_commodities_;
    std::vector<Edge> edges_;
    std::vector<std::vector<int>> queue_;

public:
    BackpressureNetwork(int n, int num_comm)
        : num_nodes_(n), num_commodities_(num_comm),
          queue_(n, std::vector<int>(num_comm, 0)) {}

    void add_edge(int u, int v, int cap) {
        edges_.push_back({u, v, cap});
    }

    void set_queue(int node, int commodity, int count) {
        queue_[node][commodity] = count;
    }

    int get_queue(int node, int commodity) const {
        return queue_[node][commodity];
    }

    void step() {
        std::vector<std::vector<int>> delta(num_nodes_, std::vector<int>(num_commodities_, 0));

        for (const auto& edge : edges_) {
            int u = edge.u;
            int v = edge.v;
            int cap = edge.capacity;

            int max_weight = 0;
            int best_commodity = -1;

            for (int c = 0; c < num_commodities_; ++c) {
                int weight = queue_[u][c] - queue_[v][c];
                if (weight > max_weight) {
                    max_weight = weight;
                    best_commodity = c;
                }
            }

            if (best_commodity != -1 && max_weight > 0) {
                int packets = std::min(queue_[u][best_commodity], cap);
                delta[u][best_commodity] -= packets;
                delta[v][best_commodity] += packets;

                std::cout << "  Ребро (" << u << "->" << v << "): переслано "
                          << packets << " пакетів товару " << best_commodity
                          << " (тиск = " << max_weight << ")\n";
            }
        }

        for (int i = 0; i < num_nodes_; ++i) {
            for (int c = 0; c < num_commodities_; ++c) {
                queue_[i][c] += delta[i][c];
                if (i == c) {
                    queue_[i][c] = 0; // Поглинання в точці призначення
                }
            }
        }
    }
};

int main() {
    BackpressureNetwork net(4, 2);

    net.add_edge(0, 1, 5);
    net.add_edge(0, 2, 5);
    net.add_edge(1, 3, 4);
    net.add_edge(2, 3, 4);

    net.set_queue(0, 3, 20);

    std::cout << "=== Початковий стан черги у вузлі 0: " << net.get_queue(0, 3) << " ===\n";

    for (int t = 1; t <= 4; ++t) {
        std::cout << "\nТакт " << t << ":\n";
        net.step();
        std::cout << "Стан черг: Node 0=" << net.get_queue(0, 3)
                  << ", Node 1=" << net.get_queue(1, 3)
                  << ", Node 2=" << net.get_queue(2, 3)
                  << ", Node 3=" << net.get_queue(3, 3) << "\n";
    }

    return 0;
}
```
:::

---

## 4. Складність та інженерні крайові випадки

### Оцінка алгоритмічної складності

- **Часова складність одного такту:** `O(|E| · |C|)`, оскільки для кожного з `|E|` ребер виконується перебір `|C|` товарних позицій для знаходження `argmax W[u][v][c]`. У великих мережах із тисячами призначень застосовують модифікацію Enhanced Backpressure (E-BP), яка обмежує вибір лише дійсними кандидатами за кратними найкоротшими шляхами, знижуючи складність до `O(|E| · K)`.
- **Просторова складність:** `O(|V| · |C|)` пам'яті для зберігання вектора черг у кожному вузлі.

### Крайові випадки та недоліки чистої схеми Backpressure

1. **Великі початкові затримки при малій кількості даних (Last-Packet Delay Problem):** оскільки передача вимагає позитивного перепаду тиску `Q[u] - Q[v] > 0`, поодинокий пакет у порожній мережі не може просунутися далі першого вузла, поки позаду нього не накопичиться достатня кількість інших пакетів для створення "тиску".
   *Рішення:* застосування гібридного алгоритму **Drift-Plus-Penalty / Enhanced Backpressure**, який додає до важеля `W[u][v][c]` від'ємний штраф, пропорційний найкоротшій відстані від `v` до призначення `c` (Shortest-Path Bias).
2. **Циклічні зациклення трафіку (Random Walk in Equal Queues):** якщо декілька сусідніх вузлів мають однакові довжини черг, пакети можуть блукати між ними туди-сюди без наближення до мети.
3. **Обмеженість буферної пам'яті (Finite Buffer Drops):** класична теорія вважає буфери нескінченними. При фіксованих буферах `Q_max` переповнення викликає відкидання пакетів, що вимагає комбінації Backpressure із локальним Hop-by-Hop Flow Control.

---

## 5. Оптимізація Drift-Plus-Penalty (Неперервний компроміс затримка-корисність)

Розширення Майкла Нілі (Michael J. Neely, 2010) додає до зсуву Ляпунова штрафну функцію видатків (або корисність) з ваговим коефіцієнтом `V > 0`:

```
  Мінімізувати:  ΔL(t) - V · ∑_{i} U[i](x[i](t))
```

Параметр `V` забезпечує строгий компроміс `[O(1/V), O(V)]`:
- Середня затримка в чергах масштабується як `O(V)`.
- Відхилення досягнутої пропускної здатності від абсолютного теоретичного максимуму становить `O(1/V)`.

При `V → ∞` алгоритм досягає 100% максимальної ємності мережевого графа за рахунок лінійного зростання середньої затримки пакета у чергах. При `V → 0` алгоритм перетворюється на мінімізатор затримки (маршрутизація найкоротшими шляхами).

---

## 6. Практичне застосування: Програмно-конфігуровані мережі (SDN/P4) та бездротові сенсори

У сучасних програмно-конфігурованих мережах (SDN) та програмних комутаторах з мовою P4 алгоритми Backpressure реалізуються через механізм програмних віртуальних черг (Shadow Queues):
- Апаратні комутаційні фабрики не зберігають тисячі фізичних черг для кожного можливого IP-призначення, а підтримують віртуальні масиви лічильників.
- Контролер SDN кожні `N` мікросекунд опитує лічильники за допомогою протоколу OpenFlow та диференційно оновлює таблиці маршрутизації (Flow Tables), перенаправляючи підпотоки на найменш завантажені ребра графа.
- У бездротових сенсорних мережах (Wireless Sensor Networks) та Ad-Hoc мережах (MANET) Backpressure забезпечує динамічне обходження завад та "мертвих" вузлів без необхідності перебудови глобального графа маршрутизації.
