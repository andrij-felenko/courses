# ⚙️ Реалізація інтерпретатора логіки першого порядку (Model Checker)

Обчислення істинності формул логіки першого порядку (First-Order Logic, FO) на скінченних реляційних структурах (графах, мережах, реляційних базах даних) називається задачею **перевірки моделей (Model Checking)**. На відміну від задачі здійсненності булевих формул (SAT), де алгоритм шукає невідому інтерпретацію змінних для задоволення виразу, у перевірці моделей сама реляційна структура є фіксованим вхідним об'єктом. Завдання інженерного інтерпретатора полягає у тому, щоб перевірити, чи володіє представлена структура властивістю, сформульованою декларативним логічним виразом.

Практична реалізація інтерпретатора логіки першого порядку вимагає побудови абстрактного синтаксичного дерева (AST), керування стек-фреймами змінних та реалізації ефективного рекурсивного обчислювача. Нижче детально розібрано архітектурні принципи, алгоритмічні деталі та повні повнофункціональні реалізації обчислювального рушія мовами C та C++.

## 1. Архітектурні принципи та представлення даних у пам'яті

Для виконання обчислень логічний вираз піддається синтаксичному аналізу та перетворюється на абстрактне синтаксичне дерево (Abstract Syntax Tree, AST).

Кожен вузол AST-дерева відповідає одному з логічних операторів або предикатів:

1. **Атомарні предикати:**
   - Предикат ребра `E(u, v)` перевіряє наявність орієнтованого зв'язку у матриці суміжності графа між змінною `u` та змінною `v`.
   - Предикат рівності `u = v` перевіряє збіг елементів домену.
   - Предикат порядку `u < v` аналізує канонічний індекс елементів у впорядкованих структурах.
2. **Логічні оператори (Connectives):**
   - Унарне заперечення `NOT` рекурсивно інвертує результат обчислення лівого піддерева.
   - Бінарна кон'юнкція `AND` та диз'юнкція `OR` обчислюють комбінацію результатів двох піддерев із використанням оптимізації короткого замикання (Short-Circuit Evaluation).
3. **Кванторні вузли (Quantifiers):**
   - Екзистенційний квантор `EXISTS(x, body)` послідовно підставляє у змінну `x` кожен елемент домену `v ∈ {0, ..., n-1}` і повертає `true`, як тільки знайдеться хоча б один елемент, на якому тіло формули істинне.
   - Універсальний квантор `FORALL(x, body)` повертає `false`, як тільки знайдеться хоча б один елемент домену, для якого тіло формули хибне.

### Складність обчислень та стек середовища (Environment)

Під час рекурсивного обходу AST-дерева інтерпретатор підтримує **середовище зв'язування змінних (Variable Binding Environment)**. Середовище зберігає поточні значення елементів домену `U`, призначені кванторами для кожної змінної `x₁, x₂, ..., xₖ`.

Якщо кванторна глибина формули дорівнює `k`, а розмір домену графа дорівнює `n = |V|`, то у найгіршому випадку обчислювач відвідає `nᵏ` комбінацій значень змінних. При фіксованій формулі `φ` часова складність оцінки становить `O(|φ| · nᵏ)`, що строго відповідає теорії дескриптивної складності (належність задачі перевірки даних до класу **AC⁰**). Просторова складність обчислення обмежена лише глибиною стека викликів `O(k + |φ|)` для збереження поточного фрейму змінних.

## 2. Реалізація мовою C (Низькорівневий низькокаліберний рушій)

У реалізації мовою C для максимальної швидкодії граф представлений матрицею суміжності у базі статичного пам'ятного буфера, а середовище змінних передається у вигляді плоского масиву індексів.

