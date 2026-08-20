# ⚙️ Автоматичний аналізатор дерев планів EXPLAIN у C та C++

Формат виводу `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` повертає вичерпну деревоподібну структуру даних про виконання запиту, проте у великих промислових запитах розмір такого JSON сягає тисяч рядків. Ручний пошук проблемних місць у розгалужених деревах забирає багато часу інженера та часто призводить до пропуску критичних аномалій. Спеціалізований діагностичний аналізатор обходить дерево плану, зіставляє початкові прогнози оптимізатора з реальними вимірами та сигналізує про відомі архітектурні дефекти.

## Архітектура та діагностичні патерни аналізатора

Програма будує в оперативній пам'яті внутрішнє поліморфне дерево плану, де кожен вузол відповідає фізичному оператору (`Seq Scan`, `Index Scan`, `Hash Join`, `Sort` тощо), зберігаючи як статичні оцінки вартості, так і динамічні лічильники таймінгів та буферів.

У мові C структура `PlanNode` керує динамічним масивом вказівників на дочірні вузли (`children`), вимагаючи явного виділення пам'яті через `realloc` та рекурсивного звільнення через `free_plan_tree`. У версії на C++ дерево інкапсульоване через ідіому RAII за допомогою `std::vector<std::unique_ptr<PlanNode>>`, що повністю усуває ризик витоків пам'яті при виникненні помилок парсингу або достроковому виході з функцій.

Під час рекурсивного обходу структури аналізатор перевіряє чотири класичні аномалії виконання:

1. **Помилка кардинальності (Cardinality Misestimate):** відхилення фактичної кількості рядків `Actual Rows` від прогнозованої `Plan Rows` у понад 10 разів при загальній кількості рядків понад 100 свідчить про деградацію системної статистики каталогу. Зазвичай це вимагає запуску `ANALYZE`, збільшення ліміту кошиків гістограм (`SET STATISTICS 500`) або створення об'єднаної статистики (`CREATE STATISTICS`) для корельованих стовпців.
2. **Низька ефективність дискового кешу (Cache Hit Ratio):** коефіцієнт попадання в оперативний кеш СУБД розраховується за формулою `shared_hit / (shared_hit + shared_read)`. Якщо для часто виконуваних транзакційних запитів він падає нижче 95% за значної кількості читань (понад 500 сторінок), це вказує на дефіцит пулу пам'яті `shared_buffers` або відсутність покривного індексу, що провокує надлишковий дисковий I/O.
3. **Скидання проміжних даних на накопичувач (Disk Spill):** використання алгоритму зовнішнього сортування злиттям (`Sort Method: external merge Disk`) або розбиття хеш-таблиці на кілька дискових батчів свідчить про занижений ліміт пам'яті сесії `work_mem`. Запис тимчасових файлів на накопичувач сповільнює роботу запиту в десятки разів.
4. **Високі втрати на фільтрації (High Filter Rows Removed):** ситуація, коли вузол послідовного читання піднімає з носія 100 000 рядків, але після перевірки предиката `Filter` відкидає 99% із них, сигналізує про гостру необхідність створення складеного або часткового індексу за фільтрованими стовпцями.

Важливим аспектом аналізу є коректний підрахунок рядків у циклах: якщо вузол виконувався всередині циклу (наприклад, внутрішня гілка `Nested Loop`), значення `Actual Rows` у виводі СУБД вказується як середнє за одну ітерацію, тому аналізатор автоматично множить його на лічильник `actual_loops`.

Рекурсивний обхід дерева реалізує патерн відвідувача (Visitor Pattern): функція спускається вглиб дерева плану, агрегує загальну кількість зчитаних та закешованих сторінок по всіх гілках і форматує текстовий звіт із візуальними відступами відповідно до рівня вкладеності вузлів.

## Обробка спеціальних та паралельних вузлів

При розширенні аналізатора на складні плани обробляються додаткові класи фізичних операторів:
- **Паралельні вузли (`Gather`, `Gather Merge`):** аналізатор зіставляє кількість запланованих фонових процесів (`Workers Planned`) із реально запущеними (`Workers Launched`). Якщо заплановано 4 воркери, а запущено лише 1 через вичерпання пулу з'єднань, система генерує попередження про дефіцит процесів паралелізму.
- **Власний час оператора (Exclusive Time):** час дочірніх вузлів віднімається від сумарного часу батьківського оператора. Це дозволяє точно відокремити час очікування I/O на лисках від витрат процесора на об'єднання рядків у вузлах `Hash Join` або `Merge Join`.
- **Комбіновані бітові карти (`BitmapAnd`, `BitmapOr`):** аналізатор перевіряє, чи не призводить об'єднання кількох індексів до огрублення карти пам'яті (`lossy bitmap`), яке змушує рушій повторно сканувати сторінки в купі.

