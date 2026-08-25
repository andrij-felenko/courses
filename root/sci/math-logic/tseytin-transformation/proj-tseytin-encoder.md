# ⚙️ Реалізація Цейтін-кодера булевих виразів мовами C та C++

Побудова працюючого транслятора синтаксичних дерев формул у КНФ демонструє виділення допоміжних змінних та генерацію диз'юнктів для логічних операторів.

Реалізація алгоритму Цейтіна є фундаментальним мостом між абстрактним логічним виразом (представленим у вигляді абстрактного синтаксичного дерева, AST, або спрямованого ациклічного графа, DAG) та лінійним текстовим представленням у форматі DIMACS CNF, яке зчитується SAT-розв'язувачами.

## 1. Архітектурні принципи побудови Цейтін-кодера

При проектуванні програмного кодера Цейтіна вирішуються три основні архітектурні задачі:

1. **Представлення вихідного синтаксичного дерева (AST):** Кожен вузол дерева описується варіантним типом (або ієрархією успадкування), який містить код операції (`AND`, `OR`, `NOT`, `IMPLIES`, `XOR`) та вказівники на дочірні операнди. Для листків AST зберігається числовий індикатор вхідної змінної.
2. **Управління лічильником нових змінних:** Кодер підтримує глобальний стан лічильника змінних `max_var`. Під час першого візиту до внутрішнього вузла виконується генерація нового унікального індексу змінної `fresh_var = ++max_var`.
3. **Акумуляція дизюнктів КНФ:** Сгенеровані диз'юнкти зберігаються у динамічному масиві (векторі). Після повного обходу дерева сформована таблиця диз'юнктів разом із одиничним кореневим диз'юнкт виводиться у потік `stdout` або файл.

Нижче наведено ідіоматичні реалізації Цейтін-транслятора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Типи вузлів синтаксичного дерева */
typedef enum {
    NODE_VAR,
    NODE_NOT,
    NODE_AND,
    NODE_OR,
    NODE_IMPLIES,
    NODE_XOR
} NodeType;

/* Структура вузла AST */
typedef struct ASTNode {
    NodeType type;
    int var_id;                  /* Номер змінної (для NODE_VAR) */
    struct ASTNode* left;
    struct ASTNode* right;
} ASTNode;

/* Динамічний масив диз'юнктів */
typedef struct {
    int* lits;
    size_t size;
    size_t capacity;
} Clause;

typedef struct {
    Clause* data;
    size_t count;
    size_t capacity;
    int max_var;
} TseytinEncoder;

/* Створення вузлів AST */
ASTNode* create_var(int var_id) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = NODE_VAR;
    node->var_id = var_id;
    node->left = NULL;
    node->right = NULL;
    return node;
}

ASTNode* create_unary(NodeType type, ASTNode* child) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var_id = 0;
    node->left = child;
    node->right = NULL;
    return node;
}

ASTNode* create_binary(NodeType type, ASTNode* left, ASTNode* right) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var_id = 0;
    node->left = left;
    node->right = right;
    return node;
}

void free_ast(ASTNode* node) {
    if (!node) return;
    free_ast(node->left);
    free_ast(node->right);
    free(node);
}

/* Управління кодером Цейтіна */
TseytinEncoder* encoder_create(int num_inputs) {
    TseytinEncoder* enc = (TseytinEncoder*)malloc(sizeof(TseytinEncoder));
    enc->count = 0;
    enc->capacity = 16;
    enc->data = (Clause*)malloc(enc->capacity * sizeof(Clause));
    enc->max_var = num_inputs;
    return enc;
}

void encoder_add_clause(TseytinEncoder* enc, const int* lits, size_t size) {
    if (enc->count >= enc->capacity) {
        enc->capacity *= 2;
        enc->data = (Clause*)realloc(enc->data, enc->capacity * sizeof(Clause));
    }
    Clause* c = &enc->data[enc->count++];
    c->size = size;
    c->capacity = size;
    c->lits = (int*)malloc(size * sizeof(int));
    for (size_t i = 0; i < size; ++i) {
        c->lits[i] = lits[i];
    }
}

void encoder_free(TseytinEncoder* enc) {
    if (!enc) return;
    for (size_t i = 0; i < enc->count; ++i) {
        free(enc->data[i].lits);
    }
    free(enc->data);
    free(enc);
}

int encoder_fresh_var(TseytinEncoder* enc) {
    return ++(enc->max_var);
}

