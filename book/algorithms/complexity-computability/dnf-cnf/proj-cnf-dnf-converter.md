# ⚙️ Алгоритми та реалізація конвертера булевих форм

Ця вставка містить практичну алгоритмічну реалізацію програмного конвертера булевих виразів у канонічні диз'юнктивні (ДНФ) та кон'юнктивні (КНФ) нормальні форми. У ній детально розглянуто два підходи до конструювання форм — через генерацію таблиць істинності (побудова досконалих ДДНФ/ДКНФ) та через рекурсивне перетворення синтаксичного дерева AST з використанням законів Де Моргана та дистрибутивності, а також наведено готові ідіоматичні реалізації мовами C та C++.

## 1. Архітектура та підходи до побудови конвертера

Перетворення довільного логічного виразу у нормальну форму є фундаментальним етапом логічного синтезу та передпроцесорної обробки для SAT-розв'язувачів. На практиці застосовують два принципово різні підходи:

1. **Табличний метод (Побудова ДДНФ / ДКНФ):**
   - Обчислюються значення виразу для всіх `2ⁿ` поєднання змінних.
   - За 1-наборами генеруються мінтерми для ДДНФ.
   - За 0-наборами генеруються макстерми для ДКНФ.
   - *Перевага:* Гарантована побудова досконалих форм, простий детермінований алгоритм.
   - *Обмеження:* Часова та просторова складність `O(2ⁿ)` робить метод придатним для малого числа змінних (`n ≤ 20`).

2. **Синтаксичний метод (Трансформація дерева AST):**
   - Побудова синтаксичного дерева виразу.
   - Усунення імплікацій (`A → B ≡ ¬A ∨ B`) та еквівалентностей (`A ≡ B ≡ (¬A ∨ B) ∧ (A ∨ ¬B)`).
   - Застосування законів Де Моргана для спускання заперечень до листків (утворення NNF, Negation Normal Form).
   - Застосування законів дистрибутивності для винесення `∨` (для ДНФ) або `∧` (для КНФ) на верхній рівень.
   - *Перевага:* Збереження структурної еквівалентності без генерації повної таблиці.
   - *Обмеження:* У найгіршому випадку розкриття дужок спричиняє експоненційний роздув `O(2ⁿ)` диз'юнктів.

## 2. Алгоритми табличної побудови канонічних форм

Табличний конвертер обходить повне дерево можливих підстановок за допомогою бітових масок. Для булевої функції від `n` змінних будується цикл від `0` до `2ⁿ - 1`. На кожній ітерації `i` значення `j`-ї змінної визначається `j`-м бітом числа `i`.

Для побудови ДДНФ (досконалої ДНФ):
- Якщо обчислення AST на наборі `i` видає `true`, створюється кон'юнкт, який містить усі `n` змінних.
- Змінна `xⱼ` входить без заперечення, якщо її біт дорівнює `1`, і з запереченням `¬xⱼ`, якщо її біт дорівнює `0`.

Для побудови ДКНФ (досконалої КНФ):
- Якщо обчислення AST на наборі `i` видає `false`, створюється диз'юнкт, який містить усі `n` змінних.
- Змінна `xⱼ` входить без заперечення, якщо її біт дорівнює `0`, і з запереченням `¬xⱼ`, якщо її біт дорівнює `1`.

Ця симетрія випливає безпосередньо з теореми про дуальність канонічних форм та гарантує точність результату.

## 3. Покрокове розтрасування роботи алгоритму для виразу `(A ∧ B) ∨ ¬C`

Розглянемо покрокову роботу алгоритму для вхідного виразу `(A ∧ B) ∨ ¬C` від 3 змінних. Кількість можливих наборів дорівнює `2³ = 8`.

1. **Набір 0 (0,0,0):** `A=0, B=0, C=0`.
   - `(0 ∧ 0) ∨ ¬0 = 0 ∨ 1 = 1`.
   - Результат = 1 ⇒ Генеруємо мінтерм ДДНФ: `(¬A ∧ ¬B ∧ ¬C)`.
2. **Набір 1 (0,0,1):** `A=0, B=0, C=1`.
   - `(0 ∧ 0) ∨ ¬1 = 0 ∨ 0 = 0`.
   - Результат = 0 ⇒ Генеруємо макстерм ДКНФ: `(A ∨ B ∨ ¬C)`.
3. **Набір 2 (0,1,0):** `A=0, B=1, C=0`.
   - `(0 ∧ 1) ∨ ¬0 = 0 ∨ 1 = 1`.
   - Результат = 1 ⇒ Генеруємо мінтерм ДДНФ: `(¬A ∧ B ∧ ¬C)`.
