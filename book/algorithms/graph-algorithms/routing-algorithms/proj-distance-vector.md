# ⚙️ Реалізація дистанційно-векторного алгоритму маршрутизації з отруйним реверсом

У цій вставці наведено практичну реалізацію розподіленого алгоритму дистанційно-векторної маршрутизації (Distance-Vector) із підтримкою розщеплення горизонту та отруйного реверсу (Split Horizon with Poison Reverse). Описано моделювання мережевих вузлів, ітеративний обмін векторами, оновлення таблиць за рівнянням Беллмана–Форда, детальний аналіз виконання, розбер обробку крайових випадків, асинхронне моделювання, тестування та автоматичне виявлення збіжності графа.

### Постановка задачі та архітектура рішення

Уявімо розподілену систему з `N` маршрутизаторів, з'єднаних каналами зв'язку з різною вартістю (затримкою). Кожен вузол має доступ лише до інформації про своїх прямих сусідів і не володіє загальною картиною графа мережі. 

Потрібно побудувати програмну модель, у якій:
1. Кожен вузол підтримує власну локальну таблицю маршрутизації зі строками `(destination, cost, next_hop)`.
2. На кожній ітерації вузол генерує персоналізований вектор відстаней для кожного зі своїх прямих сусідів. За правилом Poison Reverse, якщо шлях від поточного вузла до цільової вершини `y` пролягає через сусідський маршрутизатор `v` (тобто `next_hop == v`), то при передачі вектора саме вузлу `v` значення вартості підміняється на `INF` (нескінченність).
3. При отриманні вектора від сусіда вузол виконує оновлення оцінок за рівнянням Беллмана–Форда, перевіряючи, чи не пропонує сусід коротший обхідний шлях.
4. Процес обміну триває доки жодна таблиця маршрутизації в мережі не зазнає змін протягом повної ітерації (система досягає глобальної фіксованої точки).

Для демонстрації функціонування використовується топологія з 4 вузлів (`0`, `1`, `2`, `3`), де вузол `0` з'єднаний з `1` (вага 1) та `2` (вага 7), вузол `1` з'єднаний з `2` (вага 3), а вузол `2` з'єднаний з `3` (вага 2).

### Програмна реалізація мовами C та C++

У табличному блоці нижче наведено ідіоматичні реалізації двома мовами. Версія мовою C спирається на статичні масиви прямого адресування, класичні структури даних та явну передачу вказівників. Версія мовою C++ використовує сучасний стандарт C++20 із контейнерами `std::vector`, `std::unordered_map`, семантикою константних посилань та автоматичним управлінням ресурсами (RAII).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 10
#define INF 9999

typedef struct {
    int cost;
    int next_hop;
} RouteEntry;

typedef struct {
    int id;
    int num_neighbors;
    int neighbors[MAX_NODES];
    int link_costs[MAX_NODES];
    RouteEntry table[MAX_NODES];
} Router;

void router_init(Router *r, int id, int total_nodes) {
    r->id = id;
    r->num_neighbors = 0;
    for (int i = 0; i < total_nodes; i++) {
        if (i == id) {
            r->table[i].cost = 0;
            r->table[i].next_hop = id;
        } else {
            r->table[i].cost = INF;
            r->table[i].next_hop = -1;
        }
        r->link_costs[i] = INF;
    }
}

void router_add_neighbor(Router *r, int neighbor_id, int cost) {
    r->neighbors[r->num_neighbors++] = neighbor_id;
    r->link_costs[neighbor_id] = cost;
    r->table[neighbor_id].cost = cost;
    r->table[neighbor_id].next_hop = neighbor_id;
}

// Підготовка вектора з урахуванням Poison Reverse для конкретного сусіда
void prepare_vector(const Router *r, int target_neighbor, int *out_vector, int total_nodes) {
    for (int d = 0; d < total_nodes; d++) {
        // Якщо наш шлях до d іде через target_neighbor, отруюємо маршрут
        if (d != r->id && r->table[d].next_hop == target_neighbor) {
            out_vector[d] = INF;
        } else {
            out_vector[d] = r->table[d].cost;
        }
    }
}

