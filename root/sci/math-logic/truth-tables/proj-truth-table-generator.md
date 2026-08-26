# ⚙️ Програмний генератор таблиць істинності та верифікатор тавтологій

Побудова повних таблиць істинності для логічних виразів від `N` змінних вимагає систематичного перебору `2^N` станів для верифікації тавтологій, перевірки здійснюваності (SAT) та доведення семантичної еквівалентності формул.

## Постановка інженерної задачі та архітектурні підходи

У компіляторах, системах формальної верифікації та логічних синтезаторах мікросхем виникає потреба автоматичної перевірки логічних виразів. Наприклад, модуль компіляторної оптимізації повинен гарантувати, що заміна складного умовного виразу `(A && B) || (!A && C)` на спрощений вираз не змінює логіку програми за жодної комбінації вхідних прапорців.

Для програмної реалізації такої перевірки застосовують кілька інженерних стратегій, які відрізняються продуктивністю та складністю:

1. **Поелементний обхід абстрактного синтаксичного дерева (Tree-Walk Evaluation)**:
   Логічна формула розбирається у дерево операцій (AST). Програма перебирає цілочисельні маски станів `mask` від `0` до `2^N - 1`. Для кожної маски дерево рекурсивно обчислюється, повертаючи булеве значення `true` або `false`. Цей підхід є найбільш наочним і гнучким для налагодження, але створює значний оверхед на виклики функцій: загальна кількість операцій становить `O(2^N · M)`, де `M` — кількість вузлів у дереві.

2. **Стекова віртуальна машина та зворотна польська нотація (Bytecode / RPN)**:
   Дерево трансліюється у лінійний масив байткод-інструкцій. Під час ітерацій замість рекурсивних викликів виконується лінійний прохід по масиву операцій із використанням невеликого фіксованого стека. Це усуває накладні витрати на виклики функцій та запобігає переповненню системного стека.

3. **Біт-паралельне векторне обчислення (SWAR / SIMD Evaluation)**:
   Замість того, щоб обчислювати один рядок таблиці за одну ітерацію, ми використовуємо розрядність процесорного слова (наприклад, 64-бітні цілі числа `uint64_t`). Для `N ≤ 6` змінних уся таблиця з `2^N ≤ 64` рядків упаковується в одне 64-бітне число для кожної змінної. Логічні операції `AND`, `OR`, `XOR`, `NOT` виконуються над цілими 64-бітними регістрами за один такт процесора, що дає прискорення рівно у 64 рази порівняно з поелементним підходом.

Нижче ми розберемо класичну архітектуру на базі AST із захищеним керуванням пам'яттю та детальною покроковою діагностикою виразів.

## Робоча реалізація на C та C++

Наведена нижче програма будує синтаксичне дерево виразу, підтримує змінні та операції `NOT`, `AND`, `OR`, `XOR`, `IMPLIES` (`⇒`), генерує відформатовану таблицю істинності та видає висновок про математичний статус формули: чи є вона тавтологією (завжди істинна), суперечністю (завжди хибна) або здійснюваною формулою.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>

typedef enum {
    NODE_VAR,
    NODE_NOT,
    NODE_AND,
    NODE_OR,
    NODE_XOR,
    NODE_IMPLIES
} NodeType;

typedef struct ASTNode {
    NodeType type;
    int var_index;               /* Для NODE_VAR: індекс змінної (0, 1, ...) */
    struct ASTNode* left;        /* Лівий операнд (або єдиний операнд для NOT) */
    struct ASTNode* right;       /* Правий операнд для бінарних операцій */
} ASTNode;

/* Конструктори вузлів AST */
ASTNode* ast_create_var(int var_index) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) { perror("malloc failed"); exit(EXIT_FAILURE); }
    node->type = NODE_VAR;
    node->var_index = var_index;
    node->left = NULL;
    node->right = NULL;
    return node;
}

ASTNode* ast_create_unary(NodeType type, ASTNode* child) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) { perror("malloc failed"); exit(EXIT_FAILURE); }
    node->type = type;
    node->var_index = -1;
    node->left = child;
    node->right = NULL;
    return node;
}

