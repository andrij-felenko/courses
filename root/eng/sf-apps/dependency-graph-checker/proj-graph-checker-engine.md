# ⚙️ Реалізація рушія перевірки графа залежностей: Tarjan SCC та валідація шарів

Рушій статичного аналізу графа залежностей є ключовим інструментом автоматизованого контролю архітектурної дисципліни. Його призначення полягає в перетворенні сирого коду або конфігурацій викликів на математичну модель орієнтованого графа та валідації двох фундаментальних інваріантів:
1. **Виявлення циклічних залежностей:** знаходження всіх сильно зв'язаних компонентів (SCC) розміром більше одиниці за алгоритмом Тар'яна за лінійний час `O(|V| + |E|)`;
2. **Валідація шарової дисципліни:** перевірка спрямованості ребер графа між шарами відповідно до заданої конфігурації рівнів та виявлення несанкціонованих прямих зчеплень і зворотних викликів.

Нижче детально розібрано внутрішню архітектуру такого рушія, наведено компільовані реалізації мовами C та сучасного C++, а також описано механіку обходу та аналізу крайових випадків.

## Архітектура представлення графа в пам'яті

Для ефективного аналізу кодових баз, що містять десятки тисяч модулів і сотні тисяч зв'язків між ними, вибір структури даних є критичним для швидкодії:
- **Матриця суміжності `A[N][N]`** вимагає `O(|V|²)` пам'яті. У реальних системах граф залежностей є сильно розрідженим (кожен модуль зазвичай імпортує від 5 до 30 сусідів, тому середня густина графа рідко перевищує 1-2%). Використання квадратної матриці призводить до неефективного використання кешу процесора та сповільнює обхід;
- **Списки суміжності (Adjacency Lists)** зберігають лише фактично наявні ребра, забезпечуючи компактність у пам'яті `O(|V| + |E|)` та швидкий ітераційний перебір вихідних зв'язків для кожної вершини.

У наведених нижче реалізаціях використовується структура з прямим мапуванням ідентифікаторів вузлів та компактним представленням суміжних вершин.

## Повна програмна реалізація рушія

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NODES 128
#define MAX_NAME 64

typedef struct {
    char name[MAX_NAME];
    int layer;         /* Індекс шару: 0 - Infra, 1 - Domain, 2 - App, 3 - Presentation */
    int context_id;    /* Ідентифікатор обмеженого контексту (Bounded Context) */
} NodeMeta;

typedef struct {
    int to;
    int next;
} Edge;

typedef struct {
    NodeMeta nodes[MAX_NODES];
    int head[MAX_NODES];
    Edge edges[MAX_NODES * MAX_NODES];
    int node_count;
    int edge_count;
} Graph;

/* Ініціалізація графа */
void graph_init(Graph *g) {
    g->node_count = 0;
    g->edge_count = 0;
    for (int i = 0; i < MAX_NODES; ++i) {
        g->head[i] = -1;
    }
}

/* Додавання або отримання існуючого вузла за унікальним іменем */
int graph_add_node(Graph *g, const char *name, int layer, int context_id) {
    for (int i = 0; i < g->node_count; ++i) {
        if (strcmp(g->nodes[i].name, name) == 0) {
            return i;
        }
    }
    if (g->node_count >= MAX_NODES) {
        fprintf(stderr, "Помилка: перевищено ліміт вузлів (%d)\n", MAX_NODES);
        exit(1);
    }
    int id = g->node_count++;
    strncpy(g->nodes[id].name, name, MAX_NAME - 1);
    g->nodes[id].name[MAX_NAME - 1] = '\0';
    g->nodes[id].layer = layer;
    g->nodes[id].context_id = context_id;
    return id;
}

/* Додавання орієнтованого ребра залежності from -> to */
void graph_add_edge(Graph *g, int from, int to) {
    int e = g->edge_count++;
    g->edges[e].to = to;
    g->edges[e].next = g->head[from];
    g->head[from] = e;
}

/* Стан виконання алгоритму Тар'яна */
typedef struct {
    int dfn[MAX_NODES];
    int low[MAX_NODES];
    bool in_stack[MAX_NODES];
    int stack[MAX_NODES];
    int top;
    int timer;
    int cycle_count;
} TarjanState;

static int min_val(int a, int b) {
    return a < b ? a : b;
}

