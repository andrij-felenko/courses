# ⚙️ Автоматизований вимірник фітнес-функцій та ерозії архітектури

Автоматизована реалізація фітнес-функцій у CI/CD пайплайні дозволяє перевіряти архітектурні обмеження системи: аналізувати граф залежностей між модулями, обчислювати метрики нестабільності та виявляти недозволені зворотні зв'язки між шарами коду.

Археологія та аналіз ерозії системи вимагають точних кількісних метрик замість суб'єктивних вражень чи абстрактних рекомендацій. Без автоматичного контролю у CI/CD навіть найчистіша гексагональна архітектура деградує протягом 6–12 місяців активної розробки через локальні швидкі костилі та неконтрольоване додавання залежностей між компонентами.

```
[Початковий стан: Чисті межі]  ──(Нові фічі та швидкі костилі)──> [Архітектурна ерозія]
           │                                                            │
           ▼                                                            ▼
[Модулі ізольовані]                                             [Циклічні залежності]
[Шари дотримано]                                                [Протікання абстракцій]
           │                                                            │
           └──────────> [АВТОМАТИЗОВАНА ФІТНЕС-ФУНКЦІЯ У CI] <──────────┘
                              │                   │
                     (Успіх)  ▼                   ▼  (Дефект)
                         [Збірка пройшла]   [PR заблоковано]
```

---

## 1. Математичні метрики зчеплення та Головна Послідовність Роберта Мартіна

Для оцінки якості декомпозиції коду на рівні модулів використовуються метрики, сформульовані Робертом Мартіном (Uncle Bob):

1. **Аферентне зчеплення (Afferent Coupling, `Ca`)**: кількість зовнішніх модулів, які залежать від даного модуля (вхідні стрілки у графі залежностей). Високий `Ca` означає високу відповідальність модуля: зміна у ньому може зламати роботу багатьох залежних компонентів.
2. **Еферентне зчеплення (Efferent Coupling, `Ce`)**: кількість зовнішніх модулів, від яких залежить даний модуль (вихідні стрілки у графі залежностей). Високий `Ce` означає чутливість модуля: зміна у будь-якому із зовнішніх модулів може вимагати редагування даного коду.

На основі цих показників обчислюється **метрика нестабільності модуля (`I`)**:

```
I = Ce / (Ca + Ce)
```

Значення метрики `I` перебуває у діапазоні від `0.0` до `1.0`:

* **`I = 0.0` (Максимальна стабільність / Ригідність)**: модуль має `Ce = 0` та `Ca > 0`. На нього посилаються інші компоненти, але він не залежить від жодного зовнішнього модуля. Класичним прикладом є ядро доменної моделі (Domain Core) або абстрактні інтерфейси. Зміна такого модуля є дуже дорогою, тому він повинен бути максимально абстрактним і стабільним.
* **`I = 1.0` (Максимальна нестабільність / Гнучкість)**: модуль має `Ce > 0` та `Ca = 0`. Він посилається на багато зовнішніх модулів, але від нього не залежить жоден інший компонент. Прикладом є контролери представлення (Web HTTP Controllers) або точки входу в програму. Такий модуль легко змінювати або переписати з нуля, оскільки його зміна не зачіпає сусідів.

Окрім нестабільності, обчислюється **Абстрактність модуля (`A`)**:

```
A = Na / Nc
```

де `Na` — кількість абстрактних класів та інтерфейсів у модулі, а `Nc` — загальна кількість класів у модулі. 

Згідно із **Принципом Стабільних Абстракцій (Stable Abstractions Principle)**, модуль має бути тим абстрактнішим, чим він стабільніший. Модулі з `I = 0` мусять мати `A = 1` (бути абстрактними інтерфейсами), а модулі з `I = 1` мусять мати `A = 0` (бути конкретними реалізаціями). Відстань модуля від **Головної Послідовності (Distance from Main Sequence, `D`)** визначається як:

```
D = |A + I - 1|
```

Якщо `D` наближається до `1.0`, модуль перебуває або у **«Зоні Більості»** (`I=0, A=0` — стабільна конкретна реалізація, яку важко змінювати, наприклад синглтон-моноліт), або у **«Зоні Непотрібності»** (`I=1, A=1` — абстрактний інтерфейс, від якого ніхто не успадковується і який створює зайвий когнітивний оверхед).

---

## 2. Графова модель та перевірка інваріантів шарів