ASTNode* ast_create_binary(NodeType type, ASTNode* left, ASTNode* right) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) { perror("malloc failed"); exit(EXIT_FAILURE); }
    node->type = type;
    node->var_index = -1;
    node->left = left;
    node->right = right;
    return node;
}

/* Рекурсивне звільнення пам'яті */
void ast_free(ASTNode* root) {
    if (!root) return;
    ast_free(root->left);
    ast_free(root->right);
    free(root);
}

/* Оцінка значення AST для заданої бітової маски стану */
bool ast_evaluate(const ASTNode* root, uint32_t state_mask) {
    if (!root) return false;
    
    switch (root->type) {
        case NODE_VAR:
            return (state_mask & (1U << root->var_index)) != 0;
        case NODE_NOT:
            return !ast_evaluate(root->left, state_mask);
        case NODE_AND:
            return ast_evaluate(root->left, state_mask) && ast_evaluate(root->right, state_mask);
        case NODE_OR:
            return ast_evaluate(root->left, state_mask) || ast_evaluate(root->right, state_mask);
        case NODE_XOR:
            return ast_evaluate(root->left, state_mask) ^ ast_evaluate(root->right, state_mask);
        case NODE_IMPLIES: {
            bool left_val = ast_evaluate(root->left, state_mask);
            bool right_val = ast_evaluate(root->right, state_mask);
            return !left_val || right_val; /* P => Q еквівалентно !P || Q */
        }
        default:
            return false;
    }
}

/* Генерація повної таблиці істинності та верифікація */
void print_truth_table(const ASTNode* root, const char* const* var_names, int num_vars) {
    if (num_vars > 31) {
        fprintf(stderr, "Помилка: кількість змінних перевищує 31.\n");
        return;
    }

    /* Друк заголовка таблиці */
    for (int i = 0; i < num_vars; ++i) {
        printf("%s\t", var_names[i]);
    }
    printf("| Результат\n");
    for (int i = 0; i < num_vars * 8 + 12; ++i) putchar('-');
    putchar('\n');

    uint32_t total_rows = 1U << num_vars;
    uint32_t true_count = 0;

    for (uint32_t mask = 0; mask < total_rows; ++mask) {
        for (int i = 0; i < num_vars; ++i) {
            bool bit = (mask & (1U << i)) != 0;
            printf("%d\t", bit ? 1 : 0);
        }
        bool res = ast_evaluate(root, mask);
        if (res) true_count++;
        printf("| %d\n", res ? 1 : 0);
    }

    /* Підсумкова класифікація */
    printf("\nСтатистика: %u/%u істинних наборів.\n", true_count, total_rows);
    if (true_count == total_rows) {
        printf("Висновок: Формула є ТАВТОЛОГІЄЮ (завжди істинна).\n");
    } else if (true_count == 0) {
        printf("Висновок: Формула є СУПЕРЕЧНІСТЮ (тотожна хиба).\n");
    } else {
        printf("Висновок: Формула є ЗДІЙСНЮВАНОЮ (випадкова логічна функція).\n");
    }
}