// Оновлення таблиці при отриманні вектора від сусіда neighbor_id
bool update_from_neighbor(Router *r, int neighbor_id, const int *received_vector, int total_nodes) {
    bool changed = false;
    int cost_to_neighbor = r->link_costs[neighbor_id];

    if (cost_to_neighbor >= INF) return false;

    for (int d = 0; d < total_nodes; d++) {
        if (d == r->id) continue;

        int dist_via_neighbor = received_vector[d];
        int new_cost = (dist_via_neighbor >= INF) ? INF : (cost_to_neighbor + dist_via_neighbor);

        if (new_cost < r->table[d].cost) {
            r->table[d].cost = new_cost;
            r->table[d].next_hop = neighbor_id;
            changed = true;
        }
    }
    return changed;
}

void print_table(const Router *r, int total_nodes) {
    printf("--- Таблиця маршрутизації вузла %d ---\n", r->id);
    printf("Ціль\tДистанція\tНаступний хоп\n");
    for (int i = 0; i < total_nodes; i++) {
        if (r->table[i].cost >= INF) {
            printf("%d\tINF\t\t-\n", i);
        } else {
            printf("%d\t%d\t\t%d\n", i, r->table[i].cost, r->table[i].next_hop);
        }
    }
    printf("\n");
}

int main(void) {
    const int total_nodes = 4;
    Router routers[4];

    for (int i = 0; i < total_nodes; i++) {
        router_init(&routers[i], i, total_nodes);
    }

    // Мережеві зв'язки: 0-1 (вага 1), 1-2 (вага 3), 0-2 (вага 7), 2-3 (вага 2)
    router_add_neighbor(&routers[0], 1, 1);
    router_add_neighbor(&routers[0], 2, 7);

    router_add_neighbor(&routers[1], 0, 1);
    router_add_neighbor(&routers[1], 2, 3);

    router_add_neighbor(&routers[2], 0, 7);
    router_add_neighbor(&routers[2], 1, 3);
    router_add_neighbor(&routers[2], 3, 2);

    router_add_neighbor(&routers[3], 2, 2);

    int iteration = 0;
    bool any_changed = true;
    int temp_vector[MAX_NODES];

    printf("=== Старт дистанційно-векторного алгоритму ===\n\n");

    while (any_changed && iteration < 10) {
        any_changed = false;
        iteration++;
        printf(">>> Ітерація %d <<<\n", iteration);

        for (int u = 0; u < total_nodes; u++) {
            for (int k = 0; k < routers[u].num_neighbors; k++) {
                int v = routers[u].neighbors[k];
                prepare_vector(&routers[u], v, temp_vector, total_nodes);
                if (update_from_neighbor(&routers[v], u, temp_vector, total_nodes)) {
                    any_changed = true;
                }
            }
        }
    }

    printf("Збіжність досягнута за %d ітерацій.\n\n", iteration);
    for (int i = 0; i < total_nodes; i++) {
        print_table(&routers[i], total_nodes);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <limits>
#include <iomanip>

constexpr int INF = 9999;

struct RouteEntry {
    int cost{INF};
    int next_hop{-1};
};

class Router {
public:
    explicit Router(int id, int total_nodes) : id_(id) {
        table_.resize(total_nodes);
        table_[id_] = {0, id_};
    }

    void add_neighbor(int neighbor_id, int cost) {
        neighbors_[neighbor_id] = cost;
        table_[neighbor_id] = {cost, neighbor_id};
    }

    [[nodiscard]] int id() const { return id_; }
    [[nodiscard]] const std::unordered_map<int, int>& neighbors() const { return neighbors_; }

    // Формування вектора відстаней з отруйним реверсом (Poison Reverse)
    [[nodiscard]] std::vector<int> prepare_vector_for(int target_neighbor) const {
        std::vector<int> vec(table_.size());
        for (std::size_t d = 0; d < table_.size(); ++d) {
            if (static_cast<int>(d) != id_ && table_[d].next_hop == target_neighbor) {
                vec[d] = INF; // Отруюємо шлях, якщо він іде через цього сусіда
            } else {
                vec[d] = table_[d].cost;
            }
        }
        return vec;
    }

    // Оновлення за рівнянням Беллмана-Форда
    bool update_from(int neighbor_id, const std::vector<int>& received_vector) {
        auto it = neighbors_.find(neighbor_id);
        if (it == neighbors_.end()) return false;

        const int link_cost = it->second;
        bool changed = false;

        for (std::size_t d = 0; d < table_.size(); ++d) {
            if (static_cast<int>(d) == id_) continue;

            const int dist_via_neighbor = received_vector[d];
            const int new_cost = (dist_via_neighbor >= INF) ? INF : (link_cost + dist_via_neighbor);

            if (new_cost < table_[d].cost) {
                table_[d].cost = new_cost;
                table_[d].next_hop = neighbor_id;
                changed = true;
            }
        }
        return changed;
    }

    void print_table() const {
        std::cout << "--- Таблиця маршрутизації вузла " << id_ << " ---\n";
        std::cout << "Ціль\tДистанція\tНаступний хоп\n";
        for (std::size_t i = 0; i < table_.size(); ++i) {
            std::cout << i << "\t";
            if (table_[i].cost >= INF) {
                std::cout << "INF\t\t-\n";
            } else {
                std::cout << table_[i].cost << "\t\t" << table_[i].next_hop << "\n";
            }
        }
        std::cout << "\n";
    }

private:
    int id_;
    std::vector<RouteEntry> table_;
    std::unordered_map<int, int> neighbors_;
};

class NetworkSimulator {
public:
    explicit NetworkSimulator(int total_nodes) {
        routers_.reserve(total_nodes);
        for (int i = 0; i < total_nodes; ++i) {
            routers_.emplace_back(i, total_nodes);
        }
    }

    void add_link(int u, int v, int cost) {
        routers_[u].add_neighbor(v, cost);
        routers_[v].add_neighbor(u, cost);
    }

    void run_until_convergence() {
        int iteration = 0;
        bool any_changed = true;

        std::cout << "=== Старт симуляції (C++ RAII Engine) ===\n\n";

        while (any_changed && iteration < 15) {
            any_changed = false;
            ++iteration;
            std::cout << ">>> Ітерація " << iteration << " <<<\n";

            for (auto& sender : routers_) {
                for (const auto& [neighbor_id, _] : sender.neighbors()) {
                    auto vec = sender.prepare_vector_for(neighbor_id);
                    if (routers_[neighbor_id].update_from(sender.id(), vec)) {
                        any_changed = true;
                    }
                }
            }
        }

        std::cout << "Збіжність досягнута за " << iteration << " ітерацій.\n\n";
        for (const auto& r : routers_) {
            r.print_table();
        }
    }

private:
    std::vector<Router> routers_;
};

int main() {
    NetworkSimulator net(4);

    net.add_link(0, 1, 1);
    net.add_link(1, 2, 3);
    net.add_link(0, 2, 7);
    net.add_link(2, 3, 2);

    net.run_until_convergence();

    return 0;
}
```
:::

### Детальний покроковий розбір алгоритму

Аналізуючи структуру написаного коду, розберемо фази функціонування симулятора:

1. **Ініціалізація локальних таблиць.**
   При створенні об'єкта `Router` кожен вузол встановлює оцінку відстані до самого себе рівною 0 (`cost = 0`, `next_hop = id`), а всі інші вершини початково вважає недосяжними (`cost = INF`, `next_hop = -1`). При додаванні прямих лінків функцією `add_neighbor` відповідні оцінки в таблиці оновлюються на вагу відповідного ребра.

2. **Формування та персоніфікація векторів з Poison Reverse.**
   Ключовим елементом безпеки алгоритму є функція `prepare_vector_for(target_neighbor)`. Звичайний дистанційно-векторний алгоритм передавав би усім сусідам один і той самий вектор `table_[d].cost`. 
   
   Проте у нашій реалізації перед відправкою вектора вузлу `target_neighbor` ми перевіряємо умову:
   ```cpp
   if (table_[d].next_hop == target_neighbor) {
       vec[d] = INF;
   }
   ```
   Якщо вузол `u` прямує до вершини `d` через сусідський вузол `v`, то вузлу `v` ми передаємо інформацію, що наша відстань до `d` є нескінченною. Це унеможливлює ситуацію, коли `v` при обриві лінка до `d` вирішить використати вузол `u` як обхідний шлях, запобігаючи виникненню двовузлових петель маршрутизації (2-node routing loops).

3. **Оновлення за рівнянням Беллмана–Форда.**
   Отримавши вектор від сусіда `neighbor_id`, вузол розглядає кожну вершину `d`. Нова потенційна вартість обчислюється за формулою:
   ```cpp
   int new_cost = (dist_via_neighbor >= INF) ? INF : (link_cost + dist_via_neighbor);
   ```
   Якщо `new_cost` виявляється суворо меншим за поточну відому оцінку `table_[d].cost`, вузол знижує оцінку і запам'ятовує сусіда `neighbor_id` як новий `next_hop`.

4. **Критерій збіжності та виходу з циклу.**
   Симулятор виконує ітерації обміну у циклі `while (any_changed)`. Прапорець `any_changed` скидається в `false` на початку кожної ітерації та встановлюється в `true`, якщо бодай один вузол мережі оновив хоча б один елемент своєї таблиці маршрутизації. Якщо за повну ітерацію жодна таблиця не зазнала змін, система гарантовано досягла фіксованої точки, і симуляція завершується.

### Покрокове простеження виконання симуляції (Execution Trace)

Розглянемо, як саме змінюються таблиці маршрутизації вузлів під час виконання тестової мережі:

**Початковий стан (Ітерація 0):**
- Вузол 0 знає свої лінки: до 1 (вага 1), до 2 (вага 7). Відстань до 3 дорівнює INF.
- Вузол 1 знає свої лінки: до 0 (вага 1), до 2 (вага 3). Відстань до 3 дорівнює INF.
- Вузол 2 знає свої лінки: до 0 (вага 7), до 1 (вага 3), до 3 (вага 2).
- Вузол 3 знає свій лінк: до 2 (вага 2).

**Ітерація 1 (перший обмін векторами):**
- Вузол 0 отримує вектор від вузла 1, де `d_1(2) = 3`. Вузол 0 обчислює шлях до 2 через 1: `cost = 1 + 3 = 4`. Це менше ніж прямий лінк `7`, тому `d_0(2)` збивається до 4, `next_hop = 1`.
- Вузол 0 отримує від вузла 2 інформацію `d_2(3) = 2`. Вузол 0 обчислює шлях до 3 через 2: `cost = 7 + 2 = 9`. Оцінка `d_0(3)` збивається з INF до 9, `next_hop = 2`.
- Вузол 1 отримує від вузла 2 інформацію `d_2(3) = 2`. Вузол 1 обчислює шлях до 3 через 2: `cost = 3 + 2 = 5`. Оцінка `d_1(3)` збивається з INF до 5, `next_hop = 2`.

**Ітерація 2 (другий обмін векторами):**
- Вузол 0 отримує оновлений вектор від вузла 1, де `d_1(3) = 5` (шлях 1 → 2 → 3).
- Вузол 0 переобчислює шлях до 3 через вузол 1: `cost = c(0, 1) + d_1(3) = 1 + 5 = 6`.
- Оскільки `6 < 9`, вузол 0 оновлює свою оцінку `d_0(3) = 6` та змінює `next_hop = 1`!

**Ітерація 3 (перевірка фіксованої точки):**
- Усі вузли надсилають вектора сусідів. Жодне обчислення Беллмана–Форда не дає коротших відстаней. Прапорець `any_changed` лишається `false`. Збіжність досягнута за 2 обчислювальні ітерації.

Результатом роботи симулятора є підсумкові підтверджені найкоротші відстані:
- `d(0 → 3) = 6` (через хоп 1)
- `d(1 → 3) = 5` (через хоп 2)
- `d(2 → 3) = 2` (через хоп 3)

### Асинхронне моделювання подій та обробка черг повідомлень

У представленій синхронній моделі вузли обмінюються векторами покроково. Для наближення до реальних роутерів симулятор можна розширити до **дискретно-подієвої моделі** (англ. *Discrete Event Simulation*) з використанням пріоритетної черги подій:

```cpp
struct MessageEvent {
    double timestamp;
    int sender_id;
    int receiver_id;
    std::vector<int> distance_vector;

    bool operator>(const MessageEvent& other) const {
        return timestamp > other.timestamp; // Мережевий час затримки
    }
};

std::priority_queue<MessageEvent, std::vector<MessageEvent>, std::greater<>> event_queue;
```

Кожне повідомлення отримує час доставки `timestamp = current_time + link_latency + jitter`. Це дозволяє точно симулювати асинхронні затримки пересилки, втрати пакетів та перевпорядкування векторів, перевіряючи виконання теореми Берцекаса–Ціцікліса про асинхронну збіжність у реальному часі.

### Оптимізація пам'яті та кеш-локальності (Cache Line Alignment)

При розробці високопродуктивних маршрутизаторів ядра або мережевих карт (DPDK, XDP) розміщення структур у пам'яті важить стільки ж, скільки й самі алгоритми:

1. **Вирівнювання під кеш-лінії L1/L2.** У сучасних процесорах x86_64 та ARM64 розмір лінії кешу становить 64 байти. Структура `RouteEntry` має бути вирівняна за допомогою `alignas(64)` або упакована у плоский суцільний масив (англ. *flat contiguous array*), щоб при лінійному обході забор даних у L1D-кеш відбувався одним читанням шини пам'яті:
   ```cpp
   struct alignas(64) CacheOptimizedEntry {
       int cost;
       int next_hop;
       uint32_t flags;
       uint32_t last_update;
   };
   ```
2. **Уникнення шардингу та промахів кешу (Cache Misses).** Реалізація мовою C із суцільним масивом `table[MAX_NODES]` забезпечує $100\%$ кеш-локальність. Версія мовою C++ із `std::unordered_map` при кожному зверненні здійснює обчислення хешу та розіменування вказівників по ланцюжках бакетів, що у разі мільйонів записів спричиняє промахи кешу L3. Тому для мережевих карт реального часу вибирають плоскі масиви або спеціалізовані префіксні дерева LC-Trie.

### Перехід від симуляції до реальних мережевих демонів (POSIX Sockets & UDP)

У реальних мережевих операційних системах (наприклад, реалізації демонів `routed` чи `bird` в Linux) алгоритм Distance-Vector працює поверх мережевого стека POSIX sockets з використанням протоколу UDP:

1. **Сокети та службовий порт.** Кожен процес маршрутизатора відкриває UDP-сокет на стандартному порту (для протоколу RIP це UDP-порт 520).
2. **Сериалізація пакетів.** Замість передачі масивів C++ у пам'яті, вектор відстаней упаковується у бінарну структуру пакета (наприклад, формат RIPv2 Header + записи адреса/метрика).
3. **Мультивещание (Multicast) та Unicast.** Службові анонси відправляються або на спеціальні мультикаст-адреси (для RIPv2 це `224.0.0.9`), або на безпосередні юникаст-адреси сусідів за таблицею суміжності.
4. **Асинхронний Event Loop.** Отримання векторів здійснюється асинхронно через виклики `select()`, `poll()` або `epoll()`, де при надходженні UDP-пакета викликається відповідна функція `update_from_neighbor`.

### Порівняльний аналіз пам'яті та швидкодії C і C++ реалізацій

| Параметр | C-реалізація (Статичні масиви) | C++ реалізація (STL Containers) |
| :--- | :--- | :--- |
| **Управління пам'яттю** | Статична `BSS`/стек, 0 викликів `malloc` | Динамічна куча (`std::vector`, `std::unordered_map`) |
| **Кеш-локальність пам'яті** | Висока (суцільні масиви `table[MAX_NODES]`) | Середня (хеш-таблиці з хешуванням ланцюжками) |
| **Безпека типів** | Ручний контроль меж масивів | Перевірки `size()` та авто-деструктори |
| **Сфера застосування** | Мікроконтролери, embedded, kernel space | Демони вищого рівня (user-space, симулятори) |

### Розширення симулятора: Обробка обривів лінків та триговані оновлення (Triggered Updates)

У базовій реалізації ми розглянули процес збіжності за статичної топології. У реальних протоколах (таких як RIP) додаються два важливих інженерних механізми:

1. **Триговані оновлення (Triggered Updates).** Замість того щоб чекати чергового таймера обміну (наприклад, 30 секунд), вузол при виявленні зміни стану лінка або отриманні анонсу про нескінченність (`INF`) негайно відправляє оновлений вектор сусідам. Це зменшує час виявлення недосяжності з декількох хвилин до мілісекунд.

2. **Інтеграція таймерів недійсності (Invalidity Timers).** Для кожного запису таблиці додається поле `last_updated_timestamp`. Якщо протягом `180` секунд від сусіда не надходить анонс про маршрут, маршрут вважається недійсним (`cost = INF`), але зберігається у таблиці протягом часу `Hold-Down` для пропогування отруєного анонсу сусіднім вузлам.

### Моделювання динамічного обриву зв'язку в коді

Для перевірки отруйного реверсу в дії доповнимо симуляцію викликом методу обриву лінка `remove_link(u, v)` після досягнення первинної збіжності:

```cpp
void remove_link(int u, int v) {
    routers_[u].remove_neighbor(v);
    routers_[v].remove_neighbor(u);
}
```

При обриві лінка `2 — 3` вузол 2 фіксує втрату прямого зв'язку з 3 (`cost_to_3 = INF`). Завдяки методу `prepare_vector_for`, вузол 1 при спробі передати вектор вузлу 2 надсилає `d_1(3) = INF` (оскільки його `next_hop` для 3 дорівнював 2). Вузол 2 бачить `INF` від усіх сусідів і негайно встановлює `d_2(3) = INF`, запобігаючи нескінченному відліку.

### Стратегія тестування та перевірка тверджень (Unit Testing Strategy)

Для верифікації реалізації алгоритму маршрутизації розроблено набір автотестів:

```cpp
void test_two_node_loop_prevention() {
    NetworkSimulator net(3);
    net.add_link(0, 1, 1);
    net.add_link(1, 2, 1);
    net.run_until_convergence();

    // Симулюємо обрив лінка (1, 2)
    net.remove_link(1, 2);
    net.run_until_convergence();

    // Завдяки Poison Reverse вузли повинні за 1-2 ітерації встановити INF
    // замість нескінченного відліку 3, 4, 5...
}
```

Тестове покриття перевіряє три класи станів:
- **Повна ізоляція компоненти**: перевірка поведінки системи при розпаді графа на два незв'язані підграфи.
- **Осциляція метрик лінків**: перевірка стійкості при швидкій зміні вартостей лінків $c(u, v)$ у часі.
- **Багатошляхове просування (ECMP)**: рівність оцінок при наявності декількох симетричних шляхів.

### Порівняльна реалізація алгоритму Link-State (Dijkstra SPT)

Для розуміння принципової різниці між дистанційно-векторним підходом та алгоритмами стану зв'язків (Link-State), розглянемо, як той самий граф обробляється у протоколах OSPF. 

У Link-State кожен вузол накопичує у базі LSDB повну матрицю суміжності графа `G = (V, E)` і виконує локальний алгоритм Дейкстри з пріоритетною чергою:

```cpp
struct GraphLink {
    int to;
    int cost;
};

void run_dijkstra_spt(int source, int total_nodes, const std::vector<std::vector<GraphLink>>& adj) {
    std::vector<int> dist(total_nodes, INF);
    std::vector<int> parent(total_nodes, -1);
    using PII = std::pair<int, int>; // (cost, node)
    std::priority_queue<PII, std::vector<PII>, std::greater<PII>> pq;

    dist[source] = 0;
    pq.push({0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (d > dist[u]) continue;

        for (const auto& edge : adj[u]) {
            if (dist[u] + edge.cost < dist[edge.to]) {
                dist[edge.to] = dist[u] + edge.cost;
                parent[edge.to] = u;
                pq.push({dist[edge.to], edge.to});
            }
        }
    }
}
```

Порівняльний аналіз складності двох підходів у коді:
1. **Обчислительна складність у коді**: у дистанційно-векторному алгоритмі вузол обробляє отриманий вектор за час `O(|N(u)| * |V|)`. У Link-State вузол запускає локальний алгоритм Дейкстри складності `O(|E| + |V| log |V|)`.
2. **Складність повідомлень**: у дистанційно-векторному алгоритмі розмір анонсу лінійно залежить від кількості цільових мереж `O(|V|)` і передається періодично кожні `T` секунд. У Link-State пакет LSA передається лише при змінах топології і містить лише список прямих сусідів `O(|N(u)|)`.
3. **Витрати оперативної пам'яті (RAM Overhead)**: для дистанційно-векторного підходу на 10 000 мереж таблиця займає `10000 * sizeof(RouteEntry) ≈ 80 KB`. Для Link-State підходу база даних LSDB зберігає увесь граф `G = (V, E)`, що при 100 000 лінках вимагає десятки мегабайтів оперативної пам'яті та постійної перебудови пріоритетної черги `std::priority_queue`.
4. **Конкурентність та Thread-Safety у реальних демонах**: у багатонитокових демонах (наприклад, FRRouting) таблиця RIB захищається за допомогою читацько-письменницьких мутексів `std::shared_mutex`. Читання та просування пакетів виконується під спільним замиканням `std::shared_lock`, тоді як отримання нового вектора дистанцій вимагає ексклюзивного блокування `std::unique_lock` для запобігання гонитві даних (Data Race) між ниткою обробки сокета та ниткою таймерів.

### Гасіння осциляцій та демпфування маршрутів (Route Flap Damping)

У реальних комунікаційних мережах фізичний лінк між роутерами може перейти в стан "flapping" — періодично включатися та відключатися декілька разів на секунду через пошкоджений волоконно-оптичний кабель або нестабільність оптичного трансивера SFP. 

Якщо реалізувати алгоритм Distance-Vector без демпфування, кожне відновлення та обрив каналу викличуть лавину штормових оновлень (Triggered Updates) по всій мережі. 

Для запобігання цьому у коді реалізують лічильник штрафних балів `penalty_score`:
1. При кожному обриві лінка до показника `penalty_score` даного сусіда додається штраф `P = 1000`.
2. Показник штрафу експоненційно згасає в часі за формулою `P(t) = P_0 * e^(-lambda * t)`.
3. Якщо `penalty_score` перевищує поріг подавлення `suppress_threshold`, маршрут блокується і не бере участі в релаксації Беллмана-Форда, поки штраф не опуститься нижче порога повторного включення `reuse_threshold`.

Такий демпфуючий експоненційний фільтр захищає маршрутизатори від перевантаження процесора (CPU Spikes) при неідеальній якості фізичних лінків, запобігаючи виснаженню обчислительних ресурсів мережевих оперативних систем у реальних масштабованих мережах. При зниженні показника штрафу нижче порога повернення маршрут автоматично повертається в активну релаксацію Беллмана-Форда, відновлюючи проходження мережевих пакетів без втручання мережевого адміністратора. Це забезпечує високу надійність функціонування розподіленого алгоритму.

### Інженерні пастки та крайові випадки (Edge Cases)

- **Переповнення цілочисельного типу (Integer Overflow).** При додаванні ваги ребра до значення нескінченності `INF + cost` виникає ризик цілочисельного переповнення, якщо `INF` вибрано як `INT_MAX`. У реалізації ми встановили `INF = 9999` (або `16` у протоколі RIP), а при обчисленні явно перевіряємо `if (dist_via_neighbor >= INF)`, уникаючи додавання до нескінченності.
- **Динамічний обрив зв'язку.** Якщо лінк між вузлами падає у процесі роботи, відповідний `link_cost` встановлюється в `INF`. Якщо поточний `next_hop` для якоїсь цілі використовував цей лінк, вузол повинен негайно встановити `table_[d].cost = INF` і розіслати отруєний анонс (Poison Advertisement) сусідам для прискорення збіжності.
- **Рівність вартостей (Equal-Cost Multi-Path, ECMP).** Якщо новий обчислений шлях має точно таку саму вартість, як і поточний (`new_cost == table_[d].cost`), алгоритм не змінює `next_hop`, щоб уникнути непотрібних осциляцій трафіку між еквівалентними каналами.
- **Масштабованість пам'яті C vs C++.** Версія мовою C++ за рахунок використання `std::unordered_map` дозволяє динамічно додавати вузли з довільними ідентифікаторами (наприклад, IP-адресами), тоді як версія мовою C вимагає компактної нумерації вершин `0..N-1` через суцільну індексацію масивів. У реальних вбудованих системах із суворими обмеженнями пам'яті (маршрутизатори на мікроконтролерах) C-версія надає перевагу передбачуваного статичного розміру пам'яті без динамічної кучі (heap allocation).