## Реалізація аналізатора

Нижче наведено робочу реалізацію діагностичного парсера та аналізатора дерева плану двома системними мовами програмування:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

typedef struct PlanNode {
    char node_type[64];
    char relation_name[64];
    double startup_cost;
    double total_cost;
    double plan_rows;
    double actual_time_ms;
    double actual_rows;
    int actual_loops;
    long shared_hit_blocks;
    long shared_read_blocks;
    long rows_removed_filter;
    bool spilled_to_disk;
    
    struct PlanNode** children;
    size_t children_count;
    size_t children_capacity;
} PlanNode;

typedef struct {
    int total_nodes;
    int cardinality_warnings;
    int disk_spills;
    int filter_warnings;
    long total_shared_hit;
    long total_shared_read;
} DiagnosticSummary;

PlanNode* create_plan_node(const char* type, const char* rel, double cost, 
                          double plan_r, double act_time, double act_r, int loops) {
    PlanNode* node = (PlanNode*)calloc(1, sizeof(PlanNode));
    if (!node) return NULL;
    
    strncpy(node->node_type, type, sizeof(node->node_type) - 1);
    if (rel) strncpy(node->relation_name, rel, sizeof(node->relation_name) - 1);
    
    node->total_cost = cost;
    node->plan_rows = plan_r;
    node->actual_time_ms = act_time;
    node->actual_rows = act_r;
    node->actual_loops = loops;
    return node;
}

void add_child_node(PlanNode* parent, PlanNode* child) {
    if (!parent || !child) return;
    if (parent->children_count >= parent->children_capacity) {
        size_t new_cap = parent->children_capacity == 0 ? 2 : parent->children_capacity * 2;
        PlanNode** new_children = (PlanNode**)realloc(parent->children, new_cap * sizeof(PlanNode*));
        if (!new_children) return;
        parent->children = new_children;
        parent->children_capacity = new_cap;
    }
    parent->children[parent->children_count++] = child;
}

void analyze_node_recursive(const PlanNode* node, int depth, DiagnosticSummary* summary) {
    if (!node) return;
    summary->total_nodes++;
    summary->total_shared_hit += node->shared_hit_blocks;
    summary->total_shared_read += node->shared_read_blocks;

    double total_actual_rows = node->actual_rows * node->actual_loops;
    double ratio = node->plan_rows > 0 ? total_actual_rows / node->plan_rows : 1.0;

    // Відступ для візуалізації ієрархії дерева
    for (int i = 0; i < depth; ++i) printf("  ");
    printf("-> %s", node->node_type);
    if (strlen(node->relation_name) > 0) printf(" on %s", node->relation_name);
    printf(" (cost=%.2f, act_time=%.2f ms, act_rows=%.0f, plan_rows=%.0f)\n",
           node->total_cost, node->actual_time_ms * node->actual_loops,
           total_actual_rows, node->plan_rows);

    // 1. Перевірка помилки кардинальності
    if ((ratio > 10.0 || ratio < 0.1) && total_actual_rows > 100.0) {
        summary->cardinality_warnings++;
        for (int i = 0; i < depth + 1; ++i) printf("  ");
        printf("⚠️  [УВАГА: Кардинальність] Прогноз %.0f рядків, факт: %.0f (коефіцієнт %.1fx)\n",
               node->plan_rows, total_actual_rows, ratio);
    }

    // 2. Перевірка скидання на диск
    if (node->spilled_to_disk) {
        summary->disk_spills++;
        for (int i = 0; i < depth + 1; ++i) printf("  ");
        printf("⚠️  [КРИТИЧНО: Диск] Вузол скинув дані на диск через нестачу work_mem!\n");
    }

    // 3. Перевірка надмірної фільтрації
    if (node->rows_removed_filter > 10000) {
        summary->filter_warnings++;
        for (int i = 0; i < depth + 1; ++i) printf("  ");
        printf("⚠️  [УВАГА: Фільтр] Відкинуто %ld рядків предиката. Потрібен індекс!\n",
               node->rows_removed_filter);
    }

    for (size_t i = 0; i < node->children_count; ++i) {
        analyze_node_recursive(node->children[i], depth + 1, summary);
    }
}