4. **Набір 3 (0,1,1):** `A=0, B=1, C=1`.
   - `(0 ∧ 1) ∨ ¬1 = 0 ∨ 0 = 0`.
   - Результат = 0 ⇒ Генеруємо макстерм ДКНФ: `(A ∨ ¬B ∨ ¬C)`.
5. **Набір 4 (1,0,0):** `A=1, B=0, C=0`.
   - `(1 ∧ 0) ∨ ¬0 = 0 ∨ 1 = 1`.
   - Результат = 1 ⇒ Генеруємо мінтерм ДДНФ: `(A ∧ ¬B ∧ ¬C)`.
6. **Набір 5 (1,0,1):** `A=1, B=0, C=1`.
   - `(1 ∧ 0) ∨ ¬1 = 0 ∨ 0 = 0`.
   - Результат = 0 ⇒ Генеруємо макстерм ДКНФ: `(¬A ∨ B ∨ ¬C)`.
7. **Набір 6 (1,1,0):** `A=1, B=1, C=0`.
   - `(1 ∧ 1) ∨ ¬0 = 1 ∨ 1 = 1`.
   - Результат = 1 ⇒ Генеруємо мінтерм ДДНФ: `(A ∧ B ∧ ¬C)`.
8. **Набір 7 (1,1,1):** `A=1, B=1, C=1`.
   - `(1 ∧ 1) ∨ ¬1 = 1 ∨ 0 = 1`.
   - Результат = 1 ⇒ Генеруємо мінтерм ДДНФ: `(A ∧ B ∧ C)`.

У результаті збирання мінтермів отримуємо ДДНФ з 5 кон'юнктів, а збиранням макстермів — ДКНФ з 3 диз'юнктів.

## 4. Програмна реалізація мовами C та C++

Нижче наведено паралельні реалізації табличного конвертера булевих форм. Версія мовою C застосовує явні структурні вказівники та ручне управління динамічною пам'яттю, тоді як версія мовою C++ демонструє об'єктно-орієнтований підхід із розумними вказівниками `std::unique_ptr` та контейнерами стандартної бібліотеки.

