# ⚙️ Реалізація рушія обчислення дерев атак та оцінки DREAD

Побудова дерева атак на папері є зручною для концептуального обговорення під час первинних архітектурних сесій. Проте в реальних промислових системах дерево атак швидко розростається до сотень вузлів, які містять перехресні залежності, динамічно змінювані оцінки вартості та багаторівневі комбінації логічних операторів. Вручну розраховувати коммулятивні показники для такої структури стає неможливо. Щоб автоматизувати розрахунок мінімальних витрат нападника, пошук критичного шляху найвищої ймовірності та інтегральну калькуляцію рейтингу DREAD, необхідний програмний рушій обчислення дерев атак.

## Архітектура та модель даних

Програмний рушій представляє дерево як орієнтовану ієрархічну структуру вузлів, де кожен вузол належить до одного з трьох фундаментальних типів:

1. **Листковий вузол (Leaf Node):** Представляє атомарну дію зловмисника, яка не підлягає подальшій архітектурній декомпозиції в межах поточної моделі (наприклад, «викрасти токен через фішинг» або «підібрати пароль до тестового облікового запису»). Листок містить базові емпіричні метрики:
   - `cost` — фінансові або апаратні витрати нападника (у грошових одиницях);
   - `probability` — апріорна ймовірність успіху дії за умови виділення необхідного ресурсу (`0.0 ≤ p ≤ 1.0`);
   - `skill_level` — мінімальний рівень кваліфікації зловмисника (ціле число від 1 до 4);
   - `dread` — структура з п'яти числових компонентів DREAD.

2. **Логічний диз'юнктивний вузол (OR Node):** Представляє мету або підціль, яка досягається, якщо спрацює **хоча б один** із дочірніх векторів атаки. Оскільки раціональний нападник прагне мінімізувати зусилля та максимізувати шанси на успіх:
   - Мінімальна вартість вузла `cost` дорівнює найменшій вартості серед усіх дочірніх гілок;
   - Сукупна ймовірність успіху `probability` обчислюється через імовірність об'єднання незалежних подій: `P(OR) = 1 - ∏(1 - P_i)`;
   - Необхідний рівень кваліфікації обирається за найпростішим доступним шляхом: `min(skill_i)`;
   - Рейтинг DREAD успадковує вектор тієї дочірньої гілки, яка створює найвищий сукупний ризик.

3. **Логічний кон'юнктивний вузол (AND Node):** Представляє складну атаку, яка вимагає **одночасного й обов'язкового** виконання всіх без винятку дочірніх етапів (наприклад, «знайти вразливість нульового дня І створити надійний експлойт І обійти мережевий моніторинг»). Для кон'юнкції правила агрегації змінюються:
   - Підсумкова вартість вузла `cost` дорівнює сумі витрат на всі обов'язкові етапи: `∑ cost_i`;
   - Сукупна ймовірність успіху `probability` різко падає і дорівнює добутку ймовірностей усіх ланок ланцюга: `∏ P_i`;
   - Рівень кваліфікації визначається найскладнішим кроком у ланцюгу (вузьким місцем): `max(skill_i)`;
   - Оцінки DREAD усереднюються між усіма обов'язковими етапами атаки.

## Алгоритм рекурсивного обходу та часова складність

Обчислення показників дерева виконується за допомогою рекурсивного обходу в глибину (Depth-First Search, DFS) у порядку зворотного обходу (post-order traversal). Рушій спочатку спускається до листкових вузлів дерева, а потім піднімається вгору, обчислюючи агреговані значення для батьківських вузлів лише після того, як повністю розраховано всіх їхніх нащадків.

Часова складність алгоритму є строго лінійною відносно розміру графа:
```
T(V, E) = O(|V| + |E|)
```
де `|V|` — кількість вузлів у дереві, а `|E|` — кількість ребер між ними. Оскільки в дереві кількість ребер строго дорівнює `|V| - 1`, повний розрахунок навіть для великих дерев із десятками тисяч вузлів виконується за частки мілісекунди. Просторова складність становить `O(H)`, де `H` — максимальна висота дерева, що відповідає глибині стека викликів рекурсії.

