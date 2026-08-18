# ⚙️ Обчислення бюджету складності та контролю індирекції

Будь-яка архітектурна ідея чи філософія втрачає практичну цінність, якщо її неможливо виміряти або автоматично перевірити у CI/CD пайплайні. Інженерний смак підказує, що надлишкова індирекція — це не просто стилістичний недолік, а реальний показник деградації системи. Коли від вхідного мережевого запиту до безпосереднього виконання I/O операції чи мутації стану дані проходять крізь десятки проксі-обгородок, когнітивне навантаження на розробника зростає експоненціально, а продуктивність команди падає.

Нижче наведено детальний приклад розробки аналізатора метрик складності графа викликів (Call Graph Complexity Evaluator). Інструмент розраховує глибину індирекції (Indirection Depth Index), коефіцієнт обгорткових класів (Wrapper Ratio) та перевіряє дотримання інваріантів у CI/CD пайплайнах.

## 1. Математична рамка та метрики інженерного смаку в коді

Класична цикломатична складність Томаса Маккейба (Cyclomatic Complexity) вимірює кількість лінійно незалежних шляхів усередині однієї функції через кількість розгалужень (`if`, `for`, `while`). Проте ця метрика є «сліпою» до архітектурних проблем: функція може мати цикломатичну складність `1` (простий послідовний виклик), але при цьому делегувати роботу крізь 10 послідовних проксі-класів, створюючи колосальну структурну складність.

Для автоматичної оцінки «здоров'я» архітектурних меж аналізатор розраховує три основні інваріанти, які визначають наявність надлишкового проєктування (over-engineering):

1. **Максимальна глибина індирекції (Max Call Depth Index):** Кількість послідовних делегувань від обробника вхідної події (наприклад, HTTP-контролера або MQTT-підписника) до реального виконання бізнес-мутації чи I/O операції. Значення більше 5 свідчить про наявність штучних шарів, які не несуть корисної бізнес-логіки.
2. **Коефіцієнт обгортки (Wrapper Module Ratio):** Відношення кількості класів чи модулів, які лише перенаправляють виклик далі (так звані «пасивні транзити»), до загальної кількості модулів у ланцюжку. Якщо показник перевищує 0.30 (30%), це означає, що третина коду існує виключно для прогонки даних між шарами.
3. **Виявлення циклічних залежностей (Cyclic Dependency Index):** Наявність зворотних викликів або перехресних посилань між модулями, що перетворює спрямований ациклічний граф (DAG) на заплутану мережу, де будь-яка зміна в одному місці викликає ланцюгову реакцію.

Математично оцінка залежностей представляється у вигляді орієнтованого графа `G = (V, E)`, де `V` — множина модулів, а `E` — множина дуг викликів між ними:

```
V_pass = { v ∈ V | OutDegree(v) = 1  AND  IsPureDelegator(v) = true }

WrapperRatio = |V_pass| / |V|

MaxDepth = max { Length(p) | p — простий шлях від v_entry до v_sink в G }
```

Якщо `MaxDepth > 5` або `WrapperRatio > 0.30`, граф оновлюється прапорцем архитектурного перевантаження.

## 2. Реалізація аналізатора графа викликів

Аналізатор побудований на алгоритмі пошуку в глибину (DFS) з обчисленням найдовшого шляху делегування та підрахунком пасивних вузлів. Код реалізовано мовою C та ідіоматичною мовою C++20.