void print_diagnostic_report(const PlanNode* root) {
    printf("================ ЗВІТ АНАЛІЗУ ПЛАНУ EXPLAIN ================\n");
    DiagnosticSummary summary = {0};
    analyze_node_recursive(root, 0, &summary);

    printf("\n----------------------- ПІДСУМОК -----------------------\n");
    printf("Всього вузлів у дереві: %d\n", summary.total_nodes);
    printf("Помилок кардинальності: %d\n", summary.cardinality_warnings);
    printf("Скидань на диск:       %d\n", summary.disk_spills);
    printf("Вузлів із високою фільтрацією: %d\n", summary.filter_warnings);

    long total_blocks = summary.total_shared_hit + summary.total_shared_read;
    if (total_blocks > 0) {
        double hit_ratio = (double)summary.total_shared_hit / (double)total_blocks * 100.0;
        printf("Ефективність кешу (Hit Ratio): %.2f%% (%ld hit, %ld read)\n",
               hit_ratio, summary.total_shared_hit, summary.total_shared_read);
        if (hit_ratio < 95.0 && summary.total_shared_read > 500) {
            printf("⚠️  [УВАГА: Кеш] Hit ratio нижчий за 95%%. Можливий дефіцит пам'яті.\n");
        }
    }
    printf("============================================================\n");
}

void free_plan_tree(PlanNode* node) {
    if (!node) return;
    for (size_t i = 0; i < node->children_count; ++i) {
        free_plan_tree(node->children[i]);
    }
    free(node->children);
    free(node);
}