static void tarjan_dfs(Graph *g, TarjanState *st, int u) {
    st->dfn[u] = st->low[u] = ++st->timer;
    st->stack[++st->top] = u;
    st->in_stack[u] = true;

    for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
        int v = g->edges[e].to;
        if (st->dfn[v] == 0) {
            /* Пряме ребро дерева пошуку (Tree Edge) */
            tarjan_dfs(g, st, v);
            st->low[u] = min_val(st->low[u], st->low[v]);
        } else if (st->in_stack[v]) {
            /* Зворотне ребро до предка в поточному стеку (Back Edge) */
            st->low[u] = min_val(st->low[u], st->dfn[v]);
        }
    }

    /* Якщо знайдено корінь сильно зв'язаної компоненти */
    if (st->low[u] == st->dfn[u]) {
        int scc_members[MAX_NODES];
        int count = 0;
        while (st->top >= 0) {
            int node = st->stack[st->top--];
            st->in_stack[node] = false;
            scc_members[count++] = node;
            if (node == u) break;
        }

        /* Якщо в компоненті більше 1 вузла — це циклічна ерозія */
        if (count > 1) {
            st->cycle_count++;
            printf("[ПОМИЛКА: ЦИКЛ #%d] Сильно зв'язана компонента (%d вузлів):\n  ", 
                   st->cycle_count, count);
            for (int i = 0; i < count; ++i) {
                printf("%s%s", g->nodes[scc_members[i]].name, 
                       (i + 1 < count) ? " <-> " : "\n");
            }
        }
    }
}

/* Пошук усіх циклів у графі */
int check_cycles(Graph *g) {
    TarjanState st;
    memset(&st, 0, sizeof(TarjanState));

    for (int i = 0; i < g->node_count; ++i) {
        if (st.dfn[i] == 0) {
            tarjan_dfs(g, &st, i);
        }
    }
    return st.cycle_count;
}

/* Перевірка шарових обмежень: вищий шар не може залежати від вищого за себе */
int check_layer_violations(Graph *g) {
    int violations = 0;
    for (int u = 0; u < g->node_count; ++u) {
        for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
            int v = g->edges[e].to;
            /* Правило: шар u не може залежати від v, якщо layer(u) < layer(v) (зворотний виклик) */
            if (g->nodes[u].layer < g->nodes[v].layer) {
                violations++;
                printf("[ПОМИЛКА: ШАР] Зворотна залежність: %s (шар %d) -> %s (шар %d)\n",
                       g->nodes[u].name, g->nodes[u].layer,
                       g->nodes[v].name, g->nodes[v].layer);
            }
        }
    }
    return violations;
}