:::tabs
```c
/* C Implementation: FO Model Checker on Finite Graphs */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 16
#define MAX_NODES 1000

typedef struct {
    int num_vertices;
    bool adj[MAX_NODES][MAX_NODES];
} Graph;

typedef enum {
    NODE_PRED_EDGE,   /* E(x, y) */
    NODE_PRED_EQ,     /* x == y */
    NODE_NOT,         /* NOT child */
    NODE_AND,         /* child1 AND child2 */
    NODE_OR,          /* child1 OR child2 */
    NODE_EXISTS,      /* EXISTS var_id child */
    NODE_FORALL       /* FORALL var_id child */
} NodeType;

typedef struct ASTNode {
    NodeType type;
    int var1;
    int var2;
    struct ASTNode *left;
    struct ASTNode *right;
} ASTNode;

/* Створення атомарного предиката E(var1, var2) або (var1 == var2) */
ASTNode* create_pred(NodeType type, int var1, int var2) {
    ASTNode *node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var1 = var1;
    node->var2 = var2;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/* Створення логічного оператора NOT, AND, OR */
ASTNode* create_op(NodeType type, ASTNode *left, ASTNode *right) {
    ASTNode *node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var1 = -1;
    node->var2 = -1;
    node->left = left;
    node->right = right;
    return node;
}

/* Створення квантора EXISTS(var_id, body) або FORALL(var_id, body) */
ASTNode* create_quantifier(NodeType type, int var_id, ASTNode *body) {
    ASTNode *node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var1 = var_id;
    node->var2 = -1;
    node->left = body;
    node->right = NULL;
    return node;
}

void free_ast(ASTNode *node) {
    if (!node) return;
    free_ast(node->left);
    free_ast(node->right);
    free(node);
}

/* Рекурсивний обчислювач істинності формули щодо середовища env */
bool eval_fo(const ASTNode *node, const Graph *g, int *env) {
    if (!node) return false;

    switch (node->type) {
        case NODE_PRED_EDGE: {
            int u = env[node->var1];
            int v = env[node->var2];
            return g->adj[u][v];
        }
        case NODE_PRED_EQ: {
            return env[node->var1] == env[node->var2];
        }
        case NODE_NOT: {
            return !eval_fo(node->left, g, env);
        }
        case NODE_AND: {
            return eval_fo(node->left, g, env) && eval_fo(node->right, g, env);
        }
        case NODE_OR: {
            return eval_fo(node->left, g, env) || eval_fo(node->right, g, env);
        }
        case NODE_EXISTS: {
            int var_id = node->var1;
            for (int val = 0; val < g->num_vertices; val++) {
                env[var_id] = val;
                if (eval_fo(node->left, g, env)) {
                    return true;
                }
            }
            return false;
        }
        case NODE_FORALL: {
            int var_id = node->var1;
            for (int val = 0; val < g->num_vertices; val++) {
                env[var_id] = val;
                if (!eval_fo(node->left, g, env)) {
                    return false;
                }
            }
            return true;
        }
    }
    return false;
}

int main(void) {
    Graph g;
    g.num_vertices = 4;
    memset(g.adj, 0, sizeof(g.adj));

    /* Створюємо трикутник: 0 -> 1, 1 -> 2, 2 -> 0 */
    g.adj[0][1] = true;
    g.adj[1][2] = true;
    g.adj[2][0] = true;

    /* Формуємо формулу наявності трикутника K3: 
       ∃x ∃y ∃z (E(x,y) ∧ E(y,z) ∧ E(z,x)) */
    ASTNode *e_xy = create_pred(NODE_PRED_EDGE, 0, 1);
    ASTNode *e_yz = create_pred(NODE_PRED_EDGE, 1, 2);
    ASTNode *e_zx = create_pred(NODE_PRED_EDGE, 2, 0);

    ASTNode *conj1 = create_op(NODE_AND, e_xy, e_yz);
    ASTNode *conj2 = create_op(NODE_AND, conj1, e_zx);

    ASTNode *exists_z = create_quantifier(NODE_EXISTS, 2, conj2);
    ASTNode *exists_y = create_quantifier(NODE_EXISTS, 1, exists_z);
    ASTNode *exists_x = create_quantifier(NODE_EXISTS, 0, exists_y);

    int env[MAX_VARS] = {0};
    bool has_triangle = eval_fo(exists_x, &g, env);

    printf("Результат перевірки формули K3: %s\n", has_triangle ? "TRUE" : "FALSE");

    free_ast(exists_x);
    return 0;
}
```
```cpp
// C++ Implementation: Object-Oriented Idiomatic FO Model Checker
#include <iostream>
#include <vector>
#include <memory>
#include <unordered_map>
#include <string>

class Graph {
public:
    explicit Graph(size_t vertices) : num_vertices_(vertices), adj_(vertices, std::vector<bool>(vertices, false)) {}

    void add_edge(size_t u, size_t v) {
        if (u < num_vertices_ && v < num_vertices_) {
            adj_[u][v] = true;
        }
    }

    [[nodiscard]] bool has_edge(size_t u, size_t v) const {
        if (u < num_vertices_ && v < num_vertices_) {
            return adj_[u][v];
        }
        return false;
    }

    [[nodiscard]] size_t size() const noexcept { return num_vertices_; }

private:
    size_t num_vertices_;
    std::vector<std::vector<bool>> adj_;
};

using Environment = std::unordered_map<int, size_t>;

class ASTNode {
public:
    virtual ~ASTNode() = default;
    [[nodiscard]] virtual bool evaluate(const Graph& g, Environment& env) const = 0;
};

class EdgePredicate : public ASTNode {
public:
    EdgePredicate(int u_var, int v_var) : u_var_(u_var), v_var_(v_var) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return g.has_edge(env.at(u_var_), env.at(v_var_));
    }

private:
    int u_var_;
    int v_var_;
};

class EqualityPredicate : public ASTNode {
public:
    EqualityPredicate(int u_var, int v_var) : u_var_(u_var), v_var_(v_var) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return env.at(u_var_) == env.at(v_var_);
    }

private:
    int u_var_;
    int v_var_;
};

class LogicalAnd : public ASTNode {
public:
    LogicalAnd(std::unique_ptr<ASTNode> left, std::unique_ptr<ASTNode> right)
        : left_(std::move(left)), right_(std::move(right)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return left_->evaluate(g, env) && right_->evaluate(g, env);
    }

private:
    std::unique_ptr<ASTNode> left_;
    std::unique_ptr<ASTNode> right_;
};

class LogicalNot : public ASTNode {
public:
    explicit LogicalNot(std::unique_ptr<ASTNode> child) : child_(std::move(child)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        return !child_->evaluate(g, env);
    }

private:
    std::unique_ptr<ASTNode> child_;
};

class ExistsQuantifier : public ASTNode {
public:
    ExistsQuantifier(int var_id, std::unique_ptr<ASTNode> body)
        : var_id_(var_id), body_(std::move(body)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        for (size_t val = 0; val < g.size(); ++val) {
            env[var_id_] = val;
            if (body_->evaluate(g, env)) {
                return true;
            }
        }
        return false;
    }

private:
    int var_id_;
    std::unique_ptr<ASTNode> body_;
};

class ForAllQuantifier : public ASTNode {
public:
    ForAllQuantifier(int var_id, std::unique_ptr<ASTNode> body)
        : var_id_(var_id), body_(std::move(body)) {}

    bool evaluate(const Graph& g, Environment& env) const override {
        for (size_t val = 0; val < g.size(); ++val) {
            env[var_id_] = val;
            if (!body_->evaluate(g, env)) {
                return false;
            }
        }
        return true;
    }

private:
    int var_id_;
    std::unique_ptr<ASTNode> body_;
};

int main() {
    Graph g(4);
    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 0);

    // Formulate ∃x ∃y ∃z (E(x,y) ∧ E(y,z) ∧ E(z,x))
    auto e_xy = std::make_unique<EdgePredicate>(0, 1);
    auto e_yz = std::make_unique<EdgePredicate>(1, 2);
    auto e_zx = std::make_unique<EdgePredicate>(2, 0);

    auto conj1 = std::make_unique<LogicalAnd>(std::move(e_xy), std::move(e_yz));
    auto conj2 = std::make_unique<LogicalAnd>(std::move(conj1), std::move(e_zx));

    auto exists_z = std::make_unique<ExistsQuantifier>(2, std::move(conj2));
    auto exists_y = std::make_unique<ExistsQuantifier>(1, std::move(exists_z));
    auto exists_x = std::make_unique<ExistsQuantifier>(0, std::move(exists_y));

    Environment env;
    bool has_k3 = exists_x->evaluate(g, env);

    std::cout << "Результат перевірки формули K3 (C++): " << (has_k3 ? "TRUE" : "FALSE") << "\n";

    return 0;
}
```
:::

