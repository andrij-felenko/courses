# ⚙️ Генератор і валідатор дерева пошуку несправностей

Графи діагностики та локалізації відмов (Fault Tree Analysis та Troubleshooting Decision Trees) є фундаментом автоматизованих сервісних систем, експертних модулів вбудованого програмного забезпечення та інтерактивних посібників з ремонту складної техніки. Головна проблема під час ручного складання таблиць пошуку несправностей у текстових редакторах полягає у виникненні прихованих логічних дефектів: зациклень запитань, коли ланцюжок відповідей водить техніка по колу; висячих вузлів (dead ends), де жодна гілка не приводить до конкретної відновлювальної дії; або недосяжних станів, перевірка яких ніколи не буде викликана в реальній системі через логічні блокування попередніх кроків.

Щоб гарантувати надійність сервісної інструкції та скоротити час простою технологічного обладнання, діагностичну матрицю формалізують у вигляді орієнтованого графа станів. Кожен вузол графа належить до одного з трьох чітко розмежованих типів:
1. **Вузол спостереження або симптому (Symptom Node):** вхідна точка графа, що фіксує первинний прояв відмови. Це поверхневий сигнал, який фіксує оператор без використання спеціальних вимірювальних приладів (поведінка світлодіода, відсутність кадрів у шині зв'язку, характерний звук спрацювання захисного реле чи числовий код помилки на сегментному дисплеї).
2. **Вузол перевірки або тесту (Check Node):** бінарне розгалуження, що вимагає однозначного вимірювання фізичної величини (напруга на клемах, опір диференціальної пари, струм споживання) або опитування внутрішніх регістрів контролера через сервісний порт. Має рівно дві вихідні дуги: `PASS` (виміряне значення відповідає нормі) та `FAIL` (фіксується відхилення від робочого діапазону).
3. **Вузол відновлювальної дії (Action Node):** термінальний лист графа, який містить вичерпну інженерну інструкцію із заміни запобіжника, корекції термінатора шини зв'язку, підтягування гвинтових клем або перепрошивки енергонезалежної пам'яті.

## Алгоритмічні інваріанти валідації діагностичного графа

Для математичної коректності матриці діагностики граф проходить обов'язкову автоматичну перевірку на дотримання чотирьох інваріантів цілісності:
- **Ациклічність або контрольована ітерація:** спрямований граф не повинен містити нескінченних циклів без лічильника спроб. Якщо відновлювальна дія пропонує повторну діагностику після ремонту, дуга повернення повинна мати жорстке обмеження кількості циклів (не більше 2–3 ітерацій), щоб не блокувати оператора в разі повторного виходу з ладу суміжних компонентів або наявності комбінованої несправності.
- **Досяжність термінальних дій (Leaf Reachability):** для кожного зареєстрованого симптому будь-яка можлива послідовність відповідей на тестові перевірки зобов'язана завершуватися вузлом типу `ACTION`. Неприпустимо залишати проміжний вузол перевірки без визначених вихідних переходів, оскільки в польових умовах це залишає техніка в глухому куті без подальших вказівок.
- **Відсутність ізольованих вузлів (No Orphan Nodes):** кожен створений у базі вузол тесту або дії повинен мати хоча б один активний шлях предків, починаючи від кореневих симптомів. Ізольовані вузли свідчать про застарілу або втрачену під час редагування документацію.
- **Детермінізм переходів:** кожен тестовий вузол повинен мати несуперечливі умови переходів без логічного перекриття критеріїв `PASS` та `FAIL`.

## Оптимізація вартості перевірок та ентропія пошуку

Під час проєктування дерева діагностики критично враховувати вартість кожної перевірки. Вартість вимірюється у часі, необхідності використання додаткових вимірювальних приладів або ризику пошкодження компонентів під час демонтажу. Перевірки впорядковуються за спаданням інформаційної ентропії на одиницю витраченого часу:
1. **Неінвазивні візуальні тести:** перевірка стану світлодіодів індикації, прапорців у веб-інтерфейсі або положення зовнішніх перемикачів (виконуються за 5–10 секунд без розбирання корпусу).
2. **Прямі електричні вимірювання на клемах:** контроль напруги живлення мультиметром, перевірка цілісності запобіжників (1–2 хвилини без демонтажу приладу з DIN-рейки).
3. **Вимірювання параметрів ліній зв'язку:** контроль опору термінації знеструмленої шини, перевірка наявності зміщення на лініях зв'язку (2–5 хвилин із відключенням окремих кабелів).
4. **Інвазивні та стендові тести:** підключення цифрового осцилографа для аналізу форми сигналу, заміна модулів із резервного фонду або демонтаж плати для лабораторного огляду (понад 10–20 хвилин).

Розміщення інвазивних і складних процедур на ранніх кроках графа є грубою інженерною помилкою, оскільки у 80% випадків причиною зупинки системи є елементарне падіння напруги в кабелі живлення або переплутана полярність сигнальних ліній.

## Безпека пам'яті та детермінізм у вбудованих системах

Під час перенесення діагностичного рушія у прошивку мікроконтролера (наприклад, для реалізації вбудованого помічника в сервісній консолі UART або CLI) висуваються суворі вимоги безпеки пам'яті за стандартами MISRA C та IEC 61508. Динамічне виділення пам'яті через купу (`malloc` / `free`) у критичних вбудованих вузлах забороняється через ризик фрагментації пам'яті або вичерпання ресурсів під час аварії.

Тому реалізація на мові C використовує статичні масиви фіксованого розміру з нульовим динамічним оверхедом, а рекурсивний обхід для перевірки досяжності обмежується глибиною стека та масивом прапорців відвіданих вузлів. Реалізація на C++20 демонструє сучасний архітектурний підхід для діагностичних утиліт вищого рівня, серверних бекендів підтримки та автоматизованих генераторів друкованих посібників, використовуючи строго типізовані перерахування, структуровані типи `std::optional` та обробку помилок через `std::expected`.

Нижче наведено повну реалізацію генератора, валідатора та інтерактивного рушія діагностичного графа:

:::tabs
@tab C99
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_NODES 32
#define MAX_TEXT_LEN 128

typedef enum {
    NODE_SYMPTOM,
    NODE_CHECK,
    NODE_ACTION
} NodeType;

typedef struct {
    uint32_t id;
    NodeType type;
    char description[MAX_TEXT_LEN];
    int32_t next_pass_id;  /* ID вузла при успішній перевірці (або єдиний перехід) */
    int32_t next_fail_id;  /* ID вузла при невдалій перевірці (тільки для NODE_CHECK) */
} DiagNode;

typedef struct {
    DiagNode nodes[MAX_NODES];
    size_t count;
} DiagGraph;

void graph_init(DiagGraph *graph) {
    if (!graph) return;
    graph->count = 0;
}

bool graph_add_node(DiagGraph *graph, uint32_t id, NodeType type, const char *desc,
                    int32_t pass_id, int32_t fail_id) {
    if (!graph || graph->count >= MAX_NODES) return false;
    
    DiagNode *node = &graph->nodes[graph->count++];
    node->id = id;
    node->type = type;
    strncpy(node->description, desc, MAX_TEXT_LEN - 1);
    node->description[MAX_TEXT_LEN - 1] = '\0';
    node->next_pass_id = pass_id;
    node->next_fail_id = fail_id;
    return true;
}

static const DiagNode* graph_find_node(const DiagGraph *graph, int32_t id) {
    if (!graph || id < 0) return NULL;
    for (size_t i = 0; i < graph->count; ++i) {
        if ((int32_t)graph->nodes[i].id == id) {
            return &graph->nodes[i];
        }
    }
    return NULL;
}

static bool check_path_to_action(const DiagGraph *graph, const DiagNode *curr,
                                 bool visited[MAX_NODES]) {
    if (!curr) return false;
    if (curr->type == NODE_ACTION) return true;

    /* Пошук індексу поточного вузла у масиві для захисту від зациклення */
    size_t idx = 0;
    for (; idx < graph->count; ++idx) {
        if (graph->nodes[idx].id == curr->id) break;
    }
    if (idx >= graph->count || visited[idx]) {
        return false; /* Виявлено нескінченний цикл без виходу на дію */
    }
    visited[idx] = true;

    bool pass_ok = false;
    bool fail_ok = false;

    if (curr->type == NODE_SYMPTOM) {
        const DiagNode *next = graph_find_node(graph, curr->next_pass_id);
        pass_ok = check_path_to_action(graph, next, visited);
        visited[idx] = false;
        return pass_ok;
    }

    if (curr->type == NODE_CHECK) {
        const DiagNode *pass_node = graph_find_node(graph, curr->next_pass_id);
        const DiagNode *fail_node = graph_find_node(graph, curr->next_fail_id);

        if (!pass_node || !fail_node) {
            visited[idx] = false;
            return false; /* Глухий кут: відсутній один із переходів */
        }

        bool visited_pass[MAX_NODES];
        bool visited_fail[MAX_NODES];
        memcpy(visited_pass, visited, sizeof(bool) * MAX_NODES);
        memcpy(visited_fail, visited, sizeof(bool) * MAX_NODES);

        pass_ok = check_path_to_action(graph, pass_node, visited_pass);
        fail_ok = check_path_to_action(graph, fail_node, visited_fail);
        visited[idx] = false;
        return pass_ok && fail_ok;
    }

    visited[idx] = false;
    return false;
}

bool graph_validate(const DiagGraph *graph, char *err_buf, size_t buf_size) {
    if (!graph || graph->count == 0) {
        snprintf(err_buf, buf_size, "Помилка: граф порожній");
        return false;
    }

    for (size_t i = 0; i < graph->count; ++i) {
        const DiagNode *n = &graph->nodes[i];
        if (n->type == NODE_SYMPTOM) {
            bool visited[MAX_NODES] = {false};
            if (!check_path_to_action(graph, n, visited)) {
                snprintf(err_buf, buf_size, "Помилка: від симптому [ID %u: %s] "
                         "немає повного шляху до дії", n->id, n->description);
                return false;
            }
        }
    }

    snprintf(err_buf, buf_size, "Граф валідний: усі гілки завершуються діями, циклів немає");
    return true;
}

void graph_simulate_troubleshooting(const DiagGraph *graph, uint32_t start_symptom_id) {
    const DiagNode *curr = graph_find_node(graph, (int32_t)start_symptom_id);
    if (!curr || curr->type != NODE_SYMPTOM) {
        printf("[СИСТЕМА] Симптом ID %u не знайдено.\n", start_symptom_id);
        return;
    }

    printf("\n=== ПОЧАТОК СЕАНСУ ДІАГНОСТИКИ ===\n");
    printf("[СИМПТОМ] ID %u: %s\n", curr->id, curr->description);
    curr = graph_find_node(graph, curr->next_pass_id);

    while (curr) {
        if (curr->type == NODE_CHECK) {
            printf("\n[ПЕРЕВІРКА ID %u]: %s\n", curr->id, curr->description);
            printf("Результат тесту (1 - ТАК/PASS, 0 - НІ/FAIL): 0\n");
            /* Симуляція негативного результату для демонстрації гілки */
            int choice = 0;
            if (choice == 1) {
                curr = graph_find_node(graph, curr->next_pass_id);
            } else {
                curr = graph_find_node(graph, curr->next_fail_id);
            }
        } else if (curr->type == NODE_ACTION) {
            printf("\n[ВІДНОВЛЮВАЛЬНА ДІЯ ID %u]:\n-> %s\n", curr->id, curr->description);
            printf("=== ДІАГНОСТИКУ ЗАВЕРШЕНО ===\n");
            break;
        } else {
            break;
        }
    }
}

int main(void) {
    DiagGraph g;
    graph_init(&g);

    /* Побудова тестового діагностичного дерева */
    graph_add_node(&g, 1, NODE_SYMPTOM, "Червоний світлодіод STATUS блимає кожні 2 с", 2, -1);
    graph_add_node(&g, 2, NODE_CHECK, "Напруга живлення V+ у межах 18..30 В DC?", 3, 101);
    graph_add_node(&g, 101, NODE_ACTION, "Замінити запобіжник 24 В та перевірити блок живлення", -1, -1);
    graph_add_node(&g, 3, NODE_CHECK, "Термінація RS-485 на шині дорівнює 60 Ом?", 4, 102);
    graph_add_node(&g, 102, NODE_ACTION, "Увімкнути термінатор 120 Ом на кінцевих вузлах", -1, -1);
    graph_add_node(&g, 4, NODE_ACTION, "Перевірити унікальність Modbus ID та швидкість зв'язку", -1, -1);

    char report[256];
    bool ok = graph_validate(&g, report, sizeof(report));
    printf("Результат валідації: %s\n", report);

    if (ok) {
        graph_simulate_troubleshooting(&g, 1);
    }
    return 0;
}
```
@tab C++20
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <optional>
#include <expected>
#include <memory>

enum class NodeKind {
    Symptom,
    Check,
    Action
};

struct DiagnosticNode {
    uint32_t id;
    NodeKind kind;
    std::string description;
    std::optional<uint32_t> next_pass_id;
    std::optional<uint32_t> next_fail_id;
};

class DiagnosticGraph {
public:
    void add_node(uint32_t id, NodeKind kind, std::string_view desc,
                  std::optional<uint32_t> pass_id = std::nullopt,
                  std::optional<uint32_t> fail_id = std::nullopt) {
        nodes_[id] = DiagnosticNode{
            .id = id,
            .kind = kind,
            .description = std::string(desc),
            .next_pass_id = pass_id,
            .next_fail_id = fail_id
        };
    }

    [[nodiscard]] std::expected<void, std::string> validate() const {
        if (nodes_.empty()) {
            return std::unexpected("Граф порожній: немає зареєстрованих станів");
        }

        for (const auto& [id, node] : nodes_) {
            if (node.kind == NodeKind::Symptom) {
                std::unordered_set<uint32_t> visited;
                auto res = check_reachability(node, visited);
                if (!res) {
                    return std::unexpected("Симптом [ID " + std::to_string(id) + 
                                           ": " + node.description + "] має дефект: " + res.error());
                }
            }
        }
        return {};
    }

    void execute_interactive(uint32_t symptom_id, const std::vector<bool>& simulated_answers = {}) const {
        auto it = nodes_.find(symptom_id);
        if (it == nodes_.end() || it->second.kind != NodeKind::Symptom) {
            std::cout << "[ПОМИЛКА] Вхідний симптом не знайдено.\n";
            return;
        }

        std::cout << "\n=== СЕАНС ДІАГНОСТИКИ (C++20 Engine) ===\n";
        std::cout << "[СИМПТОМ] ID " << it->second.id << ": " << it->second.description << "\n";

        if (!it->second.next_pass_id) return;
        uint32_t current_id = *it->second.next_pass_id;
        size_t answer_idx = 0;

        while (nodes_.contains(current_id)) {
            const auto& current = nodes_.at(current_id);
            if (current.kind == NodeKind::Check) {
                std::cout << "\n[ПЕРЕВІРКА ID " << current.id << "]: " << current.description << "\n";
                bool answer = false;
                if (answer_idx < simulated_answers.size()) {
                    answer = simulated_answers[answer_idx++];
                    std::cout << "Результат тесту (симуляція): " << (answer ? "ТАК / PASS" : "НІ / FAIL") << "\n";
                } else {
                    std::cout << "Результат тесту (за замовчуванням): НІ / FAIL\n";
                }

                if (answer) {
                    if (!current.next_pass_id) break;
                    current_id = *current.next_pass_id;
                } else {
                    if (!current.next_fail_id) break;
                    current_id = *current.next_fail_id;
                }
            } else if (current.kind == NodeKind::Action) {
                std::cout << "\n[ВІДНОВЛЮВАЛЬНА ДІЯ ID " << current.id << "]:\n-> "
                          << current.description << "\n";
                std::cout << "=== ВІДНОВЛЕННЯ ЗАВЕРШЕНО ===\n";
                break;
            } else {
                break;
            }
        }
    }

private:
    std::unordered_map<uint32_t, DiagnosticNode> nodes_;

    [[nodiscard]] std::expected<void, std::string> check_reachability(
        const DiagnosticNode& node, std::unordered_set<uint32_t>& visited) const {
        
        if (node.kind == NodeKind::Action) {
            return {};
        }

        if (visited.contains(node.id)) {
            return std::unexpected("Виявлено циклічну залежність у вузлі ID " + std::to_string(node.id));
        }
        visited.insert(node.id);

        if (node.kind == NodeKind::Symptom) {
            if (!node.next_pass_id || !nodes_.contains(*node.next_pass_id)) {
                return std::unexpected("Симптом не має вихідного переходу до перевірки");
            }
            auto res = check_reachability(nodes_.at(*node.next_pass_id), visited);
            visited.erase(node.id);
            return res;
        }

        if (node.kind == NodeKind::Check) {
            if (!node.next_pass_id || !nodes_.contains(*node.next_pass_id)) {
                return std::unexpected("Вузол перевірки ID " + std::to_string(node.id) + " не має гілки PASS");
            }
            if (!node.next_fail_id || !nodes_.contains(*node.next_fail_id)) {
                return std::unexpected("Вузол перевірки ID " + std::to_string(node.id) + " не має гілки FAIL");
            }

            auto visited_pass = visited;
            auto pass_res = check_reachability(nodes_.at(*node.next_pass_id), visited_pass);
            if (!pass_res) return pass_res;

            auto visited_fail = visited;
            auto fail_res = check_reachability(nodes_.at(*node.next_fail_id), visited_fail);
            if (!fail_res) return fail_res;

            visited.erase(node.id);
            return {};
        }

        visited.erase(node.id);
        return std::unexpected("Невідомий тип вузла");
    }
};

int main() {
    DiagnosticGraph diag;

    /* Створення вузлів графа діагностики промислового контролера */
    diag.add_node(1, NodeKind::Symptom, "Червоний світлодіод STATUS блимає кожні 2 с", 2);
    diag.add_node(2, NodeKind::Check, "Напруга живлення V+ у межах 18..30 В DC?", 3, 101);
    diag.add_node(101, NodeKind::Action, "Замінити запобіжник 24 В та перевірити блок живлення");
    diag.add_node(3, NodeKind::Check, "Термінація RS-485 на шині дорівнює 60 Ом?", 4, 102);
    diag.add_node(102, NodeKind::Action, "Увімкнути термінатор 120 Ом на кінцевих вузлах");
    diag.add_node(4, NodeKind::Action, "Перевірити унікальність Modbus ID та швидкість зв'язку");

    auto validation = diag.validate();
    if (validation) {
        std::cout << "[ВАЛІДАЦІЯ] Граф перевірено успішно: усі шляхи досягають відновлювальних дій.\n";
        diag.execute_interactive(1, {true, false});
    } else {
        std::cout << "[ПОМИЛКА ВАЛІДАЦІЇ] " << validation.error() << "\n";
    }

    return 0;
}
```
:::

## Серіалізація графа та інтеграція з польовою телеметрією

Для практичного використання у веб-сервісах технічної підтримки та мобільних додатках сервісних інженерів граф діагностики експортується у структурований JSON-формат. Це дозволяє централізовано оновлювати процедури ремонту на хмарному сервері та автоматично завантажувати оновлені діагностичні дерева в автономні польові планшети без необхідності повторного випуску друкованої документації:

```json
{
  "device_class": "Industrial-Gateway-V2",
  "schema_version": "1.2.0",
  "root_symptoms": [1],
  "nodes": [
    {
      "id": 1,
      "type": "SYMPTOM",
      "description": "Червоний світлодіод STATUS блимає кожні 2 с",
      "next_pass_id": 2
    },
    {
      "id": 2,
      "type": "CHECK",
      "description": "Напруга живлення V+ у межах 18..30 В DC?",
      "telemetry_source": "sys.pwr.v_in_mv",
      "auto_eval_min": 18000,
      "auto_eval_max": 30000,
      "next_pass_id": 3,
      "next_fail_id": 101
    },
    {
      "id": 101,
      "type": "ACTION",
      "description": "Замінити запобіжник 24 В та перевірити блок живлення",
      "required_tools": ["multimeter", "spare_fuse_2A"],
      "safety_warning": "Знеструмити щит перед заміною запобіжника!"
    }
  ]
}
```

За наявності каналу зв'язку з пристроєм інтерактивний діагностичний рушій може автоматично підставляти виміряні значення з потоку внутрішньої телеметрії (`telemetry_source`), автоматично проходячи базові перевірки живлення та шин зв'язку за долі секунди й одразу спрямовуючи техніка до локалізованого несправного вузла.

## Інженерні висновки для розробників інструкцій

Застосування формальних графів діагностики трансформує розділ пошуку несправностей із суб'єктивного опису симптомів у строгий інженерний алгоритм. Валідація відсутності зациклень та глухих кутів гарантує, що польовий інженер або оператор у стресовій ситуації не опиниться перед нерозв'язним станом системи. Комбінація чітких діагностичних дерев із протоколами самодіагностики скорочує середній час відновлення системи (Mean Time To Repair, MTTR) та виключає хибні повернення справного обладнання за гарантією.