int main(void) {
    /* Конструюємо формулу Закону Контрапозиції: (P => Q) => (!Q => !P) */
    const char* names[] = {"P", "Q"};
    int num_vars = 2;

    /* Ліва частина: P => Q */
    ASTNode* p1 = ast_create_var(0);
    ASTNode* q1 = ast_create_var(1);
    ASTNode* left_side = ast_create_binary(NODE_IMPLIES, p1, q1);

    /* Права частина: !Q => !P */
    ASTNode* q2 = ast_create_var(1);
    ASTNode* not_q = ast_create_unary(NODE_NOT, q2);
    ASTNode* p2 = ast_create_var(0);
    ASTNode* not_p = ast_create_unary(NODE_NOT, p2);
    ASTNode* right_side = ast_create_binary(NODE_IMPLIES, not_q, not_p);

    /* Повна формула: (P => Q) => (!Q => !P) */
    ASTNode* formula = ast_create_binary(NODE_IMPLIES, left_side, right_side);

    printf("Перевірка виразу: (P => Q) => (!Q => !P)\n\n");
    print_truth_table(formula, names, num_vars);

    ast_free(formula);
    return 0;
}
```

@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <cstdint>
#include <span>

enum class OpType {
    Var,
    Not,
    And,
    Or,
    Xor,
    Implies
};

// Базовий абстрактний вузол синтаксичного дерева з RAII
class ExprNode {
public:
    virtual ~ExprNode() = default;
    [[nodiscard]] virtual bool evaluate(uint32_t stateMask) const noexcept = 0;
};

// Вузол логічної змінної
class VariableNode final : public ExprNode {
    int varIndex;
public:
    explicit VariableNode(int index) noexcept : varIndex(index) {}
    
    [[nodiscard]] bool evaluate(uint32_t stateMask) const noexcept override {
        return (stateMask & (1U << varIndex)) != 0;
    }
};

// Вузол унарного заперечення (NOT)
class NotNode final : public ExprNode {
    std::unique_ptr<ExprNode> operand;
public:
    explicit NotNode(std::unique_ptr<ExprNode> op) noexcept : operand(std::move(op)) {}
    
    [[nodiscard]] bool evaluate(uint32_t stateMask) const noexcept override {
        return !operand->evaluate(stateMask);
    }
};

// Вузол бінарних логічних операцій
class BinaryOpNode final : public ExprNode {
    OpType op;
    std::unique_ptr<ExprNode> left;
    std::unique_ptr<ExprNode> right;
public:
    BinaryOpNode(OpType operation, std::unique_ptr<ExprNode> lhs, std::unique_ptr<ExprNode> rhs) noexcept
        : op(operation), left(std::move(lhs)), right(std::move(rhs)) {}

    [[nodiscard]] bool evaluate(uint32_t stateMask) const noexcept override {
        const bool l = left->evaluate(stateMask);
        const bool r = right->evaluate(stateMask);
        switch (op) {
            case OpType::And:     return l && r;
            case OpType::Or:      return l || r;
            case OpType::Xor:     return l ^ r;
            case OpType::Implies: return !l || r;
            default:              return false;
        }
    }
};

// Клас генератора таблиць та верифікатора формул
class TruthTableEngine {
public:
    static void generateAndVerify(const ExprNode& root, std::span<const std::string_view> varNames) {
        const size_t numVars = varNames.size();
        if (numVars > 31) {
            std::cerr << "Помилка: підтримується не більше 31 змінної.\n";
            return;
        }

        // Вивід заголовка
        for (const auto& name : varNames) {
            std::cout << name << '\t';
        }
        std::cout << "| Результат\n";
        std::cout << std::string(numVars * 8 + 12, '-') << '\n';

        const uint32_t totalRows = 1U << numVars;
        uint32_t trueCount = 0;

        for (uint32_t mask = 0; mask < totalRows; ++mask) {
            for (size_t i = 0; i < numVars; ++i) {
                const bool bit = (mask & (1U << i)) != 0;
                std::cout << (bit ? 1 : 0) << '\t';
            }
            const bool result = root.evaluate(mask);
            if (result) {
                trueCount++;
            }
            std::cout << "| " << (result ? 1 : 0) << '\n';
        }

        std::cout << "\nСтатистика: " << trueCount << "/" << totalRows << " істинних наборів.\n";
        if (trueCount == totalRows) {
            std::cout << "Висновок: Формула є ТАВТОЛОГІЄЮ (завжди істинна).\n";
        } else if (trueCount == 0) {
            std::cout << "Висновок: Формула є СУПЕРЕЧНІСТЮ (тотожна хиба).\n";
        } else {
            std::cout << "Висновок: Формула є ЗДІЙСНЮВАНОЮ (випадкова логічна функція).\n";
        }
    }
};

int main() {
    // Верифікуємо Закон Контрапозиції: (P => Q) => (!Q => !P)
    const std::vector<std::string_view> varNames = {"P", "Q"};

    // Ліва частина: P => Q
    auto p1 = std::make_unique<VariableNode>(0);
    auto q1 = std::make_unique<VariableNode>(1);
    auto leftSide = std::make_unique<BinaryOpNode>(OpType::Implies, std::move(p1), std::move(q1));

    // Права частина: !Q => !P
    auto q2 = std::make_unique<VariableNode>(1);
    auto notQ = std::make_unique<NotNode>(std::move(q2));
    auto p2 = std::make_unique<VariableNode>(0);
    auto notP = std::make_unique<NotNode>(std::move(p2));
    auto rightSide = std::make_unique<BinaryOpNode>(OpType::Implies, std::move(notQ), std::move(notP));

    // Повна формула
    auto root = std::make_unique<BinaryOpNode>(OpType::Implies, std::move(leftSide), std::move(rightSide));

    std::cout << "Перевірка формули закону контрапозиції:\n\n";
    TruthTableEngine::generateAndVerify(*root, varNames);

    return 0;
}
```
:::