## 3. Детальний аналіз реалізації мовою C++

Версія мовою C++ демонструє сучасний об'єктно-орієнтований підхід із суворим дотриманням принципів керування ресурсами через RAII (Resource Acquisition Is Initialization).

Ключовими відмінностями реалізації C++ є:

1. **Ієрархія класів та поліморфізм:** Абстрактний базовий клас `ASTNode` оголошує чистий віртуальний метод `evaluate()`. Кожен підтип вузла (предикат ребра, предикат рівності, логічні оператори, квантори) реалізує власну специфічну обчислительну логіку. Це усуває потребу у розгалуженні через `switch-case` та робить систему легко розширюваною новими логічними операторами (наприклад, оператором нерухомої точки LFP).
2. **Розумні вказівники та RAII:** Використання `std::unique_ptr<ASTNode>` гарантує унікальне володіння піддеревами та автоматичне очищення пам'яті у деструкторі при виході з області видимості. Це унеможливлює витоки пам'яті, які потенційно можуть виникнути у версії C при помилках у рекурсивній функції `free_ast()`.
3. **Інкапсуляція середовища:** Середовище прив'язки змінних закодовано через `std::unordered_map<int, size_t>`, що забезпечує безпечну підтримку довільної кількості змінних без ризику виходу за межі фіксованого static-масиву.