## Програмна реалізація трьома мовами

Нижче наведено робочу реалізацію рушія на C (із ручним керуванням пам'яттю), ідіоматичному сучасному C++ (на базі розумних вказівників `std::unique_ptr` та RAII) та Python.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    NODE_LEAF,
    NODE_OR,
    NODE_AND
} NodeType;

typedef struct {
    double damage;
    double reproducibility;
    double exploitability;
    double affected_users;
    double discoverability;
} DreadScore;

typedef struct AttackNode {
    char name[64];
    NodeType type;
    double cost;
    double probability;
    int skill_level;
    DreadScore dread;

    struct AttackNode** children;
    size_t children_count;
    size_t children_capacity;
} AttackNode;

AttackNode* create_leaf(const char* name, double cost, double probability, int skill, DreadScore dread) {
    AttackNode* node = (AttackNode*)malloc(sizeof(AttackNode));
    if (!node) return NULL;
    strncpy(node->name, name, sizeof(node->name) - 1);
    node->name[sizeof(node->name) - 1] = '\0';
    node->type = NODE_LEAF;
    node->cost = cost;
    node->probability = probability;
    node->skill_level = skill;
    node->dread = dread;
    node->children = NULL;
    node->children_count = 0;
    node->children_capacity = 0;
    return node;
}

AttackNode* create_operator(const char* name, NodeType type) {
    AttackNode* node = (AttackNode*)malloc(sizeof(AttackNode));
    if (!node) return NULL;
    strncpy(node->name, name, sizeof(node->name) - 1);
    node->name[sizeof(node->name) - 1] = '\0';
    node->type = type;
    node->cost = 0.0;
    node->probability = 0.0;
    node->skill_level = 0;
    memset(&node->dread, 0, sizeof(DreadScore));
    node->children = NULL;
    node->children_count = 0;
    node->children_capacity = 0;
    return node;
}

bool add_child(AttackNode* parent, AttackNode* child) {
    if (!parent || !child || parent->type == NODE_LEAF) return false;
    if (parent->children_count == parent->children_capacity) {
        size_t new_cap = parent->children_capacity == 0 ? 4 : parent->children_capacity * 2;
        AttackNode** new_buf = (AttackNode**)realloc(parent->children, new_cap * sizeof(AttackNode*));
        if (!new_buf) return false;
        parent->children = new_buf;
        parent->children_capacity = new_cap;
    }
    parent->children[parent->children_count++] = child;
    return true;
}

double calculate_dread_total(const DreadScore* d) {
    return (d->damage + d->reproducibility + d->exploitability + d->affected_users + d->discoverability) / 5.0;
}

void evaluate_tree(AttackNode* root) {
    if (!root || root->type == NODE_LEAF) return;

    for (size_t i = 0; i < root->children_count; ++i) {
        evaluate_tree(root->children[i]);
    }

    if (root->children_count == 0) return;

    if (root->type == NODE_OR) {
        double min_cost = root->children[0]->cost;
        double prod_inv_p = 1.0 - root->children[0]->probability;
        int min_skill = root->children[0]->skill_level;
        DreadScore max_dread = root->children[0]->dread;

        for (size_t i = 1; i < root->children_count; ++i) {
            AttackNode* c = root->children[i];
            if (c->cost < min_cost) min_cost = c->cost;
            prod_inv_p *= (1.0 - c->probability);
            if (c->skill_level < min_skill) min_skill = c->skill_level;
            if (calculate_dread_total(&c->dread) > calculate_dread_total(&max_dread)) {
                max_dread = c->dread;
            }
        }
        root->cost = min_cost;
        root->probability = 1.0 - prod_inv_p;
        root->skill_level = min_skill;
        root->dread = max_dread;
    } else if (root->type == NODE_AND) {
        double sum_cost = 0.0;
        double prod_p = 1.0;
        int max_skill = 0;
        DreadScore avg_dread = {0};

        for (size_t i = 0; i < root->children_count; ++i) {
            AttackNode* c = root->children[i];
            sum_cost += c->cost;
            prod_p *= c->probability;
            if (c->skill_level > max_skill) max_skill = c->skill_level;
            avg_dread.damage += c->dread.damage;
            avg_dread.reproducibility += c->dread.reproducibility;
            avg_dread.exploitability += c->dread.exploitability;
            avg_dread.affected_users += c->dread.affected_users;
            avg_dread.discoverability += c->dread.discoverability;
        }
        double n = (double)root->children_count;
        avg_dread.damage /= n;
        avg_dread.reproducibility /= n;
        avg_dread.exploitability /= n;
        avg_dread.affected_users /= n;
        avg_dread.discoverability /= n;

        root->cost = sum_cost;
        root->probability = prod_p;
        root->skill_level = max_skill;
        root->dread = avg_dread;
    }
}