int main(void) {
    Graph g;
    graph_init(&g);

    /* Створення вузлів системи (Layer: 0-Infra, 1-Domain, 2-App, 3-Presentation) */
    int api   = graph_add_node(&g, "Presentation.HttpApi", 3, 1);
    int order = graph_add_node(&g, "Application.OrderService", 2, 1);
    int core  = graph_add_node(&g, "Domain.OrderCore", 1, 1);
    int repo  = graph_add_node(&g, "Infrastructure.PostgresRepo", 0, 1);
    int bill  = graph_add_node(&g, "Application.BillingService", 2, 2);

    /* Дозволені залежності */
    graph_add_edge(&g, api, order);
    graph_add_edge(&g, order, core);
    graph_add_edge(&g, order, repo);

    /* Порушення 1: Зворотна залежність Domain -> Infrastructure (DIP) */
    graph_add_edge(&g, core, repo);

    /* Порушення 2: Цикл між сервісами OrderService <-> BillingService */
    graph_add_edge(&g, order, bill);
    graph_add_edge(&g, bill, order);

    printf("=== СТАТИЧНИЙ АНАЛІЗ АРХІТЕКТУРНИХ ЗАЛЕЖНОСТЕЙ (C) ===\n");
    int cycles = check_cycles(&g);
    int layer_errs = check_layer_violations(&g);

    printf("\nПідсумок: виявлено %d циклів та %d шарових порушень.\n", cycles, layer_errs);
    return (cycles + layer_errs > 0) ? 1 : 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <stack>
#include <algorithm>
#include <string_view>
#include <span>

enum class Layer {
    Infrastructure = 0,
    Domain = 1,
    Application = 2,
    Presentation = 3
};

struct Node {
    std::string name;
    Layer layer;
    int context_id;
};

class DependencyGraphChecker {
public:
    int add_node(std::string name, Layer layer, int context_id) {
        if (auto it = name_to_id_.find(name); it != name_to_id_.end()) {
            return it->second;
        }
        int id = static_cast<int>(nodes_.size());
        name_to_id_[name] = id;
        nodes_.push_back(Node{std::move(name), layer, context_id});
        adj_.emplace_back();
        return id;
    }

    void add_dependency(int from, int to) {
        adj_[from].push_back(to);
    }

    struct AnalysisReport {
        std::vector<std::vector<std::string>> cycles;
        std::vector<std::string> layer_violations;
        bool has_violations() const { return !cycles.empty() || !layer_violations.empty(); }
    };

    AnalysisReport analyze() const {
        AnalysisReport report;
        find_cycles(report);
        check_layers(report);
        return report;
    }

private:
    std::vector<Node> nodes_;
    std::unordered_map<std::string, int> name_to_id_;
    std::vector<std::vector<int>> adj_;

    void find_cycles(AnalysisReport& report) const {
        int n = static_cast<int>(nodes_.size());
        std::vector<int> dfn(n, 0);
        std::vector<int> low(n, 0);
        std::vector<bool> in_stack(n, false);
        std::stack<int> st;
        int timer = 0;

        auto tarjan_dfs = [&](auto& self, int u) -> void {
            dfn[u] = low[u] = ++timer;
            st.push(u);
            in_stack[u] = true;

            for (int v : adj_[u]) {
                if (dfn[v] == 0) {
                    /* Пряме дерево обходу DFS */
                    self(self, v);
                    low[u] = std::min(low[u], low[v]);
                } else if (in_stack[v]) {
                    /* Зворотне ребро у вершину, активну в стеку */
                    low[u] = std::min(low[u], dfn[v]);
                }
            }

            /* Вершина u є коренем сильно зв'язаної компоненти */
            if (low[u] == dfn[u]) {
                std::vector<std::string> scc_group;
                while (!st.empty()) {
                    int node = st.top();
                    st.pop();
                    in_stack[node] = false;
                    scc_group.push_back(nodes_[node].name);
                    if (node == u) break;
                }
                if (scc_group.size() > 1) {
                    report.cycles.push_back(std::move(scc_group));
                }
            }
        };

        for (int i = 0; i < n; ++i) {
            if (dfn[i] == 0) {
                tarjan_dfs(tarjan_dfs, i);
            }
        }
    }

    void check_layers(AnalysisReport& report) const {
        for (size_t u = 0; u < adj_.size(); ++u) {
            for (int v : adj_[u]) {
                if (nodes_[u].layer < nodes_[v].layer) {
                    report.layer_violations.push_back(
                        "Зворотна залежність: " + nodes_[u].name + " (рівень " +
                        std::to_string(static_cast<int>(nodes_[u].layer)) + ") -> " +
                        nodes_[v].name + " (рівень " +
                        std::to_string(static_cast<int>(nodes_[v].layer)) + ")"
                    );
                }
            }
        }
    }
};

int main() {
    DependencyGraphChecker checker;

    int api   = checker.add_node("Presentation.HttpApi", Layer::Presentation, 1);
    int order = checker.add_node("Application.OrderService", Layer::Application, 1);
    int core  = checker.add_node("Domain.OrderCore", Layer::Domain, 1);
    int repo  = checker.add_node("Infrastructure.PostgresRepo", Layer::Infrastructure, 1);
    int bill  = checker.add_node("Application.BillingService", Layer::Application, 2);

    /* Дозволені залежності */
    checker.add_dependency(api, order);
    checker.add_dependency(order, core);
    checker.add_dependency(order, repo);

    /* Порушення 1: Зворотна залежність Domain -> Infrastructure (DIP) */
    checker.add_dependency(core, repo);

    /* Порушення 2: Циклічна залежність між сервісами */
    checker.add_dependency(order, bill);
    checker.add_dependency(bill, order);

    auto report = checker.analyze();

    std::cout << "=== СТАТИЧНИЙ АНАЛІЗ АРХІТЕКТУРНИХ ЗАЛЕЖНОСТЕЙ (C++) ===\n";
    for (size_t i = 0; i < report.cycles.size(); ++i) {
        std::cout << "[ПОМИЛКА: ЦИКЛ #" << (i + 1) << "]: ";
        for (size_t j = 0; j < report.cycles[i].size(); ++j) {
            std::cout << report.cycles[i][j] << (j + 1 < report.cycles[i].size() ? " <-> " : "\n");
        }
    }

    for (const auto& violation : report.layer_violations) {
        std::cout << "[ПОМИЛКА: ШАР] " << violation << "\n";
    }

    return report.has_violations() ? 1 : 0;
}
```
:::

## Механіка та покроковий аналіз алгоритму Тар'яна

Алгоритм Тар'яна працює на основі класифікації ребер орієнтованого графа під час одного проходу пошуку в глибину (DFS). Кожна вершина `u` отримує порядковий номер входу `dfn[u]`, що зростає монотонно.

Ключовим елементом алгоритму є динамічний масив `lowlink[u]`:
1. На початку обходу вершини `u` встановлюється `lowlink[u] = dfn[u]`, і вершина додається у стек активних елементів (`in_stack[u] = true`);
2. Алгоритм послідовно перебирає всі вихідні ребра `(u, v)`:
   - Якщо сусід `v` ще не відвідувався (`dfn[v] == 0`), ребро є **деревним** (Tree Edge). Викликається рекурсивний обхід для `v`. Після повернення значення `lowlink[u]` оновлюється як мінімум між поточним `lowlink[u]` та повернутим `lowlink[v]`. Таким чином інформація про досяжні циклічні вершини передається вгору по дереву DFS;
   - Якщо сусід `v` уже був відвіданий і досі знаходиться в стеку (`in_stack[v] == true`), це **зворотне ребро** (Back Edge) або поперечне ребро всередині тієї самої підмножини. Це прямий доказ наявності циклу. `lowlink[u]` оновлюється як `min(lowlink[u], dfn[v])`;
   - Якщо сусід `v` уже відвіданий, але вже знятий зі стека (`in_stack[v] == false`), це ребро веде до раніше повністю обробленої та закритої сильно зв'язаної компоненти. Таке ребро ігнорується, оскільки воно не може утворити новий цикл через вершину `u`;
3. Після обходу всіх суміжних вершин перевіряється умова `lowlink[u] == dfn[u]`. Якщо рівність виконується, вершина `u` є коренем поточної сильно зв'язаної компоненти. Усі елементи, що лежать у стеку вище за `u` (включно з самою `u`), знімаються зі стека та формують одну замкнену компоненту.

Якщо кількість елементів у витягнутій компоненті строго більша за одиницю, це свідчить про наявність взаємного циклічного зчеплення між відповідними архітектурними модулями.

## Валідація шарової архітектури та перевірка предикатів

Після перевірки ациклічності рушій виконує валідацію шарових правил. Кожному модулю присвоєно цілочисельний ранг шару (наприклад, 0 для Infrastructure, 1 для Domain, 2 для Application, 3 для Presentation).

Ітератор проходить по кожному ребру `(u, v)` у списку суміжності та перевіряє умову:
```text
layer(u) >= layer(v)
```
Якщо індекс шару джерела `layer(u)` виявляється строго меншим за індекс цільового вузла `layer(v)`, фіксується архітектурна помилка типу «Зворотний виклик» (Inverted Dependency). Наприклад, якщо модуль доменного ядра (`layer = 1`) імпортує інфраструктурний адаптер бази даних (`layer = 0`), це пряме порушення принципу інверсії залежностей (DIP), оскільки високорівнева бізнес-логіка починає залежати від деталей низькорівневої реалізації сховища.

## Крайові випадки та інженерні пастки реалізації

Під час практичного використання аналізатора в реальних проєктах виникають специфічні ускладнення, які необхідно враховувати під час розробки:

1. **Глибока рекурсія та переповнення стека (Stack Overflow):** У великих монорепозиторіях із сотнями тисяч файлів довжина лінійного ланцюжка залежностей може перевищити ліміт глибини викликів потоку ОС (типово 1–8 МБ). Для промислових аналізаторів рекурсивний виклик `tarjan_dfs` замінюють ітеративною версією на базі власного стека станів у динамічній пам'яті (Heap);
2. **Агрегація мультиребер:** Якщо файл `A.cpp` імпортує 50 класів і структур із файлу `B.hpp`, не слід додавати 50 однакових орієнтованих ребер `A -> B`. Додавання дублюючих ребер штучно роздуває пам'ять списків суміжності та сповільнює обхід. Оптимальний підхід — зберігати унікальні пари `(u, v)` та збільшувати числову вагу ребра `weight(u, v) = 50`;
3. **Непрямі та динамічні залежності:** Статичний аналіз коду (AST-парсинг) не здатний автоматично зафіксувати виклики через рефлексію (Reflection), фабрики рядкових імен чи динамічне завантаження плагінів (`dlopen`/`LoadLibrary`). Для таких систем статичний граф збагачують даними розподіленого трасування (OpenTelemetry/Jaeger), додаючи ребра на основі фактичних мережевих запитів у тестовому середовищі;
4. **Ігнорування тестових залежностей:** Модульні тести часто імпортують як доменні сутності, так і інфраструктурні моки. Тестові файли (`*_test.go`, `*.spec.ts`, `tests/**`) необхідно виключати з перевірки шарової дисципліни або аналізувати за окремим, більш ліберальним набором правил.