int main(void) {
    // Демонстраційна побудова плану для SELECT * FROM orders JOIN users ON ...
    PlanNode* root = create_plan_node("Hash Join", NULL, 942.50, 4300, 14.30, 4120, 1);
    root->shared_hit_blocks = 1200;
    root->shared_read_blocks = 450;

    PlanNode* scan_orders = create_plan_node("Seq Scan", "orders", 540.00, 15000, 6.80, 15000, 1);
    scan_orders->rows_removed_filter = 35000;
    scan_orders->shared_hit_blocks = 800;
    scan_orders->shared_read_blocks = 400;

    PlanNode* hash_node = create_plan_node("Hash", NULL, 160.00, 1200, 0.74, 1180, 1);
    PlanNode* scan_users = create_plan_node("Index Scan", "users", 160.00, 120, 0.52, 1180, 1);
    scan_users->shared_hit_blocks = 400;
    scan_users->shared_read_blocks = 50;

    add_child_node(hash_node, scan_users);
    add_child_node(root, scan_orders);
    add_child_node(root, hash_node);

    print_diagnostic_report(root);
    free_plan_tree(root);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <iomanip>

struct DiagnosticSummary {
    int total_nodes = 0;
    int cardinality_warnings = 0;
    int disk_spills = 0;
    int filter_warnings = 0;
    int64_t total_shared_hit = 0;
    int64_t total_shared_read = 0;
};

class PlanNode {
public:
    std::string node_type;
    std::string relation_name;
    double startup_cost = 0.0;
    double total_cost = 0.0;
    double plan_rows = 0.0;
    double actual_time_ms = 0.0;
    double actual_rows = 0.0;
    int actual_loops = 1;
    int64_t shared_hit_blocks = 0;
    int64_t shared_read_blocks = 0;
    int64_t rows_removed_filter = 0;
    bool spilled_to_disk = false;

    std::vector<std::unique_ptr<PlanNode>> children;

    PlanNode(std::string_view type, std::string_view rel, double cost,
             double plan_r, double act_time, double act_r, int loops = 1)
        : node_type(type), relation_name(rel), total_cost(cost),
          plan_rows(plan_r), actual_time_ms(act_time), actual_rows(act_r),
          actual_loops(loops) {}

    void add_child(std::unique_ptr<PlanNode> child) {
        if (child) children.push_back(std::move(child));
    }
};

class PlanAnalyzer {
public:
    static void generate_report(const PlanNode& root) {
        std::cout << "================ ЗВІТ АНАЛІЗУ ПЛАНУ EXPLAIN ================\n";
        DiagnosticSummary summary;
        traverse(root, 0, summary);

        std::cout << "\n----------------------- ПІДСУМОК -----------------------\n";
        std::cout << "Всього вузлів у дереві: " << summary.total_nodes << "\n";
        std::cout << "Помилок кардинальності: " << summary.cardinality_warnings << "\n";
        std::cout << "Скидань на диск:       " << summary.disk_spills << "\n";
        std::cout << "Вузлів із високою фільтрацією: " << summary.filter_warnings << "\n";

        const int64_t total_blocks = summary.total_shared_hit + summary.total_shared_read;
        if (total_blocks > 0) {
            const double hit_ratio = static_cast<double>(summary.total_shared_hit) /
                                     static_cast<double>(total_blocks) * 100.0;
            std::cout << std::fixed << std::setprecision(2);
            std::cout << "Ефективність кешу (Hit Ratio): " << hit_ratio << "% ("
                      << summary.total_shared_hit << " hit, " << summary.total_shared_read << " read)\n";
            if (hit_ratio < 95.0 && summary.total_shared_read > 500) {
                std::cout << "⚠️  [УВАГА: Кеш] Hit ratio нижчий за 95%. Можливий дефіцит пам'яті.\n";
            }
        }
        std::cout << "============================================================\n";
    }

private:
    static void traverse(const PlanNode& node, int depth, DiagnosticSummary& summary) {
        summary.total_nodes++;
        summary.total_shared_hit += node.shared_hit_blocks;
        summary.total_shared_read += node.shared_read_blocks;

        const double total_actual_rows = node.actual_rows * node.actual_loops;
        const double ratio = node.plan_rows > 0.0 ? total_actual_rows / node.plan_rows : 1.0;

        std::string indent(depth * 2, ' ');
        std::cout << indent << "-> " << node.node_type;
        if (!node.relation_name.empty()) {
            std::cout << " on " << node.relation_name;
        }
        std::cout << std::fixed << std::setprecision(2);
        std::cout << " (cost=" << node.total_cost << ", act_time="
                  << (node.actual_time_ms * node.actual_loops) << " ms, act_rows="
                  << total_actual_rows << ", plan_rows=" << node.plan_rows << ")\n";

        // 1. Кардинальність
        if ((ratio > 10.0 || ratio < 0.1) && total_actual_rows > 100.0) {
            summary.cardinality_warnings++;
            std::cout << indent << "  ⚠️  [УВАГА: Кардинальність] Прогноз " << node.plan_rows
                      << " рядків, факт: " << total_actual_rows << " (коефіцієнт " << ratio << "x)\n";
        }

        // 2. Скидання на диск
        if (node.spilled_to_disk) {
            summary.disk_spills++;
            std::cout << indent << "  ⚠️  [КРИТИЧНО: Диск] Вузол скинув дані на диск через нестачу work_mem!\n";
        }

        // 3. Фільтрація
        if (node.rows_removed_filter > 10000) {
            summary.filter_warnings++;
            std::cout << indent << "  ⚠️  [УВАГА: Фільтр] Відкинуто " << node.rows_removed_filter
                      << " рядків предиката. Потрібен індекс!\n";
        }

        for (const auto& child : node.children) {
            if (child) traverse(*child, depth + 1, summary);
        }
    }
};

int main() {
    auto root = std::make_unique<PlanNode>("Hash Join", "", 942.50, 4300, 14.30, 4120, 1);
    root->shared_hit_blocks = 1200;
    root->shared_read_blocks = 450;

    auto scan_orders = std::make_unique<PlanNode>("Seq Scan", "orders", 540.00, 15000, 6.80, 15000, 1);
    scan_orders->rows_removed_filter = 35000;
    scan_orders->shared_hit_blocks = 800;
    scan_orders->shared_read_blocks = 400;

    auto hash_node = std::make_unique<PlanNode>("Hash", "", 160.00, 1200, 0.74, 1180, 1);
    auto scan_users = std::make_unique<PlanNode>("Index Scan", "users", 160.00, 120, 0.52, 1180, 1);
    scan_users->shared_hit_blocks = 400;
    scan_users->shared_read_blocks = 50;

    hash_node->add_child(std::move(scan_users));
    root->add_child(std::move(scan_orders));
    root->add_child(std::move(hash_node));

    PlanAnalyzer::generate_report(*root);
    return 0;
}
```
:::

## Збирання та виконання

Програму можна скомпілювати будь-яким сучасним компілятором C або C++:

```bash
# Збирання версії на мові C:
gcc -O2 -Wall -Wextra plan_analyzer.c -o plan_analyzer_c
./plan_analyzer_c

# Збирання версії на мові C++:
g++ -O2 -Wall -Wextra -std=c++20 plan_analyzer.cpp -o plan_analyzer_cpp
./plan_analyzer_cpp
```

## Інтеграція з парсерами JSON та пайплайнами CI/CD

У реальних виробничих проектах дерево `PlanNode` наповнюється даними автоматично з виводу бібліотек `libpq` (C/C++) або системних логів `auto_explain`. Для цього вхідний JSON парситься бібліотекою (наприклад, `cJSON` для C або `nlohmann/json` для C++), витягуючи поля об'єкта `Plan` та рекурсивно додаючи дочірні плани з масиву `Plans`.

При інтеграції в конвеєр безперервної інтеграції (CI/CD) утиліта запускається під час прогону інтеграційних тестів. Якщо аналізатор фіксує появу `external merge Disk` або розходження прогнозу кардинальності понад 10x на таблицях із понад 100 000 рядків, CI/CD-пайплайн повертає ненульовий код помилки та блокує злиття гілки до репозиторію. Це запобігає випуску в продакшен повільних запитів, які могли б спричинити блокування бази або падіння продуктивності під навантаженням.

Крім того, вивід утиліти можна транслювати у формат метрик для систем моніторингу Prometheus та панелей Grafana. Регулярний аудит повільних запитів із журналів бази даних дозволяє команді розробки завчасно виявляти запити, які починають деградувати в міру росту обсягів таблиць, і планувати створення індексів заздалегідь, не чекаючи на інциденти від користувачів.