void print_tree_report(const AttackNode* node, int indent) {
    if (!node) return;
    for (int i = 0; i < indent; ++i) printf("  ");
    const char* type_str = node->type == NODE_LEAF ? "LEAF" : (node->type == NODE_OR ? "OR" : "AND");
    printf("[%s] %s | Cost: %.0f грн | Prob: %.4f (%.2f%%) | Skill: %d | DREAD: %.1f/10\n",
           type_str, node->name, node->cost, node->probability, node->probability * 100.0,
           node->skill_level, calculate_dread_total(&node->dread));

    for (size_t i = 0; i < node->children_count; ++i) {
        print_tree_report(node->children[i], indent + 1);
    }
}

void free_tree(AttackNode* node) {
    if (!node) return;
    for (size_t i = 0; i < node->children_count; ++i) {
        free_tree(node->children[i]);
    }
    free(node->children);
    free(node);
}

int main(void) {
    AttackNode* root = create_operator("Злам платіжного шлюзу", NODE_OR);

    AttackNode* branch1 = create_operator("API підробка", NODE_AND);
    DreadScore d1 = {8.0, 7.0, 6.0, 9.0, 5.0};
    AttackNode* l1 = create_leaf("Фішинг API-ключа", 25000.0, 0.20, 2, d1);
    DreadScore d2 = {6.0, 8.0, 5.0, 4.0, 7.0};
    AttackNode* l2 = create_leaf("BGP/IP spoofing", 15000.0, 0.30, 3, d2);
    add_child(branch1, l1);
    add_child(branch1, l2);

    AttackNode* branch2 = create_operator("SQL-ін'єкція", NODE_AND);
    DreadScore d3 = {9.0, 9.0, 8.0, 10.0, 6.0};
    AttackNode* l3 = create_leaf("Виявлення SQLi", 10000.0, 0.10, 2, d3);
    DreadScore d4 = {7.0, 6.0, 5.0, 8.0, 4.0};
    AttackNode* l4 = create_leaf("Обхід WAF", 20000.0, 0.25, 3, d4);
    add_child(branch2, l3);
    add_child(branch2, l4);

    add_child(root, branch1);
    add_child(root, branch2);

    evaluate_tree(root);
    print_tree_report(root, 0);

    free_tree(root);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <numeric>
#include <algorithm>
#include <iomanip>
#include <limits>

enum class NodeType {
    Leaf,
    Or,
    And
};

struct DreadScore {
    double damage{0.0};
    double reproducibility{0.0};
    double exploitability{0.0};
    double affected_users{0.0};
    double discoverability{0.0};

    [[nodiscard]] double total() const noexcept {
        return (damage + reproducibility + exploitability + affected_users + discoverability) / 5.0;
    }
};

class AttackNode {
public:
    std::string name;
    NodeType type;
    double cost{0.0};
    double probability{0.0};
    int skill_level{0};
    DreadScore dread{};
    std::vector<std::unique_ptr<AttackNode>> children;

    AttackNode(std::string node_name, NodeType node_type, double c = 0.0, double p = 0.0,
               int skill = 0, DreadScore d = {})
        : name(std::move(node_name)), type(node_type), cost(c), probability(p),
          skill_level(skill), dread(d) {}

    void add_child(std::unique_ptr<AttackNode> child) {
        children.push_back(std::move(child));
    }

    void evaluate() {
        for (const auto& child : children) {
            child->evaluate();
        }

        if (type == NodeType::Leaf || children.empty()) {
            return;
        }

        if (type == NodeType::Or) {
            cost = std::numeric_limits<double>::max();
            double prod_inv_p = 1.0;
            skill_level = std::numeric_limits<int>::max();
            double max_dread_val = -1.0;

            for (const auto& child : children) {
                cost = std::min(cost, child->cost);
                prod_inv_p *= (1.0 - child->probability);
                skill_level = std::min(skill_level, child->skill_level);
                if (child->dread.total() > max_dread_val) {
                    max_dread_val = child->dread.total();
                    dread = child->dread;
                }
            }
            probability = 1.0 - prod_inv_p;
        } else if (type == NodeType::And) {
            cost = 0.0;
            probability = 1.0;
            skill_level = 0;
            DreadScore sum_dread{};

            for (const auto& child : children) {
                cost += child->cost;
                probability *= child->probability;
                skill_level = std::max(skill_level, child->skill_level);
                sum_dread.damage += child->dread.damage;
                sum_dread.reproducibility += child->dread.reproducibility;
                sum_dread.exploitability += child->dread.exploitability;
                sum_dread.affected_users += child->dread.affected_users;
                sum_dread.discoverability += child->dread.discoverability;
            }

            const double n = static_cast<double>(children.size());
            dread = DreadScore{
                sum_dread.damage / n,
                sum_dread.reproducibility / n,
                sum_dread.exploitability / n,
                sum_dread.affected_users / n,
                sum_dread.discoverability / n
            };
        }
    }

    void print_report(int indent = 0) const {
        const std::string pad(indent * 2, ' ');
        const char* type_label = type == NodeType::Leaf ? "LEAF" : (type == NodeType::Or ? "OR" : "AND");
        std::cout << pad << "[" << type_label << "] " << name
                  << " | Cost: " << std::fixed << std::setprecision(0) << cost << " грн"
                  << " | Prob: " << std::setprecision(4) << probability
                  << " (" << std::setprecision(2) << probability * 100.0 << "%)"
                  << " | Skill: " << skill_level
                  << " | DREAD: " << std::setprecision(1) << dread.total() << "/10\n";

        for (const auto& child : children) {
            child->print_report(indent + 1);
        }
    }
};

int main() {
    auto root = std::make_unique<AttackNode>("Злам платіжного шлюзу", NodeType::Or);

    auto branch1 = std::make_unique<AttackNode>("API підробка", NodeType::And);
    branch1->add_child(std::make_unique<AttackNode>("Фішинг API-ключа", NodeType::Leaf, 25000.0, 0.20, 2, DreadScore{8.0, 7.0, 6.0, 9.0, 5.0}));
    branch1->add_child(std::make_unique<AttackNode>("BGP/IP spoofing", NodeType::Leaf, 15000.0, 0.30, 3, DreadScore{6.0, 8.0, 5.0, 4.0, 7.0}));

    auto branch2 = std::make_unique<AttackNode>("SQL-ін'єкція", NodeType::And);
    branch2->add_child(std::make_unique<AttackNode>("Виявлення SQLi", NodeType::Leaf, 10000.0, 0.10, 2, DreadScore{9.0, 9.0, 8.0, 10.0, 6.0}));
    branch2->add_child(std::make_unique<AttackNode>("Обхід WAF", NodeType::Leaf, 20000.0, 0.25, 3, DreadScore{7.0, 6.0, 5.0, 8.0, 4.0}));

    root->add_child(std::move(branch1));
    root->add_child(std::move(branch2));

    root->evaluate();
    root->print_report();

    return 0;
}
```
```py
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class NodeType(Enum):
    LEAF = "LEAF"
    OR = "OR"
    AND = "AND"


@dataclass
class DreadScore:
    damage: float = 0.0
    reproducibility: float = 0.0
    exploitability: float = 0.0
    affected_users: float = 0.0
    discoverability: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.damage
            + self.reproducibility
            + self.exploitability
            + self.affected_users
            + self.discoverability
        ) / 5.0