Система описується орієнтованим графом `G = (V, E)`, де вершины `V` відповідають модулям системи, а ребра `E` представляють наявність залежності (імпорту, виклику або успадкування).

Окрім аналізу `I` та `D`, фітнес-функція виконує перевірку **Правила Шаруватості (Layer Rule)**:

```
[ Presentation Layer (Level 2) ]    ──(Дозволено)──>   [ UseCase Layer (Level 1) ]
[ Infrastructure Layer (Level 2) ]  ──(Дозволено)──>   [ Domain Layer (Level 0) ]
                                                                 │
[ Domain Layer (Level 0) ]  ──❌ ЗАБОРОНЕНО імпортувати ─────────┘
```

Модуль із нижчим рівнем шару (Domain, level 0) під загрозою падіння CI-збірки **не має права** імпортувати або посилатися на модулі з вищим рівнем шару (Infrastructure/Web, level 2). Якщо розробник додасть у доменну сутність виклик SQL-драйвера чи HTTP-клієнта, аналізатор зафіксує це як порушення межі.

---

## 3. Практична реалізація фітнес-вимірника мовами C та C++

Нижче наведено робочу реалізацію вимірника фітнес-функцій двома мовами програмування. Реалізація будує матрицю суміжності графа залежностей, обчислює аферентне та еферентне зчеплення, вираховує коефіцієнт нестабільності `I` та виявляє прямі порушення правил шарів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_MODULES 16
#define MAX_NAME_LEN 32

typedef struct {
    char name[MAX_NAME_LEN];
    int layer_level; /* 0 = Domain, 1 = Service, 2 = Infrastructure/Web */
} Module;

typedef struct {
    int module_count;
    Module modules[MAX_MODULES];
    bool adj[MAX_MODULES][MAX_MODULES]; /* adj[i][j] = true означає i залежить від j */
} DependencyGraph;

void graph_init(DependencyGraph *g) {
    g->module_count = 0;
    memset(g->adj, 0, sizeof(g->adj));
}

int graph_add_module(DependencyGraph *g, const char *name, int layer) {
    if (g->module_count >= MAX_MODULES) return -1;
    int id = g->module_count++;
    strncpy(g->modules[id].name, name, MAX_NAME_LEN - 1);
    g->modules[id].name[MAX_NAME_LEN - 1] = '\0';
    g->modules[id].layer_level = layer;
    return id;
}

void graph_add_dependency(DependencyGraph *g, int from_id, int to_id) {
    if (from_id >= 0 && from_id < g->module_count &&
        to_id >= 0 && to_id < g->module_count) {
        g->adj[from_id][to_id] = true;
    }
}

void analyze_instability(const DependencyGraph *g) {
    printf("=== АНАЛІЗ НЕСТАБІЛЬНОСТІ МОДУЛІВ (I = Ce / (Ca + Ce)) ===\n");
    for (int i = 0; i < g->module_count; i++) {
        int ca = 0; /* вхідні залежності (хто залежить від i) */
        int ce = 0; /* вихідні залежності (від кого залежить i) */

        for (int j = 0; j < g->module_count; j++) {
            if (i == j) continue;
            if (g->adj[i][j]) ce++;
            if (g->adj[j][i]) ca++;
        }

        double instability = 0.0;
        if (ca + ce > 0) {
            instability = (double)ce / (ca + ce);
        }

        printf("Модуль [%-15s] (Шар %d): Ca=%2d, Ce=%2d => Нестабільність I = %.2f\n",
               g->modules[i].name, g->modules[i].layer_level, ca, ce, instability);
    }
}

bool check_layer_violations(const DependencyGraph *g) {
    printf("\n=== ПЕРЕВІРКА ПРАВИЛ ШАРІВ ТА ПОРОШЕНЬ АРХІТЕКТУРИ ===\n");
    bool violations_found = false;

    for (int i = 0; i < g->module_count; i++) {
        for (int j = 0; j < g->module_count; j++) {
            if (i == j) continue;

            if (g->adj[i][j]) {
                /* Якщо модуль з нижчого шару посилається на вищий шар */
                if (g->modules[i].layer_level < g->modules[j].layer_level) {
                    printf("❌ КРИТИЧНИЙ ДЕФЕКТ: Модуль шару %d [%s] залежить від модуля вищого шару %d [%s]!\n",
                           g->modules[i].layer_level, g->modules[i].name,
                           g->modules[j].layer_level, g->modules[j].name);
                    violations_found = true;
                }
            }
        }
    }

    if (!violations_found) {
        printf("✅ ПОРОШЕНЬ ШАРІВ НЕ ВИЯВЛЕНО: Архітектурні межі дотримано!\n");
    }
    return !violations_found;
}