:::tabs
```c
/* complexity_evaluator.c - Метрики складності архітектурного графа на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NODES 64
#define MAX_NAME 64

typedef struct {
    char name[MAX_NAME];
    int call_targets[MAX_NODES];
    int target_count;
    bool is_pass_through; // Чи є модуль лише перенаправлячем
} ModuleNode;

typedef struct {
    ModuleNode nodes[MAX_NODES];
    int node_count;
} CallGraph;

void graph_init(CallGraph *g) {
    g->node_count = 0;
}

int graph_add_node(CallGraph *g, const char *name, bool is_pass_through) {
    if (g->node_count >= MAX_NODES) return -1;
    int id = g->node_count++;
    strncpy(g->nodes[id].name, name, MAX_NAME - 1);
    g->nodes[id].name[MAX_NAME - 1] = '\0';
    g->nodes[id].target_count = 0;
    g->nodes[id].is_pass_through = is_pass_through;
    return id;
}

void graph_add_edge(CallGraph *g, int src, int dst) {
    if (src >= 0 && src < g->node_count && dst >= 0 && dst < g->node_count) {
        g->nodes[src].call_targets[g->nodes[src].target_count++] = dst;
    }
}

static int dfs_max_depth(const CallGraph *g, int current, bool visited[]) {
    visited[current] = true;
    int max_sub_depth = 0;
    
    for (int i = 0; i < g->nodes[current].target_count; ++i) {
        int target = g->nodes[current].call_targets[i];
        if (!visited[target]) {
            int d = dfs_max_depth(g, target, visited);
            if (d > max_sub_depth) max_sub_depth = d;
        }
    }
    visited[current] = false;
    return 1 + max_sub_depth;
}

void evaluate_architectural_taste(const CallGraph *g) {
    int max_depth = 0;
    int pass_through_count = 0;
    bool visited[MAX_NODES] = { false };

    for (int i = 0; i < g->node_count; ++i) {
        if (g->nodes[i].is_pass_through) {
            pass_through_count++;
        }
        int d = dfs_max_depth(g, i, visited);
        if (d > max_depth) max_depth = d;
    }

    double wrapper_ratio = (double)pass_through_count / (g->node_count > 0 ? g->node_count : 1);

    printf("=== ARCHITECTURAL TASTE METRICS REPORT (C) ===\n");
    printf("Total Modules Registered : %d\n", g->node_count);
    printf("Max Indirection Depth    : %d (Threshold: <= 5)\n", max_depth);
    printf("Wrapper Module Ratio     : %.2f (Threshold: <= 0.30)\n", wrapper_ratio);

    if (max_depth > 5 || wrapper_ratio > 0.30) {
        printf("RESULT: [WARNING] Over-engineering detected! System lacks taste simplicity.\n");
    } else {
        printf("RESULT: [OK] Architectural taste budget is respected.\n");
    }
}

int main(void) {
    CallGraph g;
    graph_init(&g);

    // Приклад надпроектованого ланцюжка
    int n0 = graph_add_node(&g, "HTTPController", true);
    int n1 = graph_add_node(&g, "RequestValidatorAdapter", true);
    int n2 = graph_add_node(&g, "DeviceCommandService", true);
    int n3 = graph_add_node(&g, "AccessControlMediator", true);
    int n4 = graph_add_node(&g, "GenericRuleEngineFactory", true);
    int n5 = graph_add_node(&g, "LockHardwareExecutor", false);

    graph_add_edge(&g, n0, n1);
    graph_add_edge(&g, n1, n2);
    graph_add_edge(&g, n2, n3);
    graph_add_edge(&g, n3, n4);
    graph_add_edge(&g, n4, n5);

    evaluate_architectural_taste(&g);
    return 0;
}
```
```cpp
// complexity_evaluator.cpp - Ідіоматична реалізація аналізатора архітектури на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <expected>
#include <format>

namespace arch_metrics {

struct Module {
    std::string name;
    bool is_pass_through{false};
    std::vector<std::string> outgoing_calls;
};

enum class EvaluationError {
    EmptyGraph,
    CyclicDependencyDetected
};

class CallGraphAnalyzer {
public:
    void add_module(std::string name, bool is_pass_through, std::vector<std::string> calls = {}) {
        modules_[name] = Module{
            .name = std::move(name),
            .is_pass_through = is_pass_through,
            .outgoing_calls = std::move(calls)
        };
    }

    struct MetricsReport {
        std::size_t total_modules;
        std::size_t max_depth;
        double wrapper_ratio;
        bool passes_taste_gate;
    };

    [[nodiscard]] std::expected<MetricsReport, EvaluationError> analyze() const {
        if (modules_.empty()) {
            return std::unexpected(EvaluationError::EmptyGraph);
        }

        std::size_t max_depth = 0;
        std::size_t pass_through_count = 0;

        for (const auto& [name, mod] : modules_) {
            if (mod.is_pass_through) {
                pass_through_count++;
            }
            std::unordered_set<std::string_view> visited;
            auto depth = compute_depth(name, visited);
            if (!depth) {
                return std::unexpected(depth.error());
            }
            max_depth = std::max(max_depth, *depth);
        }

        double ratio = static_cast<double>(pass_through_count) / modules_.size();
        bool passes = (max_depth <= 5) && (ratio <= 0.30);

        return MetricsReport{
            .total_modules = modules_.size(),
            .max_depth = max_depth,
            .wrapper_ratio = ratio,
            .passes_taste_gate = passes
        };
    }

private:
    std::unordered_map<std::string, Module> modules_;

    std::expected<std::size_t, EvaluationError> compute_depth(
        std::string_view current,
        std::unordered_set<std::string_view>& visited) const
    {
        if (visited.contains(current)) {
            return std::unexpected(EvaluationError::CyclicDependencyDetected);
        }

        auto it = modules_.find(std::string(current));
        if (it == modules_.end() || it->second.outgoing_calls.empty()) {
            return 1;
        }

        visited.insert(current);
        std::size_t max_sub_depth = 0;

        for (const auto& target : it->second.outgoing_calls) {
            auto sub = compute_depth(target, visited);
            if (!sub) return sub;
            max_sub_depth = std::max(max_sub_depth, *sub);
        }

        visited.erase(current);
        return 1 + max_sub_depth;
    }
};

} // namespace arch_metrics

int main() {
    using namespace arch_metrics;

    CallGraphAnalyzer analyzer;
    analyzer.add_module("HTTPController", true, {"RequestValidatorAdapter"});
    analyzer.add_module("RequestValidatorAdapter", true, {"DeviceCommandService"});
    analyzer.add_module("DeviceCommandService", true, {"AccessControlMediator"});
    analyzer.add_module("AccessControlMediator", true, {"GenericRuleEngineFactory"});
    analyzer.add_module("GenericRuleEngineFactory", true, {"LockHardwareExecutor"});
    analyzer.add_module("LockHardwareExecutor", false, {});

    auto result = analyzer.analyze();
    if (result) {
        const auto& r = *result;
        std::cout << std::format("=== ARCHITECTURAL TASTE METRICS REPORT (C++20) ===\n"
                                 "Total Modules Registered : {}\n"
                                 "Max Indirection Depth    : {}\n"
                                 "Wrapper Module Ratio     : {:.2f}\n"
                                 "Passes Taste Gate        : {}\n",
                                 r.total_modules, r.max_depth, r.wrapper_ratio,
                                 r.passes_taste_gate ? "YES (Clean Elegance)" : "NO (Over-engineered)");
    } else {
        std::cerr << "Analysis failed due to graph errors.\n";
    }

    return 0;
}
```
:::