@dataclass
class AttackNode:
    name: str
    node_type: NodeType
    cost: float = 0.0
    probability: float = 0.0
    skill_level: int = 0
    dread: DreadScore = field(default_factory=DreadScore)
    children: List["AttackNode"] = field(default_factory=list)

    def add_child(self, child: "AttackNode") -> None:
        self.children.append(child)

    def evaluate(self) -> None:
        for child in self.children:
            child.evaluate()

        if self.node_type == NodeType.LEAF or not self.children:
            return

        if self.node_type == NodeType.OR:
            self.cost = min(c.cost for c in self.children)
            prod_inv = 1.0
            for c in self.children:
                prod_inv *= (1.0 - c.probability)
            self.probability = 1.0 - prod_inv
            self.skill_level = min(c.skill_level for c in self.children)
            self.dread = max(self.children, key=lambda c: c.dread.total).dread

        elif self.node_type == NodeType.AND:
            self.cost = sum(c.cost for c in self.children)
            prod_p = 1.0
            for c in self.children:
                prod_p *= c.probability
            self.probability = prod_p
            self.skill_level = max(c.skill_level for c in self.children)

            n = len(self.children)
            self.dread = DreadScore(
                damage=sum(c.dread.damage for c in self.children) / n,
                reproducibility=sum(c.dread.reproducibility for c in self.children) / n,
                exploitability=sum(c.dread.exploitability for c in self.children) / n,
                affected_users=sum(c.dread.affected_users for c in self.children) / n,
                discoverability=sum(c.dread.discoverability for c in self.children) / n,
            )

    def print_report(self, indent: int = 0) -> None:
        pad = "  " * indent
        print(
            f"{pad}[{self.node_type.value}] {self.name} | "
            f"Cost: {self.cost:.0f} грн | "
            f"Prob: {self.probability:.4f} ({self.probability * 100:.2f}%) | "
            f"Skill: {self.skill_level} | "
            f"DREAD: {self.dread.total:.1f}/10"
        )
        for child in self.children:
            child.print_report(indent + 1)