int main(void) {
    DependencyGraph g;
    graph_init(&g);

    int m_domain = graph_add_module(&g, "DomainCore", 0);
    int m_usecase = graph_add_module(&g, "OrderUseCase", 1);
    int m_db_adapter = graph_add_module(&g, "PostgresAdapter", 2);
    int m_web_ctrl = graph_add_module(&g, "HttpController", 2);

    /* Дозволені залежності */
    graph_add_dependency(&g, m_web_ctrl, m_usecase);    /* Controller -> UseCase */
    graph_add_dependency(&g, m_db_adapter, m_domain);   /* Adapter -> Domain */
    graph_add_dependency(&g, m_usecase, m_domain);      /* UseCase -> Domain */

    /* ІМІТАЦІЯ ДЕФЕКТУ: Доменна сутність випадково викликає DB Adapter */
    /* graph_add_dependency(&g, m_domain, m_db_adapter); */

    analyze_instability(&g);
    bool pass = check_layer_violations(&g);

    return pass ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <iomanip>
#include <numeric>
#include <algorithm>

enum class Layer {
    Domain = 0,
    UseCase = 1,
    Infrastructure = 2,
    Presentation = 2
};

struct ModuleNode {
    std::string name;
    Layer layer;
};

class FitnessArchitectureEvaluator {
public:
    struct AnalysisResult {
        std::string module_name;
        Layer layer;
        size_t afferent_ca{0};
        size_t efferent_ce{0};
        double instability{0.0};
    };

    struct Violation {
        std::string source_module;
        Layer source_layer;
        std::string target_module;
        Layer target_layer;
    };

    size_t add_module(std::string name, Layer layer) {
        size_t id = modules_.size();
        modules_.push_back({std::move(name), layer});
        adj_matrix_.resize(modules_.size(), std::vector<bool>(modules_.size(), false));
        for (auto& row : adj_matrix_) {
            row.resize(modules_.size(), false);
        }
        return id;
    }

    void add_dependency(size_t from_id, size_t to_id) {
        if (from_id < modules_.size() && to_id < modules_.size()) {
            adj_matrix_[from_id][to_id] = true;
        }
    }

    [[nodiscard]] std::vector<AnalysisResult> compute_metrics() const {
        std::vector<AnalysisResult> results;
        results.reserve(modules_.size());

        for (size_t i = 0; i < modules_.size(); ++i) {
            size_t ca = 0;
            size_t ce = 0;

            for (size_t j = 0; j < modules_.size(); ++j) {
                if (i == j) continue;
                if (adj_matrix_[i][j]) ++ce;
                if (adj_matrix_[j][i]) ++ca;
            }

            double inst = (ca + ce > 0) ? static_cast<double>(ce) / static_cast<double>(ca + ce) : 0.0;
            results.push_back({modules_[i].name, modules_[i].layer, ca, ce, inst});
        }
        return results;
    }

    [[nodiscard]] std::vector<Violation> find_layer_violations() const {
        std::vector<Violation> violations;

        for (size_t i = 0; i < modules_.size(); ++i) {
            for (size_t j = 0; j < modules_.size(); ++j) {
                if (i == j) continue;

                if (adj_matrix_[i][j]) {
                    if (static_cast<int>(modules_[i].layer) < static_cast<int>(modules_[j].layer)) {
                        violations.push_back({
                            modules_[i].name, modules_[i].layer,
                            modules_[j].name, modules_[j].layer
                        });
                    }
                }
            }
        }
        return violations;
    }

private:
    std::vector<ModuleNode> modules_;
    std::vector<std::vector<bool>> adj_matrix_;
};

int main() {
    FitnessArchitectureEvaluator evaluator;

    auto m_domain = evaluator.add_module("DomainCore", Layer::Domain);
    auto m_usecase = evaluator.add_module("OrderUseCase", Layer::UseCase);
    auto m_db = evaluator.add_module("PostgresAdapter", Layer::Infrastructure);
    auto m_web = evaluator.add_module("HttpController", Layer::Presentation);

    evaluator.add_dependency(m_web, m_usecase);
    evaluator.add_dependency(m_db, m_domain);
    evaluator.add_dependency(m_usecase, m_domain);

    auto metrics = evaluator.compute_metrics();
    std::cout << "=== СТАТИСТИКА НЕСТАБІЛЬНОСТІ МОДУЛІВ ===\n";
    for (const auto& res : metrics) {
        std::cout << "Модуль: " << std::left << std::setw(16) << res.module_name
                  << " | Ca=" << std::setw(2) << res.afferent_ca
                  << " | Ce=" << std::setw(2) << res.efferent_ce
                  << " | Instability I=" << std::fixed << std::setprecision(2) << res.instability << "\n";
    }

    auto violations = evaluator.find_layer_violations();
    std::cout << "\n=== РЕЗУЛЬТАТ ПЕРЕВІРКИ ФІТНЕС-ФУНКЦІЇ ===\n";
    if (violations.empty()) {
        std::cout << "✅ Усі фітнес-функції успішно виконано. Архітектурну ерозію не виявлено.\n";
        return 0;
    }

    for (const auto& v : violations) {
        std::cerr << "❌ ПОШКОДЖЕННЯ МЕЖІ: Модуль [" << v.source_module
                  << "] імпортує вищий шар [" << v.target_module << "]\n";
    }
    return 1;
}
```
:::

---

## 4. Виявлення циклічних залежностей та інструменти автоматизації у CI/CD

Окрім перевірки прямого зчеплення шарів, фітнес-функція повинна виконувати пошук **Циклічних Залежностей (Cyclic Dependencies)**. Наявність циклу між трьома модулями (наприклад, `A → B → C → A`) означає, що ці три модулі де-факто є єдиним монолітом: їх неможливо скомпільувати, протестувати або розгорнути окремо.

Виявлення циклів у графі здійснюється за допомогою алгоритму Тарджана (Tarjan's Strongly Connected Components) або обходу в глибину (DFS) з відстеженням стеку рекурсії (Recursion Stack):

1. Під час DFS-обходу кожна вершина позначається у трьох станах: `Unvisited` (білий), `Visiting` (сірий, у стеку), `Visited` (чорний).
2. Якщо під час переходу з сірої вершини ми потрапляємо у сіру вершину, знайдено зворотне ребло (Back Edge), яке є сигнатурою наявності циклу у графі.
3. CI/CD пайплайн негайно завершується з ненульовим кодом помилки (`exit status 1`), блокуючи злиття Pull Request.

### Повідомлення про помилки та аналіз хибних спрацьовувань

Під час впровадження автоматизованих фітнес-функцій інженерні команди найчастіше стикаються із трьома класами проблем:

* **Хибні спрацьовування на інтерфейсах-заглушках**: розробники часто намагаються обійти виявлення залежностей через приведення типів або динамічний reflection. Фітнес-функція повинна аналізувати статичний граф збірки або байткод/AST, а не лише тексти заголовочних файлів.
* **Невраховані спільні DTO**: якщо шар Domain та шар Presentation обидва посилаються на один «спільний DTO модуль», цей модуль стає глобальною точкою зчеплення. Його метрика `Ca` різко зростає, що робить будь-яку зміну в ньому катастрофічною для усієї системи.
* **Тестові залежності у продакшн-коді**: мок-об'єкти та утиліти тестування, розміщені у папці модуля, можуть приховано імпортувати інфраструктуру. Для запобігання цього тестові модулі відокремлюються у виділений шар `TestHarness`.

### Готові фреймворки для різних екосистем

Для автоматичного захисту архітектури від ерозії у реальних проєктах застосовуються готові фреймворки, що реалізують описувані принципи:

* **Java/JVM**: бібліотека `ArchUnit` (дозволяє писати юніт-тести вигляду `noClasses().that().resideInAPackage("..domain..").should().dependOnClassesThroughBy("..infrastructure..")`).
* **JavaScript/TypeScript**: інструмент `dependency-cruiser` (налаштування правил у `.dependency-cruiser.js` для заборони імпортів між директоріями).
* **Go**: інструмент `go-arch-lint` або `ArchGo` (декларативна перевірка залежностей пакетів у `arch-lint.yml`).
* **C/C++**: статичний аналізатор на основі Clang AST (`clang-tidy` з кастомними правилами або парсинг графа `cmake --graphviz`).

Інтеграція таких перевірок у CI/CD пайплайн перетворює архітектуру із паперових домовленостей на автоматизований інженерний інваріант, що захищає систему від поступової деградації.