## 4. Практичні інженерні пастки та методи оптимізації

Під час розробки та промислової експлуатації інтерпретаторів логіки першого порядку необхідно враховувати такі інженерні пастки та оптимізаційні прийоми:

### Інженерні пастки:

1. **Експоненціальне уповільнення при глибокому вкладенні кванторів:** Додавання кожного нового квантора `∃` або `∀` збільшує кількість ітерацій в `n` разів. Для формули з кванторною глибиною `k = 6` на графі з `n = 100` вершин кількість обчислювальних кроків сягає `100⁶ = 10¹²` операцій, що призводить до тривалого зависання інтерпретатора.
2. **Конфлікти імен змінних (Variable Shadowing):** Якщо формула містить вкладені квантори по однаковій змінній (наприклад, `∃x (E(x, y) ∧ ∃x E(x, z))`), внутрішній квантор перезаписує значення `x` у середовищі `env`, що призводить до спотворення результату для зовнішніх підформул. Для запобігання цьому обов'язково виконується попередній крок альфа-конверсії (автоматичного перейменування змінних унікальними індексами).
3. **Відсутність перевірки вільних змінних:** Спроба оцінити предикат `E(u, v)` без попереднього призначення значення змінним у кванторах генерує виняток відсутності ключа `std::out_of_range` у середовищі C++ або звернення до неініціалізованої пам'яті в C.

### Методи оптимізації швидкодії:

1. **Коротке замикання (Short-Circuiting):** Вузол `ExistsQuantifier` припиняє перебір елементів домену негайно після того, як перший елемент дав `true`. Аналогічно `ForAllQuantifier` миттєво повертає `false` при першому невдалому елементі.
2. **Індексація відношень та хешування ребер:** Представлення графа через матрицю суміжності або хеш-таблицю `std::unordered_set` дозволяє перевіряти наявність ребра `E(u, v)` за константний час `O(1)`.
3. **Мемоїзація підформул:** Для однакових замкнених підформул результат обчислення можна кешувати в хеш-таблиці щодо поточного стану прив'язаних змінних.