:::tabs
```c
/* 
 * Табличний конвертер булевих форм мовою C (C99)
 * Генерація ДДНФ та ДКНФ за обчисленням значення AST для n змінних.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 10
#define MAX_CLAUSES 1024

typedef enum {
    NODE_VAR,
    NODE_NOT,
    NODE_AND,
    NODE_OR
} NodeType;

typedef struct ASTNode {
    NodeType type;
    char var_name;
    struct ASTNode* left;
    struct ASTNode* right;
} ASTNode;

/* Створення вузла змінної */
ASTNode* create_var(char name) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = NODE_VAR;
    node->var_name = name;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/* Створення унарного/бінарного вузла */
ASTNode* create_op(NodeType type, ASTNode* left, ASTNode* right) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var_name = '\0';
    node->left = left;
    node->right = right;
    return node;
}

/* Звільнення пам'яті AST */
void free_ast(ASTNode* node) {
    if (!node) return;
    free_ast(node->left);
    free_ast(node->right);
    free(node);
}

/* Рекурсивна оцінка AST під задану підстановку змінних */
bool eval_ast(const ASTNode* node, const bool env[26]) {
    if (!node) return false;
    switch (node->type) {
        case NODE_VAR:
            return env[node->var_name - 'A'];
        case NODE_NOT:
            return !eval_ast(node->left, env);
        case NODE_AND:
            return eval_ast(node->left, env) && eval_ast(node->right, env);
        case NODE_OR:
            return eval_ast(node->left, env) || eval_ast(node->right, env);
    }
    return false;
}

/* Друк ДДНФ (Досконала ДНФ) за 1-наборами */
void print_sdnf(const ASTNode* root, const char vars[], int var_count) {
    bool env[26] = {false};
    int total_combinations = 1 << var_count;
    bool first_term = true;

    printf("SDNF: ");
    for (int i = 0; i < total_combinations; ++i) {
        /* Присвоєння значень змінним за бітами числа i */
        for (int j = 0; j < var_count; ++j) {
            env[vars[j] - 'A'] = (i >> (var_count - 1 - j)) & 1;
        }

        if (eval_ast(root, env)) {
            if (!first_term) {
                printf(" ∨ ");
            }
            first_term = false;
            printf("(");
            for (int j = 0; j < var_count; ++j) {
                bool val = env[vars[j] - 'A'];
                if (j > 0) printf(" ∧ ");
                if (!val) {
                    printf("¬%c", vars[j]);
                } else {
                    printf("%c", vars[j]);
                }
            }
            printf(")");
        }
    }
    if (first_term) {
        printf("0 (Тотожна хибність)");
    }
    printf("\n");
}

/* Друк ДКНФ (Досконала КНФ) за 0-наборами */
void print_sknf(const ASTNode* root, const char vars[], int var_count) {
    bool env[26] = {false};
    int total_combinations = 1 << var_count;
    bool first_clause = true;

    printf("SKNF: ");
    for (int i = 0; i < total_combinations; ++i) {
        for (int j = 0; j < var_count; ++j) {
            env[vars[j] - 'A'] = (i >> (var_count - 1 - j)) & 1;
        }

        /* ДКНФ будується за наборами, де формула дорівнює 0 */
        if (!eval_ast(root, env)) {
            if (!first_clause) {
                printf(" ∧ ");
            }
            first_clause = false;
            printf("(");
            for (int j = 0; j < var_count; ++j) {
                bool val = env[vars[j] - 'A'];
                if (j > 0) printf(" ∨ ");
                /* Для 0 береться змінна без заперечення, для 1 - з запереченням */
                if (val) {
                    printf("¬%c", vars[j]);
                } else {
                    printf("%c", vars[j]);
                }
            }
            printf(")");
        }
    }
    if (first_clause) {
        printf("1 (Тотожна істинність)");
    }
    printf("\n");
}

int main(void) {
    /* Побудова формули: (A ∧ B) ∨ ¬C */
    ASTNode* node_a = create_var('A');
    ASTNode* node_b = create_var('B');
    ASTNode* node_ab = create_op(NODE_AND, node_a, node_b);

    ASTNode* node_c = create_var('C');
    ASTNode* node_not_c = create_op(NODE_NOT, node_c, NULL);

    ASTNode* root = create_op(NODE_OR, node_ab, node_not_c);

    char vars[] = {'A', 'B', 'C'};
    int var_count = 3;

    printf("--- Табличний конвертер ДДНФ / ДКНФ (Мова C) ---\n");
    print_sdnf(root, vars, var_count);
    print_sknf(root, vars, var_count);

    free_ast(root);
    return 0;
}
```
```cpp
/*
 * Об'єктно-орієнтований конвертер булевих форм мовою C++ (C++20)
 * Використання std::unique_ptr, RAII, std::vector та ідіоматичних контейнерів.
 */
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <unordered_map>
#include <cmath>

enum class OpType { Var, Not, And, Or };

class ASTNode {
public:
    OpType type;
    char var_name{'\0'};
    std::unique_ptr<ASTNode> left;
    std::unique_ptr<ASTNode> right;

    explicit ASTNode(char name) : type(OpType::Var), var_name(name) {}
    ASTNode(OpType op, std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r = nullptr)
        : type(op), left(std::move(l)), right(std::move(r)) {}

    [[nodiscard]] bool evaluate(const std::unordered_map<char, bool>& env) const {
        switch (type) {
            case OpType::Var:
                return env.at(var_name);
            case OpType::Not:
                return !left->evaluate(env);
            case OpType::And:
                return left->evaluate(env) && right->evaluate(env);
            case OpType::Or:
                return left->evaluate(env) || right->evaluate(env);
        }
        return false;
    }
};

class BooleanFormConverter {
private:
    const ASTNode& root_;
    std::vector<char> vars_;

public:
    BooleanFormConverter(const ASTNode& root, std::vector<char> vars)
        : root_(root), vars_(std::move(vars)) {}

    [[nodiscard]] std::string generate_sdnf() const {
        std::string result;
        const size_t num_vars = vars_.size();
        const size_t total_rows = 1ULL << num_vars;
        bool first_term = true;

        for (size_t i = 0; i < total_rows; ++i) {
            std::unordered_map<char, bool> env;
            for (size_t j = 0; j < num_vars; ++j) {
                env[vars_[j]] = ((i >> (num_vars - 1 - j)) & 1ULL) != 0;
            }

            if (root_.evaluate(env)) {
                if (!first_term) {
                    result += " ∨ ";
                }
                first_term = false;
                result += "(";
                for (size_t j = 0; j < num_vars; ++j) {
                    if (j > 0) result += " ∧ ";
                    if (!env[vars_[j]]) {
                        result += "¬";
                    }
                    result += vars_[j];
                }
                result += ")";
            }
        }
        return first_term ? "0" : result;
    }

    [[nodiscard]] std::string generate_sknf() const {
        std::string result;
        const size_t num_vars = vars_.size();
        const size_t total_rows = 1ULL << num_vars;
        bool first_clause = true;

        for (size_t i = 0; i < total_rows; ++i) {
            std::unordered_map<char, bool> env;
            for (size_t j = 0; j < num_vars; ++j) {
                env[vars_[j]] = ((i >> (num_vars - 1 - j)) & 1ULL) != 0;
            }

            if (!root_.evaluate(env)) {
                if (!first_clause) {
                    result += " ∧ ";
                }
                first_clause = false;
                result += "(";
                for (size_t j = 0; j < num_vars; ++j) {
                    if (j > 0) result += " ∨ ";
                    if (env[vars_[j]]) {
                        result += "¬";
                    }
                    result += vars_[j];
                }
                result += ")";
            }
        }
        return first_clause ? "1" : result;
    }
};

int main() {
    // Побудова виразу: (A ∨ B) ∧ (¬A ∨ C)
    auto node_a1 = std::make_unique<ASTNode>('A');
    auto node_b = std::make_unique<ASTNode>('B');
    auto clause1 = std::make_unique<ASTNode>(OpType::Or, std::move(node_a1), std::move(node_b));

    auto node_a2 = std::make_unique<ASTNode>('A');
    auto not_a = std::make_unique<ASTNode>(OpType::Not, std::move(node_a2));
    auto node_c = std::make_unique<ASTNode>('C');
    auto clause2 = std::make_unique<ASTNode>(OpType::Or, std::move(not_a), std::move(node_c));

    auto root = std::make_unique<ASTNode>(OpType::And, std::move(clause1), std::move(clause2));

    std::vector<char> variables = {'A', 'B', 'C'};
    BooleanFormConverter converter(*root, variables);

    std::cout << "--- Конвертер ДДНФ / ДКНФ (Мова C++) ---\n";
    std::cout << "SDNF: " << converter.generate_sdnf() << "\n";
    std::cout << "SKNF: " << converter.generate_sknf() << "\n";

    return 0;
}
```
:::