if __name__ == "__main__":
    root = AttackNode("Злам платіжного шлюзу", NodeType.OR)

    branch1 = AttackNode("API підробка", NodeType.AND)
    branch1.add_child(AttackNode("Фішинг API-ключа", NodeType.LEAF, cost=25000.0, probability=0.20, skill_level=2, dread=DreadScore(8, 7, 6, 9, 5)))
    branch1.add_child(AttackNode("BGP/IP spoofing", NodeType.LEAF, cost=15000.0, probability=0.30, skill_level=3, dread=DreadScore(6, 8, 5, 4, 7)))

    branch2 = AttackNode("SQL-ін'єкція", NodeType.AND)
    branch2.add_child(AttackNode("Виявлення SQLi", NodeType.LEAF, cost=10000.0, probability=0.10, skill_level=2, dread=DreadScore(9, 9, 8, 10, 6)))
    branch2.add_child(AttackNode("Обхід WAF", NodeType.LEAF, cost=20000.0, probability=0.25, skill_level=3, dread=DreadScore(7, 6, 5, 8, 4)))

    root.add_child(branch1)
    root.add_child(branch2)

    root.evaluate()
    root.print_report()
```
:::

## Інтерпретація результатів обчислення

Запуск скомпільованого бінарного файлу виводить ієрархічну структуру зведених показників безпеки:

```text
[OR] Злам платіжного шлюзу | Cost: 30000 грн | Prob: 0.0835 (8.35%) | Skill: 2 | DREAD: 8.4/10
  [AND] API підробка | Cost: 40000 грн | Prob: 0.0600 (6.00%) | Skill: 3 | DREAD: 6.0/10
    [LEAF] Фішинг API-ключа | Cost: 25000 грн | Prob: 0.2000 (20.00%) | Skill: 2 | DREAD: 7.0/10
    [LEAF] BGP/IP spoofing | Cost: 15000 грн | Prob: 0.3000 (30.00%) | Skill: 3 | DREAD: 6.0/10
  [AND] SQL-ін'єкція | Cost: 30000 грн | Prob: 0.0250 (2.50%) | Skill: 3 | DREAD: 8.4/10
    [LEAF] Виявлення SQLi | Cost: 10000 грн | Prob: 0.1000 (10.00%) | Skill: 2 | DREAD: 8.4/10
    [LEAF] Обхід WAF | Cost: 20000 грн | Prob: 0.2500 (25.00%) | Skill: 3 | DREAD: 6.0/10