## Покроковий механізм обчислення та робота з регістрами

Розгляньмо, як процесор обробляє кожен рядок таблиці на рівні бітових операцій:

1. **Кодування конфігурації у двійковий вектор**:
   Значення всіх змінних індексуються позиціями бітів: змінна з індексом `0` відповідає молодшому біту `bit 0`, змінна `1` — `bit 1`, і так далі. Коли лічильник циклу `mask` набуває значення, наприклад, `5` (у двійковій системі `...000101_2`), це автоматично означає присвоєння `P = 1`, `Q = 0`, `R = 1`.

2. **Миттєве вилучення значення змінної**:
   Вузол `VariableNode` виконує вилучення значення за допомогою бітової маски:
   ```text
   значення = (mask & (1 << index)) != 0
   ```
   Це транслюється компілятором в одну асемблерну інструкцію тестування біта (наприклад, `bt` на архітектурі x86 або `tst` на ARM), не вимагаючи жодного звернення до оперативної пам'яті.

3. **Коротке замикання та семантика операцій**:
   Оператор `switch` у методі `evaluate` використовує стандартну семантику мов C та C++: операція `&&` і `||` виконує ліниве обчислення (short-circuit evaluation). Якщо лівий операнд кон'юнкції хибний, праве піддерево не обчислюється, що суттєво економить такти процесора на складних вкладених підвиразах.

## Аналіз складності, пам'ять та крайові випадки

1. **Керування пам'яттю та RAII**:
   - У версії на C реалізовано рекурсивне очищення дерева функцією `ast_free`, що запобігає витокам пам'яті у динамічній купі (heap).
   - У версії на C++ застосовано сучасні розумні вказівники `std::unique_ptr` та інтерфейси без копіювання `std::span` і `std::string_view`. Усі вузли володіють своїми дочірніми елементами за принципом монопольного володіння, що гарантує деструкцію дерева за будь-яких умов, включно з аварійним виходом через винятки.

2. **Часова складність**:
   - Часова складність становить `O(2^N · M)`, де `N` — кількість вхідних змінних, а `M` — загальна кількість операцій у формулі.
   - Експоненційне масштабування `2^N` визначає практичну межу застосовності методу: таблиці ефективні для `N ≤ 20–25`. Для `N=20` таблиця містить `1 048 576` рядків і прораховується за частки секунди; для `N=30` кількість рядків перевищує один мільярд, що вимагає переходу до спеціалізованих SAT-солверів на базі алгоритму DPLL/CDCL.

3. **Просторова складність**:
   - `O(M)` пам'яті для зберігання вузлів дерева AST.
   - `O(D)` додаткової пам'яті у стеку викликів під час рекурсії, де `D` — глибина дерева (`D ≤ M`). Для збалансованого дерева `D = O(log M)`.

4. **Захисне програмування та крайові випадки**:
   - **Переповнення розрядності**: Зсув `1U << numVars` для `numVars ≥ 32` на 32-бітних цілих числах спричиняє невизначену поведінку (UB). Код містить обов'язкову захисну перевірку `numVars > 31`.
   - **Глибина рекурсії**: Для дуже довгих лінійних ланцюжків операцій (наприклад, кон'юнкції з тисяч елементів) рекурсивний обхід може переповнити системний стек. У промислових парсерах такі дерева оптимізують за допомогою перетворення у багатовходові вузли (N-ary nodes) або ітеративного стекового обходу.