## 5. Синтаксичне перетворення дерев AST (NNF та розкриття дужок)

Для уникнення експоненційного обходу таблиці істинності використовують процедуру розкриття дужок на рівні синтаксичного дерева AST. Алгоритм складається з трьох послідовних фаз:

1. **Фаза усунення допоміжних операторів (Elimination Phase):**
   - Усі імплікації замінюються за тотожністю: `A → B ≡ ¬A ∨ B`.
   - Усі еквівалентності замінюються на пару імплікацій: `A ≡ B ≡ (¬A ∨ B) ∧ (¬B ∨ A)`.

2. **Побудова нормальної форми заперечення (NNF Phase):**
   - Заперечення просуваються вниз до листків з використанням законів Де Моргана: `¬(A ∧ B) ≡ ¬A ∨ ¬B` та `¬(A ∨ B) ≡ ¬A ∧ ¬B`.
   - Подвійні заперечення вилучаються: `¬¬A ≡ A`.
   - Після цього етапу операція `¬` застосовується виключно до атомарних змінних (літералів).

3. **Фаза дистрибутивного розгортання (Distribution Phase):**
   - Для побудови КНФ застосовується закон дистрибутивності диз'юнкції відносно кон'юнкції: `A ∨ (B ∧ C) ≡ (A ∨ B) ∧ (A ∨ C)`.
   - Для побудови ДНФ застосовується закон дистрибутивності кон'юнкції відносно диз'юнкції: `A ∧ (B ∨ C) ≡ (A ∧ B) ∨ (A ∧ C)`.

Ця рекурсивна підстановка продовжується доти, доки верхній рівень дерева не перетвориться на суто кон'юнктивний (для КНФ) або суто диз'юнктивний (для ДНФ).

## 6. Аналіз складності та крайові випадки

При практичній розробці логічних модулів необхідно зважати на такі аналітичні властивості та крайові випадки:

1. **Тотожні формули (Тавтології та Суперечності):**
   - Якщо формула є тотожною істиною (`F ≡ 1`), то її ДКНФ містить порожній набір макстермів. Програма повертає символьну константу `1`.
   - Якщо формула є тотожною хибністю (`F ≡ 0`), то її ДДНФ містить порожній набір мінтермів. Програма повертає символьну константу `0`.

2. **Просторовий роздув пам'яті:**
   - Табличний метод використовує `2ⁿ` ітерацій оцінки AST. Для `n = 30` кількість наборів становить `1 073 741 824`, що робить прямий перебір непридатним для використання у високопродуктивних системах.
   - Для розв'язання задач великої розмірності замість повного перебору застосовують алгоритм трансформації Цейтіна з кодуванням диз'юнктів у форматі DIMACS CNF.

3. **Синтаксичні оптимізації у C++:**
   - Використання `std::unique_ptr` гарантує автоматичне вилучення дерева AST при виході з області видимості (RAII), що запобігає витокам пам'яті без необхідності ручного виклику рекурсивних функцій типу `free_ast()`.