```

Отримані значення дозволяють зробити чіткі інженерні висновки:
1. **Критичний вектор атаки за вартістю:** Гілка «SQL-ін'єкція» є дешевшою для зловмисника (30 000 грн проти 40 000 грн) і вимагає нижчого початкового бар'єра кваліфікації (рівень 2 для виявлення діри проти обов'язкового рівня 3 на обох кроках першої гілки).
2. **Критичний вектор за ймовірністю:** Гілка «API підробка» має вищу сукупну ймовірність успіху (6.0% проти 2.5%), що робить її небезпечнішою за умови наявності у нападника достатнього фінансування.
3. **Пріоритет усунення за DREAD:** Листок «Виявлення SQLi» має найвищий індивідуальний рейтинг DREAD (8.4/10), оскільки успішна SQL-ін'єкція призводить до максимального збитку (Damage = 9) та компрометації всіх користувачів (Affected Users = 10). Впровадження параметризованих запитів на цьому листку повністю блокує всю праву гілку AND.

## Інженерні компроміси та типові пастки реалізації

Під час проектування та експлуатації рушіїв дерев атак у виробничому середовищі необхідно враховувати чотири фундаментальні підводні камені:

1. **Проблема спільних листкових вузлів (DAG vs Tree):** У реальних системах одна й та сама атомарна вразливість (наприклад, «викрасти майстер-ключ шифрування») може використовуватися в десятках різних сценаріїв атак. Якщо структурувати модель як чисте дерево, цей листок дублюється, що спотворює загальну ймовірність компрометації системи через помилкове припущення про незалежність подій. Правильною моделлю для таких випадків є спрямований ациклічний граф (DAG), а розрахунок імовірностей вимагає побудови таблиць істинності або використання бінарних діаграм рішень (Binary Decision Diagrams, BDD).
2. **Захист від зациклення під час динамічного парсингу:** Якщо дерево формується автоматично з інфраструктурних маніфестів, взаємні виклики між мікросервісами можуть створити циклічні залежності («Сервіс А викликає Б, який викликає А»). Наївний рекурсивний DFS у такому разі призводить до вичерпання стека викликів (stack overflow). Рушій зобов'язаний виконувати перевірку графа на ациклічність перед початком обчислень.
3. **Ідіома керування ресурсами:** У мові C граф будується на динамічних масивах вказівників, де кожна операція додавання дитини потенційно викликає `realloc`. Помилка у звільненні пам'яті (`free_tree`) або подвійне вивільнення спільного вузла призводить до витоку пам'яті чи аварійного завершення процесу. У C++ застосування `std::unique_ptr` повністю ізолює пам'ять і автоматично знищує все піддерево за принципом RAII, коли кореневий об'єкт виходить з області видимості.