/* Рекурсивний обхід AST та генерація КНФ-диз'юнктів */
int tseytin_transform_node(TseytinEncoder* enc, const ASTNode* node) {
    if (!node) return 0;
    if (node->type == NODE_VAR) {
        return node->var_id;
    }

    int left_var = tseytin_transform_node(enc, node->left);
    int right_var = tseytin_transform_node(enc, node->right);
    int out_var = encoder_fresh_var(enc);

    switch (node->type) {
        case NODE_NOT: {
            /* out_var <-> NOT left_var */
            int c1[] = {-out_var, -left_var};
            int c2[] = {out_var, left_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            break;
        }
        case NODE_AND: {
            /* out_var <-> (left_var AND right_var) */
            int c1[] = {-out_var, left_var};
            int c2[] = {-out_var, right_var};
            int c3[] = {out_var, -left_var, -right_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            encoder_add_clause(enc, c3, 3);
            break;
        }
        case NODE_OR: {
            /* out_var <-> (left_var OR right_var) */
            int c1[] = {out_var, -left_var};
            int c2[] = {out_var, -right_var};
            int c3[] = {-out_var, left_var, right_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            encoder_add_clause(enc, c3, 3);
            break;
        }
        case NODE_IMPLIES: {
            /* out_var <-> (left_var -> right_var) */
            int c1[] = {out_var, left_var};
            int c2[] = {out_var, -right_var};
            int c3[] = {-out_var, -left_var, right_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            encoder_add_clause(enc, c3, 3);
            break;
        }
        case NODE_XOR: {
            /* out_var <-> (left_var XOR right_var) */
            int c1[] = {-out_var, -left_var, -right_var};
            int c2[] = {-out_var, left_var, right_var};
            int c3[] = {out_var, -left_var, right_var};
            int c4[] = {out_var, left_var, -right_var};
            encoder_add_clause(enc, c1, 3);
            encoder_add_clause(enc, c2, 3);
            encoder_add_clause(enc, c3, 3);
            encoder_add_clause(enc, c4, 3);
            break;
        }
        default:
            break;
    }
    return out_var;
}

void print_dimacs(const TseytinEncoder* enc, int root_var) {
    /* Кількість клауз = згенеровані + 1 для кореня */
    printf("p cnf %d %zu\n", enc->max_var, enc->count + 1);
    for (size_t i = 0; i < enc->count; ++i) {
        for (size_t j = 0; j < enc->data[i].size; ++j) {
            printf("%d ", enc->data[i].lits[j]);
        }
        printf("0\n");
    }
    printf("%d 0\n", root_var);
}

int main(void) {
    /* Побудова формули F = (A AND B) OR (NOT C) */
    /* Вхідні змінні: 1=A, 2=B, 3=C */
    ASTNode* varA = create_var(1);
    ASTNode* varB = create_var(2);
    ASTNode* varC = create_var(3);

    ASTNode* and_node = create_binary(NODE_AND, varA, varB);
    ASTNode* not_node = create_unary(NODE_NOT, varC);
    ASTNode* root = create_binary(NODE_OR, and_node, not_node);

    TseytinEncoder* enc = encoder_create(3);
    int root_var = tseytin_transform_node(enc, root);

    printf("c Згенерований DIMACS CNF для виразу (A AND B) OR (NOT C)\n");
    print_dimacs(enc, root_var);

    encoder_free(enc);
    free_ast(root);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>

enum class NodeType {
    Var,
    Not,
    And,
    Or,
    Implies,
    Xor
};

// Ідіоматична ієрархія вузлів AST з RAII керуванням пам'яттю
class ASTNode {
public:
    virtual ~ASTNode() = default;
    virtual NodeType getType() const = 0;
};

class VarNode : public ASTNode {
    int m_varId;
public:
    explicit VarNode(int id) : m_varId(id) {}
    NodeType getType() const override { return NodeType::Var; }
    int getId() const { return m_varId; }
};

class UnaryNode : public ASTNode {
    NodeType m_type;
    std::unique_ptr<ASTNode> m_child;
public:
    UnaryNode(NodeType type, std::unique_ptr<ASTNode> child)
        : m_type(type), m_child(std::move(child)) {}
    NodeType getType() const override { return m_type; }
    const ASTNode* getChild() const { return m_child.get(); }
};

class BinaryNode : public ASTNode {
    NodeType m_type;
    std::unique_ptr<ASTNode> m_left;
    std::unique_ptr<ASTNode> m_right;
public:
    BinaryNode(NodeType type, std::unique_ptr<ASTNode> left, std::unique_ptr<ASTNode> right)
        : m_type(type), m_left(std::move(left)), m_right(std::move(right)) {}
    NodeType getType() const override { return m_type; }
    const ASTNode* getLeft() const { return m_left.get(); }
    const ASTNode* getRight() const { return m_right.get(); }
};

// Клас кодера Цейтіна
class TseytinEncoder {
    using Clause = std::vector<int>;
    std::vector<Clause> m_clauses;
    int m_maxVar;

public:
    explicit TseytinEncoder(int numInputs) : m_maxVar(numInputs) {}

    int freshVar() {
        return ++m_maxVar;
    }

    void addClause(Clause clause) {
        m_clauses.push_back(std::move(clause));
    }

    int transform(const ASTNode* node) {
        if (!node) return 0;

        if (node->getType() == NodeType::Var) {
            return static_cast<const VarNode*>(node)->getId();
        }

        if (node->getType() == NodeType::Not) {
            auto unary = static_cast<const UnaryNode*>(node);
            int childVar = transform(unary->getChild());
            int outVar = freshVar();
            
            // outVar <-> NOT childVar
            addClause({-outVar, -childVar});
            addClause({outVar, childVar});
            return outVar;
        }

        auto binary = static_cast<const BinaryNode*>(node);
        int leftVar = transform(binary->getLeft());
        int rightVar = transform(binary->getRight());
        int outVar = freshVar();

        switch (node->getType()) {
            case NodeType::And:
                // outVar <-> (leftVar AND rightVar)
                addClause({-outVar, leftVar});
                addClause({-outVar, rightVar});
                addClause({outVar, -leftVar, -rightVar});
                break;

            case NodeType::Or:
                // outVar <-> (leftVar OR rightVar)
                addClause({outVar, -leftVar});
                addClause({outVar, -rightVar});
                addClause({-outVar, leftVar, rightVar});
                break;

            case NodeType::Implies:
                // outVar <-> (leftVar -> rightVar)
                addClause({outVar, leftVar});
                addClause({outVar, -rightVar});
                addClause({-outVar, -leftVar, rightVar});
                break;

            case NodeType::Xor:
                // outVar <-> (leftVar XOR rightVar)
                addClause({-outVar, -leftVar, -rightVar});
                addClause({-outVar, leftVar, rightVar});
                addClause({outVar, -leftVar, rightVar});
                addClause({outVar, leftVar, -rightVar});
                break;

            default:
                break;
        }

        return outVar;
    }

    void exportDimacs(std::ostream& os, int rootVar) const {
        os << "p cnf " << m_maxVar << " " << (m_clauses.size() + 1) << "\n";
        for (const auto& clause : m_clauses) {
            for (int lit : clause) {
                os << lit << " ";
            }
            os << "0\n";
        }
        os << rootVar << " 0\n";
    }
};

int main() {
    // Вхідні змінні: 1=A, 2=B, 3=C
    auto varA = std::make_unique<VarNode>(1);
    auto varB = std::make_unique<VarNode>(2);
    auto varC = std::make_unique<VarNode>(3);

    auto andNode = std::make_unique<BinaryNode>(NodeType::And, std::move(varA), std::move(varB));
    auto notNode = std::make_unique<UnaryNode>(NodeType::Not, std::move(varC));
    auto root = std::make_unique<BinaryNode>(NodeType::Or, std::move(andNode), std::move(notNode));

    TseytinEncoder encoder(3);
    int rootVar = encoder.transform(root.get());

    std::cout << "c C++ Tseytin Encoder DIMACS Output\n";
    encoder.exportDimacs(std::cout, rootVar);

    return 0;
}
```
:::

## 2. Покроковий трасування обходу синтаксичного дерева

Простежимо виконання функції `tseytin_transform_node()` для формули `F = (A ∧ B) ∨ ¬C`.
Початкові вхідні змінні мають індекси: `A = 1`, `B = 2`, `C = 3`. Лічильник `max_var = 3`.

1. **Перший крок:** Рекурсивний виклик для піддерева `(A ∧ B)`.
   - Обхід лівого листка `A`: повертає `left_var = 1`.
   - Обхід правого листка `B`: повертає `right_var = 2`.
   - Виклик `fresh_var()`: генерує змінну `out_var = 4` для вузла AND (`x₁`).
   - Додавання КНФ-блоку для AND:
     - Диз'юнкт 1: `(-4, 1)`
     - Диз'юнкт 2: `(-4, 2)`
     - Диз'юнкт 3: `(4, -1, -2)`
   - Повертає індекс `4`.

2. **Другий крок:** Рекурсивний виклик для піддерева `¬C`.
   - Обхід листка `C`: повертає `left_var = 3`.
   - Виклик `fresh_var()`: генерує змінну `out_var = 5` для вузла NOT (`x₃`).
   - Додавання КНФ-блоку для NOT:
     - Диз'юнкт 4: `(-5, -3)`
     - Диз'юнкт 5: `(5, 3)`
   - Повертає індекс `5`.

3. **Третій крок:** Обробка кореневого вузла `OR`.
   - Лівий операнд є результати першого кроку: `left_var = 4`.
   - Правий операнд є результатом другого кроку: `right_var = 5`.
   - Виклик `fresh_var()`: генерує змінну `out_var = 6` для кореневого вузла OR (`x₂`).
   - Додавання КНФ-блоку для OR:
     - Диз'юнкт 6: `(6, -4)`
     - Диз'юнкт 7: `(6, -5)`
     - Диз'юнкт 8: `(-6, 4, 5)`
   - Повертає індекс `6` як `root_var`.

4. **Завершальний крок:** Функція `print_dimacs()` додає одиничний кореневий диз'юнкт `(6)` та виводить підсумковий заголовок `p cnf 6 9`.

## 3. Порівняння розбіжностей підходів реалізації у C та C++

Порівняння двох реалізацій висвітлює принципові відмінності між процедурним кодуванням на C та ідіоматичним об'єктно-орієнтованим дизайном на C++:

### 3.1. Управління пам'яттю та тривалістю життя об'єктів (Memory Lifetime)

- **Реалізація мовою C:** Вимагає ручного виділення пам'яті через `malloc` та обов'язкового рекурсивного обходу дерева для її звільнення процедурою `free_ast()`. Динамічний масив КНФ-диз'юнктів керується вручну за допомогою функції `realloc`. Будь-який передчасний вихід із функції (наприклад, через помилку) без виклику `encoder_free()` спричиняє витік пам'яті (Memory Leak).
- **Реалізація мовою C++:** Застосовує паттерн RAII (Resource Acquisition Is Initialization). Дерево формули будується з використанням розумних вказівників `std::unique_ptr<ASTNode>`, що гарантує деструкцію всіх вузлів AST при руйнуванні кореневого об'єкта. Диз'юнкти зберігаються у стандартному контейнері `std::vector<std::vector<int>>`, який автоматично масштабує пам'ять без ризику витоків.

### 3.2. Типобезпека та поліморфізм

- **У мові C:** Вузол дерева описується єдиною структурою `ASTNode`, яка містить поля для всіх можливих типів вузлів. Поля `left` та `right` лишаються невикористаними (NULL) для листків, що призводить до надлишкового витрачання пам'яті.
- **У мові C++:** Використовується чітка ієрархія класів із віртуальними функціями (`ASTNode`, `VarNode`, `UnaryNode`, `BinaryNode`). Це дозволяє ізолювати конкретні дані вузла (наприклад `m_varId` для листка) у відповідному класі, уникаючи порожніх полів.

## 4. Практичні оптимізації: Спільні підформули (CSE / DAG Encoding)

Наведена базова реалізація обходить формулу як дерево. Якщо одна й та сама підформула `(A ∧ B)` зустрічається у формулі у кількох місцях, дерево містить дубльовані вузли, і алгоритм створить для них кілька різних допоміжних змінних `x₄` та `x₇`.

Для оптимізації промислові кодери (такі як у Z3 чи Yosys) застосовують **мемоізацію (Hash Consing)**:
1. Замість дерева створюється спрямований ациклічний граф (DAG).
2. Перед генерацією нової змінної кодер перевіряє хеш-таблицю вже оброблених підформул за сигнатурою `(NodeType, left_var, right_var)`.
3. Якщо така підформула вже кодувалася раніше і їй було зіставлено змінну `x₄`, кодер миттєво повертає `x₄` без генерації нових диз'юнктів.

Це дозволяє додатково скоротити кількість диз'юнктів у КНФ для симетричних логічних схем (наприклад, суматорів та помножувачів).

## 5. Обробка крайових випадків та пряме підключення In-memory API

При інтеграції Цейтін-кодера у виробничі системи виникають три додаткові практичні вимоги:

1. **Пряме розв'язання в оперативній пам'яті (In-memory SAT Integration):** Виводити текстові дані у формат DIMACS на диск є надто повільним процесом для мільйонів перевірок. У C++ проектах клас `TseytinEncoder` замість запису у файл транслює `std::vector<Clause>` напряму у виклики `solver->addClause()` бібліотек MiniSAT або Z3 C++ API.
2. **Обробка глибоких дерев формул (Stack Overflow Prevention):** Рекурсивне розгортання `tseytin_transform_node()` може вичерпати системний стек (Stack Overflow) при глибині вкладеності понад 100 000 вузлів. Для захисту рекурсію замінюють явним ітеративним обходом з власною структурою стека у купі (Heap Stack) або застосовують алгоритм постфіксного розкладу.
3. **Обробка константних листків:** Якщо AST містить константи `TRUE` або `FALSE`, кодер усуває їх ще на етапі обходу, уникаючи створення зайвих змінних і КНФ-диз'юнктів для константних виразів.