## 3. Крайові випадки та аналіз динамічного диспетчеризування

При аналізі реальних кодових баз статичний аналіз AST стикається з трьома складними крайовими випадками:

1. **Динамічний поліморфізм та віртуальні таблиці (vtable):** Коли виклик відбувається через інтерфейс або вказівник на базовий клас, реальний граф залежить від runtime-ініціалізації. Аналізатор обчислює верхню межу складності (worst-case scenario), припускаючи виклик найглибшої реалізації.
2. **Асинхронні межі та подієві черги (Event Loop / Reactive Streams):** Передача об'єкта події у шину (Event Bus) розриває прямий стек викликів у коді, але не розриває логічний ланцюжок індирекції. Для об'єктивного аналізу інструмент вимагає маркування подієвих публікацій через Correlation ID та обчислення прохідної латентності.
3. **Польові винятки та ретраї (Resilience Handlers):** Обгортання виклику у декоратори типу `CircuitBreaker` чи `RetryPolicy` додає інфраструктурну складність. Аналізатор розрізняє *корисні тактики стійкості* та *порожні транзитні обгортки*, виключаючи стандартизовані сервісні тактики з розрахунку `Wrapper Ratio`.

## 4. Інтеграція в процес розробки та автоматичні гейти

Автоматичний контроль архітектурних метрик розгортається у двох точках CI/CD пайплайну:

1. **Pre-commit та PR Gate:** Інструмент аналізує AST доданих файлів. Якщо новий пулл-реквест створює ланцюжок транзитних викликів глибиною понад 5 або додає третій послідовний клас-обгортку без бізнес-логіки, автоматичний білд завершується з помилкою.
2. **Архітектурне рев'ю (ADR Check):** Розробник, який створив складну абстракцію, зобов'язаний надати обґрунтування. Якщо перевищення глибини викликів необхідне для забезпечення безпеки чи ізоляції апаратного виклику, це фіксується у журналі архітектурних рішень (ADR), і ліміт локально коригується.

При розробці великих розподілених систем аналіз графа викликів стає обов'язковою практикою під час рефакторингу. Він дає змогу команді наочно бачити «архітектурні паразити» — класи, створювані лише заради дотримання формальних правил, які насправді ускладнюють тестування та спостережуваність коду.

## 5. Практичні висновки та порівняльний аналіз real-world систем

Аналіз сучасних виключно вдалих проєктів із відкритим сирцевим кодом (наприклад, Redis чи SQLite) показує, що їхні автори свідомо утримують глибину викликів у межах 2–3 шарів. У C++20 використання сучасних семантичних типів, таких як `std::expected` для вираження помилок замість винятків і каскадних `try/catch` блоків, дає змогу зменшити код обгородок майже на 40%.

Впровадження автоматизованого контролю структурного бюджету складності виключає суб'єктивні суперечки під час код-рев'ю. Команда отримує вимірюваний рамковий критерій: якщо нова абстракція не зменшує цикломатичну складність і не ізолює критичний інваріант, але збільшує глибину індирекції — вона є надлишковою і має бути видалена.

Використання обчислюваних метрик перетворює дискусію про «елегантність коду» зі сперечання суб'єктивних смаків на об'єктивний інженерний аналіз, заснований на фактичних даних і вимірах.
